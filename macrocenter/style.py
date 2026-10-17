"""Estilos de MacroCenter. Usa colores translúcidos para verse bien en modo claro y oscuro."""
from __future__ import annotations

import functools
import html
import math
import re

import streamlit as st

from macrocenter.estilos import CELESTE, SOL, FUENTE, CSS, ESTILO_PANO, _version_clara
AUTOR = "Juan Manuel Pianciola"
LINKEDIN = "https://www.linkedin.com/in/jmp1412/"
# página de suscripción al boletín semanal (Buttondown). Vacío = no se muestra la invitación en el pie.
BOLETIN = "https://buttondown.com/macrocenter"
_ICONO_LINKEDIN = ('<svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M20.45 '
                   '20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 '
                   '1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 '
                   '4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 '
                   '1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>')

#: Tipografía: fuentes del sistema (Segoe UI en Windows, SF en Mac, Roboto en Android…). Se eligen a propósito en
#: lugar de Google Fonts para que el navegador no le pida nada a terceros (ver la Política de Privacidad).

# Al tocar una pestaña de un borde, la fila se desliza lo justo para mostrar la que sigue (o la anterior); las del
# medio no mueven nada. Se instala una sola vez por página y también sigue a las flechas del teclado.
JS_PESTANAS = """
<script>
(() => {
  // Íconos: se muestran recién cuando cargó su fuente (ver el CSS de stIconMaterial)
  const raiz = document.documentElement;
  if (raiz.dataset.iconos) return;
  const listo = () => { raiz.dataset.iconos = 'listos'; };
  try {
    if (!document.fonts || !document.fonts.load) { listo(); return; }
    document.fonts.load('24px "Material Symbols Rounded"').then(() => document.fonts.ready).then(listo, listo);
    setTimeout(listo, 3000);
  } catch (e) { listo(); }
})();
(() => {
  // Botón para ocultar la barra del pie (y volver a mostrarla). La elección se recuerda en este navegador.
  if (window.__mcPie) return;
  window.__mcPie = true;
  const raiz = document.documentElement;
  const leer = () => { try { return localStorage.getItem('mc_pie_oculto') === '1'; } catch (e) { return false; } };
  const guardar = (v) => { try { localStorage.setItem('mc_pie_oculto', v ? '1' : '0'); } catch (e) {} };
  const poner = (oculto) => { if (oculto) raiz.dataset.pie = 'oculto'; else delete raiz.dataset.pie; };
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'mc-pie-btn';
  // (sin HTML dentro del script: el sanitizador de Streamlit descarta los scripts que contienen etiquetas)
  const pintar = () => {
    const oculto = !!raiz.dataset.pie;  // 'oculto' o 'cerrando'
    b.textContent = oculto ? '▲' : '▼';
    b.title = oculto ? 'Mostrar la barra inferior' : 'Ocultar la barra inferior';
    b.setAttribute('aria-label', b.title);
    b.setAttribute('aria-pressed', oculto ? 'true' : 'false');
  };
  poner(leer());
  const quieto = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MS = 300;  // lo mismo que dura la animación en el CSS
  let reloj = 0;
  // el elemento que de verdad se desplaza (en Streamlit es el contenedor principal, no la ventana)
  const desplazable = (el) => {
    for (let p = el && el.parentElement; p; p = p.parentElement) {
      const o = getComputedStyle(p).overflowY;
      if ((o === 'auto' || o === 'scroll') && p.scrollHeight > p.clientHeight) return p;
    }
    return document.scrollingElement || document.documentElement;
  };
  // desplaza la página de `desde` a `hasta` en lo que dura la animación (a mano y no con scrollBy «smooth»: ese no se
  // mueve en todos los navegadores dentro de Streamlit). Al final se fija `hasta` por si el navegador lo recortó.
  const deslizar = (caja, desde, hasta) => {
    const t0 = performance.now();
    const paso = (t) => {
      const k = quieto() ? 1 : Math.min(1, (t - t0) / MS);
      caja.scrollTop = desde + (hasta - desde) * (1 - Math.pow(1 - k, 3));
      if (k < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
    setTimeout(() => { if (Math.abs(caja.scrollTop - hasta) > 1) caja.scrollTop = hasta; }, MS + 80);
  };
  b.addEventListener('click', () => {
    const oculto = !raiz.dataset.pie;
    clearTimeout(reloj);
    guardar(oculto);
    const barra = document.querySelector('.st-key-pie_datos');
    // la página se mueve lo mismo que mide la barra: baja al abrirla (así no tapa lo que se estaba leyendo) y sube al
    // cerrarla. Si solo bajara, abrir y cerrar varias veces iba corriendo la página hacia abajo.
    const caja = barra ? desplazable(barra) : null;
    const alto = barra ? barra.getBoundingClientRect().height : 0;
    if (oculto) {
      // cierre: la barra baja y recién después se saca
      if (!barra || quieto()) {
        delete raiz.dataset.pieAnim; poner(true); pintar();
        if (caja) caja.scrollTop = Math.max(0, caja.scrollTop - alto);
        return;
      }
      raiz.dataset.pieAnim = 'sale';
      raiz.dataset.pie = 'cerrando';
      pintar();
      deslizar(caja, caja.scrollTop, Math.max(0, caja.scrollTop - alto));
      reloj = setTimeout(() => { poner(true); delete raiz.dataset.pieAnim; pintar(); }, MS);
    } else {
      // apertura: la barra sube y la página baja lo mismo que mide
      poner(false);
      if (!quieto()) raiz.dataset.pieAnim = 'entra';
      pintar();
      if (barra) deslizar(caja, caja.scrollTop, caja.scrollTop + barra.getBoundingClientRect().height);
      reloj = setTimeout(() => { delete raiz.dataset.pieAnim; }, MS);
    }
  });
  pintar();
  document.body.appendChild(b);
})();
(() => {
  // Logo: lleva al Resumen sin recargar la página (toca el botón oculto «ir_resumen» de la barra lateral). Con Ctrl,
  // Mayús o la rueda del mouse sigue siendo un enlace común, para abrirlo en otra pestaña.
  if (window.__mcLogo) return;
  window.__mcLogo = true;
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a.mc-brand');
    if (!a || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    const b = document.querySelector('.st-key-ir_resumen button');
    if (!b) return;  // si no estuviera, el enlace funciona como siempre
    e.preventDefault();
    b.click();
    // arriba de todo; se repite mientras la pantalla se redibuja (si no, el cambio de contenido corta el desplazamiento)
    const arriba = () => {
      const p = document.querySelector('[data-testid="stMain"]');
      if (p) p.scrollTop = 0;
      window.scrollTo(0, 0);
    };
    arriba();
    [150, 500, 1200, 2500].forEach((ms) => setTimeout(arriba, ms));
  }, true);
})();
(() => {
  // Menú desplegable «Secciones» (grilla): los enlaces no recargan la página; tocan los botones ocultos de la
  // barra lateral (uno por sección, ver puente_secciones en app.py) y cierran el pliegue. Con Ctrl, Mayús o la
  // rueda del mouse sigue siendo un enlace común, para abrirlo en otra pestaña.
  if (window.__mcSecciones) return;
  window.__mcSecciones = true;
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a[data-btn]');
    if (!a || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    const b = document.querySelector('.st-key-' + a.dataset.btn + ' button');
    if (!b) return;  // si no estuviera, el enlace funciona como siempre
    e.preventDefault();
    b.click();
    // el pliegue del menú se cierra: se le toca el botón si quedó abierto
    const g = document.querySelector('.st-key-menu_secciones [data-testid="stPopoverButton"][aria-expanded="true"]');
    if (g) g.click();
  }, true);
})();
(() => {
  // Celular: la barra lateral se abre deslizando el dedo hacia la derecha desde el borde izquierdo y se cierra
  // deslizándolo hacia la izquierda. Toca los mismos botones de Streamlit (flecha de abrir y de cerrar). Solo cuenta
  // un gesto claramente horizontal, para no confundirse con desplazar la página, una tabla o un gráfico.
  if (window.__mcGesto) return;
  window.__mcGesto = true;
  const BORDE = 32, MINIMO = 55;
  let x0 = null, y0 = 0, desdeBorde = false;
  const abierta = () => {
    const sb = document.querySelector('[data-testid="stSidebar"]');
    return !!sb && sb.getAttribute('aria-expanded') === 'true';
  };
  document.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) { x0 = null; return; }
    x0 = e.touches[0].clientX; y0 = e.touches[0].clientY;
    desdeBorde = x0 <= BORDE;
  }, { passive: true, capture: true });
  document.addEventListener('touchend', (e) => {
    if (x0 === null || !e.changedTouches.length) return;
    const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    x0 = null;
    if (Math.abs(dx) < MINIMO || Math.abs(dy) > Math.abs(dx) * 0.6) return;  // corto o más vertical que horizontal
    if (dx > 0 && desdeBorde && !abierta()) {
      const b = document.querySelector('[data-testid="stExpandSidebarButton"]');
      if (b) b.click();
    } else if (dx < 0 && abierta() && window.matchMedia('(max-width: 768px)').matches) {
      const b = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
      if (b) b.click();
    }
  }, { passive: true, capture: true });
})();
(() => {
  // En el celular, elegir un destino también deja a la vista su contenido.
  if (!window.__mcMenuMovil) {
    window.__mcMenuMovil = true;
    document.addEventListener('click', (e) => {
      if (!window.matchMedia('(max-width: 768px)').matches) return;
      const destino = e.target.closest && e.target.closest('[class*="st-key-nav_"], [class*="st-key-atajo_"], .mc-brand');
      if (!destino) return;
      setTimeout(() => {
        const boton = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
        if (boton) boton.click();
      }, 0);
    });
  }
  // Tema claro u oscuro (Streamlit no lo marca): se mira el fondo de la página. Algunos colores cambian en el claro.
  if (window.__mcTema) return;
  window.__mcTema = true;
  // Al cambiar de tema, Streamlit reemplaza sus estilos (cambia la cabecera y las clases): se revisa en ese mismo
  // instante, antes de pintar, para que no quede ni un cuadro con colores del tema anterior. Durante el cambio se
  // apagan las transiciones (si no, botones e íconos se ven un momento con el color viejo).
  const raiz = document.documentElement;
  const revisar = () => {
    const app = document.querySelector('.stApp') || document.body;
    const m = getComputedStyle(app).backgroundColor.match(/[0-9]+/g);
    if (!m) return;
    const claro = (0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2]) > 150;
    if (claro === (raiz.dataset.tema === 'claro')) return;
    raiz.dataset.temaCambio = '1';
    if (claro) raiz.dataset.tema = 'claro'; else delete raiz.dataset.tema;
    requestAnimationFrame(() => requestAnimationFrame(() => { delete raiz.dataset.temaCambio; }));
    window.dispatchEvent(new Event('mc-tema'));
  };
  revisar();
  raiz.dataset.listo = '1';  // estilos y tema listos: se muestra el contenido (ver OCULTAR_HASTA_ESTILO)
  new MutationObserver(revisar).observe(raiz, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => requestAnimationFrame(revisar)); } catch (e) {}
  setInterval(revisar, 1500);
})();
(() => {
  // La franja de cotizaciones se pausa cuando no se ve (al bajar por la página): ahorra batería en el celular.
  if (window.__mcFranja) return;
  window.__mcFranja = true;
  let pendiente = false;
  const revisar = () => {
    pendiente = false;
    document.querySelectorAll('.mc-ticker').forEach((t) => {
      const r = t.getBoundingClientRect();
      t.classList.toggle('quieta', r.bottom < 0 || r.top > innerHeight);
    });
  };
  const pedir = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(revisar); } };
  document.addEventListener('scroll', pedir, {capture: true, passive: true});
  addEventListener('resize', pedir, {passive: true});
})();
(() => {
  // Montos: se aplican solos al dejar de escribir, sin tener que presionar Enter (Streamlit confirma un campo de
  // texto con Enter o al salir de él; acá se le manda ese Enter un instante después de la última tecla).
  if (window.__mcMontos) return;
  window.__mcMontos = true;
  let espera;
  document.addEventListener('input', (e) => {
    const el = e.target;
    if (!el.matches || !el.matches('[data-testid="stTextInput"] input')) return;
    clearTimeout(espera);
    espera = setTimeout(() => {
      if (!el.isConnected) return;
      el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
    }, 650);
  }, true);
})();
(() => {
  if (window.__mcPestanasV6) return;
  window.__mcPestanasV6 = true;
  // Mostrar la pestaña elegida dentro del área libre; las flechas quedan fuera de esa área.
  const destinoPara = (tab) => {
    const c = tab && tab.closest('[role="tablist"]');
    if (!c || c.scrollWidth <= c.clientWidth + 1) return null;
    const tabs = [...c.querySelectorAll('[role="tab"]')], i = tabs.indexOf(tab);
    if (i < 0) return null;
    // Los dos primeros marcadores recuperan el inicio exacto.
    if (i <= 1) return {c, left: 0};
    const r = c.getBoundingClientRect(), t = tab.getBoundingClientRect();
    const primero = tabs[0], fijo = getComputedStyle(primero).position === 'sticky';
    const desde = fijo ? primero.getBoundingClientRect().right + 20 : r.left + 8;
    const hasta = r.right - 8;
    let delta = 0;
    if (t.width > hasta - desde) delta = t.left - desde;
    else if (t.left < desde) delta = t.left - desde;
    else if (t.right > hasta) delta = t.right - hasta;
    if (Math.abs(delta) < 2) return null;
    return {c, left: Math.max(0, Math.min(c.scrollWidth - c.clientWidth, c.scrollLeft + delta))};
  };
  // Streamlit desliza la fila por su cuenta al cambiar de pestaña (scrollIntoView); lo anulamos para las pestañas
  // y queda un único movimiento suave, el nuestro (si no, las dos animaciones se pisan y la fila salta).
  const scrollOriginal = Element.prototype.scrollIntoView;
  Element.prototype.scrollIntoView = function (...args) {
    if (this.getAttribute && this.getAttribute('role') === 'tab' && this.closest('[role="tablist"]')) {
      const fila = this.closest('[role="tablist"]'), r = fila.getBoundingClientRect();
      if (r.top < 0 || r.bottom > window.innerHeight) scrollOriginal.call(fila, {block: 'nearest', inline: 'nearest'});
      return;
    }
    return scrollOriginal.apply(this, args);
  };
  let turno = 0;
  const mover = (d) => {
    if (!d) return;
    const mio = ++turno;
    setTimeout(() => {
      if (mio !== turno) return;
      d.c.scrollTo({left: d.left, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
      // si la animación no llega (pestaña en segundo plano, ahorro de energía), termina igual; un clic posterior manda
      setTimeout(() => { if (mio === turno && Math.abs(d.c.scrollLeft - d.left) > 2) d.c.scrollLeft = d.left; }, 900);
    }, 0);
  };
  // También mostrar la seleccionada al abrir un enlace directo o redimensionar la ventana.
  // El desplazamiento manual no altera la selección y no dispara este seguimiento.
  const instaladas = new WeakSet();
  const seguirListas = () => {
    document.querySelectorAll('[role="tablist"]').forEach(c => {
      if (instaladas.has(c)) return;
      instaladas.add(c);
      const mostrarElegida = () => mover(destinoPara(c.querySelector('[role="tab"][aria-selected="true"]')));
      new MutationObserver(mostrarElegida).observe(c, {subtree: true, attributes: true, attributeFilter: ['aria-selected']});
      if (window.ResizeObserver) new ResizeObserver(mostrarElegida).observe(c);
      mostrarElegida();
    });
  };
  let esperandoLista = false;
  new MutationObserver(() => {
    if (esperandoLista) return;
    esperandoLista = true;
    requestAnimationFrame(() => { esperandoLista = false; seguirListas(); });
  }).observe(document.body, {childList: true, subtree: true});
  seguirListas();
  // Al abrir una pestaña, Streamlit vacía el contenido viejo antes de que llegue el nuevo y la página se encoge un
  // instante (el pie salta y el scroll se pierde). Se mantiene el alto actual hasta que termina de cargar.
  let soltar = 0;
  const congelarAlto = () => {
    // se congela el bloque de las pestañas (no el contenedor general): la barra del pie va justo debajo y, si el
    // bloque se encoge, sube con él aunque la página siga igual de alta
    const m = document.querySelector('[data-testid="stTabs"]');
    if (!m) return;
    m.style.minHeight = m.offsetHeight + 'px';
    const t0 = Date.now(), mio = ++soltar;
    let quietos = 0;
    const iv = setInterval(() => {
      if (mio !== soltar) { clearInterval(iv); return; }
      quietos = document.querySelector('[data-stale="true"]') ? 0 : quietos + 1;
      if ((quietos >= 3 && Date.now() - t0 > 700) || Date.now() - t0 > 8000) { m.style.minHeight = ''; clearInterval(iv); }
    }, 100);
  };
  document.addEventListener('click', (e) => {
    const tab = e.target.closest && e.target.closest('[role="tablist"] [role="tab"]');
    if (tab) { mover(destinoPara(tab)); congelarAlto(); }
  }, true);
  // flechas de la fila: van directo a una punta (la de la derecha muestra el último marcador; la de la izquierda, el
  // primero). Los del medio siempre se ven, así que avanzar de a poco no sumaba nada. Se corta el manejo de Streamlit
  // (que corre la fila un tramo) para que no haya dos movimientos a la vez.
  document.addEventListener('click', (e) => {
    const flecha = e.target.closest && e.target.closest('[data-testid="stTabsScrollLeft"], [data-testid="stTabsScrollRight"]');
    if (!flecha) return;
    const bloque = flecha.closest('[data-testid="stTabs"]');
    const c = bloque && bloque.querySelector('[role="tablist"]');
    if (!c) return;
    e.stopPropagation();
    e.preventDefault();
    const fin = flecha.getAttribute('data-testid') === 'stTabsScrollRight' ? c.scrollWidth - c.clientWidth : 0;
    mover({c, left: fin});
  }, true);
  // si la persona mueve la fila a mano (flechitas, rueda, dedo), eso manda sobre cualquier movimiento pendiente
  const aMano = (e) => { if (e.target.closest && e.target.closest('[data-testid^="stTabsScroll"], [role="tablist"]')) turno++; };
  document.addEventListener('pointerdown', (e) => { if (e.target.closest && e.target.closest('[data-testid^="stTabsScroll"]')) turno++; }, true);
  document.addEventListener('wheel', aMano, {capture: true, passive: true});
  document.addEventListener('touchstart', aMano, {capture: true, passive: true});
  document.addEventListener('keyup', (e) => {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    const tab = document.activeElement;
    if (tab && tab.getAttribute('role') === 'tab') mover(destinoPara(tab));
  }, true);
})();
(() => {
  // Mapa de inflación: la provincia bajo el cursor se «levanta» (sube y deja su sombra, como una pieza en 3D).
  // Liviano: no hay observadores ni bucles; se escuchan los eventos de Plotly y se mueve una sola copia de la
  // provincia con una transición de CSS (solo transform y opacity, que resuelve la placa de video).
  if (window.__mcMapa) return;
  window.__mcMapa = true;
  const NS = 'http://www.w3.org/2000/svg';
  const quitar = (g) => {
    if (!g || g.__fuera) return;
    g.__fuera = true;
    g.classList.remove('arriba');
    setTimeout(() => g.remove(), 260);
  };
  const enganchar = (gd) => {
    if (gd.__mcLift || typeof gd.on !== 'function') return;
    gd.__mcLift = true;
    let actual = null;
    gd.on('plotly_hover', (ev) => {
      const pt = ev && ev.points && ev.points[0];
      if (!pt) return;
      const capa = gd.querySelector('.choroplethlayer');
      const caminos = capa ? capa.querySelectorAll('path.choroplethlocation') : [];
      const src = caminos[pt.pointNumber];
      if (!src) return;
      if (actual && actual.__src === src) return;
      quitar(actual);
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'mc-lift');
      g.__src = src;
      const sombra = src.cloneNode(false);
      sombra.setAttribute('class', 'mc-lift-sombra');
      const tapa = src.cloneNode(false);
      tapa.setAttribute('class', 'mc-lift-tapa');
      tapa.style.opacity = '1';
      g.appendChild(sombra);
      g.appendChild(tapa);
      src.parentNode.appendChild(g);
      actual = g;
      requestAnimationFrame(() => requestAnimationFrame(() => { if (!g.__fuera) g.classList.add('arriba'); }));
    });
    gd.on('plotly_unhover', () => { quitar(actual); actual = null; });
  };
  // se engancha la primera vez que el mouse entra a un gráfico con mapa (y otra vez si Streamlit lo vuelve a armar)
  document.addEventListener('pointerover', (e) => {
    const gd = e.target && e.target.closest ? e.target.closest('.js-plotly-plot') : null;
    if (gd && !gd.__mcLift && gd.querySelector('.choroplethlayer')) enganchar(gd);
  }, { passive: true });
})();
(() => {
  // Noticias leídas: el navegador las guarda en su almacenamiento local y, al abrir la página, las copia en el campo
  // oculto de la barra lateral para que la app las conozca. Mientras la app no las recibe, el botón de noticias se ve
  // normal y sin cuenta (sin datos equivocados); apenas llegan, se completa. Si no hay nada guardado, se manda un valor
  // vacío («00000000») igual, para que la app sepa que ya consultó.
  if (window.__mcLeidas) return;
  window.__mcLeidas = true;
  let v = '00000000';
  try {
    const g = localStorage.getItem('mc_leidas') || '';
    if (/^[0-9a-f]{8}(,[0-9a-f]{8})*$/.test(g)) v = g;
  } catch (e) {}
  let intentos = 0;
  const pasar = () => {
    if (intentos++ > 200) return;
    const inp = document.querySelector('.st-key-puente_leidas input');
    if (!inp) { setTimeout(pasar, 120); return; }
    if (inp.value === v) return;
    const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    inp.focus({ preventScroll: true });
    set.call(inp, v);
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    inp.blur();
    setTimeout(pasar, 2500);  // si la app lo pisó al redibujar, se vuelve a poner
  };
  pasar();
})();
(() => {
  // Detalles del documento que Streamlit no deja configurar: idioma español (para los lectores de pantalla), color de
  // la barra del navegador en el celular según el tema, título de la pestaña sin «· Streamlit», íconos que no se leen
  // en voz alta y el alto real de la barra inferior (para apoyar encima la lengüeta ▼). Liviano: un repaso cada 2 s.
  if (window.__mcDoc) return;
  window.__mcDoc = true;
  const docs = () => { const out = [document]; try { if (window.parent && window.parent.document) out.push(window.parent.document); } catch (e) {} return out; };
  const repasar = () => {
    const claro = document.documentElement.dataset.tema === 'claro';
    for (const d of docs()) {
      try {
        if (d.documentElement.lang !== 'es') d.documentElement.lang = 'es';
        let m = d.querySelector('meta[name="theme-color"]');
        if (!m) { m = d.createElement('meta'); m.name = 'theme-color'; d.head.appendChild(m); }
        const color = claro ? '#FFFFFF' : '#0E1420';
        if (m.content !== color) m.content = color;
        const titulo = document.title.replace(/ *[·|-] *Streamlit *$/, '') || 'MacroCenter';
        if (d.title !== titulo && (!d.title || /Streamlit/.test(d.title))) d.title = titulo;
      } catch (e) {}
    }
    document.querySelectorAll('[data-testid="stIconMaterial"]:not([aria-hidden])').forEach((i) => i.setAttribute('aria-hidden', 'true'));
    const abrirMenu = document.querySelector('[data-testid="stExpandSidebarButton"]');
    const cerrarMenu = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
    if (abrirMenu && abrirMenu.getAttribute('aria-label') !== 'Abrir menú de navegación') abrirMenu.setAttribute('aria-label', 'Abrir menú de navegación');
    if (cerrarMenu && cerrarMenu.getAttribute('aria-label') !== 'Cerrar menú de navegación') cerrarMenu.setAttribute('aria-label', 'Cerrar menú de navegación');

    // Los enlaces internos de las etiquetas Markdown comparten la misma pestaña del navegador.
    document.querySelectorAll('a[href^="?ver="]').forEach((a) => { if (a.target !== '_self') a.target = '_self'; });
    const barra = document.querySelector('.st-key-pie_datos');
    if (barra && barra.offsetHeight) document.documentElement.style.setProperty('--mc-pie-alto', barra.offsetHeight + 'px');
  };
  repasar();
  setInterval(repasar, 2000);
  window.addEventListener('resize', () => setTimeout(repasar, 150), { passive: true });
  window.addEventListener('mc-tema', repasar);
})();
// Intercepta clics en los enlaces de los KPIs para cambiar de pestaña al instante
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a || !a.closest('[data-testid="stMetricLabel"], .mc-pp-enl')) return;
    const href = a.getAttribute('href') || '';
    if (href.indexOf('tablero/') === -1) return;

    const slug = href.split('tablero/')[1].replace(/[/?#].*$/, '');
    const mapa = {
      'tasas-y-riesgo-pais': 'tasas',
      'inflacion-y-dinero': 'inflacion',
      'actividad-y-pbi': 'actividad',
      'salarios': 'salarios',
      'reservas': 'reservas'
    };
    const clave = mapa[slug] || slug;

    const tabs = Array.from(document.querySelectorAll('[data-testid="stTab"], [role="tab"]'));
    const destino = tabs.find((t) => {
      const texto = (t.textContent || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      return texto.indexOf(clave) !== -1;
    });

    if (destino) {
      e.preventDefault();
      destino.click();
      window.history.replaceState(null, '', href);
    }
  });

(() => {
  // Los gráficos siguen el ancho del panel sin retardo: Streamlit pinta el ancho fijo en px al crearlos y se
  // re-mide tarde; al plegar o desplegar la columna el dibujo quedaba desparejo un segundo. Este observador
  // re-acopla cada gráfico a su envoltorio apenas el área útil cambia.
  if (window.__mcGraficos) return;
  window.__mcGraficos = true;
  const ajustar = () => {
    document.querySelectorAll('[data-testid="stPlotlyChart"]').forEach(el => {
      if (el.style.width !== '100%') el.style.width = '100%';
      const p = el.querySelector('.js-plotly-plot');
      if (p && window.Plotly) { try { Plotly.Plots.resize(p); } catch (e) {} }
    });
  };
  let t = null;
  const encolar = () => { clearTimeout(t); t = setTimeout(ajustar, 60); };
  window.addEventListener('resize', encolar, true);
  const blanco = () => document.querySelector('[data-testid="stMain"]') || document.body;
  const obs = new ResizeObserver(encolar);
  obs.observe(blanco());
})();
(() => {
  // Cloud (share.streamlit.io) agrega su insignia «Hosted with Streamlit» y el chip «Created by …» en el documento que
  // envuelve a la app —afuera del iframe—: no se pueden sacar por CSS desde acá. El iframe es del mismo origen, así que
  // esas dos piezas se buscan por su texto en el documento de arriba y se esconden. En local (sin envoltorio) no hace nada.
  if (window.__mcCloud) return;
  window.__mcCloud = true;
  const texto = (el) => ((el && el.textContent) || '').replace(/\\s+/g, ' ').trim().toLowerCase();
  const ocultar = () => {
    try {
      if (window.parent === window) return;
      const doc = window.parent.document;
      const marca = [...doc.querySelectorAll('a, div')]
        .filter(el => texto(el).includes('hosted with streamlit') && !el.querySelector('iframe'))
        .sort((a, b) => texto(a).length - texto(b).length)[0];
      if (!marca) return;  // no es el envoltorio de Cloud (o ya está limpio)
      marca.style.setProperty('display', 'none', 'important');
      const credito = [...doc.querySelectorAll('div')]
        .filter(el => texto(el).includes('created by') && !el.querySelector('iframe') && el.querySelector('img'))
        .sort((a, b) => texto(a).length - texto(b).length)[0];
      if (credito) credito.style.setProperty('display', 'none', 'important');
    } catch (e) {}  // envoltorio de otro origen: no se puede tocar
  };
  ocultar();
  setInterval(ocultar, 1500);
})();
</script>
"""


GOATCOUNTER = "https://jmp0912.goatcounter.com/count"


def slug(texto: str) -> str:
    """«Tasas y riesgo país» → «tasas-y-riesgo-pais» (para las rutas de las estadísticas)."""
    import unicodedata

    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "inicio"


def contador_visitas(ruta: str, titulo: str) -> str:
    """Cuenta una visita a la sección con GoatCounter: sin cookies ni datos personales (solo totales por página,
    navegador, país y tamaño de pantalla). Cada sección cuenta una vez por cambio; en la computadora local no cuenta."""
    import json

    return f"""<script>
(() => {{
  const ruta = {json.dumps(ruta)}, titulo = {json.dumps(titulo)};
  if (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) return;
  if (window.__mcRuta === ruta) return;
  window.__mcRuta = ruta;
  // pedido directo al contador (método «sin JavaScript» de GoatCounter): el script oficial no arranca dentro del
  // marco en el que Streamlit Cloud muestra la app. La procedencia solo se manda en la primera sección de la visita.
  let origen = '';
  if (!window.__mcOrigen) {{
    window.__mcOrigen = true;
    try {{ origen = window.parent.document.referrer || document.referrer; }} catch (e) {{ origen = document.referrer; }}
  }}
  const q = new URLSearchParams({{p: ruta, t: titulo, r: origen,
    s: [screen.width, screen.height, window.devicePixelRatio || 1].join(','),
    rnd: Math.random().toString(36).slice(2)}});
  const img = new Image();
  img.referrerPolicy = 'no-referrer-when-downgrade';
  img.src = {json.dumps(GOATCOUNTER)} + '?' + q.toString();
}})();
</script>"""


# Primer elemento de la página: deja invisible el contenido (no el fondo) hasta que llega la hoja de estilos grande y,
# mientras tanto, muestra un círculo de carga. Oculta con opacidad y no con visibility: algunos elementos de Streamlit
# se declaran visibles y se escapaban del ocultamiento. En un navegador nuevo, Streamlit baja por partes el código que dibuja cada
# tipo de elemento; si el de los textos llegaba antes que el de la hoja de estilos, se veía todo sin formato. En un
# celular con 4G, la primera vez, la hoja puede tardar varios segundos (con un respaldo de 4 s se llegó a ver la franja
# de cotizaciones cruda): el respaldo queda en 20 s, solo para el caso de que la hoja no llegue nunca. Va con
# st.markdown, el mismo tipo que los textos, así que se aplica junto con ellos.
OCULTAR_HASTA_ESTILO = (
    "<style>[data-testid=\"stSidebarUserContent\"],[data-testid=\"stMainBlockContainer\"]{opacity:0;"
    "animation:mc-ver-igual 0s linear 20s forwards}@keyframes mc-ver-igual{to{opacity:1}}"
    ".stApp::after{content:\"\";position:fixed;left:50%;top:42%;width:42px;height:42px;margin:-21px 0 0 -21px;"
    "border-radius:50%;border:4px solid rgba(116,172,223,.18);border-top-color:#74ACDF;border-right-color:#74ACDF;"
    "z-index:999990;pointer-events:none;opacity:0;animation:mc-aro-ini .8s linear infinite,mc-aro-ver .3s ease .3s forwards}"
    "@keyframes mc-aro-ini{to{transform:rotate(360deg)}}@keyframes mc-aro-ver{to{opacity:1}}</style>"
)


def aplicar() -> None:
    st.markdown(OCULTAR_HASTA_ESTILO, unsafe_allow_html=True)
    # st.html y no st.markdown: el Markdown interpretaba este bloque grande con su procesador de texto y tardaba ~0,1 s;
    # mientras tanto la barra lateral (más liviana) ya se dibujaba sin estilo. Con solo <style>, st.html lo manda al
    # contenedor de eventos (no ocupa lugar) y se aplica enseguida
    st.html(CSS)
    st.html(JS_PESTANAS, unsafe_allow_javascript=True)


def _sol_svg(cx: float, cy: float, r: float) -> str:
    """Sol de Mayo: disco con 32 rayos alternando largos y cortos."""
    partes = []
    n = 32
    for i in range(n):
        a = 2 * math.pi * i / n
        largo = r * (2.15 if i % 2 == 0 else 1.7)
        ancho = math.pi / n * 0.55
        pts = [(cx + r * 1.12 * math.cos(a - ancho), cy + r * 1.12 * math.sin(a - ancho)),
               (cx + largo * math.cos(a), cy + largo * math.sin(a)),
               (cx + r * 1.12 * math.cos(a + ancho), cy + r * 1.12 * math.sin(a + ancho))]
        partes.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
    return f'<g fill="{SOL}">{"".join(partes)}<circle cx="{cx}" cy="{cy}" r="{r}"/></g>'


def sol(tam: int = 52) -> str:
    """Sol de Mayo solo, sin bandera (para el título)."""
    return (
        f'<svg class="mc-sunsvg" width="{tam}" height="{tam}" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Sol de Mayo">{_sol_svg(30, 30, 11)}</svg>'
    )


def bandera(ancho: int = 44) -> str:
    """Bandera argentina en SVG (el emoji se ve como 'AR' en Windows)."""
    alto = round(ancho * 2 / 3)
    return (
        f'<svg class="mc-flagsvg" width="{ancho}" height="{alto}" viewBox="0 0 90 60" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Bandera argentina"><rect width="90" height="60" fill="{CELESTE}"/>'
        f'<rect y="20" width="90" height="20" fill="#FFFFFF"/>{_sol_svg(45, 30, 5.2)}</svg>'
    )


FONDO_LOGO = "#0E1A2B"


def logo(tam: int = 52) -> str:
    """Logo de MacroCenter: una «C» abierta (anillo celeste) que encierra una «M» con forma de línea de gráfico, y el Sol
    de Mayo dorado en la apertura de la C. Cuadrado de esquinas redondeadas, para que sirva como ícono."""
    return (
        f'<svg class="mc-logo" width="{tam}" height="{tam}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="MacroCenter"><rect width="64" height="64" rx="15" fill="{FONDO_LOGO}"/>'
        f'<path d="M 49 15 A 24 24 0 1 0 49 49" fill="none" stroke="{CELESTE}" stroke-width="6" stroke-linecap="round"/>'
        '<polyline points="21,42 21,24 32,36 43,24 43,42" fill="none" stroke="#FFFFFF" stroke-width="5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="53" cy="32" r="4.6" fill="{SOL}"/></svg>'
    )


@functools.lru_cache(maxsize=1)
def favicon():
    """Ícono de la pestaña: el mismo logo, dibujado con PIL (viene incluido con Streamlit) en alta resolución.
    Se dibuja una sola vez por proceso: dibujarlo en cada corrida costaba ~0,25 s por clic."""
    from PIL import Image, ImageDraw

    k, final = 16, 256  # se dibuja 16 veces más grande y se reduce para que los bordes salgan suaves
    s = final * k
    u = s / 64  # una unidad del SVG
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=15 * u, fill=FONDO_LOGO)
    caja = [(32 - 27) * u, (32 - 27) * u, (32 + 27) * u, (32 + 27) * u]  # PIL dibuja el trazo hacia adentro: 24 + 3
    d.arc(caja, start=45, end=315, fill=CELESTE, width=int(6 * u))
    for ang, (cx, cy) in ((45, (49, 49)), (315, (49, 15))):  # terminaciones redondeadas de la C
        d.ellipse([(cx - 3) * u, (cy - 3) * u, (cx + 3) * u, (cy + 3) * u], fill=CELESTE)
    m = [(21, 42), (21, 24), (32, 36), (43, 24), (43, 42)]
    d.line([(x * u, y * u) for x, y in m], fill="white", width=int(5 * u), joint="curve")
    for x, y in (m[0], m[-1]):
        d.ellipse([(x - 2.5) * u, (y - 2.5) * u, (x + 2.5) * u, (y + 2.5) * u], fill="white")
    d.ellipse([(53 - 4.6) * u, (32 - 4.6) * u, (53 + 4.6) * u, (32 + 4.6) * u], fill=SOL)
    return img.resize((final, final), Image.LANCZOS)


def _favicon_bandera():
    """Ícono de pestaña: bandera con Sol de Mayo (PIL viene incluido con Streamlit)."""
    from PIL import Image, ImageDraw

    s = 128
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    h = int(s * 2 / 3)
    top = (s - h) // 2
    d.rounded_rectangle([0, top, s - 1, top + h], radius=10, fill=CELESTE)
    d.rectangle([0, top + h // 3, s - 1, top + 2 * h // 3], fill="white")
    cx, cy, r = s / 2, s / 2, 9
    for i in range(32):
        a = 2 * math.pi * i / 32
        largo = r * (2.2 if i % 2 == 0 else 1.7)
        w = math.pi / 32 * 0.55
        d.polygon([(cx + r * 1.1 * math.cos(a - w), cy + r * 1.1 * math.sin(a - w)),
                   (cx + largo * math.cos(a), cy + largo * math.sin(a)),
                   (cx + r * 1.1 * math.cos(a + w), cy + r * 1.1 * math.sin(a + w))], fill=SOL)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOL)
    return img


def marca() -> str:
    return (
        f'<a class="mc-brand" href="?ver=tablero/resumen" target="_self" title="Ir al resumen" aria-label="MacroCenter: ir al resumen">'
        # todo en elementos de línea (span): con bloques (div, h1, p) adentro de un enlace, el Markdown de Streamlit
        # partía la marca en pedazos
        f'<span class="mc-flag">{logo(46)}</span><span class="txt"><span class="mc-wm" role="heading" aria-level="1">'
        'Macro<span class="c">Center</span><span class="beta" title="Versión de prueba: puede haber detalles por '
        'pulir">Beta</span></span></a>'
    )


def hero() -> str:
    return (
        f'<div class="mc-title"><div class="mc-flag">{sol(44)}</div>'
        '<div><h1>MacroCenter</h1><div class="sub">Tablero macroeconómico de Argentina</div></div></div>'
    )


def creditos() -> str:
    return f'<div class="mc-by">Creada por <b>{AUTOR}</b></div>'


def franja() -> str:
    return '<div class="mc-stripe"></div>'

def resultado_final(fichas: list[tuple[str, str, str, str]]) -> str:
    """Fichas (etiqueta, valor, detalle, tono) con tono '', 'ok' o 'mal'. Los textos son propios de la app."""
    import html
    return '<div class="mc-rf">' + "".join(
        f'<div class="f {t}"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div>'
        f'<div class="d">{html.escape(d)}</div></div>' for k, v, d, t in fichas) + "</div>"


def lista_noticias(items: list[dict], meses: list[str]) -> str:
    """Lista de noticias: fecha a la izquierda, fuente y «Nueva» como etiquetas, título y resumen corto.
    items: {titulo, url, fecha, resumen, fuente, clase ('bcra'|'economia'|'indec'), nueva}. Todo el texto viene de afuera: se escapa."""
    from macrocenter.news import url_segura

    if not items:
        return '<div class="mc-news-vacio">No hay noticias para mostrar.</div>'
    filas = []
    for it in items:
        url = it["url"] if url_segura(it["url"]) else ""
        resumen = (it.get("resumen") or "").strip()
        f = it["fecha"]
        tag_nueva = '<span class="tag nueva">Nueva</span>' if it.get("nueva") else ""
        filas.append(
            f'<div class="mc-news-it{" es-nueva" if it.get("nueva") else ""}">'
            f'<div class="mc-news-fecha"><b>{f.day}</b><span>{html.escape(meses[f.month - 1][:3])}</span></div>'
            f'<div class="mc-news-txt"><div class="mc-news-tags"><span class="tag {html.escape(it["clase"])}">'
            f'{html.escape(it["fuente"])}</span>{tag_nueva}</div>'
            f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(it["titulo"])}</a>'
            + (f'<p>{html.escape(resumen)}</p>' if resumen else "") + "</div></div>")
    return '<div class="mc-news">' + "".join(filas) + "</div>"


def pie_noticias(sitios: list[tuple[str, str]]) -> str:
    links = " · ".join(f'<a href="{html.escape(u, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(n)} ↗</a>'
                       for n, u in sitios)
    return f'<div class="mc-news-pie">Todo en los sitios oficiales: {links}</div>'


def titulo_grafico(titulo: str, bajada: str | None = None) -> str:
    """Título de un gráfico como texto de la página (se parte en renglones; el de Plotly se cortaba en el celular).
    Los títulos son propios de la app; igual se escapan."""
    b = f'<div class="b">{html.escape(bajada)}</div>' if bajada else ""
    return f'<div class="mc-gtit"><div class="t" role="heading" aria-level="4">{html.escape(titulo)}</div>{b}</div>'


def etiqueta(texto: str) -> str:
    return f'<div class="mc-label">{texto}</div>'


def _md_a_html(texto: str) -> str:
    """El poquito de Markdown que usan las frases del panorama: **negrita**, :green[...] y :red[...]."""
    t = html.escape(texto)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r":green\[(.+?)\]", r'<span class="pos">\1</span>', t)
    return re.sub(r":red\[(.+?)\]", r'<span class="neg">\1</span>', t)


def panorama(items: list[dict], fecha: str = "") -> str:
    """Guía de lectura: conceptos complementarios, sin duplicar indicadores."""
    esc = html.escape
    destinos = {"Dólar": "dolar", "Inflación": "inflacion-y-dinero", "Reservas": "reservas",
                "Riesgo país": "tasas-y-riesgo-pais", "Salarios": "salarios", "Actividad": "actividad-y-pbi"}
    tarjetas = []
    for i in items:
        destino = destinos.get(i["tema"])
        enlace = (f'<a href="?ver=tablero/{destino}" target="_self">Explorar {esc(i["tema"].lower())} ↗</a>'
                  if destino else "")
        tarjetas.append(f'<article class="mc-contexto-tarjeta"><h4>{esc(i.get("titulo", i["tema"]))}</h4>'
                        f'<p>{_md_a_html(i["texto"])}</p>{enlace}</article>')
    return ('<section class="mc-contexto" aria-label="Más allá del dato">'
            '<h3>Más allá del dato</h3><p class="mc-contexto-bajada">Tres claves para interpretar los indicadores en conjunto.</p>'
            f'<div class="mc-contexto-grilla">{"".join(tarjetas)}</div></section>')


def cargando(texto: str = "Cargando datos…", alto: str = "55vh") -> str:
    """Círculo de carga para la zona principal mientras se bajan datos. Aparece recién a los 0,4 s: en las cargas rápidas
    (casi todas) no llega a verse y no parpadea. Trae su propio estilo porque puede mostrarse antes que el de la página."""
    return (
        '<style>'
        '.mc-cargando{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;'
        f'min-height:{alto};opacity:0;animation:mc-aparece .3s ease .4s forwards}}'
        '.mc-cargando .aro{width:46px;height:46px;border-radius:50%;border:4px solid rgba(116,172,223,.18);'
        f'border-top-color:{CELESTE};border-right-color:{CELESTE};animation:mc-gira .8s linear infinite;position:relative}}'
        f'.mc-cargando .aro::after{{content:"";position:absolute;top:-7px;left:50%;width:8px;height:8px;margin-left:-4px;'
        f'border-radius:50%;background:{SOL};box-shadow:0 0 8px rgba(246,180,14,.8)}}'
        '.mc-cargando .t{font-size:.86rem;opacity:.7;letter-spacing:.02em}'
        '@keyframes mc-gira{to{transform:rotate(360deg)}}@keyframes mc-aparece{to{opacity:1}}'
        '@media (prefers-reduced-motion:reduce){.mc-cargando .aro{animation-duration:2.4s}}'
        '</style>'
        f'<div class="mc-cargando" role="status" aria-live="polite"><div class="aro"></div>'
        f'<div class="t">{html.escape(texto)}</div></div>'
    )


def pantalla_carga(termino: str, definicion: str) -> str:
    """Pantalla que se ve mientras se bajan los datos de todas las fuentes (servidor recién prendido). Trae sus propios
    estilos porque aparece antes de que se apliquen los de la página."""
    import base64

    esc = html.escape
    # el logo va como imagen: este bloque filtra los SVG escritos directamente
    _logo_img = "data:image/svg+xml;base64," + base64.b64encode(logo(68).encode()).decode()
    fuentes = "".join(f'<span style="animation-delay:{i * .35:.2f}s">{f}</span>'
                      for i, f in enumerate(("BCRA", "INDEC", "Ministerio de Economía", "ArgentinaDatos", "FRED")))
    return f"""
<style>
.mc-carga {{ min-height: 78vh; display: flex; align-items: center; justify-content: center; font-family: {FUENTE}; }}
.mc-carga .caja {{ width: min(520px, 92vw); text-align: center; }}
.mc-carga .logo {{ display: inline-block; animation: mc-latir 2.2s ease-in-out infinite; }}
.mc-carga h1 {{ margin: 14px 0 2px; font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; }}
.mc-carga h1 span {{ color: {CELESTE}; }}
.mc-carga .sub {{ opacity: .85; font-size: .95rem; }}
.mc-carga .pista {{ position: relative; height: 6px; margin: 22px auto 14px; width: 78%; border-radius: 999px; overflow: hidden;
    background: rgba(116,172,223,.16); }}
.mc-carga .pista::after {{ content: ""; position: absolute; top: 0; bottom: 0; width: 38%; border-radius: 999px;
    background: linear-gradient(90deg, {CELESTE}, #4A8FD4, {SOL}); animation: mc-avance 1.4s ease-in-out infinite; }}
.mc-carga .fuentes {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 6px 8px; }}
.mc-carga .fuentes span {{ font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; padding: 3px 10px;
    border-radius: 999px; border: 1px solid rgba(116,172,223,.35); color: {CELESTE}; opacity: .85;
    animation: mc-fuente 1.75s ease-in-out infinite; }}
.mc-carga .termino {{ margin-top: 26px; text-align: left; padding: 12px 14px; border-radius: 12px; border-left: 3px solid {SOL};
    background: rgba(116,172,223,.08); }}
.mc-carga .termino b {{ display: block; color: {SOL}; font-size: .9rem; margin-bottom: 3px; }}
.mc-carga .termino small {{ display: block; font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; opacity: .85;
    margin-bottom: 4px; }}
.mc-carga .termino p {{ margin: 0; font-size: .85rem; line-height: 1.45; opacity: .9; }}
.mc-carga .nota {{ margin-top: 14px; font-size: .78rem; opacity: .85; }}
@keyframes mc-avance {{ 0% {{ left: -38%; }} 100% {{ left: 100%; }} }}
@keyframes mc-latir {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.06); }} }}
@keyframes mc-fuente {{ 0%, 100% {{ opacity: .4; }} 50% {{ opacity: 1; background: rgba(116,172,223,.14); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-carga * {{ animation: none !important; }} }}
</style>
<div class="mc-carga"><div class="caja">
  <div class="logo"><img src="{_logo_img}" width="68" height="68" alt="MacroCenter"></div>
  <h1>Macro<span>Center</span></h1>
  <div class="sub">Preparando el tablero con los últimos datos oficiales…</div>
  <div class="pista"></div>
  <div class="fuentes">{fuentes}</div>
  <div class="termino"><small>Mientras tanto, el término del día</small><b>{esc(termino)}</b><p>{esc(definicion)}</p></div>
  <div class="nota">La primera carga tarda unos segundos; después la página abre al instante.</div>
</div></div>"""


def conversor(filas: list[tuple[str, str, str]], nota: str) -> str:
    """Resultado del conversor de la barra lateral. filas: (dólar, cotización, resultado)."""
    esc = html.escape
    cuerpo = "".join(f'<div class="f"><span class="k">{esc(n)}<small>{esc(p)}</small></span><span class="v">{esc(r)}</span></div>'
                     for n, p, r in filas)
    return f'<div class="mc-conv">{cuerpo}<div class="nota">{esc(nota)}</div></div>'


def termino_del_dia(termino: str, definicion: str) -> str:
    return (f'<div class="mc-termino"><div class="mc-termino-t">{html.escape(termino)}</div>'
            f'<div class="mc-termino-d">{html.escape(definicion)}</div></div>')


def cotizacion(nombre: str, valor: str, variacion: float | None) -> str:
    if variacion is None:
        d = ""
    else:
        clase = "mc-up" if variacion > 0.005 else "mc-down" if variacion < -0.005 else "mc-flat"
        flecha = "▲" if variacion > 0.005 else "▼" if variacion < -0.005 else "■"
        d = f'<span class="d {clase}">{flecha} {abs(variacion):.1f}%</span>'.replace(".", ",")
    return f'<div class="mc-tick"><span class="n">{nombre}</span><span class="v">{valor}{d}</span></div>'


def ministros(resumen: list | None, grupos: list[dict], intro: str = "") -> str:
    """Sección de ministros de Economía. resumen: [(etiqueta, valor, detalle)] o None. Cada grupo: titulo, periodo,
    foto, nota, items [{nombre, iniciales, foto, cargo, periodo, duracion, barra, perfil, hitos, datos, pico, actual}]."""
    esc = html.escape

    def img(url: str | None, alt: str) -> str:
        return (f'<img src="{esc(url)}" alt="{esc(alt)}" loading="lazy" decoding="async" referrerpolicy="no-referrer">' if url else "")

    out = []
    if intro or resumen:  # portada (va arriba del filtro, por eso se dibuja aparte)
        out.append('<div class="mc-min-hero"><div class="eyebrow">Historia económica · 1983 – hoy</div>'
                   '<h3>Ministros de Economía</h3>' + (f"<p>{esc(intro)}</p>" if intro else ""))
        if resumen:
            out.append('<div class="mc-min-res">' + "".join(
                f'<div><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div><div class="d">{esc(d)}</div></div>'
                for k, v, d in resumen) + "</div>")
        out.append("</div>")
    for g in grupos:
        ini_p = "".join(p[0] for p in g["titulo"].split() if p[0].isupper())[:2]
        n = len(g["items"])
        out.append(
            f'<div class="mc-min-grupo"><div class="pf"><span>{esc(ini_p)}</span>{img(g.get("foto"), g["titulo"])}</div>'
            f'<div class="t"><small>Presidencia</small><b>{esc(g["titulo"])}</b><span>{esc(g["periodo"])}</span></div>'
            f'<div class="n">{n} ministro{"s" if n != 1 else ""}</div></div><div class="mc-min-linea"></div>')
        if g.get("nota"):
            out.append(f'<div class="mc-min-nota">{esc(g["nota"])}</div>')
        out.append('<div class="mc-min">')
        for it in g["items"]:
            datos = "".join(
                f'<div class="dato"><div class="k">{esc(d["k"])}</div><div class="v">{esc(d["v"])}</div>'
                f'<div class="s{" " + d["tend"] if d.get("tend") else ""}">{esc(d["s"])}</div></div>' for d in it["datos"])
            # los dos primeros hitos a la vista; el resto, plegado (la sección completa ocupaba ~10 pantallas)
            hitos = "".join(f"<li>{esc(h)}</li>" for h in it["hitos"][:2])
            resto = it["hitos"][2:]
            if resto:
                hitos += (f'<li class="mas"><details><summary>+{len(resto)} hito{"s" if len(resto) > 1 else ""} más</summary>'
                          f'<ul>{"".join(f"<li>{esc(h)}</li>" for h in resto)}</ul></details></li>')
            pico = f'<div class="pico">{esc(it["pico"])}</div>' if it.get("pico") else ""
            vivo = '<span class="vivo">EN EJERCICIO</span>' if it.get("actual") else ""
            out.append(
                f'<div class="mc-min-card{" actual" if it.get("actual") else ""}">{vivo}'
                f'<div class="top"><div class="ph"><span>{esc(it["iniciales"])}</span>{img(it.get("foto"), it["nombre"])}</div>'
                f'<div><div class="per">{esc(it["periodo"])}</div><h5>{esc(it["nombre"])}</h5>'
                f'<div class="cargo">{esc(it["cargo"])}</div></div></div>'
                f'<div class="cuerpo"><div class="dur"><span>{esc(it["duracion"])}</span>'
                f'<div class="b"><i style="width:{float(it["barra"]):.0f}%"></i></div></div>'
                f'<div class="perfil">{esc(it["perfil"])}</div><ul>{hitos}</ul>'
                + (f'<div class="datos">{datos}</div>' if datos else "") + f"{pico}</div></div>"
            )
        out.append("</div>")
    return "".join(out)


def _columnas(n: int) -> int:
    """Columnas de la grilla de tarjetas en pantallas anchas: las que dejan filas completas (16 → 4×4, 10 → 5×2) o, si
    ninguna divide justo, la que deja la última fila más llena (7 → 4+3). Nunca una tarjeta sola en una fila."""
    if n <= 4:
        return 4
    return max((5, 4, 6), key=lambda c: (n % c == 0, (n % c or c) / c))


def cotizaciones(tarjetas: list[dict]) -> str:
    """Grilla de tarjetas de cotización. Cada una: nombre, desc, valor, detalle, var (% o None), chip (texto o None)."""
    esc = html.escape
    out = [f'<div class="mc-fxwrap"><div class="mc-fxgrid" style="--cols:{_columnas(len(tarjetas))}">']
    for t in tarjetas:
        var = _chip_var(t.get("var"), t.get("var_txt", "30 d"), t.get("sentido", "neutro"))
        extra = "".join(_chip_var(v, txt, t.get("sentido", "neutro")) for txt, v in t.get("extras", []))
        chip = f'<span class="chip">{esc(t["chip"])}</span>' if t.get("chip") else ""
        spark = (sparkline(t.get("spark") or [], ancho=76, color=t.get("spark_color"), sentido=t.get("sentido", "neutro"))
                 if t.get("spark") else "")
        out.append(
            f'<div class="mc-fx"><div class="n">{esc(t["nombre"])}</div><div class="d">{esc(t["desc"])}</div>'
            f'<div class="fila"><div class="v">{esc(t["valor"])}</div>{spark}</div><div class="c">{esc(t["detalle"])}</div>'
            f'<div class="chips">{var}{extra}{chip}</div>'
            f'{t.get("meta", "")}</div>'
        )
    out.append("</div></div>")
    return "".join(out)


def _chip_var(v, texto: str, sentido: str = "neutro") -> str:
    """Chip con flecha y variación. sentido: 'neutro' (sin juicio), 'alto' (subir es bueno) o 'bajo' (subir es malo)."""
    if v is None or v != v:
        return ""
    return f'<span class="chip {_clase_var(v, sentido)}">{_flecha(v)} {abs(v):.1f}% · {html.escape(texto)}</span>'.replace(".", ",")


def _flecha(v: float) -> str:
    return "▲" if v > 0.05 else "▼" if v < -0.05 else "■"


def _clase_var(v: float, sentido: str = "neutro") -> str:
    """Color de una variación: verde si es buena noticia, rojo si es mala.
    sentido: 'alto' (subir es bueno: reservas, bolsas, soja), 'bajo' (subir es malo: dólar, riesgo país, inflación)
    o 'neutro' (sin juicio claro: oro, tasas): sin color, solo la flecha."""
    if abs(v) <= 0.05:
        return "flat"
    if sentido == "neutro":
        return "up" if v > 0 else "down"
    return "bien" if (v > 0) == (sentido == "alto") else "mal"


def sparkline(valores: list, ancho: int = 92, alto: int = 30, color: str | None = None, sentido: str = "alto") -> str:
    """Mini-gráfico de línea en SVG. Sin color explícito, verde si terminó arriba de donde empezó y rojo si no."""
    vs = [float(x) for x in valores if x is not None and x == x]
    if len(vs) < 2:
        return ""
    if len(vs) > 48:  # alcanza con ~48 puntos para un mini-gráfico
        paso = (len(vs) - 1) / 47
        vs = [vs[round(i * paso)] for i in range(48)]
    mn, mx = min(vs), max(vs)
    rango = (mx - mn) or 1.0
    puntos = " ".join(f"{1 + i * (ancho - 2) / (len(vs) - 1):.1f},{alto - 2 - (v - mn) / rango * (alto - 4):.1f}"
                      for i, v in enumerate(vs))
    if not color:  # verde si el período fue bueno, rojo si fue malo; sin juicio, celeste
        if sentido == "neutro" or vs[-1] == vs[0]:
            color = CELESTE
        else:
            color = "#10AC84" if (vs[-1] > vs[0]) == (sentido == "alto") else "#EE5253"
    return (f'<svg class="spark" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none" '
            f'aria-hidden="true">'
            f'<polyline points="{puntos}" fill="none" stroke="{color}" stroke-width="1.8" vector-effect="non-scaling-stroke" stroke-linejoin="round" '
            f'stroke-linecap="round"/></svg>')


def menu_secciones(secciones: list[str], actual: str) -> str:
    enlaces = []
    for nombre in secciones:
        activa = ' aria-current="page"' if nombre == actual else ''
        # data-btn: el botón oculto de la barra lateral que ejecuta este enlace (JS_PESTANAS lo toca y así la página
        # no se recarga); el href queda como respaldo (sirve sin JS y con Ctrl, Mayús o la rueda)
        enlaces.append(f'<a href="?ver=tablero/{slug(nombre)}" target="_self" data-btn="sec_{slug(nombre)}"{activa}>{html.escape(nombre)}</a>')
    return '<nav class="mc-menu-secciones" aria-label="Secciones del tablero">' + ''.join(enlaces) + '</nav>'


def ticker(items: list[dict]) -> str:
    """Franja superior deslizante con datos clave. item: {n: nombre, v: valor, d: variación % o None, sentido: ...}."""
    esc = html.escape
    if not items:
        return ""
    celdas = []
    for it in items:
        d = it.get("d")
        periodo = esc(it.get("periodo", "1 d"))
        if d is None or d != d:
            var = f'<span class="d">{periodo}</span>'
        else:
            clase = _clase_var(d, it.get("sentido", "neutro"))
            flecha = _flecha(d)
            # la franja muestra la variación del último día (los indicadores clave, la de 30 días): se aclara con «1 d»
            numero = f'{abs(d):.1f}'.replace(".", ",")
            var = (f'<span class="d {clase}" title="Variación: {periodo}">{flecha} '
                   f'{numero}{esc(it.get("dsuf", "%"))} · {periodo}</span>')
        celdas.append(f'<span class="tk"><span class="n">{esc(it["n"])}</span><span class="v">{esc(it["v"])}</span>{var}</span>')
    pista = "".join(celdas)
    return (f'<div class="mc-ticker" aria-label="Datos clave"><div class="pista">{pista}'
            f'<span class="copia" aria-hidden="true">{pista}</span></div></div>')


def tabla_simple(cabeceras: list[str], filas: list[list[str]]) -> str:
    """Tabla HTML simple con el estilo de las demás (primera columna alineada a la izquierda)."""
    esc = html.escape
    cab = "".join(f"<th>{esc(c)}</th>" for c in cabeceras)
    cuerpo = "".join("<tr>" + "".join(f"<td>{esc(str(c))}</td>" for c in f) + "</tr>" for f in filas)
    ancho = ' mc-tabla-ancha' if len(cabeceras) >= 4 else ''
    return (f'<div class="mc-tabla-scroll{ancho}" role="region" tabindex="0" aria-label="Tabla de datos; desplazamiento horizontal">'
            f'<table class="mc-cmp"><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></div>')


def foto_html(nombre: str, iniciales: str, url: str | None, pagina: str | None = None, actual: bool = False) -> str:
    """Círculo con la foto (o las iniciales si la foto no carga). Reutiliza el estilo de la línea de tiempo."""
    esc = html.escape
    img = (f'<img src="{esc(url)}" alt="{esc(nombre)}" loading="lazy" decoding="async" referrerpolicy="no-referrer">' if url else "")
    estilo = f' style="box-shadow:0 0 0 3px {SOL},0 0 20px rgba(246,180,14,.65)"' if actual else ""
    nodo = f'<div class="mc-foto"{estilo}><span>{esc(iniciales)}</span>{img}</div>'
    if pagina:
        nodo = f'<a href="{esc(pagina)}" target="_blank" rel="noopener noreferrer" title="{esc(nombre)} en Wikipedia">{nodo}</a>'
    return nodo


def viaje(nombre: str, iniciales: str, periodo: str, hito: str, url: str | None, pagina: str | None, actual: bool) -> str:
    esc = html.escape
    return (f'<div class="mc-viaje">{foto_html(nombre, iniciales, url, pagina, actual)}<div>'
            f'<div class="per">{esc(periodo)}</div><h3>{esc(nombre)}</h3><div class="hito">{esc(hito)}</div></div></div>')


def intro(texto_md: str, leyenda: list[tuple[str, str]] | None = None, nota_md: str = "", *, resumen: str = "",
          inicio: bool = False) -> str:
    """Cuadros de leyenda de las pestañas: se sacaron de todas las páginas (los textos y la leyenda de colores
    desaparecieron). La función sigue existiendo solo para la píldora «← Inicio» de las secciones del tablero;
    con cualquier otro uso devuelve vacío."""
    if not inicio:
        return ""
    return ('<div class="mc-intro-fila"><a class="mc-inicio" href="./?ver=tablero" target="_self" '
            'data-btn="nav_resumen" title="Ir al Resumen"><span>←</span>Inicio</a></div>')


def titulo(texto: str, cap: str = "", estado: str = "") -> str:
    """Encabezado de las secciones de Inicio: barra celeste, título y (si hay) bajada — la misma pieza que abre
    «En pocas palabras», de modo que todos los encabezados de la vista midan lo mismo. Con `estado`, a la derecha
    queda el indicador de datos (píldora con puntito), alineado con el borde de las tarjetas."""
    bajada = f'<p class="cap">{html.escape(cap)}</p>' if cap else ""
    clase = "mc-tit-seccion con-estado" if estado else "mc-tit-seccion"
    return (f'<div class="{clase}"><div class="tit"><h3 class="tt">{html.escape(texto)}</h3>{bajada}</div>'
            + estado + '</div>')


def pocas_titulo(cap: str) -> str:
    """Encabezado de «En pocas palabras» (la bajada la pasa la vista)."""
    return ('<div class="mc-pocas"><div class="tit"><div class="tt">En pocas palabras</div>'
            f'<div class="cap">{html.escape(cap)}</div></div></div>')


def pocas_items(filas: list[dict]) -> str:
    """Ítems de «En pocas palabras» sin encabezado ni pie: la vista los reparte en columnas.
    Cada fila: {num: '01', nombre: 'Dólar', href: enlace a la sección, texto: historia con <b>…</b>}.
    El texto va armado arriba (los valores ya escapados adentro); acá solo se estructura."""
    esc = html.escape
    renglones = "".join(
        f'<div class="fila"><span class="num">{esc(f["num"])}</span>'
        f'<a class="enl" href="{esc(f["href"])}">{esc(f["nombre"])}<span class="fl" aria-hidden="true">↗</span></a>'
        f'<p class="tx">{f["texto"]}</p></div>'
        for f in filas)
    return f'<div class="mc-pocas">{renglones}</div>' if renglones else ""


def pocas_pie() -> str:
    """Nota al pie de «En pocas palabras», a todo el ancho debajo de las columnas."""
    return ('<div class="mc-pocas"><div class="pie">Resumen automático con el último dato publicado por cada fuente '
            '(algunos tienen semanas de rezago).</div></div>')


def aclaracion(*filas: tuple[str, str], leyenda: list[tuple[str, str]] | None = None) -> str:
    """Aclaraciones al pie de un cuadro o gráfico, siempre con el mismo formato: una tarjeta chica con filas
    rotuladas («Colores», «Supuestos», «Fuente», «Ojo»...) para que se entienda por qué está cada texto.
    `leyenda`: [(«bien»|«mal»|«neutro», texto)] arma la fila «Colores» con sus puntitos. Admite **negrita**."""
    partes = []
    if leyenda:
        ley = "".join(f'<span class="{html.escape(c)}">{_md_a_html(t)}</span>' for c, t in leyenda)
        partes.append(f'<div class="f"><div class="et">Colores</div><div class="tx ley">{ley}</div></div>')
    partes += [f'<div class="f"><div class="et">{html.escape(e)}</div><div class="tx">{_md_a_html(t)}</div></div>'
               for e, t in filas if t]
    return f'<div class="mc-acl" role="note">{"".join(partes)}</div>'


def aviso(texto_md: str, titulo: str = "") -> str:
    """Recuadro de aclaración (dorado), con título opcional. Admite **negrita**; el resto se escapa."""
    tit = f'<div class="t">{html.escape(titulo)}</div>' if titulo else ""
    return (f'<div class="mc-aviso" role="note"><span class="ic" aria-hidden="true">i</span>'
            f'<div>{tit}<p>{_md_a_html(texto_md)}</p></div></div>')


def nota_destacada(titulo: str, valor: str, texto_md: str) -> str:
    """Recuadro celeste con un número grande: el dato clave de una pantalla."""
    esc = html.escape
    return (f'<div class="mc-nota"><div class="t">{esc(titulo)}</div><div class="v">{esc(valor)}</div>'
            f'<p>{_md_a_html(texto_md)}</p></div>')


def tabla(cabeceras: list[str], filas: list[list], compacta: bool = False) -> str:
    """Como tabla_simple, pero cada celda puede ser texto o (texto, clase[, aclaración]): clase 'mejor' (verde) o
    'peor' (rojo); la aclaración va en letra chica debajo. `compacta`: para tablas con la primera columna corta (en el
    celular no le reserva lugar para nombres largos)."""
    esc = html.escape

    def celda(c) -> str:
        if isinstance(c, tuple):
            texto, clase, *resto = c
            sub = f'<span class="sub">{esc(resto[0])}</span>' if resto and resto[0] else ""
            return f'<td class="{esc(clase or "")}">{esc(str(texto))}{sub}</td>'
        return f"<td>{esc(str(c))}</td>"

    cab = "".join(f"<th>{esc(c)}</th>" for c in cabeceras)
    cuerpo = "".join("<tr>" + "".join(celda(c) for c in f) + "</tr>" for f in filas)
    clase = "mc-tablas compacta" if compacta else "mc-tablas"
    return f'<div class="{clase}"><table class="mc-cmp"><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></div>'


def conceptos(grupos: list[tuple[str, list[tuple[str, str]]]]) -> str:
    """Tarjetas de conceptos agrupadas: [(grupo, [(término, definición)])]."""
    esc = html.escape
    return "".join(
        f'<div class="mc-conc-g">{esc(g)}</div><div class="mc-conc">'
        + "".join(f'<div class="c"><b>{esc(t)}</b><span>{esc(d)}</span></div>' for t, d in items) + "</div>"
        for g, items in grupos)


def comparacion(filas: list[dict], a: str, b: str) -> str:
    """Tabla A vs B. filas: [{'k', 'a', 'b', 'cambio', 'tend'}]."""
    esc = html.escape
    cuerpo = "".join(
        f'<tr><td>{esc(f["k"])}</td><td>{esc(f["a"])}</td><td>{esc(f["b"])}</td>'
        f'<td class="{f.get("tend", "")}">{esc(f["cambio"])}</td></tr>' for f in filas)
    return (f'<table class="mc-cmp"><thead><tr><th></th><th>{esc(a)}</th><th>{esc(b)}</th><th>Cambio</th></tr></thead>'
            f'<tbody>{cuerpo}</tbody></table>')


FUENTES = [
    ("BCRA", "Estadísticas y cotizaciones cambiarias", "https://www.bcra.gob.ar/"),
    ("INDEC / Ministerio de Economía", "Series de Tiempo (datos.gob.ar)", "https://www.datos.gob.ar/series/"),
    ("ArgentinaDatos", "Dólares, inflación histórica, riesgo país, plazos fijos, fondos y rendimientos",
     "https://argentinadatos.com/"),
    ("CoinGecko", "Criptomonedas", "https://www.coingecko.com/"),
    ("CriptoYa", "USDT por exchange y dólar MEP, CCL y cripto en vivo", "https://criptoya.com/"),
    ("Yahoo Finance", "Bolsas y materias primas (fuente no oficial)", "https://finance.yahoo.com/"),
    ("FRED (Reserva Federal de St. Louis)", "Tasa de la Fed, bonos del Tesoro e inflación de EE. UU.",
     "https://fred.stlouisfed.org/"),
    ("data912", "Bonos argentinos en dólares (precios de BYMA, fuente no oficial)", "https://data912.com/"),
    ("Wikipedia / Wikimedia Commons", "Fotos de presidentes y ministros", "https://commons.wikimedia.org/"),
]


def footer() -> str:
    """Pie de página con color propio (celeste de la paleta): fuentes, aviso y crédito."""
    esc = html.escape
    lista = "".join(f'<li><a href="{esc(u)}" title="{esc(d)}" target="_blank" rel="noopener noreferrer">{esc(n.split(" (")[0].split(" / ")[0])}</a></li>'
                    for n, d, u in FUENTES)
    return (
        '<div class="mc-foot">'
        + (f'<div class="bol"><div><b>Resumen semanal por mail</b><span>Todos los lunes, lo más importante de la '
           'economía en un minuto. Gratis y sin publicidad.</span></div>'
           f'<a href="{esc(BOLETIN, quote=True)}" target="_blank" rel="noopener noreferrer">Suscribirme →</a></div>'
           if BOLETIN else '')
        + f'<div class="bol err"><div><b>¿Notaste algún error?</b><span>Es una versión beta: si encontrás un error, un dato '
        'que no cierra o algo que se ve mal, contanos.</span></div>'
        f'<a href="{esc(_mail_error(), quote=True)}">Escribinos →</a></div>'
        + '<div class="main">'
        f'<div class="marca"><div class="logo">{bandera(30)}<div><b>MacroCenter</b><span>Creada por {esc(AUTOR)}</span></div>'
        f'<a class="mc-linkedin" href="{esc(LINKEDIN, quote=True)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="LinkedIn de {esc(AUTOR)}">{_ICONO_LINKEDIN} LinkedIn</a></div>'
        '<p>Reunir en un solo lugar los principales datos de la economía argentina, tomados de fuentes públicas y consultados periódicamente, '
        'para que cualquier persona pueda consultarlos, compararlos con su historia y entenderlos.</p></div>'
        f'<div class="fuentes"><div class="tit">Fuentes de datos</div><ul>{lista}</ul></div>'
        '</div>'
        '<details><summary>Importante: los datos pueden tener rezago y son de referencia</summary>'
        '<p><b>Algunos datos pueden tener un rezago</b> respecto de lo que difunden las fuentes en el día '
        '(por ejemplo, las reservas del BCRA se publican con 1 o 2 días de demora). '
        'Los datos vienen de APIs y sitios públicos y pueden tener demoras o revisiones. '
        'Los valores son de referencia y no constituyen asesoramiento financiero. Las notas y las calificaciones son '
        'medidas orientativas, con criterios propios.</p></details>'
        '<div class="legal"><span>© 2026 MacroCenter — Todos los derechos reservados.</span>'
        '<span class="made">Hecho en Argentina</span>'
        '<span><a href="?legal=terminos" target="_self">Términos y condiciones</a>'
        ' · <a href="?legal=privacidad" target="_self">Política de privacidad</a></span></div>'
        '<p class="frec">El dólar y el riesgo país se renuevan cada 30 segundos; cripto y bolsas, cada 5 minutos.</p>'
        '</div>'
    )


def estado_datos(hora_dolar: str | None, oficiales: str) -> str:
    """Franja del pie: «En vivo», a qué hora se actualizó el dólar y cuándo se bajaron las series oficiales."""
    esc = html.escape
    dolar = f"<span>Dólar: {esc(hora_dolar)}</span>" if hora_dolar else ""
    return (f'<div class="mc-vivo"><span class="en">Actualización periódica</span>{dolar}'
            f'<span class="sec">Series oficiales: {esc(oficiales)}</span></div>')


def pie_enlaces() -> str:
    """Enlace del resumen semanal y el aviso de derechos en la barra inferior; los legales quedan en «Acerca de»."""
    esc = html.escape
    bol = (f'<a class="bol" href="{esc(BOLETIN, quote=True)}" target="_blank" rel="noopener noreferrer" title="Resumen semanal por mail" aria-label="Suscribirme al resumen semanal"><span class="ic" aria-hidden="true">✉</span><span class="l">Resumen semanal</span>'
           '<span class="s">Suscribirme</span></a>'
           if BOLETIN else '')
    return f'<div class="mc-pielinks">{bol}<span class="c">© 2026 MacroCenter</span></div>'


def _mail_error() -> str:
    """Enlace de correo para avisar un error (beta), con asunto ya puesto. Va al contacto público de la página."""
    from urllib.parse import quote

    from macrocenter.legal import CONTACTO

    return f"mailto:{CONTACTO}?subject=" + quote("MacroCenter (beta): noté un error")


def legal_pagina(doc: dict, actualizacion: str) -> str:
    """Documento legal (términos, privacidad) en tarjetas sobrias. Los textos admiten **negrita**; todo lo demás se escapa."""
    esc = html.escape

    def texto(t: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t))

    secciones = "".join(
        f'<h3>{esc(titulo)}</h3><div class="card">' + "".join(f"<p>{texto(p)}</p>" for p in parrafos) + "</div>"
        for titulo, parrafos in doc["secciones"]
    )
    return (f'<div class="mc-legal"><h1>{esc(doc["titulo"])}</h1><div class="act">Última actualización: {esc(actualizacion)}</div>'
            f'<div class="card intro"><p>{texto(doc["intro"])}</p></div>{secciones}</div>')


def pie() -> str:
    return (f'<div class="mc-footer">{bandera(30)}<div>Creada por<br><b>{AUTOR}</b></div>'
            '<div class="mc-made">Hecho en Argentina</div></div>')
