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


def _fechas_cortas(x) -> list | None:
    """Fechas de un eje como texto corto («2024-10-11» en vez de «2024-10-11T00:00:00.000000»). Plotly las sigue
    leyendo como fechas. None si el eje no es de fechas (categorías, números)."""
    try:
        if len(x) == 0:
            return None
        muestra = next((v for v in x if v is not None and not (isinstance(v, float) and math.isnan(v))), None)
        if not isinstance(muestra, (pd.Timestamp, np.datetime64)) and type(muestra).__name__ not in ("datetime", "date"):
            return None
        idx = pd.DatetimeIndex(pd.to_datetime(list(x)))
    except (TypeError, ValueError):
        return None
    fmt = "%Y-%m-%d" if bool((idx.dropna() == idx.dropna().normalize()).all()) else "%Y-%m-%d %H:%M"
    return [None if pd.isna(v) else v.strftime(fmt) for v in idx]


def _un_numero(v: float) -> float | None:
    if not math.isfinite(v):
        return None
    if abs(v) >= 1:  # la parte entera nunca se toca; decimales: al menos 2 (más si el número es chico)
        return round(v, max(2, 6 - (int(math.log10(abs(v))) + 1)))
    return float(f"{v:.6g}")  # menores que 1 (cripto chicas, tasas): 6 cifras significativas


def _redondear(y) -> list | None:
    """Saca el ruido de punto flotante (1534.9999999998 → 1535.0) sin cambiar el valor que se lee al pasar el cursor.
    None si no son todos números."""
    if any(isinstance(v, (str, bool, np.bool_)) for v in y):  # categorías («2016», nombres) quedan como están
        return None
    try:
        a = np.asarray(y, dtype=float)
    except (TypeError, ValueError):
        return None
    if a.ndim != 1:
        return None
    return [_un_numero(v) for v in a.tolist()]


def compactar(fig: go.Figure) -> go.Figure:
    """Achica lo que viaja al navegador sin cambiar el gráfico: fechas cortas y números sin decimales de sobra.
    En las series diarias el peso del gráfico baja a menos de la mitad."""
    for tr in fig.data:
        for eje in ("x", "y"):
            v = getattr(tr, eje, None)
            if v is None or isinstance(v, str):
                continue
            fechas = _fechas_cortas(v)
            if fechas is not None:
                tr.update({eje: fechas})
                continue
            if getattr(tr, "orientation", None) == "h" and eje == "y":
                continue  # en las barras horizontales el eje y son los nombres
            nums = _redondear(v)
            if nums is not None:
                tr.update({eje: nums})
    return fig


def trazas_de(fig: go.Figure) -> list[tuple]:
    """Los datos de cada línea o barra, tal como están ahora (antes de aligerar el gráfico): [(nombre, eje, valores)].
    Solo guarda referencias, no copia nada: el CSV se arma recién si alguien lo pide (ver `csv_de`)."""
    out = []
    for i, tr in enumerate(fig.data):
        if getattr(tr, "type", "") not in ("scatter", "bar") or tr.x is None or tr.y is None or len(tr.x) != len(tr.y):
            continue
        eje, valores = (tr.y, tr.x) if getattr(tr, "orientation", None) == "h" else (tr.x, tr.y)
        out.append((tr.name or f"Serie {i + 1}", eje, valores))
    largo = max((len(e) for _, e, _ in out), default=0)
    # marcas sueltas (el último punto, un promedio) no van: un punto solo, o dos al lado de series largas
    return [t for t in out if largo <= 1 or (len(t[1]) > 1 and (len(t[1]) > 2 or largo <= 10))]


def csv_de(trazas: list[tuple]) -> bytes:
    """CSV para Excel en castellano: separado por punto y coma, con coma decimal y fechas AAAA-MM-DD."""
    columnas = {}
    for nombre, eje, valores in trazas:
        s = pd.Series(pd.to_numeric(pd.Series(list(valores)), errors="coerce").to_numpy(), index=list(eje))
        s = s[~pd.Index(s.index).duplicated(keep="last")]
        clave, n = str(nombre), 2
        while clave in columnas:
            clave, n = f"{nombre} ({n})", n + 1
        columnas[clave] = s
    df = pd.DataFrame(columnas)
    try:
        idx = pd.to_datetime(df.index, format="ISO8601")
        df.index = idx.strftime("%Y-%m-%d" if bool((idx == idx.normalize()).all()) else "%Y-%m-%d %H:%M")
        df = df.sort_index()
        df.index.name = "fecha"
    except (TypeError, ValueError):
        df.index.name = "categoría"
    return df.to_csv(sep=";", decimal=",").encode("utf-8-sig")


def sacar_titulo(fig: go.Figure) -> tuple[str | None, str | None]:
    """Saca el título (y la bajada) de la figura para mostrarlo como texto de la página: Plotly no parte los títulos
    largos en renglones y en el celular quedaban cortados. Achica el margen de arriba que ocupaba el título."""
    titulo = fig.layout.title.text if fig.layout.title else None
    if not titulo:
        return None, None
    bajada = fig.layout.title.subtitle.text if fig.layout.title.subtitle else None
    arriba = fig.layout.margin.t if fig.layout.margin.t is not None else 80
    fig.update_layout(title_text=None, title_subtitle_text=None, margin_t=max(12, arriba - (72 if bajada else 50)))
    return titulo, bajada


def _marcas(fmt: str | None) -> str | None:
    """Formato de las marcas del eje: el mismo que el de los valores pero sin ceros de relleno («25» y no «25,0»;
    «2,5» sigue igual). El formato completo queda para el recuadro que aparece al pasar el cursor."""
    if fmt and fmt.endswith("f") and "~" not in fmt and "." in fmt:
        return fmt[:-1] + "~f"
    return fmt


def _partir_titulo(titulo: str) -> tuple[str, str | None]:
    """Los títulos largos no entran en pantallas angostas (Plotly no los parte y quedan cortados): lo que va después de
    « — » o el último paréntesis pasa a una bajada más chica."""
    if len(titulo) <= 44:
        return titulo, None
    if " — " in titulo:
        a, b = titulo.split(" — ", 1)
        return a, b[:1].upper() + b[1:]
    i = titulo.rfind(" (")
    if i > 15 and len(titulo) - i > 7:  # «(%)» o «($)» quedan en el título
        return titulo[:i], titulo[i + 1:]
    return titulo, None


def _base(fig: go.Figure, titulo: str, yfmt: str | None, height: int) -> go.Figure:
    titulo, bajada = _partir_titulo(titulo)
    if bajada:
        fig.update_layout(title_subtitle=dict(text=bajada, font=dict(size=12, color="rgba(128,128,128,1)")))
    fig.update_layout(
        font=dict(family="Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, Helvetica Neue, Roboto, Arial, sans-serif"),
        title=dict(text=titulo, font=dict(size=16)),
        height=height,
        margin=dict(l=10, r=10, t=50, b=45),
        hovermode="x unified",
        # la leyenda va abajo (arriba pisaba el título en pantallas angostas)
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(128,128,128,0.2)", tickformat=_marcas(yfmt), hoverformat=yfmt,
                   separatethousands=True),
        separators=",.",  # formato argentino en ejes y etiquetas: 1.600,5
    )
    if bajada:
        fig.update_layout(margin_t=72)
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


def evolucion_montos(df: pd.DataFrame, series: dict[str, str], referencia: str | None, titulo: str,
                     height: int = 420) -> go.Figure:
    """Cuánto valdría un monto invertido en cada alternativa, día a día. `referencia` (la inflación) va punteada y
    dorada: lo que está arriba de esa línea ganó poder de compra."""
    fig = go.Figure()
    if referencia and referencia in df:
        d = df[["fecha", referencia]].dropna()
        fig.add_trace(go.Scatter(x=d["fecha"], y=d[referencia], name="Inflación (lo que hacía falta para no perder)",
                                 mode="lines", line=dict(color="#F6B40E", width=2.5, dash="dash")))
    # colores propios: ni dorado (la inflación) ni verde/rojo (que en la página significan mejor/peor)
    colores = ["#2E86DE", "#A55EEA", "#00CEC9", "#FD79A8", "#8395A7", "#CD853F"]
    for i, (nombre, col) in enumerate(series.items()):
        d = df[["fecha", col]].dropna()
        fig.add_trace(go.Scatter(x=d["fecha"], y=d[col], name=nombre, mode="lines",
                                 line=dict(color=colores[i % len(colores)], width=2)))
    fig = _base(fig, titulo, ",.0f", height)
    fig.update_yaxes(tickprefix="$")
    return fig


def equilibrio_uva(infl: list[float], tradicional: list[float], uva: list[float], esperada: float | None,
                   corte: float | None, titulo: str, height: int = 360) -> go.Figure:
    """Monto final de un plazo fijo tradicional (horizontal: no depende de la inflación) y de uno UVA (sube con la
    inflación) según la inflación mensual promedio. Se cruzan en el punto de equilibrio."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=infl, y=tradicional, name="Plazo fijo tradicional", mode="lines",
                             line=dict(color="#4A8FD4", width=3)))
    fig.add_trace(go.Scatter(x=infl, y=uva, name="Plazo fijo UVA", mode="lines", line=dict(color="#F79F1F", width=3)))
    if corte is not None and infl[0] <= corte <= infl[-1]:
        fig.add_vline(x=corte, line_width=1.5, line_dash="dot", line_color="rgba(128,128,128,.8)",
                      annotation_text=f"Empate: {num(corte, 2, '%')}", annotation_position="top left",
                      annotation_font=dict(size=12), annotation_yshift=-18)  # un renglón más abajo: no se pisa con la otra
    if esperada is not None and infl[0] <= esperada <= infl[-1]:
        fig.add_vline(x=esperada, line_width=2, line_dash="dash", line_color="#F6B40E",
                      annotation_text=f"Esperada (REM): {num(esperada, 2, '%')}", annotation_position="top right",
                      annotation_font=dict(color="#F6B40E", size=12))
    fig = _base(fig, titulo, ",.0f", height)
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=70, b=45))
    fig.update_xaxes(ticksuffix="%", hoverformat=",.2f", showgrid=True,
                     gridcolor="rgba(128,128,128,.15)")
    fig.update_yaxes(tickprefix="$")
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
    # cada eje con sus propias marcas redondas (sincronizadas daban 17, 70, 124…); el color de las marcas indica a qué
    # serie corresponde cada eje, y los nombres ya están en la leyenda
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, tickformat=",~f", hoverformat=",.1f",
                                  tickmode="auto", nticks=6, rangemode="tozero", tickfont=dict(color=PALETA[1]),
                                  separatethousands=True),
                      yaxis=dict(rangemode="tozero", tickfont=dict(color=PALETA[0]), nticks=6))
    return fig
