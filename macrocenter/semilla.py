"""Copia de respaldo de todas las series ("semilla").

GitHub Actions la arma cada 3 horas (monitor/semilla.py) y la publica en la rama `datos` del repositorio. La página
la usa en dos casos:
  - recién prendido el servidor (después de cada publicación o reinicio) no hay nada guardado: en vez de hacer esperar
    a la primera visita mientras se bajan ~60 series, arranca con la copia y actualiza de fondo;
  - si una fuente está caída, esa serie se muestra con su último dato de la copia en vez de quedar vacía.

Va en JSON comprimido (no en pickle): leerla nunca puede ejecutar código, aunque alguien la alterara. Solo trae datos
públicos de las fuentes oficiales; nada de las visitas.
"""
from __future__ import annotations

import gzip
import io
import json
from datetime import datetime

import pandas as pd
import requests

URL = "https://raw.githubusercontent.com/pianciola/macrocenter/datos/semilla.json.gz"
MAX_BYTES = 40_000_000  # descomprimida; la real ronda los 5 MB
VERSION = 1


def a_bytes(datos: dict, cuando: datetime) -> bytes:
    """Solo se guardan las series que llegaron bien (las fallas, que son textos, quedan afuera)."""
    series = {k: json.loads(v.to_json(orient="split", date_format="iso", index=False, double_precision=15))
              for k, v in datos.items() if isinstance(v, pd.DataFrame) and not v.empty and "fecha" in v.columns}
    cuerpo = json.dumps({"version": VERSION, "cuando": cuando.isoformat(), "series": series}, separators=(",", ":"))
    return gzip.compress(cuerpo.encode("utf-8"), compresslevel=9)


def de_bytes(crudo: bytes, claves: set[str] | None = None) -> tuple[dict[str, pd.DataFrame], datetime] | None:
    """(series, fecha de la copia), o None si el archivo no es válido. Con `claves`, ignora lo que no esté ahí."""
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(crudo)) as g:
            texto = g.read(MAX_BYTES + 1)
        if len(texto) > MAX_BYTES:
            return None
        cuerpo = json.loads(texto)
        if not isinstance(cuerpo, dict) or cuerpo.get("version") != VERSION:
            return None
        cuando = datetime.fromisoformat(str(cuerpo["cuando"]))
        if cuando.tzinfo is not None:  # se guarda con su zona: acá pasa a la hora local del servidor (como datetime.now())
            cuando = cuando.astimezone().replace(tzinfo=None)
        series = {}
        for k, v in dict(cuerpo["series"]).items():
            if claves is not None and k not in claves:
                continue
            if not isinstance(v, dict) or not isinstance(v.get("columns"), list) or "fecha" not in v["columns"]:
                continue
            df = pd.DataFrame(v.get("data") or [], columns=[str(c) for c in v["columns"]])
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.tz_localize(None)
            for c in df.columns:
                if c != "fecha":
                    df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna(subset=["fecha"])
            if not df.empty:
                series[str(k)] = df.sort_values("fecha").reset_index(drop=True)
        return (series, cuando) if series else None
    except Exception:  # noqa: BLE001 — una copia dañada o de otro formato se ignora
        return None


def bajar(claves: set[str] | None = None, timeout: float = 8) -> tuple[dict[str, pd.DataFrame], datetime] | None:
    """La copia publicada, o None si no se pudo bajar o no es válida (la página sigue como si no existiera)."""
    try:
        r = requests.get(URL, timeout=timeout)
        if r.status_code != 200 or len(r.content) > MAX_BYTES:
            return None
        return de_bytes(r.content, claves)
    except requests.RequestException:
        return None
