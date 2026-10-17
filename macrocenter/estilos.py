"""Hojas de estilo y adaptación al tema de MacroCenter."""
import re

CELESTE = "#74ACDF"
SOL = "#F6B40E"
FUENTE = '"Segoe UI Variable Text", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Roboto, Arial, sans-serif'

CSS = f"""
<style>
/* el contenido estaba invisible hasta que llegara esta hoja (ver OCULTAR_HASTA_ESTILO): se muestra cuando además
   JS_PESTANAS ya detectó el tema (html[data-listo]), así tampoco se ve un instante con los colores del otro tema */
html[data-listo] [data-testid="stSidebarUserContent"], html[data-listo] [data-testid="stMainBlockContainer"] {{
    opacity: 1 !important; animation: none !important; }}
/* si el script del tema tardara, igual se muestra a los 1,2 s de llegar esta hoja (otro nombre de animación: así
   arranca recién ahora y no hereda el reloj del respaldo de OCULTAR_HASTA_ESTILO) */
[data-testid="stSidebarUserContent"], [data-testid="stMainBlockContainer"] {{
    animation: mc-ver-hoja 0s linear 1.2s forwards; }}
@keyframes mc-ver-hoja {{ to {{ opacity: 1; }} }}
/* llegó la hoja: se va el círculo de carga de OCULTAR_HASTA_ESTILO */
.stApp::after {{ content: none !important; display: none !important; animation: none !important; }}
/* al cambiar de tema, todo cambia de color de golpe (sin transiciones que arrastren el color del tema anterior) */
html[data-tema-cambio] *, html[data-tema-cambio] *::before, html[data-tema-cambio] *::after {{ transition: none !important; }}
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
    display: flex; align-items: center; gap: 13px; background: none; box-shadow: none; border-radius: 0;
    padding: 6px 4px 18px; margin-bottom: 16px; color: inherit; position: relative;
}}
/* una línea fina que se desvanece (antes, una franja gruesa celeste y blanca) */
.mc-brand::after {{
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1px;
    background: linear-gradient(90deg, rgba(116,172,223,.75), rgba(116,172,223,.25) 60%, rgba(116,172,223,0));
}}
/* toda la marca es un enlace al resumen */
a.mc-brand, a.mc-brand:hover {{ text-decoration: none !important; color: inherit !important; cursor: pointer; }}
.mc-brand .mc-flag {{ line-height: 0; }}
.mc-brand .mc-flag svg {{ transition: transform .18s ease, box-shadow .18s ease; }}
a.mc-brand:hover .mc-flag svg {{ transform: translateY(-1px) scale(1.04); box-shadow: 0 8px 20px rgba(0,0,0,.4), 0 0 0 1px {CELESTE}; }}
.mc-brand .mc-flag svg {{ width: 46px; height: 46px; border-radius: 13px;
    box-shadow: 0 6px 16px rgba(0,0,0,.35), 0 0 0 1px rgba(116,172,223,.35); }}
.mc-brand h1 {{ margin: 0; padding: 0; font-size: 1.5rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.05;
    color: inherit; }}
/* el nombre: misma familia que la página, en seminegrita pareja (sin mezclar pesos) y con «Center» celeste. Las reglas apuntan a
   .c y no a «h1 span»: Streamlit envuelve el texto del título en su propio <span>, y con «h1 span» todo el nombre
   quedaba fino y celeste */
.mc-brand .txt {{ display: flex; flex-direction: column; min-width: 0; }}
.stApp section[data-testid="stSidebar"] .mc-brand .mc-wm {{ display: block; line-height: 1.05; font-size: 1.45rem; font-weight: 600 !important;
    letter-spacing: 0; color: #FFFFFF; }}
.stApp section[data-testid="stSidebar"] .mc-brand .mc-wm * {{ font-weight: inherit !important; color: inherit; }}
.stApp section[data-testid="stSidebar"] .mc-brand .mc-wm .c {{ color: {CELESTE} !important; font-weight: 600 !important; }}
html[data-tema="claro"] .stApp section[data-testid="stSidebar"] .mc-brand .mc-wm {{ color: #0E1A2B; }}
html[data-tema="claro"] .stApp section[data-testid="stSidebar"] .mc-brand .mc-wm .c {{ color: #2E6DB4 !important; }}
/* etiqueta «Beta» junto al nombre: chica, para avisar que todavía es una versión de prueba */
.stApp section[data-testid="stSidebar"] .mc-brand .mc-wm .beta {{ display: inline-block; vertical-align: middle;
    margin-left: 7px; padding: 2px 7px; border-radius: 999px; font-size: .62rem !important; font-weight: 800 !important;
    letter-spacing: .08em; text-transform: uppercase; line-height: 1.3; color: #0E1A2B !important; background: {SOL};
    position: relative; top: -2px; }}
.mc-brand .sub {{ display: block; margin: 6px 0 0; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
    line-height: 1.2; opacity: .85; }}

/* ── Barra lateral: terminación propia ── */
/* sin barra de desplazamiento (se veía la de Windows, gruesa y genérica): se sigue pudiendo deslizar, y el borde de
   abajo se desvanece para indicar que hay más */
[data-testid="stSidebarContent"] {{ scrollbar-width: none !important;
    -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 56px), transparent);
    mask-image: linear-gradient(to bottom, #000 calc(100% - 56px), transparent); }}
[data-testid="stSidebarContent"]::-webkit-scrollbar {{ display: none !important; width: 0 !important; }}
[data-testid="stSidebarUserContent"] {{ padding-bottom: 72px !important; }}
/* títulos de sección: celestes, con una línea fina hasta el borde */
section[data-testid="stSidebar"] .mc-label {{ display: flex; align-items: center; gap: 10px; color: {CELESTE}; opacity: 1;
    margin: 22px 0 8px; font-size: .84rem; font-weight: 700; letter-spacing: .14em; }}
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
    color: {CELESTE}; font-size: 1.1rem; width: 30px; height: 30px; display: inline-flex; align-items: center;
    justify-content: center; border-radius: 8px; background: rgba(116,172,223,.13); flex: 0 0 30px; }}
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
.st-key-btn_noticias_nuevas button [data-testid="stIconMaterial"] {{ color: #3A2A00 !important; }}  /* el ícono, visible sobre el dorado */
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
    background: linear-gradient(135deg, #3A7BC0 0%, #2563A8 100%) !important; border-color: {CELESTE} !important;
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
.mc-news .tag.indec {{ color: #C3A6F0; background: rgba(195,166,240,.14); }}
.mc-news .tag.nueva {{ color: #3A2A00; background: {SOL}; }}
.mc-news-txt a {{ font-weight: 700; font-size: .98rem; line-height: 1.35; color: inherit !important; text-decoration: none; }}
.mc-news-txt a:hover {{ color: {CELESTE} !important; text-decoration: underline; text-underline-offset: 3px; }}
.mc-news-txt p {{ margin: 5px 0 0; font-size: .84rem; opacity: .85; line-height: 1.45;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.mc-news-pie {{ font-size: .8rem; opacity: .8; margin-top: 12px; }}
.mc-news-pie a {{ color: {CELESTE} !important; }}
.mc-news-vacio {{ padding: 18px; opacity: .85; }}
/* botones de la ventana de noticias: la misma familia (altura, esquinas, letra e ícono). «Marcar todas» y «Leída»,
   celestes con contorno; «Todo leído», verde suave */
:is(.st-key-btn_marcar_leidas, .st-key-btn_todo_leido, [class*="st-key-leer_"]) button {{
    min-height: 40px !important; padding: .45rem 1rem !important; border-radius: 10px !important; gap: .4rem;
    border: 1px solid rgba(116,172,223,.5) !important; background: rgba(116,172,223,.10) !important;
    transition: background-color .15s ease, border-color .15s ease, transform .15s ease;
}}
:is(.st-key-btn_marcar_leidas, .st-key-btn_todo_leido, [class*="st-key-leer_"]) button p {{
    font-size: .95rem !important; font-weight: 700; color: {CELESTE} !important; white-space: nowrap; }}
:is(.st-key-btn_marcar_leidas, .st-key-btn_todo_leido, [class*="st-key-leer_"]) button [data-testid="stIconMaterial"] {{
    color: {CELESTE}; font-size: 1.15rem; }}
:is(.st-key-btn_marcar_leidas, [class*="st-key-leer_"]) button:hover {{
    background: rgba(116,172,223,.2) !important; border-color: {CELESTE} !important; transform: translateY(-1px); }}
.st-key-btn_todo_leido button {{ background: rgba(16,172,132,.14) !important; border-color: rgba(16,172,132,.55) !important; }}
.st-key-btn_todo_leido button p, .st-key-btn_todo_leido button [data-testid="stIconMaterial"] {{ color: #2ED3A0 !important; }}
.st-key-btn_todo_leido button:hover {{ background: rgba(16,172,132,.22) !important; border-color: #10AC84 !important; }}
html[data-tema="claro"] .st-key-btn_todo_leido button p,
html[data-tema="claro"] .st-key-btn_todo_leido button [data-testid="stIconMaterial"] {{ color: #0B7A5E !important; }}
html[data-tema="claro"] :is(.st-key-btn_marcar_leidas, [class*="st-key-leer_"]) button p,
html[data-tema="claro"] :is(.st-key-btn_marcar_leidas, [class*="st-key-leer_"]) button [data-testid="stIconMaterial"] {{ color: #2E6DB4 !important; }}

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
.mc-conv .k {{ font-size: .92rem; font-weight: 600; display: flex; flex-direction: column; line-height: 1.2; }}
.mc-conv .k small {{ font-size: .84rem; font-weight: 500; opacity: .85; }}
.mc-conv .v {{ font-size: 1.1rem; font-weight: 800; white-space: nowrap; }}
.mc-conv .nota {{ font-size: .84rem; opacity: .85; margin: 6px 0 0; padding: 8px 0 4px; text-align: center;
    border-top: 1px solid rgba(116,172,223,.2); }}
/* Streamlit le resta un margen inferior al texto de la caja: sin este relleno la nota quedaba pegada al borde */
section[data-testid="stSidebar"] .st-key-conv_caja .mc-conv {{ padding-bottom: 12px !important; }}
section[data-testid="stSidebar"] .st-key-conv_sentido button {{ padding: .25rem .5rem; font-size: .8rem; flex: 1 1 0; }}
section[data-testid="stSidebar"] .st-key-conv_sentido [data-baseweb="button-group"],
section[data-testid="stSidebar"] .st-key-conv_sentido [role="radiogroup"] {{ width: 100%; flex-wrap: nowrap; }}
section[data-testid="stSidebar"] .st-key-conv_pesos input, section[data-testid="stSidebar"] .st-key-conv_usd input {{
    font-weight: 700; }}
.mc-termino {{ border-left: 3px solid {SOL}; }}
.mc-termino-t {{ font-weight: 800; font-size: 1.05rem; margin-bottom: 4px; color: {SOL}; }}
.mc-termino-d {{ font-size: .92rem; line-height: 1.5; opacity: .92; }}
/* atajos: como el menú, pero más chicos y con ícono */
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button {{
    justify-content: flex-start; background: transparent; border: none; border-radius: 10px;
    padding: .35rem .7rem; min-height: 0;
}}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button > div,
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button [data-testid="stMarkdownContainer"] {{
    justify-content: flex-start !important; text-align: left !important;
}}
section[data-testid="stSidebar"] [class*="st-key-atajo_"] button p {{ font-size: .95rem; font-weight: 600; }}
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
:is(.mc-nota, .mc-aviso) .pos {{ color: #10AC84; font-weight: 700; }}
:is(.mc-nota, .mc-aviso) .neg {{ color: #EE5253; font-weight: 700; }}

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
    background: linear-gradient(135deg, #3A7BC0 0%, #2563A8 100%) !important; color: #fff !important;
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
    background: linear-gradient(135deg, #3A7BC0 0%, #2563A8 100%) !important; border-color: transparent !important;
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
/* el texto del período elegido, dorado claro sobre el dorado suave (en el tema claro, marrón: ver más abajo) */
[class*="st-key-per_"] button[data-variant="pills"][aria-checked="true"] p,
.st-key-cal_anios button[data-variant="pills"][aria-checked="true"] p {{ color: #FFD465 !important; }}
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
.mc-pie-btn {{ position: fixed; right: 140px; bottom: calc(var(--mc-pie-alto, 66px) - 1px); z-index: 95; width: 48px;
    height: 20px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 10px 10px 0 0;
    cursor: pointer; border: 1px solid rgba(116,172,223,.6); border-bottom: 0; background: #16263b; color: {CELESTE};
    font: 700 11px/1 inherit; opacity: .9; box-shadow: 0 -2px 8px rgba(0,0,0,.25);
    transition: opacity .15s ease, transform .15s ease, bottom .3s ease, width .3s ease, height .3s ease,
    border-radius .3s ease; }}
.mc-pie-btn:hover, .mc-pie-btn:focus-visible {{ opacity: 1; transform: translateY(-1px); }}
/* íconos de Streamlit: hasta que llega su fuente (la primera vez que se entra desde un navegador) se veía su nombre como
   texto («newspaper», «tune»...). Quedan invisibles y recortados hasta que JS_PESTANAS confirma que la fuente cargó;
   si el script no corriera, aparecen igual a los 3 segundos */
[data-testid="stIconMaterial"] {{ overflow: hidden; white-space: nowrap; }}
html:not([data-iconos]) [data-testid="stIconMaterial"] {{ opacity: 0; animation: mc-icono-ver 0s linear 3s forwards; }}
@keyframes mc-icono-ver {{ to {{ opacity: 1; }} }}
html[data-pie] .mc-pie-btn {{ bottom: 0; width: 56px; height: 22px; border-radius: 10px 10px 0 0; border-bottom: 0;
    opacity: .85; }}
html[data-pie="oculto"] .st-key-pie_datos {{ display: none !important; }}
/* apertura y cierre animados: la barra sube desde el borde inferior o baja hasta desaparecer (lo marca JS_PESTANAS) */
@keyframes mc-pie-entra {{ from {{ transform: translateY(100%); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
@keyframes mc-pie-sale {{ from {{ transform: none; opacity: 1; }} to {{ transform: translateY(100%); opacity: 0; }} }}
html[data-pie-anim="entra"] .st-key-pie_datos {{ animation: mc-pie-entra .3s ease-out; }}
html[data-pie-anim="sale"] .st-key-pie_datos {{ animation: mc-pie-sale .3s ease-in forwards; }}
html[data-pie="oculto"] [data-testid="stMainBlockContainer"] {{ padding-bottom: 2rem !important; }}
/* en el celular, la esquina inferior derecha la ocupan el logo de Streamlit y el de la cuenta (no se pueden sacar desde
   la app): la lengüeta va a la izquierda. La barra lateral desplegada la tapa (queda por debajo de ella) */
@media (max-width: 560px) {{ .mc-pie-btn {{ right: auto; left: 12px; }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-pie-btn {{ transition: none; }}
    html[data-pie-anim] .st-key-pie_datos {{ animation: none; }} }}
/* mapa de inflación: la provincia bajo el cursor se levanta (la copia la arma JS_PESTANAS). Solo se animan transform y
   opacity: la sombra es otra copia oscura que queda en el lugar, sin filtros que obliguen a repintar */
.mc-lift {{ pointer-events: none; }}
.mc-lift path {{ transform-box: fill-box; transform-origin: center; transition: transform .22s ease-out, opacity .22s ease-out; }}
.mc-lift-sombra {{ fill: #000 !important; opacity: 0 !important; stroke: none !important; }}
.mc-lift-tapa {{ stroke: #FFFFFF !important; stroke-width: 1.4px !important; }}
.mc-lift.arriba .mc-lift-sombra {{ opacity: .45 !important; transform: translate(3px, 4px); }}
.mc-lift.arriba .mc-lift-tapa {{ transform: translate(-2px, -6px) scale(1.06); }}
@media (prefers-reduced-motion: reduce) {{ .mc-lift path {{ transition: none; }} }}
/* campo oculto por el que el navegador le pasa a la app las noticias leídas (no se ve ni ocupa lugar) */
.st-key-puente_leidas {{ position: absolute !important; left: -9999px !important; width: 1px !important; height: 1px !important;
    overflow: hidden !important; opacity: 0 !important; pointer-events: none !important; }}
[data-testid="stElementContainer"]:has(> .st-key-puente_leidas), [data-testid="stLayoutWrapper"]:has(> .st-key-puente_leidas) {{
    position: absolute !important; height: 0 !important; margin: 0 !important; overflow: hidden !important; }}
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

.mc-foto {{
    width: 88px; height: 88px; border-radius: 50%; position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 1.6rem;
    background: linear-gradient(135deg, {CELESTE}, #4A8FD4); border: 4px solid #FFFFFF;
    box-shadow: 0 0 0 3px {CELESTE}, 0 6px 16px rgba(0,0,0,.3);
}}
.mc-foto img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top center; }}
.mc-fila {{
    display: flex; justify-content: space-between; gap: 10px; padding: 5px 0;
    border-top: 1px dashed rgba(128,128,128,.3); font-size: .84rem;
}}
.mc-fila .k {{ opacity: .85; }}
.mc-fila .v {{ font-weight: 600; text-align: right; }}
.mc-fila .mejor {{ color: #10AC84; }}
.mc-fila .peor {{ color: #EE5253; }}
/* ── Selector de sección de Historia y de Ahorro e inversiones: pestañas grandes ── */
:is(.st-key-hist_seccion, .st-key-inv_seccion), :is(.st-key-hist_seccion, .st-key-inv_seccion) [data-testid="stButtonGroup"] {{ width: 100% !important; }}
/* misma separación entre botones que contra el borde del recuadro, y todos del mismo ancho (Streamlit les pone un
   margen negativo para pegarlos: acá van sueltos) */
:is(.st-key-hist_seccion, .st-key-inv_seccion) [data-testid="stButtonGroup"] > div {{ width: 100% !important;
    max-width: none !important; display: flex; gap: 8px !important; padding: 6px !important; box-sizing: border-box; }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button {{
    flex: 1 1 0; min-width: 0; margin: 0 !important; min-height: 3.3rem; border-radius: 16px !important; padding: .6rem 1.1rem !important;
    border: 1px solid rgba(116,172,223,.4) !important; background: rgba(116,172,223,.07) !important;
    transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease;
}}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button p {{ font-size: 1.02rem !important; font-weight: 800; }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(74,143,212,.2); }}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button[aria-checked="true"] {{
    background: linear-gradient(135deg, #3A7BC0 0%, #2563A8 100%) !important; border-color: {CELESTE} !important;
    box-shadow: 0 8px 20px rgba(74,143,212,.35), inset 0 -3px 0 {SOL};
}}
:is(.st-key-hist_seccion, .st-key-inv_seccion) button[aria-checked="true"] p {{ color: #fff !important; }}

/* selectores grandes de sección (Historia, Ahorro e inversiones) con poco ancho: letra algo menor y el texto puede bajar
   de renglón en vez de cortarse */
@container principal (max-width: 640px) {{
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button {{ padding: .5rem .55rem !important; min-height: 2.9rem; }}
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button p {{
        font-size: .9rem !important; white-space: normal !important; overflow: visible !important;
        text-overflow: clip !important; line-height: 1.2; text-align: center; }}
}}

/* selector de Herramientas (tres tarjetas): en una fila; si no entran, una debajo de la otra (con poco ancho, el
   texto de cada botón se partía letra por letra) */
[data-testid="stHorizontalBlock"]:has(.st-key-modo_0) {{ display: grid !important; gap: .75rem !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)); }}
[data-testid="stHorizontalBlock"]:has(.st-key-modo_0) > [data-testid="stColumn"] {{ width: auto !important; min-width: 0 !important; }}
@container principal (max-width: 640px) {{
    [data-testid="stHorizontalBlock"]:has(.st-key-modo_0) {{ grid-template-columns: 1fr; }}
}}
[class*="st-key-modo_"] button p {{ word-break: normal !important; overflow-wrap: normal !important; }}

/* presentación de cada pestaña (style.intro): tarjeta liviana con la frase y la leyenda de colores */
.mc-intro {{ margin: 2px 0 16px; padding: 12px 16px 12px 18px; border-radius: 12px; position: relative;
    background: linear-gradient(90deg, rgba(116,172,223,.10), rgba(116,172,223,.03) 70%);
    border: 1px solid rgba(116,172,223,.18); }}
.mc-intro::before {{ content: ""; position: absolute; left: 0; top: 10px; bottom: 10px; width: 3px; border-radius: 3px;
    background: {CELESTE}; }}
.mc-intro p {{ margin: 0; font-size: 1rem; line-height: 1.55; }}
.mc-intro b {{ color: {CELESTE}; font-weight: 700; }}
.mc-intro .ley {{ display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 8px; font-size: .88rem; font-weight: 600; }}
.mc-intro .ley span {{ display: inline-flex; align-items: center; gap: 8px; opacity: .92; }}
.mc-intro .ley span::before {{ content: ""; width: 9px; height: 9px; border-radius: 50%; background: #8A9BB0; }}
.mc-intro .ley .bien::before {{ background: #10AC84; box-shadow: 0 0 0 3px rgba(16,172,132,.18); }}
.mc-intro .ley .mal::before {{ background: #EE5253; box-shadow: 0 0 0 3px rgba(238,82,83,.18); }}
.mc-intro .nota {{ margin-top: 6px; font-size: .88rem; opacity: .9; }}
html[data-tema="claro"] .mc-intro {{ background: linear-gradient(90deg, #EEF5FC, #F8FBFE 70%); border-color: #D6E5F4; }}
html[data-tema="claro"] .mc-intro::before {{ background: #2E6DB4; }}
html[data-tema="claro"] .mc-intro b {{ color: #2E6DB4; }}
/* botón discreto para ocultarla: una flechita arriba a la derecha. Oculta, queda solo una píldora para volver a abrirla */
.mc-intro {{ padding-right: 46px; }}
.mc-intro .mc-intro-x {{ position: absolute; top: 8px; right: 10px; min-width: 28px; height: 28px; padding: 0 6px;
    display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; cursor: pointer;
    color: {CELESTE}; opacity: .55; font-size: .9rem; font-weight: 700; user-select: none;
    transition: opacity .15s ease, background-color .15s ease; }}
.mc-intro .mc-intro-x::after {{ content: "▴"; font-size: 1rem; line-height: 1; }}
.mc-intro .mc-intro-x:hover, .mc-intro .mc-intro-x:focus-visible {{ opacity: 1; background: rgba(116,172,223,.16); outline: none; }}
/* oculta, queda una píldora para volver a abrirla: círculo con la «i», texto y una flechita */
html[data-intros="ocultas"] .mc-intro {{ display: inline-flex; padding: 0; margin: 0 0 14px; border-radius: 999px;
    background: linear-gradient(135deg, rgba(116,172,223,.18), rgba(116,172,223,.06));
    border: 1px solid rgba(116,172,223,.40); box-shadow: 0 2px 10px rgba(0,0,0,.18);
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease; }}
html[data-intros="ocultas"] .mc-intro:hover {{ transform: translateY(-1px); border-color: rgba(116,172,223,.75);
    box-shadow: 0 6px 16px rgba(74,143,212,.25); }}
html[data-intros="ocultas"] .mc-intro::before, html[data-intros="ocultas"] .mc-intro > p,
html[data-intros="ocultas"] .mc-intro .ley, html[data-intros="ocultas"] .mc-intro .nota {{ display: none; }}
html[data-intros="ocultas"] .mc-intro .mc-intro-x {{ position: static; height: 34px; padding: 0 14px 0 5px; gap: 9px;
    opacity: 1; color: #E6EDF6; font-size: .88rem; font-weight: 700; background: none; }}
html[data-intros="ocultas"] .mc-intro .mc-intro-x::before {{ content: "i"; display: inline-flex; align-items: center;
    justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: .82rem; font-weight: 800;
    font-style: italic; font-family: Georgia, serif; color: #0E1A2B; background: linear-gradient(135deg, #9CC6EC, {CELESTE}); }}
html[data-intros="ocultas"] .mc-intro .mc-intro-x::after {{ content: "Ver presentación  ▾"; font-size: .88rem; white-space: pre; }}
html[data-tema="claro"] .mc-intro .mc-intro-x {{ color: #2E6DB4; }}
html[data-tema="claro"][data-intros="ocultas"] .mc-intro {{ background: linear-gradient(135deg, #EAF2FB, #F7FAFE);
    border-color: #BCD3EC; box-shadow: 0 2px 8px rgba(30,60,100,.10); }}
html[data-tema="claro"][data-intros="ocultas"] .mc-intro .mc-intro-x {{ color: #1F3B5C; }}
html[data-tema="claro"][data-intros="ocultas"] .mc-intro .mc-intro-x::before {{ color: #FFFFFF;
    background: linear-gradient(135deg, #3A7BC0, #2563A8); }}
/* selectores de una sola opción: la elegida no se puede volver a tocar. Streamlit la desmarcaba al instante y recién
   la volvía a marcar al responder el servidor (selector.uno), así que se veía un rato sin nada elegido */
[data-testid="stButtonGroup"] button[role="radio"][aria-checked="true"] {{ pointer-events: none; cursor: default; }}
/* aclaraciones al pie (style.aclaracion): misma tarjeta chica en toda la página, cada fila con su rótulo */
.mc-acl {{ margin: 8px 0 22px; padding: 10px 14px; border-radius: 10px; font-size: .86rem; line-height: 1.55;
    background: rgba(128,128,128,.06); border: 1px solid rgba(128,128,128,.18); }}
.mc-acl .f {{ display: grid; grid-template-columns: 6.4rem 1fr; gap: 12px; align-items: baseline; }}
.mc-acl .f + .f {{ margin-top: 6px; padding-top: 6px; border-top: 1px dashed rgba(128,128,128,.2); }}
.mc-acl .et {{ font-size: .72rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; color: {CELESTE}; }}
.mc-acl .tx {{ opacity: .92; }}
.mc-acl .tx strong {{ font-weight: 700; }}
.mc-acl .ley {{ display: flex; flex-wrap: wrap; gap: 4px 18px; }}
.mc-acl .ley span {{ display: inline-flex; align-items: baseline; gap: 7px; }}
.mc-acl .ley span::before {{ content: ""; flex: 0 0 auto; width: 8px; height: 8px; border-radius: 50%; background: #8A9BB0;
    transform: translateY(-1px); }}
.mc-acl .ley .bien::before {{ background: #10AC84; }}
.mc-acl .ley .mal::before {{ background: #EE5253; }}
html[data-tema="claro"] .mc-acl {{ background: #F6F9FC; border-color: #DCE6F0; }}
@container principal (max-width: 560px) {{
    .mc-acl .f {{ grid-template-columns: 1fr; gap: 2px; }}
}}
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
.mc-min-card .per {{ font-size: .78rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #9CC6EC; }}
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
.st-key-pie_datos {{ position: sticky; bottom: 0; z-index: 90; margin-top: 28px; min-height: 66px; box-sizing: border-box;
    /* (su alto real lo mide JS_PESTANAS y lo guarda en --mc-pie-alto para apoyar la lengüeta ▼ encima) */
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
.mc-pielinks {{ display: flex; flex-wrap: wrap; align-items: center; gap: 2px 16px; font-size: .9rem; white-space: nowrap; }}
.mc-pielinks a {{ color: {CELESTE}; font-weight: 600; text-decoration: none; }}
.mc-pielinks a:hover {{ text-decoration: underline; }}
/* compacto: texto corto, un poco más alto que ancho de relleno, así no se ve como una franja estirada */
.mc-pielinks a.bol {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 13px 6px 11px; border-radius: 999px;
    background: {CELESTE}; color: #0E1A2B; font-weight: 700; line-height: 1.15;
    box-shadow: 0 0 0 0 rgba(116,172,223,.6); animation: mc-resalta 2.6s ease-out infinite; transition: transform .15s ease; }}
.mc-pielinks a.bol:hover {{ text-decoration: none; transform: translateY(-1px); filter: brightness(1.08); }}
@keyframes mc-resalta {{ 0% {{ box-shadow: 0 0 0 0 rgba(116,172,223,.55); }} 70%, 100% {{ box-shadow: 0 0 0 9px rgba(116,172,223,0); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-pielinks a.bol {{ animation: none; }} }}
.mc-pielinks a.bol .ic {{ font-size: .95em; line-height: 1; }}
.mc-pielinks .c {{ opacity: .85; }}
.st-key-pie_datos [data-testid="stPopover"] button {{ white-space: nowrap; }}
.mc-vivo, .mc-vivo span {{ white-space: nowrap; }}
/* lo que entra depende del ancho real de la barra (con la barra lateral abierta es bastante menos que la ventana):
   se va ocultando lo secundario, nunca los botones. Términos y privacidad siguen en «Acerca de» */
.st-key-pie_datos {{ container-type: inline-size; container-name: pie; }}
@container pie (max-width: 1380px) {{ .mc-pielinks .c, .mc-vivo .sec {{ display: none; }} }}
@container pie (max-width: 1040px) {{ .mc-pielinks a:not(.bol) {{ display: none; }} }}
@container pie (max-width: 840px) {{ .mc-vivo span:not(.en) {{ display: none; }} }}
/* angosto (celular): la suscripción sigue a la vista con un texto corto, y los otros dos botones quedan solo con su
   ícono (el texto sigue ahí para los lectores de pantalla) */
.mc-pielinks .bol .s {{ display: none; }}
@container pie (max-width: 660px) {{
    .mc-pielinks .bol .l {{ display: none; }}
    .mc-pielinks .bol .s {{ display: inline; }}
    .st-key-pie_datos button [data-testid="stMarkdownContainer"] {{ position: absolute; width: 1px; height: 1px;
        overflow: hidden; clip-path: inset(50%); white-space: nowrap; }}
    .st-key-pie_datos button {{ padding: .4rem .55rem !important; gap: 0 !important; }}
    .st-key-pie_datos [data-testid="stPopover"] button div[aria-hidden="true"] {{ display: none; }}
    .st-key-pie_datos button [data-testid="stIconMaterial"] {{ font-size: 1.15rem; }}
}}
@container pie (max-width: 430px) {{ .st-key-pie_datos .mc-vivo .en {{ font-size: 0; gap: 0; }} }}
/* en el celular la barra es más baja: entre el encabezado de arriba y esta barra se perdía mucha pantalla */
@media (max-width: 560px) {{ .st-key-pie_datos {{ padding-left: 14px !important; padding-right: 112px !important; gap: 8px !important;
    min-height: 52px; padding-top: 6px; padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px)); margin-top: 18px; }}
    .st-key-pie_datos > :first-child {{ display: none; }} }}
/* el panel «Acerca de»: el contenido del pie, sin marco propio */
[data-testid="stPopoverBody"] .mc-foot {{ margin: 0; padding: 4px 4px 8px; border: none; border-radius: 0; background: none;
    width: min(620px, 80vw); }}
@media (max-width: 560px) {{
    [data-testid="stPopoverBody"] .mc-foot {{ width: auto; }}
    [data-testid="stPopoverBody"] .mc-foot .main {{ grid-template-columns: 1fr; gap: 14px; }}
    [data-testid="stPopoverBody"] .mc-foot .marca p {{ max-width: none; }}
}}
.mc-vivo {{ display: flex; flex-wrap: nowrap; align-items: center; gap: 4px 16px; font-size: .9rem; opacity: .9; }}
.mc-vivo .en {{ display: inline-flex; align-items: center; gap: 6px; font-weight: 800; letter-spacing: .08em;
    text-transform: uppercase; font-size: .78rem; color: #10AC84; }}
.mc-vivo .en::before {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background: #10AC84;
    box-shadow: 0 0 0 0 rgba(16,172,132,.6); animation: mc-latido 2s ease-out infinite; }}
@keyframes mc-latido {{ 0% {{ box-shadow: 0 0 0 0 rgba(16,172,132,.55); }} 100% {{ box-shadow: 0 0 0 8px rgba(16,172,132,0); }} }}
@media (prefers-reduced-motion: reduce) {{ .mc-vivo .en::before {{ animation: none; }} }}
.st-key-pie_datos button {{ min-height: 0 !important; padding: .28rem .8rem .28rem .65rem !important; border-radius: 999px !important;
    border: 1px solid rgba(116,172,223,.45) !important; background: transparent !important; }}
.st-key-pie_datos button p {{ font-size: .9rem !important; font-weight: 700; color: {CELESTE} !important; }}
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
.mc-fx .n {{ font-weight: 800; font-size: 1.05rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
@container (max-width: 170px) {{ .mc-fx .n {{ white-space: normal; }} }}
/* descripción: siempre el alto de dos renglones, así los valores de todas las tarjetas quedan a la misma altura */
.mc-fx .d {{ font-size: .85rem; opacity: .85; line-height: 1.3; min-height: 2.6em; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
/* mismo tamaño de cifra que los indicadores (stMetricValue): 1.85rem en toda la página */
.mc-fx .v {{ font-size: clamp(1.1rem, 9.5cqw, 1.85rem); font-weight: 800; letter-spacing: -.5px; line-height: 1.15; margin: 6px 0 0;
    white-space: nowrap; min-width: 0; }}
.mc-fx .c {{ font-size: .9rem; opacity: .85; margin-bottom: 8px; }}
.mc-fx .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.mc-fx .chip {{ font-size: .88rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; background: rgba(128,128,128,.16); }}
.mc-fx .chip.bien {{ color: #10AC84; background: rgba(16,172,132,.16); }}
.mc-fx .chip.mal {{ color: #EE5253; background: rgba(238,82,83,.16); }}
.mc-fx .chip.flat {{ opacity: .8; }}
/* el valor ocupa su renglón entero y el mini-gráfico va debajo, a todo el ancho: así la cifra puede ser grande en
   cualquier tarjeta sin montarse sobre el gráfico */
.mc-fx .fila {{ display: flex; flex-direction: column; align-items: stretch; gap: 4px; min-width: 0; }}
.mc-fx {{ container-type: inline-size; }}
.mc-fx .spark {{ display: block; width: 100%; height: 26px; opacity: .95; }}

@media (max-width: 640px) {{
    .mc-fx {{ padding: 11px 12px 10px; }}
    .mc-fx .c {{ font-size: .85rem; }}
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
.mc-ticker .copia {{ display: contents; }}  /* la segunda vuelta de la franja (oculta para lectores de pantalla) */
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
.mc-viaje .per {{ font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: #9CC6EC; }}
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
    /* columnas de ancho repartido y celdas que se parten si hace falta: una tabla de cuatro columnas ya no se sale */
    .mc-cmp {{ font-size: .9rem; table-layout: fixed; }}
    .mc-cmp thead th {{ padding: 9px 6px; font-size: .74rem; letter-spacing: 0; overflow-wrap: break-word; }}
    .mc-cmp td {{ padding: 10px 6px; overflow-wrap: break-word; }}
    .mc-cmp th:first-child, .mc-cmp td:first-child {{ width: 31%; hyphens: auto; }}
    /* las tablas anchas (muchas columnas, dentro de .mc-tablas) mantienen su ancho natural y se deslizan de costado */
    .mc-tablas .mc-cmp {{ table-layout: auto; }}
    .mc-tablas .mc-cmp th, .mc-tablas .mc-cmp td {{ white-space: nowrap; }}
    .mc-tablas .mc-cmp th:first-child, .mc-tablas .mc-cmp td:first-child {{ width: auto; white-space: normal;
        min-width: 120px; max-width: 150px; }}  /* el nombre se parte en renglones: así los números entran sin deslizar */
    /* tablas compactas (primera columna corta, como un año): sin ese mínimo, y la letra de abajo un poco menor */
    .mc-tablas.compacta .mc-cmp th:first-child, .mc-tablas.compacta .mc-cmp td:first-child {{ min-width: 0; }}
    .mc-tablas.compacta .mc-cmp td {{ padding: 9px 5px; }}
    .mc-tablas.compacta .mc-cmp td .sub {{ font-size: .74rem; }}
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
html[data-tema="claro"] :is(.mc-min-card, .mc-viaje, .mc-nota, .mc-min-grupo, .mc-fx) :is(.per, .t, small) {{
    color: #1F5F99 !important; }}

[data-testid="stMetric"] {{ border-radius: 14px; transition: border-color .18s ease; }}
[data-testid="stMetric"]:hover {{ border-color: rgba(116,172,223,.55); }}
/* números de los indicadores: más peso y espaciado ajustado, como en los tableros financieros */
[data-testid="stMetricValue"] {{ font-weight: 650 !important; letter-spacing: -.02em; }}
/* un solo tamaño de cifra para todos los indicadores (antes, según la pestaña, 36, 23 o 19 px) */
/* (también el <p> de adentro: la regla general del texto corrido le ponía 1.02rem y la cifra quedaba chica) */
/* la cifra se achica con el ancho de su tarjeta (cqw = % del ancho del indicador): en el celular, «USD 49.709 M» entra */
[data-testid="stMetricValue"] > div, [data-testid="stMetricValue"] p {{
    font-size: clamp(1.15rem, 12.5cqw, 1.85rem) !important; line-height: 1.15; white-space: nowrap; }}
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] p {{ font-size: .95rem !important; }}
[data-testid="stMetricDelta"] {{ margin-top: 4px; padding: 2px 9px !important; }}
[data-testid="stMetricDelta"] svg {{ width: 1rem; height: 1rem; }}
/* indicadores angostos (tres o más por fila con poco ancho): el valor se achica en vez de cortarse con «…» y la
   etiqueta puede ocupar dos renglones */
[data-testid="stMetric"] {{ container-type: inline-size; }}
[data-testid="stMetricLabel"] p {{ white-space: normal !important; overflow: visible !important; line-height: 1.25; }}
@container (max-width: 190px) {{ [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] p {{ font-size: .85rem !important; }} }}
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
[role="tablist"] {{ gap: 6px; align-items: center; padding-bottom: 8px; scrollbar-width: none !important; }}
[role="tablist"]::-webkit-scrollbar {{ display: none !important; }}
/* el bloque que solo trae el script no ocupa lugar (ni el espacio entre elementos) */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > script:only-child) {{ display: none; }}
/* Las flechas tienen carriles propios: nunca ocupan el área de texto desplazable. */
[role="tablist"] {{
    width: calc(100% - 96px) !important; margin-inline: 48px !important; box-sizing: border-box;
}}
[data-testid="stTabsScrollLeft"], [data-testid="stTabsScrollRight"] {{
    position: absolute !important; top: 0 !important; width: 40px !important; height: 3.4rem !important;
    display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 4;
    background: transparent !important;
}}
[data-testid="stTabsScrollLeft"] {{ left: 0 !important; right: auto !important; }}
[data-testid="stTabsScrollRight"] {{ right: 0 !important; left: auto !important; }}
@media (hover: none) {{
    [data-testid="stTabsScrollLeft"], [data-testid="stTabsScrollRight"] {{ display: none !important; }}
    [role="tablist"] {{ width: 100% !important; margin-inline: 0 !important; }}
}}
/* En filas angostas, la píldora fija dejaba sin espacio a los demás marcadores. */
@container principal (max-width: 600px) {{
    [role="tablist"] [data-testid="stTab"]:first-of-type {{ position: relative !important; left: auto !important; }}
}}
[data-testid="stTabsScrollLeft"] svg, [data-testid="stTabsScrollRight"] svg {{
    width: 32px !important; height: 32px !important; padding: 5px; box-sizing: border-box; border-radius: 50%;
    color: {CELESTE}; border: 1px solid rgba(116,172,223,.55);
    /* fondo opaco: sin él, el texto de las pestañas que pasan por debajo se veía a través de la flechita */
    background: linear-gradient(rgba(116,172,223,.16), rgba(116,172,223,.16)), #0E1420;
    box-shadow: 0 2px 10px rgba(0,0,0,.18);
    transition: transform .18s ease, background-color .18s ease, color .18s ease, box-shadow .18s ease;
}}
html[data-tema="claro"] [data-testid="stTabsScrollLeft"] svg, html[data-tema="claro"] [data-testid="stTabsScrollRight"] svg {{
    background: linear-gradient(rgba(116,172,223,.16), rgba(116,172,223,.16)), #FFFFFF; }}
[data-testid="stTabsScrollLeft"]:hover svg, [data-testid="stTabsScrollRight"]:hover svg {{
    background: {CELESTE}; color: #0E1420; transform: scale(1.1); box-shadow: 0 0 0 4px rgba(116,172,223,.22);
}}
[data-testid="stTabsScrollLeft"]:active svg, [data-testid="stTabsScrollRight"]:active svg {{ transform: scale(.94); }}
[data-testid="stTabsScrollLeft"]:focus-visible svg, [data-testid="stTabsScrollRight"]:focus-visible svg {{
    outline: 2px solid {CELESTE}; outline-offset: 2px;
}}
/* Misma altura y eje para todos; el icono de Resumen conserva su espacio propio. */
[data-testid="stTab"] {{
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    box-sizing: border-box; height: 2.8rem; margin-block: .3rem; padding: 0 1.15rem;
}}
[data-testid="stTab"] [data-testid="stMarkdownContainer"] {{ margin: 0; padding: 0; }}
[data-testid="stTab"] p {{
    margin: 0; padding: 0; font-size: 1.15rem; font-weight: 600; line-height: 1.25;
    text-align: center; white-space: nowrap;
}}
/* animación sutil al pasar el cursor por un marcador */
[data-testid="stTab"] {{
    border-radius: 10px 10px 0 0;
    transition: transform .18s ease, background-color .18s ease, box-shadow .18s ease, filter .18s ease;
}}
[data-testid="stTab"] p {{ transition: color .18s ease, letter-spacing .18s ease; }}
[data-testid="stTab"]:hover {{
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
/* fija a la izquierda de la fila: al desplazar las pestañas, «Inicio» queda siempre a mano. (left = su margen
   izquierdo: un valor mayor la corría sobre «Dólar» con la fila sin desplazar) */
[role="tablist"] [data-testid="stTab"]:first-of-type {{
    position: sticky; left: 1.1rem; z-index: 3; height: 2.8rem; margin: .3rem 1.25rem .3rem 1.1rem; padding: 0 1.15rem 0 2.45rem;
    border-radius: 999px; border: 1px solid rgba(116,172,223,.55);
    /* fondo opaco y sombras del color de la página a los costados: tapan las pestañas que pasan por debajo */
    --mc-fondo: #0E1420;
    --mc-tapa: -14px 0 0 7px var(--mc-fondo), 16px 0 0 7px var(--mc-fondo);
    background: linear-gradient(135deg, rgba(116,172,223,.20), rgba(116,172,223,.07)), var(--mc-fondo);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), var(--mc-tapa);
}}
html[data-tema="claro"] [role="tablist"] [data-testid="stTab"]:first-of-type {{ --mc-fondo: #FFFFFF; }}
[role="tablist"] [data-testid="stTab"]:first-of-type p {{ color: {CELESTE} !important; }}
[role="tablist"] [data-testid="stTab"]:first-of-type:hover {{
    border-color: {CELESTE};
    background: linear-gradient(135deg, rgba(116,172,223,.32), rgba(116,172,223,.12)), var(--mc-fondo);
    box-shadow: 0 3px 11px rgba(116,172,223,.25), var(--mc-tapa);
}}
[role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"] {{
    border-color: transparent; background: linear-gradient(135deg, {CELESTE} 0%, #4A8FD4 100%);
    box-shadow: 0 3px 12px rgba(74,143,212,.45), inset 0 1px 0 rgba(255,255,255,.35), var(--mc-tapa);
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
/* línea divisoria: centrada entre «Resumen» y la primera pestaña (con «Inicio», más corta, quedaba bien más cerca) */
[role="tablist"] [data-testid="stTab"]:first-of-type::after {{
    content: ""; position: absolute; right: -22px; top: 15%; height: 70%; width: 1px;
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
        flex: 0 1 calc(50% - .3rem) !important; min-width: calc(50% - .3rem) !important; width: auto !important;
    }}  /* (sin crecer: el quinto indicador, solo en su fila, se estiraba a todo el ancho con la cifra enorme) */
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
    [data-testid="stMetricLabel"] p {{ font-size: .88rem !important; }}
    [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] p {{ font-size: .85rem !important; }}
    /* pestañas y botones más cómodos al tacto */
    [data-testid="stTab"] {{ height: 3rem; padding: 0 .85rem; }}
    [data-testid="stTab"] p {{ font-size: 1rem; }}
    button[data-variant="segmented_control"] {{ padding: .5rem .85rem; }}
    /* tablas anchas: se deslizan de costado en lugar de apretarse */
    [data-testid="stTable"], [data-testid="stDataFrame"] {{ overflow-x: auto; }}
    /* pie de página y fichas en una columna */
    .mc-foot {{ padding: 14px 14px 10px; margin-top: 28px; }}
    .mc-foot .legal {{ flex-direction: column; }}
    .stApp section[data-testid="stSidebar"] .mc-brand .mc-wm {{ font-size: 1.25rem !important; }}
}}

/* Ajustes de legibilidad sobre el diseño existente. */
[data-testid="stTab"][aria-selected="true"] {{
    background-color: rgba(116,172,223,.18); box-shadow: inset 0 -2px 0 #74ACDF;
}}
[data-testid="stTab"] p {{ font-weight: 600; }}
[data-testid="stTab"]:hover {{ box-shadow: inset 0 -2px 0 rgba(116,172,223,.5); }}
[role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"] {{
    box-shadow: inset 0 1px 0 rgba(255,255,255,.22), var(--mc-tapa);
}}
[role="tablist"] [data-testid="stTab"]:first-of-type:hover::before {{ transform: translateY(-50%); }}
.mc-label, .mc-acl .et, .mc-nota .t, .mc-foot .tit {{
    text-transform: none; letter-spacing: .025em; font-weight: 600;
}}
.mc-acl .et {{ font-size: .8rem; }}
.mc-intro b, .mc-panorama b {{ font-weight: 600; }}
[data-testid="stMain"] h3 {{ font-size: 1.35rem; font-weight: 650 !important; }}
[data-testid="stMain"] h4 {{ font-size: 1.12rem; font-weight: 600; }}
.mc-fx, [data-testid="stMetric"] {{ border-radius: 12px; padding: 1rem; }}
.mc-fx {{ transition: border-color .18s ease; }}
.mc-fx:hover {{ transform: none; box-shadow: none; }}
[data-testid="stMetricLabel"] {{ min-height: 2.5em; align-items: flex-start; }}
[data-testid="stMetric"] {{ min-height: 132px; }}
[data-testid="stMetric"] > div {{ padding: 0 !important; }}
.mc-dato-meta {{ display: flex; flex-direction: column; gap: 2px; font-size: .78rem;
    line-height: 1.4; opacity: .85; overflow-wrap: anywhere; margin: -4px 2px 12px; }}
.mc-dato-atrasado {{ color: #F6B40E; font-weight: 600; }}
.mc-fx .mc-dato-meta {{ margin: 10px 0 0; padding-top: 8px; border-top: 1px solid rgba(128,128,128,.2); }}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"]:has(.mc-dato-meta) {{ gap: .75rem; }}
.mc-vivo .en {{ text-transform: none; letter-spacing: 0; font-weight: 600; color: inherit; }}
.mc-vivo .en::before {{ animation: none; box-shadow: none; background: #8A9BB0; }}
.mc-intro .ley .bien::before, .mc-intro .ley .mal::before {{ box-shadow: none; }}
.mc-ticker .pista {{ animation-duration: 85s; }}
@container principal (max-width: 560px) {{
    [data-testid="stHorizontalBlock"]:is(:has(.st-key-personalizar), :has(.st-key-inicio_otro)) {{ flex-wrap: wrap !important; }}
    [data-testid="stHorizontalBlock"]:is(:has(.st-key-personalizar), :has(.st-key-inicio_otro)) > [data-testid="stColumn"]:first-child {{
        flex-basis: 100% !important;
    }}
    [role="tablist"] {{ width: 100% !important; margin-inline: 0 !important; scroll-padding-inline: 8px; }}
    [data-testid="stTabsScrollLeft"], [data-testid="stTabsScrollRight"] {{ display: none !important; }}
    [data-testid="stTab"], [role="tablist"] [data-testid="stTab"]:first-of-type {{
        height: 2.8rem; margin-block: .3rem; min-height: 44px;
    }}
    [role="tablist"] [data-testid="stTab"]:first-of-type {{ margin-left: .35rem; margin-right: .65rem; }}
    [role="tablist"] [data-testid="stTab"]:first-of-type::after {{ display: none; }}
    [data-testid="stTab"] {{ padding-inline: .85rem; }}
    [data-testid="stTab"] p {{ font-size: 1rem; }}
    .mc-dato-meta {{ font-size: .76rem; }}
    .mc-fx .n {{ overflow-wrap: anywhere; }}
    .mc-acl .f {{ grid-template-columns: 1fr; gap: 4px; }}
    .mc-intro {{ padding-left: 14px; }}
    [data-testid="stMain"] h3 {{ font-size: 1.2rem; }}
}}
@media (max-width: 380px) {{
    [data-testid="stMetric"] {{ padding: .65rem !important; }}
    [data-testid="stMetricLabel"] p {{ font-size: .82rem !important; }}
    [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] p {{ font-size: .78rem !important; }}
}}

.mc-tabla-scroll {{ width: 100%; max-width: 100%; overflow-x: auto; overscroll-behavior-x: contain; }}
.mc-tabla-scroll:focus-visible {{ outline: 2px solid #74ACDF; outline-offset: 3px; }}
.mc-tabla-scroll .mc-cmp {{ margin-block: 4px; }}
.mc-tabla-scroll .mc-cmp th {{ white-space: normal; }}
.mc-tabla-scroll .mc-cmp td:not(:first-child) {{ white-space: nowrap; }}
@container principal (max-width: 560px) {{
    .mc-tabla-ancha .mc-cmp {{ min-width: 540px; }}
    .mc-tabla-scroll .mc-cmp th, .mc-tabla-scroll .mc-cmp td {{ padding: 10px 12px; }}
    .mc-acl .f {{ grid-template-columns: 1fr; gap: 3px; }}
    button[data-variant="segmented_control"], [role="radio"] {{ min-height: 44px; }}
}}

@container principal (max-width: 480px) {{
    :is(.st-key-hist_seccion, .st-key-inv_seccion) [data-testid="stButtonGroup"] > div {{
        display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px !important;
    }}
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button:last-child {{ grid-column: 1 / -1; }}
    :is(.st-key-hist_seccion, .st-key-inv_seccion) button p {{
        overflow-wrap: normal !important; word-break: normal !important; font-weight: 600;
    }}
}}
/* Acceso compacto a todas las secciones, en la misma fila que el carrusel. */
.st-key-navegacion_tablero {{ position: relative; gap: 0 !important; }}
.st-key-navegacion_tablero .st-key-pestana [role="tablist"] {{
    width: calc(100% - 148px) !important; max-width: calc(100% - 148px); min-width: 0;
}}
@container principal (max-width: 560px) {{
    .st-key-navegacion_tablero .st-key-pestana [role="tablist"] {{
        width: calc(100% - 52px) !important; max-width: calc(100% - 52px);
    }}
}}
@media (hover: none) {{
    .st-key-navegacion_tablero .st-key-pestana [role="tablist"] {{
        width: calc(100% - 52px) !important; max-width: calc(100% - 52px); margin-inline: 0 !important;
    }}
}}
.st-key-navegacion_tablero [data-testid="stTabsScrollRight"] {{ right: 52px !important; }}
.st-key-menu_secciones {{ position: absolute !important; right: 0; top: 9px; width: 40px !important; z-index: 5; }}
.st-key-menu_secciones [data-testid="stPopoverButton"] {{
    width: 40px; min-width: 40px; height: 40px; min-height: 40px; padding: 8px;
    border: 0; border-radius: 10px; background: transparent; color: inherit;
    opacity: .75; box-shadow: none;
}}
.st-key-menu_secciones [data-testid="stPopoverButton"]:is(:hover, [aria-expanded="true"]) {{
    background: rgba(116,172,223,.14); opacity: 1;
}}
.st-key-menu_secciones button p {{
    position: absolute; width: 1px; height: 1px; clip-path: inset(50%); overflow: hidden; white-space: nowrap;
}}
.st-key-menu_secciones button > div > div[aria-hidden="true"] {{ display: none; }}
.st-key-menu_secciones button [data-testid="stIconMaterial"] {{ font-size: 21px; }}

/* Auditoría móvil: blancos táctiles y cifras completas en pantallas pequeñas o táctiles. */
@media (max-width: 640px), (pointer: coarse) {{
    .stApp button:not([role="switch"]):not([role="checkbox"]),
    .stApp [role="radio"], .stApp input:not([type="checkbox"]):not([type="range"]) {{
        min-height: 44px;
    }}
    .stApp summary {{ min-height: 44px; box-sizing: border-box; }}
    .st-key-menu_secciones {{ width: 44px !important; top: 9px; }}
    .st-key-menu_secciones [data-testid="stPopoverButton"] {{ width: 44px; min-width: 44px; min-height: 44px; }}
    [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button {{
        width: 44px !important; height: 44px !important;
    }}
    .st-key-pie_datos button, .mc-pielinks a.bol {{ min-width: 44px !important; min-height: 44px !important; box-sizing: border-box; }}
    .mc-pie-btn, html[data-tema="claro"] .mc-pie-btn {{
        min-width: 44px; min-height: 44px; align-items: flex-end; padding-bottom: 4px;
        background: transparent !important; border: 0 !important; box-shadow: none !important;
    }}
    .mc-pie-btn::before {{
        content: ""; position: absolute; inset: 22px 0 0; z-index: -1;
        border-radius: 10px 10px 0 0; border: 1px solid rgba(116,172,223,.6); border-bottom: 0;
        background: #16263b;
    }}
    html[data-tema="claro"] .mc-pie-btn::before {{ background: #E9F1FA; }}
    [data-testid="stTooltipIcon"] button {{ min-width: 32px; min-height: 32px; }}
    [data-testid="stSlider"] {{ padding: 8px 16px; }}
    [data-testid="stSlider"] [data-rac]:has(> div > input[type="range"]) {{
        width: 44px; height: 44px; box-sizing: border-box;
        border: 10px solid transparent; background-clip: padding-box;
    }}
    [data-testid="stMetricValue"] > div, [data-testid="stMetricValue"] p {{
        white-space: normal !important; overflow: visible !important; text-overflow: clip !important;
    }}
    .mc-intro .mc-intro-x {{ min-width: 44px; min-height: 44px; top: 0; right: 0; }}
}}
@media (max-width: 360px) {{
    .mc-pielinks .bol .s {{ display: none; }}
    .mc-pielinks a.bol {{ justify-content: center; padding-inline: 10px; }}
}}
@container principal (max-width: 340px) {{
    .stApp [data-testid="stHorizontalBlock"]:is(:has([data-testid="stMetric"]),
        :has(> [data-testid="stColumn"]:nth-child(4):last-child [data-testid="stMetric"])) > [data-testid="stColumn"] {{
        flex: 1 1 100% !important; min-width: 100% !important; width: 100% !important;
    }}
}}

/* Lista de navegación táctil: todos los destinos siguen accesibles en horizontal. */
[data-testid="stPopoverBody"]:has(.mc-menu-secciones) {{
    max-height: min(560px, calc(100dvh - 96px)); overflow-y: auto; overscroll-behavior: contain;
}}
.mc-menu-secciones {{ display: flex; flex-direction: column; gap: 2px; min-width: min(240px, 70vw); }}
.mc-menu-secciones a {{
    display: flex; align-items: center; min-height: 44px; padding: 8px 12px; border-radius: 8px;
    box-sizing: border-box; color: inherit; text-decoration: none; line-height: 1.4;
}}
.mc-menu-secciones a:is(:hover, [aria-current="page"]) {{ background: rgba(116,172,223,.15); }}
.mc-menu-secciones a[aria-current="page"] {{ font-weight: 700; }}

/* Fichas y navegación accesibles en ambos temas. */
.mc-ficha {{ margin-top: 4px; }}
.mc-ficha summary {{ cursor: pointer; padding: 6px 0; font-weight: 600; line-height: 1.5; }}
.mc-ficha dl {{ margin: 8px 0; }}
.mc-ficha dt {{ font-weight: 700; margin-top: 8px; }}
.mc-ficha dd {{ margin: 2px 0 8px; line-height: 1.5; }}
.stApp :is(a, button, input, select, textarea, summary, [tabindex]):focus-visible {{
    outline: 3px solid #74ACDF !important; outline-offset: 3px !important;
}}
html[data-tema="claro"] .stApp :is(a, button, input, select, textarea, summary, [tabindex]):focus-visible {{
    outline-color: #245E94 !important;
}}
.mc-dato-meta {{ opacity: 1; color: #BAC8D8; font-size: .82rem; }}
.mc-pano .tema a {{ color: inherit; text-decoration: underline; text-underline-offset: 3px; }}
.choroplethlayer path.choroplethlocation {{ stroke: #BAC8D8 !important; }}
html[data-tema="claro"] .choroplethlayer path.choroplethlocation {{ stroke: #41536A !important; }}
html[data-tema="claro"] .mc-dato-meta {{ color: #41536A; }}
html[data-tema="claro"] .mc-dato-atrasado {{ color: #775000; }}
@media (prefers-reduced-motion: reduce) {{
    .stApp *, .stApp *::before, .stApp *::after {{
        animation: none !important; transition: none !important; scroll-behavior: auto !important;
    }}
    [data-testid="stSidebarUserContent"], [data-testid="stMainBlockContainer"] {{ opacity: 1 !important; }}
}}
</style>
"""


def _minificar_css(css: str) -> str:
    """Saca comentarios y espacios de sobra (el CSS viaja en cada carga): ~25% menos de bytes, mismas reglas.
    Las comillas («content: "$"», data URIs) se respetan."""
    # los comentarios primero y en todo el texto: si un comentario tenía comillas, antes quedaba sin sacar
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    partes = re.split(r'("[^"]*"|\'[^\']*\')', css)  # los textos entre comillas no se tocan...
    for i in range(0, len(partes), 2):
        p = re.sub(r"\s+", " ", partes[i])
        partes[i] = re.sub(r"\s*([{};,>])\s*", r"\1", p)
    for i in range(1, len(partes), 2):  # ...salvo los íconos SVG (data URI): sus < y > van codificados, porque el
        if partes[i][1:].startswith("data:"):  # saneador de st.html descarta una hoja con «<algo» adentro
            partes[i] = partes[i].replace("<", "%3C").replace(">", "%3E")
    return "".join(partes).replace(";}", "}").strip()


CSS = _minificar_css(CSS)

# Tema claro: los colores de texto pensados para fondo oscuro (celeste, verde, rojo y dorado) se leen mal sobre blanco
# (contraste de 2 a 1, cuando lo recomendado es 4,5 a 1). En vez de repetir cada regla a mano, se arma su versión clara:
# para cada regla de primer nivel que pinta el TEXTO de uno de esos colores, la misma regla con un tono más oscuro bajo
# html[data-tema="claro"]. Se saltean las reglas que además ponen un fondo oscuro propio (ahí el color claro va bien).
CLARO_TEXTO = {CELESTE.lower(): "#2563A8", "#10ac84": "#08805F", "#ee5253": "#C62828", SOL.lower(): "#8A5A00",
               "#f79f1f": "#9A5B00", "#2ed3a0": "#08805F"}


def _version_clara(css: str) -> str:
    cuerpo = css[len("<style>"):-len("</style>")] if css.startswith("<style>") else css
    reglas, nivel, inicio, i = [], 0, 0, 0
    while i < len(cuerpo):
        ch = cuerpo[i]
        if ch == "{":
            if nivel == 0:
                sel, sel_ini = cuerpo[inicio:i], i + 1
            nivel += 1
        elif ch == "}":
            nivel -= 1
            if nivel == 0:
                if not sel.lstrip().startswith("@"):
                    reglas.append((sel.strip(), cuerpo[sel_ini:i]))
                inicio = i + 1
        i += 1
    out = []
    for sel, decl in reglas:
        if "data-tema" in sel or "-hero" in sel:  # los encabezados con fondo oscuro propio quedan como están
            continue
        m = re.search(r"(?:^|;)\s*color:\s*(#[0-9a-fA-F]{6})\s*(!important)?", decl)
        if not m or m.group(1).lower() not in CLARO_TEXTO:
            continue
        fondo = re.search(r"background(?:-color)?:\s*(#[0-9a-fA-F]{6})", decl)
        if fondo and sum(int(fondo.group(1)[k:k + 2], 16) for k in (1, 3, 5)) < 3 * 90:
            continue  # fondo oscuro propio: el color claro sigue estando bien
        nuevo = CLARO_TEXTO[m.group(1).lower()] + (" !important" if m.group(2) else "")
        sels = ",".join(f'html[data-tema="claro"] {x.strip()}' for x in sel.split(","))
        out.append(f"{sels}{{color:{nuevo}}}")
    return "<style>" + cuerpo + "".join(out) + "</style>"


CSS = _version_clara(CSS)

# «En pocas palabras» trae su propio estilo (va dentro del mismo bloque que el informe): en el celular, la primera vez,
# el informe podía dibujarse un par de segundos antes que la hoja general y se veía sin formato.
ESTILO_PANO = _version_clara(_minificar_css("<style>" + r"""/* informe "En pocas palabras" de Inicio: neutral (no califica nada como bueno o malo). Título como los demás títulos
   de sección (barra celeste), filas numeradas separadas por líneas finas, misma letra que el resto de la página */
.mc-pano { margin: 6px 0 10px; counter-reset: pano; }
.mc-pano .cab { padding: 4px 0 12px; border-bottom: 1px solid rgba(128,128,128,.35); }
.mc-pano .cab .tit { font-size: 1.5rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.25;
    border-left: 4px solid #74ACDF; padding-left: 12px; }
.mc-pano .cab .sub { font-size: .84rem; opacity: .85; margin: 4px 0 0 16px; }
.mc-pano .fila { display: grid; grid-template-columns: 2.1rem 150px 1fr; gap: 18px; align-items: baseline;
    padding: 15px 2px; counter-increment: pano; }
.mc-pano .fila + .fila { border-top: 1px solid rgba(128,128,128,.2); }
.mc-pano .fila::before { content: counter(pano, decimal-leading-zero); font-size: .9rem; font-weight: 700;
    color: #74ACDF; opacity: .8; font-variant-numeric: tabular-nums; }
.mc-pano .tema { font-size: .8rem; font-weight: 600; opacity: .85; }
.mc-pano .cifra { font-size: 1.45rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.15;
    font-variant-numeric: tabular-nums; margin: 1px 0; }
.mc-pano .det { font-size: .78rem; opacity: .85; }
.mc-pano .txt { font-size: .94rem; line-height: 1.6; }
.mc-pano .txt strong, .mc-pano .txt :is(.pos, .neg) { font-weight: 700; color: inherit; }
.mc-pano .pie { font-size: .78rem; opacity: .85; padding: 10px 0 0; border-top: 1px solid rgba(128,128,128,.35); }
@container principal (max-width: 640px) {
    .mc-pano .fila { grid-template-columns: 1.8rem 1fr; gap: 4px 10px; padding: 13px 0; }
    .mc-pano .izq { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
    .mc-pano .txt { grid-column: 2; font-size: .9rem; }
    .mc-pano .cifra { font-size: 1.15rem; }
    .mc-pano .cab .tit { font-size: 1.3rem; }
}""" + "</style>"))
# ajustes del tema claro que la regla automática no cubre (o que pisaría mal)
CSS = CSS.replace("</style>", (
    'html[data-tema="claro"] .mc-pielinks a.bol{color:#0E1A2B}'  # botón celeste relleno: el texto sigue oscuro
    'html[data-tema="claro"] .mc-foot .bol a{color:#0E1A2B}'
    # etiquetas de fuente de las noticias (gris y violeta claros: sobre blanco no se leían)
    'html[data-tema="claro"] .mc-news .tag.economia{color:#3D4F66;background:rgba(61,79,102,.12)}'
    'html[data-tema="claro"] .mc-news .tag.indec{color:#5B3A9E;background:rgba(91,58,158,.12)}'
    'html[data-tema="claro"] .mc-news-pie{opacity:1}'
    'html[data-tema="claro"] .mc-foot a.mc-linkedin:hover{color:#fff}'
    'html[data-tema="claro"] section[data-testid="stSidebar"] .mc-label{opacity:1}'
    'html[data-tema="claro"] [class*="st-key-per_"] button[data-variant="pills"][aria-checked="true"] p{color:#7A4F00 !important}'
    'html[data-tema="claro"] [class*="st-key-gtit_"] [data-testid="stDownloadButton"] button{opacity:.8}'
    # «Resumen» elegida: texto oscuro sobre la píldora celeste (la regla automática lo pasaba a azul y no se leía)
    'html[data-tema="claro"] [role="tablist"] [data-testid="stTab"]:first-of-type[aria-selected="true"] p{color:#0B1A2E !important}'
    # variaciones de los indicadores (colores de Streamlit): un poco más oscuras sobre blanco
    'html[data-tema="claro"] [data-testid="stMetricDelta"]{filter:brightness(.72) saturate(1.15)}'
    # barra inferior y su lengüeta: claras en el tema claro (antes quedaban azul oscuro)
    'html[data-tema="claro"] .st-key-pie_datos{background:color-mix(in srgb,#FFFFFF 90%,#74ACDF 10%);border-top-color:#2563A8}'
    'html[data-tema="claro"] .mc-pie-btn{background:#E9F1FA;color:#2563A8;border-color:#9DBEE0;box-shadow:0 -2px 6px rgba(30,60,100,.12)}'
    "</style>"))
