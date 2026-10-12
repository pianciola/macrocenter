"""Boletín semanal: lo corre GitHub Actions los lunes (ver .github/workflows/boletin.yml).

Arma el resumen de la semana (macrocenter/boletin.py) y lo manda por Buttondown a todos los suscriptores.
Queda como BORRADOR (sin mandarse) en dos casos, para que el dueño lo revise y lo mande desde buttondown.com:
  - si faltó algún dato (una fuente caída): mejor revisarlo que mandar un boletín incompleto;
  - si BOLETIN_ENVIAR no es "true" (el workflow lo pone en la corrida automática de los lunes y, a mano, solo si se
    tilda «enviar»: así no se manda dos veces la misma semana por error).
Si Buttondown rechaza el envío (por ejemplo, cuenta todavía sin aprobar), lo deja como borrador y termina con error:
GitHub le avisa al dueño por mail.

La clave de la API va como secreto del repositorio (BUTTONDOWN_API_KEY), nunca en el código. Sin la clave (por
ejemplo, al correrlo en la computadora) solo guarda una vista previa en boletin_vista_previa.html.
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


def crear(clave: str, asunto: str, cuerpo: str, estado: str) -> requests.Response:
    """Crea el mail en Buttondown. estado: "draft" (borrador) o "about_to_send" (se manda ya)."""
    headers = {"Authorization": f"Token {clave}", "X-API-Version": "2026-04-01"}
    if estado == "about_to_send":
        headers["X-Buttondown-Live-Dangerously"] = "true"  # confirmación que pide Buttondown para mandar por la API
    return requests.post(API, timeout=60, json={"subject": asunto, "body": cuerpo, "status": estado}, headers=headers)


def anotar(texto: str) -> None:
    print(texto)
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(texto + "\n")


def main() -> int:
    asunto, cuerpo, completo = boletin.armar()
    clave = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not clave:
        destino = Path(os.environ.get("BOLETIN_SALIDA", RAIZ / "boletin_vista_previa.html"))
        destino.write_text(f"<!doctype html><meta charset='utf-8'><title>{html.escape(asunto)}</title>{cuerpo}",
                           encoding="utf-8")
        print(f"Sin BUTTONDOWN_API_KEY: vista previa en {destino}\nAsunto: {asunto}\nCompleto: {completo}")
        return 0

    enviar = os.environ.get("BOLETIN_ENVIAR", "").strip().lower() == "true"
    if enviar and completo:
        r = crear(clave, asunto, cuerpo, "about_to_send")
        if r.status_code < 300:
            anotar(f"## Boletín semanal\n\n✅ **Enviado a los suscriptores:** {asunto}\n")
            return 0
        anotar(f"## Boletín semanal\n\n❌ Buttondown no aceptó el envío ({r.status_code}: {r.text[:300]}). "
               "Se intenta dejarlo como borrador para mandarlo a mano.\n")
        motivo, error = "no se pudo mandar", True
    elif enviar:
        motivo, error = "faltó algún dato esta semana (revisalo antes de mandarlo)", True
    else:
        motivo, error = "corrida manual", False

    r = crear(clave, asunto, cuerpo, "draft")
    if r.status_code >= 300:
        anotar(f"❌ Tampoco se pudo crear el borrador ({r.status_code}: {r.text[:300]}).")
        return 1
    titulo = "" if motivo == "no se pudo mandar" else "## Boletín semanal\n\n"
    anotar(f"{titulo}📝 **Quedó como borrador** ({motivo}): {asunto}\n\n"
           "Revisalo y mandalo desde buttondown.com → Emails → Drafts.\n")
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
