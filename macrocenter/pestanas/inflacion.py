"""Pestaña «Inflación» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import charts, style


def mostrar(
    *, HOY, delta, dif, dol, dol_rec, get, grafico, grafico_periodo, infl_ia, infl_m, inflacion_distritos, ipim, ipp,
    kpi, rec, rem, ult_y_ant, ultimo, uva,
) -> None:
    st.markdown(style.intro("La inflación (**IPC** del INDEC), lo que espera el mercado para los próximos 12 meses (**REM** del BCRA) y la "
                            "**UVA**, la unidad que ajusta créditos y plazos fijos por inflación.",
                            [("bien", "La inflación baja"), ("mal", "Sube")]), unsafe_allow_html=True)
    k = st.columns(4)
    v, a_ = ult_y_ant(infl_m)
    kpi(k[0], "Inflación mensual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse")
    v, a_ = ult_y_ant(infl_ia)
    kpi(k[1], "Inflación interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse")
    v, a_ = ult_y_ant(rem)
    kpi(k[2], "Esperada 12 meses (REM)", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse",
        help="Mediana de lo que esperan los analistas del Relevamiento de Expectativas de Mercado.")
    kpi(k[3], "UVA", ultimo(uva) if uva is not None else None, 2, pre="$",
        d=delta(uva) if uva is not None else None, color="off", help="Sube con la inflación (CER), con unas semanas de rezago.")
    if infl_m is not None and infl_ia is not None:
        st.markdown("#### Inflación")
        m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
        a, b = st.columns(2)
        with a:
            grafico(charts.barras_y_linea(rec(m, 2), "valor_m", "valor_ia", "Inflación (IPC INDEC, %)",
                                          "Mensual", "Interanual"))
        with b:
            if rem is not None:
                x = m[["fecha", "valor_ia"]].rename(columns={"valor_ia": "Inflación interanual observada"})
                y = rem.rename(columns={"valor": "Expectativa 12 m (REM)"})
                grafico(charts.lineas(x.merge(y, on="fecha", how="outer").sort_values("fecha").pipe(rec, 2),
                                      {"Interanual observada": "Inflación interanual observada",
                                       "Expectativa 12 m (REM)": "Expectativa 12 m (REM)"},
                                      "Inflación interanual vs. expectativas del REM (%)", yfmt=",.0f"))
    if ipim is not None:
        mayoristas(ipim, ipp, infl_ia, dif, grafico, kpi, rec, ult_y_ant)
    inflacion_distritos()
    if infl_ia is not None and dol is not None:
        st.markdown("#### ¿El dólar le ganó a la inflación?")
        # dólar: último dato de cada mes y variación contra el mismo mes del año anterior (igual que la inflación interanual)
        dm = dol_rec[dol_rec["fecha"] <= HOY][["fecha", "oficial", "blue"]].copy()
        dm["mes"] = dm["fecha"].dt.to_period("M")
        dm = dm.groupby("mes").last()
        for c_ in ("oficial", "blue"):
            dm[c_] = dm[c_].pct_change(12) * 100
        ii = infl_ia[infl_ia["fecha"] <= HOY].assign(mes=lambda d: d["fecha"].dt.to_period("M")).set_index("mes")
        comp = dm.join(ii["valor"].rename("inflacion"), how="outer")
        # la fecha del punto es el fin de mes; el mes en curso (incompleto) queda en el último día con dato
        fin = comp.index.to_timestamp(how="end").normalize()
        comp["fecha"] = comp["fecha"].where(fin > HOY, fin).fillna(pd.Series(fin, index=comp.index))
        comp = comp.reset_index(drop=True)
        grafico_periodo("precios_dolar_infl", comp, lambda d: charts.lineas(
            d, {"Inflación interanual": "inflacion", "Dólar oficial": "oficial", "Dólar blue": "blue"},
            "Inflación vs. dólar — variación contra el mismo mes del año anterior (%)", yfmt=",.0f", height=340),
            mensual=True)
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "Si una línea del dólar queda por debajo de la inflación, el dólar subió menos que los precios: "
                            "en términos reales, se abarató."),
            ("Nota", "La inflación se publica con un mes de rezago.")), unsafe_allow_html=True)
    with st.expander("Índices de ajuste: UVA, CER, UVI e ICL"):
        pares = [("bcra:uva", "UVA (pesos)", ",.0f"), ("bcra:cer", "CER (base 2/2/2002 = 1)", ",.0f"),
                 ("bcra:uvi", "UVI (pesos)", ",.0f"), ("bcra:icl", "ICL — Índice para Contratos de Locación", ",.1f")]
        for fila in (pares[:2], pares[2:]):
            cols = st.columns(2)
            for col, (clave, titulo, fmt) in zip(cols, fila):
                d = get(clave)
                if d is not None:
                    with col:
                        grafico(charts.lineas(rec(d), {titulo: "valor"}, titulo, yfmt=fmt, height=320))


def _variaciones(df: pd.DataFrame) -> pd.DataFrame:
    """Un índice mensual -> variación del mes (%) y contra el mismo mes del año anterior (%)."""
    d = df.sort_values("fecha").copy()
    d["mensual"] = d["valor"].pct_change() * 100
    d["interanual"] = d["valor"].pct_change(12) * 100
    return d.dropna(subset=["mensual"])


def mayoristas(ipim: pd.DataFrame, ipp: pd.DataFrame | None, infl_ia: pd.DataFrame | None, dif, grafico, kpi, rec,
               ult_y_ant) -> None:
    """Precios mayoristas (INDEC): lo que cobran productores e importadores, antes de llegar al consumidor."""
    st.markdown("#### Precios mayoristas")
    vm = _variaciones(ipim)
    k = st.columns(3)
    v, a_ = ult_y_ant(vm, "mensual")
    kpi(k[0], "IPIM · mensual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse",
        help="Índice de precios internos al por mayor: lo que cobran los productores y los importadores en el mercado "
             "interno, con impuestos.")
    v, a_ = ult_y_ant(vm, "interanual")
    kpi(k[1], "IPIM · interanual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse")
    if ipp is not None:
        vp = _variaciones(ipp)
        v, a_ = ult_y_ant(vp, "mensual")
        kpi(k[2], "IPP · mensual", v, 1, suf="%", d=dif(v, a_), d_suf=" pp", d_txt="vs mes ant.", color="inverse",
            help="Índice de precios básicos del productor: igual que el IPIM, pero sin impuestos.")
    a, b = st.columns(2)
    with a:
        if ipp is not None:
            m = vm[["fecha", "mensual"]].rename(columns={"mensual": "IPIM"}).merge(
                _variaciones(ipp)[["fecha", "mensual"]].rename(columns={"mensual": "IPP"}), on="fecha", how="outer")
            grafico(charts.lineas(rec(m.sort_values("fecha"), 2), {"IPIM": "IPIM", "IPP": "IPP"},
                                  "Precios mayoristas: variación mensual (%)", yfmt=",.1f", height=340,
                                  colores=("#74ACDF", "#F6B40E")))
    with b:
        if infl_ia is not None:
            m = vm[["fecha", "interanual"]].rename(columns={"interanual": "Mayoristas (IPIM)"}).merge(
                infl_ia[["fecha", "valor"]].rename(columns={"valor": "Consumidores (IPC)"}), on="fecha", how="outer")
            grafico(charts.lineas(rec(m.sort_values("fecha"), 2),
                                  {"Mayoristas (IPIM)": "Mayoristas (IPIM)", "Consumidores (IPC)": "Consumidores (IPC)"},
                                  "Variación interanual: mayoristas y consumidores (%)", yfmt=",.0f", height=340,
                                  colores=("#74ACDF", "#A78BFA")))
    st.markdown(style.aclaracion(
        ("Qué mide", "El IPIM es lo que cobran los productores y los importadores en el mercado interno, con impuestos; "
                     "el IPP es lo mismo sin impuestos. Son precios anteriores a los que paga el consumidor: a veces "
                     "anticipan la inflación al consumidor, pero no siempre se trasladan."),
        ("Cómo leerlo", "Arriba, la suba de cada mes. Abajo, cuánto subieron respecto del mismo mes del año anterior, "
                        "comparado con la inflación al consumidor."),
        ("Fuente", "INDEC, Sistema de Índices de Precios Mayoristas, con datos de la API de datos.gob.ar. Se publica con "
                   "un mes de rezago.")), unsafe_allow_html=True)
