from macrocenter import style, charts
from macrocenter.diseno import FUENTE_GRAFICOS
import pandas as pd


def test_intro_dejo_de_dibujar_leyendas():
    # las leyendas de colores y los textos de introducción ya no se dibujan en ninguna página
    assert style.intro("Explicación completa.", nota_md="Supuesto necesario.", resumen="Síntesis.") == ""
    # y en las secciones del tablero la función solo conserva la píldora «← Inicio»
    html = style.intro("Explicación completa.", inicio=True)
    assert 'class="mc-inicio"' in html and 'data-btn="nav_resumen"' in html
    assert "mc-intro" not in html.replace("mc-intro-fila", "").replace('class="mc-inicio"', "")
    assert "Explicación completa." not in html and "Supuesto necesario." not in html


def test_pregunta_conserva_unidad_y_datos():
    titulo = "Brecha cambiaria (%)"
    serie = pd.Series([10, 20], index=pd.to_datetime(["2026-01-01", "2026-02-01"]))
    fig = charts.lineas(pd.DataFrame({"fecha": serie.index, "brecha": serie.values}), {"Brecha": "brecha"}, titulo)
    assert fig.layout.meta["pregunta"]
    assert "%" in fig.layout.title.text
    assert list(fig.data[0].y) == [10, 20]
    assert fig.layout.font.family == FUENTE_GRAFICOS



def test_panorama_presenta_contexto_sin_otra_tarjeta_numerica():
    html = style.panorama([{"tema": "Dólar", "texto": "La brecha compara dos cotizaciones.",
                            "cifra": "$1.535", "detalle": "oficial"}], "17/10/2026")
    assert "La brecha compara dos cotizaciones." in html
    assert '$1.535' not in html
    assert '<div class="cifra">' not in html
    assert '?ver=tablero/dolar' in html
