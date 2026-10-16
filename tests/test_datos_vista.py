import pandas as pd
from macrocenter import datos_vista, charts


def test_fecha_del_dato_ignora_futuro_y_no_depende_del_orden():
    df = pd.DataFrame({"fecha": ["2027-01-01", "2026-10-15", None, "2026-10-14"]})
    html = datos_vista.detalle(df, "BCRA", hoy="2026-10-16")
    assert "15/10/2026" in html and "2027" not in html
    assert "Dato con rezago" not in html


def test_rezago_distingue_frecuencia_y_escapa_fuente():
    diaria = pd.DataFrame({"fecha": pd.date_range("2026-08-01", periods=20)})
    assert "Dato con rezago" in datos_vista.detalle(diaria, "BCRA", hoy="2026-10-16")
    mensual = pd.DataFrame({"fecha": pd.date_range("2026-01-01", periods=8, freq="MS")})
    html = datos_vista.detalle(mensual, "INDEC <dato>", hoy="2026-10-16")
    assert "Dato con rezago" not in html
    assert "&lt;dato&gt;" in html and "<dato>" not in html
    assert "Fecha no disponible" in datos_vista.detalle(None, "CoinGecko")


def test_presentar_no_cambia_colores_valores_ni_unidades():
    f = charts.lineas(pd.DataFrame({"fecha": pd.date_range("2026-01-01", periods=3), "v": [1,2,3]}),
                      {"Serie": "v"}, "Tasa (%)")
    color, valores = f.data[0].line.color, list(f.data[0].y)
    charts.presentar(f)
    assert f.data[0].line.color == color and list(f.data[0].y) == valores
    assert f.layout.title.text == "Tasa (%)"
    assert f.layout.xaxis.automargin and f.layout.legend.maxheight == .24
