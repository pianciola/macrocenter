"""Cómo recibió y cómo dejó la economía cada presidente desde la vuelta de la democracia (1983).

Los números se calculan con las series reales (no hay valores escritos a mano); lo único fijo son las fechas de
cada mandato, un hito conocido y el título de la nota de Wikipedia para la foto.

Criterios (importan para leer bien los números):
  - Inflación anual: variación de los 12 meses previos al último mes completo antes de asumir / al irse.
    Entre 2007 y 2015 son las cifras oficiales del INDEC intervenido, que distintos analistas consideran subestimadas.
  - PBI: crecimiento acumulado en el mandato, comparando el PBI de los 4 trimestres previos a asumir con el de los
    4 trimestres previos a irse. Empalme de tres series oficiales (base 1986, 1993 y 2004).
  - Desocupación: dato anual EPH (en mandatos que empiezan antes de noviembre se usa el año anterior).
  - Dólar: oficial, solo desde 1992; antes las series están en monedas de cada época (peso argentino, austral) y
    con tramos congelados, así que no se calcula.
  - Reservas: brutas del BCRA, saldo de fin de mes.
  - Riesgo país: disponible desde 1999.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

HOY = pd.Timestamp.today().normalize()


@dataclass(frozen=True)
class Mandato:
    clave: str
    nombre: str
    desde: pd.Timestamp
    hasta: pd.Timestamp | None  # None = en ejercicio
    wiki: str  # título del artículo en es.wikipedia.org (de ahí sale la foto)
    hito: str
    nota: str = ""

    @property
    def fin(self) -> pd.Timestamp:
        return self.hasta or HOY

    @property
    def periodo(self) -> str:
        return f"{self.desde.year} – {self.hasta.year if self.hasta else 'hoy'}"


MANDATOS = [
    Mandato("alfonsin", "Raúl Alfonsín", pd.Timestamp("1983-12-10"), pd.Timestamp("1989-07-08"), "Raúl Alfonsín",
            "Primer presidente tras la dictadura. Lanzó el Plan Austral y entregó el mando antes de tiempo, "
            "en plena hiperinflación."),
    Mandato("menem", "Carlos Menem", pd.Timestamp("1989-07-08"), pd.Timestamp("1999-12-10"), "Carlos Menem",
            "Convertibilidad 1 a 1, privatizaciones y estabilidad de precios… hasta que el modelo se agotó."),
    Mandato("delarua", "Fernando de la Rúa", pd.Timestamp("1999-12-10"), pd.Timestamp("2001-12-20"),
            "Fernando de la Rúa", "Heredó la convertibilidad en recesión; terminó con el corralito y la renuncia "
            "en diciembre de 2001."),
    Mandato("duhalde", "Eduardo Duhalde", pd.Timestamp("2002-01-01"), pd.Timestamp("2003-05-25"), "Eduardo Duhalde",
            "Asumió tras una semana con cinco presidentes. Salió de la convertibilidad: devaluación y pesificación.",
            "Antes de él pasaron brevemente Ramón Puerta, Adolfo Rodríguez Saá y Eduardo Camaño."),
    Mandato("kirchner", "Néstor Kirchner", pd.Timestamp("2003-05-25"), pd.Timestamp("2007-12-10"), "Néstor Kirchner",
            "Rebote tras la crisis, canje de la deuda en default y cancelación de la deuda con el FMI."),
    Mandato("cfk", "Cristina Fernández de Kirchner", pd.Timestamp("2007-12-10"), pd.Timestamp("2015-12-10"),
            "Cristina Fernández de Kirchner",
            "Dos mandatos: estatización de las AFJP, cepo cambiario desde 2011 y estancamiento al final."),
    Mandato("macri", "Mauricio Macri", pd.Timestamp("2015-12-10"), pd.Timestamp("2019-12-10"), "Mauricio Macri",
            "Levantó el cepo en el primer día, volvió a los mercados de deuda y firmó un acuerdo récord con el FMI."),
    Mandato("fernandez", "Alberto Fernández", pd.Timestamp("2019-12-10"), pd.Timestamp("2023-12-10"),
            "Alberto Fernández", "Pandemia, renegociación de la deuda y una inflación que se fue acelerando."),
    Mandato("milei", "Javier Milei", pd.Timestamp("2023-12-10"), None, "Javier Milei",
            "Devaluación inicial, ajuste fiscal y el intento de bajar la inflación desde un punto de partida muy alto."),
]


# Hitos económicos, solo hechos con fecha (sin juicio de valor): (fecha, rótulo corto)
EVENTOS = [
    (pd.Timestamp("1985-06-14"), "Plan Austral"),
    (pd.Timestamp("1989-05-01"), "Hiperinflación"),
    (pd.Timestamp("1991-04-01"), "Convertibilidad"),
    (pd.Timestamp("1994-12-20"), "Efecto Tequila"),
    (pd.Timestamp("2001-12-03"), "Corralito"),
    (pd.Timestamp("2002-01-06"), "Fin de la convertibilidad"),
    (pd.Timestamp("2005-03-18"), "Canje de deuda"),
    (pd.Timestamp("2011-10-28"), "Cepo cambiario"),
    (pd.Timestamp("2015-12-16"), "Fin del cepo"),
    (pd.Timestamp("2018-06-20"), "Acuerdo con el FMI"),
    (pd.Timestamp("2019-09-01"), "Cepo (restablecido)"),
    (pd.Timestamp("2020-03-20"), "Pandemia"),
    (pd.Timestamp("2023-12-12"), "Devaluación"),
]

# Comparación entre mandatos: (nombre visible, clave en `indicadores`, formato de la unidad, texto de ayuda)
COMPARACIONES = {
    "Inflación anual al irse": ("inf_fin", "%", "Inflación de los 12 meses previos al fin del mandato (o al último dato)."),
    "Inflación acumulada": ("inf_acum", "%", "Suba total de precios durante todo el mandato."),
    "PBI en el mandato": ("pbi", "%", "Crecimiento acumulado del PBI real entre el inicio y el final del mandato."),
    "Desocupación al irse": ("paro_fin", "%", "Tasa de desocupación (EPH) al final del mandato."),
    "Dólar: veces que se multiplicó": ("usd_mult", "×", "Dólar oficial al irse dividido el dólar al asumir (desde 1992)."),
    "Reservas al irse (USD M)": ("res_fin", "", "Reservas brutas del BCRA al final del mandato."),
}

CORTO = {"alfonsin": "Alfonsín", "menem": "Menem", "delarua": "De la Rúa", "duhalde": "Duhalde",
         "kirchner": "N. Kirchner", "cfk": "CFK", "macri": "Macri", "fernandez": "A. Fernández", "milei": "Milei"}


def inflacion_anual_serie(inf: pd.DataFrame) -> pd.DataFrame:
    """Inflación de los 12 meses que terminan en cada mes (%), para el gráfico panorámico."""
    d = inf.copy()
    d["valor"] = ((1 + d["valor"] / 100).rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100
    return d.dropna()


GRAFICOS = ["Inflación", "Dólar", "PBI", "Desocupación", "Reservas", "Riesgo país"]  # el primero es el predeterminado


def grafico_historico(nombre: str, dp: dict) -> tuple[pd.DataFrame, dict]:
    """Serie (fecha, valor) y opciones de `charts.serie_presidentes` para cada gráfico del selector."""
    if nombre == "Dólar":
        a = dp["dolar_actual"]
        df = pd.concat([dp["dolar_hist"][dp["dolar_hist"]["fecha"] < a["fecha"].min()], a]).sort_values("fecha")
        return df, dict(titulo="Dólar oficial en pesos, desde 1992 (escala logarítmica)", log=True,
                        ticks=([1, 10, 100, 1000], ["$1", "$10", "$100", "$1.000"]), color="#2E86DE")
    if nombre == "PBI":
        s = dp["pbi"]
        df = ((s / s.shift(4) - 1) * 100).dropna().rename("valor").rename_axis("fecha").reset_index()
        return df, dict(titulo="Crecimiento anual del PBI real (%)", yfmt=",.0f", cero=True, color="#10AC84")
    if nombre == "Desocupación":
        a = dp["paro_anual"]
        return a.assign(valor=a["valor"] * 100), dict(titulo="Desocupación (%, EPH anual)", yfmt=",.0f", color="#8E44AD")
    if nombre == "Reservas":
        h, r = dp["reservas_hist"], dp["reservas_actual"]
        df = pd.concat([h[h["fecha"] < r["fecha"].min()], r]).sort_values("fecha")
        return df, dict(titulo="Reservas brutas del BCRA (USD millones)", yfmt=",.0f", color="#F79F1F")
    if nombre == "Riesgo país":
        return dp["riesgo"], dict(titulo="Riesgo país (puntos básicos)", yfmt=",.0f", color="#EE5253")
    anual = inflacion_anual_serie(dp["inflacion"])
    return anual, dict(titulo="Inflación anual desde 1983 (escala logarítmica)", log=True, minimo_log=1,
                       ticks=([1, 10, 100, 1000, 10000], ["1%", "10%", "100%", "1.000%", "10.000%"]))


# ───────────────────────── cálculos por serie ─────────────────────────
def _antes(df: pd.DataFrame, fecha: pd.Timestamp, col: str = "valor") -> float | None:
    """Último dato con fecha <= `fecha`."""
    d = df[df["fecha"] <= fecha].dropna(subset=[col])
    return None if d.empty else float(d.iloc[-1][col])


def _mes_previo(df: pd.DataFrame, fecha: pd.Timestamp, col: str = "valor") -> float | None:
    """Dato mensual del mes anterior al de `fecha` (series con fecha = primer día del mes, saldo a fin de mes)."""
    d = df[df["fecha"] < fecha.replace(day=1)].dropna(subset=[col])
    return None if d.empty else float(d.iloc[-1][col])


def inflacion_12m(inf: pd.DataFrame, fecha: pd.Timestamp) -> float | None:
    """Inflación de los 12 meses que terminan en el último mes completo antes de `fecha` (en %)."""
    d = inf[inf["fecha"] < fecha].tail(12)
    if len(d) < 12:
        return None
    return float(((1 + d["valor"] / 100).prod() - 1) * 100)


def inflacion_mandato(inf: pd.DataFrame, m: Mandato) -> tuple[float | None, tuple[pd.Timestamp, float] | None]:
    """(inflación acumulada en el mandato en %, (mes, valor) del pico mensual). Un mes cuenta para quien
    estaba en el cargo a fin de ese mes."""
    d = inf[(inf["fecha"] >= m.desde) & (inf["fecha"] < m.fin)]
    if d.empty:
        return None, None
    pico = d.loc[d["valor"].idxmax()]
    return float(((1 + d["valor"] / 100).prod() - 1) * 100), (pico["fecha"], float(pico["valor"]))


def pbi_empalmado(s86: pd.DataFrame, s93: pd.DataFrame, s04: pd.DataFrame) -> pd.Series:
    """PBI real de los últimos 4 trimestres, empalmando las tres series oficiales. Índice = fin del trimestre."""
    def t4(df: pd.DataFrame) -> pd.Series:
        s = df.set_index("fecha")["valor"].sort_index().rolling(4).sum().dropna()
        s.index = s.index + pd.offsets.QuarterEnd(0)  # inicio de trimestre -> fin de trimestre
        return s

    a, b, c = t4(s86), t4(s93), t4(s04)
    q1, q2 = pd.Timestamp("1996-12-31"), pd.Timestamp("2010-12-31")
    b = b * (a.loc[q1] / b.loc[q1])
    c = c * (b.loc[q2] / c.loc[q2])
    return pd.concat([a[a.index <= q1], b[(b.index > q1) & (b.index <= q2)], c[c.index > q2]])


def pbi_mandato(pbi: pd.Series, m: Mandato) -> float | None:
    ini = pbi[pbi.index <= m.desde]
    fin = pbi[pbi.index <= m.fin]
    if ini.empty or fin.empty:
        return None
    return float((fin.iloc[-1] / ini.iloc[-1] - 1) * 100)


def _anio_ref(fecha: pd.Timestamp) -> int:
    """Año del dato anual a usar: el mismo año si la fecha es de noviembre/diciembre, si no, el anterior."""
    return fecha.year if fecha.month >= 11 else fecha.year - 1


def desocupacion(anual: pd.DataFrame, trimestral: pd.DataFrame | None, m: Mandato) -> tuple[float | None, float | None]:
    def anio(y: int) -> float | None:
        d = anual[anual["fecha"].dt.year == y]
        return None if d.empty else float(d.iloc[-1]["valor"]) * 100

    ini = anio(_anio_ref(m.desde))
    if m.hasta is None and trimestral is not None and not trimestral.empty:
        fin = float(trimestral.iloc[-1]["valor"]) * 100
    else:
        fin = anio(_anio_ref(m.fin))
    return ini, fin


def dolar_oficial(hist: pd.DataFrame, actual: pd.DataFrame, fecha: pd.Timestamp) -> float | None:
    """Dólar oficial: serie del BCRA hasta 2010 y ArgentinaDatos desde 2011. Solo desde 1992."""
    if fecha < pd.Timestamp("1992-01-02"):
        return None
    base = actual if fecha >= actual["fecha"].min() else hist
    return _antes(base, fecha)


def _host_ok(url: str, hosts: tuple[str, ...]) -> bool:
    from urllib.parse import urlparse

    try:
        p = urlparse(url)
        return p.scheme == "https" and (p.hostname or "") in hosts
    except ValueError:
        return False


def fotos() -> dict[str, dict]:
    """Foto y página de Wikipedia de cada presidente, pedidas a la API de es.wikipedia.org en el momento.
    Las imágenes se alojan en Wikimedia Commons (licencias libres); no se guardan en el proyecto.
    Devuelve {} si no hay conexión: las tarjetas se muestran igual, con las iniciales."""
    import requests

    try:
        r = requests.get(
            "https://es.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "prop": "pageimages|info", "inprop": "url",
                    "pithumbsize": 400, "redirects": 1, "titles": "|".join(m.wiki for m in MANDATOS)},
            headers={"User-Agent": "MacroCenter/1.0 (tablero personal)"}, timeout=30,
        ).json()["query"]
        redirigido = {x["from"]: x["to"] for x in r.get("redirects", []) + r.get("normalized", [])}
        paginas = {p["title"]: p for p in r["pages"].values()}
        out = {}
        for m in MANDATOS:
            p = paginas.get(redirigido.get(m.wiki, m.wiki))
            foto = ((p or {}).get("thumbnail") or {}).get("source", "")
            if foto and _host_ok(foto, ("upload.wikimedia.org", "thumb.wikimedia.org")):  # nunca otra cosa que Wikimedia
                pagina = p.get("fullurl", "")
                out[m.clave] = {"url": foto, "pagina": pagina if _host_ok(pagina, ("es.wikipedia.org",)) else ""}
        return out
    except Exception:  # noqa: BLE001
        return {}


# ───────────────────────── formato ─────────────────────────
def _n(x: float | None, dec: int = 0, pre: str = "", suf: str = "") -> str:
    if x is None:
        return "s/d"
    s = f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{pre}{s}{suf}"


def _pct(x: float | None) -> str:
    return _n(x, 0 if x is not None and abs(x) >= 100 else 1, suf="%")


def _tendencia(ini: float | None, fin: float | None, mejor: str) -> str:
    """'mejor' / 'peor' / '' según si el cambio fue en la dirección buena (mejor='bajo' o 'alto')."""
    if ini is None or fin is None or abs(fin - ini) < 1e-9:
        return ""
    bajo = fin < ini
    return "mejor" if bajo == (mejor == "bajo") else "peor"


def filas(m: Mandato, i: dict) -> list[dict]:
    """Filas de la tarjeta: [{'k': etiqueta, 'ini': texto, 'fin': texto, 'tend': ''|'mejor'|'peor'}]."""
    usd = ""
    if i["usd_ini"] and i["usd_fin"]:
        usd = f" (×{_n(i['usd_fin'] / i['usd_ini'], 1)})"
    pbi = i["pbi"]
    return [
        {"k": "Inflación anual", "ini": _pct(i["inf_ini"]), "fin": _pct(i["inf_fin"]),
         "tend": _tendencia(i["inf_ini"], i["inf_fin"], "bajo")},
        {"k": "PBI en el mandato", "ini": "", "fin": ("+" if pbi and pbi > 0 else "") + _pct(pbi),
         "tend": "" if pbi is None else ("mejor" if pbi > 0 else "peor")},
        {"k": "Desocupación", "ini": _pct(i["paro_ini"]), "fin": _pct(i["paro_fin"]),
         "tend": _tendencia(i["paro_ini"], i["paro_fin"], "bajo")},
        {"k": "Dólar oficial", "ini": _n(i["usd_ini"], 2, "$") if i["usd_ini"] else "s/d",
         "fin": (_n(i["usd_fin"], 2, "$") if i["usd_fin"] else "s/d") + usd, "tend": ""},
        {"k": "Reservas (USD M)", "ini": _n(i["res_ini"]), "fin": _n(i["res_fin"]),
         "tend": _tendencia(i["res_ini"], i["res_fin"], "alto")},
        {"k": "Riesgo país", "ini": _n(i["rp_ini"]), "fin": _n(i["rp_fin"]),
         "tend": _tendencia(i["rp_ini"], i["rp_fin"], "bajo")},
    ]


def pico_texto(m: Mandato, i: dict) -> str:
    if not i["inf_pico"]:
        return ""
    mes, v = i["inf_pico"]
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    # caso discutible: el mes de la asunción. Se aclara el criterio en la propia tarjeta.
    primer = (" · su primer mes: cada mes se asigna a quien gobernaba al cierre, aunque la suba se haya gestado antes"
              if (mes.year, mes.month) == (m.desde.year, m.desde.month) else "")
    return f"Pico de inflación mensual: {_pct(v)} ({meses[mes.month - 1]}-{mes.year}{primer})"


def indicadores(m: Mandato, d: dict) -> dict:
    """Todos los datos de un mandato. `d` trae las series ya cargadas (claves en app.py)."""
    inf, pbi = d["inflacion"], d["pbi"]
    out: dict = {}
    out["inf_ini"], out["inf_fin"] = inflacion_12m(inf, m.desde), inflacion_12m(inf, m.fin)
    out["inf_acum"], out["inf_pico"] = inflacion_mandato(inf, m)
    out["pbi"] = pbi_mandato(pbi, m)
    out["paro_ini"], out["paro_fin"] = desocupacion(d["paro_anual"], d.get("paro_trim"), m)
    out["usd_ini"] = dolar_oficial(d["dolar_hist"], d["dolar_actual"], m.desde)
    out["usd_fin"] = dolar_oficial(d["dolar_hist"], d["dolar_actual"], m.fin)
    out["res_ini"] = _mes_previo(d["reservas_hist"], m.desde)
    out["res_fin"] = _antes(d["reservas_actual"], m.fin) if m.hasta is None else _mes_previo(d["reservas_hist"], m.fin)
    rp = d["riesgo"]
    ini, fin = _antes(rp, m.desde), _antes(rp, m.fin)
    out["rp_ini"] = ini if m.desde >= rp["fecha"].min() else None
    out["rp_fin"] = fin if m.fin >= rp["fecha"].min() else None
    return out
