"""Monitor de MacroCenter: lo corre GitHub Actions cada 6 horas (ver .github/workflows/monitor.yml).

Revisa tres cosas y, si alguna está mal, termina con error: GitHub le manda un mail al dueño del repositorio.
  1. Que la página publicada responda.
  2. Que cada fuente de datos funcione (con un reintento: una falla de un minuto no es motivo de alarma) y que su
     último dato no esté desactualizado para lo que se espera de esa serie (diaria, mensual, trimestral o anual).
     Las fuentes «críticas» (oficiales) disparan el aviso; las «secundarias» (no oficiales, que a veces rechazan
     pedidos desde servidores de GitHub) solo quedan anotadas en el resumen.
  3. Que todas las pantallas de la app se dibujen sin errores con los datos de ese momento.

No guarda ni manda datos de nadie: solo consulta fuentes públicas y la propia página.
Se puede correr a mano: python monitor/revisar.py
"""
from __future__ import annotations

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import requests  # noqa: E402

from macrocenter import data, news  # noqa: E402

URL = "https://macrocenter-argentina.streamlit.app"
DESDE_BCRA = "2016-01-01"  # el mismo que usa app.py
REINTENTO_S = 90


def fuentes() -> tuple[dict, dict]:
    """(críticas, secundarias): nombre -> función que descarga. Las mismas que usa app.py."""
    criticas = {f"BCRA · {k}": (lambda k=k: data.bcra(k, desde=DESDE_BCRA)) for k in data.BCRA_IDS}
    criticas |= {f"INDEC/Economía · {k}": (lambda k=k: data.serie(k)) for k in data.SERIES_IDS}
    criticas |= {"ArgentinaDatos · dólares": data.dolares, "ArgentinaDatos · riesgo país": data.riesgo_pais,
                 "ArgentinaDatos · dólar histórico": data.dolar_historico,
                 "ArgentinaDatos · inflación histórica": data.inflacion_historica,
                 "BCRA · euro": lambda: data.divisa("EUR"), "BCRA · libra": lambda: data.divisa("GBP")}
    secundarias = {"FRED · inflación EE. UU.": data.ipc_eeuu, "CoinGecko · criptomonedas": data.cripto_mercado,
                   "CriptoYa · USDT": data.usdt_exchanges, "Noticias · BCRA": news.bcra,
                   "Noticias · Economía": news.economia, "Noticias · INDEC": news.indec,
                   "ArgentinaDatos · plazo fijo por banco": data.plazo_fijo_bancos,
                   "ArgentinaDatos · rendimientos de plataformas": data.rendimientos_plataformas,
                   "ArgentinaDatos · fondos money market": data.fci}
    secundarias |= {f"Yahoo · {nombre}": (lambda s=simbolo: data.indice(s)) for simbolo, nombre, *_ in data.INDICES}
    return criticas, secundarias


# Series de archivo (terminan a propósito) o que la fuente dejó de publicar: no cuentan como desactualizadas.
# (reservas_hist es el saldo mensual desde 1940 para la historia de presidentes: lo reciente sale de la serie diaria
# del BCRA, así que su atraso no se ve en la página. ipc_neuquen: la página la muestra solo cuando está al día)
SIN_FRESCURA = {"BCRA · tpm", "INDEC/Economía · pib_1986", "INDEC/Economía · pib_1993", "ArgentinaDatos · dólar histórico",
                "INDEC/Economía · reservas_hist", "INDEC/Economía · ipc_neuquen"}


def dias_maximos(paso_dias: float) -> int:
    """Cuántos días puede tener el último dato según cada cuánto se publica la serie (con el retraso habitual de cada
    organismo: el INDEC publica un trimestre casi tres meses después de terminado; algunas provincias, dos meses)."""
    if paso_dias <= 3:
        return 10      # diarias (contando feriados largos)
    if paso_dias <= 45:
        return 180     # mensuales
    if paso_dias <= 120:
        return 300     # trimestrales
    return 900         # anuales


def antiguedad(r) -> str | None:
    """Si la serie tiene fechas y su último dato es más viejo de lo esperable, lo dice; si no, None."""
    if not hasattr(r, "columns") or "fecha" not in r.columns or len(r) < 3:
        return None
    import pandas as pd

    f = pd.to_datetime(r["fecha"], errors="coerce").dropna().sort_values()
    hoy = pd.Timestamp(data.hoy_argentina())
    f_pasado = f[f <= hoy]
    if f_pasado.empty:
        return None
    paso = float(f.diff().dt.days.median())
    edad = (hoy - f_pasado.iloc[-1]).days
    if edad > dias_maximos(paso):
        return f"desactualizada: último dato del {f_pasado.iloc[-1]:%d/%m/%Y} ({edad} días)"
    return None


def probar(fn, nombre: str = "") -> str | None:
    """None si anda (y trae datos al día); si no, el error en pocas palabras."""
    try:
        r = fn()
        if r is None or (hasattr(r, "empty") and r.empty) or (isinstance(r, (list, dict)) and not r):
            return "respondió vacío"
        return None if nombre in SIN_FRESCURA else antiguedad(r)
    except Exception as e:  # noqa: BLE001 — cualquier falla cuenta como falla de la fuente
        return f"{type(e).__name__}: {str(e)[:120]}"


def revisar_fuentes(tareas: dict) -> dict[str, str]:
    """Prueba todas en paralelo; las que fallan se reintentan una vez después de REINTENTO_S segundos."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        res = dict(zip(tareas, pool.map(probar, tareas.values(), tareas)))
    fallan = {k: v for k, v in res.items() if v}
    if fallan:
        time.sleep(REINTENTO_S)
        with ThreadPoolExecutor(max_workers=8) as pool:
            res2 = dict(zip(fallan, pool.map(probar, (tareas[k] for k in fallan), fallan)))
        fallan = {k: v for k, v in res2.items() if v}
    return fallan


def revisar_sitio() -> tuple[str, str]:
    """('ok' | 'dormida' | 'caida', detalle). Una app dormida (sin visitas por un tiempo) no es una falla."""
    try:
        r = requests.get(f"{URL}/~/+/_stcore/health", timeout=60)
        if r.status_code == 200 and r.text.strip() == "ok":
            return "ok", "responde"
    except requests.RequestException as e:
        detalle = type(e).__name__
    else:
        detalle = f"health HTTP {r.status_code}"
    try:
        r = requests.get(URL + "/", timeout=60)
        if r.status_code == 200:
            return "dormida", f"{detalle}; la portada responde (la app está dormida o arrancando)"
        return "caida", f"{detalle}; portada HTTP {r.status_code}"
    except requests.RequestException as e:
        return "caida", f"{detalle}; portada {type(e).__name__}"


def revisar_pantallas() -> list[str]:
    """Dibuja cada pantalla con AppTest y devuelve los problemas (excepciones o secciones que no se pudieron mostrar)."""
    pestanas = ["Resumen", "Dólar", "Bonos", "Cripto", "Bolsas", "Reservas", "Inflación y dinero", "Tasas",
                "Actividad", "Empleo y salarios", "Resultado fiscal", "Comercio exterior"]
    vistas = [(f"Tablero · {p}", {"pestana": p}) for p in pestanas]
    vistas += [("Historia · Presidentes", {"vista": "historia"}),
               ("Historia · Ministros", {"vista": "historia", "hist_seccion": "Ministros de Economía"}),
               ("Historia · Viaje en el tiempo", {"vista": "historia", "hist_seccion": "Viaje en el tiempo"}),
               ("Historia · Comparador de épocas", {"vista": "historia", "hist_seccion": "Comparador de épocas"})]
    vistas += [(f"Herramientas · {m}", {"vista": "juegos", "inter_modo": m}) for m in
               ["¿Cuánto valían tus pesos?", "Ajuste de alquileres", "Glosario financiero"]]
    problemas = _correr_vistas(vistas)
    if problemas:  # una falla de un momento (una API que tardó) no es motivo de alarma: se vuelve a mirar lo que falló
        time.sleep(REINTENTO_S)
        try:  # lo que se bajó mal queda guardado en memoria unos minutos: se descarta para que se vuelva a bajar
            from macrocenter import carga

            carga._memoria().clear()
        except Exception:  # noqa: BLE001
            pass
        fallaron = {p.split(":")[0] for p in problemas}
        problemas = _correr_vistas([v for v in vistas if v[0] in fallaron])
    return problemas


def _correr_vistas(vistas: list) -> list[str]:
    from streamlit.testing.v1 import AppTest

    problemas = []
    for nombre, estado in vistas:
        at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=300)
        for k, v in estado.items():
            at.session_state[k] = v
        try:
            at.run()
        except Exception as e:  # noqa: BLE001
            problemas.append(f"{nombre}: no terminó de cargar ({type(e).__name__})")
            continue
        for e in at.exception:
            problemas.append(f"{nombre}: error — {str(e.value)[:150]}")
        # la página no muestra avisos de falla: las anota en session_state["_fallas"] (ver macrocenter/avisos.py)
        try:
            fallas = list(at.session_state["_fallas"])
        except (KeyError, AttributeError):
            fallas = []
        for f in dict.fromkeys(fallas):
            problemas.append(f"{nombre}: {str(f)[:150]}")
    return problemas


def main() -> int:
    t0 = time.time()
    estado_sitio, det_sitio = revisar_sitio()
    criticas, secundarias = fuentes()
    f_crit = revisar_fuentes(criticas)
    f_sec = revisar_fuentes(secundarias)
    pantallas = revisar_pantallas()

    alarma = estado_sitio == "caida" or bool(f_crit) or bool(pantallas)
    lineas = ["# Monitor de MacroCenter", "",
              f"**Resultado: {'⚠️ HAY PROBLEMAS' if alarma else '✅ todo bien'}** ({time.time() - t0:.0f} s)", "",
              "| Revisión | Estado | Detalle |", "|---|---|---|",
              f"| Página publicada | {'✅' if estado_sitio == 'ok' else '💤' if estado_sitio == 'dormida' else '❌'} | {det_sitio} |",
              f"| Fuentes críticas ({len(criticas)}) | {'✅' if not f_crit else '❌'} | "
              f"{'todas responden' if not f_crit else f'{len(f_crit)} fallan'} |",
              f"| Fuentes secundarias ({len(secundarias)}) | {'✅' if not f_sec else '⚠️'} | "
              f"{'todas responden' if not f_sec else f'{len(f_sec)} fallan (no dispara aviso)'} |",
              f"| Pantallas de la app | {'✅' if not pantallas else '❌'} | "
              f"{'todas se dibujan bien' if not pantallas else f'{len(pantallas)} con problemas'} |"]
    for titulo, cosas in (("Fuentes críticas que fallan", [f"{k} — {v}" for k, v in f_crit.items()]),
                          ("Fuentes secundarias que fallan", [f"{k} — {v}" for k, v in f_sec.items()]),
                          ("Pantallas con problemas", pantallas)):
        if cosas:
            lineas += ["", f"### {titulo}", ""] + [f"- {c}" for c in cosas]
    texto = "\n".join(lineas)
    print(texto)
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    return 1 if alarma else 0


if __name__ == "__main__":
    sys.exit(main())
