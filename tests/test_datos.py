"""Limpieza de series, complemento con el archivo oficial y copia de respaldo. Sin red: todo con datos inventados."""
import gzip
import json
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from macrocenter import data, semilla


def test_limpiar_ordena_saca_repetidos_e_infinitos():
    df = pd.DataFrame({"fecha": ["2024-03-01", "2024-01-01", "2024-01-01", "x", "2024-02-01"],
                       "valor": [3.0, 1.0, 1.5, 9.0, np.inf]})
    d = data.limpiar(df)
    assert list(d["fecha"].dt.strftime("%Y-%m")) == ["2024-01", "2024-03"]  # febrero quedó sin dato: se va
    assert d.loc[0, "valor"] == 1.5  # de dos fechas iguales queda la última
    assert data.limpiar("texto") == "texto"


def test_tareas_principales_tiene_todas_las_series():
    t = data.tareas_principales()
    assert {f"bcra:{k}" for k in data.BCRA_IDS} <= set(t)
    assert {f"serie:{k}" for k in data.SERIES_IDS} <= set(t)
    assert {"dolares", "riesgo_pais", "fx:EUR", "fx:GBP", "dolar_hist", "inflacion_hist"} <= set(t)


class _Resp:
    def __init__(self, texto):
        self.text = texto


def test_completar_con_archivo_suma_los_meses_que_faltan(monkeypatch):
    api = pd.Series([1.0, 2.0], index=pd.to_datetime(["2026-01-01", "2026-02-01"]))
    csv = "indice_tiempo,ripte,otra\n2026-01-01,1,9\n2026-02-01,2,9\n2026-03-01,3,9\n2026-04-01,4,9\n"
    monkeypatch.setattr(data, "_get", lambda url, _intentos=4, **p: _Resp(csv))
    meta = {"fin": "2026-04-01", "columna": "ripte", "url": data.ARCHIVOS_URL + "x.csv"}
    s = data._completar_con_archivo(api, meta)
    assert list(s.values) == [1.0, 2.0, 3.0, 4.0]


def test_completar_con_archivo_no_baja_nada_si_esta_al_dia_o_la_url_es_ajena(monkeypatch):
    def no_llamar(*a, **k):
        raise AssertionError("no debía bajar el archivo")

    monkeypatch.setattr(data, "_get", no_llamar)
    api = pd.Series([1.0], index=pd.to_datetime(["2026-04-01"]))
    assert data._completar_con_archivo(api, {"fin": "2026-04-01", "columna": "c", "url": data.ARCHIVOS_URL}) is api
    otra = pd.Series([1.0], index=pd.to_datetime(["2026-01-01"]))
    assert data._completar_con_archivo(otra, {"fin": "2026-04-01", "columna": "c", "url": "https://malo.com/x.csv"}) is otra


def _datos():
    f = pd.date_range("2024-01-01", periods=5, freq="MS")
    return {"serie:a": pd.DataFrame({"fecha": f, "valor": [1.0, 2.0, np.nan, 4.0, 5.0]}),
            "dolares": pd.DataFrame({"fecha": f, "blue": [1, 2, 3, 4, 5], "blue_compra": [1.0] * 5}),
            "bcra:x": "TimeoutError"}  # las fallas (texto) no se guardan


def test_semilla_ida_y_vuelta():
    crudo = semilla.a_bytes(_datos(), datetime(2026, 10, 14, 12, 0))
    series, cuando = semilla.de_bytes(crudo)
    assert set(series) == {"serie:a", "dolares"}
    assert cuando == datetime(2026, 10, 14, 12, 0)
    pd.testing.assert_series_equal(series["serie:a"]["valor"], _datos()["serie:a"]["valor"], check_names=False)
    assert series["dolares"]["blue"].tolist() == [1, 2, 3, 4, 5]
    assert set(semilla.de_bytes(crudo, {"dolares"})[0]) == {"dolares"}


@pytest.mark.parametrize("crudo", [
    b"no es gzip",
    gzip.compress(b"{no es json"),
    gzip.compress(json.dumps({"version": 99, "cuando": "2026-01-01", "series": {}}).encode()),
    gzip.compress(json.dumps({"version": 1, "cuando": "2026-01-01",
                              "series": {"x": {"columns": ["sin_fecha"], "data": [[1]]}}}).encode()),
    gzip.compress(b"[]"),
])
def test_semilla_rechaza_archivos_rotos(crudo):
    assert semilla.de_bytes(crudo) is None


def test_semilla_rechaza_archivos_enormes(monkeypatch):
    monkeypatch.setattr(semilla, "MAX_BYTES", 100)
    assert semilla.de_bytes(semilla.a_bytes(_datos(), datetime(2026, 1, 1))) is None


def test_bancos_ignora_fila_vacia_de_la_api(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(data, "_get", lambda *a, **k: SimpleNamespace(json=lambda: [
        {"entidad": "Banco A", "tnaClientes": .2}, [],
        {"entidad": "Banco B", "tnaNoClientes": .25},
    ]))
    tabla = data.plazo_fijo_bancos()
    assert tabla.entidad.tolist() == ["Banco A", "Banco B"]
    assert tabla.tna_clientes.tolist() == [20, 0]
    assert tabla.tna_no_clientes.tolist() == [0, 25]


def test_refresco_libera_el_bloqueo_original_si_se_recarga(monkeypatch):
    import threading
    from macrocenter import carga
    original, nuevo = threading.Lock(), threading.Lock()
    tareas = []
    class Hilo:
        def __init__(self, target, **kwargs):
            tareas.append(target)
        def start(self):
            pass
    monkeypatch.setattr(carga, "_refrescando", original)
    monkeypatch.setattr(carga.threading, "Thread", Hilo)
    monkeypatch.setattr(carga, "_descargar_todo", lambda: None)
    monkeypatch.setattr(carga, "_completar_con_disco", lambda x: x)
    monkeypatch.setattr(carga, "_guardar_disco", lambda x: None)
    carga._refrescar_en_segundo_plano()
    assert original.locked()
    monkeypatch.setattr(carga, "_refrescando", nuevo)
    tareas[0]()
    assert not original.locked() and not nuevo.locked()
