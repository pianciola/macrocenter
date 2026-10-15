"""Selectores de una sola opción (st.segmented_control / st.pills) que nunca quedan vacíos.

Streamlit deja «desmarcar» la opción elegida tocándola de nuevo: el contenido seguía mostrando la sección por defecto,
pero ningún botón quedaba resaltado. Acá, si eso pasa, se vuelve a marcar la que estaba."""
from __future__ import annotations

from typing import Any, Callable

import streamlit as st


def uno(widget: Callable, etiqueta: str, opciones: list, clave: str, defecto: Any = None, **kw) -> Any:
    """Dibuja `widget` (por ejemplo `st.segmented_control` o `columna.pills`) y devuelve la opción elegida.
    `defecto`: la que vale si todavía no se eligió ninguna (por defecto, la primera)."""
    opciones = list(opciones)
    defecto = defecto if defecto in opciones else opciones[0]
    ult = f"_ult_{clave}"
    if st.session_state.get(clave) not in opciones:  # primera vez, o un valor viejo que ya no existe
        st.session_state[clave] = defecto
    st.session_state[ult] = st.session_state[clave]

    def volver() -> None:
        if st.session_state.get(clave) not in opciones:
            st.session_state[clave] = st.session_state[ult]

    elegido = widget(etiqueta, opciones, key=clave, on_change=volver, **kw)
    return elegido if elegido in opciones else st.session_state[ult]
