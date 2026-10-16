"""Acceso a fuentes públicas de datos macroeconómicos de Argentina.

Fuentes:
  - BCRA, API Estadísticas v4.0 (reservas, tipo de cambio, tasas, UVA, CER, inflación, dinero)
  - Datos Argentina, API de Series de Tiempo (EMAE, PBI, desempleo, comercio exterior)
  - ArgentinaDatos (cotizaciones del dólar por casa, riesgo país)

Todas las funciones devuelven DataFrames con columna `fecha` (datetime64) ordenada.
"""
from __future__ import annotations

import io
import time

import pandas as pd
import requests

BCRA_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"
SERIES_URL = "https://apis.datos.gob.ar/series/api/series/"
ARGDATOS_URL = "https://api.argentinadatos.com/v1"
TIMEOUT = 40

# ids de variables del BCRA
BCRA_IDS = {
    "reservas": 1,
    "tc_minorista": 4,
    "tc_mayorista": 5,
    "badlar": 7,
    "depositos_30d": 12,
    "prestamos_personales": 14,
    "pases_1d": 150,  # tasa de pases entre terceros a 1 día (referencia vigente)
    "tpm": 160,  # tasa de política monetaria, TNA — el BCRA dejó de publicarla el 10/7/2025
    "base_monetaria": 15,
    "m2_privado_ia": 25,
    "prestamos_privados": 26,
    "inflacion_mensual": 27,
    "inflacion_interanual": 28,
    "rem_12m": 29,
    "cer": 30,
    "uva": 31,
    "uvi": 32,
    "icl": 40,
    "tamar": 44,
}

# ids de series de datos.gob.ar
SERIES_IDS = {
    "pib": "4.2_OGP_2004_T_17",  # PIB trimestral, millones de pesos de 2004
    "emae": "143.3_NO_PR_2004_A_21",  # EMAE original, base 2004=100
    "emae_sa": "143.3_NO_PR_2004_A_31",  # EMAE desestacionalizado
    "emae_sa_mom": "143.3_ICE_SER_VM_2004_A_34",  # var. % mensual desestacionalizada
    "desempleo": "42.3_EPH_PUNTUATAL_0_M_30",  # tasa de desocupación (fracción)
    "salarios": "149.1_TL_INDIIOS_OCTU_0_21",  # índice de salarios total (oct-2016=100)
    "salarios_privado": "149.1_SOR_PRIADO_OCTU_0_25",  # registrado, sector privado
    "salarios_publico": "149.1_SOR_PUBICO_OCTU_0_14",  # registrado, sector público
    "ripte": "158.1_REPTE_0_0_5",  # remuneración imponible promedio, pesos corrientes
    "smvm": "57.1_SMVMM_0_M_34",  # salario mínimo, vital y móvil mensual (incluye tramos futuros ya fijados)
    "haber_minimo": "58.1_MP_0_M_13",  # haber mínimo jubilatorio
    # series largas para la sección de presidentes
    "pib_1986": "255.1_OTA_TOTTAL_1986_0_12",  # PIB trimestral 1980-1996 (precios de 1986)
    "pib_1993": "2.2_OGP_1993_T_17",  # PIB trimestral 1993-2013 (precios de 1993)
    "paro_anual": "42.1_EPDT_0_A_30",  # desocupación anual desde 1982 (EPH), en %
    "reservas_hist": "174.1_RRVAS_IDOS_0_0_36",  # reservas BCRA, saldo mensual desde 1940
    "exportaciones": "74.3_IET_0_M_16",  # millones de USD
    "importaciones": "74.3_IIT_0_M_25",  # millones de USD
    "ipc_gba": "145.3_INGGBAGBA_DICI_M_10",  # IPC Gran Buenos Aires (INDEC), nivel general, base dic-2016 = 100
    "pib_corriente": "8.2_PIBPM_2004_T_38",  # PIB a precios de mercado en pesos corrientes, trimestral anualizado (millones)
    "fiscal_primario": "452.3_RESULTADO_RIO_0_M_18_54",  # resultado primario del sector público nacional, millones de $ corrientes
    # resultado financiero (después de intereses), millones de $. Esquema Ahorro-Inversión-Financiamiento, metodología
    # 2017: mismos valores que el IMIG (452.3_RESULTADO_ERO_0_M_20_25), que la API devolvía con la mitad de los meses vacíos
    "fiscal_financiero": "379.9_RESULTADO_017__18_38",
    # inflación por región (INDEC) y de las provincias que publican su propio índice (nivel de precios, mensual)
    "ipc_pampeana": "145.3_INGPAMANA_DICI_M_15",
    "ipc_noreste": "145.3_INGNEANEA_DICI_M_10",
    "ipc_noroeste": "145.3_INGNOANOA_DICI_M_10",
    "ipc_cuyo": "145.3_INGCUYUYO_DICI_M_11",
    "ipc_patagonia": "145.3_INGPATNIA_DICI_M_16",
    "ipc_caba": "193.2_NIVEL_GENERAL_2021_0_13_2",  # IPCBA, Instituto de Estadística de la Ciudad
    "ipc_santafe": "198.1_NIVEL_GENERAL_2014_0_13",
    "ipc_mendoza": "195.1_NIVEL_GENERAL_0_0_13",
    "ipc_tucuman": "199.1_NIVEL_GENERAL_2014_0_13",
    "ipc_sanluis": "197.1_NIVEL_GENERAL_2014_0_13",
    "ipc_chaco": "464.1_IPC_CHACO_NG_0_0_22_93",  # Gran Resistencia
    "ipc_neuquen": "196.1_NIVEL_GENERAL_2014_0_13",  # se muestra solo si está al día (ver inflacion_distritos)
    # precios mayoristas (INDEC, Sistema de Índices de Precios Mayoristas): nivel general, base dic-2015 = 100
    "ipim": "448.1_NIVEL_GENERAL_0_0_13_46",  # IPIM: precios internos al por mayor (incluye impuestos)
    "ipp": "450.1_NIVEL_GENERAL_0_0_13_92",  # IPP: precios básicos del productor (sin impuestos)
    # pobreza (EPH, % de personas, por semestre: la fecha es el comienzo del semestre SIGUIENTE al medido) y canastas
    "pobreza": "64.2_POBLACION_NUA_0_0_34_74",
    "cba_adulto": "150.1_CSTA_BARIA_0_D_26",  # canasta básica alimentaria, por adulto equivalente ($)
    "linea_pobreza": "150.1_LA_POBREZA_0_D_13",  # canasta básica total de una familia tipo de 4 integrantes ($)
    "linea_indigencia": "150.1_LA_INDICIA_0_D_16",  # canasta alimentaria de esa misma familia ($)
    # balance cambiario del BCRA (millones de USD por mes)
    "cambiario_cc": "182.1_TOTAL_CUENRIA_0_M_32",  # cuenta corriente cambiaria
    "cambiario_bienes": "182.1_CUENTA_CORNES_0_M_39",
    "cambiario_servicios": "182.1_CUENTA_CORIOS_0_M_42",
    "cambiario_financiera": "182.1_TOTAL_CUENRIA_0_M_41",  # cuenta capital y financiera cambiaria
    "cambiario_fae": "182.1_C_K_FINC_CINC_0_M_56",  # formación de activos externos de personas y empresas (neto)
}


def limpiar(df):
    """Deja una serie lista para usar aunque la fuente venga sucia: fechas ordenadas y sin repetir, infinitos como
    vacíos y sin filas totalmente vacías. Si no es un DataFrame con columna `fecha`, lo devuelve igual."""
    if not isinstance(df, pd.DataFrame) or "fecha" not in df.columns:
        return df
    d = df.copy()
    d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")
    numericas = [c for c in d.columns if c != "fecha" and pd.api.types.is_numeric_dtype(d[c])]
    if numericas:
        d[numericas] = d[numericas].replace([float("inf"), float("-inf")], float("nan"))
        d = d.dropna(subset=numericas, how="all")
    d = d.dropna(subset=["fecha"]).sort_values("fecha")
    return d.drop_duplicates("fecha", keep="last").reset_index(drop=True)


def hoy_argentina() -> str:
    """Fecha de hoy en Argentina (UTC-3) como AAAA-MM-DD. El servidor donde se publica la app anda en UTC y, de noche,
    ya está en el día siguiente: el BCRA rechaza (error 400) una fecha 'hasta' que todavía no ocurrió allá."""
    return (pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=3)).strftime("%Y-%m-%d")


def _get(url: str, _intentos: int = 4, **params) -> requests.Response:
    """GET con reintentos: si la fuente responde «demasiados pedidos» (429) o un error pasajero del servidor (5xx),
    espera un poco (más cada vez) y vuelve a probar, hasta `_intentos` veces. Cualquier otro error se informa enseguida.
    Lo que se pide al tocar un control (y frena la pantalla mientras espera) usa menos intentos."""
    espera = 1.5
    ultimo = max(1, _intentos) - 1
    for intento in range(ultimo + 1):
        try:
            resp = requests.get(url, params=params or None, timeout=TIMEOUT)
        except (requests.ConnectionError, requests.Timeout):
            if intento == ultimo:
                raise
        else:
            if resp.status_code not in (429, 500, 502, 503, 504) or intento == ultimo:
                resp.raise_for_status()
                return resp
        time.sleep(espera)
        espera *= 2
    raise RuntimeError("inalcanzable")


def bcra(variable: str, desde: str | None = None) -> pd.DataFrame:
    """Serie del BCRA por nombre lógico (ver BCRA_IDS). Pagina automáticamente."""
    var_id = BCRA_IDS[variable]
    rows: list[dict] = []
    offset = 0
    while True:
        params = {"limit": 3000, "offset": offset}
        if desde:
            params["desde"] = desde
        payload = _get(f"{BCRA_URL}/{var_id}", **params).json()
        results = payload.get("results") or []
        detalle = results[0].get("detalle", []) if results else []
        rows.extend(detalle)
        total = payload["metadata"]["resultset"]["count"]
        offset += 3000
        if offset >= total or not detalle:
            break
    df = pd.DataFrame(rows, columns=["fecha", "valor"])
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)


def serie(nombre: str, desde: str | None = None, hasta: str | None = None) -> pd.DataFrame:
    """Serie de la API de Series de Tiempo por nombre lógico (ver SERIES_IDS). Máximo 5.000 puntos por pedido."""
    params = {"ids": SERIES_IDS[nombre], "limit": 5000}
    if desde:
        params["start_date"] = desde
    if hasta:
        params["end_date"] = hasta
    # La API a veces devuelve valores vacíos al azar o la serie entera vacía, y guarda esa respuesta rota para esa
    # consulta exacta: repetirla trae siempre los mismos huecos. Variando un poco la consulta (orden, límite, fechas)
    # y el formato llegan otras respuestas, que se combinan hasta no tener huecos o hasta que varias seguidas no
    # agregan nada (los huecos reales quedan). Las respuestas vacías no cuentan. Después de la primera respuesta con
    # datos, las variantes van sin reintentos y con un tope de tiempo: completar huecos nunca debe demorar la descarga.
    inicio = time.monotonic()
    s = None
    sin_aporte = 0
    error = None
    meta: dict = {}
    for extra in _VARIANTES_SERIE:
        if any(k in params for k in extra if k not in ("limit", "sort")):
            continue  # no pisar un rango pedido a propósito
        for formato in ("json", "csv"):
            if s is not None and time.monotonic() - inicio > 20:
                break
            try:
                nuevo = _serie_pedido({**params, **extra}, formato, intentos=4 if s is None else 1,
                                      meta=meta if not meta and formato == "json" else None)
            except Exception as e:  # noqa: BLE001 — se prueba con la variante siguiente
                error = e
                continue
            if nuevo.dropna().empty:
                continue
            if s is None:
                s = nuevo
            else:
                antes = int(s.notna().sum())
                s = s.combine_first(nuevo)
                sin_aporte = sin_aporte + 1 if int(s.notna().sum()) == antes else 0
            if not s.isna().any() or sin_aporte >= 4:
                break
        if s is not None and (not s.isna().any() or sin_aporte >= 4 or time.monotonic() - inicio > 20):
            break
    # La API también puede quedarse con respuestas viejas (el RIPTE llegaba hasta abril con julio ya publicado). Su
    # propia ficha dice hasta qué fecha hay datos: si falta el final, se completa con el archivo oficial de la serie
    # (la misma plataforma, infra.datos.gob.ar).
    if not desde and not hasta and meta:
        try:
            s = _completar_con_archivo(s, meta)
        except Exception:  # noqa: BLE001 — es un complemento: sin él queda lo que trajo la API
            pass
    if s is None:
        if error is not None:
            raise error
        return pd.DataFrame(columns=["fecha", "valor"])
    df = s.rename("valor").rename_axis("fecha").reset_index()
    return df.dropna().sort_values("fecha").reset_index(drop=True)


_VARIANTES_SERIE = ({}, {"sort": "desc"}, {"limit": 4999}, {"end_date": "2100-12-31"}, {"limit": 4998, "sort": "desc"},
                    {"start_date": "1900-01-01"})
ARCHIVOS_URL = "https://infra.datos.gob.ar/"


def _completar_con_archivo(s: pd.Series | None, meta: dict) -> pd.Series | None:
    """Si la API no trajo hasta la última fecha que dice tener, baja el archivo CSV de la serie y suma lo que falte."""
    fin, columna, url = meta.get("fin"), meta.get("columna"), meta.get("url") or ""
    if not fin or not columna or not url.startswith(ARCHIVOS_URL):
        return s
    if s is not None and not s.dropna().empty and s.dropna().index.max() >= pd.Timestamp(fin):
        return s
    df = pd.read_csv(io.StringIO(_get(url, _intentos=2).text))
    if columna not in df.columns:
        return s
    arch = pd.Series(pd.to_numeric(df[columna], errors="coerce").to_numpy(dtype=float),
                     index=pd.to_datetime(df.iloc[:, 0], errors="coerce"))
    arch = arch[arch.index.notna() & ~arch.index.duplicated()]
    return arch if s is None else s.combine_first(arch)


def _serie_pedido(params: dict, formato: str, intentos: int = 4, meta: dict | None = None) -> pd.Series:
    """Un pedido a la API de Series de Tiempo: valores indexados por fecha (NaN donde vino vacío). Con `meta`, pide
    también la ficha de la serie y anota ahí su última fecha, el nombre de la columna y el archivo oficial."""
    if meta is not None:
        params = {**params, "metadata": "full"}
    resp = _get(SERIES_URL, _intentos=intentos, **params, format=formato)
    if formato == "csv":
        df = pd.read_csv(io.StringIO(resp.text))
        fechas, valores = df.iloc[:, 0], pd.to_numeric(df.iloc[:, 1], errors="coerce")
    else:
        cuerpo = resp.json()
        if meta is not None:
            try:
                ficha = cuerpo["meta"][1]
                meta.update(fin=ficha["field"].get("time_index_end"), columna=ficha["field"].get("title"),
                            url=ficha["distribution"].get("downloadURL"))
            except (KeyError, IndexError, TypeError, AttributeError):
                pass
        df = pd.DataFrame(cuerpo["data"], columns=["fecha", "valor"])
        fechas, valores = df["fecha"], pd.to_numeric(df["valor"], errors="coerce")
    s = pd.Series(valores.to_numpy(dtype=float), index=pd.to_datetime(fechas))
    return s[~s.index.duplicated()]


def dolar(casa: str) -> pd.DataFrame:
    """Cotización histórica de una casa: oficial, blue, bolsa, contadoconliqui, mayorista."""
    df = pd.DataFrame(_get(f"{ARGDATOS_URL}/cotizaciones/dolares/{casa}").json())
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "compra", "venta"]].sort_values("fecha").reset_index(drop=True)


CASAS_DOLAR = ("oficial", "mayorista", "blue", "bolsa", "contadoconliqui", "cripto", "tarjeta")


def dolares(casas: tuple[str, ...] = CASAS_DOLAR) -> pd.DataFrame:
    """Un dólar por casa: precio de venta en la columna `<casa>` y de compra en `<casa>_compra`. Las casas se piden
    todas a la vez (de a una tardaba más de 5 segundos)."""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=len(casas)) as pool:
        series = list(pool.map(dolar, casas))
    wide = None
    for casa, d in zip(casas, series):
        d = d.drop_duplicates("fecha").set_index("fecha")
        s = d[["venta", "compra"]].rename(columns={"venta": casa, "compra": f"{casa}_compra"})
        wide = s if wide is None else wide.join(s, how="outer")
    return wide.sort_index().reset_index()


CAMBIARIAS_URL = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones"


def divisa(codigo: str, desde: str = "2016-01-01") -> pd.DataFrame:
    """Cotización de referencia del BCRA de una divisa (EUR, GBP, ...) en pesos por unidad.
    Columnas: fecha, valor (pesos por unidad), pase (dólares por unidad). Pagina automáticamente."""
    filas: list[tuple] = []
    offset = 0
    while True:
        payload = _get(f"{CAMBIARIAS_URL}/{codigo}", fechadesde=desde, fechahasta=hoy_argentina(),
                       limit=1000, offset=offset).json()
        resultados = payload.get("results") or []
        for r in resultados:
            det = r["detalle"][0]
            filas.append((r["fecha"], det["tipoCotizacion"], det["tipoPase"]))
        offset += 1000
        if not resultados or offset >= payload["metadata"]["resultset"]["count"]:
            break
    df = pd.DataFrame(filas, columns=["fecha", "valor", "pase"])
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)


def ipc_eeuu() -> pd.DataFrame:
    """Índice de precios al consumidor de EE. UU. (CPIAUCSL, mensual desde 1947), de la Reserva Federal de St. Louis (FRED).
    Sirve para pasar dólares de distintas épocas a dólares de hoy. Columnas: fecha (primer día del mes), valor."""
    import io

    texto = _get("https://fred.stlouisfed.org/graph/fredgraph.csv", id="CPIAUCSL").text
    df = pd.read_csv(io.StringIO(texto))
    df.columns = ["fecha", "valor"]
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df.dropna().sort_values("fecha").reset_index(drop=True)


# Tasa de la Reserva Federal (techo del rango objetivo) y rendimiento de los bonos del Tesoro de EE. UU. (FRED, diarios).
TASAS_EEUU = [("DFEDTARU", "Tasa de la Fed"), ("DGS3MO", "Letra 3 meses"), ("DGS2", "Bono 2 años"),
              ("DGS10", "Bono 10 años"), ("DGS30", "Bono 30 años")]


def fred(serie: str, desde: str = "2016-01-01") -> pd.DataFrame:
    """Una serie de FRED (Reserva Federal de St. Louis), sin clave. Columnas: fecha, valor. Una serie por pedido: con
    varias juntas FRED devuelve un ZIP."""
    import io

    texto = _get("https://fred.stlouisfed.org/graph/fredgraph.csv", id=serie, cosd=desde).text
    df = pd.read_csv(io.StringIO(texto))
    df.columns = ["fecha", "valor"]
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")  # los feriados vienen vacíos
    return df.dropna().sort_values("fecha").reset_index(drop=True)


# Bonos del Tesoro argentino en dólares, por vencimiento: (año, ley Nueva York, ley local). El GD46 no tiene par local.
BONOS_ARG = [("2029", "GD29", "AL29"), ("2030", "GD30", "AL30"), ("2035", "GD35", "AL35"), ("2038", "GD38", "AE38"),
             ("2041", "GD41", "AL41"), ("2046", "GD46", None)]
DATA912_URL = "https://data912.com"


def bonos_ahora() -> pd.DataFrame:
    """Precio de los bonos argentinos en dólares MEP (especie «D»: AL30D, GD30D...), cada 100 de valor nominal, y su
    variación del día. Fuente: data912 (precios de BYMA, no oficial). Columnas: bono, precio, var."""
    filas = [{"bono": b["symbol"][:-1], "precio": b.get("c"), "var": b.get("pct_change")}
             for b in _get(f"{DATA912_URL}/live/arg_bonds").json()
             if isinstance(b, dict) and str(b.get("symbol", "")).endswith("D")]
    df = pd.DataFrame(filas, columns=["bono", "precio", "var"])
    df[["precio", "var"]] = df[["precio", "var"]].apply(pd.to_numeric, errors="coerce")
    return df[df["precio"] > 0].reset_index(drop=True)


def bono_historia(bono: str) -> pd.DataFrame:
    """Cierre diario de un bono argentino en dólares MEP (especie «D»), cada 100 de valor nominal. Columnas: fecha, valor."""
    df = pd.DataFrame(_get(f"{DATA912_URL}/historical/bonds/{bono}D").json())
    df = pd.DataFrame({"fecha": pd.to_datetime(df["date"], errors="coerce"), "valor": pd.to_numeric(df["c"], errors="coerce")})
    return df.dropna().sort_values("fecha").drop_duplicates("fecha", keep="last").reset_index(drop=True)


def dolar_historico() -> pd.DataFrame:
    """Dólar oficial (BCRA, serie 175.1 'Dólar estadounidense') desde 1992 hasta 2010, en pesos por dólar.
    Son ~7.000 datos diarios, así que se pide en dos tramos (la API entrega hasta 5.000 por pedido).
    Desde 2011 se usa la serie de ArgentinaDatos (ver `dolares`)."""
    ids = "175.1_DR_ESTANSE_0_0_20"
    partes = []
    for desde, hasta in (("1992-01-01", "2001-12-31"), ("2002-01-01", "2010-12-31")):
        payload = _get(SERIES_URL, ids=ids, limit=5000, format="json", start_date=desde, end_date=hasta).json()
        partes.append(pd.DataFrame(payload["data"], columns=["fecha", "valor"]))
    df = pd.concat(partes, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.dropna().sort_values("fecha").reset_index(drop=True)


DOLARAPI_URL = "https://dolarapi.com/v1/dolares"


def dolares_ahora() -> pd.DataFrame:
    """Cotización de cada dólar en este momento: casa, compra, venta y `actualizado` (hora de Argentina, sin zona).
    Junta dos fuentes y, para cada dólar, se queda con el dato más reciente: DolarApi (del autor de ArgentinaDatos) y
    CriptoYa, que toma el MEP y el CCL de las operaciones del bono AL30 y el cripto del USDT, minuto a minuto."""
    partes = []
    for fn in (_dolares_dolarapi, _dolares_criptoya):
        try:
            partes.append(fn())
        except Exception:  # noqa: BLE001 — con una sola fuente alcanza
            pass
    if not partes:
        raise RuntimeError("ninguna fuente del dólar en vivo respondió")
    todo = pd.concat(partes, ignore_index=True)
    todo = todo.sort_values("actualizado").drop_duplicates("casa", keep="last")
    return todo.reset_index(drop=True)[["casa", "compra", "venta", "actualizado"]]


def _dolares_criptoya() -> pd.DataFrame:
    d = _get(f"{CRIPTOYA_URL}/dolar", _intentos=1).json()

    def fila(casa, compra, venta, ts):
        venta = pd.to_numeric(venta, errors="coerce")
        if pd.isna(venta) or venta <= 0 or not ts:
            return None
        cuando = pd.to_datetime(ts, unit="s", utc=True) - pd.Timedelta(hours=3)
        return {"casa": casa, "compra": pd.to_numeric(compra, errors="coerce"), "venta": float(venta),
                "actualizado": cuando.tz_localize(None)}

    def bono(tipo):
        v = ((d.get(tipo) or {}).get("al30") or {}).get("ci") or {}
        return v.get("price"), v.get("price"), v.get("timestamp")

    usdt = (d.get("cripto") or {}).get("usdt") or {}
    filas = [
        fila("oficial", (d.get("oficial") or {}).get("bid"), (d.get("oficial") or {}).get("ask"), (d.get("oficial") or {}).get("timestamp")),
        fila("blue", (d.get("blue") or {}).get("bid"), (d.get("blue") or {}).get("ask"), (d.get("blue") or {}).get("timestamp")),
        fila("mayorista", None, (d.get("mayorista") or {}).get("price"), (d.get("mayorista") or {}).get("timestamp")),
        fila("tarjeta", None, (d.get("tarjeta") or {}).get("price"), (d.get("tarjeta") or {}).get("timestamp")),
        fila("bolsa", *bono("mep")),
        fila("contadoconliqui", *bono("ccl")),
        fila("cripto", usdt.get("bid"), usdt.get("ask"), usdt.get("timestamp")),
    ]
    return pd.DataFrame([f for f in filas if f], columns=["casa", "compra", "venta", "actualizado"])


def _dolares_dolarapi() -> pd.DataFrame:
    filas = []
    for d in _get(DOLARAPI_URL).json():
        casa = str(d.get("casa") or "").strip()
        venta = pd.to_numeric(d.get("venta"), errors="coerce")
        cuando = pd.to_datetime(d.get("fechaActualizacion"), errors="coerce", utc=True)
        if casa in CASAS_DOLAR and pd.notna(venta) and venta > 0 and pd.notna(cuando):
            filas.append({"casa": casa, "compra": pd.to_numeric(d.get("compra"), errors="coerce"), "venta": float(venta),
                          "actualizado": (cuando - pd.Timedelta(hours=3)).tz_localize(None)})
    return pd.DataFrame(filas, columns=["casa", "compra", "venta", "actualizado"])


def riesgo_pais_ahora() -> pd.DataFrame:
    """Último valor del riesgo país (ArgentinaDatos). Columnas: fecha, valor."""
    d = _get(f"{ARGDATOS_URL}/finanzas/indices/riesgo-pais/ultimo").json()
    df = pd.DataFrame([{"fecha": pd.to_datetime(d.get("fecha"), errors="coerce"),
                        "valor": pd.to_numeric(d.get("valor"), errors="coerce")}])
    return df.dropna().reset_index(drop=True)


def plazo_fijo_bancos() -> pd.DataFrame:
    """Tasa de plazo fijo a 30 días de cada banco (ArgentinaDatos, con datos del BCRA). TNA en %; 0 = no informa."""
    filas = [{"entidad": str(e.get("entidad") or "").strip(),
              "tna_clientes": float(e.get("tnaClientes") or 0) * 100,
              "tna_no_clientes": float(e.get("tnaNoClientes") or 0) * 100}
             for e in _get(f"{ARGDATOS_URL}/finanzas/tasas/plazoFijo").json()]
    df = pd.DataFrame(filas, columns=["entidad", "tna_clientes", "tna_no_clientes"])
    return df[(df["entidad"] != "") & ((df["tna_clientes"] > 0) | (df["tna_no_clientes"] > 0))].reset_index(drop=True)


def rendimientos_plataformas() -> pd.DataFrame:
    """Rendimiento anual (APY, %) que informa cada billetera o plataforma cripto, por moneda (ArgentinaDatos)."""
    filas = [{"entidad": str(e.get("entidad") or ""), "moneda": str(r.get("moneda") or "").upper(),
              "apy": r.get("apy"), "fecha": r.get("fecha")}
             for e in _get(f"{ARGDATOS_URL}/finanzas/rendimientos").json() for r in (e.get("rendimientos") or [])]
    df = pd.DataFrame(filas, columns=["entidad", "moneda", "apy", "fecha"])
    df["apy"] = pd.to_numeric(df["apy"], errors="coerce")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df.dropna(subset=["apy", "fecha"]).reset_index(drop=True)


def fci(tipo: str = "mercadoDinero", fecha: str = "ultimo") -> pd.DataFrame:
    """Valor de la cuotaparte (vcp) y patrimonio de cada fondo común de inversión (ArgentinaDatos, datos de la CAFCI).
    `fecha`: 'ultimo', 'penultimo' o 'AAAA/MM/DD'."""
    if tipo not in ("mercadoDinero", "rentaFija", "rentaVariable", "rentaMixta"):
        raise ValueError(f"tipo de fondo desconocido: {tipo}")
    df = pd.DataFrame(_get(f"{ARGDATOS_URL}/finanzas/fci/{tipo}/{fecha}").json(),
                      columns=["fondo", "horizonte", "fecha", "vcp", "patrimonio"])
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    for c in ("vcp", "patrimonio"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["fondo", "fecha", "vcp"]).drop_duplicates("fondo").reset_index(drop=True)


def inflacion_historica() -> pd.DataFrame:
    """IPC mensual (%) desde 1943 (ArgentinaDatos). Fecha = fin de mes."""
    df = pd.DataFrame(_get(f"{ARGDATOS_URL}/finanzas/indices/inflacion").json())
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "valor"]].sort_values("fecha").reset_index(drop=True)


# (símbolo en Yahoo Finance, nombre, grupo, unidad)
INDICES = [
    ("^MERV", "Merval", "Argentina", "pesos"),
    ("^GSPC", "S&P 500", "Estados Unidos", "puntos"),
    ("^DJI", "Dow Jones", "Estados Unidos", "puntos"),
    ("^IXIC", "Nasdaq", "Estados Unidos", "puntos"),
    ("^FTSE", "FTSE 100", "Europa", "libras"),
    ("^GDAXI", "DAX", "Europa", "puntos"),
    ("^FCHI", "CAC 40", "Europa", "puntos"),
    ("^STOXX50E", "Euro Stoxx 50", "Europa", "puntos"),
    ("^N225", "Nikkei 225", "Asia", "yenes"),
    ("^HSI", "Hang Seng", "Asia", "puntos"),
    ("000001.SS", "Shanghái", "Asia", "puntos"),
    ("^BVSP", "Bovespa", "Latinoamérica", "reales"),
    ("^MXX", "IPC México", "Latinoamérica", "pesos mex."),
    ("GC=F", "Oro", "Materias primas", "USD/onza"),
    ("CL=F", "Petróleo WTI", "Materias primas", "USD/barril"),
    ("ZS=F", "Soja", "Materias primas", "US¢/bushel"),
]
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


def indice(simbolo: str, rango: str = "5y") -> pd.DataFrame:
    """Cierre diario de un índice o materia prima (Yahoo Finance, fuente no oficial). Columnas: fecha, valor."""
    resp = requests.get(f"{YAHOO_URL}/{requests.utils.quote(simbolo)}", params={"range": rango, "interval": "1d"},
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"},
                        timeout=TIMEOUT)
    resp.raise_for_status()
    res = resp.json()["chart"]["result"][0]
    df = pd.DataFrame({"fecha": pd.to_datetime(res["timestamp"], unit="s").normalize(),
                       "valor": res["indicators"]["quote"][0]["close"]})
    return df.dropna().drop_duplicates("fecha", keep="last").reset_index(drop=True)


COINGECKO_URL = "https://api.coingecko.com/api/v3"
CRIPTOYA_URL = "https://criptoya.com/api"


CRIPTOS = ("bitcoin", "ethereum", "tether", "binancecoin", "solana", "ripple", "usd-coin", "cardano", "dogecoin", "tron")


def cripto_mercado(ids: tuple[str, ...] = CRIPTOS) -> pd.DataFrame:
    """Criptomonedas conocidas, de mayor a menor capitalización (CoinGecko), con precio en USD y en pesos, variaciones
    de 24 h / 7 d / 30 d y la serie de 7 días para el mini-gráfico. Los pesos son opcionales: si fallan, quedan vacíos."""
    mercado = _get(f"{COINGECKO_URL}/coins/markets", vs_currency="usd", ids=",".join(ids), order="market_cap_desc",
                   per_page=len(ids), page=1, sparkline="true", price_change_percentage="24h,7d,30d").json()
    filas = [{
        "id": c["id"], "simbolo": str(c["symbol"]).upper(), "nombre": c["name"], "usd": c.get("current_price"),
        "cap": c.get("market_cap"), "volumen": c.get("total_volume"),
        "cambio_24h": c.get("price_change_percentage_24h_in_currency", c.get("price_change_percentage_24h")),
        "cambio_7d": c.get("price_change_percentage_7d_in_currency"),
        "cambio_30d": c.get("price_change_percentage_30d_in_currency"),
        "actualizado": c.get("last_updated"),
        "spark": ((c.get("sparkline_in_7d") or {}).get("price")) or [],
    } for c in mercado]
    df = pd.DataFrame(filas)
    df["ars"] = float("nan")
    try:
        ars = _get(f"{COINGECKO_URL}/coins/markets", vs_currency="ars", ids=",".join(df["id"])).json()
        precios = {c["id"]: c.get("current_price") for c in ars}
        df["ars"] = df["id"].map(precios).astype(float)
    except Exception:  # noqa: BLE001 — el precio en pesos es un extra, no debe tirar abajo todo el panel
        pass
    return df


YAHOO_CRIPTO = {"bitcoin": "BTC-USD", "ethereum": "ETH-USD", "tether": "USDT-USD", "binancecoin": "BNB-USD",
                "solana": "SOL-USD", "ripple": "XRP-USD", "usd-coin": "USDC-USD", "cardano": "ADA-USD",
                "dogecoin": "DOGE-USD", "tron": "TRX-USD"}


def cripto_historia(coin_id: str, dias: int = 365) -> pd.DataFrame:
    """Precio diario en USD de una criptomoneda (CoinGecko público: hasta 365 días hacia atrás). CoinGecko limita
    seguido la cantidad de pedidos: si rechaza, se usa el cierre diario de Yahoo Finance."""
    dias = min(int(dias), 365)
    try:
        payload = _get(f"{COINGECKO_URL}/coins/{coin_id}/market_chart", _intentos=1, vs_currency="usd",
                       days=dias, interval="daily").json()
        df = pd.DataFrame(payload["prices"], columns=["fecha", "valor"])
        df["fecha"] = pd.to_datetime(df["fecha"], unit="ms").dt.normalize()
        return df
    except Exception:
        if coin_id not in YAHOO_CRIPTO:
            raise
    df = indice(YAHOO_CRIPTO[coin_id], rango="1y")
    return df[df["fecha"] >= df["fecha"].max() - pd.Timedelta(days=dias)].reset_index(drop=True)


def usdt_exchanges() -> pd.DataFrame:
    """Precio del USDT en pesos en cada exchange argentino (CriptoYa): `compra` = lo que pagás para comprar USDT (ask),
    `venta` = lo que recibís si lo vendés (bid)."""
    payload = _get(f"{CRIPTOYA_URL}/usdt/ars/1").json()
    filas = [{"exchange": k, "compra": v.get("ask"), "venta": v.get("bid"), "hora": v.get("time")}
             for k, v in payload.items() if isinstance(v, dict) and v.get("ask") and v.get("bid")]
    df = pd.DataFrame(filas, columns=["exchange", "compra", "venta", "hora"])
    df["hora"] = pd.to_datetime(df["hora"], unit="s", errors="coerce")
    if len(df) >= 5:  # descarta precios absurdos (libros vacíos, errores): más de 8% lejos de la mediana
        for col in ("compra", "venta"):
            mediana = df[col].median()
            df = df[(df[col] - mediana).abs() <= 0.08 * mediana]
    return df.sort_values("compra").reset_index(drop=True)


def riesgo_pais() -> pd.DataFrame:
    df = pd.DataFrame(_get(f"{ARGDATOS_URL}/finanzas/indices/riesgo-pais").json())
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)


def tareas_principales(desde_bcra: str = "2016-01-01") -> dict:
    """Todas las series que carga la página al arrancar: clave -> función que la descarga. La usan app.py y la copia
    de respaldo (monitor/semilla.py), así las dos piden exactamente lo mismo."""
    tareas = {f"bcra:{k}": (lambda k=k: bcra(k, desde=desde_bcra)) for k in BCRA_IDS}
    tareas |= {f"serie:{k}": (lambda k=k: serie(k)) for k in SERIES_IDS}
    tareas["dolares"] = dolares
    tareas["riesgo_pais"] = riesgo_pais
    tareas["fx:EUR"] = lambda: divisa("EUR")
    tareas["fx:GBP"] = lambda: divisa("GBP")
    tareas["fred:ipc_eeuu"] = ipc_eeuu
    tareas["dolar_hist"] = dolar_historico
    tareas["inflacion_hist"] = inflacion_historica
    return tareas
