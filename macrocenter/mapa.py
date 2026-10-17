"""Mapa de la inflación por provincia: se toca una provincia y se ve la inflación de su región y, si la tiene, la de
su propio índice. Los límites son los oficiales del IGN (assets/provincias.geojson, armado con tools/armar_mapa.py);
Tierra del Fuego incluye las islas Malvinas.

Los colores son una escala neutra (de menos a más inflación interanual, sin juzgar): cada provincia lleva el color de
su región del INDEC, que es el dato que existe para todas."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from macrocenter import charts

GEOJSON = Path(__file__).resolve().parent.parent / "assets" / "provincias.geojson"
GBA, PAMPEANA, NEA, NOA, CUYO, PATAGONIA = ("Gran Buenos Aires", "Región Pampeana", "Región Noreste", "Región Noroeste",
                                            "Región Cuyo", "Región Patagonia")

# provincia -> región INDEC con la que se pinta (Buenos Aires: el resto de la provincia es Pampeana; sus 24 partidos del
# conurbano son el GBA, que se muestra aparte al tocarla)
REGION = {
    "Ciudad Autónoma de Buenos Aires": GBA, "Buenos Aires": PAMPEANA, "Córdoba": PAMPEANA, "Entre Ríos": PAMPEANA,
    "La Pampa": PAMPEANA, "Santa Fe": PAMPEANA, "Chaco": NEA, "Corrientes": NEA, "Formosa": NEA, "Misiones": NEA,
    "Catamarca": NOA, "Jujuy": NOA, "La Rioja": NOA, "Salta": NOA, "Santiago del Estero": NOA, "Tucumán": NOA,
    "Mendoza": CUYO, "San Juan": CUYO, "San Luis": CUYO, "Chubut": PATAGONIA, "Neuquén": PATAGONIA,
    "Río Negro": PATAGONIA, "Santa Cruz": PATAGONIA, "Tierra del Fuego": PATAGONIA,
}
# provincia -> nombre del distrito con índice propio (los de app.py: DISTRITOS_IPC)
PROPIO = {"Ciudad Autónoma de Buenos Aires": "Ciudad de Buenos Aires", "Santa Fe": "Santa Fe", "Mendoza": "Mendoza",
          "Tucumán": "Tucumán", "San Luis": "San Luis", "Chaco": "Chaco (Gran Resistencia)", "Neuquén": "Neuquén"}
APARTE = {"Buenos Aires": [GBA]}  # además de su región
ESCALA = [[0, "#dbe9f6"], [0.5, "#5a9bd4"], [1, "#0b3d73"]]


@st.cache_resource(show_spinner=False)
def _geojson() -> dict:
    return json.loads(GEOJSON.read_text(encoding="utf-8"))


def distritos_de(provincia: str) -> list[str]:
    """Los distritos (de `series` en app.py) que se muestran al tocar una provincia: el propio, si tiene, y su región."""
    out = [PROPIO[provincia]] if provincia in PROPIO else []
    out += APARTE.get(provincia, [])
    region = REGION.get(provincia)
    return out + ([region] if region and region not in out else [])


def _provincia_elegida(clave: str) -> str | None:
    estado = st.session_state.get(clave)
    try:
        puntos = estado["selection"]["points"]
        loc = puntos[0].get("location") if puntos else None
    except (KeyError, TypeError, IndexError, AttributeError):
        return None
    return loc if loc in REGION else None


def _ultimo(v: pd.DataFrame) -> pd.Series:
    return v.dropna(subset=["mensual"]).iloc[-1]


def mostrar(series: dict, clave: str = "mapa_infl") -> None:
    """`series`: {distrito: (fuente, DataFrame fecha/mensual/interanual)}, el mismo de la tabla de inflación."""
    try:
        geo = _geojson()
    except (OSError, ValueError):
        return  # sin el archivo de límites no hay mapa; la tabla y el gráfico siguen
    provincias = [p for p in REGION if REGION[p] in series]
    if len(provincias) < 10:
        return
    ia = {p: float(_ultimo(series[REGION[p]][1])["interanual"]) for p in provincias}
    elegida = _provincia_elegida(clave)
    fig = go.Figure(go.Choropleth(
        geojson=geo, locations=provincias, z=[ia[p] for p in provincias], featureidkey="id",
        customdata=[REGION[p] for p in provincias], colorscale=ESCALA, marker_line_color="rgba(105,124,145,0.8)", marker_line_width=0.6,
        # el resaltado de la elegida lo hace Plotly en el navegador (el dibujo no cambia al tocar): si el gráfico
        # cambiara con cada toque, Streamlit lo volvería a armar y el mapa parpadearía
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=0.5)),
        hovertemplate="<b>%{location}</b><br>%{customdata}: %{z:.1f}% interanual<extra></extra>",
        # la escala va abajo y a lo ancho: en el celular, una barra vertical al costado achicaba el mapa a la mitad
        colorbar=dict(orientation="h", title=dict(text="Inflación interanual (%)", side="top"), thickness=10, len=0.8,
                      x=0.5, xanchor="center", y=-0.02, yanchor="top", ticksuffix="%", outlinewidth=0),
    ))
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)", projection_type="mercator")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=64), height=540, dragmode=False, clickmode="event+select",
                      uirevision="mapa", separators=",.", paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))
    st.markdown("**Tocá una provincia** para ver su inflación. Cada una lleva el color de su región del INDEC.")
    st.plotly_chart(fig, width="stretch", key=clave, on_select="rerun", selection_mode="points",
                    config={"displayModeBar": False, "scrollZoom": False})
    if not elegida:
        return
    st.markdown(f"#### {elegida}")
    nac = _ultimo(series["Nacional"][1]) if "Nacional" in series else None
    nombres = [d for d in distritos_de(elegida) if d in series]
    cols = st.columns(len(nombres))
    for col, nombre in zip(cols, nombres):
        fuente, v = series[nombre]
        u = _ultimo(v)
        with col:
            st.markdown(f"**{nombre}**" + ("" if nombre.startswith(("Región", "Gran")) else " · índice propio"))
            c1, c2 = st.columns(2)
            c1.metric("Mensual", charts.num(u["mensual"], 1, suf="%"), border=True)
            dif = (u["interanual"] - nac["interanual"]) if nac is not None and pd.notna(u["interanual"]) else None
            c2.metric("Interanual", charts.num(u["interanual"], 1, suf="%"),
                      None if dif is None or nombre == "Nacional" else f"{charts.num(dif, 1)} pp vs nacional",
                      delta_color="off", border=True)
            st.caption(f"{fuente} · dato de {u['fecha']:%m/%Y}")
    if elegida == "Buenos Aires":
        st.caption("El GBA son la Ciudad y 24 partidos del conurbano; el resto de la provincia está en la región Pampeana.")
    if elegida in PROPIO and REGION[elegida]:
        st.caption(f"Su región es {REGION[elegida]}; el índice propio lo mide el instituto de estadística local.")
