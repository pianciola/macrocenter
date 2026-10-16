"""Regresiones de la fila de pestañas y de la comparación trasladada."""
import shutil
import subprocess

import pandas as pd
import pytest

from macrocenter import inversiones, style


def test_navegacion_agrupa_indicadores_sin_fila_desplazable():
    from macrocenter.presentacion import ECONOMIA, MERCADOS
    assert "Inflación y dinero" in ECONOMIA
    assert "Dólar" in MERCADOS
    assert not set(ECONOMIA) & set(MERCADOS)


def test_comparacion_trasladada_conserva_variacion_interanual(monkeypatch):
    monkeypatch.setattr(inversiones, "_hoy", lambda: pd.Timestamp("2026-10-16"))
    monkeypatch.setattr(inversiones.st, "markdown", lambda *a, **kw: None)
    fechas = pd.date_range("2024-01-31", periods=33, freq="ME")
    dolares = pd.DataFrame({"fecha": fechas, "oficial": [100 * 1.02**i for i in range(33)],
                            "blue": [120 * 1.03**i for i in range(33)]})
    infl = pd.DataFrame({"fecha": fechas, "valor": 30.})
    dibujos = []
    def grafico(clave, datos, crear, **kw):
        dibujos.append((clave, datos, crear(datos)))
    inversiones.comparar_dolar_inflacion({"dolares": dolares, "infl_ia": infl}, grafico)
    clave, datos, figura = dibujos[0]
    assert clave == "inv_dolar_infl"
    assert datos["oficial"].dropna().iloc[-1] == pytest.approx((1.02**12 - 1) * 100)
    assert len(figura.data) >= 3
