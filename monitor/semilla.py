"""Copia de respaldo de las series: la corre GitHub Actions cada 3 horas (ver .github/workflows/semilla.yml).

Baja las mismas series que la página (data.tareas_principales) y deja `semilla.json.gz` en la carpeta indicada
(por defecto, ./semilla). El workflow la publica en la rama `datos`; la página la usa al arrancar y cuando una fuente
falla (ver macrocenter/semilla.py).

Si una serie falla, se conserva la de la copia anterior. Si aun así faltan muchas, termina con error y no publica nada:
mejor una copia de hace unas horas que una incompleta. Solo baja datos públicos; nada de las visitas.
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from macrocenter import data, semilla  # noqa: E402

DESDE_BCRA = "2016-01-01"  # el mismo que usa app.py
MIN_COMPLETA = 0.9  # con menos del 90 % de las series no se publica


def main() -> int:
    salida = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "semilla")
    tareas = data.tareas_principales(DESDE_BCRA)

    def correr(item):
        nombre, fn = item
        try:
            d = data.limpiar(fn())
            return nombre, d if isinstance(d, pd.DataFrame) and not d.empty else None
        except Exception as e:  # noqa: BLE001
            print(f"falla {nombre}: {type(e).__name__}: {str(e)[:150]}")
            return nombre, None

    with ThreadPoolExecutor(max_workers=10) as pool:
        datos = dict(pool.map(correr, tareas.items()))
    faltan = [k for k, v in datos.items() if v is None]
    if faltan:
        anterior = semilla.bajar(set(tareas))
        if anterior:
            for k in faltan:
                if k in anterior[0]:
                    datos[k] = anterior[0][k]
                    print(f"{k}: se conserva el dato de la copia anterior ({anterior[1]:%d/%m %H:%M})")
    ok = {k: v for k, v in datos.items() if v is not None}
    print(f"{len(ok)} de {len(tareas)} series")
    if len(ok) < MIN_COMPLETA * len(tareas):
        print("Demasiadas series faltantes: no se publica la copia.")
        return 1
    salida.mkdir(parents=True, exist_ok=True)
    crudo = semilla.a_bytes(ok, datetime.now(timezone.utc))
    (salida / "semilla.json.gz").write_bytes(crudo)
    assert semilla.de_bytes(crudo) is not None, "la copia generada no se puede leer"
    print(f"semilla.json.gz: {len(crudo) / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
