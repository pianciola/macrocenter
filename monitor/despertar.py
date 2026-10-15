"""Mantiene despierta la página publicada: la abre con un navegador real (Streamlit Community Cloud duerme las apps sin
visitas y el primer visitante del día veía «This app has gone to sleep»). Si la encuentra dormida, toca el botón para
despertarla y espera a que cargue. Lo corre GitHub Actions cada pocas horas (ver .github/workflows/despertar.yml).

No guarda ni manda datos de nadie: solo abre la página pública, como cualquier visita.
Se puede correr a mano: python monitor/despertar.py
"""
from __future__ import annotations

import sys

from playwright.sync_api import TimeoutError as Demora, sync_playwright

URL = "https://macrocenter-argentina.streamlit.app/"


def main() -> int:
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page()
        pag.goto(URL, wait_until="domcontentloaded", timeout=90_000)
        try:  # dormida: Streamlit muestra un botón para despertarla
            pag.get_by_role("button", name="Yes, get this app back up!").click(timeout=8_000)
            print("La app estaba dormida: se la despertó.")
        except Demora:
            print("La app estaba despierta.")
        # la app vive en un iframe: se espera a que dibuje su contenido (la marca de la barra lateral)
        try:
            pag.frame_locator("iframe[src*=\"/~/+/\"]").locator(".mc-brand").first.wait_for(timeout=240_000)
            print("La página cargó bien.")
            return 0
        except Demora:
            print("La página no terminó de cargar a tiempo.")
            return 1
        finally:
            nav.close()


if __name__ == "__main__":
    sys.exit(main())
