"""Pestaña «Reservas» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style


def mostrar(*, HOY, bloque_cambiario, delta, grafico, kpi, rec, reservas, selector_periodo, ultimo) -> None:
    st.markdown(style.intro("Los dólares y el oro que tiene el **Banco Central** para pagar deuda e intervenir en el mercado cambiario.",
                            [("bien", "Suben"), ("mal", "Bajan")]), unsafe_allow_html=True)
    if reservas is not None:
        @st.fragment
        def bloque_reservas() -> None:
            """Período + indicadores + gráfico: al cambiar el período se redibuja solo esto."""
            per_res = selector_periodo("reservas")
            r = rec(reservas, 0, per_res)
            c = st.columns(3)
            f_res = reservas[reservas["fecha"] <= HOY].dropna(subset=["valor"])
            d_res = delta(reservas, dias=1, modo="abs")
            # la unidad va en el título (como en el Resumen): la cifra sola entra en cualquier tarjeta
            kpi(c[0], f"Reservas al {f_res['fecha'].iloc[-1]:%d/%m/%Y} (USD M)" if not f_res.empty else "Reservas (USD M)",
                ultimo(reservas), 0, d=d_res, d_suf=" M", d_txt="vs día anterior", color="normal",
                help="Serie oficial del BCRA, que se publica con 1 o 2 días de demora. La cifra que el BCRA difunde en sus "
                     "redes el mismo día es provisoria y puede diferir.", serie=f_res, fuente='BCRA')
            if len(r) > 1:
                ini_r, fin_r = float(r["valor"].iloc[0]), float(r["valor"].iloc[-1])
                kpi(c[1], ("Variación en todo el período" if per_res == "Todo" else f"Variación en {per_res.lower()}") + " (USD M)",
                    fin_r - ini_r, 0,
                    d=None if ini_r == 0 else (fin_r / ini_r - 1) * 100, d_txt="", color="normal",
                    help="Verde si las reservas subieron en el período, rojo si bajaron.", serie=r, fuente='BCRA · cálculo propio')
                maximo = float(r["valor"].max())
                kpi(c[2], "Máximo del período (USD M)", maximo, 0,
                    d=None if maximo == 0 else (fin_r / maximo - 1) * 100, d_txt="hoy vs el máximo", color="normal", serie=r, fuente='BCRA · cálculo propio')
            grafico(charts.lineas(r, {"Reservas brutas": "valor"}, "Reservas internacionales brutas del BCRA (USD millones)",
                                  height=460))

        bloque_reservas()
        st.markdown(style.aclaracion(
            ("Qué mide", "Son las reservas **brutas**: incluyen el swap con China, los encajes de los depósitos en dólares y "
                         "los repos con bancos, que no son de libre disponibilidad."),
            ("Nota", "Las **netas** (lo que el BCRA puede usar para intervenir) son bastante menores, pero no se muestran porque "
                    "no existe una serie oficial pública con la que calcularlas.")), unsafe_allow_html=True)
        with st.expander("Variación mensual"):
            rm = reservas.set_index("fecha")["valor"].resample("ME").last().diff().rename("var").reset_index()
            grafico(charts.barras(rec(rm.dropna(), 2), "var", "Variación mensual de reservas (USD millones)", yfmt=",.0f", color_signo=True))
    bloque_cambiario()
