"""Noticias oficiales del BCRA y del Ministerio de Economía.

Ninguno de los dos organismos ofrece API ni RSS de noticias, así que se leen sus sitios públicos (HTML).
Cada fuente tiene varias rutas, que se prueban en orden hasta que una devuelve notas:

  BCRA          1) listado /noticias/   2) listado /category/noticias/   3) sitemap + metadatos de cada nota
  Economía      1) listado /economia/noticias   2) portada /economia + metadatos de cada nota

Si todas fallan, se levanta un error con el detalle: la app no lo muestra (queda registrado) y la ventana de noticias sigue con lo que haya.
Solo se toman título, fecha, bajada y enlace; la nota completa se lee en el sitio original.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (MacroCenter; tablero personal)"}
TIMEOUT = 30

BCRA_URL = "https://www.bcra.gob.ar/noticias/"
BCRA_URL_ALT = "https://www.bcra.gob.ar/category/noticias/"
BCRA_SITEMAP = "https://www.bcra.gob.ar/post-sitemap.xml"
ECONOMIA_URL = "https://www.argentina.gob.ar/economia/noticias"
ECONOMIA_PORTADA = "https://www.argentina.gob.ar/economia"
ECONOMIA_BASE = "https://www.argentina.gob.ar"

MESES = {m: i for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
     "noviembre", "diciembre"], start=1)}


HOSTS_PERMITIDOS = {"www.bcra.gob.ar", "bcra.gob.ar", "www.argentina.gob.ar", "argentina.gob.ar"}


def url_segura(url: str | None) -> bool:
    """Solo se enlazan páginas https de los dominios oficiales esperados (nunca javascript:, data:, otros sitios...)."""
    try:
        p = urlparse(url or "")
        return p.scheme == "https" and (p.hostname or "") in HOSTS_PERMITIDOS
    except ValueError:
        return False


@dataclass(frozen=True)
class Noticia:
    fuente: str
    fecha: datetime
    titulo: str
    resumen: str
    url: str
    etiquetas: str = ""


# ───────────────────────── utilidades ─────────────────────────
def _html(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    r.encoding = "utf-8"
    return BeautifulSoup(r.text, "html.parser")


def _texto(nodo) -> str:
    return re.sub(r"\s+", " ", nodo.get_text(" ", strip=True)).strip() if nodo else ""


def _fecha_es(texto: str) -> datetime:
    """'08 de octubre de 2026' -> datetime."""
    m = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", texto.lower())
    if not m or m.group(2) not in MESES:
        raise ValueError(f"fecha no reconocida: {texto!r}")
    return datetime(int(m.group(3)), MESES[m.group(2)], int(m.group(1)))


def _meta(s: BeautifulSoup, *nombres: str) -> str | None:
    for n in nombres:
        t = s.find("meta", attrs={"property": n}) or s.find("meta", attrs={"name": n})
        if t and t.get("content"):
            return t["content"].strip()
    return None


def _desde_pagina(url: str, fuente: str, sufijo_titulo: str = "") -> Noticia | None:
    """Arma una Noticia leyendo los metadatos (og:title, og:description, fecha) de la página de la nota."""
    try:
        s = _html(url)
        titulo = _meta(s, "og:title", "twitter:title")
        publicada = _meta(s, "article:published_time")
        t = s.find("time")
        if not publicada and t is not None and t.get("datetime"):
            publicada = t["datetime"].replace(" ", "T")
        if not titulo or not publicada:
            return None
        if sufijo_titulo and titulo.endswith(sufijo_titulo):
            titulo = titulo[: -len(sufijo_titulo)].rstrip()
        fecha = datetime.fromisoformat(publicada).replace(tzinfo=None)
        resumen = re.sub(r"[*_]{1,3}", "", _meta(s, "og:description", "description") or "")
        return Noticia(fuente, fecha, titulo, re.sub(r"\s+", " ", resumen).strip(), url)
    except Exception:  # noqa: BLE001 — una nota que falla no debe tirar abajo a las demás
        return None


def _desde_paginas(urls: list[str], fuente: str, sufijo_titulo: str = "") -> list[Noticia]:
    with ThreadPoolExecutor(max_workers=6) as pool:
        notas = pool.map(lambda u: _desde_pagina(u, fuente, sufijo_titulo), urls)
    return [n for n in notas if n]


def _con_respaldo(rutas: list[tuple[str, Callable[[], list[Noticia]]]], limite: int) -> list[Noticia]:
    """Prueba las rutas en orden y devuelve las notas de la primera que funcione."""
    errores = []
    for nombre, fn in rutas:
        try:
            notas = fn()
        except Exception as e:  # noqa: BLE001
            errores.append(f"{nombre}: {type(e).__name__}: {e}")
            continue
        # el contenido viene de afuera: solo enlaces https oficiales y textos de largo razonable
        notas = [replace(n, titulo=n.titulo[:300], resumen=n.resumen[:600]) for n in notas if url_segura(n.url)]
        if notas:
            return sorted(notas, key=lambda n: n.fecha, reverse=True)[:limite]
        errores.append(f"{nombre}: sin notas")
    raise RuntimeError(" | ".join(errores))


# ───────────────────────── BCRA ─────────────────────────
def _bcra_listado(url: str) -> list[Noticia]:
    out = []
    for art in _html(url).find_all("article"):
        a = art.select_one("h2.entry-title a")
        fecha = art.select_one(".published")
        if not a or not fecha:
            continue
        out.append(Noticia(
            fuente="BCRA",
            fecha=_fecha_es(_texto(fecha)),
            titulo=_texto(a),
            resumen=_texto(art.select_one(".post-content-inner")),
            url=a["href"],
            etiquetas=", ".join(t for t in (x.strip() for x in _texto(art.select_one(".post-categories")).split(","))
                                if t and t != "Noticias"),
        ))
    return out


def _bcra_sitemap(cuantas: int = 14) -> list[Noticia]:
    """Último recurso: las notas más recientemente modificadas del sitemap, leídas una por una."""
    r = requests.get(BCRA_SITEMAP, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    entradas = re.findall(r"<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", r.text)
    urls = [(u, m) for u, m in entradas if "/noticias/" in u and "/en/" not in u]
    urls.sort(key=lambda x: x[1], reverse=True)
    return _desde_paginas([u for u, _ in urls[:cuantas]], "BCRA", sufijo_titulo="| BCRA")


def bcra(limite: int = 12) -> list[Noticia]:
    return _con_respaldo([
        ("listado /noticias/", lambda: _bcra_listado(BCRA_URL)),
        ("listado /category/noticias/", lambda: _bcra_listado(BCRA_URL_ALT)),
        ("sitemap", _bcra_sitemap),
    ], limite)


# ───────────────────────── Ministerio de Economía ─────────────────────────
def _economia_listado() -> list[Noticia]:
    out = []
    for a in _html(ECONOMIA_URL).select("a.panel[href^='/noticias/']"):
        t, h3 = a.find("time"), a.find("h3")
        if not t or not h3:
            continue
        out.append(Noticia(
            fuente="Ministerio de Economía",
            # sin zona horaria, como las del BCRA: si no, no se pueden ordenar juntas
            fecha=datetime.fromisoformat(t["datetime"]).replace(tzinfo=None),
            titulo=_texto(h3),
            resumen=_texto(a.select_one("p.text-muted")),
            url=ECONOMIA_BASE + a["href"],
        ))
    return out


def _economia_portada() -> list[Noticia]:
    """Respaldo: las notas enlazadas en la portada de Economía, leídas una por una."""
    hrefs = list(dict.fromkeys(a["href"] for a in _html(ECONOMIA_PORTADA).select("a[href^='/noticias/']")))
    return _desde_paginas([ECONOMIA_BASE + h for h in hrefs[:12]], "Ministerio de Economía")


def economia(limite: int = 12) -> list[Noticia]:
    return _con_respaldo([
        ("listado /economia/noticias", _economia_listado),
        ("portada /economia", _economia_portada),
    ], limite)
