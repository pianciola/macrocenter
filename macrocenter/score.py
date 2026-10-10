"""Calificación de la situación macro.

Cada driver recibe un puntaje de 0 a 100: qué tan favorable es su valor en una fecha `t` comparado con su
propia historia de los últimos `ANIOS` años (percentil, invertido si "menos es mejor"). Los drivers se
promedian por pilar y los pilares se promedian en la nota total. Como el cálculo se puede hacer "a la fecha t"
para cualquier t, la nota de hoy se compara con la de hace 3 meses, 1 año, 2 años, etc.

Es un indicador descriptivo y relativo (mejor/peor que el pasado reciente), no un pronóstico ni una
calificación crediticia.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

ANIOS = 5
MIN_OBS = 8


@dataclass(frozen=True)
class Driver:
    clave: str
    nombre: str
    pilar: str
    mejor: str  # "alto" o "bajo"
    unidad: str = ""
    dec: int = 1


DRIVERS = [
    Driver("infl_m", "Inflación mensual", "Precios", "bajo", "%"),
    Driver("rem", "Inflación esperada 12 m (REM)", "Precios", "bajo", "%"),
    Driver("reservas", "Reservas brutas", "Externo", "alto", " USD M", 0),
    Driver("riesgo", "Riesgo país", "Externo", "bajo", " pb", 0),
    Driver("brecha", "Brecha cambiaria blue/oficial", "Externo", "bajo", "%"),
    Driver("saldo12", "Saldo comercial 12 m", "Externo", "alto", " USD M", 0),
    Driver("emae", "EMAE interanual", "Actividad", "alto", "%"),
    Driver("paro", "Desocupación", "Actividad", "bajo", "%"),
    Driver("salario_real", "Salario real interanual", "Ingresos", "alto", "%"),
]
PILARES = list(dict.fromkeys(d.pilar for d in DRIVERS))

# Las etiquetas son relativas a propósito: la nota compara contra el pasado reciente, no dice si algo es "bueno".
NIVELES = [  # (puntaje mínimo, etiqueta, color)
    (75, "Mucho mejor que lo reciente", "#10AC84"),
    (60, "Mejor que lo reciente", "#7BC96F"),
    (40, "Similar a lo reciente", "#F79F1F"),
    (25, "Peor que lo reciente", "#EE7752"),
    (0, "Mucho peor que lo reciente", "#EE5253"),
]


def nivel(puntaje: float) -> tuple[str, str]:
    for minimo, etiqueta, color in NIVELES:
        if puntaje >= minimo:
            return etiqueta, color
    return NIVELES[-1][1], NIVELES[-1][2]


def valor_en(s: pd.Series, t: pd.Timestamp) -> float | None:
    """Último dato disponible a la fecha t."""
    v = s[s.index <= t].dropna()
    return None if v.empty else float(v.iloc[-1])


def puntaje_driver(s: pd.Series, t: pd.Timestamp, mejor: str, anios: int = ANIOS) -> float | None:
    if s.empty or not isinstance(s.index, pd.DatetimeIndex):
        return None
    ventana = s[(s.index <= t) & (s.index > t - pd.DateOffset(years=anios))].dropna()
    if len(ventana) < MIN_OBS:
        return None
    actual = ventana.iloc[-1]
    p = ((ventana < actual).sum() + 0.5 * (ventana == actual).sum()) / len(ventana) * 100
    return float(p if mejor == "alto" else 100 - p)


def calificar(series: dict[str, pd.Series], t: pd.Timestamp, anios: int = ANIOS,
              pesos: dict[str, float] | None = None) -> dict:
    """Devuelve {'total': float|None, 'pilares': {pilar: float}, 'drivers': {clave: float}} a la fecha t.
    `anios`: cuántos años hacia atrás se compara cada indicador. `pesos`: peso de cada pilar en la nota total
    (por defecto, todos iguales; se normalizan solos y los pilares sin datos no cuentan)."""
    drivers = {}
    for d in DRIVERS:
        if d.clave in series:
            p = puntaje_driver(series[d.clave], t, d.mejor, anios)
            if p is not None:
                drivers[d.clave] = p
    pilares = {}
    for pilar in PILARES:
        ps = [drivers[d.clave] for d in DRIVERS if d.pilar == pilar and d.clave in drivers]
        if ps:
            pilares[pilar] = sum(ps) / len(ps)
    total = None
    if pilares:
        w = {p: max(float((pesos or {}).get(p, 1.0)), 0.0) for p in pilares}
        if sum(w.values()) <= 0:
            w = {p: 1.0 for p in pilares}
        total = sum(pilares[p] * w[p] for p in pilares) / sum(w.values())
    return {"total": total, "pilares": pilares, "drivers": drivers}


def etiqueta_driver(puntaje: float) -> str:
    """Lectura en palabras de un puntaje individual."""
    return ("Mucho mejor que lo reciente" if puntaje >= 80 else "Mejor que lo reciente" if puntaje >= 60
            else "Similar a lo reciente" if puntaje >= 40 else "Peor que lo reciente" if puntaje >= 20
            else "Mucho peor que lo reciente")


def frase_driver(driver: Driver, valor: str, puntaje: float, anios: int = ANIOS) -> str:
    """Una oración concreta: qué vale hoy y cuánto mejor (o peor) es que el pasado reciente."""
    mejores = round(puntaje)
    if driver.mejor == "bajo":
        comparacion = f"es más bajo que en el {mejores}% de los últimos {anios} años (y menos es mejor)"
    else:
        comparacion = f"es más alto que en el {mejores}% de los últimos {anios} años (y más es mejor)"
    return f"**{driver.nombre}:** {valor}; {comparacion}."


def historia(series: dict[str, pd.Series], hasta: pd.Timestamp, meses: int = 60, anios: int = ANIOS,
             pesos: dict[str, float] | None = None) -> pd.DataFrame:
    """Nota total y por pilar a fin de cada mes, para los últimos `meses` meses."""
    filas = []
    for t in pd.date_range(end=hasta, periods=meses, freq="ME"):
        r = calificar(series, t, anios, pesos)
        if r["total"] is not None:
            filas.append({"fecha": t, "Total": r["total"], **r["pilares"]})
    return pd.DataFrame(filas)


def lectura(hoy: dict, antes: dict, nombre_antes: str) -> str:
    """Texto breve que resume la situación y la compara con un período anterior."""
    if hoy["total"] is None:
        return "No hay datos suficientes para calificar."
    etiqueta, _ = nivel(hoy["total"])
    texto = f"La situación macro hoy está **{etiqueta.lower()}** ({hoy['total']:.0f}/100)"
    if antes["total"] is not None:
        dif = hoy["total"] - antes["total"]
        if abs(dif) < 2:
            texto += f", prácticamente igual que {nombre_antes} ({antes['total']:.0f})."
        else:
            texto += f", {'mejor' if dif > 0 else 'peor'} que {nombre_antes} ({antes['total']:.0f}, {dif:+.0f} pts)."
    else:
        texto += "."
    nombres = {d.clave: d.nombre for d in DRIVERS}
    if hoy["drivers"]:
        orden = sorted(hoy["drivers"].items(), key=lambda kv: kv[1])
        texto += (f" Lo más fuerte: **{nombres[orden[-1][0]]}** ({orden[-1][1]:.0f}). "
                  f"Lo más débil: **{nombres[orden[0][0]]}** ({orden[0][1]:.0f}).")
    return texto
