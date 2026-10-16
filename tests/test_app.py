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
    ("inversiones/tasas-de-hoy", "inv_seccion", "Tasas y plazos fijos"),  # enlaces viejos
    ("inversiones/plazo-fijo-vs-uva", "inv_seccion", "Tasas y plazos fijos"),  # enlaces viejos (se juntó con las tasas)
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


def test_botones_de_navegacion():
    """Cada botón que cambia de pantalla (menú, atajos, «Volver al tablero») anda sin romper la página."""
    at = _correr(ver="inversiones/tasas-y-plazos-fijos")
    at.button(key="volver_tablero").click().run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    assert at.session_state["vista"] == "tablero"
    at.button(key="atajo_tasas").click().run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    assert at.session_state["vista"] == "inversiones" and at.session_state["inv_seccion"] == "Tasas y plazos fijos"
    at.button(key="nav_historia").click().run()
    assert not at.exception, [str(e.value)[:200] for e in at.exception]
    assert at.session_state["vista"] == "historia"


def test_pestana_bonos():
    """Bonos argentinos (data912) y tasas de EE. UU. (FRED): se dibujan sin errores ni secciones caídas."""
    at = _correr(ver="tablero/bonos")
    assert at.session_state["pestana"] == "Bonos"
    assert list(dict.fromkeys(at.session_state["_fallas"])) == []
    textos = " ".join(m.value for m in at.markdown)
    assert "Ley Nueva York" in textos and "GD30" in textos


def test_precios_mayoristas_se_bajan_y_se_calculan():
    """IPIM e IPP (INDEC, API de datos.gob.ar): se descargan y de ellos salen las variaciones de la pestaña Inflación."""
    from macrocenter import data
    from macrocenter.pestanas.inflacion import _variaciones

    for nombre in ("ipim", "ipp"):
        d = data.serie(nombre)
        assert not d.empty and {"fecha", "valor"} <= set(d.columns)
        v = _variaciones(d)
        assert v["mensual"].notna().all() and v["interanual"].dropna().size > 0
