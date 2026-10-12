"""Fallas de datos: no se muestran en pantalla (quien visita la página no tiene nada que hacer con un «no se pudo
cargar»). Quedan en la consola del servidor y en `st.session_state["_fallas"]`, que lee el monitor (monitor/revisar.py)
para avisarle al dueño por mail."""
from __future__ import annotations

import streamlit as st


def falla(texto: str) -> None:
    st.session_state.setdefault("_fallas", []).append(texto)
    print(f"[MacroCenter] falla: {texto}", flush=True)


def actualizando() -> None:
    """Lo único que se ve cuando una sección entera se queda sin sus datos: un mensaje neutro, sin hablar de errores.
    La carga se reintenta sola (ver reintentar_si_fallo en app.py)."""
    st.caption("Esta sección se está actualizando. Volvé a mirarla en un minuto.")
