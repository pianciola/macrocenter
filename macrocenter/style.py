"""Estilos de MacroCenter. Usa colores translúcidos para verse bien en modo claro y oscuro."""
from __future__ import annotations

import functools
import html
import math
import re

import streamlit as st

CELESTE = "#74ACDF"  # celeste de la bandera argentina
SOL = "#F6B40E"  # amarillo del Sol de Mayo
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
FUENTE = '"Segoe UI Variable Text", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Roboto, Arial, sans-serif'

CSS = f"""
<style>
/* ── Tipografía (los íconos de Streamlit conservan su propia fuente) ── */
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not([class*="material"]) {{ font-family: {FUENTE} !important; }}
.stApp {{ font-feature-settings: "tnum" 1, "lnum" 1; -webkit-font-smoothing: antialiased; }}
h1, h2, h3, h4 {{ letter-spacing: -.01em; }}
/* ── Barra lateral ── */
section[data-testid="stSidebar"] > div:first-child {{
    background-image: linear-gradient(180deg, rgba(116,172,223,.25) 0%, rgba(116,172,223,0) 40%);
    border-right: 1px solid rgba(116,172,223,.25);
}}
section[data-testid="stSidebar"] .block-container, section[data-testid="stSidebarUserContent"] {{ padding-top: 1.2rem; }}

.mc-brand {{
    background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%);
    border-radius: 16px; padding: 18px 18px 16px; margin-bottom: 18px;
    box-shadow: 0 6px 18px rgba(74,143,212,.35); color: #fff;
}}
.mc-flagsvg {{ display: block; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,.28); }}
.mc-brand .mc-flag {{ line-height: 0; }}
.mc-brand h1 {{ margin: 6px 0 2px; padding: 0; font-size: 1.55rem; font-weight: 800; letter-spacing: -.5px; color: #fff; }}
.mc-brand p {{ margin: 0; font-size: .8rem; opacity: .92; line-height: 1.35; }}

.mc-label {{
    font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
    opacity: .85; margin: 18px 0 6px;
}}

/* cotizaciones rápidas */
.mc-tick {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 12px; margin-bottom: 6px; border-radius: 10px;
    background: rgba(128,128,128,.10); border: 1px solid rgba(128,128,128,.14);
}}
.mc-tick .n {{ font-size: .82rem; opacity: .85; }}
.mc-tick .v {{ font-weight: 700; font-size: .95rem; text-align: right; }}
.mc-tick .d {{ font-size: .78rem; font-weight: 600; display: block; }}
.mc-up {{ color: #10AC84; }} .mc-down {{ color: #EE5253; }} .mc-flat {{ opacity: .85; }}

.mc-status {{ font-size: .78rem; opacity: .85; margin-top: 6px; }}
.mc-status .dot {{ color: #10AC84; }}

.mc-footer {{
    margin-top: 22px; padding-top: 14px; border-top: 3px double {CELESTE};
    font-size: .78rem; text-align: center; line-height: 1.5;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
}}
.mc-footer b {{ color: {CELESTE}; }}
.mc-footer .mc-made {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; opacity: .85; }}

/* botón de noticias: dorado (Sol de Mayo), distinto del resto */
[class*="st-key-btn_noticias"] button {{
    position: relative; border: none; border-radius: 12px; padding: .75rem 1rem; margin-bottom: 4px;
    background: linear-gradient(135deg, {SOL} 0%, #F79F1F 100%);
    box-shadow: 0 6px 16px rgba(246,180,14,.32); transition: transform .15s ease, box-shadow .15s ease;
}}
[class*="st-key-btn_noticias"] button p {{ color: #3A2A00 !important; font-weight: 800; font-size: .92rem; }}
[class*="st-key-btn_noticias"] button:hover {{
    border: none; transform: translateY(-2px); box-shadow: 0 10px 22px rgba(246,180,14,.5);
}}
[class*="st-key-btn_noticias"] button:active {{ transform: translateY(0); }}
.st-key-btn_noticias_nuevas button::after {{
    content: ""; position: absolute; top: -5px; right: -5px; width: 13px; height: 13px; border-radius: 50%;
    background: #EE5253; border: 2px solid #fff; animation: mc-pulso 1.8s infinite;
}}
@keyframes mc-pulso {{
    0% {{ box-shadow: 0 0 0 0 rgba(238,82,83,.65); }}
    70% {{ box-shadow: 0 0 0 9px rgba(238,82,83,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(238,82,83,0); }}
}}

/* botones y pills de la barra lateral */
section[data-testid="stSidebar"] .stButton > button {{
    border-radius: 10px; border: 1px solid rgba(116,172,223,.5); font-weight: 600;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{ border-color: {CELESTE}; color: {CELESTE}; }}
section[data-testid="stSidebar"] [data-testid="stPills"] button {{ border-radius: 999px; font-size: .8rem; }}

/* ── Barra lateral rediseñada: marca compacta, menú de lista, noticias en contorno dorado ── */
.mc-brand {{
    display: flex; align-items: center; gap: 12px; background: none; box-shadow: none; border-radius: 0;
    padding: 4px 2px 16px; margin-bottom: 16px; color: inherit; position: relative;
}}
.mc-brand::after {{
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 4px; border-radius: 4px;
    background: linear-gradient(to bottom, {CELESTE} 0 34%, #FFFFFF 34% 66%, {CELESTE} 66% 100%); opacity: .85;
}}
.mc-brand .mc-flag svg {{ width: 46px; height: 46px; }}
.mc-brand h1 {{ margin: 0; padding: 0; font-size: 1.45rem; font-weight: 800; letter-spacing: -.02em; color: inherit; }}
.mc-brand h1 span {{ color: {CELESTE}; }}
.mc-brand p.sub {{ margin: 2px 0 0; font-size: .78rem; font-weight: 500; opacity: .85; letter-spacing: .01em; }}

/* ── Barra lateral: terminación propia ── */
/* sin barra de desplazamiento (se veía la de Windows, gruesa y genérica): se sigue pudiendo deslizar, y el borde de
   abajo se desvanece para indicar que hay más */
[data-testid="stSidebarContent"] {{ scrollbar-width: none !important;
    -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 56px), transparent);
    mask-image: linear-gradient(to bottom, #000 calc(100% - 56px), transparent); }}
[data-testid="stSidebarContent"]::-webkit-scrollbar {{ display: none !important; width: 0 !important; }}
[data-testid="stSidebarUserContent"] {{ padding-bottom: 72px !important; }}
/* títulos de sección: celestes, con una línea fina hasta el borde */
section[data-testid="stSidebar"] .mc-label {{ display: flex; align-items: center; gap: 10px; color: {CELESTE}; opacity: .9;
    margin: 22px 0 8px; font-size: .78rem; letter-spacing: .16em; }}
section[data-testid="stSidebar"] .mc-label::after {{ content: ""; flex: 1; height: 1px; background: rgba(116,172,223,.22); }}
/* menú: cada opción con su ícono en celeste; la elegida, en una píldora con el ícono resaltado */
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {{ position: relative; border-left: none !important; border-radius: 12px !important;
    padding: .55rem .8rem !important; gap: .7rem; }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {{ padding-left: .8rem !important; background: rgba(116,172,223,.10); }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stIconMaterial"] {{
    color: {CELESTE}; font-size: 1.2rem; opacity: .85; }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {{
    background: rgba(116,172,223,.16) !important; box-shadow: inset 0 0 0 1px rgba(116,172,223,.35); }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{
    opacity: 1; }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"]::after {{
    content: ""; position: absolute; right: 12px; width: 6px; height: 6px; border-radius: 50%; background: {CELESTE}; }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] {{ margin-top: -4px; }}
/* atajos: ícono en un recuadro y una flecha que aparece al pasar el mouse */
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button > div > span {{ gap: 1.2rem !important; align-items: center; }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button {{ position: relative; padding: .38rem .55rem !important; }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button [data-testid="stIconMaterial"] {{
    color: {CELESTE}; font-size: 1rem; width: 28px; height: 28px; display: inline-flex; align-items: center;
    justify-content: center; border-radius: 8px; background: rgba(116,172,223,.13); flex: 0 0 28px; }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button::after {{
    content: "›"; position: absolute; right: 12px; font-size: 1.1rem; color: {CELESTE}; opacity: 0;
    transform: translateX(-4px); transition: opacity .15s ease, transform .15s ease; }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button:hover::after {{ opacity: 1; transform: none; }}
/* conversor: todo en una tarjeta */
section[data-testid="stSidebar"] .st-key-conv_caja {{ padding: 12px; border-radius: 14px; gap: .6rem;
    border: 1px solid rgba(116,172,223,.25); background: linear-gradient(180deg, rgba(116,172,223,.09), rgba(116,172,223,.03)); }}
section[data-testid="stSidebar"] .st-key-conv_caja .mc-conv {{ border: none; background: none; padding: 0 2px; }}
/* noticias: con ícono */
[class*="st-key-btn_noticias"] button [data-testid="stIconMaterial"] {{ color: {SOL}; font-size: 1.1rem; }}

[class*="st-key-btn_noticias"] button {{
    background: transparent !important; border: 1.5px solid {SOL} !important; box-shadow: none !important;
    border-radius: 999px; padding: .5rem 1rem; margin-bottom: 6px;
}}
[class*="st-key-btn_noticias"] button p {{ color: {SOL} !important; font-weight: 700; font-size: .88rem; }}
[class*="st-key-btn_noticias"] button:hover {{
    background: rgba(246,180,14,.14) !important; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(246,180,14,.25) !important;
}}
/* con noticias sin leer: el botón se rellena de dorado (Sol de Mayo) y late suave, para que se note sin gritar */
.st-key-btn_noticias_nuevas button {{
    background: linear-gradient(135deg, {SOL} 0%, #F79F1F 100%) !important; border-color: {SOL} !important;
    box-shadow: 0 0 0 0 rgba(246,180,14,.55) !important; animation: mc-latido 2.4s ease-out infinite;
}}
.st-key-btn_noticias_nuevas button p {{ color: #3A2A00 !important; font-weight: 800; }}
.st-key-btn_noticias_nuevas button:hover {{
    background: linear-gradient(135deg, #FFC52E 0%, #F7A93A 100%) !important; box-shadow: 0 6px 18px rgba(246,180,14,.45) !important;
}}
@keyframes mc-latido {{
    0% {{ box-shadow: 0 0 0 0 rgba(246,180,14,.55); }}
    70% {{ box-shadow: 0 0 0 10px rgba(246,180,14,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(246,180,14,0); }}
}}
@media (prefers-reduced-motion: reduce) {{ .st-key-btn_noticias_nuevas button {{ animation: none; }} }}

/* ── Campos de formulario: letra más grande ── */
[data-testid="stWidgetLabel"] p {{ font-size: 1rem !important; font-weight: 600; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{ font-size: 1.08rem !important; }}
/* sin el aviso «Press Enter to apply»: los montos se aplican solos al dejar de escribir (ver JS_PESTANAS) */
[data-testid="InputInstructions"] {{ display: none !important; }}

/* ── Botón «Volver al tablero»: píldora celeste con flecha que se corre al pasar el cursor ── */
.st-key-volver_tablero button {{
    border-radius: 999px !important; padding: .45rem 1.2rem .45rem .9rem !important; min-height: 0;
    background: rgba(116,172,223,.10) !important; border: 1px solid rgba(116,172,223,.45) !important;
    transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease;
}}
.st-key-volver_tablero button p {{ color: {CELESTE} !important; font-weight: 700; font-size: .92rem; }}
.st-key-volver_tablero button [data-testid="stIconMaterial"] {{ color: {CELESTE}; transition: transform .18s ease; }}
.st-key-volver_tablero button:hover {{
    background: rgba(116,172,223,.2) !important; border-color: {CELESTE} !important;
    box-shadow: 0 4px 14px rgba(74,143,212,.25);
}}
.st-key-volver_tablero button:hover [data-testid="stIconMaterial"] {{ transform: translateX(-3px); }}

/* ── Herramientas: selector en tarjetas ── */
[class*="st-key-modo_"] button {{
    min-height: 3.4rem; border-radius: 14px !important; justify-content: flex-start; padding: .7rem 1rem;
    border: 1px solid rgba(116,172,223,.35) !important; background: rgba(116,172,223,.06) !important;
    transition: transform .18s ease, background-color .18s ease, box-shadow .18s ease, border-color .18s ease;
}}
[class*="st-key-modo_"] button p {{ font-weight: 700; font-size: .95rem; text-align: left; white-space: normal !important;
    overflow: visible !important; text-overflow: clip !important; line-height: 1.25; }}
[class*="st-key-modo_"] button div {{ overflow: visible !important; min-width: 0; }}
[class*="st-key-modo_"] button [data-testid="stIconMaterial"] {{ color: {CELESTE}; font-size: 1.35rem; }}
[class*="st-key-modo_"] button:hover {{
    transform: translateY(-2px); border-color: {CELESTE} !important; background: rgba(116,172,223,.14) !important;
    box-shadow: 0 6px 16px rgba(74,143,212,.18);
}}
[class*="st-key-modo_"] button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%) !important; border-color: {CELESTE} !important;
    box-shadow: 0 6px 18px rgba(74,143,212,.35), inset 0 -3px 0 {SOL};
}}
[class*="st-key-modo_"] button[data-testid="stBaseButton-primary"] p,
[class*="st-key-modo_"] button[data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{ color: #FFFFFF !important; }}

/* ── Ventana de noticias: lista limpia, fecha a la izquierda, etiquetas de fuente ── */
.mc-news {{ display: flex; flex-direction: column; margin-top: 6px; }}
.mc-news-it {{
    display: grid; grid-template-columns: 58px 1fr; gap: 14px; padding: 14px 10px; border-radius: 12px;
    border-bottom: 1px solid rgba(128,128,128,.18); transition: background-color .15s ease;
}}
.mc-news-it:hover {{ background: rgba(116,172,223,.07); }}
.mc-news-it.es-nueva {{ background: rgba(246,180,14,.07); box-shadow: inset 3px 0 0 {SOL}; }}
.mc-news-fecha {{
    display: flex; flex-direction: column; align-items: center; justify-content: center; height: 58px;
    border-radius: 12px; border: 1px solid rgba(116,172,223,.35); background: rgba(116,172,223,.08);
}}
.mc-news-fecha b {{ font-size: 1.35rem; line-height: 1; }}
.mc-news-fecha span {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; opacity: .85; margin-top: 3px; }}
.mc-news-tags {{ display: flex; gap: 6px; margin-bottom: 5px; }}
.mc-news .tag {{ font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; padding: 2px 8px;
    border-radius: 999px; }}
.mc-news .tag.bcra {{ color: {CELESTE}; background: rgba(116,172,223,.15); }}
.mc-news .tag.economia {{ color: #A9B8C9; background: rgba(169,184,201,.13); }}
.mc-news .tag.nueva {{ color: #3A2A00; background: {SOL}; }}
.mc-news-txt a {{ font-weight: 700; font-size: .98rem; line-height: 1.35; color: inherit !important; text-decoration: none; }}
.mc-news-txt a:hover {{ color: {CELESTE} !important; text-decoration: underline; text-underline-offset: 3px; }}
.mc-news-txt p {{ margin: 5px 0 0; font-size: .84rem; opacity: .85; line-height: 1.45;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.mc-news-pie {{ font-size: .8rem; opacity: .8; margin-top: 12px; }}
.mc-news-pie a {{ color: {CELESTE} !important; }}
.mc-news-vacio {{ padding: 18px; opacity: .85; }}
/* botón «Marcar todas como leídas» y su estado ya leído (verde) */
.st-key-btn_marcar_leidas button {{ border: 1px solid rgba(116,172,223,.45) !important; border-radius: 999px !important;
    background: rgba(116,172,223,.08) !important; min-height: 0 !important; padding: .32rem .9rem !important; }}
.st-key-btn_marcar_leidas button p {{ color: {CELESTE} !important; font-weight: 700; font-size: .84rem !important; }}
.st-key-btn_marcar_leidas button:hover {{ background: rgba(116,172,223,.18) !important; border-color: {CELESTE} !important; }}
.st-key-btn_todo_leido button {{
    background: #10AC84 !important; border: 1px solid #10AC84 !important; border-radius: 999px !important;
    min-height: 0 !important; padding: .32rem .9rem !important;
}}
.st-key-btn_todo_leido button p {{ font-size: .84rem !important; }}
.st-key-btn_todo_leido button p {{ color: #FFFFFF !important; font-weight: 700; }}
.st-key-btn_todo_leido button:hover {{ background: #0E9673 !important; }}

/* menú de navegación: filas planas, la activa con barra celeste a la izquierda */
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {{
    justify-content: flex-start; text-align: left; background: transparent; border: none;
    border-left: 3px solid transparent; border-radius: 0 10px 10px 0; padding: .55rem .9rem; min-height: 0;
    transition: background-color .15s ease, border-color .15s ease, padding-left .15s ease;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div,
section[data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stMarkdownContainer"] {{
    justify-content: flex-start !important; width: 100%; text-align: left !important;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p {{ font-weight: 600; font-size: .95rem; text-align: left; }}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {{
    background: rgba(116,172,223,.12); border-left-color: rgba(116,172,223,.6); padding-left: 1.1rem; color: inherit;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(90deg, rgba(116,172,223,.28), rgba(116,172,223,.04)); border-left-color: {CELESTE};
    color: inherit;
}}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] p {{ font-weight: 800; }}

/* conversor de pesos y dólares, y término del día */
.mc-conv, .mc-termino {{
    border: 1px solid rgba(116,172,223,.28); border-radius: 12px; padding: 10px 12px;
    background: rgba(116,172,223,.07);
}}
.mc-conv .f {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; padding: 5px 0;
    border-bottom: 1px dashed rgba(128,128,128,.25); }}
.mc-conv .f:has(+ .nota) {{ border-bottom: none; }}
.mc-conv .k {{ font-size: .82rem; font-weight: 600; display: flex; flex-direction: column; line-height: 1.2; }}
.mc-conv .k small {{ font-size: .78rem; font-weight: 500; opacity: .85; }}
.mc-conv .v {{ font-size: .98rem; font-weight: 800; white-space: nowrap; }}
.mc-conv .nota {{ font-size: .78rem; opacity: .85; margin-top: 4px; text-align: right; }}
section[data-testid="stSidebar"] .st-key-conv_sentido button {{ padding: .25rem .5rem; font-size: .8rem; flex: 1 1 0; }}
section[data-testid="stSidebar"] .st-key-conv_sentido [data-baseweb="button-group"],
section[data-testid="stSidebar"] .st-key-conv_sentido [role="radiogroup"] {{ width: 100%; flex-wrap: nowrap; }}
section[data-testid="stSidebar"] .st-key-conv_pesos input, section[data-testid="stSidebar"] .st-key-conv_usd input {{
    font-weight: 700; }}
.mc-termino {{ border-left: 3px solid {SOL}; }}
.mc-termino-t {{ font-weight: 800; font-size: .95rem; margin-bottom: 4px; color: {SOL}; }}
.mc-termino-d {{ font-size: .82rem; line-height: 1.45; opacity: .9; }}
/* atajos: como el menú, pero más chicos y con ícono */
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button {{
    justify-content: flex-start; background: transparent; border: none; border-radius: 10px;
    padding: .35rem .7rem; min-height: 0;
}}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button > div,
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button [data-testid="stMarkdownContainer"] {{
    justify-content: flex-start !important; text-align: left !important;
}}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button p {{ font-size: .86rem; font-weight: 500; }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button:hover {{ background: rgba(116,172,223,.12); }}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] {{ margin-top: -6px; }}
/* botón «Personalizar» de Indicadores clave: píldora chica alineada a la derecha, con ícono de ajustes */
.st-key-personalizar {{ align-items: flex-end; }}
.st-key-personalizar [data-testid="stPopover"] > div > button, .st-key-personalizar [data-testid="stPopoverButton"] {{
    min-height: 0 !important; padding: .32rem .85rem .32rem .7rem !important; border-radius: 999px !important;
    border: 1px solid rgba(116,172,223,.45) !important; background: rgba(116,172,223,.08) !important;
    transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}}
.st-key-personalizar [data-testid="stPopoverButton"] p {{ font-size: .84rem !important; font-weight: 700; color: {CELESTE} !important; }}
.st-key-personalizar [data-testid="stPopoverButton"] [data-testid="stIconMaterial"] {{ color: {CELESTE}; font-size: 1.05rem; }}
.st-key-personalizar [data-testid="stPopoverButton"]:hover {{
    background: rgba(116,172,223,.18) !important; border-color: {CELESTE} !important;
    box-shadow: 0 4px 12px rgba(74,143,212,.2); transform: translateY(-1px);
}}
/* un solo criterio para los botones de acción que van a la derecha de un título (Personalizar, Ver otro análisis):
   píldora celeste chica con ícono. Mismo diseño que «Refrescar datos» del pie. */
.st-key-inicio_otro button {{
    min-height: 0 !important; padding: .32rem .85rem .32rem .7rem !important; border-radius: 999px !important;
    border: 1px solid rgba(116,172,223,.45) !important; background: rgba(116,172,223,.08) !important;
    transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}}
.st-key-inicio_otro button p {{ font-size: .84rem !important; font-weight: 700; color: {CELESTE} !important; white-space: nowrap !important; }}
.st-key-inicio_otro button [data-testid="stIconMaterial"] {{ color: {CELESTE}; font-size: 1.05rem; }}
.st-key-inicio_otro button:hover {{
    background: rgba(116,172,223,.18) !important; border-color: {CELESTE} !important;
    box-shadow: 0 4px 12px rgba(74,143,212,.2); transform: translateY(-1px);
}}
/* títulos de sección: mismo tamaño y el mismo aire arriba en todas las pestañas y vistas (antes había títulos de
   28, 24 y 20 px según la pestaña, y ninguno se separaba de lo anterior más que el espacio común entre bloques) */
[data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stHeadingWithActionElements"]):not(:first-child) {{
    margin-top: 14px; }}
/* JERARQUÍA DE TÍTULOS (igual en todas las pestañas y vistas):
   · sección (h3/h4): 24 px, negrita, con barra celeste a la izquierda; distingue la sección de los títulos de los gráficos
   · subsección (h5): 18 px, negrita, sin barra
   · gráfico: negrita chica, dentro de la figura
   Quedan afuera los títulos de las tarjetas propias (línea de tiempo, ministros…): son componentes con su estilo. */
[data-testid="stMain"] [data-testid="stHeadingWithActionElements"]:not([class*="mc-"] *) :is(h3, h4) {{
    font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -.01em;
    border-left: 4px solid {CELESTE}; padding-left: 12px !important; line-height: 1.25; }}
[data-testid="stMain"] [data-testid="stHeadingWithActionElements"]:not([class*="mc-"] *) h5 {{
    font-size: 1.15rem !important; font-weight: 700 !important; line-height: 1.3; }}
/* los títulos de las tarjetas propias no llevan la barra */
[data-testid="stMain"] [class*="mc-"] [data-testid="stHeadingWithActionElements"] :is(h3, h4, h5) {{
    border-left: none !important; padding-left: 0 !important; }}
/* informe "En pocas palabras" de Inicio: neutral (no califica nada como bueno o malo). Título como los demás títulos
   de sección (barra celeste), filas numeradas separadas por líneas finas, misma letra que el resto de la página */
.mc-pano {{ margin: 6px 0 10px; counter-reset: pano; }}
.mc-pano .cab {{ padding: 4px 0 12px; border-bottom: 1px solid rgba(128,128,128,.35); }}
.mc-pano .cab .tit {{ font-size: 1.5rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.25;
    border-left: 4px solid {CELESTE}; padding-left: 12px; }}
.mc-pano .cab .sub {{ font-size: .84rem; opacity: .85; margin: 4px 0 0 16px; }}
.mc-pano .fila {{ display: grid; grid-template-columns: 2.1rem 150px 1fr; gap: 18px; align-items: baseline;
    padding: 15px 2px; counter-increment: pano; }}
.mc-pano .fila + .fila {{ border-top: 1px solid rgba(128,128,128,.2); }}
.mc-pano .fila::before {{ content: counter(pano, decimal-leading-zero); font-size: .9rem; font-weight: 700;
    color: {CELESTE}; opacity: .8; font-variant-numeric: tabular-nums; }}
.mc-pano .tema {{ font-size: .8rem; font-weight: 600; opacity: .85; }}
.mc-pano .cifra {{ font-size: 1.45rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.15;
    font-variant-numeric: tabular-nums; margin: 1px 0; }}
.mc-pano .det {{ font-size: .78rem; opacity: .85; }}
.mc-pano .txt {{ font-size: .94rem; line-height: 1.6; }}
.mc-pano .txt strong, .mc-pano .txt :is(.pos, .neg) {{ font-weight: 700; color: inherit; }}
:is(.mc-nota, .mc-aviso) .pos {{ color: #10AC84; font-weight: 700; }}
:is(.mc-nota, .mc-aviso) .neg {{ color: #EE5253; font-weight: 700; }}
.mc-pano .pie {{ font-size: .78rem; opacity: .85; padding: 10px 0 0; border-top: 1px solid rgba(128,128,128,.35); }}
@container principal (max-width: 640px) {{
    .mc-pano .fila {{ grid-template-columns: 1.8rem 1fr; gap: 4px 10px; padding: 13px 0; }}
    .mc-pano .izq {{ display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }}
    .mc-pano .txt {{ grid-column: 2; font-size: .9rem; }}
    .mc-pano .cifra {{ font-size: 1.15rem; }}
    .mc-pano .cab .tit {{ font-size: 1.3rem; }}
}}

/* actualizar datos: discreto, al pie */
section[data-testid="stSidebar"] .st-key-actualizar button {{
    background: transparent; border: 1px dashed rgba(116,172,223,.5); font-size: .82rem; font-weight: 600;
}}

/* selector de gráficos (control segmentado): pista celeste suave y opción activa rellena */
[data-testid="stButtonGroup"] [role="radiogroup"]:has(button[data-variant="segmented_control"]) {{
    background: rgba(116,172,223,.12); border: 1px solid rgba(116,172,223,.28); border-radius: 14px;
    padding: 4px; gap: 4px; display: inline-flex; flex-wrap: wrap;
}}
button[data-variant="segmented_control"] {{
    border: none !important; border-radius: 10px !important; background: transparent !important;
    padding: .45rem 1.1rem; min-height: 0; font-weight: 600;
    transition: background-color .18s ease, color .18s ease, box-shadow .18s ease, transform .18s ease;
}}
button[data-variant="segmented_control"]:hover {{
    background: rgba(116,172,223,.22) !important; transform: translateY(-1px);
}}
button[data-variant="segmented_control"][aria-checked="true"] {{
    background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%) !important; color: #fff !important;
    box-shadow: 0 3px 10px rgba(74,143,212,.4); font-weight: 700;
}}
button[data-variant="segmented_control"][aria-checked="true"] p {{ color: #fff !important; }}

/* selectores de los gráficos: lo que se mira (categoría) y desde cuándo (período) se ven distintos en todas las pestañas.
   · CATEGORÍA (claves cat_*): fichas redondas sueltas; la elegida va rellena de celeste.
   · PERÍODO (claves per_*): grupo compacto de botones unidos, más chico; el activo lleva el amarillo del Sol de Mayo. */
[class*="st-key-cat_"] button[data-variant="pills"] {{
    border-radius: 999px; padding: .32rem 1rem; min-height: 0; font-weight: 600;
    border: 1px solid rgba(128,128,128,.38); background: transparent;
    transition: background-color .18s ease, border-color .18s ease, color .18s ease, box-shadow .18s ease;
}}
[class*="st-key-cat_"] button[data-variant="pills"]:hover {{ border-color: {CELESTE}; color: {CELESTE}; }}
[class*="st-key-cat_"] button[data-variant="pills"]:is([aria-checked="true"], [aria-pressed="true"]) {{
    background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%) !important; border-color: transparent !important;
    color: #fff !important; font-weight: 700; box-shadow: 0 2px 8px rgba(74,143,212,.38);
}}
[class*="st-key-cat_"] button[data-variant="pills"]:is([aria-checked="true"], [aria-pressed="true"]) p {{ color: #fff !important; }}
[class*="st-key-per_"] [role="radiogroup"], .st-key-cal_anios [role="radiogroup"] {{
    display: inline-flex; flex-wrap: nowrap; gap: 0; padding: 3px; max-width: 100%; overflow-x: auto;
    border-radius: 10px; background: rgba(128,128,128,.14); border: 1px solid rgba(128,128,128,.24);
}}
[class*="st-key-per_"] button[data-variant="pills"], .st-key-cal_anios button[data-variant="pills"] {{
    border: none !important; border-radius: 7px !important; background: transparent !important;
    padding: .2rem .75rem; min-height: 0; font-size: .82rem; font-weight: 600; white-space: nowrap;
    transition: background-color .18s ease, box-shadow .18s ease;
}}
[class*="st-key-per_"] button[data-variant="pills"] p, .st-key-cal_anios button[data-variant="pills"] p {{ font-size: .82rem !important; }}
[class*="st-key-per_"] button[data-variant="pills"]:hover, .st-key-cal_anios button[data-variant="pills"]:hover {{
    background: rgba(128,128,128,.22) !important;
}}
[class*="st-key-per_"] button[data-variant="pills"][aria-checked="true"], .st-key-cal_anios button[data-variant="pills"][aria-checked="true"] {{
    background: rgba(246,180,14,.24) !important; box-shadow: inset 0 0 0 1px {SOL}; font-weight: 700;
}}
/* angosto: el selector ocupa todo el ancho y todas las opciones quedan a la vista (antes se deslizaba y escondía
   «1 mes»); si igual no entran, pasan a otra fila parejas */
@container principal (max-width: 560px) {{
    [class*="st-key-per_"] [role="radiogroup"], .st-key-cal_anios [role="radiogroup"] {{ display: flex; width: 100%;
        flex-wrap: wrap; overflow: visible; }}
    [class*="st-key-per_"] button[data-variant="pills"], .st-key-cal_anios button[data-variant="pills"] {{
        flex: 1 1 auto; padding: .22rem .28rem; justify-content: center; }}
    [class*="st-key-per_"] button[data-variant="pills"] p, .st-key-cal_anios button[data-variant="pills"] p {{ font-size: .78rem !important; }}
}}

@container principal (max-width: 640px) {{
    .st-key-cal_nota [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }}
    .st-key-cal_nota [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ width: 100% !important;
        flex: 1 1 100% !important; min-width: 0 !important; }}
}}
/* título de gráfico (antes lo dibujaba Plotly): mismo aspecto, pero se parte en renglones; pegado a su gráfico */
.mc-gtit {{ margin: 6px 0 0; padding-left: 2px; }}
.mc-gtit .t {{ font-size: 16px; font-weight: 700; line-height: 1.3; }}
.mc-gtit .b {{ font-size: 13px; opacity: .85; margin-top: 2px; }}
/* botón para ocultar / mostrar la barra del pie (lo crea JS_PESTANAS). Discreto: solo una flechita casi transparente.
   El estado va en html[data-pie="oculto"] y NO en una clase con «mc-»: varios estilos (títulos de sección) excluyen todo lo
   que está dentro de un elemento con «mc-» en la clase, y con una clase en <html> perdían su estilo */
.mc-pie-btn {{ position: fixed; right: 140px; bottom: 66px; z-index: 95; width: 32px; height: 32px; padding: 0;
    display: flex; align-items: center; justify-content: center; border-radius: 50%; cursor: pointer;
    border: 1px solid rgba(116,172,223,.6); background: #13233a; color: {CELESTE};
    font: 700 13px/1 inherit; opacity: .85; box-shadow: 0 2px 8px rgba(0,0,0,.35);
    transition: opacity .15s ease, transform .15s ease, bottom .3s ease, width .3s ease, height .3s ease,
    border-radius .3s ease; }}
.mc-pie-btn:hover, .mc-pie-btn:focus-visible {{ opacity: 1; transform: translateY(-1px); }}
html[data-pie] .mc-pie-btn {{ bottom: 0; width: 56px; height: 22px; border-radius: 10px 10px 0 0; border-bottom: 0;
    opacity: .85; }}
html[data-pie="oculto"] .st-key-pie_datos {{ display: none !important; }}
/* apertura y cierre animados: la barra sube desde el borde inferior o baja hasta desaparecer (lo marca JS_PESTANAS) */
@keyframes mc-pie-entra {{ from {{ transform: translateY(100%); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
@keyframes mc-pie-sale {{ from {{ transform: none; opacity: 1; }} to {{ transform: translateY(100%); opacity: 0; }} }}
html[data-pie-anim="entra"] .st-key-pie_datos {{ animation: mc-pie-entra .3s ease-out; }}
html[data-pie-anim="sale"] .st-key-pie_datos {{ animation: mc-pie-sale .3s ease-in forwards; }}
html[data-pie="oculto"] [data-testid="stMainBlockContainer"] {{ padding-bottom: 2rem !important; }}
@media (max-width: 560px) {{ .mc-pie-btn {{ right: 12px; }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-pie-btn {{ transition: none; }}
    html[data-pie-anim] .st-key-pie_datos {{ animation: none; }} }}
/* quien ya se anotó en las alertas no vuelve a ver el formulario (lo marca JS_PESTANAS en este navegador) */
html[data-alertas="anotado"] .mc-alerta {{ display: none !important; }}
.mc-alerta-ok {{ margin: 10px 0 18px; padding: 12px 16px; border-radius: 14px; font-size: 14px;
    border: 1px solid rgba(16,172,132,.45); background: rgba(16,172,132,.10); }}
/* formulario de alertas del dólar (pestaña Dólar) */
.mc-alerta {{
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin: 10px 0 18px; padding: 14px 16px;
    border: 1px solid rgba(74,143,212,.35); border-radius: 14px; background: rgba(74,143,212,.07);
}}
.mc-alerta .tx {{ flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 3px; }}
.mc-alerta .tx b {{ font-size: 15px; }}
.mc-alerta .tx span {{ font-size: 13px; opacity: .85; line-height: 1.4; }}
.mc-alerta .cp {{ display: flex; gap: 8px; flex: 1 1 280px; max-width: 420px; }}
.mc-alerta input[type=email] {{
    flex: 1 1 auto; min-width: 0; padding: 9px 12px; border-radius: 10px; font: inherit; font-size: 14px;
    border: 1px solid rgba(128,128,128,.45); background: rgba(0,0,0,.18); color: inherit;
}}
.mc-alerta input[type=email]:focus {{ outline: 2px solid #4A8FD4; outline-offset: 1px; }}
.mc-alerta button {{
    flex: 0 0 auto; padding: 9px 16px; border-radius: 10px; border: 0; cursor: pointer; font: inherit;
    font-size: 14px; font-weight: 700; color: #fff; background: #2E86DE;
}}
.mc-alerta button:hover {{ background: #4A8FD4; }}
@container principal (max-width: 560px) {{ .mc-alerta .cp {{ max-width: none; }} }}
/* fila del título de cada gráfico: el título ocupa lo que haya y «CSV» (bajar los datos) queda chico a la derecha */
[class*="st-key-gtit_"] {{ flex-wrap: nowrap !important; gap: 6px !important; }}
[class*="st-key-gtit_"] > div:first-child {{ flex: 1 1 auto !important; min-width: 0; }}
[class*="st-key-gtit_"] > div:last-child:not(:first-child) {{ flex: 0 0 auto !important; width: auto !important; }}
[class*="st-key-gtit_"] [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
[class*="st-key-gtit_"] [data-testid="stDownloadButton"] button {{
    min-height: 0 !important; padding: 2px 6px !important; opacity: .5; transition: opacity .15s;
}}
[class*="st-key-gtit_"] [data-testid="stDownloadButton"] button p {{ font-size: 12px !important; font-weight: 600; }}
[class*="st-key-gtit_"] [data-testid="stDownloadButton"] button:hover,
[class*="st-key-gtit_"] [data-testid="stDownloadButton"] button:focus-visible {{ opacity: 1; }}
.st-key-cal_kpis {{ flex-wrap: wrap; }}
.st-key-cal_kpis > * {{ flex: 1 1 150px !important; min-width: 0; }}
.st-key-cal_kpis [data-testid="stElementContainer"], .st-key-cal_kpis [data-testid="stMetric"] {{ height: auto !important; }}

/* ── Zona principal ── */
.mc-hero {{
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
    padding: 6px 0 14px;
}}
.mc-title {{ display: flex; align-items: center; gap: 16px; padding: 4px 0 6px; }}
.mc-title .mc-flag {{ line-height: 0; }}
.mc-sunsvg {{ display: block; filter: drop-shadow(0 2px 4px rgba(246,180,14,.35)); }}
/* franja celeste - blanca - celeste, como la bandera */
.mc-stripe {{
    height: 8px; border-radius: 4px; margin-bottom: 10px;
    background: linear-gradient(to bottom, {CELESTE} 0 33.4%, #FFFFFF 33.4% 66.6%, {CELESTE} 66.6% 100%);
    box-shadow: 0 0 0 1px rgba(116,172,223,.55);
}}
.mc-title h1 {{ margin: 0; padding: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: -.8px; }}
.mc-title .sub {{ opacity: .85; font-size: .92rem; }}
.mc-by {{ font-size: .82rem; opacity: .85; text-align: right; }}
.mc-by b {{ color: {CELESTE}; opacity: 1; }}

/* ── Línea de tiempo de presidentes ── */
.mc-tl {{ position: relative; margin: 18px 0 6px; }}
.mc-tl::before {{
    content: ""; position: absolute; left: 50%; top: 0; bottom: 0; width: 6px; transform: translateX(-50%);
    border-radius: 3px; box-shadow: 0 0 0 1px rgba(116,172,223,.5);
    background: linear-gradient(to right, {CELESTE} 0 33%, #FFFFFF 33% 66%, {CELESTE} 66% 100%);
}}
.mc-tl-item {{
    display: grid; grid-template-columns: 1fr 116px 1fr; align-items: center; margin-bottom: 28px; position: relative;
}}
.mc-tl-card {{
    grid-row: 1; padding: 16px 18px 14px; border-radius: 16px; background: rgba(128,128,128,.09);
    border: 1px solid rgba(116,172,223,.38); box-shadow: 0 4px 14px rgba(0,0,0,.10);
}}
.mc-tl-item.izq .mc-tl-card {{ grid-column: 1; }}
.mc-tl-item.der .mc-tl-card {{ grid-column: 3; }}
.mc-tl-dot {{ grid-column: 2; grid-row: 1; justify-self: center; position: relative; z-index: 1; }}
.mc-foto {{
    width: 88px; height: 88px; border-radius: 50%; position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 1.6rem;
    background: linear-gradient(135deg, {CELESTE}, #4A8FD4); border: 4px solid #FFFFFF;
    box-shadow: 0 0 0 3px {CELESTE}, 0 6px 16px rgba(0,0,0,.3);
}}
.mc-foto img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top center; }}
.mc-tl-item.actual .mc-foto {{ box-shadow: 0 0 0 3px {SOL}, 0 0 20px rgba(246,180,14,.65); }}
.mc-tl-anio {{ grid-row: 1; font-size: 2rem; font-weight: 800; letter-spacing: -1px; opacity: .85; }}
.mc-tl-item.izq .mc-tl-anio {{ grid-column: 3; padding-left: 24px; }}
.mc-tl-item.der .mc-tl-anio {{ grid-column: 1; text-align: right; padding-right: 24px; }}
.mc-tl-card h4 {{ margin: 0 0 2px; padding: 0; font-size: 1.25rem; font-weight: 800; }}
.mc-tl-card .per {{ font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {CELESTE}; }}
.mc-tl-card .hito {{ font-size: .88rem; opacity: .88; margin: 8px 0 10px; line-height: 1.4; }}
.mc-fila {{
    display: flex; justify-content: space-between; gap: 10px; padding: 5px 0;
    border-top: 1px dashed rgba(128,128,128,.3); font-size: .84rem;
}}
.mc-fila .k {{ opacity: .85; }}
.mc-fila .v {{ font-weight: 600; text-align: right; }}
.mc-fila .mejor {{ color: #10AC84; }}
.mc-fila .peor {{ color: #EE5253; }}
.mc-tl-card .pico {{ margin-top: 8px; font-size: .8rem; opacity: .9; }}
.mc-tl-card .nota {{ margin-top: 6px; font-size: .78rem; opacity: .85; font-style: italic; }}
.mc-tl-hoy {{
    width: max-content; margin: 0 auto; padding: 5px 16px; border-radius: 999px; font-weight: 800; font-size: .8rem;
    letter-spacing: .14em; color: #3A2A00; background: linear-gradient(135deg, {SOL}, #F79F1F);
    box-shadow: 0 4px 12px rgba(246,180,14,.4); position: relative; z-index: 1;
}}
/* ── Selector de sección de Historia y de Ahorro e inversiones: pestañas grandes ── */
:is(.st-key-hist_seccion, .st-key-inv_seccion), :is(.st-key-hist_seccion, .st-key-inv_seccion) [data-testid="stButtonGroup"] {{ width: 100% !important; }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) [data-testid="stButtonGroup"] > div {{ width: 100% !important; max-width: none !important; display: flex; gap: 10px; }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button {{
    flex: 1 1 0; min-width: 0; min-height: 3.3rem; border-radius: 16px !important; padding: .6rem 1.1rem !important;
    border: 1px solid rgba(116,172,223,.4) !important; background: rgba(116,172,223,.07) !important;
    transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease;
}}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button p {{ font-size: 1.02rem !important; font-weight: 800; }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(74,143,212,.2); }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button[aria-checked="true"] {{
    background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%) !important; border-color: {CELESTE} !important;
    box-shadow: 0 8px 20px rgba(74,143,212,.35), inset 0 -3px 0 {SOL};
}}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button[aria-checked="true"] p {{ color: #fff !important; }}

/* con cuatro secciones, en pantallas angostas pasan a dos por fila */
/* selectores grandes de sección (Historia, Ahorro e inversiones) con poco ancho: letra algo menor y el texto puede bajar
   de renglón en vez de cortarse */
@container principal (max-width: 640px) {{
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button {{ padding: .5rem .55rem !important; min-height: 2.9rem; }}
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button p {{
        font-size: .9rem !important; white-space: normal !important; overflow: visible !important;
        text-overflow: clip !important; line-height: 1.2; text-align: center; }}
}}
@container principal (max-width: 640px) {{
    .st-key-inv_seccion [data-testid="stButtonGroup"] > div {{ flex-wrap: wrap; }}
    .st-key-inv_seccion button {{ flex: 1 1 calc(50% - 10px); min-height: 2.9rem; }}
    .st-key-inv_seccion button p {{ font-size: .9rem !important; }}
}}

/* selector de Herramientas (cinco tarjetas): si no entran en una fila, pasan a la siguiente (antes, con poco ancho, el
   texto de cada botón se partía letra por letra) */
/* grilla según el ancho real: 5 en fila; si no entran, 3 + 2 (filas parejas, nunca una tarjeta sola estirada);
   en el celular, de a 2 y la última a lo ancho */
[data-testid="stHorizontalBlock"]:has(.st-key-modo_0) {{ display: grid !important; gap: .75rem !important;
    grid-template-columns: repeat(5, minmax(0, 1fr)); }}
[data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"] {{ width: auto !important; min-width: 0 !important; }}
@container principal (max-width: 980px) {{
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) {{ grid-template-columns: repeat(6, minmax(0, 1fr)); }}
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"] {{ grid-column: span 2; }}
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"]:nth-child(n+4) {{ grid-column: span 3; }}
}}
@container principal (max-width: 520px) {{
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"]:nth-child(n+4) {{ grid-column: span 1; }}
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"]:last-child:nth-child(odd) {{ grid-column: span 2; }}
}}
[class*="st-key-modo_"] button p {{ word-break: normal !important; overflow-wrap: normal !important; }}

/* ── Ahorro e inversiones ── */
.mc-aviso {{ display: flex; gap: 14px; align-items: flex-start; margin: 6px 0 22px; padding: 14px 18px 14px 16px;
    border-radius: 12px; border: 1px solid rgba(246,180,14,.28); border-left: 4px solid {SOL};
    background: linear-gradient(90deg, rgba(246,180,14,.12), rgba(246,180,14,.03) 60%); font-size: .95rem; line-height: 1.55; }}
.mc-aviso .ic {{ flex: 0 0 auto; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; background: rgba(246,180,14,.18); color: {SOL}; font: 800 16px/1 Georgia, serif; font-style: italic; }}
.mc-aviso .t {{ font-weight: 800; font-size: 1rem; color: {SOL}; margin-bottom: 2px; }}
.mc-aviso p {{ margin: 0; }}
.mc-aviso b {{ color: {SOL}; }}
html[data-tema="claro"] .mc-aviso {{ background: #FFF8E6; border-color: #F1D58C; border-left-color: #C98A00; }}
html[data-tema="claro"] .mc-aviso .t, html[data-tema="claro"] .mc-aviso b {{ color: #8A5A00; }}
html[data-tema="claro"] .mc-aviso .ic {{ background: #FBE7B5; color: #8A5A00; }}
.mc-nota {{ margin: 10px 0 14px; padding: 16px 20px; border-radius: 16px; border: 1px solid rgba(116,172,223,.35);
    background: linear-gradient(135deg, rgba(116,172,223,.16) 0%, rgba(116,172,223,.05) 100%); }}
.mc-nota .t {{ font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: {CELESTE}; }}
.mc-nota .v {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; margin: 2px 0 4px; }}
.mc-nota p {{ margin: 0; font-size: .92rem; line-height: 1.55; }}
.mc-cmp td.mejor, .mc-cmp td.peor {{ font-weight: 700; }}
.mc-cmp td .sub {{ display: block; font-size: .78rem; font-weight: 400; opacity: .85; }}
.mc-conc-g {{ margin: 18px 0 6px; font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase;
    color: {CELESTE}; }}
.mc-conc {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }}
.mc-conc .c {{ padding: 14px 16px; border-radius: 14px; background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.18); border-top: 3px solid rgba(116,172,223,.6); }}
.mc-conc .c b {{ display: block; font-size: 1rem; margin-bottom: 4px; }}
.mc-conc .c span {{ font-size: .95rem; line-height: 1.55; opacity: .92; }}

/* ── Ministros de Economía ── */
.mc-min-hero {{
    position: relative; overflow: hidden; border-radius: 22px; padding: 26px 28px 22px; margin: 6px 0 18px; color: #fff;
    background:
        radial-gradient(circle at 92% 8%, rgba(246,180,14,.45) 0, rgba(246,180,14,0) 30%),
        radial-gradient(circle at 0% 100%, rgba(116,172,223,.55) 0, rgba(116,172,223,0) 45%),
        linear-gradient(135deg, #0E2440 0%, #17406B 55%, #1F5A93 100%);
    box-shadow: 0 14px 34px rgba(14,36,64,.35);
}}
.mc-min-hero::after {{
    content: "$"; position: absolute; right: 22px; bottom: -48px; font-size: 13rem; font-weight: 900; line-height: 1;
    color: rgba(255,255,255,.06); pointer-events: none;
}}
.mc-min-hero .eyebrow {{ font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: {SOL}; }}
.mc-min-hero h3 {{ margin: 4px 0 6px; padding: 0; font-size: 2rem; font-weight: 900; letter-spacing: -.03em; color: #fff; }}
.mc-min-hero p {{ margin: 0; max-width: 720px; font-size: .94rem; line-height: 1.5; color: rgba(255,255,255,.85); }}
.mc-min-res {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 18px; position: relative; z-index: 1; }}
.mc-min-res > div {{
    padding: 12px 14px; border-radius: 14px; background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.16);
    backdrop-filter: blur(4px);
}}
.mc-min-res .k {{ font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.7); }}
.mc-min-res .v {{ font-size: 1.3rem; font-weight: 900; margin-top: 2px; color: #fff; }}
.mc-min-res .d {{ font-size: .78rem; color: rgba(255,255,255,.7); }}
/* con poco ancho disponible (barra lateral abierta en una ventana mediana), los cuatro datos van de a dos */
.mc-min-hero {{ container-type: inline-size; }}
@container (max-width: 720px) {{ .mc-min-res {{ grid-template-columns: repeat(2, 1fr); }} }}

.mc-min-grupo {{ display: flex; align-items: center; gap: 14px; margin: 30px 0 12px; }}
.mc-min-grupo .pf {{
    flex: 0 0 52px; height: 52px; border-radius: 50%; overflow: hidden; position: relative;
    background: linear-gradient(135deg, {CELESTE}, #4A8FD4); border: 3px solid #fff; box-shadow: 0 0 0 2px {CELESTE};
    display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800;
}}
.mc-min-grupo .pf img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top center; }}
.mc-min-grupo .t {{ flex: 1; }}
.mc-min-grupo .t small {{ display: block; font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: {CELESTE}; }}
.mc-min-grupo .t b {{ font-size: 1.25rem; font-weight: 900; letter-spacing: -.02em; }}
.mc-min-grupo .t span {{ font-size: .82rem; opacity: .85; margin-left: 6px; }}
.mc-min-grupo .n {{
    font-size: .78rem; font-weight: 800; padding: 4px 12px; border-radius: 999px; white-space: nowrap;
    color: {CELESTE}; background: rgba(116,172,223,.14); border: 1px solid rgba(116,172,223,.35);
}}
.mc-min-linea {{ height: 4px; border-radius: 4px; margin: -4px 0 14px;
    background: linear-gradient(90deg, {CELESTE} 0%, rgba(116,172,223,.15) 70%, rgba(116,172,223,0) 100%); }}
.mc-min-nota {{
    font-size: .8rem; line-height: 1.45; margin: 0 0 14px; padding: 10px 14px; border-radius: 12px;
    background: rgba(246,180,14,.08); border-left: 3px solid {SOL};
}}
.mc-min {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
.mc-min-card {{
    position: relative; overflow: hidden; display: flex; flex-direction: column; border-radius: 20px;
    background: rgba(128,128,128,.07); border: 1px solid rgba(116,172,223,.3); box-shadow: 0 6px 18px rgba(0,0,0,.08);
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}}
.mc-min-card:hover {{ transform: translateY(-4px); border-color: {CELESTE}; box-shadow: 0 14px 30px rgba(74,143,212,.22); }}
.mc-min-card .top {{
    display: flex; gap: 14px; align-items: center; padding: 16px 16px 14px;
    background: linear-gradient(135deg, rgba(116,172,223,.30) 0%, rgba(74,143,212,.10) 60%, rgba(116,172,223,0) 100%);
    border-bottom: 1px solid rgba(116,172,223,.22);
}}
.mc-min-card .ph {{
    flex: 0 0 76px; height: 76px; border-radius: 50%; overflow: hidden; position: relative;
    display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 1.4rem;
    background: linear-gradient(135deg, {CELESTE}, #4A8FD4); border: 3px solid #fff;
    box-shadow: 0 0 0 2px {CELESTE}, 0 6px 14px rgba(0,0,0,.25);
}}
.mc-min-card .ph img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top center; }}
.mc-min-card .per {{ font-size: .78rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: {CELESTE}; }}
.mc-min-card h5 {{ margin: 1px 0 1px; padding: 0; font-size: 1.18rem; font-weight: 900; letter-spacing: -.02em; line-height: 1.2; }}
.mc-min-card .cargo {{ font-size: .78rem; opacity: .85; line-height: 1.3; }}
.mc-min-card .cuerpo {{ padding: 12px 16px 14px; display: flex; flex-direction: column; gap: 10px; flex: 1; }}
.mc-min-card .dur {{ display: flex; align-items: center; gap: 10px; font-size: .78rem; font-weight: 800; white-space: nowrap; }}
.mc-min-card .dur .b {{ flex: 1; height: 6px; border-radius: 6px; background: rgba(128,128,128,.18); overflow: hidden; }}
.mc-min-card .dur .b i {{ display: block; height: 100%; border-radius: 6px; background: linear-gradient(90deg, {CELESTE}, #4A8FD4); }}
.mc-min-card .perfil {{ font-size: .8rem; opacity: .85; font-style: italic; line-height: 1.4; }}
.mc-min-card ul {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 7px; }}
.mc-min-card li {{ position: relative; padding-left: 18px; font-size: .86rem; line-height: 1.42; }}
.mc-min-card li::before {{
    content: ""; position: absolute; left: 2px; top: .5em; width: 8px; height: 8px; border-radius: 50%;
    background: {CELESTE}; box-shadow: 0 0 0 3px rgba(116,172,223,.22);
}}
.mc-min-card li.mas {{ padding-left: 0; }}
.mc-min-card li.mas::before {{ display: none; }}
.mc-min-card li.mas summary {{
    cursor: pointer; list-style: none; display: inline-flex; align-items: center; gap: 6px; font-size: .78rem; font-weight: 800;
    color: {CELESTE}; padding: 3px 10px; border-radius: 999px; background: rgba(116,172,223,.12);
    border: 1px solid rgba(116,172,223,.3); transition: background-color .15s ease;
}}
.mc-min-card li.mas summary::-webkit-details-marker {{ display: none; }}
.mc-min-card li.mas summary::after {{ content: "▾"; font-size: .78rem; transition: transform .15s ease; }}
.mc-min-card li.mas details[open] summary::after {{ transform: rotate(180deg); }}
.mc-min-card li.mas summary:hover {{ background: rgba(116,172,223,.22); }}
.mc-min-card li.mas ul {{ margin-top: 8px; }}
.mc-min-card .datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(92px, 1fr)); gap: 8px; margin-top: auto; padding-top: 4px; }}
.mc-min-card .dato {{ padding: 9px 10px; border-radius: 12px; background: rgba(116,172,223,.09); border: 1px solid rgba(116,172,223,.2); }}
.mc-min-card .dato .k {{ font-size: .78rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; opacity: .85; }}
.mc-min-card .dato .v {{ font-size: .95rem; font-weight: 900; margin-top: 2px; line-height: 1.2; }}
.mc-min-card .dato .s {{ font-size: .78rem; opacity: .85; margin-top: 1px; }}
.mc-min-card .dato .mejor {{ color: #10AC84; opacity: 1; font-weight: 800; }}
.mc-min-card .dato .peor {{ color: #EE5253; opacity: 1; font-weight: 800; }}
.mc-min-card .pico {{ font-size: .78rem; opacity: .8; }}
.mc-min-card.actual {{ border-color: {SOL}; box-shadow: 0 0 0 1px {SOL}, 0 10px 26px rgba(246,180,14,.25); }}
.mc-min-card.actual .top {{ background: linear-gradient(135deg, rgba(246,180,14,.32) 0%, rgba(247,159,31,.10) 60%, rgba(246,180,14,0) 100%); }}
.mc-min-card.actual .ph {{ box-shadow: 0 0 0 2px {SOL}, 0 0 18px rgba(246,180,14,.55); background: linear-gradient(135deg, {SOL}, #F79F1F); }}
.mc-min-card.actual .dur .b i {{ background: linear-gradient(90deg, {SOL}, #F79F1F); }}
.mc-min-card .vivo {{
    position: absolute; top: 12px; right: 12px; font-size: .78rem; font-weight: 900; letter-spacing: .12em;
    padding: 3px 9px; border-radius: 999px; color: #3A2A00; background: linear-gradient(135deg, {SOL}, #F79F1F);
}}
@container principal (max-width: 760px) {{
    .mc-min-hero {{ padding: 20px 18px 18px; }}
    .mc-min-hero h3 {{ font-size: 1.55rem; }}
    .mc-min-res {{ grid-template-columns: repeat(2, 1fr); }}
    .mc-min {{ grid-template-columns: 1fr; }}
    .mc-min-card .ph {{ flex-basis: 64px; height: 64px; }}
}}
@media (prefers-reduced-motion: reduce) {{ .mc-min-card, :is(.st-key-hist_seccion, .st-key-inv_seccion) button {{ transition: none; }} }}
/* una sola columna según el ancho real disponible (con la barra lateral abierta, una ventana mediana ya no alcanza
   para alternar tarjetas a los dos lados) */
.mc-tlwrap {{ container-type: inline-size; }}
@container (max-width: 760px) {{
    .mc-tl::before {{ left: 48px; }}
    .mc-tl-item {{ grid-template-columns: 96px 1fr; }}
    .mc-tl-dot {{ grid-column: 1; justify-self: start; }}
    .mc-tl-item.izq .mc-tl-card, .mc-tl-item.der .mc-tl-card {{ grid-column: 2; }}
    .mc-tl-anio {{ display: none; }}
    .mc-tl .mc-foto {{ width: 76px; height: 76px; margin-left: 10px; }}
    .mc-tl-hoy {{ margin-left: 10px; }}
}}
@media (max-width: 860px) {{ .mc-foto {{ width: 76px; height: 76px; margin-left: 10px; }} }}

/* ── Pie de página: franja celeste de la paleta ── */
.mc-foot {{
    margin: 40px 0 0; padding: 16px 22px 12px; border-radius: 14px 14px 0 0; color: inherit; font-size: .82rem;
    background: rgba(116,172,223,.10); border: 1px solid rgba(116,172,223,.22); border-top: 3px solid {CELESTE};
}}
.mc-foot .tit {{ margin: 0 0 4px; font-size: .78rem; font-weight: 800; letter-spacing: .14em;
    text-transform: uppercase; color: {CELESTE}; }}
.mc-foot a {{ color: {CELESTE}; font-weight: 600; text-decoration: none; }}
.mc-foot a:hover {{ text-decoration: underline; }}
.mc-foot p {{ margin: 0; line-height: 1.5; }}
/* el pie cierra la página: sin el relleno que Streamlit deja al final. El margen lateral va en una variable (--mc-pad)
   para que el pie pueda salir de él y ocupar todo el ancho */
:root {{ --mc-pad: 5rem; }}
[data-testid="stMainBlockContainer"] {{ padding-bottom: 0 !important; padding-left: var(--mc-pad) !important;
    padding-right: var(--mc-pad) !important; }}
.st-key-pie_datos {{ margin-left: calc(-1 * var(--mc-pad)) !important; margin-right: calc(-1 * var(--mc-pad)) !important;
    width: calc(100% + 2 * var(--mc-pad)) !important; max-width: none !important; border-radius: 0 !important;
    padding-left: var(--mc-pad) !important; padding-right: max(var(--mc-pad), 130px) !important; }}
/* (a la derecha queda libre la esquina donde Streamlit Cloud pone sus insignias flotantes: avatar y corona) */
/* suscripción: una franja finita */
.mc-foot .bol {{ display: flex; align-items: center; justify-content: space-between; gap: 12px 18px; flex-wrap: wrap;
    margin: 0 0 14px; padding: 9px 14px; border-radius: 10px; border: 1px solid rgba(116,172,223,.30);
    background: rgba(116,172,223,.10); }}
.mc-foot .bol > div {{ flex: 1 1 300px; min-width: 0; }}
.mc-foot .bol b {{ color: {CELESTE}; font-size: .86rem; margin-right: 8px; }}
.mc-foot .bol span {{ opacity: .85; }}
.mc-foot .bol a {{ flex: 0 0 auto; padding: 5px 14px; border-radius: 999px; background: {CELESTE}; color: #0E1A2B;
    font-size: .8rem; font-weight: 700; transition: transform .15s ease; }}
.mc-foot .bol a:hover {{ transform: translateY(-1px); text-decoration: none; }}
/* barra del pie: una sola franja fina, siempre pegada al borde inferior de la ventana (en la pestaña o pantalla que sea).
   «sticky» y no «fixed»: el contenedor principal tiene contención de layout y un elemento fijo se ubicaría respecto de él.
   Al final de una página corta queda en su lugar natural, apoyada abajo de todo */
[data-testid="stLayoutWrapper"]:has(> .st-key-pie_datos) {{ display: contents; }}
.st-key-pie_datos {{ position: sticky; bottom: 0; z-index: 90; margin-top: 28px; min-height: 60px; box-sizing: border-box;
    padding-top: 9px; padding-bottom: calc(15px + env(safe-area-inset-bottom, 0px)); justify-content: space-between; flex-wrap: nowrap; gap: 6px 16px !important;
    background: color-mix(in srgb, var(--background-color, #0E1117) 86%, #74ACDF 14%); border: none;
    border-top: 3px solid {CELESTE}; backdrop-filter: blur(6px); }}
.st-key-pie_datos [data-testid="stElementContainer"] {{ width: auto !important; }}
/* los enlaces y botones nunca se achican (antes se aplastaban y se pisaban); lo único que cede es el estado en vivo */
.st-key-pie_datos > * {{ flex: 0 0 auto; }}
/* Streamlit les pone a los textos un margen inferior negativo (-1rem): en la barra corría todo hacia abajo */
.st-key-pie_datos [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
.st-key-pie_datos [data-testid="stMarkdown"], .st-key-pie_datos [data-testid="stMarkdown"] > div {{ height: auto !important; }}
/* overflow-clip-margin: el halo animado del punto «En vivo» sobresale ~8 px y antes quedaba cortado */
.st-key-pie_datos > :first-child {{ flex: 1 1 auto; min-width: 0; overflow-x: clip; overflow-y: visible;
    overflow-clip-margin: 12px; }}
.st-key-pie_datos .mc-vivo {{ padding-left: 4px; justify-content: flex-end; }}
/* botones a la izquierda y el estado en vivo a la derecha: la esquina inferior derecha la tapa el botón «Manage app»
   que Streamlit Cloud le muestra al dueño de la app (no se puede mover desde acá) */
.st-key-pie_datos {{ justify-content: flex-start !important; }}
.st-key-pie_datos > :first-child {{ order: 9; }}
.st-key-pie_datos > :nth-child(2) {{ order: 1; }}
.st-key-pie_datos > :nth-child(3) {{ order: 2; }}
.st-key-pie_datos > :nth-child(4) {{ order: 3; }}
.mc-pielinks {{ display: flex; flex-wrap: wrap; align-items: center; gap: 2px 14px; font-size: .78rem; white-space: nowrap; }}
.mc-pielinks a {{ color: {CELESTE}; font-weight: 600; text-decoration: none; }}
.mc-pielinks a:hover {{ text-decoration: underline; }}
.mc-pielinks a.bol {{ padding: 5px 14px; border-radius: 999px; background: {CELESTE}; color: #0E1A2B; font-weight: 800;
    box-shadow: 0 0 0 0 rgba(116,172,223,.6); animation: mc-resalta 2.6s ease-out infinite; transition: transform .15s ease; }}
.mc-pielinks a.bol:hover {{ text-decoration: none; transform: translateY(-1px); filter: brightness(1.08); }}
@keyframes mc-resalta {{ 0% {{ box-shadow: 0 0 0 0 rgba(116,172,223,.55); }} 70%, 100% {{ box-shadow: 0 0 0 9px rgba(116,172,223,0); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-pielinks a.bol {{ animation: none; }} }}
.mc-pielinks .c {{ opacity: .85; }}
.st-key-pie_datos [data-testid="stPopover"] button {{ white-space: nowrap; }}
.mc-vivo, .mc-vivo span {{ white-space: nowrap; }}
/* lo que entra depende del ancho real de la barra (con la barra lateral abierta es bastante menos que la ventana):
   se va ocultando lo secundario, nunca los botones. Términos y privacidad siguen en «Fuentes y aviso» */
.st-key-pie_datos {{ container-type: inline-size; container-name: pie; }}
@container pie (max-width: 1250px) {{ .mc-pielinks .c, .mc-vivo .sec {{ display: none; }} }}
@container pie (max-width: 940px) {{ .mc-pielinks a:not(.bol) {{ display: none; }} }}
@container pie (max-width: 760px) {{ .mc-vivo span:not(.en) {{ display: none; }} }}
/* angosto (celular): la suscripción sigue a la vista con un texto corto, y los otros dos botones quedan solo con su
   ícono (el texto sigue ahí para los lectores de pantalla) */
.mc-pielinks .bol .s {{ display: none; }}
@container pie (max-width: 600px) {{
    .mc-pielinks .bol .l {{ display: none; }}
    .mc-pielinks .bol .s {{ display: inline; }}
    .st-key-pie_datos button [data-testid="stMarkdownContainer"] {{ position: absolute; width: 1px; height: 1px;
        overflow: hidden; clip-path: inset(50%); white-space: nowrap; }}
    .st-key-pie_datos button {{ padding: .4rem .55rem !important; gap: 0 !important; }}
    .st-key-pie_datos [data-testid="stPopover"] button div[aria-hidden="true"] {{ display: none; }}
    .st-key-pie_datos button [data-testid="stIconMaterial"] {{ font-size: 1.15rem; }}
}}
@container pie (max-width: 430px) {{ .st-key-pie_datos .mc-vivo .en {{ font-size: 0; gap: 0; }} }}
@media (max-width: 560px) {{ .st-key-pie_datos {{ padding-left: 14px !important; padding-right: 112px !important; gap: 8px !important; }}
    .st-key-pie_datos > :first-child {{ display: none; }} }}
/* el panel «Fuentes y aviso»: el contenido del pie, sin marco propio */
[data-testid="stPopoverBody"] .mc-foot {{ margin: 0; padding: 4px 4px 8px; border: none; border-radius: 0; background: none;
    width: min(620px, 80vw); }}
@media (max-width: 560px) {{
    [data-testid="stPopoverBody"] .mc-foot {{ width: auto; }}
    [data-testid="stPopoverBody"] .mc-foot .main {{ grid-template-columns: 1fr; gap: 14px; }}
    [data-testid="stPopoverBody"] .mc-foot .marca p {{ max-width: none; }}
}}
.mc-vivo {{ display: flex; flex-wrap: nowrap; align-items: center; gap: 4px 14px; font-size: .78rem; opacity: .85; }}
.mc-vivo .en {{ display: inline-flex; align-items: center; gap: 6px; font-weight: 800; letter-spacing: .08em;
    text-transform: uppercase; font-size: .78rem; color: #10AC84; }}
.mc-vivo .en::before {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background: #10AC84;
    box-shadow: 0 0 0 0 rgba(16,172,132,.6); animation: mc-latido 2s ease-out infinite; }}
@keyframes mc-latido {{ 0% {{ box-shadow: 0 0 0 0 rgba(16,172,132,.55); }} 100% {{ box-shadow: 0 0 0 8px rgba(16,172,132,0); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-vivo .en::before {{ animation: none; }} }}
.st-key-pie_datos button {{ min-height: 0 !important; padding: .28rem .8rem .28rem .65rem !important; border-radius: 999px !important;
    border: 1px solid rgba(116,172,223,.45) !important; background: transparent !important; }}
.st-key-pie_datos button p {{ font-size: .78rem !important; font-weight: 700; color: {CELESTE} !important; }}
.st-key-pie_datos button [data-testid="stIconMaterial"] {{ color: {CELESTE}; font-size: 1rem; }}
.st-key-pie_datos button:hover:not(:disabled) {{ background: rgba(116,172,223,.16) !important; border-color: {CELESTE} !important; }}
/* cuerpo: marca a la izquierda, fuentes a la derecha */
.mc-foot .main {{ display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 18px 36px; align-items: start; }}
.mc-foot .logo {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
.mc-foot .logo b {{ display: block; font-size: .95rem; }}
.mc-foot .logo span {{ display: block; font-size: .78rem; opacity: .85; }}
.mc-foot a.mc-linkedin {{ display: inline-flex; align-items: center; gap: 5px; margin-left: auto; padding: 3px 10px;
    border-radius: 999px; border: 1px solid rgba(116,172,223,.45); font-size: .78rem; }}
.mc-foot a.mc-linkedin:hover {{ background: #0A66C2; border-color: #0A66C2; color: #fff; text-decoration: none; }}
.mc-foot .marca p {{ opacity: .85; max-width: 46ch; }}
.mc-foot .fuentes ul {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 2px 14px; }}
.mc-foot .fuentes li {{ white-space: nowrap; }}
/* aviso largo: plegado, para no ocupar lugar (el texto completo sigue ahí) */
.mc-foot details {{ margin-top: 10px; font-size: .78rem; }}
.mc-foot summary {{ cursor: pointer; opacity: .85; width: fit-content; }}
.mc-foot summary:hover {{ opacity: 1; color: {CELESTE}; }}
.mc-foot details p {{ margin-top: 6px; opacity: .85; }}
/* barra legal */
.mc-foot .legal {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 4px 16px;
    margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(128,128,128,.28); font-size: .78rem; opacity: .9; }}
.mc-foot .frec {{ margin-top: 6px; font-size: .78rem; opacity: .85; }}
.mc-foot .made {{ font-weight: 800; letter-spacing: .12em; text-transform: uppercase; opacity: .85; font-size: .78rem; }}

/* ── Resultado final: fichas ── */
.mc-rf {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 6px 0 4px; }}
.mc-rf .f {{
    border: 1px solid rgba(116,172,223,.3); border-left: 5px solid {CELESTE}; border-radius: 14px;
    padding: 16px 18px; background: linear-gradient(180deg, rgba(116,172,223,.10), rgba(116,172,223,.03));
    box-shadow: 0 2px 10px rgba(0,0,0,.08);
}}
.mc-rf .f.ok {{ border-left-color: #10AC84; }} .mc-rf .f.mal {{ border-left-color: #EE5253; }}
.mc-rf .k {{ font-size: .82rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
.mc-rf .v {{ font-size: 1.75rem; font-weight: 800; margin: 4px 0; letter-spacing: -.01em; }}
.mc-rf .d {{ font-size: .92rem; opacity: .9; line-height: 1.4; }}
html[data-tema="claro"] .mc-rf .f {{ background: #F4F8FD; border-color: #CFE0F2; box-shadow: 0 2px 10px rgba(30,60,100,.07); }}
html[data-tema="claro"] .mc-conc .c {{ background: #F4F8FD; border: 1px solid #DCE7F3; }}
@container principal (max-width: 760px) {{ .mc-foot .main {{ grid-template-columns: 1fr; }} }}

/* ── Páginas legales ── */
.mc-legal {{ max-width: 860px; margin: 8px auto 0; }}
.mc-legal h1 {{ margin: 0; padding: 0; font-size: 2rem; font-weight: 800; letter-spacing: -.5px; }}
.mc-legal .act {{ opacity: .85; font-size: .88rem; margin: 4px 0 18px; }}
.mc-legal h3 {{ margin: 26px 0 10px; padding: 0; font-size: 1.1rem; font-weight: 800; color: {CELESTE}; }}
.mc-legal .card {{ padding: 18px 22px; border-radius: 14px; background: rgba(128,128,128,.09);
    border: 1px solid rgba(128,128,128,.16); }}
.mc-legal .card.intro {{ background: rgba(116,172,223,.10); border-color: rgba(116,172,223,.3); }}
.mc-legal .card p {{ margin: 0 0 10px; line-height: 1.7; font-size: .95rem; }}
.mc-legal .card p:last-child {{ margin-bottom: 0; }}

/* ── Tarjetas de cotización ── */
/* columnas según la cantidad de tarjetas (--cols, ver _columnas): filas parejas, sin tarjetas huérfanas */
.mc-fxgrid {{ display: grid; grid-template-columns: repeat(var(--cols, 4), minmax(0, 1fr)); gap: 12px; margin: 8px 0 8px; }}
/* según el ancho real disponible (barra lateral abierta o no): con menos lugar, 3 y después 2 por fila. Si la última
   fila queda incompleta, sus tarjetas se estiran para llenarla (nunca una tarjeta sola en un rincón). Con 3 por fila se
   usa una grilla de 6 sub-columnas: cada tarjeta ocupa 2; una sola al final ocupa las 6 y dos, 3 cada una */
.mc-fxwrap {{ container-type: inline-size; }}
@container (max-width: 860px) {{
    .mc-fxgrid {{ grid-template-columns: repeat(6, minmax(0, 1fr)); }}
    .mc-fxgrid > * {{ grid-column: span 2; }}
    .mc-fxgrid > :last-child:nth-child(3n+1) {{ grid-column: span 6; }}
    .mc-fxgrid > :nth-last-child(2):nth-child(3n+1), .mc-fxgrid > :last-child:nth-child(3n+2) {{ grid-column: span 3; }}
}}
@container (max-width: 500px) {{
    .mc-fxgrid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
    .mc-fxgrid > *, .mc-fxgrid > :is(:last-child, :nth-last-child(2)):nth-child(n) {{ grid-column: span 1; }}
    .mc-fxgrid > :last-child:nth-child(odd) {{ grid-column: span 2; }}
}}
.mc-fx {{
    padding: 14px 16px 12px; border-radius: 14px; background: rgba(128,128,128,.09); min-width: 0; overflow: hidden;
    border: 1px solid rgba(116,172,223,.32); border-top: 4px solid {CELESTE};
    transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}}
.mc-fx:hover {{ border-color: rgba(116,172,223,.6); transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.18); }}
.mc-fx .n {{ font-weight: 800; font-size: .98rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
/* descripción: siempre el alto de dos renglones, así los valores de todas las tarjetas quedan a la misma altura */
.mc-fx .d {{ font-size: .78rem; opacity: .85; line-height: 1.3; min-height: 2.6em; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
.mc-fx .v {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.5px; margin: 6px 0 0; white-space: nowrap; min-width: 0; }}
.mc-fx .c {{ font-size: .78rem; opacity: .85; margin-bottom: 8px; }}
.mc-fx .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.mc-fx .chip {{ font-size: .78rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: rgba(128,128,128,.16); }}
.mc-fx .chip.bien {{ color: #10AC84; background: rgba(16,172,132,.16); }}
.mc-fx .chip.mal {{ color: #EE5253; background: rgba(238,82,83,.16); }}
.mc-fx .chip.flat {{ opacity: .8; }}
.mc-fx .fila {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; min-width: 0; }}
/* el valor nunca se achica (si no, se monta sobre el mini-gráfico); el mini-gráfico se angosta y, en tarjetas
   angostas (5 columnas con la barra lateral abierta), se oculta y el valor se achica un poco */
.mc-fx {{ container-type: inline-size; }}
.mc-fx .v {{ flex: 0 0 auto; }}
.mc-fx .spark {{ flex: 0 1 76px; min-width: 0; width: 76px; opacity: .95; }}
@container (max-width: 205px) {{
    .mc-fx .spark {{ display: none; }}
    .mc-fx .v {{ font-size: 1.3rem; }}
}}
@container (max-width: 150px) {{ .mc-fx .v {{ font-size: 1.1rem; }} }}
@media (max-width: 640px) {{
    .mc-fx {{ padding: 11px 12px 10px; }}
    .mc-fx .v {{ font-size: 1.15rem; }}
    .mc-fx .spark {{ display: none; }}
    .mc-fx .c {{ font-size: .78rem; }}
}}

/* ── Franja superior deslizante (inspirada en los tableros de cotizaciones) ── */
.mc-ticker {{
    overflow: hidden; white-space: nowrap; border-radius: 12px; padding: 9px 0; margin: 0 0 6px;
    background: rgba(128,128,128,.07); border: 1px solid rgba(116,172,223,.28);
    -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 3%, #000 97%, transparent 100%);
            mask-image: linear-gradient(90deg, transparent 0, #000 3%, #000 97%, transparent 100%);
}}
.mc-ticker .pista {{ display: inline-flex; width: max-content; animation: mc-marquee 120s linear infinite;
    will-change: transform; }}
.mc-ticker {{ contain: layout paint; }}  /* su movimiento no obliga a redibujar el resto de la página */
.mc-ticker:hover .pista, .mc-ticker.quieta .pista {{ animation-play-state: paused; }}  /* quieta: fuera de la vista */
.mc-ticker .tk {{ display: inline-flex; align-items: baseline; gap: 8px; padding: 0 22px; border-right: 1px solid rgba(128,128,128,.22); }}
.mc-ticker .n {{ font-size: .78rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; opacity: .85; }}
.mc-ticker .v {{ font-weight: 800; font-size: .92rem; }}
.mc-ticker .d {{ font-size: .78rem; font-weight: 700; opacity: .85; }}
.mc-ticker .d.bien {{ color: #10AC84; opacity: 1; }}
.mc-ticker .d.mal {{ color: #EE5253; opacity: 1; }}
@keyframes mc-marquee {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-ticker .pista {{ animation: none; }} .mc-ticker {{ overflow-x: auto; }} }}

/* ── Interactivo: viaje en el tiempo y comparador ── */
.mc-viaje {{
    display: flex; align-items: center; gap: 20px; padding: 16px 20px; margin: 6px 0 14px; border-radius: 16px;
    background: rgba(128,128,128,.09); border: 1px solid rgba(116,172,223,.38);
}}
.mc-viaje h3 {{ margin: 2px 0; padding: 0; font-size: 1.5rem; font-weight: 800; }}
.mc-viaje .per {{ font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {CELESTE}; }}
.mc-viaje .hito {{ font-size: .9rem; opacity: .85; line-height: 1.4; }}
/* TABLAS (todas las de la página usan .mc-cmp): tarjeta con borde redondeado, cabecera con fondo, filas alternadas,
   letra grande y nada de texto gris */
.mc-tablas {{ overflow-x: auto; margin: 10px 0 14px; border-radius: 14px; }}
.mc-cmp {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 10px 0 14px; font-size: 1rem;
    border: 1px solid rgba(116,172,223,.35); border-radius: 14px; overflow: hidden; font-variant-numeric: tabular-nums; }}
.mc-tablas .mc-cmp {{ margin: 0; }}
.mc-cmp thead th {{ text-align: right; padding: 12px 16px; font-size: .8rem; font-weight: 800; letter-spacing: .06em;
    text-transform: uppercase; background: rgba(116,172,223,.16); border-bottom: 2px solid {CELESTE}; }}
.mc-cmp th:first-child, .mc-cmp td:first-child {{ text-align: left; }}
.mc-cmp td {{ text-align: right; padding: 12px 16px; border-bottom: 1px solid rgba(128,128,128,.18); font-weight: 600;
    line-height: 1.35; }}
.mc-cmp tbody tr:nth-child(even) td {{ background: rgba(128,128,128,.06); }}
.mc-cmp tbody tr:hover td {{ background: rgba(116,172,223,.12); }}
.mc-cmp tbody tr:last-child td {{ border-bottom: 0; }}
.mc-cmp td:first-child {{ font-weight: 600; }}
.mc-cmp td .sub {{ display: block; font-size: .82rem; font-weight: 500; opacity: .85; margin-top: 2px; }}
.mc-cmp .mejor {{ color: #0E9F77; font-weight: 800; }}
.mc-cmp .peor {{ color: #E0393E; font-weight: 800; }}
@container principal (max-width: 560px) {{  /* con poco ancho, celdas más ajustadas para que la tabla entre */
    .mc-cmp {{ font-size: .9rem; }}
    .mc-cmp thead th {{ padding: 9px 8px; font-size: .74rem; letter-spacing: .02em; }}
    .mc-cmp td {{ padding: 10px 8px; }}
    .mc-cmp td:not(:first-child) {{ white-space: nowrap; }}  /* «+18,4 pp» en un solo renglón */
    .mc-cmp td:first-child {{ hyphens: auto; }}
}}
/* TEXTOS SECUNDARIOS: los de Streamlit (aclaraciones, etiquetas de campos) eran grises y chicos; van con el color del
   texto y más grandes */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ font-size: .95rem !important;
    color: inherit !important; opacity: .88; line-height: 1.5; }}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ font-size: 1rem !important; font-weight: 600 !important;
    color: inherit !important; opacity: 1 !important; }}
[data-testid="stMetricLabel"] p {{ font-size: .95rem !important; color: inherit !important; opacity: .9; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ font-size: 1.02rem; }}
/* TEMA CLARO (lo marca JS_PESTANAS en html[data-tema="claro"]): el celeste de los acentos se lee mal sobre blanco */
html[data-tema="claro"] .mc-cmp thead th {{ background: #E3EEF9; border-bottom-color: #2E6DB4; color: #12324F; }}
html[data-tema="claro"] .mc-cmp {{ border-color: #C9DBEE; }}
html[data-tema="claro"] .mc-cmp tbody tr:nth-child(even) td {{ background: #F5F8FC; }}
html[data-tema="claro"] .mc-cmp .mejor {{ color: #08805F; }}
html[data-tema="claro"] .mc-cmp .peor {{ color: #C62828; }}
html[data-tema="claro"] [data-testid="stCaptionContainer"] {{ opacity: 1; color: #374151 !important; }}
html[data-tema="claro"] :is(.mc-tl-card, .mc-min-card, .mc-viaje, .mc-nota, .mc-min-grupo, .mc-fx) :is(.per, .t, small) {{
    color: #1F5F99 !important; }}

[data-testid="stMetric"] {{ border-radius: 14px; transition: border-color .18s ease; }}
[data-testid="stMetric"]:hover {{ border-color: rgba(116,172,223,.55); }}
/* números de los indicadores: más peso y espaciado ajustado, como en los tableros financieros */
[data-testid="stMetricValue"] {{ font-weight: 650 !important; letter-spacing: -.02em; }}
/* un solo tamaño de cifra para todos los indicadores (antes, según la pestaña, 36, 23 o 19 px) */
[data-testid="stMetricValue"] > div {{ font-size: 1.5rem !important; line-height: 1.2; }}
/* indicadores angostos (tres o más por fila con poco ancho): el valor se achica en vez de cortarse con «…» y la
   etiqueta puede ocupar dos renglones */
[data-testid="stMetric"] {{ container-type: inline-size; }}
[data-testid="stMetricLabel"] p {{ white-space: normal !important; overflow: visible !important; line-height: 1.25; }}
@container (max-width: 190px) {{ [data-testid="stMetricValue"] > div {{ font-size: 1.25rem !important; }} }}
@container (max-width: 150px) {{ [data-testid="stMetricValue"] > div {{ font-size: 1.05rem !important; }} }}
/* tarjetas de una misma fila, del mismo alto (con o sin variación debajo) */
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:only-child > [data-testid="stMetric"])
    > [data-testid="stVerticalBlock"],
[data-testid="stElementContainer"]:only-child:has(> [data-testid="stMetric"]),
[data-testid="stElementContainer"]:only-child > [data-testid="stMetric"] {{ height: 100%; }}
/* menos aire muerto arriba: el contenido arranca justo debajo de la barra superior */
[data-testid="stMainBlockContainer"] {{ padding-top: 3.6rem; }}
/* al abrir una pestaña o tocar un control, Streamlit atenúa toda la página (opacidad .33) mientras recalcula: se veía
   como un parpadeo. El contenido queda como está hasta que llega el nuevo */
[data-stale="true"] {{ opacity: 1 !important; transition: none !important; }}
/* pestaña recién abierta, todavía sin contenido: un círculo de carga en lugar de un hueco en blanco */
[role="tabpanel"]:not(:has([data-testid="stElementContainer"]))::before {{
    content: ""; display: block; width: 34px; height: 34px; margin: 72px auto; border-radius: 50%;
    border: 3px solid rgba(116,172,223,.22); border-top-color: {CELESTE}; animation: mc-gira .8s linear infinite; }}
@keyframes mc-gira {{ to {{ transform: rotate(360deg); }} }}
/* sin el ícono de enlace que Streamlit agrega al pasar por los títulos */
[data-testid="stHeaderActionElements"] {{ display: none !important; }}
/* títulos de sección con un poco más de aire arriba */
[data-testid="stHeading"] h3 {{ padding-top: .9rem; }}
/* sin barra deslizante: la fila se mueve sola al tocar un marcador (ver JS_PESTANAS), con las flechas o deslizando */
[role="tablist"] {{ gap: 6px; padding-bottom: 4px; scrollbar-width: none !important; }}
[role="tablist"]::-webkit-scrollbar {{ display: none !important; }}
/* el bloque que solo trae el script no ocupa lugar (ni el espacio entre elementos) */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > script:only-child) {{ display: none; }}
/* flechas de desplazamiento: botón redondo celeste sobre el degradé que ya pone Streamlit */
[data-testid="stTabsScrollLeft"], [data-testid="stTabsScrollRight"] {{
    width: 52px !important; height: 3.4rem !important; display: flex; align-items: center; cursor: pointer;
}}
[data-testid="stTabsScrollLeft"] {{ justify-content: flex-start; }}
[data-testid="stTabsScrollRight"] {{ justify-content: flex-end; }}
[data-testid="stTabsScrollLeft"] svg, [data-testid="stTabsScrollRight"] svg {{
    width: 32px !important; height: 32px !important; padding: 5px; box-sizing: border-box; border-radius: 50%;
    color: {CELESTE}; background: rgba(116,172,223,.16); border: 1px solid rgba(116,172,223,.55);
    box-shadow: 0 2px 10px rgba(0,0,0,.18);
    transition: transform .18s ease, background-color .18s ease, color .18s ease, box-shadow .18s ease;
}}
[data-testid="stTabsScrollLeft"]:hover svg, [data-testid="stTabsScrollRight"]:hover svg {{
    background: {CELESTE}; color: #0E1420; transform: scale(1.1); box-shadow: 0 0 0 4px rgba(116,172,223,.22);
}}
[data-testid="stTabsScrollLeft"]:active svg, [data-testid="stTabsScrollRight"]:active svg {{ transform: scale(.94); }}
[data-testid="stTabsScrollLeft"]:focus-visible svg, [data-testid="stTabsScrollRight"]:focus-visible svg {{
    outline: 2px solid {CELESTE}; outline-offset: 2px;
}}
[data-testid="stTab"] {{ height: 3.4rem; padding: 0 1.15rem; }}
[data-testid="stTab"] p {{ font-size: 1.15rem; font-weight: 600; }}
/* animación sutil al pasar el cursor por un marcador */
[data-testid="stTab"] {{
    border-radius: 10px 10px 0 0;
    transition: transform .18s ease, background-color .18s ease, box-shadow .18s ease, filter .18s ease;
}}
[data-testid="stTab"] p {{ transition: color .18s ease, letter-spacing .18s ease; }}
[data-testid="stTab"]:hover {{
    transform: translateY(-2px);
    background-color: rgba(116,172,223,.14);
    box-shadow: inset 0 -2px 0 rgba(116,172,223,.8);
}}
[data-testid="stTab"]:hover p {{ color: {CELESTE} !important; }}
[data-testid="stTab"]:active {{ transform: translateY(0); }}
@media (prefers-reduced-motion: reduce) {{
    [data-testid="stTab"], [data-testid="stTab"] p {{ transition: none; }}
    [data-testid="stTab"]:hover {{ transform: none; }}
}}
/* "Inicio" (primer marcador): la casa de la app. Píldora celeste con el Sol de Mayo, como la bandera; se rellena
   cuando está elegida y queda separada del resto por una línea vertical */
[role="tablist"] [data-testid="stTab"]:first-of-type {{
    position: relative; height: 2.6rem; margin: .4rem 1.25rem .4rem .1rem; padding: 0 1.15rem 0 2.45rem;
    border-radius: 999px; border: 1px solid rgba(116,172,223,.55);
    background: linear-gradient(135deg, rgba(116,172,223,.20), rgba(116,172,223,.07));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
}}
[role="tablist"] [data-testid="stTab"]:first-of-type p {{ color: {CELESTE} !important; }}
[role="tablist"] [data-testid="stTab"]:first-of-type:hover {{
    transform: translateY(-1px); border-color: {CELESTE};
    background: linear-gradient(135deg, rgba(116,172,223,.32), rgba(116,172,223,.12));
    box-shadow: 0 4px 14px rgba(116,172,223,.25);
}}
[role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"] {{
    border-color: transparent; background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%);
    box-shadow: 0 4px 16px rgba(74,143,212,.45), inset 0 1px 0 rgba(255,255,255,.35);
}}
[role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"] p {{ color: #0B1A2E !important; }}
/* la píldora ya marca la selección: sin la rayita de abajo */
[role="tablist"] [data-testid="stTab"]:first-of-type .react-aria-SelectionIndicator {{ display: none; }}
/* la rayita no viaja desde la pestaña anterior (saliendo de «Inicio» cruzaba toda la fila como una línea saltando):
   aparece en su lugar, creciendo desde el centro */
[role="tablist"] .react-aria-SelectionIndicator {{
    transition: background-color .2s ease !important; animation: mc-raya .25s ease-out;
}}
@keyframes mc-raya {{ from {{ transform: scaleX(0); opacity: 0; }} to {{ transform: scaleX(1); opacity: 1; }} }}
@media (prefers-reduced-motion: reduce) {{ [role="tablist"] .react-aria-SelectionIndicator {{ animation: none; }} }}
[role="tablist"] [data-testid="stTab"]:first-of-type::before {{
    content: ""; position: absolute; left: .75rem; top: 50%; width: 1.3rem; height: 1.3rem; transform: translateY(-50%);
    background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><g stroke='%23F6B40E' stroke-width='1.6' stroke-linecap='round'><path d='M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1'/></g><circle cx='12' cy='12' r='5' fill='%23F6B40E'/></svg>") center / contain no-repeat;
    transition: transform .6s ease;
}}
[role="tablist"] [data-testid="stTab"]:first-of-type:hover::before {{ transform: translateY(-50%) rotate(90deg); }}
[role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"]::before {{
    filter: drop-shadow(0 0 4px rgba(246,180,14,.9));
}}
[role="tablist"] [data-testid="stTab"]:first-of-type p {{ font-weight: 800; letter-spacing: .02em; }}
[role="tablist"] [data-testid="stTab"]:first-of-type::after {{
    content: ""; position: absolute; right: -0.75rem; top: 15%; height: 70%; width: 1px;
    background: rgba(128,128,128,.45);
}}
/* pestaña recién tocada (se arma en el servidor): esqueleto de tarjetas y gráfico con un brillo que pasa, en lugar de
   un hueco vacío con el pie de página subiendo */
[data-testid="stTabPanel"] > [data-testid="stVerticalBlock"]:empty {{
    display: block; position: relative; overflow: hidden; min-height: 120vh; margin-top: 10px; border-radius: 14px;
    background-image: linear-gradient(rgba(116,172,223,.10), rgba(116,172,223,.10)),
        linear-gradient(rgba(116,172,223,.08), rgba(116,172,223,.08)),
        linear-gradient(rgba(116,172,223,.08), rgba(116,172,223,.08)),
        linear-gradient(rgba(116,172,223,.08), rgba(116,172,223,.08)),
        linear-gradient(rgba(116,172,223,.08), rgba(116,172,223,.08)),
        linear-gradient(rgba(116,172,223,.07), rgba(116,172,223,.07)),
        linear-gradient(rgba(116,172,223,.07), rgba(116,172,223,.07));
    background-repeat: no-repeat;
    background-size: 55% 14px, 23.5% 104px, 23.5% 104px, 23.5% 104px, 23.5% 104px, 30% 34px, 100% 380px;
    background-position: 0 6px, 0 40px, 33.33% 40px, 66.67% 40px, 100% 40px, 0 176px, 0 226px;
}}
[data-testid="stTabPanel"] > [data-testid="stVerticalBlock"]:empty::before {{
    content: ""; position: absolute; inset: 0; transform: translateX(-100%);
    background: linear-gradient(90deg, transparent 0, rgba(116,172,223,.13) 50%, transparent 100%);
    animation: mc-brillo 1.2s ease-in-out infinite;
}}
@keyframes mc-brillo {{ to {{ transform: translateX(100%); }} }}
@media (prefers-reduced-motion: reduce) {{
    [data-testid="stTabPanel"] > [data-testid="stVerticalBlock"]:empty::before {{ animation: none; }}
}}
@media (max-width: 640px) {{
    [data-testid="stTabPanel"] > [data-testid="stVerticalBlock"]:empty {{
        background-size: 70% 14px, 48.5% 96px, 48.5% 96px, 48.5% 96px, 48.5% 96px, 45% 30px, 100% 300px;
        background-position: 0 6px, 0 36px, 100% 36px, 0 144px, 100% 144px, 0 256px, 0 300px;
    }}
}}
/* barras de desplazamiento (barra lateral y página): finas, celestes y redondeadas, más visibles al pasar el mouse */
[data-testid="stSidebarContent"], [data-testid="stMain"] {{
    scrollbar-width: thin; scrollbar-color: rgba(116,172,223,.28) transparent;
}}
[data-testid="stSidebarContent"]:hover, [data-testid="stMain"]:hover {{ scrollbar-color: rgba(116,172,223,.55) transparent; }}
[data-testid="stSidebarContent"]::-webkit-scrollbar, [data-testid="stMain"]::-webkit-scrollbar {{ width: 8px; }}
[data-testid="stSidebarContent"]::-webkit-scrollbar-track, [data-testid="stMain"]::-webkit-scrollbar-track {{ background: transparent; }}
[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb, [data-testid="stMain"]::-webkit-scrollbar-thumb {{
    background: rgba(116,172,223,.28); border-radius: 999px; border: 2px solid transparent; background-clip: padding-box;
}}
[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb:hover, [data-testid="stMain"]::-webkit-scrollbar-thumb:hover {{
    background-color: rgba(116,172,223,.6);
}}
/* botón para plegar y desplegar la barra lateral: redondo y celeste, con una flecha simple como las de las pestañas */
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"] {{
    width: 32px !important; height: 32px !important; min-height: 0 !important; padding: 0 !important; border-radius: 50% !important;
    display: inline-flex !important; align-items: center; justify-content: center;
    background: rgba(116,172,223,.16) !important; border: 1px solid rgba(116,172,223,.55) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,.18); transition: background-color .18s ease, transform .18s ease, box-shadow .18s ease;
}}
[data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{
    font-size: 0 !important; width: 16px; height: 16px; display: block; background: {CELESTE};
    -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M15 5l-7 7 7 7' fill='none' stroke='black' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'/></svg>") center / contain no-repeat;
            mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M15 5l-7 7 7 7' fill='none' stroke='black' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'/></svg>") center / contain no-repeat;
}}
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{ transform: rotate(180deg); }}
[data-testid="stSidebarCollapseButton"] button:hover, [data-testid="stExpandSidebarButton"]:hover {{
    background: {CELESTE} !important; transform: scale(1.08); box-shadow: 0 0 0 4px rgba(116,172,223,.22);
}}
[data-testid="stSidebarCollapseButton"] button:hover [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"]:hover [data-testid="stIconMaterial"] {{ background: #0E1420; }}
h3 {{ font-weight: 700 !important; }}
/* la etiqueta de variación de los indicadores no se corta con «…»: si no entra, baja de renglón */
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] p {{
    white-space: normal !important; overflow: visible !important; text-overflow: clip !important; height: auto !important;
}}
[data-testid="stMetricDelta"] {{ max-width: 100%; line-height: 1.25; word-break: normal; overflow-wrap: normal; }}
/* Los cortes dependen del ancho REAL del contenido (no de la ventana): con la barra lateral abierta el contenido queda
   unos 460 px más angosto que la ventana. Con menos lugar, los indicadores pasan de cinco a tres por fila y después a dos,
   y los gráficos que van de a dos se apilan. */
[data-testid="stMainBlockContainer"] {{ container-type: inline-size; container-name: principal; }}
@container principal (max-width: 820px) {{
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]) {{
        flex-wrap: wrap !important; gap: .75rem !important;
    }}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]) > [data-testid="stColumn"] {{
        flex: 1 1 calc(33.3% - .75rem) !important; min-width: calc(33.3% - .75rem) !important; width: auto !important;
    }}
    /* justo cuatro: de a dos (2 + 2), no 3 + 1 con uno solo ocupando toda la fila */
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4):last-child [data-testid="stMetric"]) > [data-testid="stColumn"] {{
        flex: 1 1 calc(50% - .75rem) !important; min-width: calc(50% - .75rem) !important;
    }}
    /* dos gráficos lado a lado: con este ancho los títulos se cortaban; van uno debajo del otro */
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stPlotlyChart"]) {{
        flex-wrap: wrap !important;
    }}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stPlotlyChart"]) > [data-testid="stColumn"] {{
        flex: 1 1 100% !important; min-width: 100% !important; width: 100% !important;
    }}
}}
@container principal (max-width: 560px) {{
    [data-testid="stHorizontalBlock"]:is(:has([data-testid="stMetric"]), :has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"])) {{
        flex-wrap: wrap !important; gap: .6rem !important; }}
    [data-testid="stHorizontalBlock"]:is(:has([data-testid="stMetric"]), :has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]),
        :has(> [data-testid="stColumn"]:nth-child(4):last-child [data-testid="stMetric"])) > [data-testid="stColumn"] {{
        flex: 1 1 calc(50% - .6rem) !important; min-width: calc(50% - .6rem) !important; width: auto !important;
    }}
}}
/* encabezado de Inicio: el título y el botón «Personalizar» van en una fila; el botón nunca se aplasta */
[data-testid="stHorizontalBlock"]:is(:has(.st-key-personalizar), :has(.st-key-inicio_otro)) {{
    flex-wrap: nowrap !important; gap: .75rem !important; }}
[data-testid="stHorizontalBlock"]:is(:has(.st-key-personalizar), :has(.st-key-inicio_otro)) > [data-testid="stColumn"]:first-child {{
    flex: 1 1 0 !important; min-width: 0 !important; width: auto !important; }}
[data-testid="stHorizontalBlock"]:is(:has(.st-key-personalizar), :has(.st-key-inicio_otro)) > [data-testid="stColumn"]:last-child {{
    flex: 0 0 auto !important; width: auto !important; min-width: max-content !important; }}
.st-key-personalizar button, .st-key-personalizar p {{ white-space: nowrap !important; }}

/* ── Celular y pantallas angostas: más aire, indicadores de a dos y todo legible ── */
@media (max-width: 640px) {{
    :root {{ --mc-pad: .85rem; }}
    .block-container {{ padding: 3.2rem .85rem 0 !important; }}
    h1 {{ font-size: 1.6rem !important; }}
    h2, [data-testid="stHeading"] h2 {{ font-size: 1.3rem !important; }}
    h3 {{ font-size: 1.15rem !important; }}
    [data-testid="stMetric"] {{ padding: .7rem .8rem !important; }}
    [data-testid="stMetric"] > div {{ padding: 0 !important; }}  /* Streamlit le suma otro relleno adentro */
    [data-testid="stMetricValue"] > div {{ font-size: 1.35rem !important; }}
    [data-testid="stMetricLabel"] p {{ font-size: .8rem !important; }}
    [data-testid="stMetricDelta"] {{ font-size: .78rem !important; }}
    /* pestañas y botones más cómodos al tacto */
    [data-testid="stTab"] {{ height: 3rem; padding: 0 .85rem; }}
    [data-testid="stTab"] p {{ font-size: 1rem; }}
    button[data-variant="segmented_control"] {{ padding: .5rem .85rem; }}
    /* tablas anchas: se deslizan de costado en lugar de apretarse */
    [data-testid="stTable"], [data-testid="stDataFrame"] {{ overflow-x: auto; }}
    /* pie de página y fichas en una columna */
    .mc-foot {{ padding: 14px 14px 10px; margin-top: 28px; }}
    .mc-foot .legal {{ flex-direction: column; }}
    .mc-brand h1 {{ font-size: 1.3rem !important; }}
}}
</style>
"""


def _minificar_css(css: str) -> str:
    """Saca comentarios y espacios de sobra (el CSS viaja en cada carga): ~25% menos de bytes, mismas reglas.
    Las comillas («content: "$"», data URIs) se respetan."""
    partes = re.split(r'("[^"]*"|\'[^\']*\')', css)  # los textos entre comillas no se tocan
    for i in range(0, len(partes), 2):
        p = re.sub(r"/\*.*?\*/", "", partes[i], flags=re.S)
        p = re.sub(r"\s+", " ", p)
        partes[i] = re.sub(r"\s*([{};,>])\s*", r"\1", p)
    return "".join(partes).replace(";}", "}").strip()


CSS = _minificar_css(CSS)


# Al tocar una pestaña de un borde, la fila se desliza lo justo para mostrar la que sigue (o la anterior); las del
# medio no mueven nada. Se instala una sola vez por página y también sigue a las flechas del teclado.
JS_PESTANAS = """
<script>
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
  b.addEventListener('click', () => {
    const oculto = !raiz.dataset.pie;
    clearTimeout(reloj);
    guardar(oculto);
    const barra = document.querySelector('.st-key-pie_datos');
    if (oculto) {
      // cierre: la barra baja y recién después se saca
      if (!barra || quieto()) { delete raiz.dataset.pieAnim; poner(true); pintar(); return; }
      raiz.dataset.pieAnim = 'sale';
      raiz.dataset.pie = 'cerrando';
      pintar();
      reloj = setTimeout(() => { poner(true); delete raiz.dataset.pieAnim; pintar(); }, MS);
    } else {
      // apertura: la barra sube y la página baja lo mismo que mide, así no tapa lo que se estaba leyendo
      poner(false);
      if (!quieto()) raiz.dataset.pieAnim = 'entra';
      pintar();
      if (barra) {
        // (a mano y no con scrollBy «smooth»: ese no se mueve en todos los navegadores dentro de Streamlit)
        const caja = desplazable(barra);
        const desde = caja.scrollTop;
        const hasta = desde + barra.getBoundingClientRect().height;
        const t0 = performance.now();
        const paso = (t) => {
          const k = quieto() ? 1 : Math.min(1, (t - t0) / MS);
          caja.scrollTop = desde + (hasta - desde) * (1 - Math.pow(1 - k, 3));
          if (k < 1) requestAnimationFrame(paso);
        };
        requestAnimationFrame(paso);
        setTimeout(() => { if (caja.scrollTop < hasta - 1) caja.scrollTop = hasta; }, MS + 80);
      }
      reloj = setTimeout(() => { delete raiz.dataset.pieAnim; }, MS);
    }
  });
  pintar();
  document.body.appendChild(b);
})();
(() => {
  // Alertas por mail: al anotarse, el formulario se reemplaza por un aviso y no vuelve a aparecer en este navegador.
  // (el mail sigue yendo directo a Buttondown; acá solo se guarda que ya se anotó, nunca la dirección)
  if (window.__mcAlertas) return;
  window.__mcAlertas = true;
  const raiz = document.documentElement;
  try { if (localStorage.getItem('mc_alertas_anotado') === '1') raiz.dataset.alertas = 'anotado'; } catch (e) {}
  document.addEventListener('submit', (ev) => {
    const f = ev.target;
    if (!(f instanceof HTMLFormElement) || !f.classList.contains('mc-alerta')) return;
    try { localStorage.setItem('mc_alertas_anotado', '1'); } catch (e) {}
    setTimeout(() => {
      const ok = document.createElement('div');
      ok.className = 'mc-alerta-ok';
      ok.textContent = '✅ Listo. Revisá tu mail y confirmá la suscripción desde el enlace que te mandó Buttondown.';
      f.replaceWith(ok);
      raiz.dataset.alertas = 'anotado';  // si Streamlit vuelve a dibujar el formulario, queda oculto
    }, 0);
  }, true);
})();
(() => {
  // Tema claro u oscuro (Streamlit no lo marca): se mira el fondo de la página. Algunos colores cambian en el claro.
  if (window.__mcTema) return;
  window.__mcTema = true;
  const raiz = document.documentElement;
  const revisar = () => {
    const app = document.querySelector('.stApp') || document.body;
    const m = getComputedStyle(app).backgroundColor.match(/[0-9]+/g);
    if (!m) return;
    const claro = (0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2]) > 150;
    if (claro) raiz.dataset.tema = 'claro'; else delete raiz.dataset.tema;
  };
  revisar();
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
  if (window.__mcPestanasV3) return;
  window.__mcPestanasV3 = true;
  const MARGEN = 56;  // lo que tapa cada flechita (botón + degradé)
  // Destino de la fila para que se vean enteras la pestaña tocada y sus vecinas. Si ya se ven (las del medio),
  // devuelve null y la fila no se mueve.
  const destinoPara = (tab) => {
    const c = tab && tab.closest('[role="tablist"]');
    if (!c || c.scrollWidth <= c.clientWidth + 1) return null;
    const tabs = [...c.querySelectorAll('[role="tab"]')], i = tabs.indexOf(tab);
    const r = c.getBoundingClientRect();
    const izq = tabs[Math.max(0, i - 1)].getBoundingClientRect();
    const der = tabs[Math.min(tabs.length - 1, i + 1)].getBoundingClientRect();
    const t = tab.getBoundingClientRect();
    const desde = r.left + MARGEN, hasta = r.right - MARGEN;
    let delta = 0;
    if (der.right - izq.left > hasta - desde) delta = (t.left + t.width / 2) - (r.left + r.width / 2);  // no entran: centrar
    else if (der.right > hasta) delta = der.right - hasta;
    else if (izq.left < desde) delta = izq.left - desde;
    if (Math.abs(delta) < 2) return null;
    return {c, left: Math.max(0, Math.min(c.scrollWidth - c.clientWidth, c.scrollLeft + delta))};
  };
  // Streamlit desliza la fila por su cuenta al cambiar de pestaña (scrollIntoView); lo anulamos para las pestañas
  // y queda un único movimiento suave, el nuestro (si no, las dos animaciones se pisan y la fila salta).
  const scrollOriginal = Element.prototype.scrollIntoView;
  Element.prototype.scrollIntoView = function (...args) {
    if (this.getAttribute && this.getAttribute('role') === 'tab' && this.closest('[role="tablist"]')) return;
    return scrollOriginal.apply(this, args);
  };
  let turno = 0;
  const mover = (d) => {
    if (!d) return;
    const mio = ++turno;
    setTimeout(() => {
      if (mio !== turno) return;
      d.c.scrollTo({left: d.left, behavior: 'smooth'});
      // si la animación no llega (pestaña en segundo plano, ahorro de energía), termina igual; un clic posterior manda
      setTimeout(() => { if (mio === turno && Math.abs(d.c.scrollLeft - d.left) > 2) d.c.scrollLeft = d.left; }, 900);
    }, 0);
  };
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


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
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
        f'<div class="mc-brand"><div class="mc-flag">{logo(46)}</div><div><h1>Macro<span>Center</span></h1>'
        '<p class="sub">La economía argentina, en datos</p></div></div>'
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
    items: {titulo, url, fecha, resumen, fuente, clase ('bcra'|'economia'), nueva}. Todo el texto viene de afuera: se escapa."""
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
    return f'<div class="mc-gtit"><div class="t">{html.escape(titulo)}</div>{b}</div>'


def etiqueta(texto: str) -> str:
    return f'<div class="mc-label">{texto}</div>'


def _md_a_html(texto: str) -> str:
    """El poquito de Markdown que usan las frases del panorama: **negrita**, :green[...] y :red[...]."""
    t = html.escape(texto)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r":green\[(.+?)\]", r'<span class="pos">\1</span>', t)
    return re.sub(r":red\[(.+?)\]", r'<span class="neg">\1</span>', t)


def panorama(items: list[dict], fecha: str) -> str:
    """Informe «En pocas palabras»: una fila por tema con su cifra clave y el resumen. Es neutral: describe qué pasó, sin
    calificarlo como bueno o malo."""
    esc = html.escape
    filas = "".join(
        f'<div class="fila"><div class="izq"><div class="tema">{esc(i["tema"])}</div>'
        f'<div class="cifra">{esc(i["cifra"])}</div><div class="det">{esc(i["detalle"])}</div></div>'
        f'<div class="txt">{_md_a_html(i["texto"])}</div></div>'
        for i in items)
    return (f'<div class="mc-pano"><div class="cab"><div class="tit">En pocas palabras</div>'
            f'<div class="sub">Lo más importante de la economía · datos al {esc(fecha)}</div></div>{filas}'
            '<div class="pie">Resumen automático con el último dato publicado por cada fuente (algunos tienen semanas de '
            'rezago).</div></div>')


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


def linea_tiempo(items: list[dict]) -> str:
    """Línea de tiempo vertical de presidentes. Cada item: nombre, periodo, anio, iniciales, hito, filas
    ([{'k','ini','fin','tend'}]), pico, nota, foto, pagina, actual."""
    esc = html.escape
    out = ['<div class="mc-tlwrap"><div class="mc-tl">']
    for i, it in enumerate(items):
        lado = "izq" if i % 2 == 0 else "der"
        foto = (f'<img src="{esc(it["foto"])}" alt="{esc(it["nombre"])}" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
                if it.get("foto") else "")
        dot = f'<div class="mc-foto"><span>{esc(it["iniciales"])}</span>{foto}</div>'
        if it.get("pagina"):
            dot = f'<a href="{esc(it["pagina"])}" target="_blank" rel="noopener noreferrer" title="{esc(it["nombre"])} en Wikipedia">{dot}</a>'
        filas = ""
        for f in it["filas"]:
            if f["ini"] in ("", "s/d") and f["fin"] in ("", "s/d"):
                continue  # sin datos confiables: no se muestra la fila
            valor = (f'{esc(f["ini"])} <span style="opacity:.5">→</span> ' if f["ini"] else "") + \
                    f'<span class="{f["tend"]}">{esc(f["fin"])}</span>'
            filas += f'<div class="mc-fila"><span class="k">{esc(f["k"])}</span><span class="v">{valor}</span></div>'
        pico = f'<div class="pico">{esc(it["pico"])}</div>' if it.get("pico") else ""
        nota = f'<div class="nota">{esc(it["nota"])}</div>' if it.get("nota") else ""
        out.append(
            f'<div class="mc-tl-item {lado}{" actual" if it.get("actual") else ""}">'
            f'<div class="mc-tl-card"><div class="per">{esc(it["periodo"])}</div><h4>{esc(it["nombre"])}</h4>'
            f'<div class="hito">{esc(it["hito"])}</div>{filas}{pico}{nota}</div>'
            f'<div class="mc-tl-dot">{dot}</div><div class="mc-tl-anio">{it["anio"]}</div></div>'
        )
    out.append('<div class="mc-tl-hoy">HOY</div></div></div>')
    return "".join(out)


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
            f'<div class="chips">{var}{extra}{chip}</div></div>'
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
            f'<polyline points="{puntos}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" '
            f'stroke-linecap="round"/></svg>')


def ticker(items: list[dict]) -> str:
    """Franja superior deslizante con datos clave. item: {n: nombre, v: valor, d: variación % o None, sentido: ...}."""
    esc = html.escape
    if not items:
        return ""
    celdas = []
    for it in items:
        d = it.get("d")
        if d is None or d != d:
            var = ""
        else:
            clase = _clase_var(d, it.get("sentido", "neutro"))
            flecha = _flecha(d)
            # la franja muestra la variación del último día (los indicadores clave, la de 30 días): se aclara con «1 d»
            var = (f'<span class="d {clase}" title="Variación contra el dato anterior (1 día)">{flecha} '
                   f'{abs(d):.1f}% · 1 d</span>').replace(".", ",")
        celdas.append(f'<span class="tk"><span class="n">{esc(it["n"])}</span><span class="v">{esc(it["v"])}</span>{var}</span>')
    pista = "".join(celdas)
    return f'<div class="mc-ticker" aria-label="Datos clave"><div class="pista">{pista}{pista}</div></div>'


def tabla_simple(cabeceras: list[str], filas: list[list[str]]) -> str:
    """Tabla HTML simple con el estilo de las demás (primera columna alineada a la izquierda)."""
    esc = html.escape
    cab = "".join(f"<th>{esc(c)}</th>" for c in cabeceras)
    cuerpo = "".join("<tr>" + "".join(f"<td>{esc(str(c))}</td>" for c in f) + "</tr>" for f in filas)
    return f'<table class="mc-cmp"><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>'


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


def tabla(cabeceras: list[str], filas: list[list]) -> str:
    """Como tabla_simple, pero cada celda puede ser texto o (texto, clase[, aclaración]): clase 'mejor' (verde) o
    'peor' (rojo); la aclaración va en letra chica debajo."""
    esc = html.escape

    def celda(c) -> str:
        if isinstance(c, tuple):
            texto, clase, *resto = c
            sub = f'<span class="sub">{esc(resto[0])}</span>' if resto and resto[0] else ""
            return f'<td class="{esc(clase or "")}">{esc(str(texto))}{sub}</td>'
        return f"<td>{esc(str(c))}</td>"

    cab = "".join(f"<th>{esc(c)}</th>" for c in cabeceras)
    cuerpo = "".join("<tr>" + "".join(celda(c) for c in f) + "</tr>" for f in filas)
    return f'<div class="mc-tablas"><table class="mc-cmp"><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></div>'


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
    ("INDEC / Ministerio de Economía", "Series de Tiempo (datos.gob.ar)", "https://datos.gob.ar/series/api/"),
    ("ArgentinaDatos", "Dólares, inflación histórica, riesgo país, plazos fijos, fondos y rendimientos",
     "https://argentinadatos.com/"),
    ("CoinGecko", "Criptomonedas", "https://www.coingecko.com/"),
    ("CriptoYa", "USDT por exchange y dólar MEP, CCL y cripto en vivo", "https://criptoya.com/"),
    ("Yahoo Finance", "Bolsas y materias primas (fuente no oficial)", "https://finance.yahoo.com/"),
    ("FRED (Reserva Federal de St. Louis)", "Inflación de EE. UU., para ajustar dólares", "https://fred.stlouisfed.org/"),
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
        + '<div class="main">'
        f'<div class="marca"><div class="logo">{bandera(30)}<div><b>MacroCenter</b><span>Creada por {esc(AUTOR)}</span></div>'
        f'<a class="mc-linkedin" href="{esc(LINKEDIN, quote=True)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="LinkedIn de {esc(AUTOR)}">{_ICONO_LINKEDIN} LinkedIn</a></div>'
        '<p>Reunir en un solo lugar los principales datos de la economía argentina, tomados de fuentes oficiales y actualizados en vivo, '
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
    return (f'<div class="mc-vivo"><span class="en">En vivo</span>{dolar}'
            f'<span class="sec">Series oficiales: {esc(oficiales)}</span></div>')


def pie_enlaces() -> str:
    """Enlaces fijos de la barra inferior: suscripción, términos y privacidad."""
    esc = html.escape
    bol = (f'<a class="bol" href="{esc(BOLETIN, quote=True)}" target="_blank" rel="noopener noreferrer">✉ <span class="l">Resumen semanal por mail</span>'
           '<span class="s">Suscribirme</span></a>'
           if BOLETIN else '')
    return (f'<div class="mc-pielinks">{bol}<a href="?legal=terminos" target="_self">Términos</a>'
            '<a href="?legal=privacidad" target="_self">Privacidad</a><span class="c">© 2026 MacroCenter</span></div>')


def form_alertas() -> str:
    """Formulario para anotarse en las alertas del dólar. El mail va directo del navegador a Buttondown (con la
    etiqueta «alertas»): la página nunca lo ve ni lo guarda."""
    if not BOLETIN:
        return ""
    usuario = BOLETIN.rstrip("/").rsplit("/", 1)[-1]
    accion = f"https://buttondown.com/api/emails/embed-subscribe/{usuario}"
    return (f'<form class="mc-alerta" action="{html.escape(accion, quote=True)}" method="post" target="_blank">'
            '<div class="tx"><b>🔔 Alertas del dólar por mail</b>'
            '<span>Un aviso cuando el dólar o el riesgo país se mueven fuerte en el día (también te llega el resumen '
            'semanal). Tu mail va directo a Buttondown: MacroCenter no lo ve ni lo guarda.</span></div>'
            '<div class="cp"><input type="email" name="email" required placeholder="tu@mail.com" aria-label="Tu mail" '
            'autocomplete="email" maxlength="254"><input type="hidden" name="tag" value="alertas">'
            '<input type="hidden" name="embed" value="1"><button type="submit">Anotarme</button></div></form>')


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
