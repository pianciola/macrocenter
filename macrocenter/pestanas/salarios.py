"""Pestaña «Salarios» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style


def mostrar(
    *, bloque_pobreza, dif, grafico, haber_min, kpi, pct, rec, ripte, sal, sal_ia, sal_priv, sal_pub, salario_real,
    smvm, ult_y_ant,
) -> None:
    st.markdown(style.intro("Cuánto suben los sueldos y si le ganan a la inflación (**salario real**).",
                            [("bien", "El poder de compra mejora"), ("mal", "Empeora")], resumen='Evolución de los salarios y de su poder de compra.'), unsafe_allow_html=True)
    sr_k = salario_real()
    k = st.columns(4)
    v, a_ = ult_y_ant(sal_ia)
    kpi(k[0], "Salarios · var. interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", serie=sal_ia, fuente='INDEC')
    v, a_ = ult_y_ant(sr_k, "real")
    kpi(k[1], "Salario real · interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.",
        help="Positivo: los salarios subieron más que los precios en el último año.", serie=sr_k, fuente='INDEC · cálculo propio')
    v, a_ = ult_y_ant(smvm)
    kpi(k[2], "Salario mínimo", v, 0, pre="$", d=pct(v, a_), d_txt="vs mes ant.", serie=smvm, fuente='Secretaría de Trabajo · datos.gob.ar')
    v, a_ = ult_y_ant(haber_min)
    kpi(k[3], "Haber mínimo jubilatorio", v, 0, pre="$", d=pct(v, a_), d_txt="vs mes ant.", serie=haber_min, fuente='ANSES · datos.gob.ar')
    if sal is not None:
        st.markdown("#### Salarios e inflación")
        base = sal.rename(columns={"valor": "Total"})
        for df_, nombre in ((sal_priv, "Privado registrado"), (sal_pub, "Público")):
            if df_ is not None:
                base = base.merge(df_.rename(columns={"valor": nombre}), on="fecha", how="outer")
        base = base.sort_values("fecha")
        cols = {n: n for n in ("Total", "Privado registrado", "Público") if n in base}
        a, b = st.columns(2)
        with a:
            grafico(charts.lineas(rec(base, 3), cols, "Índice de salarios INDEC (oct-2016 = 100)"))
        sr = salario_real()
        with b:
            if sr is not None:
                grafico(charts.lineas(rec(sr, 3), {"Salarios (nominal)": "salario", "Inflación": "inflacion"},
                                      "Salarios vs inflación — variación interanual (%)", yfmt=",.0f"))
        with st.expander("Salario real, RIPTE, salario mínimo y haber mínimo"):
            a, b = st.columns(2)
            with a:
                if sr is not None:
                    grafico(charts.barras(rec(sr, 3), "real", "Salario real — variación interanual (%)", color_signo=True))
            with b:
                if ripte is not None:
                    grafico(charts.lineas(rec(ripte, 3), {"RIPTE": "valor"}, "RIPTE — remuneración imponible promedio ($)"))
            if smvm is not None or haber_min is not None:
                piso = None
                for df_, nombre in ((smvm, "Salario mínimo, vital y móvil"), (haber_min, "Haber mínimo jubilatorio")):
                    if df_ is not None:
                        df_ = df_.rename(columns={"valor": nombre})
                        piso = df_ if piso is None else piso.merge(df_, on="fecha", how="outer")
                piso = piso.sort_values("fecha")
                grafico(charts.lineas(rec(piso, 3), {c_: c_ for c_ in piso.columns if c_ != "fecha"},
                                      "Salario mínimo y haber mínimo jubilatorio ($ mensuales)", height=340))
    st.markdown(style.aclaracion(
        ("Cómo se calcula", "El salario real es (1 + salario nominal) / (1 + inflación) − 1, interanual."),
        ("Fuente", "Índice de salarios y RIPTE: INDEC / Secretaría de Seguridad Social, con unos dos meses de rezago.")), unsafe_allow_html=True)
    bloque_pobreza()
