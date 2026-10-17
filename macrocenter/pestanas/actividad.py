"""Pestaña «Actividad y PBI» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, series, style


def mostrar(*, dif, emae, emae_sa, get, grafico, kpi, paro, paro_pct, pib, rec, ult_y_ant) -> None:
    st.markdown(style.intro("Cómo viene la producción: el **PBI** (trimestral, con unos tres meses de demora) y el **EMAE**, el indicador "
                            "mensual del INDEC que lo anticipa.", [("bien", "La actividad mejora"), ("mal", "Empeora")], resumen='Actividad económica mensual y producto bruto interno.'), unsafe_allow_html=True)
    p = None
    if pib is not None:
        p = pib.copy()
        p["interanual"] = series.cambio_periodico(p, periodos=4, frecuencia="Q")["valor"]
        p["trimestral"] = series.cambio_periodico(p, periodos=1, frecuencia="Q")["valor"]
    mom = get("serie:emae_sa_mom")
    if mom is not None and mom["valor"].abs().max() < 1:  # datos.gob.ar la publica como fracción (-0,029 = -2,9%)
        mom = mom.assign(valor=mom["valor"] * 100)
    e_ia = emae.assign(interanual=series.cambio_periodico(emae)["valor"]).dropna() if emae is not None else None
    k = st.columns(4)
    v, a_ = ult_y_ant(p, "interanual", meses=3)
    kpi(k[0], "PBI · var. interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs trim. ant.",
        help="Último trimestre publicado contra el mismo trimestre del año anterior.", serie=p.dropna(subset=["interanual"]) if p is not None else None, fuente='INDEC')
    v, a_ = ult_y_ant(mom)
    kpi(k[1], "EMAE · var. mensual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.",
        help="Desestacionalizada: compara con el mes anterior sin el efecto de la época del año.", serie=mom, fuente='INDEC')
    v, a_ = ult_y_ant(e_ia, "interanual")
    kpi(k[2], "EMAE · var. interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", serie=e_ia, fuente='INDEC')
    v, a_ = ult_y_ant(paro_pct, meses=3)
    kpi(k[3], "Desocupación (EPH)", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs trim. ant.", color="inverse", serie=paro_pct, fuente='INDEC · EPH')
    if p is not None:
        st.markdown("#### PBI trimestral")
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(p, 5), {"PBI real": "valor"}, "PBI trimestral a precios constantes de 2004 (millones de $)"))
        with b:
            grafico(charts.barras(rec(p.dropna(subset=["interanual"]), 5), "interanual",
                                  "PBI — variación interanual (%)", color_signo=True))
        st.markdown(style.aclaracion(
            ("Qué mide", "Serie trimestral sin desestacionalizar de Cuentas Nacionales."),
            ("Último dato", f"{p['fecha'].iloc[-1]:%m/%Y} (inicio de trimestre)."),
            ("Fuente", "INDEC.")), unsafe_allow_html=True)
    if emae_sa is not None:
        st.markdown("#### Actividad mes a mes (EMAE)")
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(emae_sa, 3), {"EMAE desestacionalizado": "valor"},
                                  "EMAE desestacionalizado (base 2004 = 100)", yfmt=",.0f"))
        with b:
            if mom is not None:
                grafico(charts.barras(rec(mom, 3), "valor", "EMAE — variación mensual desestacionalizada (%)", yfmt=",.1f", color_signo=True))
    if emae is not None:
        with st.expander("EMAE interanual y desocupación"):
            e = emae.assign(interanual=series.cambio_periodico(emae)["valor"]).dropna()
            a, b = st.columns(2)
            with a:
                grafico(charts.barras(rec(e, 3), "interanual", "EMAE — variación interanual (%)", color_signo=True))
            with b:
                if paro is not None:
                    grafico(charts.lineas(rec(paro.assign(valor=paro["valor"] * 100), 5), {"Desocupación": "valor"},
                                          "Tasa de desocupación (EPH, %)", yfmt=",.1f"))
