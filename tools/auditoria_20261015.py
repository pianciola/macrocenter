r"""Sondas sin red de la auditoría. No modifica datos ni envía formularios.

Ejecutar desde la raíz: .venv\Scripts\python tools/auditoria_20261015.py
Los resultados describen defectos observados; no reemplazan la suite de tests.
"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from macrocenter.charts import csv_de
from macrocenter.inversiones import MONEDAS_PESOS, tabla_plataformas


def main():
    viejo = pd.DataFrame([{
        "fecha": pd.Timestamp("2020-01-01"), "moneda": "ARS",
        "apy": 25.0, "entidad": "belo",
    }])
    csv = csv_de([("TNA", ["=1+1"], [25.0])]).decode("utf-8-sig")
    print(json.dumps({
        "rendimientos_obsoletos": {
            "esperado_filas": 0,
            "obtenido_filas": len(tabla_plataformas(viejo, MONEDAS_PESOS)),
        },
        "formula_csv": {
            "esperado": "categoria neutralizada como texto",
            "obtenido": csv,
            "formula_sin_neutralizar": "\n=1+1;" in csv,
        },
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
