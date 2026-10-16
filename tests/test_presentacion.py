import pandas as pd
from macrocenter import presentacion, carga


def test_fecha_y_estado_de_respaldo_no_se_confunden_con_actualizacion():
    df = pd.DataFrame({"fecha": pd.to_datetime(["2020-01-01", "2099-01-01"]), "valor": [1., 2.]})
    assert presentacion.fecha_dato(df) == "01/01/2020"
    respaldo = carga._como_respaldo(df)
    assert "actualización pendiente" in presentacion.etiqueta_dato(respaldo, "INDEC")
    assert "estado_fuente" not in df.attrs
    assert "INDEC" in presentacion.etiqueta_dato(df, "INDEC")
    assert presentacion.fecha_dato(pd.DataFrame()) is None


def test_no_guardar_respaldo_como_descarga_fresca(tmp_path, monkeypatch):
    archivo = tmp_path / "cache.json.gz"
    monkeypatch.setattr(carga, "CACHE_DISCO", archivo)
    serie = carga._como_respaldo(pd.DataFrame({"fecha": pd.to_datetime(["2020-01-01"]), "valor": [1.]}))
    from datetime import datetime
    carga._guardar_disco(({"serie": serie}, datetime.now()))
    assert not archivo.exists()
