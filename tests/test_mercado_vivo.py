"""Contrato del panel y su flujo de reconexión sin usar la red."""
import shutil
import subprocess
from pathlib import Path

import pytest

from macrocenter import mercado_vivo


def test_panel_incluye_script_y_no_requiere_credenciales(monkeypatch):
    llamadas = []
    monkeypatch.setattr(mercado_vivo.components, "html", lambda html, **kw: llamadas.append((html, kw)))
    mercado_vivo.mostrar_cripto()
    html, opciones = llamadas[0]
    assert "/* MERCADO_SCRIPT */" not in html
    assert "wss://data-stream.binance.vision/ws/" in html
    assert "USDT" in html and "no es el historial del día" in html
    assert opciones["scrolling"]


def test_flujo_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("Requiere Node para probar JavaScript")
    archivo = Path(__file__).with_name("cripto_vivo.cjs")
    resultado = subprocess.run([node, str(archivo)], capture_output=True, text=True, timeout=15)
    assert resultado.returncode == 0, resultado.stderr
