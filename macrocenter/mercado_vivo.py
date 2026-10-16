"""Panel público de mercado: el navegador recibe datos de Binance, sin credenciales."""
from pathlib import Path

import streamlit.components.v1 as components

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def mostrar_cripto() -> None:
    html = (ASSETS / "cripto_vivo.html").read_text(encoding="utf-8")
    js = (ASSETS / "cripto_vivo.js").read_text(encoding="utf-8")
    components.html(html.replace("/* MERCADO_SCRIPT */", js), height=650, scrolling=True)
