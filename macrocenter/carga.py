"""Carga de datos de MacroCenter: descarga de todas las fuentes, cachés compartidos entre visitas, guardado en disco y
copia de respaldo (semilla). app.py solo llama a estas funciones; acá no se dibuja nada salvo lo que se cachea.

Todo lo que se guarda es compartido por todas las visitas (datos públicos de las fuentes), nunca datos de una persona.
"""
from __future__ import annotations

import os
import pickle
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from macrocenter import data, news, presidentes, semilla
from macrocenter.avisos import falla

DESDE_BCRA = "2016-01-01"  # el UVA arranca en marzo de 2016


def hoy() -> pd.Timestamp:
    """Fecha de hoy en Argentina (se calcula en cada llamada: el servidor queda prendido de un día para el otro)."""
    return pd.Timestamp(data.hoy_argentina())


def error_corto(exc: BaseException) -> str:
    """Texto de error apto para mostrar: solo el tipo. El detalle (URLs, rutas) va a la consola del servidor."""
    print(f"[MacroCenter] {type(exc).__name__}: {exc}", flush=True)
    return type(exc).__name__



CACHE_DISCO = Path(__file__).resolve().parent.parent / ".macrocenter_cache_v2.pkl"  # v2: series sin los huecos al azar de la API
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
            # una serie vacía guardada (de antes de tratarlas como falla) cuenta como faltante: se completa con lo
            # último bueno o se vuelve a pedir, y lo guardado se toma como viejo para que se actualice de fondo
            vacias = [k for k, v in datos.items() if isinstance(v, pd.DataFrame) and v.empty]
            if vacias:
                datos = {k: ("sin datos" if k in vacias else v) for k, v in datos.items()}
                edad = max(edad, DISCO_FRESCO)
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


def envejecer_disco() -> None:
    """Marca lo guardado como viejo: la próxima carga descarga todo de nuevo, pero si alguna fuente falla todavía se
    puede usar su último dato bueno (por eso no se borra)."""
    try:
        if CACHE_DISCO.exists():
            os.utime(CACHE_DISCO, (0, 0))
    except OSError:
        pass


def _completar_con_disco(resultado: tuple[dict, datetime]) -> tuple[dict, datetime]:
    """Si alguna fuente falló, usa para ella el último dato bueno guardado: mejor un dato de hace unas horas que una
    sección vacía. Así la caída de una sola fuente no deja sin caché a toda la página."""
    datos, cuando = resultado
    if not any(isinstance(v, str) for v in datos.values()):
        return resultado
    guardado = _leer_disco()
    if guardado:
        viejos = guardado[0][0]
        datos = {k: (viejos.get(k, v) if isinstance(v, str) else v) for k, v in datos.items()}
    if any(isinstance(v, str) for v in datos.values()):  # sin nada guardado (servidor recién prendido): la copia de respaldo
        copia = _semilla()
        if copia:
            datos = {k: (copia[0].get(k, v) if isinstance(v, str) else v) for k, v in datos.items()}
    return datos, cuando


SEMILLA_MAX = 3 * 86400  # una copia de respaldo de más de 3 días no se usa para arrancar (sí para tapar una falla)


@st.cache_resource(ttl=1800, show_spinner=False)
def _semilla() -> tuple[dict, datetime] | None:
    """Copia de respaldo publicada por GitHub Actions (ver macrocenter/semilla.py). Se baja una vez cada 30 minutos
    como mucho, y solo si hace falta (servidor recién prendido o una fuente caída)."""
    return semilla.bajar(set(_tareas()))


def _arrancar_con_semilla() -> tuple[dict, datetime] | None:
    """Servidor recién prendido, sin nada en disco: arranca con la copia de respaldo (si es reciente) y baja todo de
    fondo. Las series que no estén en la copia quedan como falla hasta que termine esa descarga (un par de minutos)."""
    copia = _semilla()
    if not copia or (datetime.now() - copia[1]).total_seconds() > SEMILLA_MAX:
        return None
    _refrescar_en_segundo_plano()
    return {k: copia[0].get(k, "todavía no llegó") for k in _tareas()}, copia[1]


def _refrescar_en_segundo_plano() -> None:
    """Descarga todo sin bloquear la página; al terminar deja el disco al día y suelta el caché de memoria."""
    if not _refrescando.acquire(blocking=False):
        return

    def tarea():
        try:
            _guardar_disco(_completar_con_disco(_descargar_todo()))
            cargar_todo.clear()
        except Exception:  # noqa: BLE001
            pass
        finally:
            _refrescando.release()

    threading.Thread(target=tarea, daemon=True).start()


@st.cache_data(ttl=3600, show_spinner=False)  # la espera la muestra `pantalla_carga` (ver más abajo)
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
    else:
        resultado = _arrancar_con_semilla()
        if resultado:
            return resultado
    resultado = _completar_con_disco(_descargar_todo())
    _guardar_disco(resultado)
    return resultado


def _tareas() -> dict:
    return data.tareas_principales(DESDE_BCRA)


def _descargar_todo() -> tuple[dict[str, pd.DataFrame | str], datetime]:
    """Descarga todas las fuentes en paralelo. Cada fuente que falla queda como str con el error."""
    tareas = _tareas()

    def correr(item):
        nombre, fn = item
        try:
            d = data.limpiar(fn())
        except Exception as e:  # noqa: BLE001 — queremos aislar cualquier falla de red/formato
            return nombre, error_corto(e)
        # una respuesta vacía cuenta como falla: así se usa el último dato bueno guardado y se reintenta en un minuto
        # (antes quedaba guardada como dato válido y la sección mostraba «sin datos» durante una hora)
        if isinstance(d, pd.DataFrame) and d.empty:
            return nombre, "la fuente respondió sin datos"
        return nombre, d

    with ThreadPoolExecutor(max_workers=10) as pool:  # son pedidos de red: conviene hacer muchos a la vez
        return dict(pool.map(correr, tareas.items())), datetime.now()


@st.cache_resource
def _memoria() -> dict:
    """Últimos datos de noticias, cripto y bolsas, compartidos por todas las visitas (ver `al_dia`)."""
    return {}


def _entrada(mem: dict, nombre: str) -> dict:
    e = mem.get(nombre)
    if e is None:
        e = mem.setdefault(nombre, {"v": None, "t": 0.0, "lock": threading.Lock()})
    return e


def _bajar_y_guardar(e: dict, bajar, ttl: int, reintento: int) -> None:
    nuevo = bajar()
    viejo = e["v"] or {}
    e["v"] = {k: (viejo[k] if isinstance(v, str) and k in viejo and not isinstance(viejo[k], str) else v)
              for k, v in nuevo.items()}
    falla = any(isinstance(v, str) for v in nuevo.values())
    e["t"] = time.time() - (ttl - reintento if falla else 0)
    if not all(isinstance(v, str) for v in nuevo.values()):
        e["ver"] = e.get("ver", 0) + 1  # la página abierta se redibuja sola cuando esto cambia (ver estado_vivo)


def al_dia(nombre: str, bajar, ttl: int, reintento: int = 60):
    """Devuelve lo último que se bajó con `bajar()` sin hacer esperar a nadie: si tiene más de `ttl` segundos, lo
    renueva de fondo y mientras tanto se muestra lo anterior. Solo la primera vez (servidor recién prendido) se espera.
    Si una parte falla, se conserva su último dato bueno y se reintenta en `reintento` segundos."""
    e = _entrada(_memoria(), nombre)
    if e["v"] is not None and time.time() - e["t"] < ttl:
        return e["v"]

    def bajar_y_guardar() -> None:
        _bajar_y_guardar(e, bajar, ttl, reintento)

    if e["v"] is None:  # primera vez: no hay nada que mostrar, hay que esperar (si otra visita ya está bajando, a ella)
        with e["lock"]:
            if e["v"] is None:
                bajar_y_guardar()
        return e["v"]

    def de_fondo() -> None:
        try:
            bajar_y_guardar()
        except Exception:  # noqa: BLE001 — se sigue mostrando lo anterior
            traceback.print_exc()
        finally:
            e["lock"].release()

    if e["lock"].acquire(blocking=False):
        threading.Thread(target=de_fondo, daemon=True).start()
    return e["v"]


@st.cache_resource
def _precalentar() -> bool:
    """Servidor recién prendido: las descargas que la primera visita tiene que esperar (dólar en vivo, cripto, bolsas,
    noticias) arrancan todas juntas en paralelo, en vez de una detrás de otra. `al_dia` espera a que termine cada una."""
    mem = _memoria()

    def uno(nombre, bajar, ttl):
        e = _entrada(mem, nombre)
        with e["lock"]:
            if e["v"] is None:
                try:
                    _bajar_y_guardar(e, bajar, ttl, 60)
                except Exception:  # noqa: BLE001 — si falla, la visita lo vuelve a intentar con al_dia
                    traceback.print_exc()

    for nombre, bajar, ttl in (("vivo", _bajar_vivo, 30), ("cripto", _bajar_cripto, 300),
                               ("mercados", _bajar_mercados, 300), ("noticias", _bajar_noticias, 1800)):
        threading.Thread(target=uno, args=(nombre, bajar, ttl), daemon=True).start()
    return True


def cargar_noticias() -> dict[str, list[news.Noticia] | str]:
    return al_dia("noticias", _bajar_noticias, ttl=1800)


def cargar_cripto() -> dict[str, pd.DataFrame | str]:
    return al_dia("cripto", _bajar_cripto, ttl=300)


def cargar_mercados() -> dict[str, pd.DataFrame | str]:
    return al_dia("mercados", _bajar_mercados, ttl=300)


def cargar_vivo() -> dict[str, pd.DataFrame | str]:
    return al_dia("vivo", _bajar_vivo, ttl=30, reintento=30)


def _bajar_vivo() -> dict[str, pd.DataFrame | str]:
    """Dólar (DolarApi + CriptoYa) y riesgo país del momento. Se piden cada 30 segundos y pisan el dato del día de las series."""
    out: dict[str, pd.DataFrame | str] = {}
    for clave, fn in (("dolares", data.dolares_ahora), ("riesgo", data.riesgo_pais_ahora)):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    return out


def con_dolar_vivo(dol: pd.DataFrame | None, vivo) -> pd.DataFrame | None:
    """Agrega a la serie de dólares la cotización del momento: cada casa va en la fila de su fecha de actualización
    (si ya existe, se pisa; si es de hoy y no existe, se agrega). Nunca reemplaza un dato por uno más viejo."""
    if dol is None or not isinstance(vivo, pd.DataFrame) or vivo.empty:
        return dol
    d = dol.set_index("fecha")
    for _, r in vivo.iterrows():
        casa, f = r["casa"], pd.Timestamp(r["actualizado"]).normalize()
        if casa not in d or f > hoy():
            continue
        ultima = d[casa].dropna().index.max()
        if pd.notna(ultima) and f < ultima:
            continue
        d.loc[f, casa] = float(r["venta"])
        if f"{casa}_compra" in d and pd.notna(r["compra"]):
            d.loc[f, f"{casa}_compra"] = float(r["compra"])
    return d.sort_index().reset_index()


def con_riesgo_vivo(riesgo: pd.DataFrame | None, vivo) -> pd.DataFrame | None:
    if riesgo is None or not isinstance(vivo, pd.DataFrame) or vivo.empty:
        return riesgo
    u = vivo.iloc[-1]
    if u["fecha"] > hoy() or u["fecha"] < riesgo["fecha"].max():
        return riesgo
    return pd.concat([riesgo[riesgo["fecha"] != u["fecha"]], vivo[["fecha", "valor"]]]).sort_values("fecha").reset_index(drop=True)


def cargar_inversiones() -> dict[str, pd.DataFrame | str]:
    return al_dia("inversiones", _bajar_inversiones, ttl=1800)


def _bajar_inversiones() -> dict[str, pd.DataFrame | str]:
    """Tasas de plazo fijo por banco, rendimientos de plataformas, fondos money market (hoy y hace ~30 días, para
    calcular cuánto rindieron) y bitcoin en dólares. Cada parte falla por separado. Dura 30 minutos."""
    out: dict[str, pd.DataFrame | str] = {}
    for clave, fn in (("bancos", data.plazo_fijo_bancos), ("rendimientos", data.rendimientos_plataformas),
                      ("fci_hoy", data.fci), ("bitcoin", lambda: data.limpiar(data.indice("BTC-USD")))):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    out["fci_antes"] = "sin el dato de hoy"
    hoy_f = out["fci_hoy"]
    if isinstance(hoy_f, pd.DataFrame) and not hoy_f.empty:
        base = hoy_f["fecha"].max() - pd.Timedelta(days=30)
        # fines de semana y feriados no tienen datos, y algunos días la fuente trae pocos fondos o falla un momento:
        # se juntan hasta tres días hábiles cercanos (el primero de cada fondo) para que casi todos tengan con qué compararse
        dias, error = [], None
        for atras in range(8):
            f = base - pd.Timedelta(days=atras)
            try:
                antes = data.fci("mercadoDinero", f.strftime("%Y/%m/%d"))
            except Exception as e:  # noqa: BLE001
                error = error_corto(e)
                continue
            if not antes.empty:
                dias.append(antes)
                if len(dias) == 3 or len(antes) >= 150:
                    break
        if dias:
            out["fci_antes"] = pd.concat(dias, ignore_index=True).drop_duplicates("fondo").reset_index(drop=True)
        elif error:
            out["fci_antes"] = error
    return out


def _bajar_noticias() -> dict[str, list[news.Noticia] | str]:
    """Cada fuente falla por separado: si una cambia su sitio, la otra se sigue mostrando."""
    out: dict[str, list[news.Noticia] | str] = {}
    for clave, fn in (("bcra", news.bcra), ("economia", news.economia), ("indec", news.indec)):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    return out


def _bajar_cripto() -> dict[str, pd.DataFrame | str]:
    """Mercado de criptomonedas y precio del USDT por exchange. Cada parte falla por separado. Dura 5 minutos."""
    out: dict[str, pd.DataFrame | str] = {}
    for clave, fn in (("mercado", data.cripto_mercado), ("usdt", data.usdt_exchanges)):
        try:
            out[clave] = fn()
        except Exception as e:  # noqa: BLE001
            out[clave] = error_corto(e)
    return out


def _bajar_mercados() -> dict[str, pd.DataFrame | str]:
    """Cierres de las bolsas del mundo y materias primas (Yahoo Finance). Cada una falla por separado. 15 minutos."""
    def uno(item):
        simbolo = item[0]
        try:
            return simbolo, data.limpiar(data.indice(simbolo))
        except Exception as e:  # noqa: BLE001
            return simbolo, error_corto(e)

    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(pool.map(uno, data.INDICES))


def cargar_bonos() -> dict[str, pd.DataFrame | str]:
    """Bonos argentinos y tasas de EE. UU.: el precio del momento cada 5 minutos; las historias (un dato por día),
    cada hora."""
    return {**al_dia("bonos_hist", _bajar_bonos_hist, ttl=3600), **al_dia("bonos", _bajar_bonos, ttl=300)}


def _bajar_bonos() -> dict[str, pd.DataFrame | str]:
    try:
        return {"vivo": data.bonos_ahora()}
    except Exception as e:  # noqa: BLE001
        return {"vivo": error_corto(e)}


def _bajar_bonos_hist() -> dict[str, pd.DataFrame | str]:
    """Historia de cada bono argentino (data912) y de cada tasa de EE. UU. (FRED). Cada una falla por separado."""
    trabajos = [(f"bono:{b}", lambda b=b: data.bono_historia(b)) for _, ny, loc in data.BONOS_ARG for b in (ny, loc) if b]
    trabajos += [(f"fred:{s}", lambda s=s: data.fred(s)) for s, _ in data.TASAS_EEUU]

    def uno(t):
        clave, fn = t
        try:
            return clave, fn()
        except Exception as e:  # noqa: BLE001
            return clave, error_corto(e)

    with ThreadPoolExecutor(max_workers=8) as pool:
        return dict(pool.map(uno, trabajos))


@st.cache_data(ttl=900, show_spinner=False)
def _historia_cripto(coin_id: str, dias: int) -> pd.DataFrame:
    return data.limpiar(data.cripto_historia(coin_id, dias))  # si falla, la excepción no se guarda en el caché


@st.cache_resource
def _ultima_historia_cripto() -> dict:
    """Último historial bueno de cada moneda: si CoinGecko rechaza un pedido, se sigue mostrando ese."""
    return {}


@st.cache_data(ttl=60, show_spinner=False)
def historia_cripto(coin_id: str, dias: int) -> pd.DataFrame | str:
    """El error también se guarda (1 minuto): si CoinGecko rechaza por exceso de pedidos, no se reintenta en cada
    clic. Mientras tanto se usa el último historial bueno, si lo hay."""
    guardado = _ultima_historia_cripto()
    try:
        d = _historia_cripto(coin_id, dias)
        guardado[(coin_id, dias)] = d
        return d
    except Exception as e:  # noqa: BLE001
        return guardado.get((coin_id, dias), error_corto(e))


@st.cache_data(ttl=86400, show_spinner=False)
def cargar_fotos() -> dict[str, dict]:
    """Fotos de los presidentes (Wikipedia/Commons). Se piden una vez por día."""
    return presidentes.fotos()


@st.cache_resource
def _estado_actualizar() -> dict:
    """Estado compartido por todas las sesiones: cuándo se usó por última vez «Refrescar datos»."""
    return {"ultimo": 0.0}


def reintentar_si_fallo(cache_fn, clave: str, fallo: bool, espera: int = 60) -> None:
    """Que una falla pasajera no quede pegada en el caché: si algo falló, se borra el caché para volver a intentarlo
    en la próxima interacción (como máximo una vez cada `espera` segundos, para no martillar a las fuentes)."""
    if fallo and time.time() - st.session_state.get(f"_reintento_{clave}", 0) > espera:
        st.session_state[f"_reintento_{clave}"] = time.time()
        cache_fn.clear()


@contextmanager
def protegido(nombre: str):
    """Aísla una sección: si algo falla adentro, no se muestra (queda registrado) y el resto de la página sigue.
    (st.stop() y st.rerun() no son Exception, así que pasan de largo.)"""
    try:
        yield
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()  # queda en la consola del servidor para poder diagnosticarlo
        falla(f"no se pudo mostrar «{nombre}» ({type(e).__name__})")


@st.cache_resource
def _ultima_carga() -> dict:
    """Cuándo terminó la última carga de datos en este servidor (para saber si la próxima va a hacer esperar)."""
    return {"t": 0.0}


def _va_a_demorar() -> bool:
    """¿Hay que bajar todo de las fuentes? Solo si no hay datos en memoria ni un guardado en disco de menos de 12 h."""
    if time.time() - _ultima_carga()["t"] < 3600:
        return False
    try:
        return time.time() - CACHE_DISCO.stat().st_mtime >= DISCO_VIEJO_MAX
    except OSError:
        return True
