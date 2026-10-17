from macrocenter import style, charts
from macrocenter.diseno import FUENTE_GRAFICOS
import pandas as pd


def test_intro_conserva_explicacion_y_nota():
    html = style.intro("Explicación completa.", nota_md="Supuesto necesario.", resumen="Síntesis.")
    assert "Síntesis." in html
    assert "Explicación completa." in html and "Supuesto necesario." in html
    assert '<details class="mc-como">' in html


def test_pregunta_conserva_unidad_y_datos():
    titulo = "Brecha cambiaria (%)"
    serie = pd.Series([10, 20], index=pd.to_datetime(["2026-01-01", "2026-02-01"]))
    fig = charts.lineas(pd.DataFrame({"fecha": serie.index, "brecha": serie.values}), {"Brecha": "brecha"}, titulo)
    assert fig.layout.meta["pregunta"]
    assert "%" in fig.layout.title.text
    assert list(fig.data[0].y) == [10, 20]
    assert fig.layout.font.family == FUENTE_GRAFICOS

