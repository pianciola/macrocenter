"""Piezas de la página que no necesitan red: gráficos, CSV, estilo y el monitor."""
import pandas as pd
import plotly.graph_objects as go

import revisar  # monitor/revisar.py
from macrocenter import charts, style


def test_num_formato_argentino():
    assert charts.num(1234567.891, 2) == "1.234.567,89"
    assert charts.num(-0.04, 1) == "0,0"
    assert charts.num(None) == "s/d"


def test_csv_de_un_grafico():
    f = pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01"])
    fig = go.Figure([go.Scatter(x=f, y=[1.5, 2.25, 3.0], name="Blue"),
                     go.Scatter(x=f[1:], y=[10.0, 20.0], name="MEP"),
                     go.Scatter(x=[f[-1]], y=[3.0], name="último")])  # marca suelta: no va al CSV
    t = charts.trazas_de(fig)
    assert [n for n, _, _ in t] == ["Blue", "MEP"]
    texto = charts.csv_de(t).decode("utf-8-sig")
    assert texto.splitlines() == ["fecha;Blue;MEP", "2026-01-01;1,5;", "2026-02-01;2,25;10,0", "2026-03-01;3,0;20,0"]


def test_csv_de_barras_horizontales_y_categorias():
    fig = go.Figure(go.Bar(x=[5.0, 7.0, 9.0], y=["Banco A", "Banco B", "Banco C"], orientation="h", name="TNA"))
    texto = charts.csv_de(charts.trazas_de(fig)).decode("utf-8-sig")
    assert texto.splitlines()[0] == "categoría;TNA" and "Banco B;7,0" in texto


def test_css_balanceado():
    assert style.CSS.count("{") == style.CSS.count("}")


def test_form_alertas_va_directo_a_buttondown():
    f = style.form_alertas()
    assert 'action="https://buttondown.com/api/emails/embed-subscribe/macrocenter"' in f
    assert 'name="tag" value="alertas"' in f and 'type="email"' in f


def test_slug():
    assert style.slug("Tasas y riesgo país") == "tasas-y-riesgo-pais"
    assert style.slug("¿Cuánto valían tus pesos?") == "cuanto-valian-tus-pesos"


def test_frescura_segun_la_frecuencia(monkeypatch):
    monkeypatch.setattr(revisar.data, "hoy_argentina", lambda: "2026-10-14")
    hoy = pd.Timestamp("2026-10-14")
    diaria = pd.DataFrame({"fecha": pd.date_range(end=hoy - pd.Timedelta(days=3), periods=30, freq="D")})
    assert revisar.antiguedad(diaria.assign(valor=1.0)) is None
    vieja = pd.DataFrame({"fecha": pd.date_range(end=hoy - pd.Timedelta(days=20), periods=30, freq="D"), "valor": 1.0})
    assert "desactualizada" in revisar.antiguedad(vieja)
    mensual = pd.DataFrame({"fecha": pd.date_range(end="2026-06-01", periods=24, freq="MS"), "valor": 1.0})
    assert revisar.antiguedad(mensual) is None  # 135 días: normal para un índice provincial
    assert revisar.dias_maximos(1) == 10 and revisar.dias_maximos(31) == 180 and revisar.dias_maximos(91) == 300


def test_mapa_cubre_todas_las_provincias_con_malvinas():
    import json

    from macrocenter import mapa

    geo = json.loads(mapa.GEOJSON.read_text(encoding="utf-8"))
    nombres = {f["id"] for f in geo["features"]}
    assert nombres == set(mapa.REGION) and len(nombres) == 24
    tdf = next(f for f in geo["features"] if f["id"] == "Tierra del Fuego")
    lon_min, lon_max = -75, -56
    xs = [pt[0] for poly in tdf["geometry"]["coordinates"] for ring in poly for pt in ring]
    ys = [pt[1] for poly in tdf["geometry"]["coordinates"] for ring in poly for pt in ring]
    assert lon_min < min(xs) and max(xs) < lon_max and min(ys) > -56
    assert any(-61.5 < x < -57.5 and -53.2 < y < -51 for x, y in zip(xs, ys)), "faltan las islas Malvinas"


def test_mapa_distritos_por_provincia():
    from macrocenter import mapa

    assert mapa.distritos_de("Santa Fe") == ["Santa Fe", "Región Pampeana"]
    assert mapa.distritos_de("Buenos Aires") == ["Gran Buenos Aires", "Región Pampeana"]
    assert mapa.distritos_de("Ciudad Autónoma de Buenos Aires") == ["Ciudad de Buenos Aires", "Gran Buenos Aires"]
    assert mapa.distritos_de("Tierra del Fuego") == ["Región Patagonia"]
    assert all(mapa.distritos_de(p) for p in mapa.REGION)
