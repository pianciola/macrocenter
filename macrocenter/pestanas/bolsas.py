"""Bolsas.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import datos_vista, charts, data, style


def mostrar(*, _var_pct, cargar_mercados, falla) -> None:
    mk = cargar_mercados()
    st.markdown(style.intro("Las principales bolsas del mundo y algunas materias primas que mueven a la Argentina.",
                            [("bien", "Sube"), ("mal", "Baja")],
                            "Yahoo Finance (fuente no oficial, con demora). Se actualiza cada 5 minutos.", resumen='Bolsas y materias primas relevantes para la Argentina.', inicio=True), unsafe_allow_html=True)
    tarjetas = []
    for simbolo, nombre, grupo, unidad in data.INDICES:
        df = mk.get(simbolo)
        if not isinstance(df, pd.DataFrame) or len(df) < 2:
            continue
        ult = float(df.iloc[-1]["valor"])
        tarjetas.append(dict(
            meta=datos_vista.detalle(df.dropna(subset=["valor"]), "Yahoo Finance · con demora", nombre=nombre,
                                    frecuencia="Diaria; consulta cada 5 minutos", unidad=unidad,
                                    definicion=f"Cotización histórica de {nombre}. La disponibilidad depende de las sesiones del mercado."),
            nombre=nombre, desc=grupo, valor=charts.num(ult, 0 if ult >= 1000 else 2), detalle=unidad,
            var=_var_pct(df), var_txt="1 d", extras=[("30 d", _var_pct(df, 30))],
            sentido="alto", spark=list(df.tail(30)["valor"])))  # cotización: verde si sube, rojo si baja
    if not tarjetas:
        falla("no se pudieron cargar las cotizaciones de las bolsas")
        return
    st.markdown(style.cotizaciones(tarjetas), unsafe_allow_html=True)
    faltan = [n for s, n, _, _ in data.INDICES if not isinstance(mk.get(s), pd.DataFrame)]
    if faltan:
        st.caption("Sin datos por ahora: " + ", ".join(faltan) + ".")
