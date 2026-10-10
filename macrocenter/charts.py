"""Constructores de gráficos Plotly y formateo numérico (es-AR) para MacroCenter."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go

PALETA = ["#2E86DE", "#EE5253", "#10AC84", "#F79F1F", "#8E44AD", "#576574"]
POS, NEG = "#10AC84", "#EE5253"


def num(x: float | None, dec: int = 0, suf: str = "", pre: str = "") -> str:
    """Formato argentino: 1.234,56"""
    if x is None or pd.isna(x):
        return "s/d"
    if round(x, dec) == 0:
        x = 0.0  # evita «-0,0»
    s = f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{pre}{s}{suf}"


def _base(fig: go.Figure, titulo: str, yfmt: str | None, height: int) -> go.Figure:
    fig.update_layout(
        font=dict(family="Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, Helvetica Neue, Roboto, Arial, sans-serif"),
        title=dict(text=titulo, font=dict(size=16)),
        height=height,
        margin=dict(l=10, r=10, t=50, b=45),
        hovermode="x unified",
        # la leyenda va abajo (arriba pisaba el título en pantallas angostas)
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(128,128,128,0.2)", tickformat=yfmt, separatethousands=True),
        separators=",.",  # formato argentino en ejes y etiquetas: 1.600,5
    )
    if _eje_x_fechas(fig):
        # fechas en formato numérico argentino (Plotly trae los meses en inglés: «Jan 2025»)
        fig.update_xaxes(
            hoverformat="%d/%m/%Y",
            tickformatstops=[
                dict(dtickrange=[None, 86_400_000 * 27], value="%d/%m"),        # días o semanas
                dict(dtickrange=[86_400_000 * 27, 86_400_000 * 360], value="%m/%Y"),  # meses
                dict(dtickrange=[86_400_000 * 360, None], value="%Y"),          # años
            ])
    return fig


def _eje_x_fechas(fig: go.Figure) -> bool:
    """¿Alguna serie del gráfico tiene fechas en el eje x?"""
    for tr in fig.data:
        x = getattr(tr, "x", None)
        if x is None or len(x) == 0:
            continue
        if pd.api.types.is_datetime64_any_dtype(pd.Series(x)) or isinstance(x[0], (pd.Timestamp, np.datetime64)):
            return True
    return False


def lineas(
    df: pd.DataFrame,
    series: dict[str, str],
    titulo: str,
    yfmt: str | None = ",.0f",
    height: int = 380,
    x: str = "fecha",
    paso: bool = False,
    ocultas: tuple[str, ...] = (),
) -> go.Figure:
    """Líneas. `series` mapea nombre visible -> columna de df. Las de `ocultas` arrancan apagadas
    (se prenden tocando la leyenda)."""
    fig = go.Figure()
    for i, (nombre, col) in enumerate(series.items()):
        d = df[[x, col]].dropna()
        fig.add_trace(
            go.Scatter(
                x=d[x], y=d[col], name=nombre, mode="lines",
                line=dict(color=PALETA[i % len(PALETA)], width=2, shape="hv" if paso else "linear"),
                visible="legendonly" if nombre in ocultas else True,
            )
        )
    return _base(fig, titulo, yfmt, height)


def barras(
    df: pd.DataFrame,
    col: str,
    titulo: str,
    yfmt: str | None = ",.1f",
    height: int = 380,
    x: str = "fecha",
    color_signo: bool = True,
    nombre: str | None = None,
) -> go.Figure:
    d = df[[x, col]].dropna()
    colores = [POS if v >= 0 else NEG for v in d[col]] if color_signo else PALETA[0]
    fig = go.Figure(go.Bar(x=d[x], y=d[col], marker_color=colores, name=nombre or col))
    return _base(fig, titulo, yfmt, height)


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def medidor(puntaje: float, etiqueta: str, color: str, niveles: list[tuple[int, str, str]], height: int = 250) -> go.Figure:
    """Medidor semicircular 0-100 con las franjas de cada nivel de calificación."""
    cortes = [n[0] for n in niveles][::-1] + [100]  # ascendente
    colores = [n[2] for n in niveles][::-1]
    pasos = [dict(range=[cortes[i], cortes[i + 1]], color=_rgba(colores[i], 0.28)) for i in range(len(colores))]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=puntaje,
        number=dict(suffix="/100", valueformat=".0f", font=dict(size=40)),
        title=dict(text=f"<b>{etiqueta}</b>", font=dict(size=17, color=color)),
        gauge=dict(axis=dict(range=[0, 100], tickvals=[0, 25, 40, 60, 75, 100]),
                   bar=dict(color=color, thickness=0.32), steps=pasos, borderwidth=0),
    ))
    fig.update_layout(height=height, margin=dict(l=25, r=25, t=60, b=10))
    return fig


def evolucion_nota(df: pd.DataFrame, niveles: list[tuple[int, str, str]], titulo: str, height: int = 400) -> go.Figure:
    """Nota total (línea gruesa) y por pilar (finas) con las franjas de nivel de fondo."""
    fig = go.Figure()
    cortes = [n[0] for n in niveles][::-1] + [100]
    for i, (_, _, color) in enumerate(niveles[::-1]):
        fig.add_hrect(y0=cortes[i], y1=cortes[i + 1], fillcolor=_rgba(color, 0.10), line_width=0, layer="below")
    pilares = [c for c in df.columns if c not in ("fecha", "Total")]
    for i, p in enumerate(pilares):
        fig.add_trace(go.Scatter(x=df["fecha"], y=df[p], name=p, mode="lines",
                                 line=dict(color=PALETA[(i + 1) % len(PALETA)], width=1.3), opacity=0.75))
    fig.add_trace(go.Scatter(x=df["fecha"], y=df["Total"], name="Nota total", mode="lines",
                             line=dict(color=PALETA[0], width=3.5)))
    fig = _base(fig, titulo, ",.0f", height)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5),
                      margin=dict(l=10, r=10, t=50, b=40))
    fig.update_yaxes(range=[0, 100])
    return fig


def serie_presidentes(df: pd.DataFrame, mandatos: list, cortos: dict[str, str], titulo: str, height: int = 330,
                      marca: pd.Timestamp | None = None, log: bool = False, yfmt: str = ",.0f",
                      ticks: tuple[list, list] | None = None, minimo_log: float | None = None, cero: bool = False,
                      color: str | None = None, desde: pd.Timestamp | str = "1983-12-01") -> go.Figure:
    """Una serie histórica con cada mandato sombreado y rotulado. `df`: fecha, valor.
    En escala logarítmica los valores menores a `minimo_log` se dibujan en ese piso (no admite negativos);
    el texto del hover siempre muestra el valor real."""
    d = df[df["fecha"] >= pd.Timestamp(desde)]
    y = d["valor"].clip(lower=minimo_log) if (log and minimo_log is not None) else d["valor"]
    fig = go.Figure(go.Scatter(
        x=d["fecha"], y=y, mode="lines", line=dict(color=color or PALETA[1], width=2), name=titulo,
        customdata=d["valor"], hovertemplate="%{x|%m/%Y}: %{customdata:,.1f}<extra></extra>"))
    for i, m in enumerate(mandatos):
        fig.add_vrect(x0=m.desde, x1=m.fin, line_width=0, layer="below",
                      fillcolor=_rgba("#74ACDF", 0.16 if i % 2 == 0 else 0.04))
        fig.add_annotation(x=m.desde + (m.fin - m.desde) / 2, y=0.98, yref="paper", yanchor="top",
                           text=cortos.get(m.clave, m.nombre), showarrow=False, textangle=-90,
                           font=dict(size=11), opacity=0.85)
    if cero:
        fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="rgba(128,128,128,.7)")
    if marca is not None:  # línea vertical: "estás acá"
        fig.add_vline(x=marca, line_width=3, line_color="#F6B40E")
    fig = _base(fig, titulo, None if log else yfmt, height)
    fig.update_layout(showlegend=False, hovermode="x")
    fig.update_xaxes(range=[d["fecha"].min(), pd.Timestamp.today()])
    if log:
        fig.update_yaxes(type="log")
    if ticks:
        fig.update_yaxes(tickvals=ticks[0], ticktext=ticks[1])
    return fig


def marcar_eventos(fig: go.Figure, eventos: list, desde: pd.Timestamp) -> go.Figure:
    """Líneas punteadas verticales con el rótulo de cada hito (solo los que caen dentro del gráfico)."""
    for fecha, texto in eventos:
        if fecha < pd.Timestamp(desde):
            continue
        fig.add_vline(x=fecha, line_width=1, line_dash="dot", line_color="rgba(246,180,14,.85)")
        fig.add_annotation(x=fecha, y=0.02, yref="paper", yanchor="bottom", xanchor="left", text=texto, showarrow=False,
                           textangle=-90, font=dict(size=10, color="#F6B40E"), opacity=0.95)
    return fig


def comparar_mandatos(nombres: list[str], valores: list, titulo: str, sufijo: str = "", dec: int = 1,
                      actual: str | None = None, height: int = 330, logaritmica: bool = False) -> go.Figure:
    """Barras por mandato en orden cronológico (no ordenadas por valor, para no sugerir un ranking)."""
    ok = [(n, v) for n, v in zip(nombres, valores) if v is not None and v == v]
    colores = ["#F6B40E" if n == actual else PALETA[0] for n, _ in ok]
    ys = [v for _, v in ok]
    if logaritmica:
        # escala logarítmica que admite ceros y negativos (simétrica): una hiperinflación no aplasta al resto
        ys = [math.copysign(math.log10(1 + abs(v)), v) for v in ys]
    fig = go.Figure(go.Bar(
        x=[n for n, _ in ok], y=ys, marker_color=colores,
        text=[num(v, dec, sufijo) for _, v in ok], textposition="outside", cliponaxis=False,
        hovertemplate="%{x}: %{text}<extra></extra>"))
    fig = _base(fig, titulo, None, height)
    fig.update_layout(hovermode="closest", showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    fig.update_yaxes(zeroline=True, zerolinecolor="rgba(128,128,128,.5)")
    if logaritmica:
        marcas = [0, 10, 100, 1000, 10000, 100000, 1000000]
        tope = max((abs(v) for _, v in ok), default=0)
        marcas = [m for m in marcas if m == 0 or m <= tope * 10]
        fig.update_yaxes(tickvals=[math.log10(1 + m) for m in marcas],
                         ticktext=[num(m, 0, sufijo) for m in marcas], title=dict(text="escala logarítmica", font=dict(size=11)))
    return fig


def rendimientos(nombres: list[str], valores: list[float], inflacion: float | None, titulo: str, height: int = 340) -> go.Figure:
    """Barras horizontales ordenadas de mayor a menor; en verde lo que superó a la inflación del período (línea punteada)."""
    orden = sorted(zip(nombres, valores), key=lambda p: p[1])
    ref = inflacion if inflacion is not None else 0
    colores = [POS if v > ref else NEG for _, v in orden]
    fig = go.Figure(go.Bar(
        y=[n for n, _ in orden], x=[v for _, v in orden], orientation="h", marker_color=colores,
        text=[num(v, 1, "%") for _, v in orden], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{text}<extra></extra>"))
    if inflacion is not None:
        fig.add_vline(x=inflacion, line_width=2, line_dash="dash", line_color="#F6B40E",
                      annotation_text=f"Inflación {num(inflacion, 1, '%')}", annotation_position="top",
                      annotation_font=dict(color="#F6B40E", size=12))
    fig = _base(fig, titulo, None, height)
    fig.update_layout(hovermode="closest", showlegend=False, margin=dict(l=10, r=40, t=60, b=10))
    fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor="rgba(128,128,128,.2)", zeroline=True,
                     zerolinecolor="rgba(128,128,128,.5)")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    return fig


def inflacion_presidentes(df: pd.DataFrame, mandatos: list, cortos: dict[str, str], titulo: str,
                          height: int = 330, marca: pd.Timestamp | None = None) -> go.Figure:
    """Inflación anual en escala logarítmica (valores menores a 1% se dibujan en 1%)."""
    fig = serie_presidentes(df, mandatos, cortos, titulo, height, marca, log=True, minimo_log=1,
                            ticks=([1, 10, 100, 1000, 10000], ["1%", "10%", "100%", "1.000%", "10.000%"]))
    fig.update_yaxes(range=[0, 4.1])
    return fig


def barras_y_linea(
    df: pd.DataFrame, col_barra: str, col_linea: str, titulo: str,
    nombre_barra: str, nombre_linea: str, yfmt: str = ",.1f", height: int = 380, x: str = "fecha",
) -> go.Figure:
    d = df[[x, col_barra, col_linea]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d[x], y=d[col_barra], name=nombre_barra, marker_color=PALETA[0], opacity=0.55))
    fig.add_trace(go.Scatter(x=d[x], y=d[col_linea], name=nombre_linea, mode="lines", yaxis="y2",
                             line=dict(color=PALETA[1], width=2.5)))
    fig = _base(fig, titulo, yfmt, height)
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, tickformat=",.0f",
                                  title=dict(text=nombre_linea, font=dict(color=PALETA[1], size=11)),
                                  tickfont=dict(color=PALETA[1])),
                      yaxis=dict(title=dict(text=nombre_barra, font=dict(color=PALETA[0], size=11))))
    return fig
