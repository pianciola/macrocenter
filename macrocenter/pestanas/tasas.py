"""Pestaña «Tasas y riesgo país» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style


def mostrar(
    *, _ult_y_hace, dif, get, grafico, grafico_periodo, kpi, panel_plazo_fijo, pases, rec, riesgo, tpm,
) -> None:
    st.markdown(style.intro("Cuánto cuesta el dinero en pesos (**tasas de interés**) y cuánto le cuesta a la Argentina endeudarse "
                            "(**riesgo país**).", [("bien", "El riesgo país baja"), ("mal", "Sube")]), unsafe_allow_html=True)
    k = st.columns(4)
    v, a_ = _ult_y_hace(riesgo)
    kpi(k[0], "Riesgo país", v, 0, suf=" pb", d=dif(v, a_), d_suf=" pb", d_dec=0, color="inverse",
        help="Puntos básicos sobre los bonos de EE. UU. (100 pb = 1 punto porcentual). Variación contra 30 días atrás.")
    for slot, (clave_t, nombre_t, ayuda_t) in zip(k[1:], (
            ("bcra:badlar", "Tasa BADLAR", "Plazos fijos de más de $1 millón en bancos privados (TNA)."),
            ("bcra:depositos_30d", "Plazo fijo a 30 días", "Tasa promedio de plazos fijos a 30 días (TNA)."),
            ("bcra:prestamos_personales", "Préstamos personales", "Tasa promedio de préstamos personales (TNA)."))):
        v, a_ = _ult_y_hace(get(clave_t))
        kpi(slot, nombre_t, v, 1, suf="%", d=dif(v, a_), d_suf=" pp", color="off",
            help=ayuda_t + " Variación contra 30 días atrás.")
    st.subheader("Tasas de interés")
    if pases is not None or tpm is not None:
        ref = None
        for df_, nombre in ((tpm, "Tasa de política monetaria"), (pases, "Pases a 1 día")):
            if df_ is not None:
                df_ = df_.rename(columns={"valor": nombre})
                ref = df_ if ref is None else ref.merge(df_, on="fecha", how="outer")
        ref = ref.sort_values("fecha")
        grafico(charts.lineas(rec(ref, 3), {c_: c_ for c_ in ref.columns if c_ != "fecha"},
                              "Tasa de política monetaria y tasa de pases a 1 día (TNA, %)", yfmt=",.0f", paso=True))
        st.caption("La API del BCRA no registra datos de tasa de política monetaria después del 10/07/2025 "
                   "(último valor: 29% TNA). Como referencia vigente se muestra la tasa de pases a 1 día.")
    a, b = st.columns(2)
    with a:
        tasas = {}
        base = None
        for clave, nombre in [("bcra:badlar", "BADLAR"), ("bcra:tamar", "TAMAR"), ("bcra:depositos_30d", "Plazo fijo 30 d")]:
            d = get(clave)
            if d is not None:
                d = d.rename(columns={"valor": nombre})
                base = d if base is None else base.merge(d, on="fecha", how="outer")
                tasas[nombre] = nombre
        if base is not None:
            grafico(charts.lineas(rec(base.sort_values("fecha")), tasas, "Tasas de interés en pesos (TNA, %)", yfmt=",.0f"))
    with b:
        pp = get("bcra:prestamos_personales")
        if pp is not None:
            grafico(charts.lineas(rec(pp), {"Préstamos personales": "valor"}, "Tasa de préstamos personales (TNA, %)", yfmt=",.0f"))
    if riesgo is not None:
        st.subheader("Riesgo país")
        grafico_periodo("tasas_riesgo", riesgo, lambda d: charts.lineas(d, {"Riesgo país": "valor"},
                                                                          "Riesgo país — EMBI (puntos básicos)", height=380))
    st.divider()
    panel_plazo_fijo()
