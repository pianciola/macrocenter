"""Ahorro e inversiones: tasas y plazos fijos (con la calculadora tradicional vs. UVA), rendimientos pasados y glosario.

Es una sección informativa: muestra datos, el pasado y simulaciones. No recomienda nada. Por eso las listas van
ordenadas por nombre (no por rendimiento), cada pantalla aclara qué no incluye y los colores siguen la regla de toda la
página: verde si le gana a la inflación, rojo si pierde contra ella.
"""
from __future__ import annotations

import math
import re

import pandas as pd
import streamlit as st

from . import charts, data, glosario, selector, style
from .avisos import falla
from .interactivo import entrada_monto

SECCIONES = ["Tasas y plazos fijos", "Rendimientos pasados", "Glosario"]
AVISO_TITULO = "Información, no recomendación"
AVISO = ("Tasas, resultados pasados y simulaciones para comparar opciones. No es asesoramiento financiero: antes de "
         "invertir, revisá las condiciones de cada producto y, si lo necesitás, consultá a un asesor registrado en la CNV.")


def _hoy() -> pd.Timestamp:
    return pd.Timestamp(data.hoy_argentina())


def _pct(x: float | None, dec: int = 1, signo: bool = False) -> str:
    if x is None or x != x:
        return "s/d"
    return ("+" if signo and x > 0.05 * 10 ** -dec else "") + charts.num(x, dec, "%")


def _ok(df) -> bool:
    return isinstance(df, pd.DataFrame) and not df.empty


def _ultimo(df, col: str = "valor") -> float | None:
    if not _ok(df):
        return None
    d = df[df["fecha"] <= _hoy()].dropna(subset=[col])
    return None if d.empty else float(d.iloc[-1][col])


def inflacion_esperada_mensual(rem) -> tuple[float | None, float | None]:
    """(inflación esperada para los próximos 12 meses, su equivalente mensual), ambas en %, según el REM del BCRA."""
    anual = _ultimo(rem)
    if anual is None:
        return None, None
    return anual, ((1 + anual / 100) ** (1 / 12) - 1) * 100


# ───────────────────────── nombres prolijos ─────────────────────────
_BANCOS = {
    "BANCO DE LA NACION ARGENTINA": "Banco Nación", "BANCO DE GALICIA Y BUENOS AIRES": "Galicia",
    "BANCO BBVA ARGENTINA": "BBVA", "BANCO SANTANDER ARGENTINA": "Santander",
    "BANCO DE LA PROVINCIA DE BUENOS AIRES": "Banco Provincia", "BANCO MACRO": "Macro",
    "INDUSTRIAL AND COMMERCIAL BANK OF CHINA": "ICBC", "BANCO DE LA CIUDAD DE BUENOS AIRES": "Banco Ciudad",
    "BANCO PATAGONIA": "Patagonia", "BANCO CREDICOOP": "Credicoop", "BANCO HIPOTECARIO": "Hipotecario",
    "BANCO DE LA PROVINCIA DE CORDOBA": "Bancor (Córdoba)", "BANCO DEL CHUBUT": "Banco del Chubut",
    "BANCO PROVINCIA DE TIERRA DEL FUEGO": "Banco de Tierra del Fuego", "UALA": "Ualá",
}
# los ocho bancos con más depósitos: su promedio es la referencia de «lo que paga un plazo fijo»
GRANDES = ("Banco Nación", "Banco Provincia", "Galicia", "BBVA", "Santander", "Macro", "ICBC", "Banco Ciudad")
_ACENTOS = {"NACION": "Nación", "CORDOBA": "Córdoba", "CREDITO": "Crédito", "COMPAÑIA": "Compañía",
            "COMPANIA": "Compañía", "CMF": "CMF", "BICA": "BICA", "VOII": "Voii"}
_MENORES = {"de", "del", "la", "las", "los", "y"}


def nombre_banco(crudo: str) -> str:
    t = re.sub(r"\s+", " ", str(crudo)).strip()
    sin = re.sub(r"\b(S\.?\s?A\.?\s?U?\.?|SOCIEDAD ANONIMA|SOCIEDAD ANÓNIMA|COOPERATIVO LIMITADO)\s*$", "", t,
                 flags=re.I).strip(" .,")
    sin = re.sub(r"\s*\(ARGE.*$", "", sin, flags=re.I).strip()
    for clave, lindo in _BANCOS.items():
        if sin.upper().startswith(clave):
            return lindo
    if sin != sin.upper():  # ya viene escrito con mayúsculas y minúsculas (Brubank, Banco Piano)
        return sin
    palabras = []
    for i, w in enumerate(sin.split()):
        wu = w.upper()
        palabras.append(_ACENTOS.get(wu) or (w.lower() if i and w.lower() in _MENORES else w.capitalize()))
    return " ".join(palabras)


_PLATAFORMAS = {"nexo": "Nexo", "fiwind": "Fiwind", "letsbit": "Let'sBit", "belo": "Belo", "lemoncash": "Lemon",
                "ripio": "Ripio", "satoshitango": "SatoshiTango", "lucamoney": "Luca", "decrypto": "Decrypto",
                "vesseo": "Vesseo", "astropay": "AstroPay", "lunefi": "Lunefi", "berry": "Berry", "buenbit": "Buenbit",
                "cocos": "Cocos", "prex": "Prex"}
MONEDAS_PESOS = {"ARS": "Pesos", "WARS": "Pesos (token wARS)", "ARGT": "Pesos (token ARGT)"}
MONEDAS_DOLAR = {"USD": "Dólares", "USDT": "USDT (dólar digital)", "USDC": "USDC (dólar digital)", "DAI": "DAI (dólar digital)"}


# ───────────────────────── cálculos ─────────────────────────
def tea_desde_tna(tna: float, dias: int = 30) -> float:
    """TEA (%) de una TNA (%) reinvirtiendo cada `dias` días."""
    return ((1 + tna / 100 * dias / 365) ** (365 / dias) - 1) * 100


def tabla_bancos(bancos: pd.DataFrame) -> pd.DataFrame:
    """Una fila por banco: nombre, TNA (la de clientes; si no informa, la de no clientes) y TEA. Por nombre."""
    b = bancos.copy()
    b["banco"] = b["entidad"].map(nombre_banco)
    b["tna"] = b["tna_clientes"].where(b["tna_clientes"] > 0, b["tna_no_clientes"])
    b = b[(b["tna"] > 0) & (b["tna"] < 300)].drop_duplicates("banco")
    b["tea"] = b["tna"].map(tea_desde_tna)
    return b.sort_values("banco", key=lambda s: s.str.lower()).reset_index(drop=True)


def promedio_grandes(tb: pd.DataFrame) -> float | None:
    g = tb[tb["banco"].isin(GRANDES)]
    return float(g["tna"].mean()) if len(g) >= 3 else (float(tb["tna"].mean()) if not tb.empty else None)


def tabla_plataformas(rend: pd.DataFrame, monedas: dict[str, str]) -> pd.DataFrame:
    """Rendimientos vigentes (informados en los últimos 21 días) en las monedas pedidas, por plataforma y moneda."""
    r = rend[rend["moneda"].isin(monedas)].copy()
    if r.empty:
        return r
    hoy = _hoy()
    r = r[r["fecha"].between(hoy - pd.Timedelta(days=21), hoy)]
    r = r[(r["apy"] > 0) & (r["apy"] < 200)]
    r["plataforma"] = r["entidad"].map(lambda e: _PLATAFORMAS.get(str(e).lower(), str(e).capitalize()))
    r["moneda_txt"] = r["moneda"].map(monedas)
    return r.sort_values(["plataforma", "moneda"], key=lambda s: s.str.lower()).reset_index(drop=True)


def rendimiento_fci(hoy: pd.DataFrame, antes: pd.DataFrame, max_fondos: int = 15) -> pd.DataFrame:
    """Fondos money market en pesos: rendimiento de los últimos ~30 días expresado como TNA, para los `max_fondos` con
    más patrimonio (los fondos chicos o sin datos recientes quedan afuera). Ordenados por nombre."""
    h = hoy[hoy["fecha"] >= hoy["fecha"].max() - pd.Timedelta(days=4)]
    h = h[~h["fondo"].str.contains(r"d[oó]lar|usd|u\$s", case=False, regex=True)]
    m = h.merge(antes[["fondo", "fecha", "vcp"]], on="fondo", suffixes=("", "_antes"))
    m["dias"] = (m["fecha"] - m["fecha_antes"]).dt.days
    m = m[(m["dias"] >= 20) & (m["dias"] <= 45) & (m["vcp_antes"] > 0)]
    m["tna"] = (m["vcp"] / m["vcp_antes"] - 1) * 365 / m["dias"] * 100
    m = m[(m["tna"] > 0) & (m["tna"] < 150)]
    # un mismo fondo tiene varias clases (A, B, H…) con distintas comisiones: queda la de más patrimonio
    m["base"] = m["fondo"].str.replace(r"\s*-\s*Clase\s+\w+\s*$", "", regex=True, case=False).str.strip()
    m = m.sort_values("patrimonio", ascending=False).drop_duplicates("base").head(max_fondos)
    return m.sort_values("fondo", key=lambda s: s.str.lower()).reset_index(drop=True)


def _serie_diaria(df: pd.DataFrame | None, idx: pd.DatetimeIndex, col: str = "valor") -> pd.Series | None:
    """La serie llevada a todos los días de `idx` (el último dato conocido de cada día). None si no hay dato al inicio."""
    if not _ok(df) or col not in df:
        return None
    s = df.dropna(subset=[col]).drop_duplicates("fecha", keep="last").set_index("fecha")[col].sort_index()
    s = s[s.index <= idx[-1]]
    if s.empty or s.index[0] > idx[0]:
        return None
    return s.reindex(s.index.union(idx)).ffill().reindex(idx)


def simular_plazo_fijo(tasas: pd.Series, idx: pd.DatetimeIndex, monto: float) -> pd.Series:
    """Plazo fijo renovado cada 30 días con la tasa de cada momento (`tasas`: TNA % por día). Entre renovaciones, el
    valor incluye el interés ganado hasta ese día."""
    valores, capital, inicio = [], monto, idx[0]
    tna = float(tasas.loc[inicio])
    for f in idx:
        while (f - inicio).days >= 30:
            capital *= 1 + tna / 100 * 30 / 365
            inicio += pd.Timedelta(days=30)
            tna = float(tasas.loc[inicio])
        valores.append(capital * (1 + tna / 100 * (f - inicio).days / 365))
    return pd.Series(valores, index=idx)


def alternativas(d: dict, desde: pd.Timestamp, monto: float) -> tuple[pd.DataFrame, dict, list[str]]:
    """Valor diario de `monto` invertido en `desde` en cada alternativa. Devuelve (tabla con fecha + una columna por
    alternativa + 'Inflación', {nombre: columna}, alternativas sin datos para ese período)."""
    hoy = _hoy()
    idx = pd.date_range(desde.normalize(), hoy, freq="D")
    out, faltan = pd.DataFrame({"fecha": idx}), []
    series: dict[str, str] = {}

    cer = _serie_diaria(d.get("cer"), idx)
    if cer is not None:
        out["Inflación"] = (monto * cer / cer.iloc[0]).to_numpy()

    dol = d.get("dolares")
    mep_v = _serie_diaria(dol, idx, "bolsa") if _ok(dol) and "bolsa" in dol else None
    mep_c = _serie_diaria(dol, idx, "bolsa_compra") if _ok(dol) and "bolsa_compra" in dol else None
    if mep_c is None:
        mep_c = mep_v

    def agregar(nombre: str, valores: pd.Series | None) -> None:
        if valores is None or valores.isna().all():
            faltan.append(nombre)
            return
        col = f"a{len(series)}"
        out[col] = valores.to_numpy()
        series[nombre] = col

    tasas = _serie_diaria(d.get("depositos_30d"), idx)
    agregar("Plazo fijo (renovado cada 30 días)", None if tasas is None else simular_plazo_fijo(tasas, idx, monto))
    uva = _serie_diaria(d.get("uva"), idx)
    agregar("Plazo fijo UVA (solo el ajuste)", None if uva is None else monto * uva / uva.iloc[0])
    agregar("Dólar MEP", None if mep_v is None else monto / mep_v.iloc[0] * mep_c)
    merval = _serie_diaria(d.get("merval"), idx)
    agregar("Acciones argentinas (Merval)", None if merval is None else monto * merval / merval.iloc[0])
    for clave, nombre in (("sp500", "Acciones de EE. UU. (S&P 500)"), ("bitcoin", "Bitcoin")):
        s = _serie_diaria(d.get(clave), idx)
        agregar(nombre, None if s is None or mep_v is None else monto / mep_v.iloc[0] * (s / s.iloc[0]) * mep_c)
    return out, series, faltan


def comparar_plazos(monto: float, dias: int, tna: float, tna_uva: float, infl_m: float) -> dict:
    """Plazo fijo tradicional (renovado cada 30 días a la misma tasa) contra uno UVA con una inflación mensual
    promedio `infl_m` (%). También la inflación de empate: con más, gana el UVA; con menos, el tradicional."""
    completos, resto = divmod(dias, 30)
    f_trad = (1 + tna / 100 * 30 / 365) ** completos * (1 + tna / 100 * resto / 365)
    extra = 1 + tna_uva / 100 * dias / 365

    def f_uva(pi: float) -> float:
        return (1 + pi / 100) ** (dias / 30) * extra

    empate = ((f_trad / extra) ** (30 / dias) - 1) * 100
    f_precios = (1 + infl_m / 100) ** (dias / 30)
    return {"trad": monto * f_trad, "uva": monto * f_uva(infl_m), "empate": empate, "f_uva": f_uva,
            "real_trad": (f_trad / f_precios - 1) * 100, "real_uva": (f_uva(infl_m) / f_precios - 1) * 100,
            "precios": monto * f_precios}


# ───────────────────────── pantallas ─────────────────────────
def _tono(real: float | None) -> str:
    """Verde si le ganó a la inflación, rojo si perdió; sin color si quedó prácticamente igual."""
    if real is None or abs(real) < 0.05:
        return ""
    return "ok" if real > 0 else "mal"


def _monto_txt(v: float) -> str:
    return charts.num(v, 0, pre="$")


def pantalla_tasas(d: dict) -> None:
    st.markdown(style.intro("Lo que pagan hoy los plazos fijos, los fondos money market y las billeteras y plataformas, comparado con "
               "la inflación que esperan las consultoras. Al final, una calculadora para comparar el plazo fijo tradicional "
               "con el UVA.", nota_md="Las listas van por orden alfabético, no por rendimiento."), unsafe_allow_html=True)
    rem_a, rem_m = inflacion_esperada_mensual(d.get("rem"))
    bancos, rend, fci_hoy, fci_antes = d.get("bancos"), d.get("rendimientos"), d.get("fci_hoy"), d.get("fci_antes")
    tb = tabla_bancos(bancos) if _ok(bancos) else None
    fondos = rendimiento_fci(fci_hoy, fci_antes) if _ok(fci_hoy) and _ok(fci_antes) else None

    # resumen arriba: plazo fijo, money market e inflación esperada
    fichas = []
    prom = promedio_grandes(tb) if tb is not None and not tb.empty else None
    if prom is not None:
        tea = tea_desde_tna(prom)
        tono = "" if rem_a is None else ("ok" if tea > rem_a else "mal")
        fichas.append(("Plazo fijo · bancos grandes", f"TNA {_pct(prom)}",
                       f"TEA {_pct(tea)} · promedio de {', '.join(GRANDES[:4])} y otros", tono))
    if fondos is not None and not fondos.empty:
        med = float(fondos["tna"].median())
        tono = "" if rem_a is None else ("ok" if tea_desde_tna(med, 1) > rem_a else "mal")
        fichas.append(("Fondos money market", f"TNA {_pct(med)}",
                       f"mediana de los {len(fondos)} más grandes · últimos 30 días", tono))
    if rem_a is not None:
        fichas.append(("Inflación esperada", f"{_pct(rem_a)} anual", f"≈ {_pct(rem_m, 2)} por mes · REM del BCRA", ""))
    if fichas:
        st.markdown(style.resultado_final(fichas), unsafe_allow_html=True)
        st.markdown(style.aclaracion(
            ("Nota", "Se compara con la inflación que **esperan** las consultoras para los próximos 12 meses: es una "
                    "referencia, no una garantía. La inflación real puede ser otra."),
            leyenda=[("bien", "La tasa anual efectiva le gana a esa inflación"), ("mal", "Queda abajo")]),
            unsafe_allow_html=True)

    # plazo fijo por banco
    st.markdown("#### Plazo fijo a 30 días, banco por banco")
    if tb is None or tb.empty:
        falla(f"no se pudieron cargar las tasas de los bancos ({bancos if isinstance(bancos, str) else 'sin datos'})")
    else:
        c1, _ = st.columns([1, 2])
        monto = entrada_monto(c1, "Monto para calcular cuánto rinde", "inv_monto_pf", 1_000_000)
        cab = ["Banco", "TNA", "TEA", f"Interés en 30 días ({_monto_txt(monto)})"]

        def filas(t: pd.DataFrame) -> list:
            out = []
            for _, r in t.iterrows():
                gana = None if rem_a is None else r["tea"] > rem_a
                out.append([r["banco"], _pct(r["tna"], 2),
                            (_pct(r["tea"], 2), "" if gana is None else "mejor" if gana else "peor"),
                            _monto_txt(monto * r["tna"] / 100 * 30 / 365)])
            return out

        grandes, resto = tb[tb["banco"].isin(GRANDES)], tb[~tb["banco"].isin(GRANDES)]
        if grandes.empty:
            grandes, resto = tb, tb.iloc[0:0]
        st.markdown(style.tabla(cab, filas(grandes)), unsafe_allow_html=True)
        if not resto.empty:
            with st.expander(f"Ver los otros {len(resto)} bancos y financieras"):
                st.markdown(style.tabla(cab, filas(resto)), unsafe_allow_html=True)
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "**TNA**: la tasa que publica el banco. **TEA**: lo que rinde en un año renovando cada 30 días. "
                            "Es la tasa para clientes (si el banco no la informa, la de no clientes)."),
            ("Protección", "Los plazos fijos están cubiertos por el seguro de depósitos hasta el tope que fija el BCRA."),
            ("No incluye", "Impuestos."),
            ("Fuente", "Lo que cada banco informa al BCRA."),
            leyenda=[("bien", "La TEA le gana a la inflación esperada"), ("mal", "Queda abajo")]), unsafe_allow_html=True)

    # fondos money market
    st.markdown("#### Fondos money market (rescate inmediato)")
    if fondos is None or fondos.empty:
        falla("no se pudieron calcular los rendimientos de los fondos")
    else:
        filas = []
        for _, r in fondos.iterrows():
            tea = tea_desde_tna(float(r["tna"]), 1)
            gana = None if rem_a is None else tea > rem_a
            filas.append([r["fondo"], _pct(r["tna"], 2),
                          (_pct(tea, 2), "" if gana is None else "mejor" if gana else "peor"),
                          charts.num(r["patrimonio"] / 1e9, 0, pre="$", suf=" mil M")])
        st.markdown(style.tabla(["Fondo", "TNA (30 días)", "TEA", "Patrimonio"], filas), unsafe_allow_html=True)
        st.markdown(style.aclaracion(
            ("Cómo leerlo", f"Los {len(fondos)} fondos money market en pesos con más patrimonio. El rendimiento es el de "
                            "los últimos 30 días, llevado a tasa anual: el de los próximos días puede ser otro. Muchas "
                            "cuentas remuneradas de billeteras invierten en este tipo de fondos."),
            ("Protección", "Los fondos **no** están cubiertos por el seguro de depósitos."),
            ("Fuente", "CAFCI (Cámara Argentina de Fondos Comunes de Inversión)."),
            leyenda=[("bien", "La TEA le gana a la inflación esperada"), ("mal", "Queda abajo")]), unsafe_allow_html=True)

    # billeteras y plataformas
    st.markdown("#### Billeteras y plataformas")
    if not _ok(rend):
        falla("no se pudieron cargar los rendimientos de las plataformas")
    else:
        a, b = st.columns(2)
        for slot, monedas, titulo in ((a, MONEDAS_PESOS, "En pesos"), (b, MONEDAS_DOLAR, "En dólares")):
            t = tabla_plataformas(rend, monedas)
            with slot:
                st.markdown(f"**{titulo}**")
                if t.empty:
                    st.caption("Sin datos vigentes.")
                else:
                    st.markdown(style.tabla(["Plataforma", "Moneda", "Rendimiento anual", "Dato de"],
                                            [[r["plataforma"], r["moneda_txt"], _pct(r["apy"], 2),
                                              r["fecha"].strftime("%d/%m/%Y")] for _, r in t.iterrows()]),
                                unsafe_allow_html=True)
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "El rendimiento anual que informa cada plataforma (en su mayoría, empresas cripto). Puede "
                            "cambiar todos los días y tener topes o condiciones."),
            ("Protección", "No son depósitos bancarios: no los cubre el seguro de depósitos y dependen de la solidez de "
                           "cada empresa.")), unsafe_allow_html=True)


PERIODOS = {"1 mes": 30, "3 meses": 91, "6 meses": 182, "1 año": 365, "2 años": 730, "3 años": 1095, "5 años": 1826}


def pantalla_historica(d: dict, grafico) -> None:
    st.markdown(style.intro(
        "Elegí un **monto** y **desde cuándo**, y mirá cuánto tendrías hoy si lo hubieras puesto en cada alternativa "
        "(plazo fijo, UVA, dólar, acciones, bitcoin) y si le ganó a la inflación.",
        [("bien", "Le ganó a la inflación"), ("mal", "Perdió contra ella")],
        "Es el pasado: no dice nada de lo que va a pasar."), unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    monto = entrada_monto(c1, "Monto inicial", "inv_monto_hist", 1_000_000)
    with c2:
        per = selector.uno(st.pills, "Desde hace", list(PERIODOS), "per_inv_hist", "1 año")
    desde = _hoy() - pd.Timedelta(days=PERIODOS[per])
    tabla, series, faltan = alternativas(d, desde, monto)
    if not series:
        falla("no hay datos para «Rendimientos pasados» en este período")
        return
    infl_final = float(tabla["Inflación"].iloc[-1]) if "Inflación" in tabla else None

    fichas = []
    for nombre, col in series.items():
        final = float(tabla[col].dropna().iloc[-1])
        nominal = (final / monto - 1) * 100
        real = None if infl_final is None else (final / infl_final - 1) * 100
        detalle = f"{_pct(nominal, 1, True)} en pesos" + ("" if real is None else f" · {_pct(real, 1, True)} contra la inflación")
        fichas.append((nombre, _monto_txt(final), detalle, _tono(real)))
    if infl_final is not None:
        st.markdown(style.nota_destacada(
            f"Para no perder contra la inflación ({per})", _monto_txt(infl_final),
            f"Es lo que tenías que tener hoy para comprar lo mismo que con {_monto_txt(monto)} en "
            f"{desde.strftime('%d/%m/%Y')}: los precios subieron **{_pct((infl_final / monto - 1) * 100)}**."),
            unsafe_allow_html=True)
    st.markdown(style.resultado_final(fichas), unsafe_allow_html=True)

    grafico(charts.evolucion_montos(tabla[::max(1, len(tabla) // 400)] if len(tabla) > 800 else tabla, series,
                                    "Inflación" if infl_final is not None else None,
                                    f"Cuánto valdrían {_monto_txt(monto)} invertidos hace {per}"), key="graf_inv_hist")
    st.markdown(style.aclaracion(
        ("Supuestos", "El plazo fijo usa la tasa promedio a 30 días del BCRA y se renueva cada mes. El UVA muestra solo "
                      "el ajuste por inflación (los bancos suman una tasa chica). El dólar MEP se compra al precio de "
                      "venta y se vende al de compra. Las acciones de EE. UU. y el bitcoin se pasan a pesos con el MEP."),
        ("Inflación", "Se mide con el CER, que sigue al IPC con unas semanas de rezago."),
        ("No incluye", "Impuestos ni comisiones."),
        ("Fuente", "BCRA; bolsas y bitcoin: Yahoo Finance (fuente no oficial)."),
        ("Sin datos", ", ".join(faltan) if faltan else ""),
        leyenda=[("bien", "Terminó arriba de la inflación (ganó poder de compra)"), ("mal", "Quedó abajo")]),
        unsafe_allow_html=True)


def comparar_dolar_inflacion(d: dict, grafico_periodo) -> None:
    """Comparación interanual trasladada desde Inflación a Rendimientos pasados."""
    HOY = _hoy()
    infl_ia, dol = d.get("infl_ia"), d.get("dolares")
    dol_rec = dol.dropna(subset=["oficial"]) if _ok(dol) else None
    if _ok(infl_ia) and _ok(dol_rec):
        st.markdown("#### ¿El dólar le ganó a la inflación?")
        # dólar: último dato de cada mes y variación contra el mismo mes del año anterior (igual que la inflación interanual)
        dm = dol_rec[dol_rec["fecha"] <= HOY][["fecha", "oficial", "blue"]].copy()
        dm["mes"] = dm["fecha"].dt.to_period("M")
        dm = dm.groupby("mes").last()
        if not dm.empty:
            dm = dm.reindex(pd.period_range(dm.index.min(), dm.index.max(), freq="M"))
        for c_ in ("oficial", "blue"):
            dm[c_] = dm[c_].pct_change(12, fill_method=None) * 100
        ii = infl_ia[infl_ia["fecha"] <= HOY].assign(mes=lambda d: d["fecha"].dt.to_period("M")).set_index("mes")
        comp = dm.join(ii["valor"].rename("inflacion"), how="outer")
        # la fecha del punto es el fin de mes; el mes en curso (incompleto) queda en el último día con dato
        fin = comp.index.to_timestamp(how="end").normalize()
        comp["fecha"] = comp["fecha"].where(fin > HOY, fin).fillna(pd.Series(fin, index=comp.index))
        comp = comp.reset_index(drop=True)
        grafico_periodo("inv_dolar_infl", comp, lambda d: charts.lineas(
            d, {"Inflación interanual": "inflacion", "Dólar oficial": "oficial", "Dólar blue": "blue"},
            "Inflación vs. dólar — variación contra el mismo mes del año anterior (%)", yfmt=",.0f", height=340),
            mensual=True)
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "Si una línea del dólar queda por debajo de la inflación, el dólar subió menos que los precios: "
                            "en términos reales, se abarató."),
            ("Nota", "La inflación se publica con un mes de rezago.")), unsafe_allow_html=True)


def pantalla_uva(d: dict, grafico) -> None:
    """Calculadora tradicional vs. UVA: va al final de «Tasas y plazos fijos»."""
    st.markdown("#### ¿Plazo fijo tradicional o UVA?")
    st.markdown("Uno paga una tasa fija; el otro se ajusta por inflación. Cuál termina con más plata depende de la "
                "inflación que venga, que nadie sabe: esta calculadora muestra a partir de qué inflación uno supera al otro.")
    rem_a, rem_m = inflacion_esperada_mensual(d.get("rem"))
    tb = tabla_bancos(d["bancos"]) if _ok(d.get("bancos")) else None
    tna_ref = promedio_grandes(tb) if tb is not None and not tb.empty else _ultimo(d.get("depositos_30d"))

    c1, c2, c3 = st.columns(3)
    monto = entrada_monto(c1, "Monto", "inv_monto_uva", 1_000_000)
    with c2:
        dias = selector.uno(st.segmented_control, "Plazo (días)", [90, 180, 270, 365], "inv_dias", 180,
                            help="El plazo fijo UVA tiene un plazo mínimo de 90 días.")
    with c3:
        tna = st.number_input("TNA del plazo fijo tradicional (%)", 0.0, 300.0, round(tna_ref or 30.0, 2), 0.25,
                              format="%.2f", key="inv_tna",
                              help="Por defecto, el promedio de los bancos grandes hoy. Podés poner la de tu banco.")
    c4, c5 = st.columns(2)
    with c4:
        tna_uva = st.number_input("Tasa adicional del UVA (TNA %)", 0.0, 20.0, 1.0, 0.25, format="%.2f",
                                  key="inv_tna_uva", help="La tasa chica que los bancos pagan encima del ajuste por UVA.")
    with c5:
        defecto = round(rem_m, 1) if rem_m is not None else 2.0
        infl = st.slider("Inflación mensual promedio que suponés (%)", 0.0, 10.0, min(max(defecto, 0.0), 10.0), 0.1,
                         key="inv_infl", help="Por defecto, la que esperan las consultoras (REM del BCRA).")

    r = comparar_plazos(monto, int(dias), float(tna), float(tna_uva), float(infl))
    gana_uva = r["uva"] > r["trad"]
    fichas = [("Plazo fijo tradicional", _monto_txt(r["trad"]),
               f"{_pct(r['real_trad'], 1, True)} contra la inflación supuesta", _tono(r["real_trad"])),
              ("Plazo fijo UVA", _monto_txt(r["uva"]),
               f"{_pct(r['real_uva'], 1, True)} contra la inflación supuesta", _tono(r["real_uva"]))]
    st.markdown(style.resultado_final(fichas), unsafe_allow_html=True)
    dif = abs(r["uva"] - r["trad"])
    st.markdown(style.nota_destacada(
        "Inflación de empate", f"{_pct(r['empate'], 2)} por mes",
        f"Con una inflación promedio mayor a esa en los próximos {dias} días, el **UVA** termina con más plata; con una "
        f"menor, el **tradicional**. Con la que pusiste ({_pct(infl, 1)} por mes) quedaría adelante el "
        f"**{'UVA' if gana_uva else 'tradicional'}**, por {_monto_txt(dif)}."
        + ("" if rem_m is None else f" Las consultoras esperan {_pct(rem_m, 2)} por mes ({_pct(rem_a)} en 12 meses).")),
        unsafe_allow_html=True)

    tope = max(4.0, math.ceil(max(r["empate"], infl, rem_m or 0) * 2))
    xs = [round(i * 0.05, 2) for i in range(int(tope / 0.05) + 1)]
    grafico(charts.equilibrio_uva(xs, [r["trad"]] * len(xs), [monto * r["f_uva"](x) for x in xs], rem_m, r["empate"],
                                  f"Cuánto tendrías a los {dias} días según la inflación mensual promedio"), key="graf_inv_uva")
    st.markdown(style.aclaracion(
        ("Cómo leerlo", "La línea del tradicional es plana: no depende de la inflación. La del UVA sube con ella. Donde "
                        "se cruzan está la inflación de empate."),
        ("Supuestos", "El tradicional se renueva cada 30 días a la misma tasa. El UVA ajusta por la inflación promedio "
                      "que elegiste más la tasa adicional (en la práctica, la UVA sigue al IPC con unas semanas de rezago)."),
        ("Protección", "Los dos están cubiertos por el seguro de depósitos."),
        ("No incluye", "Impuestos.")), unsafe_allow_html=True)


EXTRAS = {
    "Cuenta remunerada": "Una cuenta (de banco o de billetera) que paga intereses por el saldo, día a día, y deja sacar "
                         "la plata cuando quieras. Muchas billeteras invierten esos saldos en fondos money market.",
    "Caución": "Un préstamo de muy corto plazo (desde un día) que se hace a través de la bolsa, con garantía de títulos. "
               "Se opera desde una cuenta en un agente de bolsa y la tasa se conoce al momento de hacerla.",
    "LECAP": "Letras del Tesoro en pesos, de corto plazo y tasa fija: se compran por menos de lo que pagan al vencimiento, "
             "y esa diferencia es la ganancia. Se compran y venden en la bolsa.",
    "Seguro de depósitos": "Cubre los plazos fijos y las cuentas en bancos, en pesos y en dólares, hasta un monto por "
                           "persona y por banco que fija el BCRA. No cubre fondos comunes, acciones, bonos ni saldos en "
                           "plataformas cripto.",
    "Rendimiento pasado": "Lo que rindió algo antes no dice cuánto va a rendir después. Los períodos buenos y malos se "
                          "alternan, y una racha puede cortarse en cualquier momento.",
    "Perfil de inversor": "Cuánto riesgo puede y quiere asumir una persona según su edad, sus ingresos, sus objetivos y "
                          "el plazo. Bancos y agentes de bolsa lo piden antes de dejar operar.",
}
GRUPOS = [
    ("Tasas e intereses", ["TNA", "TEA", "Tasa real", "Interés compuesto", "Regla del 72", "CFT"]),
    ("Dónde poner los pesos", ["Plazo fijo", "Plazo fijo UVA", "Cuenta remunerada", "Fondo común de inversión",
                               "Money market", "Caución", "LECAP", "Bono CER"]),
    ("Dólares y bolsa", ["Dólar MEP", "Bono", "Acción", "Dividendo", "CEDEAR", "Merval", "S&P 500", "Stablecoin"]),
    ("Antes de invertir", ["Riesgo", "Volatilidad", "Liquidez", "Diversificación", "Fondo de emergencia",
                           "Seguro de depósitos", "Rendimiento pasado", "Perfil de inversor"]),
]


def pantalla_conceptos() -> None:
    st.markdown(style.intro("Las palabras que aparecen cuando se habla de ahorro e inversiones, explicadas en dos líneas."), unsafe_allow_html=True)
    defs = dict(glosario.TERMINOS) | EXTRAS
    grupos = [(g, [(t, defs[t]) for t in terminos if t in defs]) for g, terminos in GRUPOS]
    st.markdown(style.conceptos([(g, items) for g, items in grupos if items]), unsafe_allow_html=True)


def mostrar(d: dict, grafico, grafico_periodo) -> None:
    """Pantalla completa. `d`: las series y tablas (ver app.py); `grafico`: la función de la app que dibuja figuras."""
    st.markdown(style.aviso(AVISO, AVISO_TITULO), unsafe_allow_html=True)
    sec = selector.uno(st.segmented_control, "Sección", SECCIONES, "inv_seccion", label_visibility="collapsed")
    if sec == "Tasas y plazos fijos":
        pantalla_tasas(d)
        pantalla_uva(d, grafico)
    elif sec == "Rendimientos pasados":
        pantalla_historica(d, grafico)
        comparar_dolar_inflacion(d, grafico_periodo)
    else:
        pantalla_conceptos()
