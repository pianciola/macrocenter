"""Pestaña «Dinero y crédito» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style


def mostrar(*, _ult_y_hace, delta, dif, get, grafico, kpi, rec, ultimo) -> None:
    bm, pr, m2 = get("bcra:base_monetaria"), get("bcra:prestamos_privados"), get("bcra:m2_privado_ia")
    st.markdown(style.intro("Cuántos pesos hay en la economía (**base monetaria** y **M2**) y cuánto le prestan los bancos a empresas y "
                            "familias.", [("bien", "El crédito crece"), ("mal", "Cae")],
                            "El dinero se muestra sin color: crecer no es bueno ni malo en sí."), unsafe_allow_html=True)
    k = st.columns(3)
    kpi(k[0], "Base monetaria", ultimo(bm) / 1e6 if bm is not None and ultimo(bm) else None, 1, pre="$", suf=" bill.",
        d=delta(bm) if bm is not None else None, color="off", help="Billones de pesos. Variación contra 30 días atrás.", serie=bm, fuente='BCRA')
    v, a_ = _ult_y_hace(m2)  # serie diaria hábil: 30 días corridos, no 30 datos (serían ~6 semanas)
    kpi(k[1], "M2 privado · var. interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", color="off", serie=m2, fuente='BCRA')
    kpi(k[2], "Préstamos al sector privado", ultimo(pr) / 1e6 if pr is not None and ultimo(pr) else None, 1, pre="$",
        suf=" bill.", d=delta(pr) if pr is not None else None,
        help="Billones de pesos (nominales). Variación contra 30 días atrás.", serie=pr, fuente='BCRA')
    a, b = st.columns(2)
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
