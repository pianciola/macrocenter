"""Pestaña «Inicio» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import traceback

import pandas as pd
import streamlit as st

from macrocenter import charts, style


def mostrar(
    *, CATALOGO, GRAFICOS_INICIO, HOY, _grafico_periodo, badlar, bloque_comercio_inicio, bloque_dolar_precios,
    bloque_expectativas, bloque_fiscal, bloque_pobreza, bloque_reservas_riesgo, bloque_salarios, dol, dol_rec,
    emae_sa, falla, grafico, guardar_prefs, infl_ia, infl_m, kpi, panel_plazo_fijo, panorama_inicio, reservas,
    restablecer_prefs, riesgo, sal_real_df, selector_categoria, selector_periodo, turno_de_visita, ultimo, uva,
) -> None:
    turno = turno_de_visita()
    # el estado de sesión puede traer claves viejas o inválidas: se filtra antes de dibujar el selector
    previos = st.session_state.get("kpis_sel")
    st.session_state["kpis_sel"] = [k for k in (previos if isinstance(previos, list) else [])
                                    if isinstance(k, str) and k in CATALOGO]
    h, p = st.columns([5, 1.5], vertical_alignment="center")
    h.subheader("Indicadores clave")
    with p.container(key="personalizar"), st.popover("Personalizar", icon=":material/tune:", width="content"):
        st.caption("Elegí qué indicadores ver (y en qué orden). Tu elección queda guardada.")
        st.multiselect(
            "Indicadores", options=list(CATALOGO), key="kpis_sel", on_change=guardar_prefs,
            format_func=lambda k: f"{CATALOGO[k][0]} · {CATALOGO[k][1]}", label_visibility="collapsed",
            placeholder="Elegí indicadores…",
        )
        st.button("Restablecer los de siempre", on_click=restablecer_prefs, width="stretch")
    elegidos = st.session_state["kpis_sel"]
    if not elegidos:
        st.info("No elegiste ningún indicador. Usá **Personalizar** para agregar los que quieras ver.")
    for i in range(0, len(elegidos), 5):
        for slot, clave in zip(st.columns(5), elegidos[i:i + 5]):
            try:
                kpi(slot, CATALOGO[clave][1], **CATALOGO[clave][2]())
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                kpi(slot, CATALOGO[clave][1], None)

    # Panorama en texto: la coyuntura en cuatro o cinco frases, armadas con los últimos datos
    frases = panorama_inicio()
    if frases:
        st.html(style.panorama(frases, f"{HOY:%d/%m/%Y}"))

    # un solo gráfico a la vez, para que la portada no se llene; cada visita arranca con uno distinto
    st.markdown("#### Gráfico destacado")
    @st.fragment
    def grafico_inicio() -> None:
        """Selector de gráfico + período: cambiar uno u otro redibuja solo esto."""
        OPC = list(GRAFICOS_INICIO)
        inicial = OPC[turno % len(OPC)]
        elegido_i = selector_categoria("Gráfico", OPC, "inicio_grafico", defecto=inicial) or inicial
        if elegido_i == "Dólar" and dol is not None:
            _grafico_periodo("res_dolar", dol_rec, lambda d: charts.lineas(d, {"Oficial": "oficial", "Blue": "blue"}, "Dólar ($)",
                                                                           height=340))
        elif elegido_i == "Inflación" and infl_m is not None and infl_ia is not None:
            m = infl_m.merge(infl_ia, on="fecha", suffixes=("_m", "_ia"))
            _grafico_periodo("res_infl", m, lambda d: charts.barras_y_linea(d, "valor_m", "valor_ia", "Inflación (%)",
                                                                            "Mensual", "Interanual", height=340),
                            defecto="5 años", mensual=True)
        elif elegido_i == "Reservas" and reservas is not None:
            _grafico_periodo("res_reservas", reservas, lambda d: charts.lineas(d, {"Reservas brutas": "valor"},
                                                                               "Reservas internacionales (USD millones)", height=340))
        elif elegido_i == "Riesgo país" and riesgo is not None:
            _grafico_periodo("res_riesgo", riesgo, lambda d: charts.lineas(d, {"Riesgo país": "valor"},
                                                                           "Riesgo país (puntos básicos)", height=340))
        elif elegido_i == "Brecha" and dol is not None:
            _grafico_periodo("ini_brecha", dol.dropna(subset=["brecha_blue"]),
                             lambda d: charts.lineas(d, {"Blue vs oficial": "brecha_blue", "CCL vs oficial": "brecha_ccl"},
                                                     "Brecha cambiaria (% sobre el oficial)", yfmt=",.0f", height=340))
        elif elegido_i == "Actividad" and emae_sa is not None:
            _grafico_periodo("ini_emae", emae_sa, lambda d: charts.lineas(
                d, {"EMAE desestacionalizado": "valor"}, "Actividad económica (EMAE desestacionalizado, 2004 = 100)",
                yfmt=",.0f", height=340), defecto="5 años", mensual=True)
        elif elegido_i == "Salario real" and sal_real_df is not None and not sal_real_df.empty:
            _grafico_periodo("ini_salreal", sal_real_df, lambda d: charts.barras(
                d, "real", "Salario real — variación interanual (%)", yfmt=",.1f", height=340),
                defecto="5 años", mensual=True)
        else:
            falla(f"no se pudo cargar el gráfico destacado «{elegido_i}»")
            return
        st.caption(GRAFICOS_INICIO[elegido_i])

    grafico_inicio()

    def que_le_gano() -> None:
        """Comparativo contra la inflación: cambiar el período redibuja solo esto."""
        ventanas = {"3 meses": 3, "6 meses": 6, "1 año": 12}
        vent = selector_periodo("rend", "1 año", opciones=list(ventanas))
        n_m = ventanas[vent]
        try:
            corte = HOY - pd.DateOffset(months=n_m)
            nombres_r, valores_r = [], []

            def variacion(s: pd.Series) -> float | None:
                s = s.dropna()
                s = s[s.index <= HOY]
                antes = s[s.index <= corte]
                if s.empty or antes.empty or antes.iloc[-1] == 0:
                    return None
                return float((s.iloc[-1] / antes.iloc[-1] - 1) * 100)

            if dol is not None:
                for col, nom in (("oficial", "Dólar oficial"), ("blue", "Dólar blue"), ("bolsa", "Dólar MEP")):
                    if col in dol:
                        v_ = variacion(dol.set_index("fecha")[col])
                        if v_ is not None:
                            nombres_r.append(nom); valores_r.append(v_)
            # la UVA no compite: ajusta por CER (la inflación con rezago), así que por construcción queda pegada a la línea.
            # Se informa como referencia, debajo del gráfico.
            uva_p = variacion(uva.set_index("fecha")["valor"]) if uva is not None else None
            infl_p = None
            if n_m == 12 and infl_ia is not None and ultimo(infl_ia) is not None:
                infl_p = ultimo(infl_ia)  # 12 meses: el dato interanual oficial, el mismo de los indicadores clave
            elif infl_m is not None:
                im_ = infl_m[(infl_m["fecha"] <= HOY)].dropna(subset=["valor"]).tail(n_m)
                if len(im_) == n_m:
                    infl_p = float(((1 + im_["valor"] / 100).prod() - 1) * 100)
            if badlar is not None:
                tm_ = badlar[badlar["fecha"] <= HOY].set_index("fecha")["valor"].resample("ME").mean().dropna().tail(n_m)
                if len(tm_) == n_m:
                    nombres_r.append("Plazo fijo (BADLAR)")
                    valores_r.append(float(((1 + tm_ / 1200).prod() - 1) * 100))
            if len(valores_r) >= 2:
                grafico(charts.rendimientos(nombres_r, valores_r, infl_p, f"Variación en los últimos {vent} (%)"))
                st.markdown(style.aclaracion(
                    ("Supuestos", "El plazo fijo se aproxima con la tasa BADLAR, sin impuestos ni comisiones; el dólar se mide sin "
                                  "considerar costos de compra o venta."),
                    ("UVA", "" if uva_p is None else
                            f"Subió {charts.num(uva_p, 1, '%')}. No se compara porque se ajusta por la inflación (CER, con unas semanas "
                            "de rezago), así que siempre queda cerca de la línea."),
                    ("Ojo", "Es el pasado: no anticipa qué va a pasar."),
                    leyenda=[("bien", "Superó a la inflación del período (línea punteada)"), ("mal", "Quedó abajo")]), unsafe_allow_html=True)
            else:
                falla("no hay datos para el comparativo contra la inflación")
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            falla("no se pudo armar el comparativo contra la inflación")

    # Análisis destacado: rota en cada visita y con el botón se pasa al siguiente (solo se redibuja esta parte)
    ANALISIS = [
        ("¿Qué le ganó a la inflación?", que_le_gano),
        ("¿Los salarios le ganan a la inflación?", bloque_salarios),
        ("¿Le ganó el plazo fijo a la inflación?", lambda: panel_plazo_fijo("ini_real", subtitulo=False)),
        ("¿Cómo vienen las cuentas públicas?", bloque_fiscal),
        ("¿Qué espera el mercado de la inflación?", bloque_expectativas),
        ("¿El dólar subió más o menos que los precios?", bloque_dolar_precios),
        ("¿Cómo viene el comercio exterior?", bloque_comercio_inicio),
        ("¿Cómo vienen las reservas y el riesgo país?", bloque_reservas_riesgo),
        ("¿Cuántas personas están por debajo de la línea de pobreza?", bloque_pobreza),
    ]

    def _otro_analisis() -> None:
        st.session_state["inicio_analisis"] = st.session_state.get("inicio_analisis", 0) + 1

    @st.fragment
    def analisis_inicio() -> None:
        if not isinstance(st.session_state.get("inicio_analisis"), int):
            st.session_state["inicio_analisis"] = turno
        i = st.session_state["inicio_analisis"] % len(ANALISIS)
        titulo_a, dibujar = ANALISIS[i]
        h_, b_ = st.columns([5, 1.5], vertical_alignment="center")
        h_.subheader(titulo_a)
        b_.button("Ver otro análisis", icon=":material/autorenew:", key="inicio_otro", width="content",
                  on_click=_otro_analisis)
        try:
            dibujar()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            falla("no se pudo armar el análisis destacado")

    st.divider()
    analisis_inicio()
