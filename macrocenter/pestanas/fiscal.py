"""Pestaña «Resultado fiscal» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import charts, style


def mostrar(*, actualizando, dif, falla, fiscal_anual, fiscal_df, grafico, graficos_fiscales, kpi) -> None:
    f = fiscal_df()
    if f.empty:
        falla("no se pudieron cargar los datos fiscales o el PBI")
        actualizando()
    else:
        ult_f = f.iloc[-1]
        st.markdown(style.intro(
            "Las cuentas del **sector público nacional**: cuánto le sobra o le falta, como porcentaje del PBI (base caja). "
            "Positivo = superávit; negativo = déficit.", [("bien", "Mejora"), ("mal", "Empeora")],
            f"Último dato: {ult_f['fecha']:%m/%Y}.", resumen='Resultado primario y financiero del sector público nacional.'), unsafe_allow_html=True)
        k = st.columns(4)
        for slot, (nombre, col, ayuda) in zip(k, [
                ("Primario 12 meses", "primario_12m", "Suma de los últimos 12 meses sobre el PBI de ese período."),
                ("Financiero 12 meses", "financiero_12m", "Suma de los últimos 12 meses sobre el PBI de ese período."),
                ("Primario del mes", "primario", "El resultado del mes sobre 1/12 del PBI. Cambia mucho de mes a mes (aguinaldo, vencimientos)."),
                ("Financiero del mes", "financiero", "El resultado del mes sobre 1/12 del PBI. Cambia mucho de mes a mes (aguinaldo, vencimientos).")]):
            if col not in f:  # esa serie no se pudo cargar
                kpi(slot, nombre, None)
                continue
            # cada serie con su último dato propio: el financiero a veces llega un mes después que el primario
            # (antes quedaba «s/d» aunque hubiera datos del mes anterior)
            con_dato = f.dropna(subset=[col])
            if con_dato.empty:
                kpi(slot, nombre, None)
                continue
            fila = con_dato.iloc[-1]
            v = float(fila[col])
            if fila["fecha"] != ult_f["fecha"]:
                nombre = f"{nombre} ({fila['fecha']:%m/%Y})"
            hace_un_anio = f[f["fecha"] <= fila["fecha"] - pd.DateOffset(months=12)][col].dropna()
            antes = float(hace_un_anio.iloc[-1]) if not hace_un_anio.empty else None
            kpi(slot, nombre, v, 1, suf="% del PBI", d=dif(v, antes), d_suf=" pp", d_txt="vs un año antes",
                help=ayuda + " Verde: el resultado mejoró contra un año antes; rojo: empeoró.", serie=con_dato, fuente='Ministerio de Economía / INDEC · cálculo propio')
        st.markdown(style.aclaracion(
            ("Qué mide", "**Primario**: ingresos menos gastos, sin contar intereses de la deuda. **Financiero**: lo que "
                         "queda después de pagar intereses.")), unsafe_allow_html=True)
        graficos_fiscales(f)
        fa = fiscal_anual()
        if not fa.empty:
            st.markdown("#### Resultado anual")
            a, b = st.columns(2)
            for col_, c, titulo in ((a, "primario", "Resultado primario anual (% del PBI)"),
                                    (b, "financiero", "Resultado financiero anual (% del PBI)")):
                if c in fa and fa[c].notna().any():
                    with col_:
                        fig_a = charts.barras(fa.dropna(subset=[c]), c, titulo, yfmt=",.1f", height=320, x="etiqueta", color_signo=True)
                        fig_a.update_traces(text=[charts.num(v, 1, "%") for v in fa.dropna(subset=[c])[c]],
                                            textposition="outside", cliponaxis=False)
                        fig_a.update_xaxes(type="category")
                        grafico(fig_a)
            if (fa["meses"] < 12).any():
                st.markdown(style.aclaracion(
                    ("Nota", "El año en curso es el acumulado de los meses publicados sobre el PBI estimado del año completo, así "
                            "que todavía puede cambiar (diciembre suele ser deficitario por el aguinaldo).")), unsafe_allow_html=True)
        with st.expander("Cómo se calcula el porcentaje del PBI"):
            st.markdown(
                "- **Resultado:** informe mensual de ingresos y gastos del Ministerio de Economía (base caja).\n"
                "- **PBI:** a precios corrientes, trimestral anualizado del INDEC. Para cada mes se usa el promedio de los últimos "
                "4 trimestres; pasado el último trimestre publicado, se lo actualiza con la inflación mensual (no incluye "
                "crecimiento real, por eso las últimas cifras son una estimación).\n"
                "- **Mensual:** resultado del mes sobre 1/12 del PBI. Es muy variable; mirá el acumulado de 12 meses para la tendencia.\n"
                "- Puede diferir de las cifras que publica el Gobierno, que usan su propio PBI y criterios de ajuste (por ejemplo, "
                "ingresos extraordinarios).")
        st.markdown(style.aclaracion(
            ("Fuente", "Ministerio de Economía (IMIG, Informe Mensual de Ingresos y Gastos) e INDEC, vía datos.gob.ar.")), unsafe_allow_html=True)
