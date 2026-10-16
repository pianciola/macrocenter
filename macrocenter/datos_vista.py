"""Metadatos visibles de las observaciones, sin consultas adicionales de red."""
from __future__ import annotations

from html import escape
import pandas as pd


def detalle(serie, fuente: str, *, hoy=None, max_dias: int | None = None) -> str:
    if not isinstance(serie, pd.DataFrame) or "fecha" not in serie:
        return f'<div class="mc-dato-meta"><span>{escape(fuente)}</span><span>Fecha no disponible</span></div>' if fuente else ""
    hoy = pd.Timestamp(hoy) if hoy is not None else pd.Timestamp.now(tz="America/Argentina/Buenos_Aires")
    hoy = hoy.tz_localize(None).normalize() if hoy.tzinfo else hoy.normalize()
    fechas = pd.to_datetime(serie["fecha"], errors="coerce", utc=True).dt.tz_localize(None)
    fechas = fechas.dropna().drop_duplicates().sort_values()
    fechas = fechas[fechas <= hoy + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)]
    if fechas.empty:
        return f'<div class="mc-dato-meta"><span>{escape(fuente)}</span><span>Fecha no disponible</span></div>'
    paso = fechas.diff().dt.total_seconds().div(86400).median() if len(fechas) > 1 else float("nan")
    limite = max_dias if max_dias is not None else (10 if paso <= 3 else 100 if paso <= 45 else 180 if paso <= 120 else 550)
    ultima = fechas.iloc[-1]
    aviso = '<span class="mc-dato-atrasado">Dato con rezago</span>' if (hoy - ultima.normalize()).days > limite else ""
    return (f'<div class="mc-dato-meta"><span>{escape(fuente)}</span>'
            f'<span>Dato: {ultima:%d/%m/%Y}</span>{aviso}</div>')
