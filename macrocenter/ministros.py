"""Ministros de Economía desde la vuelta de la democracia (1983).

Fechas: listado oficial del Centro de Documentación e Información del Ministerio de Economía
(cdi.mecon.gob.ar/ministros-de-economia). Los hitos son hechos con fecha, redactados sin calificativos; los números de
cada gestión (inflación, dólar, reservas) no están escritos a mano: se calculan con las mismas series oficiales que usa
la línea de tiempo de presidentes.

Criterios:
  - Un mes de inflación cuenta para quien estaba en el cargo al cierre de ese mes (igual que con los presidentes).
  - Dólar oficial: solo desde 1992 (antes las series están en monedas de cada época).
  - Reservas brutas del BCRA: saldo del mes anterior a la fecha (o el dato diario más cercano en los últimos años).
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from macrocenter import presidentes as P


@dataclass(frozen=True)
class Ministro:
    nombre: str
    desde: pd.Timestamp
    hasta: pd.Timestamp | None  # None = en ejercicio
    presidentes: tuple[str, ...]  # claves de presidentes.MANDATOS con los que ejerció
    perfil: str
    hitos: tuple[str, ...]
    cargo: str = "Ministro de Economía"
    apellido: str = ""  # solo si tiene más de una palabra (para las iniciales)
    wiki: str = ""  # título en es.wikipedia.org si no es igual al nombre (de ahí sale la foto)
    archivo: str = ""  # foto elegida a mano en Wikimedia Commons cuando la del artículo no sirve; "-" = sin foto

    @property
    def iniciales(self) -> str:
        return self.nombre[0] + (self.apellido or self.nombre.split()[-1])[0]

    @property
    def fin(self) -> pd.Timestamp:
        return self.hasta or P.hoy()

    @property
    def dias(self) -> int:
        return max(int((self.fin - self.desde).days), 1)


def _f(s: str) -> pd.Timestamp:
    return pd.Timestamp(s)


MINISTROS = [
    # ── Alfonsín ──
    Ministro("Bernardo Grinspun", _f("1983-12-10"), _f("1985-02-18"), ("alfonsin",),
             "Contador público. Había sido secretario de Comercio durante el gobierno de Illia.",
             ("Primer ministro de Economía de la democracia; recibió una deuda externa cercana a USD 45.000 M.",
              "Aplicó políticas de recuperación del salario y la demanda, con una inflación que siguió acelerándose.",
              "Negoció con el FMI una carta de intención en 1984.")),
    Ministro("Juan Vital Sourrouille", _f("1985-02-19"), _f("1989-03-30"), ("alfonsin",),
             "Economista. Venía de la Secretaría de Planificación.",
             ("Plan Austral (junio de 1985): nueva moneda (1 austral = 1.000 pesos argentinos), congelamiento de precios "
              "y salarios y compromiso de no emitir para financiar al Tesoro.",
              "La inflación mensual bajó de forma marcada en los meses siguientes y volvió a subir desde 1987.",
              "Plan Primavera (agosto de 1988), con acuerdos de precios y un esquema cambiario desdoblado.",
              "Dejó el cargo tras la corrida cambiaria de febrero de 1989.")),
    Ministro("Juan Carlos Pugliese", _f("1989-04-04"), _f("1989-05-26"), ("alfonsin",),
             "Presidente de la Cámara de Diputados; había sido ministro de Economía de Illia.",
             ("Gestión de menos de dos meses, en plena aceleración inflacionaria y antes de las elecciones de mayo de 1989.",
              "Se lo recuerda por la frase «les hablé con el corazón y me contestaron con el bolsillo»."),
             archivo="JuanCarlosPugliese (cropped).jpg"),
    Ministro("Jesús Rodríguez", _f("1989-05-27"), _f("1989-07-08"), ("alfonsin",),
             "Diputado nacional.",
             ("Ejerció durante el pico de la hiperinflación de 1989.",
              "El traspaso presidencial se adelantó al 8 de julio de 1989."), wiki="Jesús Rodríguez (político)"),
    # ── Menem ──
    Ministro("Miguel Ángel Roig", _f("1989-07-08"), _f("1989-07-15"), ("menem",),
             "Directivo del grupo Bunge & Born.",
             ("Murió de un infarto a los pocos días de asumir: es la gestión más corta del período.",)),
    Ministro("Néstor Rapanelli", _f("1989-07-15"), _f("1989-12-15"), ("menem",),
             "También directivo de Bunge & Born.",
             ("Plan «BB»: devaluación, suba de tarifas y acuerdos de precios con empresas.",
              "Se sancionaron las leyes de Reforma del Estado (base de las privatizaciones) y de Emergencia Económica.",
              "La inflación bajó durante unos meses y volvió a dispararse en diciembre de 1989.")),
    Ministro("Antonio Erman González", _f("1989-12-15"), _f("1991-01-31"), ("menem",),
             "Contador. Luego fue ministro de Defensa y de Trabajo.",
             ("Plan Bonex (enero de 1990): canje obligatorio de plazos fijos por bonos en dólares a 10 años.",
              "Segundo episodio hiperinflacionario a comienzos de 1990.",
              "Primeras privatizaciones grandes: ENTel y Aerolíneas Argentinas (1990)."), archivo="-"),
    Ministro("Domingo Cavallo", _f("1991-01-31"), _f("1996-08-02"), ("menem",),
             "Doctor en Economía (Harvard). Había presidido el BCRA en 1982 y fue canciller entre 1989 y 1991.",
             ("Ley de Convertibilidad (abril de 1991): 10.000 australes = 1 dólar; desde 1992, 1 peso = 1 dólar.",
              "La inflación anual pasó de más del 1.000% en 1990 a menos del 5% en 1994.",
              "Privatizaciones (entre ellas YPF), Plan Brady de deuda (1993) y sistema de jubilación privada (AFJP, 1994).",
              "Efecto Tequila (1995): caída del PBI y desocupación récord del 18,4% en mayo de ese año."),
             cargo="Ministro de Economía y Obras y Servicios Públicos"),
    Ministro("Roque Fernández", _f("1996-08-02"), _f("1999-12-10"), ("menem",),
             "Doctor en Economía (Chicago). Presidió el BCRA entre 1991 y 1996.",
             ("Mantuvo la convertibilidad en un contexto de crisis externas: asiática (1997), rusa (1998) y "
              "devaluación de Brasil (1999).",
              "Desde fines de 1998 la economía entró en recesión, con precios estables o en baja."),
             cargo="Ministro de Economía y Obras y Servicios Públicos"),
    # ── De la Rúa ──
    Ministro("José Luis Machinea", _f("1999-12-10"), _f("2001-03-05"), ("delarua",),
             "Economista. Presidió el BCRA entre 1986 y 1989.",
             ("Suba de impuestos a fines de 1999 para reducir el déficit.",
              "«Blindaje» financiero (diciembre de 2000): paquete de unos USD 40.000 M encabezado por el FMI.",
              "La recesión iniciada en 1998 continuó durante su gestión.")),
    Ministro("Ricardo López Murphy", _f("2001-03-05"), _f("2001-03-20"), ("delarua",),
             "Economista. Había sido ministro de Defensa del mismo gobierno.",
             ("Anunció un recorte del gasto cercano a $2.000 M, que incluía fondos para universidades.",
              "Tras el rechazo político y social al plan, renunció a las dos semanas."), apellido="López Murphy"),
    Ministro("Domingo Cavallo", _f("2001-03-20"), _f("2001-12-20"), ("delarua",),
             "Volvió al cargo que había ocupado entre 1991 y 1996.",
             ("Impuesto a los débitos y créditos bancarios («impuesto al cheque») y Ley de Déficit Cero (julio de 2001).",
              "Megacanje de deuda (junio de 2001) por unos USD 30.000 M.",
              "«Corralito» (diciembre de 2001): límite de $250 semanales para retirar efectivo de los bancos.",
              "Renunció durante la crisis de diciembre de 2001.")),
    # ── Duhalde ──
    Ministro("Jorge Remes Lenicov", _f("2002-01-07"), _f("2002-04-26"), ("duhalde",),
             "Economista. Había sido ministro de Economía de la provincia de Buenos Aires.",
             ("Con la Ley de Emergencia Pública (enero de 2002) terminó la convertibilidad.",
              "Devaluación, pesificación asimétrica (depósitos a $1,40 por dólar y deudas 1 a 1) y creación del CER.",
              "Volvieron las retenciones a las exportaciones."), apellido="Remes Lenicov"),
    Ministro("Roberto Lavagna", _f("2002-04-26"), _f("2005-11-28"), ("duhalde", "kirchner"),
             "Economista. Fue secretario de Industria con Alfonsín y embajador ante la Unión Europea.",
             ("Ejerció con dos presidentes: Duhalde y Néstor Kirchner.",
              "El dólar llegó a cerca de $4 a mediados de 2002 y después se estabilizó en torno a $3.",
              "Salida gradual del corralito y canje de depósitos por bonos (Boden).",
              "Canje de la deuda en default (2005), con quita y una adhesión del 76%.",
              "Superávit fiscal y comercial («superávits gemelos») y crecimiento cercano al 9% anual."),
             cargo="Ministro de Economía y Producción"),
    # ── N. Kirchner ──
    Ministro("Felisa Miceli", _f("2005-12-01"), _f("2007-07-17"), ("kirchner",),
             "Economista. Presidía el Banco Nación. Primera mujer al frente del Ministerio de Economía.",
             ("Cancelación anticipada de la deuda con el FMI (enero de 2006, unos USD 9.500 M).",
              "Acuerdos de precios con empresas; intervención del INDEC (enero de 2007).",
              "Renunció en julio de 2007 tras una causa judicial por dinero hallado en su despacho."),
             cargo="Ministra de Economía y Producción"),
    Ministro("Miguel Peirano", _f("2007-07-17"), _f("2007-12-10"), ("kirchner",),
             "Economista. Venía de la Secretaría de Industria.",
             ("Gestión de cinco meses hasta el fin del mandato, con la medición del INDEC ya en discusión.",
              "Comenzaba la crisis financiera internacional de las hipotecas «subprime»."),
             cargo="Ministro de Economía y Producción"),
    # ── CFK ──
    Ministro("Martín Lousteau", _f("2007-12-10"), _f("2008-04-25"), ("cfk",),
             "Economista. Presidía el Banco Provincia; asumió con 37 años.",
             ("Resolución 125 (marzo de 2008): retenciones móviles a la soja y otros granos.",
              "Desató un conflicto con las entidades del campo, con paros y cortes de ruta por meses.",
              "Renunció en abril de 2008, con el conflicto en curso."),
             cargo="Ministro de Economía y Producción"),
    Ministro("Carlos Fernández", _f("2008-04-25"), _f("2009-07-10"), ("cfk",),
             "Contador. Venía de la Secretaría de Hacienda.",
             ("El Senado rechazó la Resolución 125 (julio de 2008) con el voto de desempate del vicepresidente.",
              "Estatización de las AFJP (noviembre de 2008): los aportes volvieron al sistema estatal (SIPA).",
              "Crisis financiera mundial: la economía se contrajo en 2009."),
             cargo="Ministro de Economía y Finanzas Públicas", wiki="Carlos Rafael Fernández"),
    Ministro("Amado Boudou", _f("2009-07-10"), _f("2011-12-10"), ("cfk",),
             "Economista. Dirigía la ANSES; después fue vicepresidente (2011–2015).",
             ("Asignación Universal por Hijo (noviembre de 2009).",
              "Fondo del Bicentenario: uso de reservas del BCRA para pagar deuda (2010).",
              "Reapertura del canje de deuda (2010), con una adhesión acumulada cercana al 92%.",
              "Crecimiento alto en 2010 y 2011; a fines de 2011 empezaron las restricciones para comprar dólares."),
             cargo="Ministro de Economía y Finanzas Públicas"),
    Ministro("Hernán Lorenzino", _f("2011-12-10"), _f("2013-11-20"), ("cfk",),
             "Abogado. Venía de la Secretaría de Finanzas.",
             ("Endurecimiento del control de cambios: desde julio de 2012 se prohibió comprar dólares para ahorro.",
              "Reforma de la carta orgánica del BCRA (2012) y expropiación del 51% de YPF (mayo de 2012).",
              "Fallo del juez Griesa en Nueva York a favor de los bonistas que no entraron a los canjes (2012)."),
             cargo="Ministro de Economía y Finanzas Públicas"),
    Ministro("Axel Kicillof", _f("2013-11-20"), _f("2015-12-10"), ("cfk",),
             "Economista y docente de la UBA. Era viceministro; luego fue gobernador de Buenos Aires.",
             ("Devaluación de enero de 2014 (el oficial pasó de unos $6,9 a $8) y programa Precios Cuidados.",
              "Acuerdo con Repsol por la expropiación de YPF (USD 5.000 M en bonos) y con el Club de París (2014).",
              "Default selectivo en julio de 2014 tras el fallo Griesa; swap de monedas con China.",
              "Control de cambios vigente durante toda la gestión, con brecha entre el oficial y el paralelo."),
             cargo="Ministro de Economía y Finanzas Públicas"),
    # ── Macri ──
    Ministro("Alfonso Prat-Gay", _f("2015-12-10"), _f("2016-12-31"), ("macri",),
             "Economista. Presidió el BCRA entre 2002 y 2004.",
             ("Levantamiento del control de cambios (diciembre de 2015): el oficial pasó de unos $9,8 a cerca de $14.",
              "Baja o eliminación de retenciones a las exportaciones.",
              "Acuerdo con los bonistas en litigio y regreso a los mercados con una emisión de USD 16.500 M (abril de 2016).",
              "Blanqueo de capitales de 2016 y emergencia estadística en el INDEC."),
             cargo="Ministro de Hacienda y Finanzas Públicas"),
    Ministro("Nicolás Dujovne", _f("2017-01-02"), _f("2019-08-20"), ("macri",),
             "Economista.",
             ("Reformas tributaria y previsional (diciembre de 2017).",
              "Crisis cambiaria de 2018: el dólar pasó de unos $20 a cerca de $40.",
              "Acuerdo stand-by con el FMI (junio de 2018) por USD 50.000 M, ampliado luego a unos USD 57.000 M.",
              "Volvieron las retenciones (septiembre de 2018) con meta de equilibrio fiscal primario para 2019."),
             cargo="Ministro de Hacienda"),
    Ministro("Hernán Lacunza", _f("2019-08-20"), _f("2019-12-09"), ("macri",),
             "Economista. Había sido ministro de Economía de la provincia de Buenos Aires.",
             ("Asumió tras la fuerte suba del dólar posterior a las PASO de agosto de 2019.",
              "Postergación («reperfilamiento») de los vencimientos de deuda de corto plazo.",
              "Restablecimiento del control de cambios (septiembre de 2019)."),
             cargo="Ministro de Hacienda"),
    # ── A. Fernández ──
    Ministro("Martín Guzmán", _f("2019-12-10"), _f("2022-07-04"), ("fernandez",),
             "Economista e investigador en la Universidad de Columbia.",
             ("Ley de Solidaridad (diciembre de 2019), que creó el impuesto PAIS a la compra de dólares.",
              "Reestructuración de deuda con acreedores privados (2020) por unos USD 65.000 M.",
              "Pandemia: IFE para trabajadores informales y ATP para el pago de salarios.",
              "Acuerdo de facilidades extendidas con el FMI (marzo de 2022) para refinanciar el préstamo de 2018.")),
    Ministro("Silvina Batakis", _f("2022-07-04"), _f("2022-08-03"), ("fernandez",),
             "Economista. Había sido ministra de Economía bonaerense; luego presidió el Banco Nación.",
             ("Gestión de un mes, en medio de una fuerte suba del dólar paralelo.",
              "Anunció el congelamiento de ingresos en el Estado y el compromiso con las metas acordadas con el FMI."),
             cargo="Ministra de Economía"),
    Ministro("Sergio Massa", _f("2022-08-03"), _f("2023-12-07"), ("fernandez",),
             "Abogado. Presidía la Cámara de Diputados.",
             ("Ministerio ampliado que sumó Desarrollo Productivo y Agricultura.",
              "«Dólar soja» y otros tipos de cambio especiales para exportadores.",
              "Sequía de 2022/23, con una fuerte caída de las exportaciones agrícolas.",
              "Devaluación del oficial tras las PASO de agosto de 2023 (de unos $287 a $350); fue candidato a presidente.")),
    # ── Milei ──
    Ministro("Luis Caputo", _f("2023-12-10"), None, ("milei",),
             "Economista. Fue ministro de Finanzas (2017–2018) y presidente del BCRA (2018) con Macri.",
             ("Devaluación inicial (diciembre de 2023): el dólar mayorista pasó de unos $366 a $800, con ajustes mensuales del 2%.",
              "Fuerte recorte del gasto: superávit fiscal primario y financiero desde 2024.",
              "Blanqueo de capitales (2024) y baja sostenida de la inflación mensual.",
              "Abril de 2025: nuevo acuerdo con el FMI, bandas cambiarias y fin del control de cambios para personas.")),
]

# notas que van con el grupo de cada presidente (interinatos y cambios de estructura del ministerio)
NOTAS = {
    "duhalde": "Entre el 20 de diciembre de 2001 y el 7 de enero de 2002 la cartera estuvo a cargo, de forma interina, "
               "de Nicolás Gallo, Jorge Capitanich y Rodolfo Frigeri. En esos días se declaró la cesación de pagos de la deuda.",
    "macri": "Entre 2017 y 2019 el ministerio estuvo dividido en Hacienda y Finanzas. Finanzas estuvo a cargo de Luis "
             "Caputo hasta junio de 2018, cuando se fusionó con Hacienda.",
}


# ───────────────────────── cálculos ─────────────────────────
def inflacion_gestion(inf: pd.DataFrame, m: Ministro) -> tuple[float | None, int, tuple[pd.Timestamp, float] | None]:
    """(inflación acumulada en %, meses contados, (mes, valor) del pico). Un mes cuenta para quien estaba al cierre."""
    cierre = inf["fecha"] + pd.offsets.MonthEnd(0)
    d = inf[(cierre >= m.desde) & (cierre < m.fin)]
    if d.empty:
        return None, 0, None
    pico = d.loc[d["valor"].idxmax()]
    return float(((1 + d["valor"] / 100).prod() - 1) * 100), len(d), (pico["fecha"], float(pico["valor"]))


def reservas(d: dict, fecha: pd.Timestamp) -> float | None:
    act = d["reservas_actual"]
    if not act.empty and fecha >= act["fecha"].min():
        return P._antes(act, fecha)
    return P._mes_previo(d["reservas_hist"], fecha)


def indicadores(m: Ministro, d: dict) -> dict:
    out: dict = {}
    out["inf"], out["meses"], out["pico"] = inflacion_gestion(d["inflacion"], m)
    out["usd_ini"] = P.dolar_oficial(d["dolar_hist"], d["dolar_actual"], m.desde)
    out["usd_fin"] = P.dolar_oficial(d["dolar_hist"], d["dolar_actual"], m.fin)
    out["res_ini"], out["res_fin"] = reservas(d, m.desde), reservas(d, m.fin)
    return out


def duracion(dias: int) -> str:
    if dias < 60:
        return f"{dias} día{'s' if dias != 1 else ''}"
    meses = round(dias / 30.44)
    a, me = divmod(meses, 12)
    partes = ([f"{a} año{'s' if a != 1 else ''}"] if a else []) + ([f"{me} mes{'es' if me != 1 else ''}"] if me else [])
    return " y ".join(partes)


_MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _fecha(f: pd.Timestamp) -> str:
    return f"{_MESES[f.month - 1]} {f.year}"


def periodo(m: Ministro) -> str:
    if m.hasta is not None and (m.desde.year, m.desde.month) == (m.hasta.year, m.hasta.month):
        return _fecha(m.desde)
    return f"{_fecha(m.desde)} – {_fecha(m.hasta) if m.hasta else 'hoy'}"


def _usd(x: float) -> str:
    return P._n(x, 2 if x < 100 else 0, "$")


def datos(i: dict) -> list[dict]:
    """Cifras de la tarjeta: [{'k': título, 'v': valor, 's': detalle, 'tend': ''|'mejor'|'peor'}].
    Las que no tienen dato (o no cambian en gestiones de pocos días) no se muestran."""
    out = []
    if i["inf"] is not None:
        if i["meses"] >= 2:
            prom = ((1 + i["inf"] / 100) ** (1 / i["meses"]) - 1) * 100
            prom = 0.0 if abs(prom) < 0.05 else prom  # sin «-0,0%»
            det = f"{P._n(prom, 1)}% por mes · {i['meses']} meses"
        else:
            det = "en su único mes"
        out.append({"k": "Inflación acumulada", "v": P._pct(i["inf"]), "s": det, "tend": ""})
    if i["usd_ini"] and i["usd_fin"]:
        out.append({"k": "Dólar oficial", "v": f"{_usd(i['usd_ini'])} → {_usd(i['usd_fin'])}",
                    "s": f"×{P._n(i['usd_fin'] / i['usd_ini'], 1)}", "tend": ""})
    if i["res_ini"] and i["res_fin"] is not None and i["res_ini"] != i["res_fin"]:
        cambio = (i["res_fin"] / i["res_ini"] - 1) * 100
        out.append({"k": "Reservas (USD M)", "v": f"{P._n(i['res_ini'])} → {P._n(i['res_fin'])}",
                    "s": ("+" if cambio > 0 else "") + P._n(cambio, 0, suf="%"),
                    "tend": P._tendencia(i["res_ini"], i["res_fin"], "alto")})
    return out


def foto_url(m: Ministro, fotos_wiki: dict[str, str]) -> str:
    """Foto del ministro: la elegida a mano en Commons, o la del artículo de Wikipedia, o ninguna."""
    if m.archivo == "-":
        return ""
    if m.archivo:
        from urllib.parse import quote
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(m.archivo.replace(' ', '_'))}?width=250"
    return fotos_wiki.get(m.nombre, "")


def fotos() -> dict[str, str]:
    """{nombre: url de la foto} con la imagen principal de cada artículo de es.wikipedia.org, en un solo pedido.
    Solo se aceptan imágenes alojadas en Wikimedia. Devuelve {} si no hay conexión: las tarjetas muestran iniciales."""
    import requests

    titulos = {(m.wiki or m.nombre): m.nombre for m in MINISTROS if not m.archivo}
    try:
        r = requests.get(
            "https://es.wikipedia.org/w/api.php",
            params={"action": "query", "format": "json", "prop": "pageimages", "pithumbsize": 250, "redirects": 1,
                    "titles": "|".join(titulos)},
            headers={"User-Agent": "MacroCenter/1.0 (tablero personal)"}, timeout=30,
        ).json()["query"]
        redirigido = {x["from"]: x["to"] for x in r.get("redirects", []) + r.get("normalized", [])}
        paginas = {p["title"]: p for p in r["pages"].values()}
        out = {}
        for titulo, nombre in titulos.items():
            foto = ((paginas.get(redirigido.get(titulo, titulo)) or {}).get("thumbnail") or {}).get("source", "")
            if foto and P._host_ok(foto, ("upload.wikimedia.org", "thumb.wikimedia.org")):
                out[nombre] = foto
        return out
    except Exception:  # noqa: BLE001
        return {}


def pico_texto(i: dict) -> str:
    if not i["pico"] or i["meses"] < 2:
        return ""
    mes, v = i["pico"]
    return f"Pico mensual de inflación: {P._pct(v)} en {_MESES[mes.month - 1]}-{mes.year}"


def barra_duracion(m: Ministro) -> float:
    """Ancho (0–100) de la barra de duración, relativo a la gestión más larga. Escala de raíz cuadrada para que
    una gestión de días siga siendo visible al lado de una de años."""
    mayor = max(x.dias for x in MINISTROS)
    return max(4.0, (m.dias / mayor) ** 0.5 * 100)


def resumen() -> dict:
    """Datos generales del período: cantidad de gestiones y personas, duración promedio, la más larga y la más corta."""
    personas = {m.nombre for m in MINISTROS}
    larga = max(MINISTROS, key=lambda m: m.dias)
    corta = min(MINISTROS, key=lambda m: m.dias)
    return {"gestiones": len(MINISTROS), "personas": len(personas),
            "promedio": duracion(round(sum(m.dias for m in MINISTROS) / len(MINISTROS))),
            "larga": (larga, duracion(larga.dias)), "corta": (corta, duracion(corta.dias))}
