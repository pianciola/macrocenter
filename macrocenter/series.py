"""Cálculos por período calendario: los huecos no se tratan como observaciones."""
from __future__ import annotations
import pandas as pd


def cambio_periodico(df, col="valor", periodos=12, frecuencia="M"):
    d = df.copy().sort_values("fecha").drop_duplicates("fecha", keep="last")
    d["_periodo"] = d["fecha"].dt.to_period(frecuencia)
    s = d.drop_duplicates("_periodo", keep="last").set_index("_periodo")[col]
    referencia = s.reindex(d["_periodo"] - periodos).to_numpy()
    d[col] = (d[col].to_numpy() / pd.Series(referencia).replace(0, float("nan")).to_numpy() - 1) * 100
    return d.drop(columns="_periodo")


def comparar(df, col="valor", atras=1, meses=1, hoy=None):
    if df is None or "fecha" not in df or col not in df:
        return None, None
    hoy = pd.Timestamp(hoy) if hoy is not None else pd.Timestamp.now(tz="America/Argentina/Buenos_Aires").tz_localize(None).normalize()
    d = df[df["fecha"] <= hoy].dropna(subset=[col]).sort_values("fecha").drop_duplicates("fecha", keep="last")
    if d.empty:
        return None, None
    ultimo = d.iloc[-1]
    periodo = ultimo["fecha"].to_period("M") - atras * meses
    anterior = d[d["fecha"].dt.to_period("M") == periodo]
    return float(ultimo[col]), None if anterior.empty else float(anterior.iloc[-1][col])
