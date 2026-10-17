"""Pestaña «Inicio» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import traceback

import pandas as pd
import streamlit as st

from macrocenter import catalogo, charts, datos_vista, style


def _ult(df: pd.DataFrame | None, col: str = "valor") -> float | None:
    """Último dato válido de la serie (None si no hay serie o está vacía)."""
    if df is not None and col in df:
        d = df.dropna(subset=[col])
        if not d.empty:
            return float(d[col].iloc[-1])
    return None


DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


# feriados de Argentina: si está la librería holidays se usa su calendario (reglas y decretos al día); si no,
# un recorte nativo espejo. Los fijos quedan como par (mes, día); las móviles (Carnaval y Viernes Santo según
# las Pascuas) y los trasladables (Güemes, San Martín, Diversidad y Soberanía saltan al lunes vecino) más los
# puentes con fines turísticos y el feriado extraordinario de la visita papal (9/11/26) van como fechas exactas
# de 2026 y 2027. El Día del Bancario (6/11) va con los fijos aunque cierre solo el sistema bancario.
try:
    import holidays as _holidays
except ImportError:
    _holidays = None
_FERIADOS_FIJOS = {(1, 1), (3, 24), (4, 2), (5, 1), (5, 25), (7, 9), (11, 6), (12, 8), (12, 25)}
_FERIADOS_2026_27 = {"2026-02-16", "2026-02-17", "2026-03-23", "2026-04-03", "2026-06-15", "2026-07-10",
                     "2026-11-09", "2026-11-23", "2026-12-07",
                     "2027-02-08", "2027-02-09", "2027-03-26", "2027-06-21", "2027-08-16", "2027-10-11"}


def _feriado(ts: pd.Timestamp) -> bool:
    """¿Es feriado nacional (con el Día del Bancario incluido)? Mezcla la librería si está con el recorte nativo."""
    f = ts.date()
    try:
        if _holidays is not None and f in _holidays.country_holidays("AR", years=f.year):
            return True
    except Exception:  # noqa: BLE001
        pass
    return (f.month, f.day) in _FERIADOS_FIJOS or f.isoformat() in _FERIADOS_2026_27


def _estado(ts: pd.Timestamp) -> str:
    """Píldora de estado del encabezado de Inicio (al lado del título): verde con pulso rápido mientras rueda
    el mercado (lunes a viernes de 11 a 17 hs, hora argentina, salvo feriado) y rojo con pulso lento el resto
    del tiempo. La fecha que muestra es siempre la de hoy: en fin de semana o feriado no retrocede al viernes."""
    w = ts.weekday()
    hoy = f"{DIAS[w]} {ts.day:02d}/{ts.month:02d}"
    if w < 5 and 11 <= ts.hour < 17 and not _feriado(ts):
        return ('<span class="mc-estado"><span class="mc-status-dot open"></span>'
                f'Mercado abierto · {hoy}</span>')
    return ('<span class="mc-estado"><span class="mc-status-dot closed"></span>'
            f'Mercado cerrado · {hoy}</span>')


def mostrar(
    *, CATALOGO, badlar, brecha_df, dol_s, emae_ia, emae_m, emae_sa, haber_min, HOY, infl_ia, infl_m, kpi, MESES_ES,
    paro_pct, pases, rem, reservas, ripte, riesgo, sal_ia, sal_real_df, smvm, uva, cargar_mercados,
) -> None:
    # el estado de sesión puede traer claves viejas o inválidas: se filtra antes de dibujar el selector
    previos = st.session_state.get("kpis_sel")
    st.session_state["kpis_sel"] = [k for k in (previos if isinstance(previos, list) else [])
                                    if isinstance(k, str) and k in CATALOGO]
    st.markdown(style.titulo("Indicadores clave", estado=_estado(
        pd.Timestamp.now(tz="America/Argentina/Buenos_Aires").tz_localize(None))), unsafe_allow_html=True)
    # la personalización de «Indicadores clave» se sacó de la pantalla: siempre los de siempre
    # (igual a KPIS_DEFECTO en app.py; el estado en sesión ya trae esas claves o las guardadas antes)
    POR_DEFECTO = ("oficial", "riesgo", "reservas", "infl_m", "emae_m")
    # «los de siempre»: la personalización se quitó de la pantalla; el estado o el archivo guardado no manda más
    elegidos = [k for k in POR_DEFECTO if k in CATALOGO]
    # el Merval entra como sexta tarjeta si la serie del mercado está (la misma que alimenta el ticker de arriba):
    # valor = variación del día (el nivel absoluto del índice no dice nada por sí solo), como «Actividad mensual»
    merval = None
    try:
        mk = cargar_mercados()
        dfm = mk.get("^MERV") if isinstance(mk, dict) else None
        if isinstance(dfm, pd.DataFrame) and len(dfm) >= 3:
            serie_m = dfm["valor"].astype(float)
            var = (serie_m.iloc[-1] / serie_m.iloc[-2] - 1) * 100 if serie_m.iloc[-2] else None
            var_prev = (serie_m.iloc[-2] / serie_m.iloc[-3] - 1) * 100 if serie_m.iloc[-3] else None
            if var is not None and var_prev is not None:
                merval = dict(var=var, d=var - var_prev)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    # el contenedor con clave permite achicar estas tarjetas por CSS sin tocar las de las demás secciones
    # dos filas de tres (fila 1: Dólar oficial, Riesgo país, Reservas; fila 2: Inflación mensual, Actividad,
    # Merval): con las seis en una sola fila las tarjetas quedaban asfixiadas de ancho
    piezas = list(elegidos) + (["merval"] if merval else [])
    with st.container(key="tarjetas_resumen"):
        for i in range(0, len(piezas), 3):
            for slot, clave in zip(st.columns(3), piezas[i:i + 3]):
                try:
                    if clave == "merval":
                        kpi(slot, "Merval", merval["var"], dec=1, suf="%", d=merval["d"], d_suf=" pp",
                            d_txt="vs día ant.", color="normal",
                            help="S&P Merval: variación del día contra la rueda anterior (BYMA).",
                            ruta="?ver=tablero/bolsas")
                    else:
                        # sin el pie de datos (fuente, último dato y ficha): la tarjeta queda solo con el número y la variación
                        args = CATALOGO[clave][2]()
                        for recortar in ("fuente", "serie", "max_dias"):
                            args.pop(recortar, None)
                        kpi(slot, CATALOGO[clave][1], ruta=catalogo.ruta(clave, CATALOGO[clave][0]), **args)
                except Exception:  # noqa: BLE001
                    traceback.print_exc()
                    if clave != "merval":
                        kpi(slot, CATALOGO[clave][1], None)

    # «En pocas palabras»: una fila por cada tarjeta, con el número, el nombre de la sección y la historia del dato
    ROTULO = {"Dólar": "Dólar", "Precios": "Inflación", "Ingresos": "Salarios", "Tasas": "Tasas", "Actividad": "Actividad",
              "Sector externo": "Reservas"}

    def historia(clave: str) -> tuple[str, str]:
        """(rótulo, texto html) del resumen de una tarjeta. Los valores salen de las series ya cargadas."""
        grupo, nombre = CATALOGO[clave][0], CATALOGO[clave][1]
        rotulo = {"riesgo": "Riesgo país", "paro": "Desempleo", "brecha": "Dólar"}.get(clave) or ROTULO.get(grupo, nombre)
        if clave in ("oficial", "blue", "mep", "ccl", "brecha"):
            of, bl = _ult(dol_s.get("oficial")), _ult(dol_s.get("blue"))
            if of and bl:
                br = (bl / of - 1) * 100
                if br > 0.05:
                    t = f"El blue cotiza <b>{charts.num(br, 1, '%')} por encima del oficial</b>. "\
                        "Esta brecha compara precios de venta; no incluye impuestos ni comisiones."
                elif br < -0.05:
                    t = f"El blue cotiza <b>{charts.num(-br, 1, '%')} por debajo del oficial</b>. "\
                        "Esta brecha compara precios de venta; no incluye impuestos ni comisiones."
                else:
                    t = "El blue cotiza <b>igual que el oficial</b>. "\
                        "Esta brecha compara precios de venta; no incluye impuestos ni comisiones."
                return rotulo, t
        if clave == "riesgo" and (v := _ult(riesgo)) is not None:
            return rotulo, (f"El riesgo país cierra en <b>{charts.num(v, 0)} pb</b>: el diferencial que pide el mercado "
                            "por la deuda argentina frente a los bonos del Tesoro de EE. UU. (100 pb = 1 pp).")
        if clave == "reservas" and (v := _ult(reservas)) is not None:
            return rotulo, (f"El Banco Central acumula <b>USD {charts.num(v, 0)} M</b> de reservas brutas; el número "
                            "no equivale a las reservas netas disponibles para intervenir.")
        if clave == "infl_m" and (v := _ult(infl_m)) is not None:
            s = infl_m.sort_values("fecha").dropna(subset=["valor"])
            mes = MESES_ES[int(s["fecha"].iloc[-1].month) - 1]
            return rotulo, (f"La inflación de {mes} fue <b>{charts.num(v, 1, '%')}</b> "
                            "(variación del IPC nacional respecto del mes anterior).")
        if clave == "rem":
            obs, esp = _ult(infl_ia), _ult(rem)
            if obs is not None and esp is not None:
                dif = "menos" if esp < obs - 1 else "más" if esp > obs + 1 else "casi la misma"
                return rotulo, (f"El REM anticipa <b>{dif} inflación que en los últimos 12 meses</b>: compara una "
                                "expectativa a 12 meses con la observada; no es un resultado confirmado.")
            return rotulo, "Expectativa de inflación a 12 meses relevada en el REM del BCRA; es una expectativa, no inflación observada."
        if clave == "emae_m" and (v := _ult(emae_m)) is not None:
            return rotulo, (f"La actividad económica varió <b>{charts.num(v, 1, '%')}</b> en el mes "
                            "(EMAE desestacionalizado, INDEC; la serie puede revisarse).")
        if clave == "emae" and (v := _ult(emae_ia)) is not None:
            return rotulo, (f"La actividad económica varió <b>{charts.num(v, 1, '%')}</b> frente al mismo mes del "
                            "año anterior (EMAE del INDEC, sin desestacionalizar).")
        if clave == "paro" and (v := _ult(paro_pct)) is not None:
            return rotulo, (f"La desocupación quedó en <b>{charts.num(v, 1, '%')}</b> (EPH del INDEC, 31 aglomerados "
                            "urbanos; medición trimestral).")
        if clave == "sal_nom" and (v := _ult(sal_ia)) is not None:
            return rotulo, (f"Los salarios nominales variaron <b>{charts.num(v, 1, '%')}</b> frente al mismo mes del "
                            "año anterior (Índice de salarios del INDEC).")
        if clave == "ripte" and (v := _ult(ripte)) is not None:
            return rotulo, (f"El RIPTE promedio quedó en <b>${charts.num(v, 0)}</b> (remuneración imponible "
                            "promedio de trabajadores estables).")
        if clave == "smvm" and (v := _ult(smvm)) is not None:
            return rotulo, f"El salario mínimo es <b>${charts.num(v, 0)}</b> por mes a jornada completa."
        if clave == "haber" and (v := _ult(haber_min)) is not None:
            return rotulo, (f"El haber mínimo jubilatorio es <b>${charts.num(v, 0)}</b> por mes, sin bonos "
                            "extraordinarios.")
        if clave == "badlar" and (v := _ult(badlar)) is not None:
            return rotulo, (f"El plazo fijo en bancos privados paga <b>{charts.num(v, 1, '%')}</b> anual nominal "
                            "(BADLAR); no es una tasa efectiva.")
        if clave == "pases" and (v := _ult(pases)) is not None:
            return rotulo, (f"La tasa de pases a un día quedó en <b>{charts.num(v, 1, '%')}</b> (BCRA; puede ser "
                            "una serie discontinuada).")
        if clave == "uva" and (v := _ult(uva)) is not None:
            return rotulo, (f"La UVA costaba <b>${charts.num(v, 2)}</b>: se ajusta con el CER, que sigue la "
                            "inflación con rezago.")
        if clave == "salario_real" and sal_real_df is not None and not sal_real_df.dropna(subset=["real"]).empty:
            s = sal_real_df.dropna(subset=["real"])
            u = s.iloc[-1]
            val, mes = float(u["real"]), MESES_ES[int(u["fecha"].month) - 1]
            comp = "compraba lo mismo" if abs(val) < 0.5 else \
                f"compraba <b>{charts.num(abs(val), 1, '%')} {'más' if val > 0 else 'menos'} que un año antes</b>"
            return rotulo, (f"En {mes}, el salario promedio {comp}. La comparación descuenta la inflación y "
                            "corresponde al índice general, no a cada trabajador.")
        definicion = (datos_vista.FICHAS.get(nombre, ("", "", ""))[2] or "").strip()
        if definicion:
            return rotulo, definicion
        return rotulo, f"Último dato de <b>{nombre}</b>, según la fuente publicada."

    filas = []
    for i, clave in enumerate(elegidos):
        try:
            rotulo, texto = historia(clave)
            filas.append(dict(num=f"{i + 1:02d}", nombre=rotulo, href=catalogo.ruta(clave, CATALOGO[clave][0]), texto=texto))
        except Exception:  # noqa: BLE001
            traceback.print_exc()
    if merval:
        fila = (f"El Merval varió <b>{charts.num(merval['var'], 1, '%')}</b> en el día "
                "(S&P Merval de BYMA: agrupa a las principales acciones argentinas y se mide en pesos).")
        filas.append(dict(num=f"{len(filas) + 1:02d}", nombre="Merval", href="?ver=tablero/bolsas", texto=fila))
    if filas:
        # el resumen va en dos columnas (01-03 | 04-06): a todo el ancho del monitor se hacía difícil de leer
        st.markdown(style.pocas_titulo("Síntesis de las variables clave"), unsafe_allow_html=True)
        pp_izq, pp_der = st.columns(2, gap="large")
        with pp_izq:
            st.markdown(style.pocas_items(filas[:3]), unsafe_allow_html=True)
        with pp_der:
            st.markdown(style.pocas_items(filas[3:]), unsafe_allow_html=True)
        st.markdown(style.pocas_pie(), unsafe_allow_html=True)
    # los gráficos de la vista tienen su propio encabezado, con la misma pieza que las demás secciones
    st.markdown(style.titulo("Gráficos destacados"), unsafe_allow_html=True)

    fila1_izq, fila1_der = st.columns(2)
    fila2_izq, fila2_der = st.columns(2)

    def tunear(fig):
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None
        )
        
        meses = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun", 
                 7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}
        
        try:
            x_data = fig.data[0].x
            s = pd.to_datetime(pd.Series(x_data))
            
            # Si hay más de 30 datos, es una serie diaria (Riesgo País / Reservas)
            if len(s) > 30:
                ticks = s.groupby([s.dt.year, s.dt.month]).first()
                ticks = ticks.iloc[-12:]  # Recortamos el mes incompleto
                tick_vals = ticks.values
                tick_texts = [f"{meses[d.month]} {d.year}" for d in ticks]
            
            # Si son 30 datos o menos, es una serie mensual (Inflación / EMAE)
            else:
                tick_vals = x_data  # Usamos las coordenadas exactas de las barras
                tick_texts = [f"{meses[d.month]} {d.year}" for d in s]
                
            fig.update_xaxes(
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_texts,
                tickangle=-45
            )
        except Exception:
            pass

        # eje de valores: un poco más de marcas que el automático (que deja 4 o 5) para leer el nivel de un vistazo;
        # en los de línea (Riesgo, Reservas), con rangos largos, hace falta pedir más para que Plotly no salte de a 200
        fig.update_yaxes(nticks=10 if (fig.data and fig.data[0].type == 'scatter') else 8)

        return fig
    # 1. Riesgo país
    with fila1_izq:
        st.metric("[Riesgo país (pb)](?ver=tablero/tasas)", "", help="Termómetro del riesgo financiero asociado a los bonos soberanos.")
        if riesgo is not None and not riesgo.empty:
            f_min = riesgo["fecha"].max() - pd.Timedelta(days=365)
            df_rie = riesgo[riesgo["fecha"] >= f_min].dropna(subset=["valor"])
            fig_rie = charts.lineas(df_rie, {"Riesgo país": "valor"}, "", height=210, yfmt=",.0f")
            # Agregamos "locale": "es" para que los meses salgan en español
            st.plotly_chart(tunear(fig_rie), use_container_width=True, config={"displayModeBar": False, "locale": "es"})

    # 2. Inflación mensual (Sube = rojo, baja = verde)
    with fila1_der:
        st.metric("[Inflación mensual](?ver=tablero/dinero)", "", help="Variación porcentual del IPC. En rojo si la inflación aceleró respecto al mes anterior; en verde si desaceleró o se mantuvo.")
        if infl_m is not None and not infl_m.empty:
            df_inf_full = infl_m.sort_values("fecha").dropna(subset=["valor"]).copy()
            df_inf_full["dif_mes"] = df_inf_full["valor"].diff()
            
            f_min = df_inf_full["fecha"].max() - pd.Timedelta(days=365)
            df_inf = df_inf_full[df_inf_full["fecha"] >= f_min]
            
            fig_inf = charts.barras(df_inf, "valor", "", height=210, yfmt=",.1f", etiquetas=True, sufijo_hover="%")
            
            colores = ["#ff4b4b" if d > 0 else "#00c062" for d in df_inf["dif_mes"]]
            fig_inf.update_traces(marker_color=colores)
            
            st.plotly_chart(tunear(fig_inf), use_container_width=True, config={"displayModeBar": False, "locale": "es"})

    # 3. Reservas brutas
    with fila2_izq:
        st.metric("[Reservas del BCRA](?ver=tablero/reservas)", "", help="Stock bruto de reservas internacionales del Banco Central en millones de USD.")
        if reservas is not None and not reservas.empty:
            f_min = reservas["fecha"].max() - pd.Timedelta(days=365)
            df_res = reservas[reservas["fecha"] >= f_min].dropna(subset=["valor"])
            fig_res = charts.lineas(df_res, {"Reservas": "valor"}, "", height=210, yfmt=",.0f")
            st.plotly_chart(tunear(fig_res), use_container_width=True, config={"displayModeBar": False, "locale": "es"})

    # 4. Variación mensual EMAE
    with fila2_der:
        st.metric("[Variación actividad mensual (EMAE)](?ver=tablero/actividad)", "", help="Evolución desestacionalizada del nivel general de actividad económica mes a mes.")
        if emae_sa is not None and not emae_sa.empty:
            df_act = emae_sa.sort_values("fecha").copy()
            col_var = next((c for c in ["var_m", "variacion_mensual", "var_mensual", "variacion"] if c in df_act.columns), None)
            if not col_var:
                df_act["var_m"] = df_act["valor"].pct_change() * 100
                col_var = "var_m"
            f_min = df_act["fecha"].max() - pd.Timedelta(days=365)
            df_act = df_act[df_act["fecha"] >= f_min].dropna(subset=[col_var])
            fig_act = charts.barras(df_act, col_var, "", height=210, yfmt=",.1f", color_signo=True, etiquetas=True,
                                    sufijo_hover="%")
            st.plotly_chart(tunear(fig_act), use_container_width=True, config={"displayModeBar": False, "locale": "es"})

    def que_le_gano() -> None:
        """Comparativo contra la inflación: cambiar el período redibuja solo esto."""
