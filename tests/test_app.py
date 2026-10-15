"""La app entera, con datos reales (necesita internet; tarda un par de minutos). Se corre con MACROCENTER_RED=1:
    MACROCENTER_RED=1 python -m pytest tests/test_app.py
En GitHub corre en cada publicación (ver .github/workflows/pruebas.yml)."""
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("MACROCENTER_RED") != "1", reason="necesita internet (MACROCENTER_RED=1)")

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _correr(**query):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in query.items():
        at.query_params[k] = v
    at.run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    return at


def test_inicio_sin_errores_ni_secciones_caidas():
    at = _correr()
    assert list(dict.fromkeys(at.session_state["_fallas"])) == []


@pytest.mark.parametrize("ruta,clave,valor", [
    ("tablero/dolar", "pestana", "Dólar"),
    ("tablero/inicio", "pestana", "Resumen"),  # enlaces viejos
    ("tablero/inflacion", "pestana", "Inflación"),
    ("herramientas/ajuste-de-alquileres", "inter_modo", "Ajuste de alquileres"),
    ("inversiones/glosario", "inv_seccion", "Glosario"),
    ("inversiones/conceptos", "inv_seccion", "Glosario"),  # enlaces viejos
    ("inversiones/como-les-fue", "inv_seccion", "Rendimientos pasados"),  # enlaces viejos
    ("historia/ministros-de-economia", "hist_seccion", "Ministros de Economía"),
    ("historia/viaje-en-el-tiempo", "hist_seccion", "Viaje en el tiempo"),
    ("herramientas/viaje-en-el-tiempo", "hist_seccion", "Viaje en el tiempo"),  # enlaces viejos (estaba en Herramientas)
])
def test_los_enlaces_abren_la_seccion(ruta, clave, valor):
    at = _correr(ver=ruta)
    assert at.session_state[clave] == valor


@pytest.mark.parametrize("ruta", ["cualquier-cosa", "tablero/no-existe", "<script>", "x" * 500])
def test_un_enlace_roto_cae_en_el_tablero(ruta):
    at = _correr(ver=ruta)
    assert at.session_state["vista"] == "tablero"


@pytest.mark.parametrize("i", range(9))
def test_cada_analisis_destacado_se_dibuja(i):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(APP, default_timeout=300)
    at.session_state["inicio_analisis"] = i
    at.run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    assert list(dict.fromkeys(at.session_state["_fallas"])) == []
