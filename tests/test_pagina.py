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


def test_el_script_de_la_pagina_no_lleva_etiquetas_html():
    # Streamlit sanea el HTML de st.html y descarta los scripts que contienen algo como «<span»: el script entero
    # dejaba de correr sin ningún error (pasó con el botón del pie). Los elementos se arman con createElement.
    import re

    cuerpo = style.JS_PESTANAS.replace("<script>", "").replace("</script>", "")
    assert not re.search(r"<[/\w!]", cuerpo)


def test_titulos_de_seccion_no_dependen_de_una_clase_en_html():
    # los estilos de los títulos excluyen lo que está dentro de un elemento con «mc-» en la clase: el estado del botón
    # del pie va en un atributo de <html>, nunca en una clase (con una clase, los títulos perdían la barra celeste)
    assert "mc-pie-oculto" not in style.CSS and "mc-pie-oculto" not in style.JS_PESTANAS
    assert 'html[data-pie="oculto"]' in style.CSS and "dataset.pie" in style.JS_PESTANAS


def test_formulario_de_alertas_se_oculta_al_anotarse():
    assert 'html[data-alertas="anotado"] .mc-alerta' in style.CSS
    assert "mc_alertas_anotado" in style.JS_PESTANAS and "dataset.alertas" in style.JS_PESTANAS


def test_noticias_del_indec(monkeypatch):
    # del calendario de difusión se toma solo lo ya publicado, y solo fecha, título y enlace
    from macrocenter import news

    crudo = ('[{"fechaPublicacion":"2026-10-13T16:00:00","titulo_espaniol":"\u00cdndice de precios al consumidor",'
             '"urlArchivo":"uploads/informesdeprensa/ipc.pdf","publicado":1,"DNI_alta":"1"},'
             '{"fechaPublicacion":"2999-01-01T16:00:00","titulo_espaniol":"Futuro","urlArchivo":"x.pdf","publicado":1},'
             '{"fechaPublicacion":"2026-10-12T16:00:00","titulo_espaniol":"Borrador","urlArchivo":"y.pdf","publicado":0}]')

    class R:
        content = ("<script>var CalendarJson = '" + crudo + "';</script>").encode("utf-8")

        def raise_for_status(self):
            pass

    monkeypatch.setattr(news.requests, "get", lambda *a, **k: R())
    notas = news.indec()
    assert [n.titulo for n in notas] == ["Índice de precios al consumidor"]
    assert notas[0].url == "https://www.indec.gob.ar/uploads/informesdeprensa/ipc.pdf" and news.url_segura(notas[0].url)


def test_la_hoja_de_estilos_pasa_el_saneador():
    # el CSS va por st.html: su saneador descarta una hoja de estilos entera si adentro aparece «<algo» (por ejemplo, un
    # comentario que menciona <html> o un ícono SVG sin codificar), y la página quedaría sin formato
    import re

    cuerpo = style.CSS.strip()
    assert cuerpo.startswith("<style>") and cuerpo.endswith("</style>")
    assert not re.search(r"<[/\w!]", cuerpo[len("<style>"):-len("</style>")])
