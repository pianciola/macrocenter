"""Alertas por mail: las corre GitHub Actions cada 30 minutos en horario de mercado (ver .github/workflows/alertas.yml).

Si el dólar o el riesgo país se movieron fuerte en el día (macrocenter/alertas.py), manda un mail por Buttondown SOLO a
los suscriptores con la etiqueta «alertas». Cada instrumento se avisa una vez por día.

Para no mandarle nunca una alerta a toda la lista del boletín por error, el mail se crea primero como BORRADOR con el
filtro de la etiqueta; se vuelve a leer y, solo si Buttondown confirma ese filtro, se manda. Si algo no cierra, queda
como borrador y el trabajo termina con error (GitHub le avisa al dueño).

La clave va como secreto del repositorio (BUTTONDOWN_API_KEY). Sin la clave solo muestra qué avisaría.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
import requests  # noqa: E402

from macrocenter import alertas, data  # noqa: E402

API = "https://api.buttondown.com/v1"
URL_TABLERO = "https://macrocenter-argentina.streamlit.app/?ver=tablero/dolar"


def headers(clave: str, mandar: bool = False) -> dict:
    h = {"Authorization": f"Token {clave}", "X-API-Version": "2026-04-01"}
    if mandar:
        h["X-Buttondown-Live-Dangerously"] = "true"
    return h


def id_etiqueta(clave: str) -> str | None:
    r = requests.get(f"{API}/tags", headers=headers(clave), timeout=60)
    r.raise_for_status()
    for t in r.json().get("results", []):
        if str(t.get("name", "")).strip().lower() == alertas.ETIQUETA:
            return str(t["id"])
    return None


def asuntos_recientes(clave: str) -> list[str]:
    r = requests.get(f"{API}/emails", headers=headers(clave), params={"ordering": "-creation_date"}, timeout=60)
    r.raise_for_status()
    return [str(e.get("subject", "")) for e in r.json().get("results", [])]


def filtro(tag_id: str) -> dict:
    return {"filters": [{"field": "subscriber.tags", "operator": "contains", "value": tag_id}], "groups": [],
            "predicate": "and"}


def filtro_confirmado(email: dict, tag_id: str) -> bool:
    f = email.get("filters") or {}
    hojas = f.get("filters") or []
    return (f.get("predicate") == "and" and not f.get("groups") and len(hojas) == 1
            and hojas[0].get("field") == "subscriber.tags" and hojas[0].get("operator") == "contains"
            and str(hojas[0].get("value")) == tag_id)


def anotar(texto: str) -> None:
    print(texto)
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(texto + "\n")


def main() -> int:
    hoy = pd.Timestamp(data.hoy_argentina())
    detectadas = alertas.detectar(data.dolares_ahora(), data.dolares(), data.riesgo_pais_ahora(), data.riesgo_pais(), hoy)
    clave = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not detectadas:
        anotar("Sin movimientos para avisar.")
        return 0
    if not clave:
        anotar("Sin BUTTONDOWN_API_KEY. Avisaría:\n" + "\n".join(alertas.frase(a) for a in detectadas))
        return 0

    avisadas = alertas.ya_avisadas(asuntos_recientes(clave), hoy)
    nuevas = [a for a in detectadas if a["nombre"] not in avisadas]
    if not nuevas:
        anotar("Ya se avisó hoy: " + ", ".join(sorted(avisadas)))
        return 0
    tag_id = id_etiqueta(clave)
    if not tag_id:
        anotar("Todavía nadie se anotó en las alertas (no existe la etiqueta): no se manda nada.")
        return 0

    hora = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=3)).strftime("%H:%M")
    asunto = alertas.asunto(nuevas, hoy)
    r = requests.post(f"{API}/emails", headers=headers(clave), timeout=60,
                      json={"subject": asunto, "body": alertas.cuerpo(nuevas, hora, URL_TABLERO), "status": "draft",
                            "filters": filtro(tag_id)})
    if r.status_code >= 300:
        anotar(f"❌ Buttondown no creó el borrador ({r.status_code}: {r.text[:300]}).")
        return 1
    email_id = r.json().get("id")
    leido = requests.get(f"{API}/emails/{email_id}", headers=headers(clave), timeout=60)
    if leido.status_code >= 300 or not filtro_confirmado(leido.json(), tag_id):
        anotar(f"❌ El borrador «{asunto}» no quedó filtrado por la etiqueta «{alertas.ETIQUETA}»: NO se mandó. "
               "Revisalo en buttondown.com → Emails → Drafts.")
        return 1
    r = requests.patch(f"{API}/emails/{email_id}", headers=headers(clave, mandar=True), timeout=60,
                       json={"status": "about_to_send"})
    if r.status_code >= 300:
        anotar(f"❌ Buttondown no mandó la alerta ({r.status_code}: {r.text[:300]}); quedó como borrador.")
        return 1
    anotar(f"✅ Alerta enviada a los anotados: {asunto}\n\n" + "\n".join(f"- {alertas.frase(a)}" for a in nuevas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
