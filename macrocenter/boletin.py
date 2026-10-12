"""Boletín semanal por mail: lo más importante de la semana en la economía argentina.

Lo arma `monitor/boletin.py` (GitHub Actions, los lunes) con las mismas fuentes públicas que la página y lo deja como
borrador en Buttondown, el servicio que guarda la lista de suscriptores. La página nunca ve ni guarda direcciones de mail.

`armar()` devuelve (asunto, cuerpo): el cuerpo es HTML simple con estilos en línea (lo que mejor se ve en los programas
de correo). Verde = bueno, rojo = malo, gris = sin cambios.
"""
from __future__ import annotations

import html
from datetime import timedelta

import pandas as pd

from . import charts, data

URL_PAGINA = "https://macrocenter-argentina.streamlit.app/"
VERDE, ROJO, GRIS, CELESTE = "#10AC84", "#EE5253", "#8a94a3", "#4A8FD4"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def _ult_y_hace(df: pd.DataFrame | None, col: str = "valor", dias: int = 7):
    """(último valor, valor de `dias` días antes de ese último dato, fecha del último). None donde falte."""
    if df is None or df.empty or col not in df:
        return None, None, None
    d = df.dropna(subset=[col]).sort_values("fecha")
    d = d[d["fecha"] <= pd.Timestamp(data.hoy_argentina())]
    if d.empty:
        return None, None, None
    u = d.iloc[-1]
    antes = d[d["fecha"] <= u["fecha"] - timedelta(days=dias)]
    return float(u[col]), (float(antes.iloc[-1][col]) if not antes.empty else None), u["fecha"]


def _fila(nombre: str, valor: str, cambio: str, bueno: bool | None, nota: str = "") -> str:
    color = GRIS if bueno is None else VERDE if bueno else ROJO
    esc = html.escape
    nota_html = f'<div style="font-size:12px;color:{GRIS};margin-top:2px">{esc(nota)}</div>' if nota else ""
    return (f'<tr><td style="padding:10px 0;border-bottom:1px solid #e3e8ef">'
            f'<div style="font-size:14px;color:#334155">{esc(nombre)}</div>{nota_html}</td>'
            f'<td style="padding:10px 0;border-bottom:1px solid #e3e8ef;text-align:right;font-size:16px;font-weight:700;'
            f'color:#0f172a;white-space:nowrap">{esc(valor)}</td>'
            f'<td style="padding:10px 0 10px 14px;border-bottom:1px solid #e3e8ef;text-align:right;font-size:13px;'
            f'font-weight:700;color:{color};white-space:nowrap">{esc(cambio)}</td></tr>')


def _var_pct(u: float | None, a: float | None, sube_es_bueno: bool) -> tuple[str, bool | None]:
    if u is None or a is None or not a:
        return "s/d", None
    v = (u / a - 1) * 100
    if abs(v) < 0.05:
        return "= sin cambios", None
    return f"{'▲' if v > 0 else '▼'} {charts.num(abs(v), 1, '%')}", (v > 0) == sube_es_bueno


def _seguro(fn):
    try:
        return data.limpiar(fn())
    except Exception:  # noqa: BLE001 — una fuente caída deja su fila afuera, no el boletín entero
        return None


def armar() -> tuple[str, str]:
    desde = (pd.Timestamp(data.hoy_argentina()) - timedelta(days=430)).strftime("%Y-%m-%d")
    dol = _seguro(data.dolares)
    riesgo = _seguro(data.riesgo_pais)
    reservas = _seguro(lambda: data.bcra("reservas", desde=desde))
    infl_m = _seguro(lambda: data.bcra("inflacion_mensual", desde=desde))
    infl_ia = _seguro(lambda: data.bcra("inflacion_interanual", desde=desde))
    rem = _seguro(lambda: data.bcra("rem_12m", desde=desde))

    filas, destacados = [], []
    # dólares: que suba es malo
    for col, nombre in (("oficial", "Dólar oficial"), ("blue", "Dólar blue"), ("bolsa", "Dólar MEP"),
                        ("contadoconliqui", "Contado con liqui")):
        u, a, _ = _ult_y_hace(dol, col)
        if u is not None:
            cambio, bueno = _var_pct(u, a, sube_es_bueno=False)
            filas.append(_fila(nombre, charts.num(u, 0, pre="$"), cambio, bueno))
            if col == "oficial":
                destacados.append(f"dólar {charts.num(u, 0, pre='$')}")
    of, of_a, _ = _ult_y_hace(dol, "oficial")
    bl, bl_a, _ = _ult_y_hace(dol, "blue")
    if of and bl:
        br = (bl / of - 1) * 100
        br_a = (bl_a / of_a - 1) * 100 if of_a and bl_a else None
        if br_a is None:
            cambio, bueno = "s/d", None
        elif abs(br - br_a) < 0.05:
            cambio, bueno = "= sin cambios", None
        else:
            cambio, bueno = f"{'▲' if br > br_a else '▼'} {charts.num(abs(br - br_a), 1)} pp", br < br_a
        filas.append(_fila("Brecha blue / oficial", charts.num(br, 1, "%"), cambio, bueno))

    u, a, _ = _ult_y_hace(riesgo)
    if u is not None:
        if a is None:
            cambio, bueno = "s/d", None
        elif abs(u - a) < 1:
            cambio, bueno = "= sin cambios", None
        else:
            cambio, bueno = f"{'▲' if u > a else '▼'} {charts.num(abs(u - a), 0)} pb", u < a
        filas.append(_fila("Riesgo país", f"{charts.num(u, 0)} pb", cambio, bueno))
        destacados.append(f"riesgo país {charts.num(u, 0)}")

    u, a, f = _ult_y_hace(reservas)
    if u is not None:
        if a is None:
            cambio, bueno = "s/d", None
        elif abs(u - a) < 1:
            cambio, bueno = "= sin cambios", None
        else:
            cambio, bueno = f"{'▲' if u > a else '▼'} USD {charts.num(abs(u - a), 0)} M", u > a
        filas.append(_fila("Reservas del BCRA", f"USD {charts.num(u, 0)} M", cambio, bueno,
                           f"dato al {f:%d/%m}" if f is not None else ""))

    # inflación: dato mensual, se compara con el mes anterior
    if infl_m is not None and not infl_m.empty:
        d = infl_m.dropna(subset=["valor"]).sort_values("fecha")
        if len(d) >= 2:
            ult, ant = d.iloc[-1], d.iloc[-2]
            dd = float(ult["valor"] - ant["valor"])
            cambio = "= igual" if abs(dd) < 0.05 else f"{'▲' if dd > 0 else '▼'} {charts.num(abs(dd), 1)} pp"
            filas.append(_fila(f"Inflación de {MESES[ult['fecha'].month - 1]}", charts.num(ult["valor"], 1, "%"),
                               cambio, None if abs(dd) < 0.05 else dd < 0,
                               f"frente a {MESES[ant['fecha'].month - 1]} ({charts.num(ant['valor'], 1, '%')})"))
    u, _, _ = _ult_y_hace(infl_ia)
    esp, _, _ = _ult_y_hace(rem)
    if u is not None:
        filas.append(_fila("Inflación de los últimos 12 meses", charts.num(u, 1, "%"), "", None,
                           f"las consultoras esperan {charts.num(esp, 1, '%')} para los próximos 12 (REM)"
                           if esp is not None else ""))

    if not filas:
        raise RuntimeError("no se pudo bajar ningún dato: no se arma el boletín")

    hoy = pd.Timestamp(data.hoy_argentina())
    fecha = f"{hoy.day} de {MESES[hoy.month - 1]}"
    asunto = f"MacroCenter · Semana al {fecha}" + (f": {', '.join(destacados)}" if destacados else "")
    cuerpo = (
        '<div style="font-family:Helvetica,Arial,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">'
        f'<div style="border-top:4px solid {CELESTE};padding-top:14px">'
        f'<div style="font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{CELESTE}">'
        'MacroCenter · resumen semanal</div>'
        f'<h1 style="font-size:22px;margin:6px 0 4px">La economía argentina, semana al {html.escape(fecha)}</h1>'
        f'<p style="font-size:14px;color:#475569;margin:0 0 14px">Los datos clave y cómo cambiaron en los últimos 7 días. '
        f'<span style="color:{VERDE};font-weight:700">Verde</span>: mejoró · '
        f'<span style="color:{ROJO};font-weight:700">rojo</span>: empeoró.</p></div>'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">'
        f'{"".join(filas)}</table>'
        f'<p style="margin:22px 0"><a href="{URL_PAGINA}" style="background:{CELESTE};color:#fff;text-decoration:none;'
        'font-weight:700;padding:10px 18px;border-radius:999px;display:inline-block">Ver todo en MacroCenter →</a></p>'
        f'<p style="font-size:12px;color:{GRIS};line-height:1.5">Datos de BCRA, INDEC y ArgentinaDatos, con el último '
        'dato publicado por cada fuente (algunos tienen días o semanas de rezago). Es información de referencia, no '
        'asesoramiento financiero.</p></div>'
    )
    return asunto, cuerpo
