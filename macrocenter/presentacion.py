"""Navegación y trazabilidad compartidas del observatorio."""
from pathlib import Path

import pandas as pd
import streamlit as st

ECONOMIA = ["Inflación y dinero", "Actividad y PBI", "Reservas", "Salarios", "Resultado fiscal", "Comercio exterior"]
MERCADOS = ["Dólar", "Bolsas", "Cripto", "Bonos", "Tasas y riesgo país"]


def navegar(vista, clave, valor):
    st.session_state["vista"] = vista
    st.session_state[clave] = valor


def menu():
    vista = st.session_state.get("vista", "tablero")
    pagina = st.session_state.get("pestana", "Resumen")
    def enlace(texto, clave, destino, valor, estado="pestana"):
        activo = vista == destino and st.session_state.get(estado, "Resumen") == valor
        st.button(texto, key=clave, width="stretch", type="primary" if activo else "secondary",
                  on_click=navegar, args=(destino, estado, valor))
    enlace("Resumen", "nav_tablero", "tablero", "Resumen")
    with st.expander("Economía", expanded=vista == "historia" or (vista == "tablero" and pagina in ECONOMIA)):
        for p in ECONOMIA:
            enlace(p, "menu_" + p, "tablero", p)
        enlace("Historia económica", "nav_historia", "historia", "Presidentes", "hist_seccion")
    with st.expander("Mercados y ahorro", expanded=vista == "inversiones" or (vista == "tablero" and pagina in MERCADOS)):
        for p in MERCADOS:
            enlace(p, "menu_" + p, "tablero", p)
        enlace("Tasas y plazos fijos", "nav_inversiones", "inversiones", "Tasas y plazos fijos", "inv_seccion")
        enlace("Rendimientos pasados", "menu_rendimientos", "inversiones", "Rendimientos pasados", "inv_seccion")
    with st.expander("Herramientas", expanded=vista == "juegos" or (vista == "inversiones" and st.session_state.get("inv_seccion") == "Glosario")):
        for i, p in enumerate(["Ajuste de alquileres", "¿Cuánto valían tus pesos?", "Comparador de épocas"]):
            enlace(p, "menu_herramienta_" + str(i), "juegos", p, "inter_modo")
        enlace("Glosario económico", "menu_glosario", "inversiones", "Glosario", "inv_seccion")


def fecha_dato(df):
    if not isinstance(df, pd.DataFrame) or df.empty or "fecha" not in df:
        return None
    fechas = pd.to_datetime(df["fecha"], errors="coerce").dropna()
    fechas = fechas[fechas <= pd.Timestamp.now(tz="America/Argentina/Buenos_Aires").tz_localize(None)]
    return None if fechas.empty else fechas.max().strftime("%d/%m/%Y")


def etiqueta_dato(df, fuente):
    fecha = fecha_dato(df)
    if fecha is None:
        return f"{fuente} · Sin dato disponible"
    respaldo = df.attrs.get("estado_fuente") == "respaldo"
    return f"{fuente} · Dato: {fecha}" + (" · Último dato conservado; actualización pendiente" if respaldo else "")


def aplicar():
    css = (Path(__file__).parent.parent / "assets" / "observatorio.css").read_text(encoding="utf-8")
    st.html("<style>" + css + "</style>")
