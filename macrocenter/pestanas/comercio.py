"""Pestaña «Comercio exterior» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style


def mostrar(*, comercio, dif, grafico, kpi, pct, rec, ult_y_ant) -> None:
    st.markdown(style.intro("Lo que la Argentina le vende al mundo (**exportaciones**) y le compra (**importaciones**), en dólares. "
                            "El saldo positivo trae dólares al país.", [("bien", "El saldo mejora"), ("mal", "Empeora")]), unsafe_allow_html=True)
    if comercio is not None:
        c = comercio
        k = st.columns(4)
        v, a_ = ult_y_ant(c, "exp", atras=12)
        kpi(k[0], "Exportaciones del mes (USD M)", v, 0, d=pct(v, a_), d_txt="vs un año antes")
        v, a_ = ult_y_ant(c, "imp", atras=12)
        kpi(k[1], "Importaciones del mes (USD M)", v, 0, d=pct(v, a_), d_txt="vs un año antes", color="off")
        v, a_ = ult_y_ant(c, "saldo", atras=12)
        kpi(k[2], "Saldo del mes (USD M)", v, 0, d=dif(v, a_), d_suf=" M", d_txt="vs un año antes", d_dec=0)
        v, a_ = ult_y_ant(c.dropna(subset=["saldo_12m"]), "saldo_12m", atras=12)
        kpi(k[3], "Saldo 12 meses (USD M)", v, 0, d=dif(v, a_), d_suf=" M", d_txt="vs un año antes", d_dec=0)
        ult_c = c.dropna(subset=["exp"])["fecha"].max()
        st.caption(f"Último dato: {ult_c:%m/%Y} (INDEC, intercambio comercial argentino).")
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(c, 3), {"Exportaciones": "exp", "Importaciones": "imp"},
                                  "Exportaciones e importaciones (USD millones)"))
        with b:
            grafico(charts.barras(rec(c, 3), "saldo", "Saldo comercial mensual (USD millones)", yfmt=",.0f"))
        grafico(charts.lineas(rec(c.dropna(subset=["saldo_12m"]), 3), {"Saldo acumulado 12 m": "saldo_12m"},
                              "Saldo comercial acumulado 12 meses (USD millones)", yfmt=",.0f", height=320))
