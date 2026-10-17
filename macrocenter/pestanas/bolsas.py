"""Bolsas.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import datos_vista, charts, data, style


def mostrar(*, _var_pct, cargar_mercados, falla, grafico, rec, selector_categoria, selector_periodo) -> None:
    mk = cargar_mercados()
    st.markdown(style.intro("Las principales bolsas del mundo y algunas materias primas que mueven a la Argentina.",
                            [("bien", "Sube"), ("mal", "Baja")],
                            "Yahoo Finance (fuente no oficial, con demora). Se actualiza cada 5 minutos.", resumen='Bolsas y materias primas relevantes para la Argentina.'), unsafe_allow_html=True)
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

    st.subheader("Comparar")
    nombres = {n: s for s, n, g, _ in data.INDICES if g != "Materias primas" and isinstance(mk.get(s), pd.DataFrame)}
    elegidas = selector_categoria("Bolsas a comparar", list(nombres), "bolsas", multi=True,
                                  defecto=[n for n in ("Merval", "S&P 500") if n in nombres]) or []
    per_b = selector_periodo("bolsas", "1 año")
    series = {}
    for n in elegidas:
        d = rec(mk[nombres[n]], 0, per_b)
        if len(d) >= 2 and d.iloc[0]["valor"]:
            series[n] = d.set_index("fecha")["valor"] / float(d.iloc[0]["valor"]) * 100
    if series:
        ancho = pd.concat(series, axis=1, sort=True).reset_index().rename(columns={"index": "fecha"})
        grafico(charts.lineas(ancho, {n: n for n in series}, "Evolución de las bolsas — base 100 = inicio del período",
                              yfmt=",.0f", height=380))
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "Cada índice está en su moneda: el Merval está en pesos, así que también refleja la inflación y "
                            "el tipo de cambio.")), unsafe_allow_html=True)
    else:
        st.info("Elegí al menos una bolsa para ver el gráfico.")
