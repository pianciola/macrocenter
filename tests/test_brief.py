"""Regresiones de navegación y semántica de colores del brief."""
import pandas as pd
from macrocenter import catalogo, charts, style


def test_siete_series_neutras_no_repiten_color_ni_usan_semaforo():
    df = pd.DataFrame({"fecha": pd.date_range("2026-01-01", periods=2),
                       **{str(i): [i, i + 1] for i in range(7)}})
    fig = charts.lineas(df, {str(i): str(i) for i in range(7)}, "Cotizaciones")
    colores = [t.line.color for t in fig.data]
    assert len(set(colores)) == 7
    assert not set(colores) & {charts.POS, charts.NEG}
    explicitos = ("#123456", "#654321")
    fig = charts.lineas(df, {"a": "0", "b": "1"}, "Explícitos", colores=explicitos)
    assert tuple(t.line.color for t in fig.data) == explicitos


def test_barras_neutras_por_defecto_y_semantica_explicita():
    df = pd.DataFrame({"fecha": pd.date_range("2026-01-01", periods=2), "valor": [-1., 1.]})
    assert charts.barras(df, "valor", "Serie").data[0].marker.color == charts.PALETA[0]
    assert list(charts.barras(df, "valor", "Saldo", color_signo=True).data[0].marker.color) == [charts.NEG, charts.POS]


def test_ticker_decorativo_y_periodos_distintos():
    html = style.ticker([dict(n="BTC", v="USD 1", d=1., periodo="24 h"),
                         dict(n="IPC", v="2%", periodo="Mensual")])
    assert '<span class="copia" aria-hidden="true">' in html
    assert '· 24 h' in html and 'Mensual' in html


def test_enlaces_de_resumen_y_escapado():
    assert catalogo.ruta("paro", "Actividad") == "?ver=tablero/salarios"
    assert catalogo.ruta("riesgo", "Sector externo") == "?ver=tablero/tasas-y-riesgo-pais"
    html = style.panorama([dict(tema="Reservas", cifra="USD 1 M", detalle="brutas", texto="<script>")], "17/10/2026")
    assert 'href="?ver=tablero/reservas"' in html
    assert '&lt;script&gt;' in html and '<script>' not in html


def test_tabla_de_grafico_formatea_fechas_sin_redondear_cripto_a_cero():
    xs = pd.date_range("2026-01-01", periods=3)
    assert charts.filas_accesibles(xs, [-20.123456, .00000025, None]) == [
        ["01/01/2026", "-20,1235"], ["02/01/2026", "2,5e-07"], ["03/01/2026", "s/d"]]
    assert charts.filas_accesibles(["Categoría"], [1000.]) == [["Categoría", "1.000"]]
