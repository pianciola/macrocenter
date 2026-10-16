"""Historia económica: presidentes, ministros y viaje en el tiempo.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import traceback

import pandas as pd
import streamlit as st

from macrocenter import charts, interactivo, presidentes, selector, style


def mostrar(
    *, ACTUALIZADO, DATOS, HIST_SECCIONES, actualizando, dol, falla, fotos_presidentes, grafico, historicos,
    seccion_ministros,
) -> None:
    secciones = HIST_SECCIONES
    seccion = selector.uno(st.segmented_control, "Sección", secciones, "hist_seccion", label_visibility="collapsed")
    if seccion == "Ministros de Economía":
        try:
            dp = historicos(DATOS, dol, ACTUALIZADO)[0]
        except Exception:  # noqa: BLE001 — sin series, las tarjetas se muestran sin cifras
            dp = None
        seccion_ministros(dp)
        return
    if seccion == "Viaje en el tiempo":
        try:
            dp, _, faltan = historicos(DATOS, dol, ACTUALIZADO)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            dp, faltan = None, ["cálculo"]
        if faltan:
            falla("no se pudo armar el viaje en el tiempo: falta " + ", ".join(faltan))
            actualizando()
        else:
            interactivo.pantalla_viaje(dp, fotos_presidentes())
        return
    st.markdown(style.intro("Cómo evolucionó la economía con cada presidente desde la vuelta de la democracia, y cómo se "
               "comparan los mandatos entre sí. Los números se calculan con las series oficiales."), unsafe_allow_html=True)
    try:
        dp, inds, faltan = historicos(DATOS, dol, ACTUALIZADO)
    except Exception:  # noqa: BLE001 — una falla de cálculo no debe romper el resto de la app
        traceback.print_exc()
        dp, inds, faltan = None, None, ["cálculo"]
    if faltan:
        falla("no se pudo armar la sección de presidentes: falta " + ", ".join(faltan))
        actualizando()
    else:
        if inds:
            MS = presidentes.MANDATOS
            elegido = selector.uno(st.segmented_control, "Gráfico", presidentes.GRAFICOS, "hist_grafico",
                                   label_visibility="collapsed")
            serie_g, opciones_g = presidentes.grafico_historico(elegido, dp)
            fig_g = charts.serie_presidentes(serie_g, MS, presidentes.CORTO, **opciones_g)
            if st.toggle("Mostrar hitos económicos", key="hist_hitos",
                         help="Marca en el gráfico hechos con fecha (planes, crisis, cambios de régimen cambiario). Sin valoración."):
                fig_g = charts.marcar_eventos(fig_g, presidentes.EVENTOS, serie_g["fecha"].min())
            grafico(fig_g)

            # comparación entre mandatos: orden cronológico, un indicador a la vez
            st.markdown("#### Comparar mandatos")
            comp = selector.uno(st.segmented_control, "Indicador", list(presidentes.COMPARACIONES), "hist_comp",
                                "Inflación anual al irse", label_visibility="collapsed")
            clave_c, unidad_c, ayuda_c = presidentes.COMPARACIONES[comp]
            # reservas en dólares de hoy: se corrigen por la inflación de EE. UU. (un dólar de 1989 no es un dólar de hoy)
            cpi = DATOS.get("fred:ipc_eeuu")
            ajustar = False
            if clave_c == "res_fin" and isinstance(cpi, pd.DataFrame) and not cpi.empty:
                ajustar = st.toggle("Ajustar por inflación de EE. UU. (dólares de hoy)", value=True, key="hist_res_real",
                                    help="Pasa las reservas de cada fecha a su equivalente en dólares actuales, según el IPC de EE. UU.")
            anualizar = clave_c == "pbi" and st.toggle("Mostrar crecimiento anualizado", value=True, key="pbi_anualizado")
            vals_c = []
            for m in MS:
                i_ = inds[m.clave]
                if clave_c == "usd_mult":
                    v_ = i_["usd_fin"] / i_["usd_ini"] if i_["usd_ini"] and i_["usd_fin"] else None
                else:
                    v_ = i_.get(clave_c)
                if ajustar and v_ is not None:
                    previos = cpi[cpi["fecha"] <= m.fin]
                    if previos.empty:
                        v_ = None
                    else:
                        v_ = v_ * float(cpi["valor"].iloc[-1]) / float(previos["valor"].iloc[-1])
                if anualizar and v_ is not None:
                    anios = (m.fin - m.desde).days / 365.25
                    v_ = ((1 + v_ / 100) ** (1 / anios) - 1) * 100 if anios > 0 and v_ > -100 else None
                vals_c.append(v_)
            if anualizar:
                comp = "PBI: crecimiento anualizado (%)"
                ayuda_c = "Tasa anual equivalente del crecimiento acumulado, usando la duración del mandato. El último dato disponible puede tener rezago; no mide causalidad."
            if ajustar:
                comp = "Reservas al irse (USD M de hoy)"
                ayuda_c = ("Reservas brutas del BCRA al final del mandato, expresadas en dólares de hoy con el IPC de EE. UU. "
                           "(FRED), así se pueden comparar entre épocas.")
            grafico(charts.comparar_mandatos([presidentes.CORTO[m.clave] for m in MS], vals_c, comp,
                                             sufijo=unidad_c, dec=0 if clave_c == "res_fin" else 1,
                                             actual=presidentes.CORTO[MS[-1].clave] if MS[-1].hasta is None else None,
                                             logaritmica=clave_c in ("inf_fin", "inf_acum")))
            st.markdown(style.aclaracion(
                ("Qué mide", ayuda_c),
                ("Cómo leerlo", "Barras en orden cronológico; la dorada es el mandato en curso."
                                + (" Escala logarítmica: cada marca vale 10 veces la anterior, así la hiperinflación no "
                                   "aplasta al resto." if clave_c in ("inf_fin", "inf_acum") else "")),
                ("Criterio", "La inflación de cada mes se asigna a quien gobernaba al cierre de ese mes: por eso julio de "
                             "1989 cuenta para Menem y diciembre de 2023 para Milei, aunque esas subas se hayan gestado "
                             "antes. Es discutible, y se aplica igual a todos."),
                ("Nota", "Los mandatos duraron distinto y ocurrieron en contextos muy distintos: es información, no un "
                        "ranking.")), unsafe_allow_html=True)
            st.caption("Describe la evolución durante cada mandato; no atribuye causalidad. El mandato en curso tiene un período incompleto.")
            st.dataframe(pd.DataFrame([{"Mandato": presidentes.CORTO[m.clave], "Desde": m.desde.strftime("%d/%m/%Y"), "Hasta": m.fin.strftime("%d/%m/%Y"), "Años": round((m.fin-m.desde).days/365.25, 1)} for m in MS]), hide_index=True)
            with st.expander("Cómo se calcula cada cifra"):

                st.markdown(
                    """
- **Inflación anual:** variación de los 12 meses previos al último mes completo antes de asumir y antes de irse
  (para el presidente actual, el último dato publicado). *Entre 2007 y 2015 son las cifras oficiales del INDEC
  intervenido, que distintos analistas consideran subestimadas.*
- **PBI en el mandato:** crecimiento acumulado entre el PBI de los 4 trimestres previos a asumir y el de los 4 previos
  a irse (empalme de tres series oficiales: base 1986, 1993 y 2004).
- **Desocupación:** dato anual de la EPH (si el mandato empieza antes de noviembre se usa el año anterior).
- **Dólar oficial:** solo desde 1992; antes las series están en monedas de cada época (peso argentino, austral) y con
  tramos sin actualizar, por eso no se muestra para Alfonsín ni para el inicio de Menem.
- **Reservas:** brutas del BCRA, saldo de fin de mes. **Riesgo país:** disponible desde 1999.
- No se incluye pobreza: no existe una serie oficial continua desde 1983.
                    """
                )
