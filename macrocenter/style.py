"""Estilos de MacroCenter. Usa colores translúcidos para verse bien en modo claro y oscuro."""
from __future__ import annotations

import html
import math
import re

import streamlit as st

CELESTE = "#74ACDF"  # celeste de la bandera argentina
SOL = "#F6B40E"  # amarillo del Sol de Mayo
AUTOR = "Juan Manuel Pianciola"

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
    font-size: .68rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
    opacity: .6; margin: 18px 0 6px;
}}

/* cotizaciones rápidas */
.mc-tick {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 12px; margin-bottom: 6px; border-radius: 10px;
    background: rgba(128,128,128,.10); border: 1px solid rgba(128,128,128,.14);
}}
.mc-tick .n {{ font-size: .82rem; opacity: .85; }}
.mc-tick .v {{ font-weight: 700; font-size: .95rem; text-align: right; }}
.mc-tick .d {{ font-size: .68rem; font-weight: 600; display: block; }}
.mc-up {{ color: #10AC84; }} .mc-down {{ color: #EE5253; }} .mc-flat {{ opacity: .55; }}

.mc-status {{ font-size: .75rem; opacity: .75; margin-top: 6px; }}
.mc-status .dot {{ color: #10AC84; }}

.mc-footer {{
    margin-top: 22px; padding-top: 14px; border-top: 3px double {CELESTE};
    font-size: .76rem; text-align: center; line-height: 1.5;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
}}
.mc-footer b {{ color: {CELESTE}; }}
.mc-footer .mc-made {{ font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; opacity: .6; }}

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
/* el aviso «Press Enter to apply» de Streamlit, en castellano */
[data-testid="InputInstructions"] {{ font-size: 0 !important; }}
[data-testid="InputInstructions"]::after {{ content: "Presioná Enter para aplicar"; font-size: .75rem; opacity: .7; }}

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
.mc-news-fecha span {{ font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; opacity: .75; margin-top: 3px; }}
.mc-news-tags {{ display: flex; gap: 6px; margin-bottom: 5px; }}
.mc-news .tag {{ font-size: .66rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; padding: 2px 8px;
    border-radius: 999px; }}
.mc-news .tag.bcra {{ color: {CELESTE}; background: rgba(116,172,223,.15); }}
.mc-news .tag.economia {{ color: #A9B8C9; background: rgba(169,184,201,.13); }}
.mc-news .tag.nueva {{ color: #3A2A00; background: {SOL}; }}
.mc-news-txt a {{ font-weight: 700; font-size: .98rem; line-height: 1.35; color: inherit !important; text-decoration: none; }}
.mc-news-txt a:hover {{ color: {CELESTE} !important; text-decoration: underline; text-underline-offset: 3px; }}
.mc-news-txt p {{ margin: 5px 0 0; font-size: .84rem; opacity: .72; line-height: 1.45;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.mc-news-pie {{ font-size: .8rem; opacity: .8; margin-top: 12px; }}
.mc-news-pie a {{ color: {CELESTE} !important; }}
.mc-news-vacio {{ padding: 18px; opacity: .7; }}
/* botón «Marcar todas como leídas» y su estado ya leído (verde) */
.st-key-btn_marcar_leidas button {{ border: 1px solid rgba(116,172,223,.6) !important; border-radius: 10px; }}
.st-key-btn_todo_leido button {{
    background: #10AC84 !important; border: 1px solid #10AC84 !important; border-radius: 10px;
    box-shadow: 0 4px 14px rgba(16,172,132,.35);
}}
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
.mc-conv .f:last-of-type {{ border-bottom: none; }}
.mc-conv .k {{ font-size: .82rem; font-weight: 600; display: flex; flex-direction: column; line-height: 1.2; }}
.mc-conv .k small {{ font-size: .68rem; font-weight: 500; opacity: .6; }}
.mc-conv .v {{ font-size: .98rem; font-weight: 800; white-space: nowrap; }}
.mc-conv .nota {{ font-size: .66rem; opacity: .55; margin-top: 4px; text-align: right; }}
section[data-testid="stSidebar"] .st-key-conv_sentido button {{ padding: .25rem .6rem; font-size: .8rem; }}
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
/* recuadro "En pocas palabras" de Inicio */
.st-key-panorama {{ border-left: 4px solid {CELESTE} !important; background: rgba(116,172,223,.05); }}
.st-key-panorama ul {{ margin-bottom: 0; }}
.st-key-panorama li {{ margin-bottom: .3rem; line-height: 1.55; }}

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
.mc-title .sub {{ opacity: .7; font-size: .92rem; }}
.mc-by {{ font-size: .82rem; opacity: .7; text-align: right; }}
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
.mc-tl-anio {{ grid-row: 1; font-size: 2rem; font-weight: 800; letter-spacing: -1px; opacity: .28; }}
.mc-tl-item.izq .mc-tl-anio {{ grid-column: 3; padding-left: 24px; }}
.mc-tl-item.der .mc-tl-anio {{ grid-column: 1; text-align: right; padding-right: 24px; }}
.mc-tl-card h4 {{ margin: 0 0 2px; padding: 0; font-size: 1.25rem; font-weight: 800; }}
.mc-tl-card .per {{ font-size: .74rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {CELESTE}; }}
.mc-tl-card .hito {{ font-size: .88rem; opacity: .88; margin: 8px 0 10px; line-height: 1.4; }}
.mc-fila {{
    display: flex; justify-content: space-between; gap: 10px; padding: 5px 0;
    border-top: 1px dashed rgba(128,128,128,.3); font-size: .84rem;
}}
.mc-fila .k {{ opacity: .7; }}
.mc-fila .v {{ font-weight: 600; text-align: right; }}
.mc-fila .mejor {{ color: #10AC84; }}
.mc-fila .peor {{ color: #EE5253; }}
.mc-tl-card .pico {{ margin-top: 8px; font-size: .8rem; opacity: .9; }}
.mc-tl-card .nota {{ margin-top: 6px; font-size: .74rem; opacity: .6; font-style: italic; }}
.mc-tl-hoy {{
    width: max-content; margin: 0 auto; padding: 5px 16px; border-radius: 999px; font-weight: 800; font-size: .8rem;
    letter-spacing: .14em; color: #3A2A00; background: linear-gradient(135deg, {SOL}, #F79F1F);
    box-shadow: 0 4px 12px rgba(246,180,14,.4); position: relative; z-index: 1;
}}
@media (max-width: 860px) {{
    .mc-tl::before {{ left: 48px; }}
    .mc-tl-item {{ grid-template-columns: 96px 1fr; }}
    .mc-tl-dot {{ grid-column: 1; justify-self: start; }}
    .mc-tl-item.izq .mc-tl-card, .mc-tl-item.der .mc-tl-card {{ grid-column: 2; }}
    .mc-tl-anio {{ display: none; }}
    .mc-foto {{ width: 76px; height: 76px; margin-left: 10px; }}
    .mc-tl-hoy {{ margin-left: 10px; }}
}}

/* ── Pie de página: franja celeste de la paleta ── */
.mc-foot {{
    margin: 48px 0 0; padding: 28px 30px; border-radius: 18px 18px 0 0; color: inherit;
    background: rgba(116,172,223,.10); border: 1px solid rgba(116,172,223,.22); border-top: 3px solid {CELESTE};
}}
.mc-foot .cols {{ display: grid; grid-template-columns: 1.4fr 1.2fr .8fr; gap: 28px; }}
.mc-foot h5 {{ margin: 0 0 10px; padding: 0; font-size: .74rem; font-weight: 800; letter-spacing: .14em;
    text-transform: uppercase; color: {CELESTE}; }}
.mc-foot ul {{ list-style: none; margin: 0; padding: 0; font-size: .86rem; line-height: 1.75; opacity: .9; }}
.mc-foot a {{ color: {CELESTE}; font-weight: 700; text-decoration: none; border-bottom: 1px solid rgba(116,172,223,.4); }}
.mc-foot a:hover {{ border-bottom-color: {CELESTE}; }}
.mc-foot p {{ margin: 0 0 8px; font-size: .86rem; line-height: 1.55; }}
.mc-foot .fin {{ text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; }}
.mc-foot .made {{ font-size: .7rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; opacity: .75; }}
.mc-foot .legal {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; margin-top: 22px;
    padding-top: 14px; border-top: 1px solid rgba(128,128,128,.28); font-size: .8rem; opacity: .9; }}

/* ── Resultado final: fichas ── */
.mc-rf {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 6px 0 4px; }}
.mc-rf .f {{
    border: 1px solid rgba(128,128,128,.25); border-left: 4px solid {CELESTE}; border-radius: 12px;
    padding: 12px 14px; background: rgba(128,128,128,.07);
}}
.mc-rf .f.ok {{ border-left-color: #10AC84; }} .mc-rf .f.mal {{ border-left-color: #EE5253; }}
.mc-rf .k {{ font-size: .7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; opacity: .65; }}
.mc-rf .v {{ font-size: 1.45rem; font-weight: 800; margin: 2px 0; letter-spacing: -.01em; }}
.mc-rf .d {{ font-size: .8rem; opacity: .75; line-height: 1.35; }}
@media (max-width: 860px) {{ .mc-foot .cols {{ grid-template-columns: 1fr; }} }}

/* ── Páginas legales ── */
.mc-legal {{ max-width: 860px; margin: 8px auto 0; }}
.mc-legal h1 {{ margin: 0; padding: 0; font-size: 2rem; font-weight: 800; letter-spacing: -.5px; }}
.mc-legal .act {{ opacity: .55; font-size: .88rem; margin: 4px 0 18px; }}
.mc-legal h3 {{ margin: 26px 0 10px; padding: 0; font-size: 1.1rem; font-weight: 800; color: {CELESTE}; }}
.mc-legal .card {{ padding: 18px 22px; border-radius: 14px; background: rgba(128,128,128,.09);
    border: 1px solid rgba(128,128,128,.16); }}
.mc-legal .card.intro {{ background: rgba(116,172,223,.10); border-color: rgba(116,172,223,.3); }}
.mc-legal .card p {{ margin: 0 0 10px; line-height: 1.7; font-size: .95rem; }}
.mc-legal .card p:last-child {{ margin-bottom: 0; }}

/* ── Tarjetas de cotización ── */
/* columnas según la cantidad de tarjetas (--cols, ver _columnas): filas parejas, sin tarjetas huérfanas */
.mc-fxgrid {{ display: grid; grid-template-columns: repeat(var(--cols, 4), minmax(0, 1fr)); gap: 12px; margin: 8px 0 8px; }}
@media (max-width: 1100px) {{ .mc-fxgrid {{ grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); }} }}
.mc-fx {{
    padding: 14px 16px 12px; border-radius: 14px; background: rgba(128,128,128,.09); min-width: 0; overflow: hidden;
    border: 1px solid rgba(116,172,223,.32); border-top: 4px solid {CELESTE};
    transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}}
.mc-fx:hover {{ border-color: rgba(116,172,223,.6); transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.18); }}
.mc-fx .n {{ font-weight: 800; font-size: .98rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
/* descripción: siempre el alto de dos renglones, así los valores de todas las tarjetas quedan a la misma altura */
.mc-fx .d {{ font-size: .72rem; opacity: .65; line-height: 1.3; min-height: 2.6em; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
.mc-fx .v {{ font-size: 1.5rem; font-weight: 800; letter-spacing: -.5px; margin: 6px 0 0; white-space: nowrap; min-width: 0; }}
.mc-fx .c {{ font-size: .78rem; opacity: .75; margin-bottom: 8px; }}
.mc-fx .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.mc-fx .chip {{ font-size: .7rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: rgba(128,128,128,.16); }}
.mc-fx .chip.bien {{ color: #10AC84; background: rgba(16,172,132,.16); }}
.mc-fx .chip.mal {{ color: #EE5253; background: rgba(238,82,83,.16); }}
.mc-fx .chip.flat {{ opacity: .8; }}
.mc-fx .fila {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; min-width: 0; }}
/* el mini-gráfico se angosta si el valor es largo, en lugar de salirse de la tarjeta */
.mc-fx .spark {{ flex: 0 1 76px; min-width: 28px; width: 76px; opacity: .95; }}
@media (max-width: 640px) {{
    .mc-fxgrid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
    .mc-fx {{ padding: 11px 12px 10px; }}
    .mc-fx .v {{ font-size: 1.15rem; }}
    .mc-fx .spark {{ display: none; }}
    .mc-fx .c {{ font-size: .72rem; }}
}}

/* ── Franja superior deslizante (inspirada en los tableros de cotizaciones) ── */
.mc-ticker {{
    overflow: hidden; white-space: nowrap; border-radius: 12px; padding: 9px 0; margin: 0 0 6px;
    background: rgba(128,128,128,.07); border: 1px solid rgba(116,172,223,.28);
    -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 3%, #000 97%, transparent 100%);
            mask-image: linear-gradient(90deg, transparent 0, #000 3%, #000 97%, transparent 100%);
}}
.mc-ticker .pista {{ display: inline-flex; width: max-content; animation: mc-marquee 120s linear infinite; }}
.mc-ticker:hover .pista {{ animation-play-state: paused; }}
.mc-ticker .tk {{ display: inline-flex; align-items: baseline; gap: 8px; padding: 0 22px; border-right: 1px solid rgba(128,128,128,.22); }}
.mc-ticker .n {{ font-size: .68rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; opacity: .6; }}
.mc-ticker .v {{ font-weight: 800; font-size: .92rem; }}
.mc-ticker .d {{ font-size: .75rem; font-weight: 700; opacity: .75; }}
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
.mc-viaje .per {{ font-size: .74rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {CELESTE}; }}
.mc-viaje .hito {{ font-size: .9rem; opacity: .85; line-height: 1.4; }}
.mc-cmp {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 8px 0 12px; font-size: .92rem; }}
.mc-cmp th {{ text-align: right; padding: 8px 12px; font-size: .74rem; letter-spacing: .08em; text-transform: uppercase;
    opacity: .7; border-bottom: 2px solid {CELESTE}; }}
.mc-cmp th:first-child, .mc-cmp td:first-child {{ text-align: left; }}
.mc-cmp td {{ text-align: right; padding: 9px 12px; border-bottom: 1px dashed rgba(128,128,128,.3); font-weight: 600; }}
.mc-cmp td:first-child {{ font-weight: 400; opacity: .8; }}
.mc-cmp .mejor {{ color: #10AC84; }}
.mc-cmp .peor {{ color: #EE5253; }}

[data-testid="stMetric"] {{ border-radius: 14px; transition: border-color .18s ease; }}
[data-testid="stMetric"]:hover {{ border-color: rgba(116,172,223,.55); }}
/* números de los indicadores: más peso y espaciado ajustado, como en los tableros financieros */
[data-testid="stMetricValue"] {{ font-weight: 650 !important; letter-spacing: -.02em; }}
/* tarjetas de una misma fila, del mismo alto (con o sin variación debajo) */
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:only-child > [data-testid="stMetric"])
    > [data-testid="stVerticalBlock"],
[data-testid="stElementContainer"]:only-child:has(> [data-testid="stMetric"]),
[data-testid="stElementContainer"]:only-child > [data-testid="stMetric"] {{ height: 100%; }}
/* menos aire muerto arriba: el contenido arranca justo debajo de la barra superior */
[data-testid="stMainBlockContainer"] {{ padding-top: 3.6rem; }}
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
h3 {{ font-weight: 700 !important; }}
/* la etiqueta de variación de los indicadores no se corta con «…»: si no entra, baja de renglón */
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] p {{
    white-space: normal !important; overflow: visible !important; text-overflow: clip !important; height: auto !important;
}}
[data-testid="stMetricDelta"] {{ max-width: 100%; line-height: 1.25; word-break: normal; overflow-wrap: normal; }}
/* pantallas medianas (notebook con la barra lateral abierta): los indicadores van de a tres por fila
   en vez de apretarse cinco en una, que cortaba los valores con «…» */
@media (min-width: 641px) and (max-width: 1250px) {{
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]) {{
        flex-wrap: wrap !important; gap: .75rem !important;
    }}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]) > [data-testid="stColumn"] {{
        flex: 1 1 calc(33.3% - .75rem) !important; min-width: calc(33.3% - .75rem) !important; width: auto !important;
    }}
}}

/* ── Celular y pantallas angostas: más aire, indicadores de a dos y todo legible ── */
@media (max-width: 640px) {{
    .block-container {{ padding: 3.2rem .85rem 2rem !important; }}
    h1 {{ font-size: 1.6rem !important; }}
    h2, [data-testid="stHeading"] h2 {{ font-size: 1.3rem !important; }}
    h3 {{ font-size: 1.15rem !important; }}
    /* indicadores: dos por fila en vez de una tarjeta enorme por fila */
    [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {{ flex-wrap: wrap !important; gap: .6rem !important; }}
    [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"] {{
        flex: 1 1 calc(50% - .6rem) !important; min-width: calc(50% - .6rem) !important; width: auto !important;
    }}
    [data-testid="stMetric"] {{ padding: .7rem .8rem !important; }}
    [data-testid="stMetric"] > div {{ padding: 0 !important; }}  /* Streamlit le suma otro relleno adentro */
    [data-testid="stMetricValue"] {{ font-size: 1.45rem !important; }}
    [data-testid="stMetricLabel"] p {{ font-size: .8rem !important; }}
    [data-testid="stMetricDelta"] {{ font-size: .72rem !important; }}
    /* pestañas y botones más cómodos al tacto */
    [data-testid="stTab"] {{ height: 3rem; padding: 0 .85rem; }}
    [data-testid="stTab"] p {{ font-size: 1rem; }}
    button[data-variant="segmented_control"] {{ padding: .5rem .85rem; }}
    /* tablas anchas: se deslizan de costado en lugar de apretarse */
    [data-testid="stTable"], [data-testid="stDataFrame"] {{ overflow-x: auto; }}
    /* pie de página y fichas en una columna */
    .mc-foot {{ padding: 20px 18px; margin-top: 32px; }}
    .mc-foot .legal {{ flex-direction: column; }}
    .mc-brand h1 {{ font-size: 1.3rem !important; }}
}}
</style>
"""


# Al tocar una pestaña de un borde, la fila se desliza lo justo para mostrar la que sigue (o la anterior); las del
# medio no mueven nada. Se instala una sola vez por página y también sigue a las flechas del teclado.
JS_PESTANAS = """
<script>
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
  document.addEventListener('click', (e) => {
    const tab = e.target.closest && e.target.closest('[role="tablist"] [role="tab"]');
    if (tab) mover(destinoPara(tab));
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


def favicon():
    """Ícono de la pestaña: el mismo logo, dibujado con PIL (viene incluido con Streamlit) en alta resolución."""
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
        f'<div class="mc-brand"><div class="mc-flag">{logo(46)}</div><h1>Macro<span>Center</span></h1></div>'
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


def etiqueta(texto: str) -> str:
    return f'<div class="mc-label">{texto}</div>'


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
    out = ['<div class="mc-tl">']
    for i, it in enumerate(items):
        lado = "izq" if i % 2 == 0 else "der"
        foto = (f'<img src="{esc(it["foto"])}" alt="{esc(it["nombre"])}" loading="lazy" referrerpolicy="no-referrer">'
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
    out.append('<div class="mc-tl-hoy">HOY</div></div>')
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
    out = [f'<div class="mc-fxgrid" style="--cols:{_columnas(len(tarjetas))}">']
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
    out.append("</div>")
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
    img = (f'<img src="{esc(url)}" alt="{esc(nombre)}" loading="lazy" referrerpolicy="no-referrer">' if url else "")
    estilo = f' style="box-shadow:0 0 0 3px {SOL},0 0 20px rgba(246,180,14,.65)"' if actual else ""
    nodo = f'<div class="mc-foto"{estilo}><span>{esc(iniciales)}</span>{img}</div>'
    if pagina:
        nodo = f'<a href="{esc(pagina)}" target="_blank" rel="noopener noreferrer" title="{esc(nombre)} en Wikipedia">{nodo}</a>'
    return nodo


def viaje(nombre: str, iniciales: str, periodo: str, hito: str, url: str | None, pagina: str | None, actual: bool) -> str:
    esc = html.escape
    return (f'<div class="mc-viaje">{foto_html(nombre, iniciales, url, pagina, actual)}<div>'
            f'<div class="per">{esc(periodo)}</div><h3>{esc(nombre)}</h3><div class="hito">{esc(hito)}</div></div></div>')


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
    ("ArgentinaDatos", "Dólares, inflación histórica y riesgo país", "https://argentinadatos.com/"),
    ("CoinGecko", "Criptomonedas", "https://www.coingecko.com/"),
    ("CriptoYa", "USDT por exchange argentino", "https://criptoya.com/"),
    ("Yahoo Finance", "Bolsas y materias primas (fuente no oficial)", "https://finance.yahoo.com/"),
    ("FRED (Reserva Federal de St. Louis)", "Inflación de EE. UU., para ajustar dólares", "https://fred.stlouisfed.org/"),
    ("Wikipedia / Wikimedia Commons", "Fotos de los presidentes", "https://commons.wikimedia.org/"),
]


def footer() -> str:
    """Pie de página con color propio (celeste de la paleta): fuentes, aviso y crédito."""
    esc = html.escape
    lista = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{esc(n)}</a> — {esc(d)}</li>'
                    for n, d, u in FUENTES)
    return (
        '<div class="mc-foot"><div class="cols">'
        f'<div><h5>Fuentes de datos</h5><ul>{lista}</ul></div>'
        '<div><h5>Propósito de la página</h5><p>Reunir en un solo lugar los principales datos de la economía argentina, tomados de fuentes oficiales y actualizados en vivo, '
        'para que cualquier persona pueda consultarlos, compararlos con su historia y entenderlos.</p>'
        '<h5 style="margin-top:14px">Importante</h5><p><b>Algunos datos pueden tener un rezago</b> respecto de lo que difunden las fuentes en el día '
        '(por ejemplo, las reservas del BCRA se publican con 1 o 2 días de demora). '
        'Los datos vienen de APIs y sitios públicos y pueden tener demoras o revisiones. '
        'Los valores son de referencia y no constituyen asesoramiento financiero. Las notas y las calificaciones son '
        'medidas orientativas, con criterios propios.</p></div>'
        f'<div class="fin">{bandera(46)}<p><b>MacroCenter</b><br>Creada por {esc(AUTOR)}</p>'
        '<p class="made">Hecho en Argentina</p></div>'
        '</div>'
        '<div class="legal"><span>© 2026 MacroCenter — Todos los derechos reservados.</span>'
        '<span><a href="?legal=terminos" target="_self">Términos y condiciones</a>'
        ' · <a href="?legal=privacidad" target="_self">Política de privacidad</a></span></div>'
        '</div>'
    )


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
