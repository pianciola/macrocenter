"""Herramientas interactivas: ¿cuánto valían tus pesos?, comparador de épocas y viaje en el tiempo.

Todo se calcula con las mismas series de la sección de historia económica (nada escrito a mano), y vale lo
mismo que allí: el dólar solo desde 1992, el riesgo país desde 1999, la inflación 2007-2015 es la del INDEC
intervenido.
"""
from __future__ import annotations

import random
import time
from datetime import date

import pandas as pd
import streamlit as st

from macrocenter import charts, style
from macrocenter import presidentes as P

HOY = pd.Timestamp.today().normalize()
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
         "Diciembre"]
FECHA_MIN = date(1992, 1, 2)  # desde la convertibilidad: antes las monedas eran otras (peso argentino, austral)


# ───────────────────────── valores a una fecha ─────────────────────────
def serie_dolar(d: dict) -> pd.DataFrame:
    """Dólar oficial diario unificado (BCRA hasta 2010, ArgentinaDatos desde 2011)."""
    h, a = d["dolar_hist"], d["dolar_actual"]
    return pd.concat([h[h["fecha"] < a["fecha"].min()], a]).sort_values("fecha").reset_index(drop=True)


def dolar_en(d: dict, f: pd.Timestamp) -> float | None:
    return P.dolar_oficial(d["dolar_hist"], d["dolar_actual"], f)


# Períodos de cepo cambiario: al dólar oficial no se podía comprar libremente (para personas).
CEPOS = [(pd.Timestamp("2011-10-28"), pd.Timestamp("2015-12-16")), (pd.Timestamp("2019-09-01"), pd.Timestamp("2025-04-14"))]


def en_cepo(f: pd.Timestamp) -> bool:
    return any(a <= f < b for a, b in CEPOS)


def dolar_accesible(d: dict, f: pd.Timestamp) -> tuple[float | None, str]:
    """(precio, nombre) del dólar que una persona podía comprar en la fecha `f`: durante el cepo, el blue (si hay dato);
    el resto del tiempo, el oficial."""
    blue = d.get("dolar_blue")
    if en_cepo(f) and isinstance(blue, pd.DataFrame) and not blue.empty and f >= blue["fecha"].min():
        v = P._antes(blue, f)
        if v:
            return v, "blue"
    return dolar_en(d, f), "oficial"


def reservas_en(d: dict, f: pd.Timestamp) -> float | None:
    ra = d["reservas_actual"]
    return P._antes(ra, f) if f >= ra["fecha"].min() else P._mes_previo(d["reservas_hist"], f)


def paro_en(d: dict, f: pd.Timestamp) -> float | None:
    t = d.get("paro_trim")
    if t is not None and not t.empty and f >= HOY - pd.Timedelta(days=100):
        return float(t.iloc[-1]["valor"]) * 100
    x = d["paro_anual"][d["paro_anual"]["fecha"].dt.year == P._anio_ref(f)]
    return None if x.empty else float(x.iloc[-1]["valor"]) * 100


def riesgo_en(d: dict, f: pd.Timestamp) -> float | None:
    rp = d["riesgo"]
    return P._antes(rp, f) if f >= rp["fecha"].min() else None


def pbi_en(d: dict, f: pd.Timestamp) -> float | None:
    s = d["pbi"][d["pbi"].index <= f]
    return None if s.empty else float(s.iloc[-1])


def estado_en(d: dict, f: pd.Timestamp) -> dict:
    return {"inflacion": P.inflacion_12m(d["inflacion"], f), "dolar": dolar_en(d, f), "reservas": reservas_en(d, f),
            "riesgo": riesgo_en(d, f), "paro": paro_en(d, f), "pbi": pbi_en(d, f)}


def mandato_en(f: pd.Timestamp):
    for m in P.MANDATOS:
        if m.desde <= f <= m.fin and (f < m.fin or m.hasta is None):
            return m
    return None


def _n(x, dec=0, pre="", suf=""):
    return charts.num(x, dec, suf, pre)


def _md(texto: str) -> str:
    """Escapa el signo $ para que Markdown no lo tome como fórmula matemática."""
    return texto.replace("$", "\\$")


# ───────────────────────── 1) ¿Cuánto valían tus pesos? ─────────────────────────
def factor_precios(inf: pd.DataFrame, f: pd.Timestamp) -> float:
    """Cuánto se multiplicaron los precios desde fin del mes de `f` hasta el último mes publicado."""
    d = inf[inf["fecha"] > f + pd.offsets.MonthEnd(0)]
    return float((1 + d["valor"] / 100).prod())


def indices_base100(d: dict, f: pd.Timestamp, uva: pd.DataFrame | None) -> pd.DataFrame:
    """Precios, dólar oficial y UVA en base 100 al fin del mes de `f`, mes a mes."""
    inf = d["inflacion"].set_index("fecha")["valor"]
    nivel = (1 + inf / 100).cumprod()
    ini = f + pd.offsets.MonthEnd(0)
    meses = [m for m in nivel.index if m >= ini]
    out = pd.DataFrame({"fecha": meses, "Precios": [nivel[m] / nivel[ini] * 100 for m in meses]})
    usd = serie_dolar(d).set_index("fecha")["valor"]
    base_usd = usd[usd.index <= ini].iloc[-1] if (usd.index <= ini).any() else None
    if base_usd:
        out["Dólar oficial"] = [usd[usd.index <= m].iloc[-1] / base_usd * 100 for m in meses]
    blue = d.get("dolar_blue")
    if isinstance(blue, pd.DataFrame) and not blue.empty and ini >= blue["fecha"].min():
        b = blue.set_index("fecha")["valor"]
        base_b = b[b.index <= ini].iloc[-1]
        out["Dólar blue"] = [b[b.index <= min(m, HOY)].iloc[-1] / base_b * 100 for m in meses]
    if uva is not None and ini >= uva["fecha"].min():
        u = uva.set_index("fecha")["valor"]
        base_u = u[u.index <= ini].iloc[-1]
        out["UVA"] = [u[u.index <= min(m, HOY)].iloc[-1] / base_u * 100 for m in meses]
    return out


def pantalla_pesos(d: dict, uva: pd.DataFrame | None) -> None:
    st.markdown("##### ¿Cuánto valían tus pesos?")
    st.caption("Poné un monto y una fecha: te mostramos qué fue de esa plata según la inflación, el dólar oficial y la UVA.")
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto en pesos de esa fecha", min_value=1.0, value=100_000.0, step=10_000.0, format="%.0f")
    f = pd.Timestamp(c2.date_input("¿En qué fecha lo tenías?", value=date(2019, 12, 10), min_value=FECHA_MIN,
                                   max_value=(HOY - pd.Timedelta(days=60)).date(), format="DD/MM/YYYY"))

    fac = factor_precios(d["inflacion"], f)
    equiv = monto * fac
    usd0, tipo0 = dolar_accesible(d, f)
    usd_hoy, tipo_hoy = dolar_accesible(d, HOY)
    en_usd = monto / usd0 if usd0 else None
    usd_en_pesos = en_usd * usd_hoy if en_usd and usd_hoy else None
    u0 = u_hoy = None
    if uva is not None and f >= uva["fecha"].min():
        u0 = P._antes(uva, f)
        u_hoy = P._antes(uva, HOY)
    uva_en_pesos = monto / u0 * u_hoy if u0 and u_hoy else None

    k = st.columns(4)
    k[0].metric("Para comprar lo mismo hoy necesitás", _n(equiv, 0, "$"), f"×{_n(fac, 1)} los precios", delta_color="off",
                border=True, help="Precios hasta el último mes publicado por el INDEC.")
    k[1].metric("Tus pesos de entonces hoy compran", _n(100 / fac, 1, suf="%"), "de lo que compraban", delta_color="off",
                border=True)
    k[2].metric("Si los hubieras pasado a dólares", _n(usd_en_pesos, 0, "$") if usd_en_pesos else "s/d",
                f"USD {_n(en_usd, 0)} a ${_n(usd0, 0)} ({tipo0})" if en_usd else None, delta_color="off", border=True,
                help="Se usa el dólar que de verdad se podía comprar: durante el cepo (2011-2015 y 2019-2025) el blue, "
                     "porque al oficial no se accedía libremente; fuera del cepo, el oficial. Hoy se valúan al "
                     f"dólar {tipo_hoy}.")
    k[3].metric("Si los hubieras puesto en UVA", _n(uva_en_pesos, 0, "$") if uva_en_pesos else "s/d",
                None if uva_en_pesos else "UVA existe desde 2016", delta_color="off", border=True)

    # veredicto en una línea
    opciones = {"la inflación (precios)": equiv}
    if usd_en_pesos:
        opciones["el dólar"] = usd_en_pesos
    if uva_en_pesos:
        opciones["la UVA"] = uva_en_pesos
    mejor = max(opciones, key=opciones.get)
    st.markdown(f"De estas opciones, la que más creció desde esa fecha fue **{mejor}**: "
                f"{_n(opciones[mejor] / monto, 1)} veces el monto original. "
                f"Dejar los pesos quietos hubiera sido perder **{_n((1 - 1 / fac) * 100, 0, suf='%')}** de poder de compra.")

    graf = indices_base100(d, f, uva)
    cols = {c: c for c in ("Precios", "Dólar oficial", "Dólar blue", "UVA") if c in graf}
    st.plotly_chart(charts.lineas(graf, cols, "Cómo evolucionó cada cosa (base 100 = la fecha elegida)", yfmt=",.0f",
                                  height=340), width="stretch")
    st.caption("Valores mes a mes (aproximados). No es una recomendación de inversión: es solo mirar el pasado."
               + (" La fecha elegida cae en un período de cepo: al dólar oficial no se podía comprar libremente, así que "
                  "el cálculo usa el blue." if tipo0 == "blue" else ""))


# ───────────────────────── 2) Comparador de épocas ─────────────────────────
def _momentos() -> dict[str, pd.Timestamp | None]:
    m = {"Hoy": HOY}
    for x in P.MANDATOS:
        m[f"Asumió {P.CORTO[x.clave]} ({x.desde.year})"] = x.desde
    m["Otra fecha…"] = None
    return m


def _elegir_momento(slot, etiqueta: str, clave: str, defecto: str) -> pd.Timestamp:
    opciones = _momentos()
    previo = st.session_state.get(clave)  # el estado puede venir alterado: si no es una opción válida, se vuelve al defecto
    if not isinstance(previo, str) or previo not in opciones:
        st.session_state[clave] = defecto
    # sin `index=`: el valor inicial ya está en el estado (pasar ambos hace que Streamlit muestre una advertencia)
    nombre = slot.selectbox(etiqueta, list(opciones), key=clave)
    if opciones[nombre] is None:
        return pd.Timestamp(slot.date_input("Fecha", value=date(2010, 6, 1), min_value=date(1984, 1, 1),
                                            max_value=HOY.date(), format="DD/MM/YYYY", key=clave + "_f"))
    return opciones[nombre]


def _cambio_pp(a, b, mejor="bajo", dec=1):
    if a is None or b is None:
        return "s/d", ""
    dif = b - a
    return f"{dif:+,.{dec}f} pp".replace(",", "§").replace(".", ",").replace("§", "."), P._tendencia(a, b, mejor)


def pantalla_comparador(d: dict) -> None:
    st.markdown("##### Comparador de épocas")
    st.caption("Elegí dos momentos y mirá cómo estaba la economía en cada uno.")
    c1, c2 = st.columns(2)
    fa = _elegir_momento(c1, "Momento A", "cmp_a", "Asumió Macri (2015)")
    fb = _elegir_momento(c2, "Momento B", "cmp_b", "Hoy")
    a, b = estado_en(d, fa), estado_en(d, fb)
    ma, mb = mandato_en(fa), mandato_en(fb)

    def fila(k, va, vb, fmt, cambio, tend=""):
        return {"k": k, "a": fmt(va) if va is not None else "s/d", "b": fmt(vb) if vb is not None else "s/d",
                "cambio": cambio, "tend": tend}

    cambio_inf, t_inf = _cambio_pp(a["inflacion"], b["inflacion"])
    cambio_paro, t_paro = _cambio_pp(a["paro"], b["paro"])
    cambio_rp, t_rp = _cambio_pp(a["riesgo"], b["riesgo"], dec=0)
    cambio_rp = cambio_rp.replace(" pp", " pb")
    usd_x = f"×{_n(b['dolar'] / a['dolar'], 1)}" if a["dolar"] and b["dolar"] else "s/d"
    res_x = (f"{(b['reservas'] / a['reservas'] - 1) * 100:+,.0f}%".replace(",", ".")
             if a["reservas"] and b["reservas"] else "s/d")
    pbi_x = f"{(b['pbi'] / a['pbi'] - 1) * 100:+,.1f}%".replace(".", ",") if a["pbi"] and b["pbi"] else "s/d"
    filas = [
        {"k": "Quién gobernaba", "a": ma.nombre if ma else "—", "b": mb.nombre if mb else "—", "cambio": "", "tend": ""},
        fila("Inflación anual", a["inflacion"], b["inflacion"], P._pct, cambio_inf, t_inf),
        fila("Dólar oficial", a["dolar"], b["dolar"], lambda v: _n(v, 2, "$"), usd_x),
        fila("Reservas (USD M)", a["reservas"], b["reservas"], lambda v: _n(v), res_x,
             P._tendencia(a["reservas"], b["reservas"], "alto")),
        fila("Riesgo país (pb)", a["riesgo"], b["riesgo"], lambda v: _n(v), cambio_rp, t_rp),
        fila("Desocupación", a["paro"], b["paro"], P._pct, cambio_paro, t_paro),
        {"k": "PBI real entre ambas fechas", "a": "", "b": "", "cambio": pbi_x,
         "tend": "" if pbi_x == "s/d" else ("mejor" if pbi_x.startswith("+") else "peor")},
    ]
    st.markdown(style.comparacion(filas, "A", "B"), unsafe_allow_html=True)
    st.caption("s/d = sin dato confiable para esa fecha (dólar: antes de 1992; riesgo país: antes de 1999).")


# ───────────────────────── 3) Viaje en el tiempo ─────────────────────────
def _cuadro_viaje(d: dict, fotos: dict, f: pd.Timestamp) -> None:
    m = mandato_en(f)
    if m:
        ft = fotos.get(m.clave, {})
        ini = "".join(x[0] for x in m.nombre.split() if x[0].isupper())[:2]
        st.markdown(style.viaje(m.nombre, ini, m.periodo, m.hito, ft.get("url"), ft.get("pagina"), m.hasta is None),
                    unsafe_allow_html=True)
    else:
        st.markdown(style.viaje("Período de transición", "··", "Diciembre de 2001",
                                "Entre la renuncia de De la Rúa y la asunción de Duhalde pasaron varios presidentes en pocos días.",
                                None, None, False), unsafe_allow_html=True)
    e = estado_en(d, f)
    k = st.columns(5)
    k[0].metric("Inflación anual", P._pct(e["inflacion"]), border=True)
    k[1].metric("Dólar oficial", _n(e["dolar"], 2, "$") if e["dolar"] else "s/d", border=True)
    k[2].metric("Reservas (USD M)", _n(e["reservas"]), border=True)
    k[3].metric("Riesgo país", _n(e["riesgo"]) if e["riesgo"] else "s/d", border=True)
    k[4].metric("Desocupación", P._pct(e["paro"]), border=True)
    anual = P.inflacion_anual_serie(d["inflacion"])
    st.plotly_chart(charts.inflacion_presidentes(anual[anual["fecha"] >= "1983-12-01"], P.MANDATOS, P.CORTO,
                                                 "Inflación anual: estás en la línea dorada", height=300, marca=f),
                    width="stretch")


def pantalla_viaje(d: dict, fotos: dict) -> None:
    st.markdown("##### Viaje en el tiempo")
    st.caption("Elegí una fecha y mirá cómo estaba el país ese día. También podés dejar que avance solo hasta hoy.")
    f = pd.Timestamp(st.slider("Fecha", min_value=date(1984, 1, 1), max_value=HOY.date(), value=date(2015, 12, 10),
                               format="MM/YYYY", key="viaje_fecha"))
    lugar = st.empty()
    if st.button("Reproducir hasta hoy"):
        actual = f
        while actual < HOY:
            with lugar.container():
                st.markdown(f"**{MESES[actual.month - 1]} de {actual.year}**")
                _cuadro_viaje(d, fotos, actual)
            time.sleep(0.8)
            actual += pd.DateOffset(years=1)
        f = HOY
    with lugar.container():
        _cuadro_viaje(d, fotos, f)


# ───────────────────────── entrada ─────────────────────────
MODOS = ["¿Cuánto valían tus pesos?", "Comparador de épocas", "Viaje en el tiempo"]
TARJETAS = {  # ícono (Material) y descripción corta de cada herramienta
    "¿Cuánto valían tus pesos?": (":material/savings:", "Qué fue de tu plata según la inflación, el dólar y la UVA."),
    "Comparador de épocas": (":material/compare_arrows:", "Dos momentos de la economía, lado a lado."),
    "Viaje en el tiempo": (":material/history:", "Elegí una fecha y mirá cómo estaba el país."),
    "Calificación macro": (":material/speed:", "Una nota de 0 a 100: hoy contra el pasado reciente."),
}


def mostrar(d: dict, inds: dict, fotos: dict, uva: pd.DataFrame | None, extra: dict | None = None) -> None:
    """`extra`: secciones adicionales {nombre: función sin argumentos} que se suman al selector."""
    extra = extra or {}
    opciones = MODOS + list(extra)
    if st.session_state.get("inter_modo") not in opciones:  # estado inicial o alterado: la primera herramienta
        st.session_state["inter_modo"] = MODOS[0]

    def elegir(nombre: str) -> None:
        st.session_state["inter_modo"] = nombre

    # selector en tarjetas: ícono, nombre y una línea de qué hace; la elegida queda resaltada
    st.caption("Elegí una herramienta:")
    for i, (col, nombre) in enumerate(zip(st.columns(len(opciones)), opciones)):
        icono, desc = TARJETAS.get(nombre, (":material/apps:", ""))
        with col:
            st.button(nombre, key=f"modo_{i}", icon=icono, width="stretch", on_click=elegir, args=(nombre,),
                      type="primary" if st.session_state["inter_modo"] == nombre else "secondary")
            st.caption(desc)
    st.divider()
    modo = st.session_state["inter_modo"]
    if modo in extra:
        extra[modo]()
    elif modo == MODOS[0]:
        pantalla_pesos(d, uva)
    elif modo == MODOS[1]:
        pantalla_comparador(d)
    else:
        pantalla_viaje(d, fotos)
