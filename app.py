"""MacroCenter — tablero de datos macroeconómicos de Argentina.

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import hashlib
import inspect
import importlib
import json
import os
import re
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from macrocenter import (carga, charts, data, datos_vista, glosario, interactivo, inversiones, legal, mapa, ministros, news, pestanas,
                         presidentes, selector, series, style)
from macrocenter.avisos import actualizando, falla
from macrocenter.carga import (  # descarga, cachés y copia de respaldo
    _estado_actualizar, _memoria, _precalentar, _ultima_carga, _va_a_demorar, cargar_bonos, cargar_cripto, cargar_fotos,
    cargar_inversiones, cargar_mercados, cargar_noticias, cargar_todo, cargar_vivo, con_dolar_vivo, con_riesgo_vivo,
    envejecer_disco, protegido, reintentar_si_fallo,
)

# Módulos de presentación sin estado: recargarlos evita mezclar pantallas anteriores con la navegación nueva.
for modulo in (carga, data, datos_vista, series, style, charts, inversiones, interactivo,
               *(getattr(pestanas, nombre) for nombre in pestanas.__all__)):
    importlib.reload(modulo)

st.set_page_config(page_title="MacroCenter", page_icon=style.favicon(), layout="wide")
st.session_state["_fallas"] = []  # fallas de datos de esta corrida (no se muestran; las lee el monitor)
st.session_state["_n_graf"] = 0  # numera los gráficos de esta corrida (claves de sus botones de descarga)

# fecha argentina: el servidor publicado anda en UTC y desde las 21 h ya estaría en el día siguiente
HOY = pd.Timestamp(data.hoy_argentina())
PERIODOS = {"1 mes": 30, "6 meses": 182, "1 año": 365, "2 años": 730, "5 años": 1825, "Todo": None}


def abrir(pestana, *args) -> None:
    """Dibuja una pantalla de macrocenter/pestanas/: le pasa `args` y, por nombre, los datos y funciones de esta página
    que su `mostrar` declara después del asterisco (así cada archivo dice de qué depende)."""
    firma = inspect.signature(pestana.mostrar).parameters.values()
    pestana.mostrar(*args, **{p.name: globals()[p.name] for p in firma if p.kind is inspect.Parameter.KEYWORD_ONLY})


_precalentar()  # en paralelo con la carga de las series (solo hace algo con el servidor recién prendido)
if _va_a_demorar():
    _carga = st.empty()
    _carga.html(style.pantalla_carga(*glosario.termino_del_dia(HOY)))
    DATOS, ACTUALIZADO = cargar_todo()
    _carga.empty()
else:
    DATOS, ACTUALIZADO = cargar_todo()
_ultima_carga()["t"] = time.time()
reintentar_si_fallo(cargar_todo, "datos", any(isinstance(v, str) for v in DATOS.values()))


def fotos_presidentes() -> dict[str, dict]:
    f = cargar_fotos()
    reintentar_si_fallo(cargar_fotos, "fotos", not f)
    return f


@st.cache_data(ttl=86400, show_spinner=False)
def cargar_fotos_ministros() -> dict[str, str]:
    """Fotos de los ministros de Economía (Wikipedia/Commons). Se piden una vez por día."""
    return ministros.fotos()


def fotos_ministros() -> dict[str, str]:
    f = cargar_fotos_ministros()
    reintentar_si_fallo(cargar_fotos_ministros, "fotos_ministros", not f)
    return f


NOMBRES_DATOS = {  # cómo se llama cada serie en los avisos (la clave interna no le dice nada a quien lee)
    "bcra:reservas": "reservas del BCRA", "bcra:tc_minorista": "dólar minorista del BCRA",
    "bcra:tc_mayorista": "dólar mayorista del BCRA", "bcra:badlar": "tasa BADLAR", "bcra:depositos_30d": "tasa de plazo fijo",
    "bcra:prestamos_personales": "tasa de préstamos personales", "bcra:pases_1d": "tasa de pases",
    "bcra:tpm": "tasa de política monetaria", "bcra:base_monetaria": "base monetaria", "bcra:m2_privado_ia": "M2 privado",
    "bcra:prestamos_privados": "préstamos al sector privado", "bcra:inflacion_mensual": "inflación mensual",
    "bcra:inflacion_interanual": "inflación interanual", "bcra:rem_12m": "inflación esperada (REM)", "bcra:cer": "CER",
    "bcra:uva": "UVA", "bcra:uvi": "UVI", "bcra:icl": "ICL", "bcra:tamar": "tasa TAMAR", "serie:pib": "PBI",
    "serie:emae": "EMAE", "serie:emae_sa": "EMAE desestacionalizado", "serie:emae_sa_mom": "EMAE mensual",
    "serie:desempleo": "desocupación", "serie:salarios": "índice de salarios", "serie:ripte": "RIPTE",
    "serie:smvm": "salario mínimo", "serie:haber_minimo": "haber mínimo jubilatorio",
    "serie:exportaciones": "exportaciones", "serie:importaciones": "importaciones", "serie:ipim": "IPIM", "serie:ipp": "IPP", "serie:ipc_gba": "IPC GBA",
    "dolares": "cotizaciones del dólar", "riesgo_pais": "riesgo país", "fx:EUR": "euro", "fx:GBP": "libra",
}


def get(clave: str) -> pd.DataFrame | None:
    d = DATOS.get(clave)
    if isinstance(d, pd.DataFrame) and not d.empty:
        return d
    nombre = NOMBRES_DATOS.get(clave, clave.split(":")[-1].replace("_", " "))
    falla(f"no se pudo cargar «{nombre}» ({d if isinstance(d, str) else 'sin datos'})")  # sin aviso en pantalla
    return None


# ───────────────────────── noticias (ventana emergente) ─────────────────────────
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
            "noviembre", "diciembre"]


# Los archivos de preferencias solo se usan al correr en la propia computadora (run.bat define MACROCENTER_LOCAL=1).
# Publicada en internet, cada visita guarda sus elecciones solo en su sesión: nada se comparte entre usuarios.
LOCAL = os.environ.get("MACROCENTER_LOCAL") == "1"


def _id_nota(url: str) -> str:
    """Identificador corto de una noticia (8 caracteres de la huella de su enlace): lo único que se recuerda de ella."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]


def _ids_validos(texto) -> set[str]:
    return {x for x in str(texto or "").split(",") if re.fullmatch(r"[0-9a-f]{8}", x)}


def leidas() -> set[str]:
    """Identificadores de las noticias que este navegador marcó como leídas. Los guarda el propio navegador
    (almacenamiento local, nunca el servidor): al abrir la página, un script los copia en un campo oculto de la
    barra lateral («puente_leidas») y desde ahí llegan acá."""
    if "noticias_leidas" not in st.session_state:
        st.session_state["noticias_leidas"] = set()
    puente = _ids_validos(st.session_state.get("leidas_cli"))
    if not puente <= st.session_state["noticias_leidas"]:
        st.session_state["noticias_leidas"] = st.session_state["noticias_leidas"] | puente
    return st.session_state["noticias_leidas"]


def script_guardar_leidas() -> str:
    """Script que deja las leídas en el almacenamiento local del navegador. Solo lleva identificadores hexadecimales:
    nada de la persona ni de la nota. Se mantienen las de las noticias que están hoy y, de las demás, hasta 150."""
    hoy = {_id_nota(x.url) for items in cargar_noticias().values() if isinstance(items, list) for x in items}
    todas = sorted(leidas(), key=lambda i: i not in hoy)[:150]
    st.session_state["noticias_leidas"] = set(todas)
    return ("<script>(() => { try { localStorage.setItem('mc_leidas', " + json.dumps(",".join(todas)) + "); "
            "document.cookie = 'mc_leidas=; Max-Age=0; Path=/'; } catch (e) {} })();</script>")


def marcar_leidas() -> None:
    """Marca como leídas todas las notas que se ven hoy."""
    vistas = {_id_nota(x.url) for items in cargar_noticias().values() if isinstance(items, list) for x in items}
    st.session_state["noticias_leidas"] = vistas | set(leidas())


def marcar_leida(url: str) -> None:
    """Marca como leída una sola nota."""
    st.session_state["noticias_leidas"] = {_id_nota(url)} | set(leidas())


def md_seguro(texto: str) -> str:
    """Escapa todo lo que Markdown podría interpretar en un texto que viene de afuera (enlaces, HTML, fórmulas, listas)."""
    return re.sub(r"([\\`*_{}\[\]()<>#+\-!|~$&])", r"\\\1", texto or "")



def noticias_recientes(dias: int = 1) -> int:
    """Cuántas notas sin leer se publicaron hoy o ayer (hora argentina). 0 si no se pudieron leer.
    Antes contaba toda la semana: como en la versión publicada lo «leído» dura solo la visita, cada vez que alguien
    entraba aparecían como nuevas notas de hace varios días."""
    if not _ids_validos(st.session_state.get("leidas_cli")):
        return 0  # el navegador todavía no dijo qué tiene leído: sin cuenta, para no mostrar un dato equivocado
    hoy = pd.Timestamp(data.hoy_argentina())
    total = 0
    noticias = cargar_noticias()
    for items in noticias.values():
        if isinstance(items, list):
            total += sum(1 for x in items
                         if 0 <= (hoy - pd.Timestamp(x.fecha).normalize()).days <= dias and _id_nota(x.url) not in leidas())
    return total


def es_nueva(n: news.Noticia) -> bool:
    """Misma regla que el contador del botón: sin leer y publicada hoy o ayer (hora argentina)."""
    hoy = pd.Timestamp(data.hoy_argentina())
    return _id_nota(n.url) not in leidas() and 0 <= (hoy - pd.Timestamp(n.fecha).normalize()).days <= 1


@st.dialog("Noticias oficiales", width="large")
def ver_noticias() -> None:
    noticias = cargar_noticias()
    fuentes = {"bcra": "BCRA", "economia": "Economía", "indec": "INDEC"}
    pares = [(n, k) for k in fuentes for n in (noticias.get(k) if isinstance(noticias.get(k), list) else [])]
    hay_sin_leer = any(es_nueva(n) for n, _ in pares)
    st.html(script_guardar_leidas(), unsafe_allow_javascript=True)  # recuerda lo leído en este navegador

    c_filtro, c_boton = st.columns([3, 1.4], vertical_alignment="center")
    filtro = selector.uno(c_filtro.segmented_control, "Fuente", ["Todas", *fuentes.values()], "news_filtro",
                          label_visibility="collapsed")
    if hay_sin_leer:
        # al tocarlo se marca todo y el diálogo se redibuja solo: el botón pasa a verde
        c_boton.button("Marcar todas como leídas", key="btn_marcar_leidas", icon=":material/done_all:", on_click=marcar_leidas,
                       width="stretch",
                       help="Apaga el aviso del botón de noticias hasta que haya novedades.")
    elif c_boton.button("Todo leído", key="btn_todo_leido", icon=":material/check_circle:", width="stretch",
                        help="No hay novedades sin leer. Tocalo para cerrar y actualizar el aviso."):
        st.rerun()  # cierra el diálogo y refresca el botón de la barra lateral

    for k, nombre in fuentes.items():
        if isinstance(noticias.get(k), str) or not noticias.get(k):
            falla(f"no se pudieron leer las noticias de {nombre}")
    visibles = sorted(((n, k) for n, k in pares if filtro == "Todas" or fuentes[k] == filtro),
                      key=lambda par: par[0].fecha, reverse=True)
    if not visibles:
        st.markdown(style.lista_noticias([], MESES_ES), unsafe_allow_html=True)
    for n, k in visibles[:14]:
        item = style.lista_noticias([dict(titulo=n.titulo, url=n.url, fecha=n.fecha, resumen=n.resumen,
                                          fuente=fuentes[k], clase=k, nueva=es_nueva(n))], MESES_ES)
        if es_nueva(n):
            # cada nota nueva trae su propio botón: al tocarlo solo esa pasa a leída y el diálogo se redibuja
            c_nota, c_leer = st.columns([6, 1.3], vertical_alignment="center", gap="small")
            c_nota.markdown(item, unsafe_allow_html=True)
            c_leer.button("Leída", icon=":material/check:", key=f"leer_{hashlib.sha1(n.url.encode()).hexdigest()[:12]}", on_click=marcar_leida,
                          args=(n.url,), width="stretch", help="Marca solo esta noticia como leída.")
        else:
            st.markdown(item, unsafe_allow_html=True)
    st.markdown(style.pie_noticias([("Banco Central", news.BCRA_URL), ("Ministerio de Economía", news.ECONOMIA_URL),
                                      ("INDEC", news.INDEC_URL)]),
                unsafe_allow_html=True)


# ───────────────────────── barra lateral ─────────────────────────
style.aplicar()


def ir_a(destino: str) -> None:
    """Cambia la vista principal: 'tablero' (pestañas), 'inversiones', 'historia' o 'juegos'."""
    st.session_state["vista"] = destino


VISTAS = ("tablero", "inversiones", "historia", "juegos")
# primero el ala financiera (lo que más se usa): dólar, bolsas, cripto, tasas y dinero; después precios, actividad,
# sector externo, ingresos y cuentas públicas
PESTANAS = ["Resumen", "Dólar", "Bolsas", "Cripto", "Bonos", "Inflación y dinero", "Tasas y riesgo país",
            "Actividad y PBI", "Reservas", "Salarios", "Resultado fiscal", "Comercio exterior"]
HIST_SECCIONES = ["Presidentes", "Ministros de Economía", "Viaje en el tiempo"]
# Enlaces para compartir: ?ver=tablero/dolar, ?ver=herramientas/ajuste-de-alquileres, etc. (la misma ruta que cuenta
# las visitas, ver seccion_actual). Se lee una sola vez por visita; después la dirección sigue a lo que se mira.
RUTAS = {"tablero": ("tablero", "pestana", PESTANAS), "inversiones": ("inversiones", "inv_seccion", inversiones.SECCIONES),
         "historia": ("historia", "hist_seccion", HIST_SECCIONES),
         "herramientas": ("juegos", "inter_modo", interactivo.MODOS)}


def abrir_ruta(ruta) -> None:
    """Pone la vista y la sección que pide el enlace. Una ruta desconocida o alterada se ignora (queda el tablero)."""
    if not isinstance(ruta, str) or len(ruta) > 80:
        return
    base, _, sub = ruta.strip("/").partition("/")
    if base == "herramientas" and sub == "viaje-en-el-tiempo":  # enlace viejo: el viaje pasó a Historia económica
        base = "historia"
    if base not in RUTAS:
        return
    vista_, clave, opciones = RUTAS[base]
    st.session_state["vista"] = vista_
    # enlaces viejos: secciones que cambiaron de nombre o se juntaron con otra
    sub = {"conceptos": "glosario", "como-les-fue": "rendimientos-pasados", "inicio": "resumen",
           "tasas-de-hoy": "tasas-y-plazos-fijos", "plazo-fijo-vs-uva": "tasas-y-plazos-fijos",
           "inflacion": "inflacion-y-dinero", "dinero-y-credito": "inflacion-y-dinero"}.get(sub, sub)
    elegida = next((o for o in opciones if style.slug(o) == sub), None)
    if elegida:
        st.session_state[clave] = elegida


if not st.session_state.get("_ruta_leida"):
    st.session_state["_ruta_leida"] = True
    abrir_ruta(st.query_params.get("ver"))
vista = st.session_state.setdefault("vista", "tablero")
if vista not in VISTAS:  # estado viejo o inválido: se vuelve al tablero
    vista = st.session_state["vista"] = "tablero"

# círculo de carga en la zona principal mientras se arma la barra lateral y se piden los datos del momento; se va
# cuando empieza el contenido (ver «encabezado»). Solo en la primera carga de cada visita: en las siguientes la página
# ya está a la vista y el círculo la empujaría hacia abajo. Si todo es rápido, no llega a verse.
_cargando_inicio = st.empty()
if not st.session_state.get("_ya_cargo"):
    _cargando_inicio.html(style.cargando())

def ir_al_resumen() -> None:
    """Lo que hace el logo: abre el tablero en Resumen sin recargar la página (ver JS_PESTANAS)."""
    st.session_state["vista"] = "tablero"
    st.session_state["pestana"] = "Resumen"


with st.sidebar:
    st.markdown(style.marca(), unsafe_allow_html=True)
    # contenedor oculto: el campo por el que el navegador le pasa a la app las noticias que ya marcó como leídas (ver
    # leidas()) y el botón que toca el logo para ir al Resumen sin recargar la página
    with st.container(key="puente_leidas"):
        st.text_input("Noticias leídas", key="leidas_cli", label_visibility="collapsed", max_chars=1400)
        st.button("Ir al resumen", key="ir_resumen", on_click=ir_al_resumen)
    nuevas = noticias_recientes()
    if nuevas:
        etiqueta_noticias = f"Noticias · {nuevas} {'nueva' if nuevas == 1 else 'nuevas'}"
    else:
        etiqueta_noticias = "Noticias"
    # la clave distinta cuando hay novedades activa el puntito rojo pulsante (ver style.py)
    if st.button(etiqueta_noticias, width="stretch", key="btn_noticias_nuevas" if nuevas else "btn_noticias",
                 icon=":material/newspaper:",
                 help="Últimas novedades del BCRA y del Ministerio de Economía"
                      + (f" ({nuevas} publicadas hoy o ayer, sin leer)" if nuevas else "")):
        ver_noticias()
    st.markdown(style.etiqueta("Explorar"), unsafe_allow_html=True)
    for clave_vista, texto, icono_v in (("tablero", "Tablero", ":material/dashboard:"),
                                        ("inversiones", "Ahorro e inversiones", ":material/account_balance_wallet:"),
                                        ("juegos", "Herramientas", ":material/handyman:"),
                                        ("historia", "Historia económica", ":material/history_edu:")):
        st.button(texto, width="stretch", key=f"nav_{clave_vista}", icon=icono_v, on_click=ir_a, args=(clave_vista,),
                  type="primary" if vista == clave_vista else "secondary")

def rec(df: pd.DataFrame, min_anios: int = 0, periodo: str = "2 años") -> pd.DataFrame:
    """Recorta al `periodo` (por defecto 2 años) y a fechas ya ocurridas (UVA/CER/ICL traen días futuros).
    `min_anios` garantiza una ventana mínima para series de baja frecuencia."""
    out = df[df["fecha"] <= HOY]
    dias = PERIODOS.get(periodo, PERIODOS["2 años"]) if periodo in PERIODOS else PERIODOS["2 años"]
    if dias is None:
        return out
    return out[out["fecha"] >= HOY - pd.Timedelta(days=max(dias, min_anios * 365))]


def selector_periodo(clave: str, defecto: str = "2 años", mensual: bool = False,
                     opciones: list[str] | None = None) -> str:
    """Botones de período propios de un gráfico (cada gráfico importante tiene el suyo).
    Con datos mensuales no se ofrece «1 mes» (quedaría un solo punto). `opciones` permite un juego propio
    (por ejemplo «1 mes / 3 meses / 1 año»). La clave empieza con `per_`: el estilo de style.py se engancha ahí."""
    opciones = list(opciones) if opciones else [o for o in PERIODOS if not (mensual and o == "1 mes")]
    return selector.uno(st.pills, "Período", opciones, f"per_{clave}", defecto, label_visibility="collapsed")


def selector_categoria(etiqueta: str, opciones: list, clave: str, defecto=None, multi: bool = False):
    """Fichas para elegir QUÉ se mira (un índice, una moneda, un gráfico). Se ven distinto del período a propósito.
    La clave empieza con `cat_`: el estilo de style.py se engancha ahí. Devuelve el elegido (o la lista, si `multi`)."""
    if not multi:
        return selector.uno(st.pills, etiqueta, opciones, f"cat_{clave}", defecto, label_visibility="collapsed")
    return st.pills(etiqueta, list(opciones), selection_mode="multi", default=defecto,
                    key=f"cat_{clave}", label_visibility="collapsed")


def con_periodo(clave: str, df: pd.DataFrame, min_anios: int = 0, defecto: str = "2 años", mensual: bool = False) -> pd.DataFrame:
    """Recorta `df` al período elegido. `min_anios` fuerza una ventana mínima (solo para series muy poco frecuentes);
    para series mensuales conviene `mensual=True`: cada botón recorta de verdad, desde 6 meses."""
    return rec(df, min_anios, selector_periodo(clave, defecto, mensual))


def _grafico_periodo(clave: str, df: pd.DataFrame, armar, min_anios: int = 0, defecto: str = "2 años",
                     mensual: bool = False) -> None:
    grafico(armar(con_periodo(clave, df, min_anios, defecto, mensual)), key=f"graf_{clave}")


@st.fragment
def grafico_periodo(clave: str, df: pd.DataFrame, armar, min_anios: int = 0, defecto: str = "2 años",
                    mensual: bool = False) -> None:
    """Botones de período + gráfico como «fragmento»: al tocar un período se redibuja solo este gráfico, no la app
    entera (responde al instante). `armar` recibe el df recortado y devuelve la figura."""
    _grafico_periodo(clave, df, armar, min_anios, defecto, mensual)


@st.fragment
def graficos_fiscales(f: pd.DataFrame) -> None:
    """Resultado fiscal: un solo selector de período para el acumulado de 12 meses y los dos mensuales (antes cada
    gráfico tenía el suyo y la pestaña quedaba cargada de botones repetidos)."""
    st.markdown("#### Resultado mensual")
    per = selector_periodo("fis", "5 años", mensual=True)
    cols_12 = [c for c in ("primario_12m", "financiero_12m") if c in f and f[c].notna().any()]
    if cols_12:
        nombres = {"primario_12m": "Primario", "financiero_12m": "Financiero"}
        fig = charts.lineas(rec(f.dropna(subset=cols_12, how="all"), 0, per), {nombres[c]: c for c in cols_12},
                            "Resultado acumulado de 12 meses (% del PBI)", yfmt=",.1f", height=340)
        fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="rgba(128,128,128,.7)")
        grafico(fig, key="graf_fis_12m")
    a, b = st.columns(2)
    for slot, c, titulo in ((a, "primario", "Resultado primario mensual (% del PBI)"),
                            (b, "financiero", "Resultado financiero mensual (% del PBI)")):
        if c in f:
            with slot:
                grafico(charts.barras(rec(f, 0, per), c, titulo, yfmt=",.1f", height=320), key=f"graf_fis_{c}")


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
        d: float | None = None, d_suf: str = "%", d_txt: str = "vs 30 d", color: str = "normal", help: str | None = None,
        d_dec: int = 1, serie=None, fuente: str = "", max_dias: int | None = None):
    # color por defecto: verde si sube, rojo si baja (precios). Los indicadores donde subir es malo
    # (inflación, riesgo país, desocupación) pasan color="inverse".
    # una variación que redondeada da 0,0 no lleva flecha (una flecha para arriba con 0,0% confunde)
    plano = d is not None and abs(d) < 0.5 * 10 ** -d_dec
    slot.metric(
        label,
        charts.num(valor, dec, suf, pre),
        None if d is None else (f"sin cambios {d_txt}" if plano else f"{charts.num(d, d_dec, d_suf)} {d_txt}"),
        delta_color="off" if plano else color,
        delta_arrow="off" if plano else "auto",
        help=help,
        border=True,
    )

    if fuente:
        slot.markdown(datos_vista.detalle(serie, fuente, max_dias=max_dias), unsafe_allow_html=True)


MAX_PUNTOS = 1000  # una línea de ~1.000 px de ancho no muestra más detalle que esto


def aligerar(fig) -> None:
    """Las líneas con miles de puntos (series diarias de muchos años) se reducen a ~MAX_PUNTOS tomando uno cada k
    y siempre el último: el dibujo es el mismo a la vista y la página pesa mucho menos (clave en celulares, porque
    cada carga manda los gráficos de la pestaña abierta)."""
    for tr in fig.data:
        if getattr(tr, "type", "") != "scatter" or tr.x is None or len(tr.x) <= MAX_PUNTOS:
            continue
        n = len(tr.x)
        paso = -(-n // MAX_PUNTOS)
        idx = list(range(0, n, paso))
        if idx[-1] != n - 1:
            idx.append(n - 1)
        upd = {"x": [tr.x[i] for i in idx], "y": [tr.y[i] for i in idx]}
        if tr.customdata is not None and len(tr.customdata) == n:
            upd["customdata"] = [tr.customdata[i] for i in idx]
        tr.update(**upd)


def grafico(fig, key: str | None = None):
    # sin la barra de herramientas de Plotly (tapa el gráfico, sobre todo en el celular) y sin zoom accidental al deslizar.
    # `key` hace falta cuando el mismo gráfico aparece en dos pantallas (por ejemplo, en Inicio y en su pestaña).
    charts.presentar(fig)
    fig.update_layout(dragmode=False)
    titulo, bajada = charts.sacar_titulo(fig)
    trazas = charts.trazas_de(fig)
    if titulo or trazas:
        # título del gráfico y, a la derecha, «CSV» para bajar sus datos (se arman recién al tocarlo)
        n = st.session_state["_n_graf"] = st.session_state.get("_n_graf", 0) + 1
        with st.container(key=f"gtit_{n}", horizontal=True, vertical_alignment="bottom", gap="small"):
            st.markdown(style.titulo_grafico(titulo, bajada) if titulo else "", unsafe_allow_html=True)
            if trazas:
                nombre = style.slug(titulo or key or "grafico")[:60]
                st.download_button("CSV", lambda t=trazas: charts.csv_de(t), file_name=f"macrocenter-{nombre}.csv",
                                   mime="text/csv", key=f"dl_{n}", icon=":material/download:", type="tertiary",
                                   on_click="ignore", help="Bajar los datos de este gráfico (para Excel)")
    aligerar(fig)
    charts.compactar(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False}, key=key)


# ───────────────────────── carga de series ─────────────────────────
VIVO = cargar_vivo()
dol = con_dolar_vivo(get("dolares"), VIVO.get("dolares"))
if dol is not None:
    dol = dol.copy()
    dol["brecha_blue"] = ((dol["blue"] / dol["oficial"] - 1) * 100).replace([float("inf"), float("-inf")], float("nan"))
    dol["brecha_ccl"] = ((dol["contadoconliqui"] / dol["oficial"] - 1) * 100).replace([float("inf"), float("-inf")], float("nan"))
    dol_rec = dol.dropna(subset=["oficial"])

riesgo = con_riesgo_vivo(get("riesgo_pais"), VIVO.get("riesgo"))
reservas = get("bcra:reservas")
infl_m, infl_ia, rem = get("bcra:inflacion_mensual"), get("bcra:inflacion_interanual"), get("bcra:rem_12m")
uva = get("bcra:uva")
ipim, ipp = get("serie:ipim"), get("serie:ipp")  # precios mayoristas (INDEC)
emae_sa, emae = get("serie:emae_sa"), get("serie:emae")
paro = get("serie:desempleo")
pib = get("serie:pib")
badlar = get("bcra:badlar")
pases, tpm = get("bcra:pases_1d"), get("bcra:tpm")
sal, sal_priv, sal_pub = get("serie:salarios"), get("serie:salarios_privado"), get("serie:salarios_publico")
ripte, smvm, haber_min = get("serie:ripte"), get("serie:smvm"), get("serie:haber_minimo")


def yoy(df: pd.DataFrame, periodos: int = 12) -> pd.DataFrame:
    return series.cambio_periodico(df, periodos=periodos).dropna(subset=["valor"])


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
    # sin inflación, una serie vacía pero con índice de fechas (con uno común, comparar contra fechas falla)
    inf = infl_m.set_index("fecha")["valor"] if infl_m is not None else pd.Series(dtype=float, index=pd.DatetimeIndex([]))

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


def fiscal_anual() -> pd.DataFrame:
    """Resultado primario y financiero de cada año calendario, en % del PBI de ese año.
    PBI del año: promedio de los trimestres (ya anualizados) del INDEC; los que todavía no se publicaron se estiman con
    el último trimestre actualizado por inflación. El año en curso es el acumulado hasta el último mes sobre el PBI
    estimado del año entero (así lo informa también el Ministerio de Economía). Columnas: anio, primario, financiero, meses."""
    if pib_corr is None or (fis_prim is None and fis_fin is None):
        return pd.DataFrame(columns=["anio"])
    q = pib_corr.dropna(subset=["valor"]).set_index("fecha")["valor"].sort_index()
    if q.empty:
        return pd.DataFrame(columns=["anio"])
    inf = infl_m.set_index("fecha")["valor"] if infl_m is not None else pd.Series(dtype=float, index=pd.DatetimeIndex([]))

    def pbi_trimestre(t: pd.Timestamp) -> float:
        if t in q.index:
            return float(q[t])
        if t < q.index[0]:
            return float("nan")
        tramo = inf[(inf.index >= q.index[-1] + pd.DateOffset(months=3)) & (inf.index < t + pd.DateOffset(months=3))]
        return float(q.iloc[-1] * (1 + tramo / 100).prod())

    filas = []
    base = {}
    for df_, c in ((fis_prim, "primario"), (fis_fin, "financiero")):
        if df_ is not None:
            base[c] = df_[df_["fecha"] <= HOY].set_index("fecha")["valor"]
    anios = sorted({fch.year for s in base.values() for fch in s.index})
    for y in anios:
        pbi_y = sum(pbi_trimestre(pd.Timestamp(year=y, month=m, day=1)) for m in (1, 4, 7, 10)) / 4
        if not pbi_y or pbi_y != pbi_y:
            continue
        fila = {"anio": y}
        meses = 0
        for c, s in base.items():
            sy = s[s.index.year == y].dropna()
            meses = max(meses, len(sy))
            fila[c] = float(sy.sum()) / pbi_y * 100 if len(sy) else float("nan")
        fila["meses"] = meses
        filas.append(fila)
    out = pd.DataFrame(filas)
    if out.empty:
        return pd.DataFrame(columns=["anio"])
    ultimo_mes = max(s.index.max() for s in base.values())
    out["etiqueta"] = [f"{a} (ene-{MESES_ES[ultimo_mes.month - 1][:3]})" if m < 12 else str(a)
                       for a, m in zip(out["anio"], out["meses"])]
    return out


comercio = None
if ex is not None and im is not None:
    comercio = ex.rename(columns={"valor": "exp"}).merge(im.rename(columns={"valor": "imp"}), on="fecha")
    comercio["saldo"] = comercio["exp"] - comercio["imp"]
    comercio["saldo_12m"] = comercio["saldo"].rolling(12).sum()


# ───────────────────────── barra lateral (segunda parte: necesita los datos) ─────────────────────────
# el término del día sale de macrocenter/glosario.py (365 términos, uno por día del año)


@st.fragment  # escribir un monto redibuja solo el conversor, no la página entera
def conversor_lateral() -> None:
    """Conversor pesos ↔ dólares con las cotizaciones del día. De pesos a dólares usa el precio de venta (lo que se
    paga por cada dólar); de dólares a pesos, el de compra (lo que se recibe)."""
    sentido_c = selector.uno(st.segmented_control, "Sentido", ["A dólares", "A pesos"], "conv_sentido", width="stretch",
                             label_visibility="collapsed")
    a_dolares = sentido_c == "A dólares"
    monto = interactivo.entrada_monto(st, "Pesos" if a_dolares else "Dólares",
                                      "conv_pesos" if a_dolares else "conv_usd", 1_000_000 if a_dolares else 1_000)
    filas = []
    for col_c, nombre_c in (("oficial", "Oficial"), ("blue", "Blue"), ("bolsa", "MEP"), ("tarjeta", "Tarjeta")):
        col_p = col_c if a_dolares else f"{col_c}_compra"
        if col_p not in dol or (col_c == "tarjeta" and not a_dolares):  # con tarjeta se compra, no se vende
            continue
        s_c = dol[["fecha", col_p]].dropna()
        if s_c.empty or not s_c[col_p].iloc[-1]:
            continue
        precio = float(s_c[col_p].iloc[-1])
        res = monto / precio if a_dolares else monto * precio
        filas.append((nombre_c, charts.num(precio, 0, pre="$"),
                      charts.num(res, 2 if a_dolares and res < 100 else 0, pre="US$ " if a_dolares else "$")))
    if filas:
        st.markdown(style.conversor(filas, "a precio de venta" if a_dolares else "a precio de compra"),
                    unsafe_allow_html=True)


def ir_a_seccion(vista_: str, clave: str, valor: str) -> None:
    """Atajo de la barra lateral: abre una pantalla directo en la sección elegida."""
    st.session_state["vista"] = vista_
    st.session_state[clave] = valor


# lo más buscado de la página, sin repetir lo que ya está a la vista (cotizaciones, menú): pocos y a mano
ATAJOS = (
    ("tasas", "Tasas de plazo fijo hoy", ":material/percent:", ("inversiones", "inv_seccion", "Tasas y plazos fijos")),
    ("alquiler", "Ajustar un alquiler", ":material/home:", ("juegos", "inter_modo", "Ajuste de alquileres")),
    ("pesos", "¿Cuánto valían tus pesos?", ":material/savings:", ("juegos", "inter_modo", "¿Cuánto valían tus pesos?")),
    ("mapa", "Inflación por provincia", ":material/map:", ("tablero", "pestana", "Inflación y dinero")),
    ("presidentes", "Economía por presidente", ":material/account_balance:", ("historia", "hist_seccion", "Presidentes")),
)

with st.sidebar:
    st.markdown(style.etiqueta("Atajos"), unsafe_allow_html=True)
    for clave_a, texto_a, icono_a, destino_a in ATAJOS:
        st.button(texto_a, key=f"atajo_{clave_a}", icon=icono_a, width="stretch", on_click=ir_a_seccion, args=destino_a)
    if dol is not None:
        st.markdown(style.etiqueta("Conversor"), unsafe_allow_html=True)
        with st.container(key="conv_caja"):
            conversor_lateral()
    termino, definicion = glosario.termino_del_dia(HOY)
    st.markdown(style.etiqueta("Término del día"), unsafe_allow_html=True)
    st.markdown(style.termino_del_dia(termino, definicion), unsafe_allow_html=True)


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
    abrir(pestanas.historia)


def seccion_ministros(dp: dict | None) -> None:
    """Ministros de Economía desde 1983, agrupados por presidente. Los hitos son fijos; las cifras salen de las series
    (si faltan, las tarjetas se muestran igual, sin números)."""
    abrir(pestanas.ministros_economia, dp)


# ── Interactivo ──
def pantalla_inversiones() -> None:
    espera = st.empty()
    espera.html(style.cargando("Buscando las tasas de hoy…", alto="40vh"))
    inv = cargar_inversiones()
    merc = cargar_mercados()
    espera.empty()

    def tabla(x):
        return x if isinstance(x, pd.DataFrame) else None

    d = {"bancos": inv.get("bancos"), "rendimientos": inv.get("rendimientos"), "fci_hoy": tabla(inv.get("fci_hoy")),
         "fci_antes": tabla(inv.get("fci_antes")), "bitcoin": tabla(inv.get("bitcoin")),
         "merval": tabla(merc.get("^MERV")), "sp500": tabla(merc.get("^GSPC")), "dolares": dol, "rem": rem,
         "cer": get("bcra:cer"), "uva": uva, "depositos_30d": get("bcra:depositos_30d"), "infl_ia": infl_ia}
    inversiones.mostrar(d, grafico, _grafico_periodo)


def pantalla_juegos() -> None:
    try:
        dp_i, inds_i, faltan_i = historicos(DATOS, dol, ACTUALIZADO)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        dp_i, inds_i, faltan_i = None, None, ["cálculo"]
    if faltan_i:
        falla("no se pudieron cargar los datos de las herramientas: falta " + ", ".join(faltan_i))
        actualizando()
    else:
        dp_i = {**dp_i, "uva": uva,
                "icl": get("bcra:icl"), "cer": get("bcra:cer"), "infl_m": infl_m, "ipc_gba": get("serie:ipc_gba"),
                "salarios": sal,
                "dolar_blue": None if dol is None else dol[["fecha", "blue"]].dropna().rename(columns={"blue": "valor"})}
        interactivo.mostrar(dp_i, inds_i, fotos_presidentes(), uva)


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


@st.fragment  # sus selectores redibujan solo esta pestaña
def pantalla_cripto() -> None:
    abrir(pestanas.cripto)


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


@st.fragment  # sus selectores redibujan solo esta pestaña
def pantalla_bolsas() -> None:
    abrir(pestanas.bolsas)


@st.fragment  # sus selectores redibujan solo esta pestaña
def pantalla_bonos() -> None:
    abrir(pestanas.bonos)


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
                    poner(nombre, charts.num(ultimo(s), 0, pre="$"), delta(s, dias=1), "alto")
    for clave, nombre in (("fx:EUR", "Euro"), ("fx:GBP", "Libra")):
        d_ = DATOS.get(clave)
        if isinstance(d_, pd.DataFrame) and not d_.empty:
            poner(nombre, charts.num(ultimo(d_), 0, pre="$"), delta(d_, dias=1), "alto")
    if riesgo is not None:
        poner("Riesgo país", charts.num(ultimo(riesgo), 0, suf=" pb"), delta(riesgo, dias=1), "bajo")
    if reservas is not None:
        poner("Reservas", charts.num(ultimo(reservas), 0, pre="USD ", suf=" M"), delta(reservas, dias=1), "alto")
    if infl_m is not None:
        poner("Inflación mensual", charts.num(ultimo(infl_m), 1, suf="%"))
    if badlar is not None:
        poner("BADLAR", charts.num(ultimo(badlar), 1, suf="%"))
    cr = cargar_cripto()
    m = cr.get("mercado")
    if isinstance(m, pd.DataFrame) and not m.empty:
        for sim in ("BTC", "ETH"):
            f = m[m["simbolo"] == sim]
            if not f.empty:
                poner(sim, _usd_cripto(f.iloc[0]["usd"]), f.iloc[0]["cambio_24h"], "alto")
    mk = cargar_mercados()
    for simbolo, nombre, sentido in (("^MERV", "Merval", "alto"), ("^GSPC", "S&P 500", "alto"), ("^DJI", "Dow Jones", "alto"),
                                     ("GC=F", "Oro", "alto"), ("CL=F", "Petróleo", "alto"), ("ZS=F", "Soja", "alto")):
        df = mk.get(simbolo)
        if isinstance(df, pd.DataFrame) and len(df) >= 2:
            ult = float(df.iloc[-1]["valor"])
            poner(nombre, charts.num(ult, 0 if ult >= 1000 else 2), _var_pct(df), sentido)
    return items


def seccion_actual() -> tuple[str, str]:
    """(ruta, título) de lo que se está viendo, para contar visitas por sección (GoatCounter, sin cookies)."""
    legal_ = st.query_params.get("legal")
    if isinstance(legal_, str) and legal_ in legal.PAGINAS:
        return f"/legal/{legal_}", legal.PAGINAS[legal_]["titulo"]
    v = st.session_state.get("vista", "tablero")
    if v == "historia":
        sub = st.session_state.get("hist_seccion") or "Presidentes"
        return f"/historia/{style.slug(sub)}", f"Historia económica · {sub}"
    if v == "inversiones":
        sub = st.session_state.get("inv_seccion") or inversiones.SECCIONES[0]
        return f"/inversiones/{style.slug(sub)}", f"Ahorro e inversiones · {sub}"
    if v == "juegos":
        sub = st.session_state.get("inter_modo") or interactivo.MODOS[0]
        return f"/herramientas/{style.slug(sub)}", f"Herramientas · {sub}"
    sub = st.session_state.get("pestana") or "Resumen"
    return f"/tablero/{style.slug(str(sub))}", f"Tablero · {sub}"


def refrescar_datos() -> None:
    """Vacía los cachés (compartidos por todas las visitas) y vuelve a descargar todo."""
    _estado_actualizar()["ultimo"] = time.time()
    _ultima_carga()["t"] = 0.0  # la descarga que sigue muestra la pantalla de carga
    envejecer_disco()
    cargar_todo.clear()
    for e_ in _memoria().values():  # dólar del momento, noticias, cripto y bolsas: se renuevan en la próxima carga
        e_["t"] = 0.0


def _firma_vivo() -> tuple:
    """Versión de los datos que se renuevan solos: si cambia, hay algo nuevo para mostrar."""
    mem = _memoria()
    return tuple(mem[k].get("ver", 0) if k in mem else 0 for k in ("vivo", "cripto", "mercados"))


@st.fragment(run_every=30)
def estado_vivo() -> None:
    """Cada 30 segundos: pide (de fondo) el dólar del momento, cripto y bolsas y, si llegó algo nuevo, redibuja la página
    entera para mostrarlo. Mientras tanto muestra cuándo se actualizó cada cosa."""
    vivo = cargar_vivo()
    cargar_cripto()
    cargar_mercados()
    firma, previa = _firma_vivo(), st.session_state.get("_firma_vivo")
    st.session_state["_firma_vivo"] = firma
    if previa is not None and firma != previa:
        st.rerun(scope="app")
    dv = vivo.get("dolares")
    hora = None
    if isinstance(dv, pd.DataFrame) and not dv.empty:
        u = pd.Timestamp(dv["actualizado"].max())
        hora = f"{u:%H:%M}" if u.normalize() == HOY else f"{u:%d/%m %H:%M}"
    st.markdown(style.estado_datos(hora, f"{ACTUALIZADO:%d/%m %H:%M}"), unsafe_allow_html=True)


def pie_pagina() -> None:
    # Barra fina pegada al borde inferior de la ventana en todas las pantallas (ver .st-key-pie_datos en style.py).
    # Lo largo (marca, fuentes, aviso) va en el panel «Acerca de».
    with st.container(key="pie_datos", horizontal=True, vertical_alignment="center"):
        estado_vivo()
        st.markdown(style.pie_enlaces(), unsafe_allow_html=True)
        with st.popover("Acerca de", icon=":material/info:", width="content"):
            st.markdown(style.footer(), unsafe_allow_html=True)
        # Los cachés son compartidos: vaciarlos obliga a volver a descargar para todos. Publicada, el botón tiene una
        # espera de 10 minutos entre usos (para cualquiera), así nadie puede forzar descargas en cadena.
        espera = 0 if LOCAL else 600
        faltan = int(espera - (time.time() - _estado_actualizar()["ultimo"]))
        st.button("Refrescar datos", key="actualizar", icon=":material/refresh:", width="content", disabled=faltan > 0,
                  on_click=refrescar_datos,
                  help="Vuelve a descargar todo de las fuentes. El dólar, cripto y las bolsas ya se renuevan solos."
                       if faltan <= 0 else f"Alguien refrescó hace poco. Podés volver a hacerlo en {faltan // 60 + 1} min.")
    try:
        ruta, titulo = seccion_actual()
        if not ruta.startswith("/legal/"):  # la dirección del navegador sigue a lo que se mira: se puede compartir
            if ruta == "/tablero/resumen":
                st.query_params.pop("ver", None)
            elif st.query_params.get("ver") != ruta.strip("/"):
                st.query_params["ver"] = ruta.strip("/")
        st.html(style.contador_visitas(ruta, titulo), unsafe_allow_javascript=True)
    except Exception:  # noqa: BLE001 — contar visitas nunca debe afectar la página
        traceback.print_exc()


# ───────────────────────── encabezado ─────────────────────────
_cargando_inicio.empty()
st.session_state["_ya_cargo"] = True
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
    # Vistas aparte (Historia económica, Herramientas): reemplazan al tablero y no ocupan una pestaña.
    titulos = {"inversiones": "Ahorro e inversiones", "historia": "Historia económica", "juegos": "Herramientas"}
    pantallas = {"inversiones": pantalla_inversiones, "historia": pantalla_historia, "juegos": pantalla_juegos}
    st.button("Volver al tablero", key="volver_tablero", icon=":material/arrow_back:", on_click=ir_a, args=("tablero",))
    st.subheader(titulos[vista])
    with protegido(titulos[vista]):
        pantallas[vista]()
    pie_pagina()
    st.stop()

# Migrar la selección de sesiones abiertas antes de fusionar las pestañas.
if st.session_state.get("pestana") in ("Inflación", "Dinero y crédito"):
    st.session_state["pestana"] = "Inflación y dinero"
t_res, t_dol, t_bol, t_cri, t_bonos, t_prec, t_tasas, t_act, t_res_i, t_sal, t_fis, t_com = st.tabs(
    PESTANAS,
    # cada pestaña se calcula y se manda recién al abrirla: la primera carga pesa una fracción (clave en el celular)
    key="pestana", on_change="rerun",
)

# ───────────────────────── indicadores personalizables ─────────────────────────
PREFS_ARCHIVO = Path(__file__).parent / ".macrocenter_prefs.json"
KPIS_DEFECTO = ["oficial", "riesgo", "reservas", "infl_m", "emae_m"]

dol_s = {c: dol[["fecha", c]].dropna().rename(columns={c: "valor"})
         for c in ("oficial", "blue", "bolsa", "contadoconliqui")} if dol is not None else {}
brecha_df = dol.dropna(subset=["brecha_blue"]) if dol is not None else None
emae_ia = yoy(emae) if emae is not None else None
# actividad del mes: EMAE desestacionalizado contra el mes anterior (el dato que el INDEC destaca cada mes)
emae_m = (emae_sa.assign(valor=series.cambio_periodico(emae_sa, periodos=1)["valor"]).dropna(subset=["valor"])
          if emae_sa is not None else None)
paro_pct = paro.assign(valor=paro["valor"] * 100) if paro is not None else None
sal_ia = yoy(sal) if sal is not None else None
sal_real_df = salario_real()


def _kpi(df: pd.DataFrame | None, col: str = "valor", dias: int = 30, modo: str = "pct", **kw):
    """Devuelve una función que calcula los argumentos de `kpi` (o 's/d' si falta la serie)."""
    def calcular() -> dict:
        if df is None:
            return {"valor": None, **kw}
        cambio = delta(df, col, dias=dias, modo=modo)
        if kw.get("d_txt") in ("vs mes ant.", "vs trim. ant."):
            meses = 3 if kw["d_txt"] == "vs trim. ant." else 1
            actual, anterior = series.comparar(df, col, meses=meses, hoy=HOY)
            cambio = (None if actual is None or anterior is None else
                      actual - anterior if modo == "abs" else None if anterior == 0 else (actual / anterior - 1) * 100)
        return dict(valor=ultimo(df, col), d=cambio, serie=df.dropna(subset=[col]), **kw)
    return calcular


_MES = dict(dias=25, modo="abs", d_suf=" pp", d_txt="vs mes ant.")

# clave -> (grupo, nombre, función). El orden de este diccionario es el orden del selector.
CATALOGO = {
    "oficial": ("Dólar", "Dólar oficial", _kpi(dol_s.get("oficial"), dec=0, pre="$", help="Precio de venta", fuente='DolarApi / ArgentinaDatos')),
    "blue": ("Dólar", "Dólar blue", _kpi(dol_s.get("blue"), dec=0, pre="$", help="Precio de venta", fuente='DolarApi / ArgentinaDatos')),
    "mep": ("Dólar", "Dólar MEP", _kpi(dol_s.get("bolsa"), dec=0, pre="$", help="Precio de venta", fuente='CriptoYa / ArgentinaDatos')),
    "ccl": ("Dólar", "Dólar CCL", _kpi(dol_s.get("contadoconliqui"), dec=0, pre="$", help="Precio de venta", fuente='CriptoYa / ArgentinaDatos')),
    "brecha": ("Dólar", "Brecha blue / oficial", _kpi(brecha_df, "brecha_blue", modo="abs", dec=1, suf="%", d_suf=" pp", color="inverse", fuente='ArgentinaDatos · cálculo propio')),
    "reservas": ("Sector externo", "Reservas (USD M)", _kpi(reservas, dec=0, color="normal", fuente='BCRA')),
    "riesgo": ("Sector externo", "Riesgo país (pb)", _kpi(riesgo, modo="abs", dec=0, d_suf=" pb", color="inverse", d_dec=0, fuente='ArgentinaDatos · EMBI')),
    "badlar": ("Tasas", "BADLAR (TNA)", _kpi(badlar, modo="abs", dec=1, suf="%", d_suf=" pp", color="off", fuente='BCRA')),
    "pases": ("Tasas", "Pases 1 día (TNA)", _kpi(pases, modo="abs", dec=1, suf="%", d_suf=" pp", color="off",
                                                 help="Tasa de pases a un día del BCRA. Consultá la fecha del dato: "
                                                      "la serie puede haber dejado de publicarse.", fuente='BCRA')),
    "uva": ("Tasas", "UVA", _kpi(uva, dec=2, pre="$", color="off", fuente='BCRA')),
    "infl_m": ("Precios", "Inflación mensual", _kpi(infl_m, dec=1, suf="%", color="inverse", **_MES, fuente='INDEC · vía BCRA')),
    "infl_ia": ("Precios", "Inflación interanual", _kpi(infl_ia, dec=1, suf="%", color="inverse", **_MES, fuente='INDEC · vía BCRA')),
    "rem": ("Precios", "Inflación esperada 12 m", _kpi(rem, dec=1, suf="%", color="inverse", **_MES, fuente='BCRA')),
    "emae_m": ("Actividad", "Actividad mensual", _kpi(emae_m, dec=1, suf="%", color="normal",
                                                    help="EMAE desestacionalizado, variación contra el mes anterior", **_MES, fuente='INDEC · cálculo propio')),
    "emae": ("Actividad", "EMAE interanual", _kpi(emae_ia, dec=1, suf="%", color="normal", **_MES, fuente='INDEC')),
    "paro": ("Actividad", "Desocupación (EPH)", _kpi(paro_pct, dec=1, suf="%", color="inverse", dias=80, modo="abs",
                                                      d_suf=" pp", d_txt="vs trim. ant.", fuente='INDEC · EPH')),
    "sal_nom": ("Ingresos", "Salarios interanual", _kpi(sal_ia, dec=1, suf="%", color="normal",
                                                        help="Índice de salarios INDEC, total", **_MES, fuente='INDEC')),
    "salario_real": ("Ingresos", "Salario real interanual", _kpi(sal_real_df, "real", dec=1, suf="%", color="normal",
                                                                 help="Salarios nominales descontada la inflación", **_MES, fuente='INDEC · cálculo propio')),
    "ripte": ("Ingresos", "RIPTE", _kpi(ripte, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.", fuente='Secretaría de Trabajo · datos.gob.ar')),
    "smvm": ("Ingresos", "Salario mínimo", _kpi(smvm, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.", fuente='Secretaría de Trabajo · datos.gob.ar')),
    "haber": ("Ingresos", "Haber mínimo jubilatorio", _kpi(haber_min, dias=25, dec=0, pre="$", color="normal",
                                                           d_txt="vs mes ant.", fuente='ANSES · datos.gob.ar')),
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

# Inflación por región (INDEC) y por provincia (institutos provinciales): (nombre, clave, quién la mide)
DISTRITOS_IPC = [
    ("Ciudad de Buenos Aires", "serie:ipc_caba", "Instituto de Estadística de la Ciudad"),
    ("Gran Buenos Aires", "serie:ipc_gba", "INDEC"),
    ("Santa Fe", "serie:ipc_santafe", "Estadística provincial"),
    ("Mendoza", "serie:ipc_mendoza", "Estadística provincial"),
    ("Tucumán", "serie:ipc_tucuman", "Estadística provincial"),
    ("San Luis", "serie:ipc_sanluis", "Estadística provincial"),
    ("Chaco (Gran Resistencia)", "serie:ipc_chaco", "Estadística provincial"),
    ("Neuquén", "serie:ipc_neuquen", "Estadística provincial"),
    ("Región Pampeana", "serie:ipc_pampeana", "INDEC"),
    ("Región Noreste", "serie:ipc_noreste", "INDEC"),
    ("Región Noroeste", "serie:ipc_noroeste", "INDEC"),
    ("Región Cuyo", "serie:ipc_cuyo", "INDEC"),
    ("Región Patagonia", "serie:ipc_patagonia", "INDEC"),
]


def variaciones_ipc(df: pd.DataFrame) -> pd.DataFrame:
    """De un nivel de precios mensual: variación mensual e interanual (%). Los meses que faltan quedan vacíos."""
    s = df[df["fecha"] <= HOY].drop_duplicates("fecha").set_index("fecha")["valor"].sort_index().asfreq("MS")
    out = pd.DataFrame({"mensual": s.pct_change(fill_method=None) * 100,
                        "interanual": s.pct_change(12, fill_method=None) * 100})
    return out.rename_axis("fecha").reset_index().dropna(subset=["mensual"])


@st.fragment
def inflacion_distritos() -> None:
    """Mapa con el último dato de cada distrito disponible."""
    series = {}
    if infl_m is not None and infl_ia is not None:
        n = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
        series["Nacional"] = ("INDEC", n.rename(columns={"valor_m": "mensual", "valor_ia": "interanual"}))
    for nombre, clave, fuente in DISTRITOS_IPC:
        d = DATOS.get(clave)  # sin aviso si falta: el distrito simplemente no aparece
        if isinstance(d, pd.DataFrame) and not d.empty:
            v = variaciones_ipc(d)
            # un distrito que dejó de publicar hace más de 6 meses no se muestra (un número viejo al lado de los demás
            # confunde); vuelve solo cuando su instituto publique de nuevo
            if not v.empty and v["fecha"].max() >= HOY - pd.DateOffset(months=6):
                series[nombre] = (fuente, v)
    if len(series) < 2:
        return
    st.markdown("#### Inflación por región y provincia")
    mapa.mostrar(series)
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "Cada instituto mide con su propia canasta y publica en su propia fecha, por eso el último mes no "
                        "es el mismo para todos. Una provincia que lleva más de seis meses sin publicar no se muestra "
                        "hasta que vuelva a hacerlo."),
        ("Regiones", "Las del INDEC cubren todo el país (Córdoba, por ejemplo, está en la Pampeana: su índice provincial "
                     "no está en la API de datos abiertos).")), unsafe_allow_html=True)


def ult_y_ant(df: pd.DataFrame | None, col: str = "valor", atras: int = 1, meses: int = 1) -> tuple[float | None, float | None]:
    """Compara períodos calendario; un mes o trimestre ausente no se sustituye por otro."""
    return series.comparar(df, col, atras=atras, meses=meses, hoy=HOY)


def dif(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else a - b


def pct(a: float | None, b: float | None) -> float | None:
    return None if a is None or not b else (a / b - 1) * 100


def panel_plazo_fijo(clave: str = "res_real", subtitulo: bool = True) -> None:
    # Rendimiento real de un plazo fijo: lo que rinde la tasa menos lo que subieron los precios, mes a mes.
    # `clave` distingue los botones de período cuando el panel aparece en más de una pantalla.
    if subtitulo:
        st.subheader("¿Le ganó el plazo fijo a la inflación?")
    if badlar is not None and infl_m is not None:
        tasa_m = badlar.set_index("fecha")["valor"].resample("ME").mean().rename("tna").reset_index()
        real = tasa_m.merge(infl_m.rename(columns={"valor": "inflacion"}), on="fecha")
        real["real"] = ((1 + real["tna"] / 1200) / (1 + real["inflacion"] / 100) - 1) * 100
        real = real.replace([float("inf"), float("-inf")], float("nan")).dropna(subset=["real"])
        if real.empty:
            falla("no hay datos para el rendimiento real del plazo fijo")
        else:
            ult = real.iloc[-1]
            k = st.columns(3)
            kpi(k[0], "Rinde la tasa (mensual)", float(ult["tna"]) / 12, 1, suf="%", help="BADLAR (TNA) dividida por 12")
            kpi(k[1], "Suben los precios (mensual)", float(ult["inflacion"]), 1, suf="%")
            kpi(k[2], "Rendimiento real del mes", float(ult["real"]), 1, suf="%", color="normal",
                help="Positivo: la tasa le ganó a la inflación. Negativo: el ahorro perdió poder de compra.")
            grafico_periodo(clave, real, lambda d: charts.barras(
                d, "real", "Rendimiento real mensual de un plazo fijo (%)", yfmt=",.1f", height=300), mensual=True)
            st.markdown(style.aclaracion(
                ("Supuestos", "El plazo fijo se aproxima con la tasa BADLAR (depósitos a plazo de bancos privados), promedio del "
                              "mes, contra la inflación de ese mes."),
                ("No incluye", "Impuestos ni comisiones.")), unsafe_allow_html=True)
    else:
        falla("no se pudieron cargar la tasa o la inflación del panel del plazo fijo")


# ───────────────────────── Inicio: rotación y panorama ─────────────────────────
@st.cache_resource
def _contador_visitas() -> dict:
    return {"n": 0, "lock": threading.Lock()}


def turno_de_visita() -> int:
    """Número de esta visita (una por sesión: cada vez que alguien entra o recarga la página avanza uno). Sirve para que
    la portada no muestre siempre lo mismo: el gráfico y el análisis destacados van rotando."""
    if "turno_inicio" not in st.session_state:
        c = _contador_visitas()
        with c["lock"]:
            st.session_state["turno_inicio"] = c["n"]
            c["n"] += 1
    return st.session_state["turno_inicio"]


def _ult_y_hace(df: pd.DataFrame | None, col: str = "valor", dias: int = 30) -> tuple[float | None, float | None]:
    """Último dato y el de hace `dias` días (el último publicado hasta esa fecha)."""
    if df is None or col not in df:
        return None, None
    d = df[df["fecha"] <= HOY].dropna(subset=[col])
    if d.empty:
        return None, None
    antes = d[d["fecha"] <= d["fecha"].iloc[-1] - pd.Timedelta(days=dias)]
    return float(d[col].iloc[-1]), (float(antes[col].iloc[-1]) if not antes.empty else None)


def _mes(fecha: pd.Timestamp) -> str:
    return MESES_ES[fecha.month - 1]


def _mes_corto(fecha: pd.Timestamp) -> str:
    return f"{MESES_ES[fecha.month - 1][:3]} {fecha:%Y}"


def semestre_pobreza(fecha: pd.Timestamp) -> str:
    """La serie de pobreza fecha cada semestre con el comienzo del semestre siguiente (2026-07-01 = 1.er semestre 2026)."""
    f = fecha - pd.DateOffset(months=6)
    return f"{'1.er' if f.month <= 6 else '2.º'} sem. {f.year}"


def bloque_pobreza(titulo: bool = True) -> None:
    """Pobreza (EPH, por semestre) y canastas básicas del INDEC, al pie de la pestaña Salarios. En el Resumen va sin
    título propio (`titulo=False`): ahí ya lo encabeza la pregunta del análisis."""
    pob, lp, li = get("serie:pobreza"), get("serie:linea_pobreza"), get("serie:linea_indigencia")
    if pob is None and lp is None:
        return
    if titulo:
        st.markdown("#### Pobreza y canasta básica")
    k = st.columns(3)
    pp = pob.assign(valor=pob["valor"] * 100) if pob is not None else None
    if pp is not None:
        v, a_ = ult_y_ant(pp, meses=6)
        kpi(k[0], f"Pobreza · {semestre_pobreza(pp['fecha'].iloc[-1])}", v, 1, suf="%", d=dif(v, a_), d_suf=" pp",
            d_txt="vs semestre ant.", color="inverse",
            help="Porcentaje de personas en hogares cuyos ingresos no alcanzan la canasta básica total. EPH del INDEC, "
                 "31 aglomerados urbanos; se publica por semestre, unos tres meses después de terminado.")
    for slot, df_, nombre in ((k[1], lp, "Canasta básica total"), (k[2], li, "Canasta alimentaria")):
        if df_ is not None:
            v, a_ = ult_y_ant(df_)
            kpi(slot, f"{nombre} · {_mes_corto(df_['fecha'].iloc[-1])}", v, 0, pre="$", d=pct(v, a_), d_txt="vs mes ant.",
                color="inverse", help="Para una familia de cuatro integrantes (dos adultos y dos chicos), según el INDEC. "
                                      "Es la línea de pobreza (total) y la de indigencia (alimentaria).")
    a, b = st.columns(2)
    if pp is not None:
        with a:
            # cada barra va en el comienzo del semestre medido (la serie lo fecha con el comienzo del siguiente)
            s = rec(pp, 10).assign(fecha=lambda d: d["fecha"] - pd.DateOffset(months=6))
            grafico(charts.barras(s, "valor", "Pobreza — % de personas (EPH, por semestre)", color_signo=False,
                                  nombre="Pobreza"), key="graf_pobreza")
    canastas = None
    for df_, nombre in ((lp, "Canasta básica total"), (li, "Canasta alimentaria"), (smvm, "Salario mínimo")):
        if df_ is not None:
            df_ = df_.rename(columns={"valor": nombre})
            canastas = df_ if canastas is None else canastas.merge(df_, on="fecha", how="outer")
    if canastas is not None:
        with b:
            canastas = canastas.sort_values("fecha")
            grafico(charts.lineas(rec(canastas, 3), {c_: c_ for c_ in canastas.columns if c_ != "fecha"},
                                  "Canastas de una familia tipo y salario mínimo ($ por mes)"), key="graf_canastas")
    st.markdown(style.aclaracion(
        ("Fuente", "INDEC (Encuesta Permanente de Hogares y valorización de las canastas básicas).")), unsafe_allow_html=True)


def bloque_cambiario() -> None:
    """Balance cambiario del BCRA (los dólares que entran y salen por el mercado de cambios), en la pestaña Reservas."""
    cc, bienes, serv = get("serie:cambiario_cc"), get("serie:cambiario_bienes"), get("serie:cambiario_servicios")
    fin, fae = get("serie:cambiario_financiera"), get("serie:cambiario_fae")
    if cc is None and fae is None:
        return
    st.markdown("#### Balance cambiario")
    st.markdown(style.aclaracion(
        ("Qué mide", "Los dólares que entran y salen por el mercado de cambios cada mes (millones de USD)."),
        ("Fuente", "BCRA."),
        leyenda=[("bien", "Entran más de los que salen"), ("mal", "Salen más")]), unsafe_allow_html=True)
    k = st.columns(3)
    for slot, df_, nombre, ayuda in (
            (k[0], cc, "Cuenta corriente cambiaria", "Comercio de bienes y servicios, intereses y utilidades."),
            (k[1], fin, "Cuenta financiera cambiaria", "Deuda, inversiones, préstamos y compra de dólares para ahorro.")):
        if df_ is not None:
            v, a_ = ult_y_ant(df_)
            kpi(slot, f"{nombre} · {_mes_corto(df_['fecha'].iloc[-1])} (USD M)", v, 0, d=dif(v, a_),
                d_suf=" M", d_txt="vs mes ant.", d_dec=0, help=ayuda)
    compras = fae.assign(valor=-fae["valor"]) if fae is not None else None  # la serie da las compras netas con signo negativo
    if compras is not None:
        v, a_ = ult_y_ant(compras)
        kpi(k[2], f"Compra neta de dólares · {_mes_corto(compras['fecha'].iloc[-1])} (USD M)", v, 0,
            d=dif(v, a_), d_suf=" M", d_txt="vs mes ant.", d_dec=0, color="off",
            help="Formación de activos externos de personas y empresas: dólares comprados para ahorro o inversión, "
                 "menos los vendidos. Positivo: compraron más de lo que vendieron.")
    per = selector_periodo("cambiario", "2 años", mensual=True)
    a, b = st.columns(2)
    if cc is not None:
        with a:
            grafico(charts.barras(rec(cc, 0, per), "valor", "Cuenta corriente cambiaria (USD millones)", yfmt=",.0f",
                                  nombre="Cuenta corriente"), key="graf_cambiario_cc")
    partes = None
    for df_, nombre in ((bienes, "Bienes"), (serv, "Servicios"), (compras, "Compra neta de dólares")):
        if df_ is not None:
            df_ = df_.rename(columns={"valor": nombre})
            partes = df_ if partes is None else partes.merge(df_, on="fecha", how="outer")
    if partes is not None:
        with b:
            partes = partes.sort_values("fecha")
            grafico(charts.lineas(rec(partes, 0, per), {c_: c_ for c_ in partes.columns if c_ != "fecha"},
                                  "Bienes, servicios y compra de dólares (USD millones)"), key="graf_cambiario_partes")


def panorama_inicio() -> list[dict]:
    """La coyuntura, tema por tema, con los últimos datos publicados: {tema, cifra, detalle, texto}. Cada tema
    se omite si falta su dato."""
    frases = []
    try:
        of, of_a = _ult_y_hace(dol_rec, "oficial") if dol is not None else (None, None)
        bl, _ = _ult_y_hace(dol, "blue") if dol is not None else (None, None)
        if of is not None:
            f = f"El **dólar oficial** está en **{charts.num(of, 0, pre='$')}**"
            v = pct(of, of_a)
            if v is not None:
                f += (" (sin cambios en 30 días)" if abs(v) < 0.05 else
                      f" ({(('subió ' if v > 0 else 'bajó ') + charts.num(abs(v), 1, '%'))} en 30 días)")
            if bl is not None:
                br = (bl / of - 1) * 100
                f += f" y el **blue**, en **{charts.num(bl, 0, pre='$')}**: una brecha de **{charts.num(br, 1, '%')}**"
                if abs(br) < 5:
                    f += ", prácticamente sin diferencia entre los dos"
            frases.append(dict(tema="Dólar", cifra=charts.num(of, 0, pre="$"), detalle="oficial", texto=f + "."))
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    try:
        if infl_m is not None:
            d = infl_m[infl_m["fecha"] <= HOY].dropna(subset=["valor"])
            if len(d) >= 2:
                u, a = d.iloc[-1], d.iloc[-2]
                f = f"La **inflación** de {_mes(u['fecha'])} fue **{charts.num(u['valor'], 1, '%')}**"
                dd = float(u["valor"] - a["valor"])
                if abs(dd) < 0.05:
                    f += f", igual que en {_mes(a['fecha'])}"
                else:
                    f += (f", {('más baja' if dd < 0 else 'más alta')} que en {_mes(a['fecha'])} "
                          f"({charts.num(a['valor'], 1, '%')})")
                ia = ultimo(infl_ia) if infl_ia is not None else None
                if ia is not None:
                    f += f". En los últimos 12 meses los precios subieron **{charts.num(ia, 1, '%')}**"
                esp = ultimo(rem) if rem is not None else None
                if esp is not None:
                    f += f" y las consultoras esperan **{charts.num(esp, 1, '%')}** para los próximos 12 (REM del BCRA)"
                frases.append(dict(tema="Inflación", cifra=charts.num(u["valor"], 1, "%"), detalle=f"mensual · {_mes(u['fecha'])}",
                                   texto=f + "."))
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    try:
        rs, rs_a = _ult_y_hace(reservas)
        rp, rp_a = _ult_y_hace(riesgo)
        partes = []
        if rs is not None:
            t_ = f"las **reservas** del Banco Central suman **USD {charts.num(rs, 0)} millones**"
            v = pct(rs, rs_a)
            if v is not None and abs(v) >= 0.05:
                t_ += f" ({(('subieron ' if v > 0 else 'bajaron ') + charts.num(abs(v), 1, '%'))} en 30 días)"
            partes.append(t_)
        if rp is not None:
            t_ = f"el **riesgo país** está en **{charts.num(rp, 0)} puntos**"
            v = dif(rp, rp_a)
            if v is not None and abs(v) >= 1:
                t_ += f" ({(('subió ' if v > 0 else 'bajó ') + charts.num(abs(v), 0) + ' puntos')} en 30 días)"
            partes.append(t_)
        if partes:
            f = " y ".join(partes)
            frases.append(dict(tema="Reservas y riesgo", cifra=f"{charts.num(rp, 0)} pb" if rp is not None else
                               f"USD {charts.num(rs / 1000, 1)} mil M", detalle="riesgo país" if rp is not None else "reservas",
                               texto=f[0].upper() + f[1:] + "."))
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    try:
        if sal_real_df is not None and not sal_real_df.empty:
            u = sal_real_df.dropna(subset=["real"]).iloc[-1]
            r = float(u["real"])
            gana = r >= 0
            f = (f"Los **salarios** {('le ganan' if gana else 'le pierden')} a la inflación: en "
                 f"{_mes(u['fecha'])} compraban **{charts.num(abs(r), 1, '%')} {'más' if gana else 'menos'}** "
                 "que un año antes")
            # contra el mes inmediatamente anterior: suba del salario del mes descontada la inflación de ese mes
            if sal is not None and infl_m is not None:
                s_ = sal[sal["fecha"] <= u["fecha"]].dropna(subset=["valor"]).tail(2)
                i_ = infl_m[infl_m["fecha"].dt.to_period("M") == u["fecha"].to_period("M")]
                if len(s_) == 2 and not i_.empty and s_["valor"].iloc[0]:
                    m_ = ((s_["valor"].iloc[1] / s_["valor"].iloc[0]) / (1 + float(i_["valor"].iloc[0]) / 100) - 1) * 100
                    if abs(m_) < 0.05:
                        f += f" y lo mismo que en {_mes(s_['fecha'].iloc[0])}"
                    else:
                        f += (f" y {(charts.num(abs(m_), 1, '%') + (' más' if m_ > 0 else ' menos'))} "
                              f"que en {_mes(s_['fecha'].iloc[0])}")
            frases.append(dict(tema="Salarios", cifra=f"{'+' if r > 0 else ''}{charts.num(r, 1, '%')}",
                               detalle=f"real interanual · {_mes(u['fecha'])}", texto=f + "."))
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    try:
        if emae is not None:
            e = emae.assign(ia=emae["valor"].pct_change(12) * 100).dropna(subset=["ia"])
            e = e[e["fecha"] <= HOY]
            if not e.empty:
                u = e.iloc[-1]
                v = float(u["ia"])
                f = (f"La **actividad económica** (EMAE) de {_mes(u['fecha'])} quedó "
                     f"**{charts.num(abs(v), 1, '%')}** "
                     f"{('por encima' if v >= 0 else 'por debajo')} de un año antes")
                # contra el mes inmediatamente anterior, con la serie sin estacionalidad (la original no se compara así)
                if emae_sa is not None:
                    e_ = emae_sa[emae_sa["fecha"] <= u["fecha"]].dropna(subset=["valor"]).tail(2)
                    if len(e_) == 2 and e_["fecha"].iloc[1] == u["fecha"] and e_["valor"].iloc[0]:
                        m_ = (e_["valor"].iloc[1] / e_["valor"].iloc[0] - 1) * 100
                        if abs(m_) < 0.05:
                            f += f" y quedó igual que en {_mes(e_['fecha'].iloc[0])}"
                        else:
                            f += (f" y {(('creció ' if m_ > 0 else 'cayó ') + charts.num(abs(m_), 1, '%'))} "
                                  f"frente a {_mes(e_['fecha'].iloc[0])} (sin estacionalidad)")
                frases.append(dict(tema="Actividad", cifra=f"{'+' if v > 0 else ''}{charts.num(v, 1, '%')}",
                                   detalle=f"EMAE interanual · {_mes(u['fecha'])}", texto=f + "."))
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    return frases


# Gráficos que rotan arriba: (nombre, por qué importa). El dibujo de cada uno está en grafico_inicio.
GRAFICOS_INICIO = {
    "Dólar": "El **oficial** es el que regula el Banco Central y el **blue**, el del mercado informal. Cuando se separan "
             "mucho suele haber tensión cambiaria.",
    "Inflación": "Barras: cuánto subieron los precios cada mes. Línea: la suba acumulada en 12 meses. Es lo que más pesa "
                 "en el poder de compra.",
    "Reservas": "Los dólares del Banco Central para pagar deuda e intervenir en el mercado. Más reservas, más margen para "
                "evitar saltos del dólar.",
    "Riesgo país": "Cuánto más que EE. UU. paga la Argentina para endeudarse (100 puntos = 1 punto porcentual). Más bajo "
                   "es mejor: abarata el crédito para el Estado y las empresas.",
    "Brecha": "Cuánto más caros están el blue y el contado con liquidación que el oficial. Una brecha alta suele reflejar "
              "desconfianza o trabas para comprar dólares.",
    "Actividad": "El EMAE del INDEC mide mes a mes cuánto produce la economía (es el anticipo del PBI). Si sube, la "
                 "economía crece.",
    "Salario real": "Cuánto más o menos compran los sueldos que un año antes. Barras verdes: le ganaron a la inflación; "
                    "rojas: perdieron.",
}


def bloque_salarios() -> None:
    sr = sal_real_df
    if sr is None or sr.empty:
        falla("no se pudieron cargar los salarios")
        return
    _grafico_periodo("ini_sal", sr, lambda d: charts.lineas(d, {"Salarios": "salario", "Inflación": "inflacion"},
                                                            "Salarios vs inflación — variación interanual (%)",
                                                            yfmt=",.0f", height=340), defecto="5 años", mensual=True)
    u = sr.dropna(subset=["real"]).iloc[-1]
    st.markdown(style.aclaracion(
        ("Último dato", f"En {_mes(u['fecha'])} de {u['fecha'].year} los salarios subían "
                        f"{charts.num(u['salario'], 1, '%')} interanual y los precios, {charts.num(u['inflacion'], 1, '%')}."),
        ("Cómo leerlo", "Cuando la línea de salarios va por encima de la de inflación, el sueldo alcanza para más."),
        ("Fuente", "Índice de salarios del INDEC (registrados y no registrados), con unos dos meses de rezago.")), unsafe_allow_html=True)


def bloque_expectativas() -> None:
    """Inflación interanual observada contra lo que espera el mercado a 12 meses (REM del BCRA)."""
    if infl_m is None or infl_ia is None or rem is None:
        falla("no se pudieron cargar las expectativas de inflación")
        return
    m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))[["fecha", "valor_ia"]]
    m = m.rename(columns={"valor_ia": "Inflación interanual observada"})
    y = rem.rename(columns={"valor": "Expectativa a 12 meses (REM)"})
    df = m.merge(y, on="fecha", how="outer").sort_values("fecha")
    _grafico_periodo("ini_rem", df, lambda d: charts.lineas(
        d, {"Interanual observada": "Inflación interanual observada", "Expectativa 12 m (REM)": "Expectativa a 12 meses (REM)"},
        "Inflación observada y expectativa del mercado (%)", yfmt=",.0f", height=340), defecto="5 años", mensual=True)
    obs, esp = ultimo(infl_ia), ultimo(rem)
    if obs is not None and esp is not None:
        st.markdown(style.aclaracion(
            ("Último dato", f"La inflación de los últimos 12 meses fue {charts.num(obs, 1, '%')}; los analistas esperan "
                            f"{charts.num(esp, 1, '%')} para los próximos 12 (mediana del REM del BCRA)."),
            ("Nota", "Las expectativas son una referencia y pueden cambiar mes a mes.")), unsafe_allow_html=True)


def bloque_dolar_precios() -> None:
    """Dólar oficial y blue contra los precios, con base 100 al inicio del período elegido."""
    if dol is None or infl_m is None:
        falla("no se pudo armar la comparación del dólar con los precios")
        return
    d_ = dol.set_index("fecha")[["oficial", "blue"]].resample("MS").last().dropna(how="all").reset_index()
    pr = infl_m.dropna(subset=["valor"]).sort_values("fecha").copy()
    pr["mes"] = pr["fecha"].dt.to_period("M").dt.to_timestamp()
    pr["Precios (IPC)"] = (1 + pr["valor"] / 100).cumprod()
    d_["mes"] = d_["fecha"].dt.to_period("M").dt.to_timestamp()
    df = d_.merge(pr[["mes", "Precios (IPC)"]], on="mes", how="inner").drop(columns="mes")
    df = df.rename(columns={"oficial": "Dólar oficial", "blue": "Dólar blue"})

    def armar(d: pd.DataFrame):
        d = d.copy()
        for c in ("Dólar oficial", "Dólar blue", "Precios (IPC)"):
            base = d[c].dropna()
            d[c] = d[c] / base.iloc[0] * 100 if not base.empty else d[c]
        return charts.lineas(d, {c: c for c in ("Dólar oficial", "Dólar blue", "Precios (IPC)")},
                             "Dólar y precios — base 100 al inicio del período", yfmt=",.0f", height=340,
                             colores=("#74ACDF", "#F6B40E", "#B8C4D6"))  # sin verde ni rojo: acá no hay bueno ni malo

    _grafico_periodo("ini_dolprecios", df, armar, defecto="2 años", mensual=True)
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "Todas las líneas parten de 100 al comienzo del período elegido. Si la de un dólar queda por "
                        "encima de la de precios, subió más que la inflación en ese período; si queda por debajo, subió menos.")), unsafe_allow_html=True)


def bloque_comercio_inicio() -> None:
    """Exportaciones e importaciones acumuladas de 12 meses (INDEC)."""
    if comercio is None:
        falla("no se pudo cargar el comercio exterior")
        return
    c = comercio.sort_values("fecha").copy()
    c["exp_12m"], c["imp_12m"] = c["exp"].rolling(12).sum(), c["imp"].rolling(12).sum()
    c = c.dropna(subset=["exp_12m", "imp_12m"])
    if c.empty:
        falla("no se pudo cargar el comercio exterior")
        return
    _grafico_periodo("ini_comercio", c, lambda d: charts.lineas(
        d, {"Exportaciones": "exp_12m", "Importaciones": "imp_12m"},
        "Comercio exterior — acumulado de 12 meses (USD millones)", yfmt=",.0f", height=340), defecto="5 años", mensual=True)
    u = c.iloc[-1]
    st.markdown(style.aclaracion(
        ("Último dato", f"En los 12 meses hasta {_mes(u['fecha'])} de {u['fecha'].year}, la Argentina exportó USD "
                        f"{charts.num(u['exp_12m'], 0)} millones e importó USD {charts.num(u['imp_12m'], 0)} millones: saldo "
                        f"de USD {charts.num(u['exp_12m'] - u['imp_12m'], 0)} millones."),
        ("Fuente", "INDEC.")), unsafe_allow_html=True)


def bloque_reservas_riesgo() -> None:
    """Reservas del BCRA y riesgo país, lado a lado (últimos dos años)."""
    if reservas is None and riesgo is None:
        falla("no se pudieron cargar las reservas ni el riesgo país")
        return
    a, b = st.columns(2)
    if reservas is not None:
        with a:
            grafico(charts.lineas(rec(reservas), {"Reservas brutas": "valor"}, "Reservas del BCRA (USD millones)", yfmt=",.0f",
                                  height=320), key="graf_ini_rr_res")
    if riesgo is not None:
        with b:
            grafico(charts.lineas(rec(riesgo), {"Riesgo país": "valor"}, "Riesgo país (puntos básicos)", yfmt=",.0f",
                                  height=320), key="graf_ini_rr_riesgo")
    st.markdown(style.aclaracion(
        ("Qué mide", "Las reservas son los dólares y el oro que tiene el Banco Central. El riesgo país mide cuánto más "
                     "que EE. UU. paga la Argentina para endeudarse (100 puntos = 1 punto porcentual)."),
        ("Período", "Últimos dos años.")), unsafe_allow_html=True)


def bloque_fiscal() -> None:
    f = fiscal_df()
    cols = {n: c for n, c in (("Primario", "primario_12m"), ("Financiero", "financiero_12m")) if c in f}
    if f.empty or not cols:
        falla("no se pudieron cargar las cuentas públicas")
        return
    f12 = f.dropna(subset=list(cols.values()), how="all")

    def fig12(d):
        fig = charts.lineas(d, cols, "Resultado fiscal acumulado de 12 meses (% del PBI)", yfmt=",.1f", height=340)
        fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="rgba(128,128,128,.7)")
        return fig

    _grafico_periodo("ini_fis", f12, fig12, defecto="5 años", mensual=True)
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "Arriba de la línea punteada, el Estado nacional gasta menos de lo que recauda (superávit); "
                        "abajo, más (déficit)."),
        ("Qué mide", "El **primario** no cuenta los intereses de la deuda; el **financiero** sí. Más detalle en la "
                     "pestaña Resultado fiscal.")), unsafe_allow_html=True)


# ── Inicio ──
with t_res, protegido("Resumen"):
    if t_res.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.inicio)

# ── Criptomonedas ──
with t_cri, protegido("Criptomonedas"):
    if t_cri.open:  # solo la pestaña abierta se calcula y se manda al navegador
        pantalla_cripto()

# ── Bolsas ──
with t_bol, protegido("Bolsas"):
    if t_bol.open:  # solo la pestaña abierta se calcula y se manda al navegador
        pantalla_bolsas()

# ── Dólar ──
with t_dol, protegido("Dólar"):
    if t_dol.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.dolar)

# ── Reservas ──
with t_res_i, protegido("Reservas"):
    if t_res_i.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.reservas)

# ── Actividad y PBI ──
with t_act, protegido("Actividad y PBI"):
    if t_act.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.actividad)

# ── Salarios ──
with t_sal, protegido("Salarios"):
    if t_sal.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.salarios)

# ── Inflación ──
with t_prec, protegido("Inflación y dinero"):
    if t_prec.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.inflacion)
        st.divider()
        st.markdown("### Dinero y crédito")
        abrir(pestanas.dinero)

# ── Tasas y riesgo país ──
with t_tasas, protegido("Tasas y riesgo país"):
    if t_tasas.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.tasas)

# ── Bonos ──
with t_bonos, protegido("Bonos"):
    if t_bonos.open:  # solo la pestaña abierta se calcula y se manda al navegador
        pantalla_bonos()

# ── Comercio exterior ──
with t_com, protegido("Comercio exterior"):
    if t_com.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.comercio)


# ── Resultado fiscal ──
with t_fis, protegido("Resultado fiscal"):
    if t_fis.open:  # solo la pestaña abierta se calcula y se manda al navegador
        abrir(pestanas.fiscal)


pie_pagina()
