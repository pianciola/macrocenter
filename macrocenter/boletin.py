"""Boletín semanal por mail: lo más importante de la semana en la economía argentina.

Lo arma `monitor/boletin.py` (GitHub Actions, los lunes) con las mismas fuentes públicas que la página y lo deja como
borrador en Buttondown, el servicio que guarda la lista de suscriptores. La página nunca ve ni guarda direcciones de mail.

`armar()` devuelve (asunto, cuerpo, completo): `completo` es False si faltó algún dato (entonces no se manda solo,
queda como borrador). El cuerpo es HTML simple con estilos en línea (lo que mejor se ve en los programas
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


FILAS = 9  # dólares (4), brecha, riesgo país, reservas e inflación (mensual y 12 meses)
LOGO = "https://raw.githubusercontent.com/pianciola/macrocenter/main/assets/logo_512.png"


# ───────────────────────── redacción ─────────────────────────
# El texto se arma con reglas fijas a partir de los datos (no opina ni anticipa): describe qué pasó, lo compara con la
# historia de cada serie y dice si las señales van en la misma dirección.
def _mes_anio(f: pd.Timestamp) -> str:
    return f"{MESES[f.month - 1]} de {f.year}"


def _record(df: pd.DataFrame | None, col: str, valor: float, fecha: pd.Timestamp, minimo: bool) -> str | None:
    """«el nivel más bajo desde …» / «el nivel más alto desde …» si es el extremo de al menos los últimos 6 meses."""
    if df is None or fecha is None:
        return None
    d = df.dropna(subset=[col])
    d = d[d["fecha"] < fecha - timedelta(days=7)]  # antes de esta semana (si no, el propio récord lo tapa)
    if d.empty:
        return None
    previo = d[d[col] <= valor] if minimo else d[d[col] >= valor]
    tipo = "más bajo" if minimo else "más alto"
    if previo.empty:
        return f"el nivel {tipo} desde {d['fecha'].min().year}, cuando empieza el registro"
    ultima = previo["fecha"].max()
    if (fecha - ultima).days < 180:
        return None
    return f"el nivel {tipo} desde {_mes_anio(ultima)}"


def _verbo(v: float, sube: str = "subió", baja: str = "bajó") -> str:
    return sube if v > 0 else baja


def _p(texto: str) -> str:
    return f'<p style="font-size:15px;line-height:1.6;color:#1e293b;margin:0 0 12px">{texto}</p>'


def _b(t: str) -> str:
    return f"<b>{html.escape(t)}</b>"


def _parrafo_balance(senales: list) -> str | None:
    if not senales:
        return None
    buenas, malas = senales.count(True), senales.count(False)
    palabra = ["ninguno", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
    n = lambda k: palabra[k] if k < len(palabra) else str(k)  # noqa: E731
    if buenas + malas == 0:
        return _p("<b>En pocas palabras: una semana sin grandes cambios.</b> Ninguno de los indicadores se movió de forma "
                  "apreciable.")
    if malas == 0:
        tono = "una semana positiva"
        detalle = ("El único indicador que se movió, mejoró." if buenas == 1 else
                   f"Los {n(buenas)} indicadores que se movieron mejoraron.")
    elif buenas == 0:
        tono = "una semana negativa"
        detalle = ("El único indicador que se movió, empeoró." if malas == 1 else
                   f"Los {n(malas)} indicadores que se movieron empeoraron.")
    else:
        tono = ("una semana mayormente positiva" if buenas >= 2 * malas else
                "una semana mayormente negativa" if malas >= 2 * buenas else "una semana de señales mixtas")
        detalle = (f"De los indicadores que se movieron, {n(buenas)} {'mejoró' if buenas == 1 else 'mejoraron'} y "
                   f"{n(malas)} {'empeoró' if malas == 1 else 'empeoraron'}.")
    return _p(f"<b>En pocas palabras: {tono}.</b> {detalle}")


def _parrafo_dolar(dol) -> str | None:
    of, of_a, _ = _ult_y_hace(dol, "oficial")
    bl, bl_a, _ = _ult_y_hace(dol, "blue")
    if not (of and of_a and bl and bl_a):
        return None
    v_of, v_bl = (of / of_a - 1) * 100, (bl / bl_a - 1) * 100
    p_of, p_bl = _b(charts.num(of, 0, pre="$")), _b(charts.num(bl, 0, pre="$"))
    if abs(v_of) < 0.5 and abs(v_bl) < 0.5:
        t = f"Semana tranquila en el mercado cambiario: el dólar oficial cerró en {p_of} y el blue en {p_bl}, casi sin cambios."
    else:
        t = f"El dólar oficial {_verbo(v_of)} {_b(charts.num(abs(v_of), 1, '%'))} en la semana, a {p_of}"
        if abs(v_bl) < 0.5:
            t += f", mientras que el blue casi no se movió ({p_bl})."
        elif (v_bl > 0) == (v_of > 0):
            t += f", y el blue lo acompañó: {_verbo(v_bl)} {_b(charts.num(abs(v_bl), 1, '%'))}, a {p_bl}."
        else:
            t += f", mientras que el blue fue en sentido contrario: {_verbo(v_bl)} {_b(charts.num(abs(v_bl), 1, '%'))}, a {p_bl}."
    br = (bl / of - 1) * 100
    hist = dol.dropna(subset=["oficial", "blue"])
    brechas = (hist["blue"] / hist["oficial"] - 1) * 100
    pct = float((brechas <= br).mean() * 100) if len(brechas) > 250 else 50
    desde = hist["fecha"].min().year if not hist.empty else None
    p_br = _b(charts.num(br, 1, "%"))
    if abs(br) < 3:
        t += f" La brecha entre los dos es de apenas {p_br}"
        t += f", una de las más bajas desde {desde}." if pct <= 10 and desde else "."
    elif br < 15:
        t += f" La brecha es moderada: {p_br}"
        t += (f", de las más bajas desde {desde}." if pct <= 10 and desde else
              f", de las más altas desde {desde}." if pct >= 90 and desde else ".")
    else:
        t += f" La brecha sigue alta ({p_br})"
        t += (f", aunque es de las más bajas desde {desde}." if pct <= 10 and desde else
              f", de las más altas desde {desde}." if pct >= 90 and desde else ".")
    return _p(t)


def _parrafo_externo(riesgo, reservas) -> str | None:
    partes, mejora = [], []
    rp, rp_a, f_rp = _ult_y_hace(riesgo)
    if rp is not None and rp_a is not None:
        dif = rp - rp_a
        if abs(dif) < 5:
            partes.append(f"el riesgo país se mantuvo en {_b(charts.num(rp, 0) + ' puntos')}")
        else:
            t = f"el riesgo país {_verbo(dif)} {_b(charts.num(abs(dif), 0) + ' puntos')}, a {_b(charts.num(rp, 0))}"
            r = _record(riesgo, "valor", rp, f_rp, minimo=dif < 0)
            partes.append(t + (f" ({html.escape(r)})" if r else ""))
            mejora.append(dif < 0)
    rs, rs_a, f_rs = _ult_y_hace(reservas)
    if rs is not None and rs_a is not None:
        dif = rs - rs_a
        if abs(dif) < 50:
            partes.append(f"las reservas del Banco Central quedaron estables en {_b('USD ' + charts.num(rs, 0) + ' millones')}")
        else:
            t = (f"las reservas del Banco Central {_verbo(dif, 'subieron', 'bajaron')} "
                 f"{_b('USD ' + charts.num(abs(dif), 0) + ' millones')}, a {_b('USD ' + charts.num(rs, 0) + ' millones')}")
            r = _record(reservas, "valor", rs, f_rs, minimo=dif < 0)
            partes.append(t + (f" ({html.escape(r)})" if r else ""))
            mejora.append(dif > 0)
    if not partes:
        return None
    t = "En el frente externo, " + ", y ".join(partes) + "."
    if len(mejora) == 2:
        if mejora[0] == mejora[1]:
            t += " Las dos señales van en la misma dirección: " + ("mejoran." if mejora[0] else "empeoran.")
        else:
            t += " Las dos señales van en direcciones opuestas."
    return _p(t)


def _parrafo_inflacion(infl_m, infl_ia, rem) -> str | None:
    if infl_m is None or infl_m.empty:
        return None
    d = infl_m.dropna(subset=["valor"]).sort_values("fecha")
    if len(d) < 2:
        return None
    vals = d["valor"].tolist()
    u, a, mes = vals[-1], vals[-2], d["fecha"].iloc[-1]
    t = f"El último dato de inflación es el de {MESES[mes.month - 1]}: {_b(charts.num(u, 1, '%'))}"
    if abs(u - a) < 0.05:
        t += ", igual que el mes anterior."
    else:
        sube, racha = u > a, 1
        for x, y in zip(vals[-2::-1], vals[-3::-1]):  # cuántos meses seguidos va en la misma dirección
            if abs(x - y) >= 0.05 and (x > y) == sube:
                racha += 1
            else:
                break
        t += f", {'más alta' if sube else 'más baja'} que el {charts.num(a, 1, '%')} del mes anterior"
        ordinal = {2: "segundo", 3: "tercer", 4: "cuarto", 5: "quinto", 6: "sexto"}
        if racha in ordinal:
            t += f". Es el {ordinal[racha]} mes seguido {'en alza' if sube else 'en baja'}."
        elif racha > 6:
            t += f". Ya son {racha} meses seguidos {'en alza' if sube else 'en baja'}."
        else:
            t += "."
    ia, _, _ = _ult_y_hace(infl_ia)
    esp, _, _ = _ult_y_hace(rem)
    if ia is not None and esp is not None:
        p_ia, p_esp = _b(charts.num(ia, 1, "%")), _b(charts.num(esp, 1, "%"))
        if esp < ia - 1:
            t += (f" En los últimos 12 meses los precios subieron {p_ia}, y las consultoras que releva el BCRA esperan "
                  f"que el ritmo siga bajando: proyectan {p_esp} para los próximos 12.")
        elif esp > ia + 1:
            t += (f" En los últimos 12 meses los precios subieron {p_ia}, y las consultoras que releva el BCRA esperan "
                  f"una aceleración: {p_esp} para los próximos 12.")
        else:
            t += (f" En los últimos 12 meses los precios subieron {p_ia}, y las consultoras esperan algo parecido para "
                  f"los próximos 12 ({p_esp}).")
    return _p(t)


def _redaccion(dol, riesgo, reservas, infl_m, infl_ia, rem, senales: list) -> str:
    """La lectura de la semana en párrafos. Si una parte falla o le falta su dato, se omite y el resto sigue."""
    partes = [lambda: _parrafo_balance(senales), lambda: _parrafo_dolar(dol),
              lambda: _parrafo_externo(riesgo, reservas), lambda: _parrafo_inflacion(infl_m, infl_ia, rem)]
    salida = []
    for parte in partes:
        try:
            p = parte()
        except Exception:  # noqa: BLE001
            p = None
        if p:
            salida.append(p)
    return "".join(salida)



def armar() -> tuple[str, str, bool]:
    desde = (pd.Timestamp(data.hoy_argentina()) - timedelta(days=430)).strftime("%Y-%m-%d")
    dol = _seguro(data.dolares)
    riesgo = _seguro(data.riesgo_pais)
    reservas = _seguro(lambda: data.bcra("reservas", desde="2003-01-01"))  # historia larga para los récords
    infl_m = _seguro(lambda: data.bcra("inflacion_mensual", desde=desde))
    infl_ia = _seguro(lambda: data.bcra("inflacion_interanual", desde=desde))
    rem = _seguro(lambda: data.bcra("rem_12m", desde=desde))

    filas, destacados, senales = [], [], []
    # dólares: que suba es malo
    for col, nombre in (("oficial", "Dólar oficial"), ("blue", "Dólar blue"), ("bolsa", "Dólar MEP"),
                        ("contadoconliqui", "Contado con liqui")):
        u, a, _ = _ult_y_hace(dol, col)
        if u is not None:
            # cotización: verde si sube, rojo si baja (no cuenta en el balance de buenas y malas noticias)
            cambio, bueno = _var_pct(u, a, sube_es_bueno=True)
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
        senales.append(bueno)
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
        senales.append(bueno)

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
            senales.append(None if abs(dd) < 0.05 else dd < 0)
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
        '<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="padding-right:10px">'
        f'<img src="{LOGO}" width="36" height="36" alt="MacroCenter" style="display:block;border-radius:9px"></td>'
        f'<td style="font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{CELESTE}">'
        'MacroCenter · resumen semanal</td></tr></table>'
        f'<h1 style="font-size:22px;margin:10px 0 14px">La economía argentina, semana al {html.escape(fecha)}</h1></div>'
        f'{_redaccion(dol, riesgo, reservas, infl_m, infl_ia, rem, senales)}'
        f'<h2 style="font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{GRIS};'
        'margin:24px 0 4px">Los números de la semana</h2>'
        '<p style="font-size:13px;color:#475569;margin:0 0 6px">Cambio en los últimos 7 días. En los dólares, '
        f'<span style="color:{VERDE};font-weight:700">verde</span> es que subió y '
        f'<span style="color:{ROJO};font-weight:700">rojo</span> que bajó; en el resto, verde es que mejoró y rojo que '
        'empeoró.</p>'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">'
        f'{"".join(filas)}</table>'
        f'<p style="margin:22px 0"><a href="{URL_PAGINA}" style="background:{CELESTE};color:#fff;text-decoration:none;'
        'font-weight:700;padding:10px 18px;border-radius:999px;display:inline-block">Ver todo en MacroCenter →</a></p>'
        f'<p style="font-size:12px;color:{GRIS};line-height:1.5">Datos de BCRA, INDEC y ArgentinaDatos, con el último '
        'dato publicado por cada fuente (algunos tienen días o semanas de rezago). Es información de referencia, no '
        'asesoramiento financiero.</p></div>'
    )
    completo = len(filas) == FILAS and not any(">s/d<" in f for f in filas)
    return asunto, cuerpo, completo
