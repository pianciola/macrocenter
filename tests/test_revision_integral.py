import threading
import time

import pandas as pd
import pytest

from macrocenter import carga, series, style


def test_comparacion_no_sustituye_un_mes_ausente_por_otra_fila():
    df = pd.DataFrame({"fecha": pd.to_datetime(["2026-03-01", "2026-01-01", "2027-01-01"]), "valor": [120.,100.,999.]})
    assert series.comparar(df, hoy="2026-04-01") == (120., None)
    assert series.comparar(df, atras=2, hoy="2026-04-01") == (120.,100.)


def test_comparacion_trimestral_y_semestral():
    df = pd.DataFrame({"fecha": pd.date_range("2025-01-01", periods=5, freq="QS"), "valor": [1.,2.,3.,4.,5.]})
    assert series.comparar(df, meses=3, hoy="2026-01-02") == (5.,4.)
    assert series.comparar(df, meses=6, hoy="2026-01-02") == (5.,3.)


def test_variacion_calendario_no_cuenta_filas_y_no_divide_por_cero():
    df = pd.DataFrame({"fecha": pd.to_datetime(["2025-01-01", "2025-03-01", "2026-03-01"]), "valor": [0.,100.,120.]})
    resultado = series.cambio_periodico(df)
    assert resultado.valor.iloc[-1] == pytest.approx(20.)
    assert resultado.valor.iloc[:2].isna().all()
    df.loc[1,"valor"] = 0
    assert pd.isna(series.cambio_periodico(df).valor.iloc[-1])


def test_cache_vacia_conserva_ultimo_dato_y_programa_reintento():
    anterior = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-15"]), "valor": [123.]})
    entrada = {"v": {"serie": anterior}, "t": 0., "lock": threading.Lock()}
    carga._bajar_y_guardar(entrada, lambda: {"serie": pd.DataFrame()}, ttl=300, reintento=60)
    assert entrada["v"]["serie"] is anterior
    assert 239 <= time.time()-entrada["t"] <= 242


def test_error_inesperado_no_genera_reintentos_en_cada_click():
    entrada = {"v": {"serie": "sin datos"}, "t": 0.}
    def falla():
        raise TimeoutError()
    with pytest.raises(TimeoutError):
        carga._bajar_y_guardar(entrada, falla, ttl=300, reintento=60)
    assert 239 <= time.time()-entrada["t"] <= 242


def test_tabla_accesible_y_escapada():
    html = style.tabla_simple(["Entidad", "Compra", "Venta", "Variacion"], [["<script>",1,2,3]])
    assert 'tabindex="0"' in html and 'role="region"' in html
    assert 'mc-tabla-ancha' in html and '&lt;script&gt;' in html
    assert '<script>' not in html
