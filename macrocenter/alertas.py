"""Alertas por mail: avisan cuando el dólar o el riesgo país se mueven fuerte en el día.

Las arma monitor/alertas.py (GitHub Actions, cada 30 minutos en horario de mercado) y las manda Buttondown solo a
quienes se anotaron con la etiqueta «alertas» (formulario en el pie de la página). Acá está la parte que decide y
redacta, sin red ni claves, para poder probarla.

Textos neutros: dicen cuánto y hacia dónde se movió algo, sin calificarlo.
"""
from __future__ import annotations

import html

import pandas as pd

ETIQUETA = "alertas"

# (clave, nombre, umbral en %): cuánto tiene que moverse contra el cierre anterior para avisar
INSTRUMENTOS = [
    ("oficial", "Dólar oficial", 2.0),
    ("blue", "Dólar blue", 3.0),
    ("bolsa", "Dólar MEP", 3.0),
    ("contadoconliqui", "Dólar CCL", 3.0),
    ("riesgo", "Riesgo país", 5.0),
]


def _num(x: float, dec: int = 0) -> str:
    s = f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return s


def _cierre_anterior(serie: pd.DataFrame, col: str, hoy: pd.Timestamp) -> float | None:
    """Último valor de un día anterior a hoy (el cierre de la rueda previa)."""
    if serie is None or col not in serie:
        return None
    d = serie[pd.to_datetime(serie["fecha"]).dt.normalize() < hoy].dropna(subset=[col])
    return None if d.empty else float(d[col].iloc[-1])


def detectar(ahora_dol: pd.DataFrame | None, hist_dol: pd.DataFrame | None, riesgo_ahora: pd.DataFrame | None,
             hist_riesgo: pd.DataFrame | None, hoy: pd.Timestamp) -> list[dict]:
    """Los instrumentos que hoy se movieron más que su umbral: [{clave, nombre, antes, ahora, var}].
    Solo cuenta un dato del día de hoy (un dato viejo de una fuente atrasada no dispara nada)."""
    hoy = pd.Timestamp(hoy).normalize()
    actuales: dict[str, float] = {}
    if ahora_dol is not None and not ahora_dol.empty:
        for _, r in ahora_dol.iterrows():
            if pd.Timestamp(r["actualizado"]).normalize() == hoy and pd.notna(r["venta"]):
                actuales[str(r["casa"])] = float(r["venta"])
    if riesgo_ahora is not None and not riesgo_ahora.empty:
        u = riesgo_ahora.iloc[-1]
        if pd.Timestamp(u["fecha"]).normalize() == hoy:
            actuales["riesgo"] = float(u["valor"])
    out = []
    for clave, nombre, umbral in INSTRUMENTOS:
        if clave not in actuales:
            continue
        antes = (_cierre_anterior(hist_riesgo, "valor", hoy) if clave == "riesgo"
                 else _cierre_anterior(hist_dol, clave, hoy))
        if not antes:
            continue
        var = (actuales[clave] / antes - 1) * 100
        if abs(var) >= umbral:
            out.append(dict(clave=clave, nombre=nombre, antes=antes, ahora=actuales[clave], var=var))
    return out


def frase(a: dict) -> str:
    sube = a["var"] > 0
    if a["clave"] == "riesgo":
        valor = lambda v: f"{_num(v)} puntos"  # noqa: E731
    else:
        valor = lambda v: f"${_num(v, 2 if v < 100 else 0)}"  # noqa: E731
    return (f"{a['nombre']}: {'subió' if sube else 'bajó'} {_num(abs(a['var']), 1)}% respecto del cierre anterior, "
            f"de {valor(a['antes'])} a {valor(a['ahora'])}.")


def asunto(alertas: list[dict], hoy: pd.Timestamp) -> str:
    nombres = ", ".join(a["nombre"] for a in alertas)
    return f"Alerta MacroCenter {pd.Timestamp(hoy):%d/%m}: {nombres}"


def cuerpo(alertas: list[dict], hora: str, url: str) -> str:
    items = "".join(f"<li>{html.escape(frase(a))}</li>" for a in alertas)
    return (f"<p>Movimientos fuertes del día, a las {html.escape(hora)} (hora de Argentina):</p><ul>{items}</ul>"
            f'<p><a href="{html.escape(url)}">Ver el tablero del dólar</a></p>'
            "<p style=\"color:#888;font-size:12px\">Te llega porque te anotaste en las alertas de MacroCenter. Se avisa "
            "cuando el dólar oficial se mueve 2% o más en el día, el blue, el MEP o el CCL 3% o más, o el riesgo país 5% "
            "o más. Es información, no una recomendación.</p>")


def ya_avisadas(asuntos_previos: list[str], hoy: pd.Timestamp) -> set[str]:
    """Nombres ya avisados hoy (según los asuntos de los mails mandados): cada instrumento se avisa una vez por día."""
    prefijo = f"Alerta MacroCenter {pd.Timestamp(hoy):%d/%m}: "
    out: set[str] = set()
    for s in asuntos_previos:
        if s.startswith(prefijo):
            out |= {n.strip() for n in s[len(prefijo):].split(",")}
    return out
