"""MacroCenter — tablero de datos macroeconómicos de Argentina.

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import json
import os
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from macrocenter import charts, data, interactivo, legal, news, presidentes, score, style

st.set_page_config(page_title="MacroCenter", page_icon=style.favicon(), layout="wide")

HOY = pd.Timestamp.today().normalize()
DESDE_BCRA = "2016-01-01"  # el UVA arranca en marzo de 2016
PERIODOS = {"1 mes": 30, "6 meses": 182, "1 año": 365, "2 años": 730, "5 años": 1825, "Todo": None}


def error_corto(exc: BaseException) -> str:
    """Texto de error apto para mostrar: solo el tipo. El detalle (URLs, rutas) va a la consola del servidor."""
    print(f"[MacroCenter] {type(exc).__name__}: {exc}", flush=True)
    return type(exc).__name__


# ───────────────────────── carga de datos ─────────────────────────
import pickle
import threading

CACHE_DISCO = Path(__file__).parent / ".macrocenter_cache.pkl"
DISCO_FRESCO = 3600       # un dato guardado con menos de 1 h se usa tal cual, sin descargar
DISCO_VIEJO_MAX = 43200   # hasta 12 h se muestra enseguida mientras se actualiza de fondo
_refrescando = threading.Lock()


def _leer_disco() -> tuple[tuple[dict, datetime], float] | None:
    """(datos, edad en segundos) del último guardado, o None si no hay o está dañado."""
    try:
        edad = time.time() - CACHE_DISCO.stat().st_mtime
        with open(CACHE_DISCO, "rb") as f:
            datos, cuando = pickle.load(f)
        # si cambió la lista de fuentes (código nuevo), lo guardado ya no sirve
        if isinstance(datos, dict) and isinstance(cuando, datetime) and set(datos) == set(_tareas()):
            return (datos, cuando), edad
    except Exception:  # noqa: BLE001 — archivo inexistente, a medio escribir o de otra versión
        pass
    return None


def _guardar_disco(resultado: tuple[dict, datetime]) -> None:
    """Solo se guarda una descarga sin fallas (así una caída de red no queda 'congelada' en el disco)."""
    if any(isinstance(v, str) for v in resultado[0].values()):
        return
    try:
        tmp = CACHE_DISCO.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump(resultado, f)
        tmp.replace(CACHE_DISCO)
    except Exception:  # noqa: BLE001 — el disco es solo una optimización
        pass


def borrar_disco() -> None:
    try:
        CACHE_DISCO.unlink(missing_ok=True)
    except OSError:
        pass


def _refrescar_en_segundo_plano() -> None:
    """Descarga todo sin bloquear la página; al terminar deja el disco al día y suelta el caché de memoria."""
    if not _refrescando.acquire(blocking=False):
        return

    def tarea():
        try:
            _guardar_disco(_descargar_todo())
            cargar_todo.clear()
        except Exception:  # noqa: BLE001
            pass
        finally:
            _refrescando.release()

    threading.Thread(target=tarea, daemon=True).start()


@st.cache_data(ttl=3600, show_spinner="Descargando datos de BCRA, INDEC y ArgentinaDatos…")
def cargar_todo() -> tuple[dict[str, pd.DataFrame | str], datetime]:
    """Datos de todas las fuentes. Usa el último guardado en disco si es reciente (arranque casi instantáneo);
    si es viejo pero no demasiado, lo muestra ya y actualiza de fondo; si no hay, descarga."""
    guardado = _leer_disco()
    if guardado:
        resultado, edad = guardado
        if edad < DISCO_FRESCO:
            return resultado
        if edad < DISCO_VIEJO_MAX:
            _refrescar_en_segundo_plano()
            return resultado
    resultado = _descargar_todo()
    _guardar_disco(resultado)
    return resultado


def _tareas() -> dict:
    tareas = {f"bcra:{k}": (lambda k=k: data.bcra(k, desde=DESDE_BCRA)) for k in data.BCRA_IDS}
    tareas |= {f"serie:{k}": (lambda k=k: data.serie(k)) for k in data.SERIES_IDS}
    tareas["dolares"] = data.dolares
    tareas["riesgo_pais"] = data.riesgo_pais
    tareas["fx:EUR"] = lambda: data.divisa("EUR")
    tareas["fx:GBP"] = lambda: data.divisa("GBP")
    tareas["dolar_hist"] = data.dolar_historico
    tareas["inflacion_hist"] = data.inflacion_historica
    return tareas


def _descargar_todo() -> tuple[dict[str, pd.DataFrame | str], datetime]:
    """Descarga todas las fuentes en paralelo. Cada fuente que falla queda como str con el error."""
    tareas = _tareas()

    def correr(item):
        nombre, fn = item
        try:
            return nombre, data.limpiar(fn())
        except Exception as e:  # noqa: BLE001 — queremos aislar cualquier falla de red/formato
            return nombre, error_corto(e)

    with ThreadPoolExecutor(max_workers=10) as pool:  # son pedidos de red: conviene hacer muchos a la vez
        return dict(pool.map(correr, tareas.items())), datetime.now()


@st.cache_data(ttl=1800, show_spinner="Buscando noticias del BCRA y del Ministerio de Economía…")
def cargar_noticias() -> dict[str, list[news.Noticia] | str]:
    """Cada fuente falla por separado: si una cambia su sitio, la otra se sigue mostrando."""
    out: dict[str, list[news.Noticia] | str] = {}
    for clave, fn in (("bcra", news.bcra), ("economia", news.economia)):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    return out


@st.cache_data(ttl=300, show_spinner=False)
def cargar_cripto() -> dict[str, pd.DataFrame | str]:
    """Mercado de criptomonedas y precio del USDT por exchange. Cada parte falla por separado. Dura 5 minutos."""
    out: dict[str, pd.DataFrame | str] = {}
    for clave, fn in (("mercado", data.cripto_mercado), ("usdt", data.usdt_exchanges)):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    return out


@st.cache_data(ttl=900, show_spinner=False)
def cargar_mercados() -> dict[str, pd.DataFrame | str]:
    """Cierres de las bolsas del mundo y materias primas (Yahoo Finance). Cada una falla por separado. 15 minutos."""
    def uno(item):
        simbolo = item[0]
        try:
            return simbolo, data.limpiar(data.indice(simbolo))
        except Exception as e:  # noqa: BLE001
            return simbolo, error_corto(e)

    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(pool.map(uno, data.INDICES))


@st.cache_data(ttl=900, show_spinner=False)
def _historia_cripto(coin_id: str, dias: int) -> pd.DataFrame:
    return data.limpiar(data.cripto_historia(coin_id, dias))  # si falla, la excepción no se guarda en el caché


def historia_cripto(coin_id: str, dias: int) -> pd.DataFrame | str:
    try:
        return _historia_cripto(coin_id, dias)
    except Exception as e:  # noqa: BLE001
        return error_corto(e)


@st.cache_data(ttl=86400, show_spinner=False)
def cargar_fotos() -> dict[str, dict]:
    """Fotos de los presidentes (Wikipedia/Commons). Se piden una vez por día."""
    return presidentes.fotos()


@st.cache_resource
def _estado_actualizar() -> dict:
    """Estado compartido por todas las sesiones: cuándo se usó por última vez «Actualizar datos»."""
    return {"ultimo": 0.0}


def reintentar_si_fallo(cache_fn, clave: str, fallo: bool, espera: int = 60) -> None:
    """Que una falla pasajera no quede pegada en el caché: si algo falló, se borra el caché para volver a intentarlo
    en la próxima interacción (como máximo una vez cada `espera` segundos, para no martillar a las fuentes)."""
    if fallo and time.time() - st.session_state.get(f"_reintento_{clave}", 0) > espera:
        st.session_state[f"_reintento_{clave}"] = time.time()
        if clave == "datos":
            borrar_disco()
        cache_fn.clear()


@contextmanager
def protegido(nombre: str):
    """Aísla una sección: si algo falla adentro, se avisa y el resto de la página sigue funcionando.
    (st.stop() y st.rerun() no son Exception, así que pasan de largo.)"""
    try:
        yield
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()  # queda en la consola del servidor para poder diagnosticarlo
        st.warning(f"No se pudo mostrar «{nombre}» ({type(e).__name__}). El resto de la página sigue funcionando.")


DATOS, ACTUALIZADO = cargar_todo()
reintentar_si_fallo(cargar_todo, "datos", any(isinstance(v, str) for v in DATOS.values()))


def fotos_presidentes() -> dict[str, dict]:
    f = cargar_fotos()
    reintentar_si_fallo(cargar_fotos, "fotos", not f)
    return f


def get(clave: str) -> pd.DataFrame | None:
    d = DATOS.get(clave)
    if isinstance(d, pd.DataFrame) and not d.empty:
        return d
    st.warning(f"No se pudo cargar `{clave}` ({d if isinstance(d, str) else 'sin datos'}).")
    return None


# ───────────────────────── noticias (ventana emergente) ─────────────────────────
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
            "noviembre", "diciembre"]


# Los archivos de preferencias solo se usan al correr en la propia computadora (run.bat define MACROCENTER_LOCAL=1).
# Publicada en internet, cada visita guarda sus elecciones solo en su sesión: nada se comparte entre usuarios.
LOCAL = os.environ.get("MACROCENTER_LOCAL") == "1"
LEIDAS_ARCHIVO = Path(__file__).parent / ".macrocenter_leidas.json"


def leidas() -> set[str]:
    """URLs de noticias ya marcadas como leídas (se guardan en un archivo local; si está roto, se ignora)."""
    if "noticias_leidas" not in st.session_state:
        try:
            if not LOCAL:
                raise OSError("sin archivo compartido")
            crudo = json.loads(LEIDAS_ARCHIVO.read_text(encoding="utf-8"))
            st.session_state["noticias_leidas"] = {u for u in crudo if isinstance(u, str)} if isinstance(crudo, list) else set()
        except Exception:  # noqa: BLE001
            st.session_state["noticias_leidas"] = set()
    return st.session_state["noticias_leidas"]


def marcar_leidas() -> None:
    """Marca como leídas todas las notas que se ven hoy y recuerda las últimas 300."""
    vistas = {x.url for items in cargar_noticias().values() if isinstance(items, list) for x in items}
    st.session_state["noticias_leidas"] = vistas | set(leidas())
    try:
        if LOCAL:
            LEIDAS_ARCHIVO.write_text(json.dumps(sorted(st.session_state["noticias_leidas"])[-300:]), encoding="utf-8")
    except OSError:
        pass  # sin permiso de escritura: vale para esta sesión


def md_seguro(texto: str) -> str:
    """Escapa todo lo que Markdown podría interpretar en un texto que viene de afuera (enlaces, HTML, fórmulas, listas)."""
    return re.sub(r"([\\`*_{}\[\]()<>#+\-!|~$&])", r"\\\1", texto or "")


def tarjeta_noticia(n: news.Noticia) -> None:
    with st.container(border=True):
        enlace = n.url.replace("(", "%28").replace(")", "%29").replace(" ", "%20")  # para no romper el enlace Markdown
        st.markdown(f"**[{md_seguro(n.titulo)}]({enlace})**")
        meta = f"{n.fecha.day} de {MESES_ES[n.fecha.month - 1]} de {n.fecha.year}"
        nueva = "Nueva · " if n.url not in leidas() else ""
        st.caption(nueva + meta + (f" · {md_seguro(n.etiquetas)}" if n.etiquetas else ""))
        if n.resumen:
            st.markdown(md_seguro(n.resumen if len(n.resumen) <= 260 else n.resumen[:257].rsplit(" ", 1)[0] + "…"))


def columna_noticias(slot, titulo: str, sitio: str, items: list[news.Noticia] | str, visibles: int = 4) -> None:
    with slot:
        st.markdown(f"#### {titulo}")
        if isinstance(items, str) or not items:
            st.warning("No se pudieron leer las noticias de este sitio (puede haber cambiado su diseño o estar "
                       f"caído). Podés verlas directamente en la fuente.\n\n`{items if isinstance(items, str) else 'sin resultados'}`")
        else:
            for n in items[:visibles]:
                tarjeta_noticia(n)
            if len(items) > visibles:
                with st.expander(f"Ver {len(items) - visibles} más"):
                    for n in items[visibles:]:
                        tarjeta_noticia(n)
        st.markdown(f"[Ver todas en el sitio oficial ↗]({sitio})")


def noticias_recientes(dias: int = 7) -> int:
    """Cuántas notas de las dos fuentes se publicaron en los últimos `dias` días (0 si no se pudieron leer)."""
    total = 0
    noticias = cargar_noticias()
    reintentar_si_fallo(cargar_noticias, "noticias", any(isinstance(v, str) for v in noticias.values()))
    for items in noticias.values():
        if isinstance(items, list):
            total += sum(1 for x in items if 0 <= (datetime.now() - x.fecha).days <= dias and x.url not in leidas())
    return total


@st.dialog("Noticias oficiales", width="large")
def ver_noticias() -> None:
    st.caption("Últimas novedades de los sitios oficiales (se actualizan cada 30 minutos). "
               "Los textos completos están en cada fuente.")
    noticias = cargar_noticias()
    if st.button("✓ Marcar todas como leídas", help="Apaga el aviso del botón de noticias hasta que haya novedades."):
        marcar_leidas()
        st.rerun()
    a, b = st.columns(2)
    columna_noticias(a, "Banco Central (BCRA)", news.BCRA_URL, noticias["bcra"])
    columna_noticias(b, "Ministerio de Economía", news.ECONOMIA_URL, noticias["economia"])


# ───────────────────────── barra lateral ─────────────────────────
style.aplicar()


def ir_a(destino: str) -> None:
    """Cambia la vista principal: 'tablero' (pestañas), 'historia' o 'juegos'."""
    st.session_state["vista"] = destino


VISTAS = ("tablero", "historia", "juegos")
vista = st.session_state.setdefault("vista", "tablero")
if vista not in VISTAS:  # estado viejo o inválido: se vuelve al tablero
    vista = st.session_state["vista"] = "tablero"

with st.sidebar:
    st.markdown(style.marca(), unsafe_allow_html=True)
    nuevas = noticias_recientes()
    if nuevas:
        etiqueta_noticias = f"Noticias · {nuevas} {'nueva' if nuevas == 1 else 'nuevas'}"
    else:
        etiqueta_noticias = "Noticias"
    # la clave distinta cuando hay novedades activa el puntito rojo pulsante (ver style.py)
    if st.button(etiqueta_noticias, width="stretch", key="btn_noticias_nuevas" if nuevas else "btn_noticias",
                 help="Últimas novedades del BCRA y del Ministerio de Economía"
                      + (f" ({nuevas} de los últimos 7 días)" if nuevas else "")):
        ver_noticias()
    st.markdown(style.etiqueta("Explorar"), unsafe_allow_html=True)
    for clave_vista, texto in (("tablero", "Tablero"), ("historia", "Historia económica"),
                               ("juegos", "Juegos y herramientas")):
        st.button(texto, width="stretch", key=f"nav_{clave_vista}", on_click=ir_a, args=(clave_vista,),
                  type="primary" if vista == clave_vista else "secondary")
    st.markdown(style.etiqueta("Datos"), unsafe_allow_html=True)
    # Los cachés son compartidos entre todas las visitas: vaciarlos obliga a volver a descargar para todos. Publicada, el botón
    # tiene una espera de 10 minutos entre usos (para cualquiera), así nadie puede forzar descargas en cadena.
    ESPERA_ACTUALIZAR = 0 if LOCAL else 600
    _est = _estado_actualizar()
    faltan = int(ESPERA_ACTUALIZAR - (time.time() - _est["ultimo"]))
    if st.button("Actualizar datos", width="stretch", key="actualizar", disabled=faltan > 0,
                 help=None if faltan <= 0 else f"Alguien actualizó hace poco. Podés volver a hacerlo en {faltan // 60 + 1} min."):
        _est["ultimo"] = time.time()
        borrar_disco()
        cargar_todo.clear()
        cargar_noticias.clear()
        cargar_cripto.clear()
        cargar_mercados.clear()
        st.rerun()
    st.markdown(
        f'<div class="mc-status"><span class="dot">●</span> Actualizado {ACTUALIZADO:%d/%m/%Y %H:%M}</div>',
        unsafe_allow_html=True,
    )

def rec(df: pd.DataFrame, min_anios: int = 0, periodo: str = "2 años") -> pd.DataFrame:
    """Recorta al `periodo` (por defecto 2 años) y a fechas ya ocurridas (UVA/CER/ICL traen días futuros).
    `min_anios` garantiza una ventana mínima para series de baja frecuencia."""
    out = df[df["fecha"] <= HOY]
    dias = PERIODOS.get(periodo, PERIODOS["2 años"]) if periodo in PERIODOS else PERIODOS["2 años"]
    if dias is None:
        return out
    return out[out["fecha"] >= HOY - pd.Timedelta(days=max(dias, min_anios * 365))]


def selector_periodo(clave: str, defecto: str = "2 años") -> str:
    """Botones de período propios de un gráfico (cada gráfico importante tiene el suyo)."""
    p = st.pills("Período", list(PERIODOS), default=defecto, key=f"per_{clave}", label_visibility="collapsed")
    return p if p in PERIODOS else defecto


def con_periodo(clave: str, df: pd.DataFrame, min_anios: int = 0, defecto: str = "2 años") -> pd.DataFrame:
    return rec(df, min_anios, selector_periodo(clave, defecto))


def ultimo(df: pd.DataFrame, col: str = "valor") -> float | None:
    d = df[df["fecha"] <= HOY].dropna(subset=[col])
    return None if d.empty else float(d.iloc[-1][col])


def delta(df: pd.DataFrame, col: str = "valor", dias: int = 30, modo: str = "pct") -> float | None:
    d = df[df["fecha"] <= HOY].dropna(subset=[col])
    if d.empty:
        return None
    ref = d[d["fecha"] <= d.iloc[-1]["fecha"] - pd.Timedelta(days=dias)]
    if ref.empty:
        return None
    a, b = float(d.iloc[-1][col]), float(ref.iloc[-1][col])
    if modo == "pct":
        return None if b == 0 else (a / b - 1) * 100  # variación porcentual sobre cero: no tiene sentido
    return a - b


def base100(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Pasa las columnas a base 100 = primer dato del período. Si no hay datos o el primero es cero, quedan vacías."""
    d = df.dropna(subset=cols).copy()
    for c in cols:
        if not d.empty:
            ini = d[c].iloc[0]
            d[c] = d[c] / ini * 100 if ini else float("nan")
    return d


def kpi(slot, label: str, valor: float | None, dec: int = 0, pre: str = "", suf: str = "",
        d: float | None = None, d_suf: str = "%", d_txt: str = "vs 30 d", color: str = "off", help: str | None = None):
    slot.metric(
        label,
        charts.num(valor, dec, suf, pre),
        None if d is None else f"{charts.num(d, 1, d_suf)} {d_txt}",
        delta_color=color,
        help=help,
        border=True,
    )


def grafico(fig):
    # sin la barra de herramientas de Plotly (tapa el gráfico, sobre todo en el celular) y sin zoom accidental al deslizar
    fig.update_layout(dragmode=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False})


# ───────────────────────── carga de series ─────────────────────────
dol = get("dolares")
if dol is not None:
    dol = dol.copy()
    dol["brecha_blue"] = ((dol["blue"] / dol["oficial"] - 1) * 100).replace([float("inf"), float("-inf")], float("nan"))
    dol["brecha_ccl"] = ((dol["contadoconliqui"] / dol["oficial"] - 1) * 100).replace([float("inf"), float("-inf")], float("nan"))
    dol_rec = dol.dropna(subset=["oficial"])

riesgo = get("riesgo_pais")
reservas = get("bcra:reservas")
infl_m, infl_ia, rem = get("bcra:inflacion_mensual"), get("bcra:inflacion_interanual"), get("bcra:rem_12m")
uva = get("bcra:uva")
emae_sa, emae = get("serie:emae_sa"), get("serie:emae")
paro = get("serie:desempleo")
pib = get("serie:pib")
badlar = get("bcra:badlar")
pases, tpm = get("bcra:pases_1d"), get("bcra:tpm")
sal, sal_priv, sal_pub = get("serie:salarios"), get("serie:salarios_privado"), get("serie:salarios_publico")
ripte, smvm, haber_min = get("serie:ripte"), get("serie:smvm"), get("serie:haber_minimo")


def yoy(df: pd.DataFrame, periodos: int = 12) -> pd.DataFrame:
    return df.assign(valor=df["valor"].pct_change(periodos) * 100).dropna()


def salario_real() -> pd.DataFrame | None:
    """Salario nominal (índice total) vs inflación, ambos interanuales, alineados por mes."""
    if sal is None or infl_ia is None:
        return None
    s = yoy(sal).assign(mes=lambda x: x["fecha"].dt.to_period("M")).rename(columns={"valor": "salario"})
    i = infl_ia.assign(mes=infl_ia["fecha"].dt.to_period("M")).rename(columns={"valor": "inflacion"})
    m = s[["fecha", "mes", "salario"]].merge(i[["mes", "inflacion"]], on="mes")
    m["real"] = ((1 + m["salario"] / 100) / (1 + m["inflacion"] / 100) - 1) * 100
    return m


ex, im = get("serie:exportaciones"), get("serie:importaciones")
fis_prim, fis_fin = get("serie:fiscal_primario"), get("serie:fiscal_financiero")
pib_corr = get("serie:pib_corriente")


def fiscal_df() -> pd.DataFrame:
    """Resultado primario y financiero como % del PBI: mensual (sobre 1/12 del PBI) y acumulado de 12 meses.
    Vacío si falta alguna de las series. El PBI de cada mes es el promedio de los últimos 4 trimestres (anualizados);
    pasado el último trimestre publicado se lo actualiza con la inflación mensual."""
    if pib_corr is None or (fis_prim is None and fis_fin is None):
        return pd.DataFrame(columns=["fecha"])
    partes = []
    if fis_prim is not None:
        partes.append(fis_prim[["fecha", "valor"]].rename(columns={"valor": "primario"}))
    if fis_fin is not None:
        partes.append(fis_fin[["fecha", "valor"]].rename(columns={"valor": "financiero"}))
    f = partes[0]
    for p_ in partes[1:]:
        f = f.merge(p_, on="fecha", how="outer")
    f = f[f["fecha"] <= HOY].sort_values("fecha").reset_index(drop=True)
    w = pib_corr.dropna(subset=["valor"]).set_index("fecha")["valor"].sort_index().rolling(4).mean().dropna()
    if w.empty:
        return pd.DataFrame(columns=["fecha"])
    ultimo_q = w.index[-1]
    inf = infl_m.set_index("fecha")["valor"] if infl_m is not None else pd.Series(dtype=float)

    def pbi_en(m: pd.Timestamp) -> float:
        q = m.to_period("Q").start_time
        if q in w.index:
            return float(w[q])
        if q < w.index[0]:
            return float("nan")
        tramo = inf[(inf.index >= ultimo_q + pd.DateOffset(months=3)) & (inf.index <= m)]
        return float(w.iloc[-1] * (1 + tramo / 100).prod())

    f["pbi"] = f["fecha"].map(pbi_en)
    for c in ("primario", "financiero"):
        if c in f:
            suma12 = f[c].rolling(12, min_periods=12).sum()
            f[c] = f[c] / (f["pbi"] / 12) * 100
            f[c + "_12m"] = suma12 / f["pbi"] * 100
    return f.dropna(subset=["pbi"]).replace([float("inf"), float("-inf")], float("nan")).reset_index(drop=True)
comercio = None
if ex is not None and im is not None:
    comercio = ex.rename(columns={"valor": "exp"}).merge(im.rename(columns={"valor": "imp"}), on="fecha")
    comercio["saldo"] = comercio["exp"] - comercio["imp"]
    comercio["saldo_12m"] = comercio["saldo"].rolling(12).sum()


def series_calificacion() -> dict[str, pd.Series]:
    """Series que alimentan la calificación macro (clave = Driver.clave de macrocenter.score)."""
    out: dict[str, pd.Series] = {}

    def poner(clave: str, df: pd.DataFrame | None, col: str = "valor") -> None:
        if df is not None and not df.empty:
            out[clave] = df.dropna(subset=[col]).drop_duplicates("fecha").set_index("fecha")[col].sort_index()

    poner("infl_m", infl_m)
    poner("rem", rem)
    poner("reservas", reservas)
    poner("riesgo", riesgo)
    if dol is not None:
        poner("brecha", dol.dropna(subset=["brecha_blue"]).assign(valor=lambda x: x["brecha_blue"].abs()))
    if comercio is not None:
        poner("saldo12", comercio, "saldo_12m")
    if emae is not None:
        poner("emae", yoy(emae))
    if paro is not None:
        poner("paro", paro.assign(valor=paro["valor"] * 100))
    sr_ = salario_real()
    if sr_ is not None:
        poner("salario_real", sr_, "real")
    return out


COMPARACIONES = {
    "Hoy": HOY,
    "Hace 3 meses": HOY - pd.DateOffset(months=3),
    "Hace 6 meses": HOY - pd.DateOffset(months=6),
    "Hace 1 año": HOY - pd.DateOffset(years=1),
    "Hace 2 años": HOY - pd.DateOffset(years=2),
}


@st.cache_data(show_spinner=False)
def calcular_notas(_series: dict[str, pd.Series], descarga: datetime, anios: int = score.ANIOS,
                   pesos: tuple = ()):
    """Notas a cada fecha de COMPARACIONES + historia mensual. `descarga` invalida el cache al actualizar."""
    p = dict(pesos) if pesos else None
    notas = {k: score.calificar(_series, t, anios, p) for k, t in COMPARACIONES.items()}
    return notas, score.historia(_series, HOY, meses=60, anios=anios, pesos=p)


try:
    SERIES_NOTA = series_calificacion()
    NOTAS, HIST_NOTA = calcular_notas(SERIES_NOTA, ACTUALIZADO)
except Exception:  # noqa: BLE001 — sin la calificación el resto del tablero tiene que seguir andando
    traceback.print_exc()
    SERIES_NOTA = {}
    NOTAS = {k: {"total": None, "pilares": {}, "drivers": {}} for k in COMPARACIONES}
    HIST_NOTA = pd.DataFrame()


# (las cotizaciones del día van en la franja deslizante de arriba; el crédito y las fuentes, en el pie de la página)


@st.cache_data(show_spinner=False)
def historicos(_datos: dict, _dol: pd.DataFrame | None, descarga: datetime):
    """Series largas ya empalmadas + indicadores de cada mandato. `descarga` invalida el cache al actualizar.
    Devuelve (series, indicadores por mandato, nombres de series que faltan)."""
    necesarias = {
        "inflacion": _datos.get("inflacion_hist"), "pib_1986": _datos.get("serie:pib_1986"),
        "pib_1993": _datos.get("serie:pib_1993"), "pib_2004": _datos.get("serie:pib"),
        "paro_anual": _datos.get("serie:paro_anual"), "dolar_hist": _datos.get("dolar_hist"),
        "reservas_hist": _datos.get("serie:reservas_hist"), "reservas_actual": _datos.get("bcra:reservas"),
        "riesgo": _datos.get("riesgo_pais"), "dolares": _dol,
    }
    faltan = [k for k, v in necesarias.items() if not isinstance(v, pd.DataFrame) or v.empty]
    if faltan:
        return None, None, faltan
    dp = {k: v for k, v in necesarias.items() if k not in ("pib_1986", "pib_1993", "pib_2004", "dolares")}
    dp["pbi"] = presidentes.pbi_empalmado(necesarias["pib_1986"], necesarias["pib_1993"], necesarias["pib_2004"])
    dp["dolar_actual"] = _dol[["fecha", "oficial"]].dropna().rename(columns={"oficial": "valor"})
    trim = _datos.get("serie:desempleo")
    dp["paro_trim"] = trim if isinstance(trim, pd.DataFrame) else None
    return dp, {m.clave: presidentes.indicadores(m, dp) for m in presidentes.MANDATOS}, []


# ── Historia económica (línea de tiempo de presidentes) ──
def pantalla_historia() -> None:
    st.caption("Cómo recibió y cómo dejó la economía cada presidente desde la vuelta de la democracia. "
               "Los números se calculan con las series oficiales; en cada fila: **lo que recibió → cómo dejó** "
               "(o cómo está hoy, en el caso del presidente actual).")
    try:
        dp, inds, faltan = historicos(DATOS, dol, ACTUALIZADO)
    except Exception as e:  # noqa: BLE001 — una falla de cálculo no debe romper el resto de la app
        dp, inds, faltan = None, None, ["cálculo"]
    if faltan:
        st.warning("No se pudo armar la línea de tiempo. Falta o falló: " + ", ".join(faltan))
    else:
        fotos = fotos_presidentes()
        if inds:
            MS = presidentes.MANDATOS
            elegido = st.segmented_control("Gráfico", presidentes.GRAFICOS, default=presidentes.GRAFICOS[0],
                                key="hist_grafico", label_visibility="collapsed") or presidentes.GRAFICOS[0]
            serie_g, opciones_g = presidentes.grafico_historico(elegido, dp)
            fig_g = charts.serie_presidentes(serie_g, MS, presidentes.CORTO, **opciones_g)
            if st.toggle("Mostrar hitos económicos", key="hist_hitos",
                         help="Marca en el gráfico hechos con fecha (planes, crisis, cambios de régimen cambiario). Sin valoración."):
                fig_g = charts.marcar_eventos(fig_g, presidentes.EVENTOS, serie_g["fecha"].min())
            grafico(fig_g)

            # datos curiosos: hechos puros, con el nombre del mandato que los cumple (solo los que se pueden calcular)
            def mejor(clave_dato, key=max):
                cand = [(m, inds[m.clave][clave_dato]) for m in MS if inds[m.clave][clave_dato] is not None]
                return key(cand, key=lambda par: par[1]) if cand else None

            def con_signo(v: float, dec: int = 1) -> str:
                return ("+" if v >= 0 else "") + charts.num(v, dec)

            curiosos = []
            r_pbi = mejor("pbi")
            if r_pbi:
                curiosos.append(("Mayor crecimiento del PBI", r_pbi[0], f"{con_signo(r_pbi[1])}% en el mandato"))
            r_inf = mejor("inf_fin", key=min)
            if r_inf:
                curiosos.append(("Menor inflación anual al irse", r_inf[0], f"{charts.num(r_inf[1], 1)}% anual"))
            mult = [(m, inds[m.clave]["usd_fin"] / inds[m.clave]["usd_ini"]) for m in MS
                    if inds[m.clave]["usd_ini"] and inds[m.clave]["usd_fin"]]
            if mult:
                m_usd, v_usd = max(mult, key=lambda par: par[1])
                curiosos.append(("El dólar que más se multiplicó", m_usd, f"×{charts.num(v_usd, 1)} en el mandato"))
            if curiosos:
                for slot, (titulo_c, m_c, dato_c) in zip(st.columns(len(curiosos)), curiosos):
                    slot.metric(titulo_c, presidentes.CORTO[m_c.clave], dato_c, delta_color="off", border=True)

            # comparación entre mandatos: orden cronológico, un indicador a la vez
            st.markdown("#### Comparar mandatos")
            comp = st.segmented_control("Indicador", list(presidentes.COMPARACIONES), default="Inflación anual al irse",
                            key="hist_comp", label_visibility="collapsed") or "Inflación anual al irse"
            clave_c, unidad_c, ayuda_c = presidentes.COMPARACIONES[comp]
            vals_c = []
            for m in MS:
                i_ = inds[m.clave]
                if clave_c == "usd_mult":
                    v_ = i_["usd_fin"] / i_["usd_ini"] if i_["usd_ini"] and i_["usd_fin"] else None
                else:
                    v_ = i_.get(clave_c)
                vals_c.append(v_)
            grafico(charts.comparar_mandatos([presidentes.CORTO[m.clave] for m in MS], vals_c, comp,
                                             sufijo=unidad_c, dec=0 if clave_c == "res_fin" else 1,
                                             actual=presidentes.CORTO[MS[-1].clave] if MS[-1].hasta is None else None,
                                             logaritmica=clave_c in ("inf_fin", "inf_acum")))
            st.caption(ayuda_c + (" Escala logarítmica: cada marca vale 10 veces la anterior, así la hiperinflación no aplasta al resto."
                                  if clave_c in ("inf_fin", "inf_acum") else "") + " Barras en orden cronológico; la dorada es el mandato en curso. Los mandatos duraron "
                       "distinto y ocurrieron en contextos muy distintos: es información, no un ranking.")

            def iniciales(nombre: str) -> str:
                return "".join(p[0] for p in nombre.split() if p[0].isupper())[:2]

            items = [dict(
                nombre=m.nombre, periodo=m.periodo, anio=m.desde.year, iniciales=iniciales(m.nombre), hito=m.hito,
                filas=presidentes.filas(m, inds[m.clave]), pico=presidentes.pico_texto(m, inds[m.clave]),
                nota=m.nota, foto=fotos.get(m.clave, {}).get("url"), pagina=fotos.get(m.clave, {}).get("pagina"),
                actual=m.hasta is None,
            ) for m in MS]
            st.markdown(style.linea_tiempo(items), unsafe_allow_html=True)
            st.caption("Fotos: Wikipedia / Wikimedia Commons (licencias libres); tocá una foto para ir a su página. "
                       "Ojo: los mandatos duraron y ocurrieron en contextos muy distintos, así que comparar cifras entre épocas tiene límites.")
            with st.expander("Cómo se calcula cada cifra"):
                st.markdown(
                    """
- **Inflación anual:** variación de los 12 meses previos al último mes completo antes de asumir y antes de irse
  (para el presidente actual, el último dato publicado). *Entre 2007 y 2015 son las cifras oficiales del INDEC
  intervenido, que distintos analistas consideran subestimadas.*
- **PBI en el mandato:** crecimiento acumulado entre el PBI de los 4 trimestres previos a asumir y el de los 4 previos
  a irse (empalme de tres series oficiales: base 1986, 1993 y 2004).
- **Desocupación:** dato anual de la EPH (si el mandato empieza antes de noviembre se usa el año anterior).
- **Dólar oficial:** solo desde 1992; antes las series están en monedas de cada época (peso argentino, austral) y con
  tramos sin actualizar, por eso no se muestra para Alfonsín ni para el inicio de Menem.
- **Reservas:** brutas del BCRA, saldo de fin de mes. **Riesgo país:** disponible desde 1999.
- **Pico de inflación mensual:** un mes cuenta para quien estaba en el cargo a fin de ese mes.
- No se incluye pobreza: no existe una serie oficial continua desde 1983.
                    """
                )

# ── Calificación macro (dentro de Juegos y herramientas) ──
def _calificacion_contenido() -> None:
    if NOTAS["Hoy"]["total"] is None:
        st.warning("No hay datos suficientes para calcular la calificación.")
        return

    def restablecer_calificacion() -> None:
        """Vuelve la ventana a 5 años y todos los pesos a 25 (el punto de partida)."""
        st.session_state["cal_anios"] = 5
        for p_ in score.PILARES:
            st.session_state[f"cal_peso_{p_}"] = 25

    # el estado se inicializa acá (y no con `default=`) para poder restablecerlo desde el botón sin conflictos;
    # los controles están al final, pero su valor ya está disponible porque Streamlit conserva el estado entre corridas
    if st.session_state.get("cal_anios") not in (3, 5, 10):
        st.session_state["cal_anios"] = 5
    for p_ in score.PILARES:
        if not isinstance(st.session_state.get(f"cal_peso_{p_}"), int):
            st.session_state[f"cal_peso_{p_}"] = 25
    anios_sel = int(st.session_state["cal_anios"])
    pesos_sel = {p: int(st.session_state[f"cal_peso_{p}"]) for p in score.PILARES}
    notas_c, hist_c = calcular_notas(SERIES_NOTA, ACTUALIZADO, anios_sel, tuple(pesos_sel.items()))
    hoy_n, ref_n = notas_c["Hoy"], notas_c["Hace 1 año"]

    st.markdown(
        f"**Cómo leerla:** es una nota de 0 a 100 que dice si la economía está hoy mejor o peor que en los últimos "
        f"{anios_sel} años. **0** = el peor momento del período, **100** = el mejor, **50** = un momento típico. "
        "No mide si la economía está \"bien\" en términos absolutos."
    )
    if hoy_n["total"] is None:
        st.warning("Con esta ventana no hay datos suficientes. Probá con otra en «Ajustar el criterio», al final.")
        return

    # ── 1) La nota ──
    etq_hoy, color_hoy = score.nivel(hoy_n["total"])
    g, t = st.columns([1.1, 1.4], vertical_alignment="center")
    with g:
        grafico(charts.medidor(hoy_n["total"], etq_hoy, color_hoy, score.NIVELES, height=260))
    with t:
        st.markdown(score.lectura(hoy_n, ref_n, "hace un año"))
        if ref_n["total"] is not None:
            dif = round(hoy_n["total"] - ref_n["total"])
            k1, k2 = st.columns(2)
            k1.metric("Hoy", f"{hoy_n['total']:.0f}/100", border=True)
            k2.metric("Hace 1 año", f"{ref_n['total']:.0f}/100",
                      f"{dif:+d} pts hasta hoy" if dif else "sin cambios", delta_color="off", border=True)

    # ── 2) Los cuatro pilares ──
    st.subheader("Por área")
    DESC_PILAR = {"Precios": "Inflación actual y esperada", "Externo": "Reservas, riesgo país, dólar y comercio",
                  "Actividad": "Producción y empleo", "Ingresos": "Salarios reales"}
    for slot, pilar in zip(st.columns(len(score.PILARES)), score.PILARES):
        v = hoy_n["pilares"].get(pilar)
        a = ref_n["pilares"].get(pilar)
        if v is None:
            slot.metric(pilar, "s/d", border=True)
            continue
        slot.metric(pilar, f"{v:.0f}/100", None if a is None else f"{v - a:+.0f} vs hace 1 año",
                    delta_color="off", border=True, help=DESC_PILAR.get(pilar))
        slot.caption(f"**{score.nivel(v)[0]}** · {DESC_PILAR.get(pilar, '')}")

    # ── 3) Qué empuja la nota ──
    def valor_txt(d, fecha):
        s = SERIES_NOTA.get(d.clave)
        return charts.num(score.valor_en(s, fecha), d.dec, d.unidad) if s is not None else "s/d"

    ordenados = sorted((d for d in score.DRIVERS if d.clave in hoy_n["drivers"]),
                       key=lambda d: hoy_n["drivers"][d.clave], reverse=True)
    if ordenados:
        st.subheader("Qué la empuja")
        col_suma, col_resta = st.columns(2)
        with col_suma:
            st.markdown("##### Lo que más suma")
            for d in ordenados[:3]:
                p = hoy_n["drivers"][d.clave]
                st.markdown(f"- {score.frase_driver(d, valor_txt(d, HOY), p, anios_sel)}")
        with col_resta:
            st.markdown("##### Lo que más resta")
            for d in ordenados[::-1][:3]:
                p = hoy_n["drivers"][d.clave]
                st.markdown(f"- {score.frase_driver(d, valor_txt(d, HOY), p, anios_sel)}")

    # ── 4) Evolución ──
    grafico(charts.evolucion_nota(hist_c, score.NIVELES, "Cómo fue cambiando la nota (últimos 5 años)", height=360))

    # ── 5) Detalle (plegado) ──
    with st.expander("Ver los 9 indicadores uno por uno"):
        filas = []
        for d in score.DRIVERS:
            s = SERIES_NOTA.get(d.clave)
            if s is None:
                continue
            ahora = hoy_n["drivers"].get(d.clave)
            filas.append({
                "Área": d.pilar, "Indicador": d.nombre, "Valor hoy": valor_txt(d, HOY),
                "Hace 1 año": valor_txt(d, COMPARACIONES["Hace 1 año"]),
                "Conviene": "que suba" if d.mejor == "alto" else "que baje",
                "Lectura": "s/d" if ahora is None else score.etiqueta_driver(ahora),
                "Puntaje": ahora,
            })
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch",
                     column_config={"Puntaje": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f")})
        movimientos = [(hoy_n["drivers"][d.clave] - ref_n["drivers"][d.clave], d) for d in ordenados
                       if ref_n["drivers"].get(d.clave) is not None]
        movimientos.sort(key=lambda m: m[0])
        mejoras = [m for m in movimientos[::-1][:3] if m[0] > 1]
        caidas = [m for m in movimientos[:3] if m[0] < -1]
        c_up, c_down = st.columns(2)
        with c_up:
            st.markdown("##### Lo que más mejoró en el año")
            for dif, d in mejoras:
                st.markdown(f"- **{d.nombre}:** {valor_txt(d, COMPARACIONES['Hace 1 año'])} → {valor_txt(d, HOY)} ({dif:+.0f} pts)")
            if not mejoras:
                st.caption("Nada relevante.")
        with c_down:
            st.markdown("##### Lo que más empeoró en el año")
            for dif, d in caidas:
                st.markdown(f"- **{d.nombre}:** {valor_txt(d, COMPARACIONES['Hace 1 año'])} → {valor_txt(d, HOY)} ({dif:+.0f} pts)")
            if not caidas:
                st.caption("Nada relevante.")

    # ── 6) Criterio ajustable (plegado) ──
    with st.expander("Ajustar el criterio (opcional)"):
        st.caption("La nota depende de dos decisiones que podés mover: contra cuánta historia se compara y cuánto pesa cada área.")
        st.pills("Comparar contra los últimos…", [3, 5, 10], key="cal_anios", format_func=lambda a: f"{a} años")
        cols_p = st.columns(len(score.PILARES))
        for i, p in enumerate(score.PILARES):
            cols_p[i].slider(p, 0, 100, key=f"cal_peso_{p}")
        st.caption("Los pesos se normalizan solos (importa la proporción). Con todos en 0 se usan iguales.")
        st.button("Restablecer valores de partida", on_click=restablecer_calificacion,
                  help="Ventana de 5 años y las 4 áreas con el mismo peso.")

    with st.expander("Cómo se calcula y qué no mide"):
        st.markdown(
            f"""
- Cada **indicador** recibe un puntaje de **0 a 100**: en qué lugar queda su valor actual comparado con su propia historia
  de los **últimos {anios_sel} años**. Un 90 significa «mejor que el 90% de ese período». Si conviene que baje
  (inflación, riesgo país, brecha, desocupación), se invierte.
- Los indicadores se promedian por **área** (Precios, Externo, Actividad, Ingresos) y las áreas se combinan con los pesos
  elegidos (por defecto, iguales) en la **nota total**.
- Para comparar con períodos anteriores se repite el cálculo *a esa fecha*, usando solo los datos que existían entonces.
- Niveles: Muy favorable ≥ 75 · Favorable ≥ 60 · Neutral ≥ 40 · Adversa ≥ 25 · Muy adversa < 25.
- **Qué no mide:** es una medida **relativa** (mejor o peor que el pasado reciente), no absoluta. No incluye deuda ni pobreza.
  Cambiar la ventana o los pesos puede mover mucho el resultado. No es un pronóstico ni asesoramiento financiero.
            """
        )


def pantalla_calificacion() -> None:
    with protegido("Calificación"):
        _calificacion_contenido()


# ── Interactivo ──
def pantalla_juegos() -> None:
    try:
        dp_i, inds_i, faltan_i = historicos(DATOS, dol, ACTUALIZADO)
    except Exception as e:  # noqa: BLE001
        dp_i, inds_i, faltan_i = None, None, ["cálculo"]
    if faltan_i:
        st.warning("No se pudieron cargar los datos necesarios para las herramientas interactivas. "
                   "Falta o falló: " + ", ".join(faltan_i))
        pantalla_calificacion()
    else:
        dp_i = {**dp_i, "uva": uva}
        interactivo.mostrar(dp_i, inds_i, fotos_presidentes(), uva, extra={"Calificación macro": pantalla_calificacion})


# ── Criptomonedas ──
def _usd_cripto(v: float | None) -> str:
    if v is None or v != v:
        return "s/d"
    return charts.num(v, 0 if v >= 1000 else 2 if v >= 1 else 4, pre="US$ ")


def _nombre_exchange(k: str) -> str:
    """'binancep2p' -> 'Binance P2P', 'lemoncashp2p' -> 'Lemoncash P2P', 'ripioexchange' -> 'Ripioexchange'."""
    p2p = k.endswith("p2p")
    base = k[:-3] if p2p else k
    return base.capitalize() + (" P2P" if p2p else "")


def pantalla_cripto() -> None:
    cr = cargar_cripto()
    reintentar_si_fallo(cargar_cripto, "cripto", any(isinstance(v, str) for v in cr.values()))
    mercado, usdt = cr["mercado"], cr["usdt"]
    st.caption("Las principales criptomonedas, en dólares y en pesos, y a cuánto se compra y vende el USDT en los "
               "exchanges argentinos. Se actualiza cada 5 minutos.")
    if isinstance(mercado, str) or mercado.empty:
        st.warning(f"No se pudo cargar el mercado de criptomonedas ahora. Se reintenta solo en un minuto. ({mercado})")
    else:
        tarjetas = []
        for _, c in mercado.iterrows():
            tarjetas.append(dict(
                nombre=c["nombre"], desc=c["simbolo"], valor=_usd_cripto(c["usd"]),
                detalle=f"≈ {charts.num(c['ars'], 0, pre='$')}" if c["ars"] == c["ars"] else "en pesos: s/d",
                var=c["cambio_24h"], var_txt="24 h", extras=[("7 d", c["cambio_7d"])], sentido="alto",
                spark=list(c["spark"]), ))
        st.markdown(style.cotizaciones(tarjetas), unsafe_allow_html=True)

        monedas = mercado[~mercado["simbolo"].isin(["USDT", "USDC"])].head(6)  # las estables no tienen qué graficar
        c1, c2 = st.columns([3, 2])
        elegida = c1.pills("Moneda", list(monedas["simbolo"]), default=monedas["simbolo"].iloc[0], key="cripto_moneda",
                           label_visibility="collapsed") or monedas["simbolo"].iloc[0]
        rangos = {"1 mes": 30, "3 meses": 90, "1 año": 365}
        rango = c2.pills("Rango", list(rangos), default="1 año", key="cripto_rango", label_visibility="collapsed") or "1 año"
        fila = monedas[monedas["simbolo"] == elegida]
        if not fila.empty:
            hist = historia_cripto(fila.iloc[0]["id"], rangos.get(rango, 365))
            if isinstance(hist, str) or hist.empty:
                st.info(f"No se pudo cargar el historial de {fila.iloc[0]['nombre']} ahora. ({hist})")
            else:
                grafico(charts.lineas(hist, {f"{fila.iloc[0]['nombre']} (US$)": "valor"},
                                      f"{fila.iloc[0]['nombre']} en dólares — {rango.lower()}", yfmt=",.0f", height=340))
        st.caption("El historial gratuito de CoinGecko llega hasta 1 año atrás.")

    st.subheader("USDT en pesos: ¿dónde conviene?")
    if isinstance(usdt, str) or usdt.empty:
        st.info(f"No se pudieron cargar los precios del USDT por exchange ahora. ({usdt})")
    else:
        oficial_hoy = ultimo(dol[["fecha", "oficial"]].dropna().rename(columns={"oficial": "valor"})) if dol is not None else None
        mejor_compra, mejor_venta = usdt.iloc[0], usdt.sort_values("venta", ascending=False).iloc[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("Comprar USDT más barato", charts.num(float(mejor_compra["compra"]), 0, pre="$"),
                  _nombre_exchange(mejor_compra["exchange"]), delta_color="off", border=True)
        k2.metric("Vender USDT más caro", charts.num(float(mejor_venta["venta"]), 0, pre="$"),
                  _nombre_exchange(mejor_venta["exchange"]), delta_color="off", border=True)
        if oficial_hoy:
            k3.metric("USDT vs dólar oficial", f"{(mejor_compra['compra'] / oficial_hoy - 1) * 100:+.1f}%".replace(".", ","),
                      "al comprar en el más barato", delta_color="off", border=True)
        filas = [[_nombre_exchange(r["exchange"]), charts.num(float(r["compra"]), 0, pre="$"),
                  charts.num(float(r["venta"]), 0, pre="$"),
                  (f"{(r['compra'] / oficial_hoy - 1) * 100:+.1f}%".replace(".", ",") if oficial_hoy else "s/d")]
                 for _, r in usdt.head(10).iterrows()]
        st.markdown(style.tabla_simple(["Exchange", "Comprar USDT", "Vender USDT", "Compra vs oficial"], filas),
                    unsafe_allow_html=True)
        st.caption("Precios sin comisiones, de CriptoYa. «Comprar» es lo que pagás por cada USDT; «Vender», lo que recibís. "
                   "No es una recomendación de inversión.")


# ── Bolsas ──
def _var_pct(df: pd.DataFrame, dias: int | None = None) -> float | None:
    """Variación % del último cierre contra el anterior (dias=None) o contra hace `dias` días corridos."""
    if len(df) < 2:
        return None
    ult = df.iloc[-1]
    if dias is None:
        ref = float(df.iloc[-2]["valor"])
    else:
        previos = df[df["fecha"] <= ult["fecha"] - pd.Timedelta(days=dias)]
        if previos.empty:
            return None
        ref = float(previos.iloc[-1]["valor"])
    return None if ref == 0 else (float(ult["valor"]) / ref - 1) * 100


def pantalla_bolsas() -> None:
    mk = cargar_mercados()
    reintentar_si_fallo(cargar_mercados, "mercados", any(isinstance(v, str) for v in mk.values()))
    st.caption("Las principales bolsas del mundo y algunas materias primas que mueven a la Argentina. Datos de Yahoo "
               "Finance (fuente no oficial, con demora); se actualizan cada 15 minutos.")
    tarjetas = []
    for simbolo, nombre, grupo, unidad in data.INDICES:
        df = mk.get(simbolo)
        if not isinstance(df, pd.DataFrame) or len(df) < 2:
            continue
        ult = float(df.iloc[-1]["valor"])
        tarjetas.append(dict(
            nombre=nombre, desc=grupo, valor=charts.num(ult, 0 if ult >= 1000 else 2), detalle=unidad,
            var=_var_pct(df), var_txt="1 d", extras=[("30 d", _var_pct(df, 30))],
            sentido="neutro" if grupo == "Materias primas" else "alto", spark=list(df.tail(30)["valor"])))
    if not tarjetas:
        st.warning("No se pudieron cargar las cotizaciones de las bolsas ahora. Se reintenta solo en un minuto.")
        return
    st.markdown(style.cotizaciones(tarjetas), unsafe_allow_html=True)
    faltan = [n for s, n, _, _ in data.INDICES if not isinstance(mk.get(s), pd.DataFrame)]
    if faltan:
        st.caption("Sin datos por ahora: " + ", ".join(faltan) + ".")

    st.subheader("Comparar")
    nombres = {n: s for s, n, g, _ in data.INDICES if g != "Materias primas" and isinstance(mk.get(s), pd.DataFrame)}
    elegidas = st.pills("Bolsas a comparar", list(nombres), selection_mode="multi",
                        default=[n for n in ("Merval", "S&P 500") if n in nombres], key="bolsas_sel",
                        label_visibility="collapsed") or []
    per_b = selector_periodo("bolsas", "1 año")
    series = {}
    for n in elegidas:
        d = rec(mk[nombres[n]], 0, per_b)
        if len(d) >= 2 and d.iloc[0]["valor"]:
            series[n] = d.set_index("fecha")["valor"] / float(d.iloc[0]["valor"]) * 100
    if series:
        ancho = pd.concat(series, axis=1, sort=True).reset_index().rename(columns={"index": "fecha"})
        grafico(charts.lineas(ancho, {n: n for n in series}, "Evolución de las bolsas — base 100 = inicio del período",
                              yfmt=",.0f", height=380))
        st.caption("Cada índice en su moneda: el Merval está en pesos, así que también refleja la inflación y el tipo de cambio.")
    else:
        st.info("Elegí al menos una bolsa para ver el gráfico.")


# ── Franja deslizante superior ──
def construir_ticker() -> list[dict]:
    """Datos clave para la franja de arriba. Cada pieza es opcional: lo que falte simplemente no aparece."""
    items: list[dict] = []

    def poner(nombre: str, valor: str, d: float | None = None, sentido: str = "neutro") -> None:
        items.append(dict(n=nombre, v=valor, d=d, sentido=sentido))

    if dol is not None:
        for clave, nombre in (("oficial", "Dólar oficial"), ("blue", "Blue"), ("bolsa", "MEP"),
                              ("contadoconliqui", "CCL"), ("cripto", "Dólar cripto")):
            if clave in dol:
                s = dol[["fecha", clave]].dropna().rename(columns={clave: "valor"})
                if not s.empty:
                    poner(nombre, charts.num(ultimo(s), 0, pre="$"), delta(s, dias=1))
    for clave, nombre in (("fx:EUR", "Euro"), ("fx:GBP", "Libra")):
        d_ = DATOS.get(clave)
        if isinstance(d_, pd.DataFrame) and not d_.empty:
            poner(nombre, charts.num(ultimo(d_), 0, pre="$"), delta(d_, dias=1))
    if riesgo is not None:
        poner("Riesgo país", charts.num(ultimo(riesgo), 0, suf=" pb"), delta(riesgo, dias=1), "bajo")
    if reservas is not None:
        poner("Reservas", charts.num(ultimo(reservas), 0, pre="USD ", suf=" M"), delta(reservas, dias=1), "alto")
    if infl_m is not None:
        poner("Inflación mensual", charts.num(ultimo(infl_m), 1, suf="%"))
    if badlar is not None:
        poner("BADLAR", charts.num(ultimo(badlar), 1, suf="%"))
    cr = cargar_cripto()
    reintentar_si_fallo(cargar_cripto, "cripto", any(isinstance(v, str) for v in cr.values()))
    m = cr.get("mercado")
    if isinstance(m, pd.DataFrame) and not m.empty:
        for sim in ("BTC", "ETH"):
            f = m[m["simbolo"] == sim]
            if not f.empty:
                poner(sim, _usd_cripto(f.iloc[0]["usd"]), f.iloc[0]["cambio_24h"], "alto")
    mk = cargar_mercados()
    reintentar_si_fallo(cargar_mercados, "mercados", any(isinstance(v, str) for v in mk.values()))
    for simbolo, nombre, sentido in (("^MERV", "Merval", "alto"), ("^GSPC", "S&P 500", "alto"), ("^DJI", "Dow Jones", "alto"),
                                     ("GC=F", "Oro", "neutro"), ("CL=F", "Petróleo", "neutro"), ("ZS=F", "Soja", "neutro")):
        df = mk.get(simbolo)
        if isinstance(df, pd.DataFrame) and len(df) >= 2:
            ult = float(df.iloc[-1]["valor"])
            poner(nombre, charts.num(ult, 0 if ult >= 1000 else 2), _var_pct(df), sentido)
    return items


def pie_pagina() -> None:
    st.markdown(style.footer(), unsafe_allow_html=True)


# ───────────────────────── encabezado ─────────────────────────
try:
    st.markdown(style.ticker(construir_ticker()), unsafe_allow_html=True)
except Exception:  # noqa: BLE001 — la franja es un adorno: si falla, la página sigue sin ella
    traceback.print_exc()
pagina_legal = st.query_params.get("legal")
if isinstance(pagina_legal, str) and pagina_legal in legal.PAGINAS:
    # Términos y condiciones / política de privacidad (se llega desde los enlaces del pie de página)
    st.markdown('<a href="./" target="_self">← Volver al tablero</a>', unsafe_allow_html=True)
    st.markdown(style.legal_pagina(legal.PAGINAS[pagina_legal], legal.ACTUALIZACION), unsafe_allow_html=True)
    pie_pagina()
    st.stop()

if vista != "tablero":
    # Vistas aparte (Historia económica, Juegos): reemplazan al tablero y no ocupan una pestaña.
    titulos = {"historia": "Historia económica", "juegos": "Juegos y herramientas"}
    pantallas = {"historia": pantalla_historia, "juegos": pantalla_juegos}
    st.button("← Volver al tablero", on_click=ir_a, args=("tablero",))
    st.subheader(titulos[vista])
    with protegido(titulos[vista]):
        pantallas[vista]()
    pie_pagina()
    st.stop()

t_res, t_dol, t_cri, t_bol, t_res_i, t_act, t_sal, t_prec, t_tasas, t_din, t_com, t_fis = st.tabs(
    ["Inicio", "Dólar", "Cripto", "Bolsas", "Reservas", "Actividad y PBI", "Salarios", "Precios y UVA",
     "Tasas y riesgo país", "Dinero y crédito", "Comercio exterior", "Resultado fiscal"]
)

# ───────────────────────── indicadores personalizables ─────────────────────────
PREFS_ARCHIVO = Path(__file__).parent / ".macrocenter_prefs.json"
KPIS_DEFECTO = ["oficial", "riesgo", "reservas", "infl_m", "infl_ia"]

dol_s = {c: dol[["fecha", c]].dropna().rename(columns={c: "valor"})
         for c in ("oficial", "blue", "bolsa", "contadoconliqui")} if dol is not None else {}
brecha_df = dol.dropna(subset=["brecha_blue"]) if dol is not None else None
emae_ia = yoy(emae) if emae is not None else None
paro_pct = paro.assign(valor=paro["valor"] * 100) if paro is not None else None
sal_ia = yoy(sal) if sal is not None else None
sal_real_df = salario_real()


def _kpi(df: pd.DataFrame | None, col: str = "valor", dias: int = 30, modo: str = "pct", **kw):
    """Devuelve una función que calcula los argumentos de `kpi` (o 's/d' si falta la serie)."""
    def calcular() -> dict:
        if df is None:
            return {"valor": None}
        return dict(valor=ultimo(df, col), d=delta(df, col, dias=dias, modo=modo), **kw)
    return calcular


_MES = dict(dias=25, modo="abs", d_suf=" pp", d_txt="vs mes ant.")

# clave -> (grupo, nombre, función). El orden de este diccionario es el orden del selector.
CATALOGO = {
    "oficial": ("Dólar", "Dólar oficial", _kpi(dol_s.get("oficial"), dec=0, pre="$", help="Precio de venta")),
    "blue": ("Dólar", "Dólar blue", _kpi(dol_s.get("blue"), dec=0, pre="$", help="Precio de venta")),
    "mep": ("Dólar", "Dólar MEP", _kpi(dol_s.get("bolsa"), dec=0, pre="$", help="Precio de venta")),
    "ccl": ("Dólar", "Dólar CCL", _kpi(dol_s.get("contadoconliqui"), dec=0, pre="$", help="Precio de venta")),
    "brecha": ("Dólar", "Brecha blue / oficial", _kpi(brecha_df, "brecha_blue", modo="abs", dec=1, suf="%", d_suf=" pp")),
    "reservas": ("Sector externo", "Reservas (USD M)", _kpi(reservas, dec=0, color="normal")),
    "riesgo": ("Sector externo", "Riesgo país (pb)", _kpi(riesgo, modo="abs", dec=0, d_suf=" pb", color="inverse")),
    "badlar": ("Tasas", "BADLAR (TNA)", _kpi(badlar, modo="abs", dec=1, suf="%", d_suf=" pp")),
    "pases": ("Tasas", "Pases 1 día (TNA)", _kpi(pases, modo="abs", dec=1, suf="%", d_suf=" pp",
                                                 help="Tasa de referencia vigente. La API del BCRA no registra tasa de "
                                                      "política monetaria después de julio de 2025.")),
    "uva": ("Tasas", "UVA", _kpi(uva, dec=2, pre="$")),
    "infl_m": ("Precios", "Inflación mensual", _kpi(infl_m, dec=1, suf="%", color="inverse", **_MES)),
    "infl_ia": ("Precios", "Inflación interanual", _kpi(infl_ia, dec=1, suf="%", color="inverse", **_MES)),
    "rem": ("Precios", "Inflación esperada 12 m", _kpi(rem, dec=1, suf="%", color="inverse", **_MES)),
    "emae": ("Actividad", "EMAE interanual", _kpi(emae_ia, dec=1, suf="%", color="normal", **_MES)),
    "paro": ("Actividad", "Desocupación (EPH)", _kpi(paro_pct, dec=1, suf="%", color="inverse", dias=80, modo="abs",
                                                      d_suf=" pp", d_txt="vs trim. ant.")),
    "sal_nom": ("Ingresos", "Salarios interanual", _kpi(sal_ia, dec=1, suf="%", color="normal",
                                                        help="Índice de salarios INDEC, total", **_MES)),
    "salario_real": ("Ingresos", "Salario real interanual", _kpi(sal_real_df, "real", dec=1, suf="%", color="normal",
                                                                 help="Salarios nominales descontada la inflación", **_MES)),
    "ripte": ("Ingresos", "RIPTE", _kpi(ripte, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.")),
    "smvm": ("Ingresos", "Salario mínimo", _kpi(smvm, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.")),
    "haber": ("Ingresos", "Haber mínimo jubilatorio", _kpi(haber_min, dias=25, dec=0, pre="$", color="normal",
                                                           d_txt="vs mes ant.")),
}


def cargar_prefs() -> list[str]:
    try:
        if not LOCAL:
            return list(KPIS_DEFECTO)
        elegidos = json.loads(PREFS_ARCHIVO.read_text(encoding="utf-8")).get("kpis", KPIS_DEFECTO)
        return [k for k in elegidos if k in CATALOGO]
    except (OSError, ValueError, AttributeError):
        return list(KPIS_DEFECTO)


def guardar_prefs() -> None:
    try:
        if LOCAL:
            PREFS_ARCHIVO.write_text(json.dumps({"kpis": st.session_state["kpis_sel"]}), encoding="utf-8")
    except OSError:
        pass  # sin permiso de escritura: la elección vale solo para esta sesión


def restablecer_prefs() -> None:
    st.session_state["kpis_sel"] = list(KPIS_DEFECTO)
    guardar_prefs()


if "kpis_sel" not in st.session_state:
    st.session_state["kpis_sel"] = cargar_prefs()

def panel_plazo_fijo() -> None:
    # Rendimiento real de un plazo fijo: lo que rinde la tasa menos lo que subieron los precios, mes a mes.
    st.subheader("¿Le ganó el plazo fijo a la inflación?")
    if badlar is not None and infl_m is not None:
        tasa_m = badlar.set_index("fecha")["valor"].resample("ME").mean().rename("tna").reset_index()
        real = tasa_m.merge(infl_m.rename(columns={"valor": "inflacion"}), on="fecha")
        real["real"] = ((1 + real["tna"] / 1200) / (1 + real["inflacion"] / 100) - 1) * 100
        real = real.replace([float("inf"), float("-inf")], float("nan")).dropna(subset=["real"])
        if real.empty:
            st.info("Todavía no hay datos suficientes para calcular el rendimiento real.")
        else:
            ult = real.iloc[-1]
            k = st.columns(3)
            kpi(k[0], "Rinde la tasa (mensual)", float(ult["tna"]) / 12, 1, suf="%", help="BADLAR (TNA) dividida por 12")
            kpi(k[1], "Suben los precios (mensual)", float(ult["inflacion"]), 1, suf="%")
            kpi(k[2], "Rendimiento real del mes", float(ult["real"]), 1, suf="%", color="normal",
                help="Positivo: la tasa le ganó a la inflación. Negativo: el ahorro perdió poder de compra.")
            grafico(charts.barras(con_periodo("res_real", real, 2), "real",
                                  "Rendimiento real mensual de un plazo fijo (%)", yfmt=",.1f", height=300))
            st.caption("Usa la tasa BADLAR (depósitos a plazo de bancos privados) como referencia de un plazo fijo, promedio del "
                       "mes, contra la inflación de ese mes. No incluye impuestos ni comisiones.")
    else:
        st.info("No se pudieron cargar la tasa o la inflación para este panel.")


# ── Inicio ──
with t_res, protegido("Inicio"):
    # el estado de sesión puede traer claves viejas o inválidas: se filtra antes de dibujar el selector
    previos = st.session_state.get("kpis_sel")
    st.session_state["kpis_sel"] = [k for k in (previos if isinstance(previos, list) else [])
                                    if isinstance(k, str) and k in CATALOGO]
    h, p = st.columns([5, 1.5], vertical_alignment="center")
    h.subheader("Indicadores clave")
    with p.popover("Personalizar", width="stretch"):
        st.caption("Elegí qué indicadores ver (y en qué orden). Tu elección queda guardada.")
        st.multiselect(
            "Indicadores", options=list(CATALOGO), key="kpis_sel", on_change=guardar_prefs,
            format_func=lambda k: f"{CATALOGO[k][0]} · {CATALOGO[k][1]}", label_visibility="collapsed",
            placeholder="Elegí indicadores…",
        )
        st.button("Restablecer los de siempre", on_click=restablecer_prefs, width="stretch")
    elegidos = st.session_state["kpis_sel"]
    if not elegidos:
        st.info("No elegiste ningún indicador. Usá **Personalizar** para agregar los que quieras ver.")
    for i in range(0, len(elegidos), 5):
        for slot, clave in zip(st.columns(5), elegidos[i:i + 5]):
            try:
                kpi(slot, CATALOGO[clave][1], **CATALOGO[clave][2]())
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                kpi(slot, CATALOGO[clave][1], None)

    # un solo gráfico a la vez (el usuario elige cuál), para que la portada no se llene
    OPC = ["Dólar", "Inflación", "Reservas", "Riesgo país"]
    elegido_i = st.segmented_control("Gráfico", OPC, default="Dólar", key="inicio_grafico", label_visibility="collapsed") or "Dólar"
    if elegido_i == "Dólar" and dol is not None:
        grafico(charts.lineas(con_periodo("res_dolar", dol_rec), {"Oficial": "oficial", "Blue": "blue"}, "Dólar ($)", height=340))
    elif elegido_i == "Inflación" and infl_m is not None and infl_ia is not None:
        m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
        grafico(charts.barras_y_linea(con_periodo("res_infl", m, 2, "5 años"), "valor_m", "valor_ia", "Inflación (%)",
                                      "Mensual", "Interanual", height=340))
    elif elegido_i == "Reservas" and reservas is not None:
        grafico(charts.lineas(con_periodo("res_reservas", reservas), {"Reservas brutas": "valor"},
                              "Reservas internacionales (USD millones)", height=340))
    elif elegido_i == "Riesgo país" and riesgo is not None:
        grafico(charts.lineas(con_periodo("res_riesgo", riesgo), {"Riesgo país": "valor"},
                              "Riesgo país (puntos básicos)", height=340))
    else:
        st.info("No se pudo cargar este gráfico.")

    # ¿Qué le ganó a la inflación? Variación de cada alternativa de ahorro en el mismo período.
    st.divider()
    st.subheader("¿Qué le ganó a la inflación?")
    ventanas = {"3 meses": 3, "6 meses": 6, "1 año": 12}
    vent = st.segmented_control("Período", list(ventanas), default="1 año", key="rend_periodo",
                                label_visibility="collapsed") or "1 año"
    n_m = ventanas[vent]
    try:
        corte = HOY - pd.DateOffset(months=n_m)
        nombres_r, valores_r = [], []

        def variacion(s: pd.Series) -> float | None:
            s = s.dropna()
            s = s[s.index <= HOY]
            antes = s[s.index <= corte]
            if s.empty or antes.empty or antes.iloc[-1] == 0:
                return None
            return float((s.iloc[-1] / antes.iloc[-1] - 1) * 100)

        if dol is not None:
            for col, nom in (("oficial", "Dólar oficial"), ("blue", "Dólar blue"), ("bolsa", "Dólar MEP")):
                if col in dol:
                    v_ = variacion(dol.set_index("fecha")[col])
                    if v_ is not None:
                        nombres_r.append(nom); valores_r.append(v_)
        if uva is not None:
            v_ = variacion(uva.set_index("fecha")["valor"])
            if v_ is not None:
                nombres_r.append("UVA"); valores_r.append(v_)
        infl_p = None
        if infl_m is not None:
            im_ = infl_m[(infl_m["fecha"] <= HOY)].dropna(subset=["valor"]).tail(n_m)
            if len(im_) == n_m:
                infl_p = float(((1 + im_["valor"] / 100).prod() - 1) * 100)
        if badlar is not None:
            tm_ = badlar[badlar["fecha"] <= HOY].set_index("fecha")["valor"].resample("ME").mean().dropna().tail(n_m)
            if len(tm_) == n_m:
                nombres_r.append("Plazo fijo (BADLAR)")
                valores_r.append(float(((1 + tm_ / 1200).prod() - 1) * 100))
        if len(valores_r) >= 2:
            grafico(charts.rendimientos(nombres_r, valores_r, infl_p, f"Variación en los últimos {vent} (%)"))
            st.caption("En verde, lo que superó a la inflación del período (línea punteada); en rojo, lo que quedó abajo. "
                       "Es el pasado: no anticipa qué va a pasar. El plazo fijo se aproxima con la tasa BADLAR, sin impuestos "
                       "ni comisiones; el dólar se mide sin considerar costos de compra o venta.")
        else:
            st.info("No hay datos suficientes para este comparativo.")
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        st.info("No se pudo armar este comparativo.")


# ── Criptomonedas ──
with t_cri, protegido("Criptomonedas"):
    pantalla_cripto()

# ── Bolsas ──
with t_bol, protegido("Bolsas"):
    pantalla_bolsas()

# ── Dólar ──
with t_dol, protegido("Dólar"):
    if dol is not None:
        TIPOS_DOLAR = [
            ("oficial", "Dólar oficial", "Banco Nación, venta minorista"),
            ("mayorista", "Dólar mayorista", "Entre grandes operadores"),
            ("blue", "Dólar blue", "Mercado informal"),
            ("bolsa", "Dólar MEP", "Compra de bonos en bolsa"),
            ("contadoconliqui", "Dólar CCL", "Contado con liquidación, giro al exterior"),
            ("cripto", "Dólar cripto", "Vía stablecoins (USDT)"),
            ("tarjeta", "Dólar tarjeta", "Consumos en el exterior: oficial + impuestos"),
        ]
        oficial_hoy = ultimo(dol[["fecha", "oficial"]].dropna().rename(columns={"oficial": "valor"}))
        tarjetas_usd = []
        for clave, nombre, desc in TIPOS_DOLAR:
            s = dol[["fecha", clave, f"{clave}_compra"]].dropna(subset=[clave])
            if s.empty:
                continue
            venta, compra = float(s.iloc[-1][clave]), s.iloc[-1][f"{clave}_compra"]
            tarjetas_usd.append(dict(
                nombre=nombre, desc=desc, valor=charts.num(venta, 0, pre="$"),
                detalle=f"Compra {charts.num(float(compra), 0, pre='$')} · Venta {charts.num(venta, 0, pre='$')}",
                var=delta(s.rename(columns={clave: "valor"})),
                spark=list(s.tail(30)[clave]), spark_color="#74ACDF",
                chip=None if clave == "oficial" or not oficial_hoy else
                f"{(venta / oficial_hoy - 1) * 100:+.0f}% vs oficial".replace(".", ","),
            ))
        st.markdown(style.cotizaciones(tarjetas_usd), unsafe_allow_html=True)
        st.caption(f"Cotizaciones al {dol['fecha'].max():%d/%m/%Y} (ArgentinaDatos). La variación compara con 30 días atrás.")

        eur, gbp = get("fx:EUR"), get("fx:GBP")
        tarjetas_fx = []
        for df_, nombre, simbolo in ((eur, "Euro", "€"), (gbp, "Libra esterlina", "£")):
            if df_ is not None:
                u = df_.iloc[-1]
                tarjetas_fx.append(dict(
                    nombre=nombre, desc="Cotización de referencia del BCRA",
                    valor=charts.num(float(u["valor"]), 0, pre="$"),
                    detalle=f"1 {simbolo} = US$ {charts.num(float(u['pase']), 2)}",
                    var=delta(df_), chip=None, spark=list(df_.tail(30)["valor"]), spark_color="#74ACDF"))
        if tarjetas_fx:
            st.markdown(style.cotizaciones(tarjetas_fx), unsafe_allow_html=True)
            st.caption("Euro y libra: referencia cambiaria del BCRA en pesos por unidad (no es el precio de la casa de cambio).")

        r = con_periodo("dolar", dol_rec)
        grafico(charts.lineas(r, {"Oficial": "oficial", "Mayorista": "mayorista", "Blue": "blue", "MEP": "bolsa",
                                  "CCL": "contadoconliqui", "Cripto": "cripto", "Tarjeta": "tarjeta"},
                              "Cotizaciones del dólar — precio de venta ($)", height=460,
                              ocultas=("Mayorista", "Cripto", "Tarjeta")))
        st.caption("Tocá un nombre en la leyenda para mostrar u ocultar cada dólar.")
        with st.expander("Brecha cambiaria y evolución relativa"):
            a, b = st.columns(2)
            with a:
                grafico(charts.lineas(r, {"Blue vs oficial": "brecha_blue", "CCL vs oficial": "brecha_ccl"},
                                      "Brecha cambiaria (%)", yfmt=",.0f"))
            with b:
                base = base100(r, ["oficial", "blue"])
                grafico(charts.lineas(base, {"Oficial": "oficial", "Blue": "blue"},
                                      "Evolución base 100 = inicio del período", yfmt=",.0f"))
        with st.expander("Últimas cotizaciones (venta)"):
            tabla = dol[["fecha", "oficial", "mayorista", "blue", "bolsa", "contadoconliqui", "cripto", "tarjeta",
                         "brecha_blue", "brecha_ccl"]].tail(10).sort_values("fecha", ascending=False).rename(columns={
                "fecha": "Fecha", "oficial": "Oficial", "blue": "Blue", "bolsa": "MEP",
                "contadoconliqui": "CCL", "mayorista": "Mayorista", "cripto": "Cripto", "tarjeta": "Tarjeta",
                "brecha_blue": "Brecha blue %", "brecha_ccl": "Brecha CCL %"})
            st.dataframe(tabla, hide_index=True, width="stretch",
                         column_config={"Fecha": st.column_config.DateColumn(format="DD/MM/YYYY")})

# ── Reservas ──
with t_res_i, protegido("Reservas"):
    if reservas is not None:
        per_res = selector_periodo("reservas")
        r = rec(reservas, 0, per_res)
        c = st.columns(3)
        f_res = reservas[reservas["fecha"] <= HOY].dropna(subset=["valor"])
        kpi(c[0], f"Último dato ({f_res['fecha'].iloc[-1]:%d/%m/%Y})" if not f_res.empty else "Último dato",
            ultimo(reservas), 0, pre="USD ", suf=" M",
            help="Serie oficial del BCRA, que se publica con 1 o 2 días de demora. La cifra que el BCRA difunde en sus "
                 "redes el mismo día es provisoria y puede diferir.")
        if len(r) > 1:
            kpi(c[1], f"Variación en {per_res.lower()}", r["valor"].iloc[-1] - r["valor"].iloc[0], 0,
                pre="USD ", suf=" M", color="normal")
            kpi(c[2], "Máximo del período", r["valor"].max(), 0, pre="USD ", suf=" M")
        grafico(charts.lineas(r, {"Reservas brutas": "valor"}, "Reservas internacionales del BCRA (USD millones)",
                              height=460))
        with st.expander("Variación mensual"):
            rm = reservas.set_index("fecha")["valor"].resample("ME").last().diff().rename("var").reset_index()
            grafico(charts.barras(rec(rm.dropna(), 2), "var", "Variación mensual de reservas (USD millones)", yfmt=",.0f"))

# ── Actividad y PBI ──
with t_act, protegido("Actividad y PBI"):
    if pib is not None:
        p = pib.copy()
        p["interanual"] = p["valor"].pct_change(4) * 100
        p["trimestral"] = p["valor"].pct_change() * 100
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(p, 5), {"PBI real": "valor"}, "PBI trimestral a precios constantes de 2004 (millones de $)"))
        with b:
            grafico(charts.barras(rec(p.dropna(subset=["interanual"]), 5), "interanual",
                                  "PBI — variación interanual (%)"))
        st.caption("Serie trimestral sin desestacionalizar de Cuentas Nacionales (INDEC). "
                   f"Último trimestre disponible: {p['fecha'].iloc[-1]:%m/%Y} (inicio de trimestre).")
    if emae_sa is not None:
        mom = get("serie:emae_sa_mom")
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(emae_sa, 3), {"EMAE desestacionalizado": "valor"},
                                  "EMAE desestacionalizado (base 2004 = 100)", yfmt=",.0f"))
        with b:
            if mom is not None:
                grafico(charts.barras(rec(mom, 3), "valor", "EMAE — variación mensual desestacionalizada (%)", yfmt=",.1f"))
    if emae is not None:
        with st.expander("EMAE interanual y desocupación"):
            e = emae.assign(interanual=emae["valor"].pct_change(12) * 100).dropna()
            a, b = st.columns(2)
            with a:
                grafico(charts.barras(rec(e, 3), "interanual", "EMAE — variación interanual (%)"))
            with b:
                if paro is not None:
                    grafico(charts.lineas(rec(paro.assign(valor=paro["valor"] * 100), 5), {"Desocupación": "valor"},
                                          "Tasa de desocupación (EPH, %)", yfmt=",.1f"))

# ── Salarios ──
with t_sal, protegido("Salarios"):
    if sal is not None:
        base = sal.rename(columns={"valor": "Total"})
        for df_, nombre in ((sal_priv, "Privado registrado"), (sal_pub, "Público")):
            if df_ is not None:
                base = base.merge(df_.rename(columns={"valor": nombre}), on="fecha", how="outer")
        base = base.sort_values("fecha")
        cols = {n: n for n in ("Total", "Privado registrado", "Público") if n in base}
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(base, 3), cols, "Índice de salarios INDEC (oct-2016 = 100)"))
        sr = salario_real()
        with b:
            if sr is not None:
                grafico(charts.lineas(rec(sr, 3), {"Salarios (nominal)": "salario", "Inflación": "inflacion"},
                                      "Salarios vs inflación — variación interanual (%)", yfmt=",.0f"))
        with st.expander("Salario real, RIPTE, salario mínimo y haber mínimo"):
            a, b = st.columns(2)
            with a:
                if sr is not None:
                    grafico(charts.barras(rec(sr, 3), "real", "Salario real — variación interanual (%)"))
            with b:
                if ripte is not None:
                    grafico(charts.lineas(rec(ripte, 3), {"RIPTE": "valor"}, "RIPTE — remuneración imponible promedio ($)"))
            if smvm is not None or haber_min is not None:
                piso = None
                for df_, nombre in ((smvm, "Salario mínimo, vital y móvil"), (haber_min, "Haber mínimo jubilatorio")):
                    if df_ is not None:
                        df_ = df_.rename(columns={"valor": nombre})
                        piso = df_ if piso is None else piso.merge(df_, on="fecha", how="outer")
                piso = piso.sort_values("fecha")
                grafico(charts.lineas(rec(piso, 3), {c_: c_ for c_ in piso.columns if c_ != "fecha"},
                                      "Salario mínimo y haber mínimo jubilatorio ($ mensuales)", height=340))
    st.caption("Índice de salarios y RIPTE: INDEC / Secretaría de Seguridad Social, con rezago de ~2 meses. "
               "El salario real se calcula como (1 + salario nominal) / (1 + inflación) − 1, interanual.")

# ── Precios y UVA ──
with t_prec, protegido("Precios y UVA"):
    if infl_m is not None and infl_ia is not None:
        m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
        a, b = st.columns(2)
        with a:
            grafico(charts.barras_y_linea(rec(m, 2), "valor_m", "valor_ia", "Inflación (IPC INDEC, %)",
                                          "Mensual", "Interanual"))
        with b:
            if rem is not None:
                x = m[["fecha", "valor_ia"]].rename(columns={"valor_ia": "Inflación interanual observada"})
                y = rem.rename(columns={"valor": "Expectativa 12 m (REM)"})
                grafico(charts.lineas(x.merge(y, on="fecha", how="outer").sort_values("fecha").pipe(rec, 2),
                                      {"Interanual observada": "Inflación interanual observada",
                                       "Expectativa 12 m (REM)": "Expectativa 12 m (REM)"},
                                      "Inflación interanual vs. expectativas del REM (%)", yfmt=",.0f"))
    if uva is not None and dol is not None:
        comp = pd.merge_asof(rec(dol_rec).dropna(subset=["oficial"])[["fecha", "oficial", "blue"]],
                             uva.rename(columns={"valor": "uva"}), on="fecha")
        comp = base100(comp, ["oficial", "blue", "uva"])
        grafico(charts.lineas(comp, {"UVA": "uva", "Dólar oficial": "oficial", "Dólar blue": "blue"},
                              "UVA vs dólar — base 100 = inicio del período", yfmt=",.0f", height=340))
    with st.expander("Índices de ajuste: UVA, CER, UVI e ICL"):
        pares = [("bcra:uva", "UVA (pesos)", ",.0f"), ("bcra:cer", "CER (base 2/2/2002 = 1)", ",.0f"),
                 ("bcra:uvi", "UVI (pesos)", ",.0f"), ("bcra:icl", "ICL — Índice para Contratos de Locación", ",.1f")]
        for fila in (pares[:2], pares[2:]):
            cols = st.columns(2)
            for col, (clave, titulo, fmt) in zip(cols, fila):
                d = get(clave)
                if d is not None:
                    with col:
                        grafico(charts.lineas(rec(d), {titulo: "valor"}, titulo, yfmt=fmt, height=320))

# ── Tasas y riesgo país ──
with t_tasas, protegido("Tasas y riesgo país"):
    panel_plazo_fijo()
    st.divider()
    if pases is not None or tpm is not None:
        ref = None
        for df_, nombre in ((tpm, "Tasa de política monetaria"), (pases, "Pases a 1 día")):
            if df_ is not None:
                df_ = df_.rename(columns={"valor": nombre})
                ref = df_ if ref is None else ref.merge(df_, on="fecha", how="outer")
        ref = ref.sort_values("fecha")
        grafico(charts.lineas(rec(ref, 3), {c_: c_ for c_ in ref.columns if c_ != "fecha"},
                              "Tasa de política monetaria y tasa de pases a 1 día (TNA, %)", yfmt=",.0f", paso=True))
        st.caption("La API del BCRA no registra datos de tasa de política monetaria después del 10/07/2025 "
                   "(último valor: 29% TNA). Como referencia vigente se muestra la tasa de pases a 1 día.")
    a, b = st.columns(2)
    with a:
        tasas = {}
        base = None
        for clave, nombre in [("bcra:badlar", "BADLAR"), ("bcra:tamar", "TAMAR"), ("bcra:depositos_30d", "Plazo fijo 30 d")]:
            d = get(clave)
            if d is not None:
                d = d.rename(columns={"valor": nombre})
                base = d if base is None else base.merge(d, on="fecha", how="outer")
                tasas[nombre] = nombre
        if base is not None:
            grafico(charts.lineas(rec(base.sort_values("fecha")), tasas, "Tasas de interés en pesos (TNA, %)", yfmt=",.0f"))
    with b:
        pp = get("bcra:prestamos_personales")
        if pp is not None:
            grafico(charts.lineas(rec(pp), {"Préstamos personales": "valor"}, "Tasa de préstamos personales (TNA, %)", yfmt=",.0f"))
    if riesgo is not None:
        grafico(charts.lineas(rec(riesgo), {"Riesgo país": "valor"}, "Riesgo país — EMBI (puntos básicos)", height=420))

# ── Dinero y crédito ──
with t_din, protegido("Dinero y crédito"):
    a, b = st.columns(2)
    bm, pr, m2 = get("bcra:base_monetaria"), get("bcra:prestamos_privados"), get("bcra:m2_privado_ia")
    with a:
        if bm is not None:
            grafico(charts.lineas(rec(bm.assign(valor=bm["valor"] / 1e6)), {"Base monetaria": "valor"},
                                  "Base monetaria (billones de $)", yfmt=",.1f"))
    with b:
        if m2 is not None:
            grafico(charts.lineas(rec(m2), {"M2 privado": "valor"},
                                  "M2 privado — var. interanual del promedio móvil 30 d (%)", yfmt=",.0f"))
    if pr is not None:
        grafico(charts.lineas(rec(pr.assign(valor=pr["valor"] / 1e6)), {"Préstamos al sector privado": "valor"},
                              "Préstamos al sector privado (billones de $)", yfmt=",.1f"))

# ── Comercio exterior ──
with t_com, protegido("Comercio exterior"):
    if comercio is not None:
        c = comercio
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(c, 3), {"Exportaciones": "exp", "Importaciones": "imp"},
                                  "Exportaciones e importaciones (USD millones)"))
        with b:
            grafico(charts.barras(rec(c, 3), "saldo", "Saldo comercial mensual (USD millones)", yfmt=",.0f"))
        grafico(charts.lineas(rec(c.dropna(subset=["saldo_12m"]), 3), {"Saldo acumulado 12 m": "saldo_12m"},
                              "Saldo comercial acumulado 12 meses (USD millones)", yfmt=",.0f", height=320))


# ── Resultado fiscal ──
with t_fis, protegido("Resultado fiscal"):
    f = fiscal_df()
    if f.empty:
        st.warning("No se pudieron cargar los datos fiscales o el PBI para calcular el porcentaje.")
    else:
        ult_f = f.iloc[-1]
        st.caption(f"Sector público nacional no financiero, base caja, como porcentaje del PBI. Último dato: {ult_f['fecha']:%m/%Y}. "
                   "Positivo = superávit, negativo = déficit.")
        k = st.columns(4)
        for slot, (nombre, col, ayuda) in zip(k, [
                ("Primario 12 meses", "primario_12m", "Suma de los últimos 12 meses sobre el PBI de ese período."),
                ("Financiero 12 meses", "financiero_12m", "Suma de los últimos 12 meses sobre el PBI de ese período."),
                ("Primario del mes", "primario", "El resultado del mes sobre 1/12 del PBI. Cambia mucho de mes a mes (aguinaldo, vencimientos)."),
                ("Financiero del mes", "financiero", "El resultado del mes sobre 1/12 del PBI. Cambia mucho de mes a mes (aguinaldo, vencimientos).")]):
            v = ult_f.get(col)
            kpi(slot, nombre, None if pd.isna(v) else float(v), 1, suf="% del PBI", help=ayuda)
        st.caption("Primario: ingresos menos gastos, sin contar intereses de la deuda. Financiero: lo que queda después de pagar intereses.")
        cols_12 = [c for c in ("primario_12m", "financiero_12m") if c in f and f[c].notna().any()]
        if cols_12:
            nombres = {"primario_12m": "Primario", "financiero_12m": "Financiero"}
            fig12 = charts.lineas(con_periodo("fis_12m", f.dropna(subset=cols_12, how="all"), 3, "5 años"),
                                  {nombres[c]: c for c in cols_12}, "Resultado acumulado de 12 meses (% del PBI)",
                                  yfmt=",.1f", height=340)
            fig12.add_hline(y=0, line_width=1, line_dash="dot", line_color="rgba(128,128,128,.7)")
            grafico(fig12)
        a, b = st.columns(2)
        with a:
            if "primario" in f:
                grafico(charts.barras(con_periodo("fis_prim", f, 3, "5 años"), "primario",
                                      "Resultado primario mensual (% del PBI)", yfmt=",.1f", height=320))
        with b:
            if "financiero" in f:
                grafico(charts.barras(con_periodo("fis_fin", f, 3, "5 años"), "financiero",
                                      "Resultado financiero mensual (% del PBI)", yfmt=",.1f", height=320))
        with st.expander("Cómo se calcula el porcentaje del PBI"):
            st.markdown(
                "- **Resultado:** informe mensual de ingresos y gastos del Ministerio de Economía (base caja).\n"
                "- **PBI:** a precios corrientes, trimestral anualizado del INDEC. Para cada mes se usa el promedio de los últimos "
                "4 trimestres; pasado el último trimestre publicado, se lo actualiza con la inflación mensual (no incluye "
                "crecimiento real, por eso las últimas cifras son una estimación).\n"
                "- **Mensual:** resultado del mes sobre 1/12 del PBI. Es muy variable; mirá el acumulado de 12 meses para la tendencia.\n"
                "- Puede diferir de las cifras que publica el Gobierno, que usan su propio PBI y criterios de ajuste (por ejemplo, "
                "ingresos extraordinarios).")
        st.caption("Fuente: Ministerio de Economía (IMIG, Informe Mensual de Ingresos y Gastos) e INDEC, vía datos.gob.ar.")


pie_pagina()
