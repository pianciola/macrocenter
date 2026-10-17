"""Pestaña «Bonos» del tablero: bonos argentinos en dólares (ley Nueva York y ley local), tasa de la Reserva Federal
y bonos del Tesoro de EE. UU. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las funciones de
la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import charts, data, style

# colores sin juicio (la paleta general usa verde y rojo, que en la página significan bueno y malo)
NEUTROS = ("#74ACDF", "#F6B40E", "#A78BFA", "#8A9BB0", "#5EC4B6")
# cada tasa con su color fijo (el bono a 10 años, la referencia, en dorado para que se destaque)
COLOR_TASA = {"Tasa de la Fed": "#74ACDF", "Letra 3 meses": "#8A9BB0", "Bono 2 años": "#A78BFA",
              "Bono 10 años": "#F6B40E", "Bono 30 años": "#5EC4B6"}


def _df(x) -> pd.DataFrame | None:
    return x if isinstance(x, pd.DataFrame) and not x.empty else None


def _pct(v: float | None, dec: int = 1, signo: bool = True) -> str:
    if v is None or v != v:
        return "s/d"
    return (f"{v:+.{dec}f}%" if signo else f"{v:.{dec}f}%").replace(".", ",")


def mostrar(*, _ult_y_hace, cargar_bonos, dif, falla, grafico, grafico_periodo, kpi, selector_categoria) -> None:
    st.markdown(style.intro(
        "Los bonos del Tesoro argentino en dólares, de **ley Nueva York** y de **ley local**, y lo que paga Estados "
        "Unidos: la **tasa de la Reserva Federal** y sus **bonos del Tesoro**, que marcan el costo del dinero en el mundo.",
        [("bien", "Sube"), ("mal", "Baja")],
        "Los colores de los bonos argentinos siguen a la cotización. Las tasas de EE. UU. van sin color: que suban no es "
        "bueno ni malo en sí.", resumen='Precios de referencia y evolución de bonos argentinos en dólares.'), unsafe_allow_html=True)
    b = cargar_bonos()
    bonos_argentinos(b, falla, grafico_periodo, selector_categoria)
    st.divider()
    tasas_eeuu(b, _ult_y_hace, dif, falla, grafico_periodo, kpi)


def bonos_argentinos(b: dict, falla, grafico_periodo, selector_categoria) -> None:
    st.subheader("Bonos argentinos en dólares")
    st.caption("Cotizaciones con demora · fuente gratuita data912. Consulta cada 5 minutos; no es tiempo real. "
               "Si la fuente no responde, se muestra el último cierre disponible. Sin puntas ni profundidad de mercado.")
    vivo = _df(b.get("vivo"))
    hist = {k[5:]: v for k, v in b.items() if k.startswith("bono:") and _df(v) is not None}

    def dato(bono: str | None) -> tuple[float | None, float | None]:
        """(precio, variación del día): el del momento; si no hay, el último cierre."""
        if not bono:
            return None, None
        if vivo is not None:
            f = vivo[vivo["bono"] == bono]
            if not f.empty:
                return float(f.iloc[0]["precio"]), float(f.iloc[0]["var"])
        h = hist.get(bono)
        if h is not None and len(h) >= 2:
            return float(h.iloc[-1]["valor"]), (float(h.iloc[-1]["valor"]) / float(h.iloc[-2]["valor"]) - 1) * 100
        return None, None

    filas = []
    for anio, ny, loc in data.BONOS_ARG:
        p_ny, v_ny = dato(ny)
        p_loc, v_loc = dato(loc)
        if p_ny is None and p_loc is None:
            continue

        def precio(p, v, nombre):
            if p is None:
                return ("—", "") if nombre is None else ("s/d", "")
            return (charts.num(p, 2, pre="US$ "), "mejor" if v and v > 0 else "peor" if v and v < 0 else "",
                    f"{nombre} {_pct(v, 2)}")

        brecha = None if not (p_ny and p_loc) else (p_ny / p_loc - 1) * 100
        filas.append([anio, precio(p_ny, v_ny, ny), precio(p_loc, v_loc, loc),
                      "—" if brecha is None else _pct(brecha)])
    if not filas:
        falla("no se pudieron cargar los precios de los bonos argentinos")
        return
    st.markdown(style.tabla(["Vence", "Ley Nueva York", "Ley local", "NY vs. local"], filas, compacta=True),
                unsafe_allow_html=True)

    # historia: los dos bonos de un mismo vencimiento, uno al lado del otro
    anios = [a for a, ny, loc in data.BONOS_ARG if ny in hist or (loc and loc in hist)]
    if anios:
        anio = selector_categoria("Vencimiento", anios, "bonos_arg", defecto="2030" if "2030" in anios else anios[0])
        _, ny, loc = next(x for x in data.BONOS_ARG if x[0] == anio)
        partes = {f"{ny} (ley NY)": hist.get(ny), f"{loc} (ley local)": hist.get(loc) if loc else None}
        series = {n: d.set_index("fecha")["valor"] for n, d in partes.items() if d is not None}
        ancho = pd.concat(series, axis=1, sort=True).reset_index().rename(columns={"index": "fecha"})
        grafico_periodo(f"bonos_{anio}", ancho, lambda d: charts.lineas(
            d, {n: n for n in series}, f"Bonos {anio}: precio en dólares cada 100 de valor nominal", yfmt=",.0f",
            colores=NEUTROS), defecto="1 año")
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "Precio en dólares (MEP) cada 100 dólares de valor nominal; debajo, la variación de hoy. Los bonos "
                        "ya devolvieron parte del capital, así que un precio bajo no significa por sí solo que estén "
                        "baratos. Las caídas bruscas del gráfico son los días de pago (capital e intereses), no pérdidas."),
        ("NY vs. local", "Cuánto más caro está el bono de ley Nueva York que el de ley local del mismo vencimiento."),
        ("Ley NY y local", "Los **GD** se rigen por la ley de Nueva York y los **AL** y **AE**, por la ley argentina. Pagan "
                           "parecido; la diferencia de precio refleja cuánto valora el mercado la jurisdicción. El GD46 no "
                           "tiene un par de ley local."),
        ("Fuente", "data912, con precios de BYMA (fuente no oficial, con demora). Se actualiza cada 5 minutos."),
        leyenda=[("bien", "Subió hoy"), ("mal", "Bajó hoy")]), unsafe_allow_html=True)


def tasas_eeuu(b: dict, _ult_y_hace, dif, falla, grafico_periodo, kpi) -> None:
    st.subheader("Tasas y bonos de EE. UU.")
    series = {nombre: _df(b.get(f"fred:{s}")) for s, nombre in data.TASAS_EEUU}
    series = {n: d for n, d in series.items() if d is not None}
    if not series:
        falla("no se pudieron cargar las tasas de EE. UU.")
        return
    ayudas = {
        "Tasa de la Fed": "Techo del rango objetivo de la Reserva Federal: la tasa a la que se prestan los bancos entre sí "
                          "de un día para otro. La fija la Fed en sus reuniones.",
        "Letra 3 meses": "Rendimiento anual de las letras del Tesoro a 3 meses.",
        "Bono 2 años": "Rendimiento anual del bono del Tesoro a 2 años.",
        "Bono 10 años": "Rendimiento anual del bono del Tesoro a 10 años: la referencia de las tasas largas en el mundo.",
        "Bono 30 años": "Rendimiento anual del bono del Tesoro a 30 años.",
    }
    k = st.columns(len(series))
    for slot, (nombre, d) in zip(k, series.items()):
        v, a_ = _ult_y_hace(d)
        kpi(slot, f"{nombre} (%)", v, 2, d=dif(v, a_), d_suf=" pp", d_dec=2, color="off",
            help=ayudas[nombre] + " Variación contra 30 días atrás.", serie=d, fuente='FRED · Fed / Tesoro de EE. UU.')
    ancho = pd.concat({n: d.set_index("fecha")["valor"] for n, d in series.items()}, axis=1, sort=True)
    ancho = ancho.ffill().reset_index().rename(columns={"index": "fecha"})  # la tasa de la Fed viene todos los días
    grafico_periodo("bonos_eeuu", ancho, lambda d: charts.lineas(
        d, {n: n for n in series}, "Tasa de la Fed y rendimiento de los bonos del Tesoro de EE. UU. (% anual)",
        yfmt=",.1f", colores=tuple(COLOR_TASA[n] for n in series), ocultas=("Letra 3 meses", "Bono 30 años")),
        defecto="2 años")
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "Cuando estas tasas suben, el dinero en el mundo se encarece: los países y las empresas pagan más "
                        "para endeudarse. El **riesgo país** se mide justamente contra los bonos del Tesoro de EE. UU."),
        ("Nota", "Los rendimientos de los bonos se mueven todos los días; la tasa de la Fed cambia solo en sus reuniones. "
                "Tocá un nombre en la leyenda para mostrar u ocultar cada línea."),
        ("Fuente", "Reserva Federal de St. Louis (FRED), datos diarios.")), unsafe_allow_html=True)
