"""Regresiones de la auditoría del 15/10/2026, sin red."""
import csv
import io
from datetime import datetime

import pandas as pd
import pytest

from macrocenter import carga, charts


@pytest.mark.parametrize("texto", ["=1+1", "+1+1", "-1+1", "@SUM(A1)", "  =1+1", "\ttexto", "\rtexto", "\ntexto"])
def test_csv_neutraliza_encabezados_y_categorias_sin_alterar_numeros(texto):
    contenido = charts.csv_de([(texto, [texto, "Normal"], [-25.5, 10.])]).decode("utf-8-sig")
    filas = list(csv.reader(io.StringIO(contenido, newline=""), delimiter=";"))
    assert filas[0] == ["categoría", "'" + texto]
    assert filas[1] == ["'" + texto, "-25,5"]
    assert filas[2] == ["Normal", "10,0"]


@pytest.fixture
def cache_local(tmp_path, monkeypatch):
    archivo = tmp_path / "cache.json.gz"
    monkeypatch.setattr(carga, "CACHE_DISCO", archivo)
    monkeypatch.setattr(carga, "_tareas", lambda: {"serie": None})
    return archivo


def test_cache_json_ida_vuelta_y_envejecimiento(cache_local):
    datos = {"serie": pd.DataFrame({"fecha": pd.to_datetime(["2026-10-01", "2026-10-02"]),
                                   "valor": [1.25, 2.75]})}
    cuando = datetime(2026, 10, 15, 12)
    carga._guardar_disco((datos, cuando))
    (leidos, fecha), edad = carga._leer_disco()
    pd.testing.assert_frame_equal(leidos["serie"], datos["serie"], check_dtype=False)
    assert fecha == cuando and edad < carga.DISCO_FRESCO
    carga.envejecer_disco()
    assert carga._leer_disco()[1] >= carga.DISCO_VIEJO_MAX
    anterior = cache_local.read_bytes()
    carga._guardar_disco(({"serie": "TimeoutError"}, cuando))
    assert cache_local.read_bytes() == anterior


def test_cache_rechaza_datos_rotos_y_no_lee_pickle(cache_local, monkeypatch):
    import pickle
    llamadas = []

    def prohibido(*args, **kwargs):
        llamadas.append(True)
        raise AssertionError("No se debe deserializar pickle")

    monkeypatch.setattr(pickle, "load", prohibido)
    monkeypatch.setattr(pickle, "loads", prohibido)
    for contenido in (b"roto", b"\x80\x04N."):
        cache_local.write_bytes(contenido)
        assert carga._leer_disco() is None
    assert llamadas == []


def test_cache_incompleta_o_demasiado_grande_se_ignora(cache_local, monkeypatch):
    from macrocenter import semilla

    df = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-01"]), "valor": [1.]})
    cache_local.write_bytes(semilla.a_bytes({"otra": df}, datetime(2026, 10, 15)))
    assert carga._leer_disco() is None
    monkeypatch.setattr(semilla, "MAX_BYTES", 10)
    assert carga._leer_disco() is None
