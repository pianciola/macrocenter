"""Pestaña «Inflación» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import charts, style


def mostrar(
    *, delta, dif, get, grafico, infl_ia, infl_m, inflacion_distritos,
    kpi, rec, rem, ult_y_ant, ultimo, uva,
) -> None:
    st.markdown(style.intro("La inflación (**IPC** del INDEC), lo que espera el mercado para los próximos 12 meses (**REM** del BCRA) y la "
                            "**UVA**, la unidad que ajusta créditos y plazos fijos por inflación.",
                            [("bien", "La inflación baja"), ("mal", "Sube")],
                            "pp significa puntos porcentuales: pasar de 3% a 2% es bajar 1 pp. La fecha corresponde al período medido.", resumen='Inflación observada, expectativas y unidades ajustadas por precios.', inicio=True), unsafe_allow_html=True)
    k = st.columns(4)
    v, a_ = ult_y_ant(infl_m)
    kpi(k[0], "Inflación mensual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse", serie=infl_m, fuente='INDEC · vía BCRA')
    v, a_ = ult_y_ant(infl_ia)
    kpi(k[1], "Inflación interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse", serie=infl_ia, fuente='INDEC · vía BCRA')
    v, a_ = ult_y_ant(rem)
    kpi(k[2], "Esperada 12 meses (REM)", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse",
        help="Mediana de lo que esperan los analistas del Relevamiento de Expectativas de Mercado.", serie=rem, fuente='BCRA · REM')
    kpi(k[3], "UVA", ultimo(uva) if uva is not None else None, 2, pre="$",
        d=delta(uva) if uva is not None else None, color="off", help="Sube con la inflación (CER), con unas semanas de rezago.", serie=uva, fuente='BCRA')
    if infl_m is not None and infl_ia is not None:
        st.markdown("#### Inflación")
        m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
        grafico(charts.barras_y_linea(rec(m, 2), "valor_m", "valor_ia", "Inflación (IPC INDEC, %)",
                                      "Mensual", "Interanual"))
    inflacion_distritos()
    st.markdown("#### Índices de ajuste: UVA, CER, UVI e ICL")
    pares = [("bcra:uva", "UVA (pesos)", ",.0f"), ("bcra:cer", "CER (base 2/2/2002 = 1)", ",.0f"),
             ("bcra:uvi", "UVI (pesos)", ",.0f"), ("bcra:icl", "ICL — Índice para Contratos de Locación", ",.1f")]
    for fila in (pares[:2], pares[2:]):
        cols = st.columns(2)
        for col, (clave, titulo, fmt) in zip(cols, fila):
            d = get(clave)
            if d is not None:
                with col:
                    grafico(charts.lineas(rec(d), {titulo: "valor"}, titulo, yfmt=fmt, height=320))
