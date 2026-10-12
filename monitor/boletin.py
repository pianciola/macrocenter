"""Boletín semanal: lo corre GitHub Actions los lunes (ver .github/workflows/boletin.yml).

Arma el resumen de la semana (macrocenter/boletin.py) y lo deja como BORRADOR en Buttondown: no se manda a nadie hasta
que el dueño lo revisa y aprieta «Send» en buttondown.com. La clave de la API va como secreto del repositorio
(BUTTONDOWN_API_KEY), nunca en el código.

Sin la clave (por ejemplo, al correrlo a mano) solo guarda una vista previa en boletin_vista_previa.html.
"""
from __future__ import annotations

import html
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import requests  # noqa: E402

from macrocenter import boletin  # noqa: E402

API = "https://api.buttondown.com/v1/emails"


def main() -> int:
    asunto, cuerpo = boletin.armar()
    clave = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not clave:
        destino = Path(os.environ.get("BOLETIN_SALIDA", RAIZ / "boletin_vista_previa.html"))
        destino.write_text(f"<!doctype html><meta charset='utf-8'><title>{html.escape(asunto)}</title>{cuerpo}", encoding="utf-8")
        print(f"Sin BUTTONDOWN_API_KEY: vista previa en {destino}\nAsunto: {asunto}")
        return 0
    r = requests.post(API, timeout=60, json={"subject": asunto, "body": cuerpo, "status": "draft"},
                      headers={"Authorization": f"Token {clave}", "X-API-Version": "2026-04-01"})
    if r.status_code >= 300:
        print(f"Buttondown respondió {r.status_code}: {r.text[:300]}")
        return 1
    print(f"Borrador creado en Buttondown: {asunto}")
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(f"## Boletín semanal\n\nBorrador creado: **{asunto}**\n\n"
                    "Revisalo y mandalo desde buttondown.com → Emails → Drafts.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
