"""Herramientas · Calificación macro.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import charts, score


def mostrar(
    *, ACTUALIZADO, COMPARACIONES, HOY, MESES_ES, NOTAS, SERIES_NOTA, actualizando, calcular_notas, falla, grafico,
) -> None:
    if NOTAS["Hoy"]["total"] is None:
        falla("no hay datos suficientes para la calificación")
        actualizando()
        return

    def restablecer_calificacion() -> None:
        """Vuelve la ventana a 5 años y todos los pesos a 25 (el punto de partida)."""
        st.session_state["cal_anios"] = 5
        for p_ in score.PILARES:
            st.session_state[f"cal_peso_{p_}"] = 25

    # el estado se inicializa acá (y no con `default=`) para poder restablecerlo desde el botón sin conflictos;
    # los controles están al final, pero su valor ya está disponible porque Streamlit conserva el estado entre corridas
    if st.session_state.get("cal_anios") not in (3, 5, 10):
        st.session_state["cal_anios"] = 5
    for p_ in score.PILARES:
        v_ = st.session_state.get(f"cal_peso_{p_}")
        if not isinstance(v_, int) or isinstance(v_, bool) or not 0 <= v_ <= 100:
            st.session_state[f"cal_peso_{p_}"] = 25
    anios_sel = int(st.session_state["cal_anios"])
    pesos_sel = {p: int(st.session_state[f"cal_peso_{p}"]) for p in score.PILARES}
    notas_c, hist_c = calcular_notas(SERIES_NOTA, ACTUALIZADO, anios_sel, tuple(pesos_sel.items()))
    hoy_n = notas_c["Hoy"]

    st.markdown(
        f"**Cómo leerla:** es una nota de 0 a 100 que dice si la economía está hoy mejor o peor que en los últimos "
        f"{anios_sel} años. **0** = el peor momento del período, **100** = el mejor, **50** = un momento típico. "
        "Dice **«mejor que el pasado reciente»**, no **«buena»**: si ese pasado fue muy malo, una nota alta puede convivir "
        "con valores todavía altos (por ejemplo, una inflación de 1,7% mensual sale bien parada al lado de 2023-2024)."
    )
    if hoy_n["total"] is None:
        st.warning("Con esta ventana no hay datos suficientes. Probá con otra en «Ajustar el criterio», al final.")
        return

    # ── Contra qué momento se compara ──
    OTRA = "Otra fecha"
    opciones_ref = [k for k in COMPARACIONES if k != "Hoy"] + [OTRA]
    if st.session_state.get("cal_ref") not in opciones_ref:
        st.session_state["cal_ref"] = "Hace 1 año"
    c_ref, c_mes = st.columns([3, 1.3], vertical_alignment="bottom")
    eleccion = c_ref.segmented_control("Comparar con", opciones_ref, key="cal_ref") or "Hace 1 año"
    if eleccion == OTRA:
        meses_ref = list(pd.date_range(end=HOY - pd.DateOffset(months=1), periods=12 * 10, freq="MS")[::-1])
        if st.session_state.get("cal_ref_mes") not in meses_ref:
            st.session_state["cal_ref_mes"] = meses_ref[11]
        fecha_ref = c_mes.selectbox("Mes", meses_ref, key="cal_ref_mes",
                                    format_func=lambda m: f"{MESES_ES[m.month - 1].capitalize()} {m.year}")
        ref_n = score.calificar(SERIES_NOTA, fecha_ref, anios_sel, pesos_sel)
        ref_txt = f"en {MESES_ES[fecha_ref.month - 1]} de {fecha_ref.year}"
        ref_corto = f"{MESES_ES[fecha_ref.month - 1][:3]}-{fecha_ref.year}"
    else:
        fecha_ref = COMPARACIONES[eleccion]
        ref_n = notas_c[eleccion]
        ref_txt = eleccion.lower()
        ref_corto = eleccion
    if ref_n["total"] is None:
        st.info(f"No hay datos suficientes para calcular la nota {ref_txt}: se muestra solo la de hoy.")

    # ── 1) La nota ──
    etq_hoy, color_hoy = score.nivel(hoy_n["total"])
    with st.container(key="cal_nota"):  # en pantallas angostas, medidor arriba y lectura abajo (ver style.py)
        g, t = st.columns([1.1, 1.4], vertical_alignment="center")
    with g:
        grafico(charts.medidor(hoy_n["total"], etq_hoy, color_hoy, score.NIVELES, height=260))
    with t:
        st.markdown(score.lectura(hoy_n, ref_n, ref_txt))
        if ref_n["total"] is not None:
            dif = round(hoy_n["total"] - ref_n["total"])
            # en fila si hay lugar; si no (celular, columna angosta), una debajo de la otra
            with st.container(key="cal_kpis", horizontal=True):
                k1, k2 = st.container(), st.container()
            k1.metric("Hoy", f"{hoy_n['total']:.0f}/100", border=True)
            k2.metric(ref_corto, f"{ref_n['total']:.0f}/100",
                      f"{dif:+d} pts hasta hoy" if dif else "sin cambios", delta_color="off",
                      delta_arrow="auto" if dif else "off", border=True)

    # ── 2) Los cuatro pilares ──
    st.subheader("Por área")
    DESC_PILAR = {"Precios": "Inflación actual y esperada", "Externo": "Reservas, riesgo país, dólar y comercio",
                  "Actividad": "Producción y empleo", "Ingresos": "Salarios reales"}
    for slot, pilar in zip(st.columns(len(score.PILARES)), score.PILARES):
        v = hoy_n["pilares"].get(pilar)
        a = ref_n["pilares"].get(pilar)
        if v is None:
            slot.metric(pilar, "s/d", border=True)
            continue
        slot.metric(pilar, f"{v:.0f}/100", None if a is None else f"{v - a:+.0f} vs {ref_txt.removeprefix('en ')}",
                    delta_color="off", border=True, help=DESC_PILAR.get(pilar))
        slot.caption(f"**{score.nivel(v)[0]}** · {DESC_PILAR.get(pilar, '')}")

    # ── 3) Qué empuja la nota ──
    def valor_txt(d, fecha):
        s = SERIES_NOTA.get(d.clave)
        return charts.num(score.valor_en(s, fecha), d.dec, d.unidad) if s is not None else "s/d"

    ordenados = sorted((d for d in score.DRIVERS if d.clave in hoy_n["drivers"]),
                       key=lambda d: hoy_n["drivers"][d.clave], reverse=True)
    if ordenados:
        st.subheader("Qué la empuja")
        col_suma, col_resta = st.columns(2)
        with col_suma:
            st.markdown("##### Lo que más suma")
            for d in ordenados[:3]:
                p = hoy_n["drivers"][d.clave]
                st.markdown(f"- {score.frase_driver(d, valor_txt(d, HOY), p, anios_sel)}")
        with col_resta:
            st.markdown("##### Lo que más resta")
            for d in ordenados[::-1][:3]:
                p = hoy_n["drivers"][d.clave]
                st.markdown(f"- {score.frase_driver(d, valor_txt(d, HOY), p, anios_sel)}")
        st.caption("Para tener en cuenta: el **EMAE** y el **salario real** se miden como variación interanual, así que después "
                   "de una caída fuerte el rebote suma puntos aunque el nivel siga bajo. Las **reservas** son las **brutas**: "
                   "incluyen el swap con China, los encajes de los depósitos en dólares y los repos, que no son de libre "
                   "disponibilidad; las **netas** (lo que el BCRA puede usar de verdad) son bastante menores, pero no hay una "
                   "serie oficial pública para calcularlas.")

    # ── 4) Evolución ──
    grafico(charts.evolucion_nota(hist_c, score.NIVELES, "Cómo fue cambiando la nota (últimos 5 años)", height=360))

    # ── 5) Detalle (plegado) ──
    with st.expander("Ver los 9 indicadores uno por uno"):
        filas = []
        for d in score.DRIVERS:
            s = SERIES_NOTA.get(d.clave)
            if s is None:
                continue
            ahora = hoy_n["drivers"].get(d.clave)
            filas.append({
                "Área": d.pilar, "Indicador": d.nombre, "Valor hoy": valor_txt(d, HOY),
                ref_corto: valor_txt(d, fecha_ref),
                "Conviene": "que suba" if d.mejor == "alto" else "que baje",
                "Lectura": "s/d" if ahora is None else score.etiqueta_driver(ahora),
                "Puntaje": ahora,
            })
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch",
                     column_config={"Puntaje": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f")})
        movimientos = [(hoy_n["drivers"][d.clave] - ref_n["drivers"][d.clave], d) for d in ordenados
                       if ref_n["drivers"].get(d.clave) is not None]
        movimientos.sort(key=lambda m: m[0])
        mejoras = [m for m in movimientos[::-1][:3] if m[0] > 1]
        caidas = [m for m in movimientos[:3] if m[0] < -1]
        c_up, c_down = st.columns(2)
        with c_up:
            st.markdown(f"##### Lo que más mejoró desde {ref_txt.removeprefix('en ')}")
            for dif, d in mejoras:
                st.markdown(f"- **{d.nombre}:** {valor_txt(d, fecha_ref)} → {valor_txt(d, HOY)} ({dif:+.0f} pts)")
            if not mejoras:
                st.caption("Nada relevante.")
        with c_down:
            st.markdown(f"##### Lo que más empeoró desde {ref_txt.removeprefix('en ')}")
            for dif, d in caidas:
                st.markdown(f"- **{d.nombre}:** {valor_txt(d, fecha_ref)} → {valor_txt(d, HOY)} ({dif:+.0f} pts)")
            if not caidas:
                st.caption("Nada relevante.")

    # ── 6) Criterio ajustable (plegado) ──
    with st.expander("Ajustar el criterio (opcional)"):
        st.caption("La nota depende de dos decisiones que podés mover: contra cuánta historia se compara y cuánto pesa cada área.")
        st.pills("Comparar contra los últimos…", [3, 5, 10], key="cal_anios", format_func=lambda a: f"{a} años")
        cols_p = st.columns(len(score.PILARES))
        for i, p in enumerate(score.PILARES):
            cols_p[i].slider(p, 0, 100, key=f"cal_peso_{p}")
        st.caption("Los pesos se normalizan solos (importa la proporción). Con todos en 0 se usan iguales.")
        st.button("Restablecer valores de partida", on_click=restablecer_calificacion,
                  help="Ventana de 5 años y las 4 áreas con el mismo peso.")

    with st.expander("Cómo se calcula y qué no mide"):
        st.markdown(
            f"""
- Cada **indicador** recibe un puntaje de **0 a 100**: en qué lugar queda su valor actual comparado con su propia historia
  de los **últimos {anios_sel} años**. Un 90 significa «mejor que el 90% de ese período». Si conviene que baje
  (inflación, riesgo país, brecha, desocupación), se invierte.
- Los indicadores se promedian por **área** (Precios, Externo, Actividad, Ingresos) y las áreas se combinan con los pesos
  elegidos (por defecto, iguales) en la **nota total**.
- Para comparar con períodos anteriores se repite el cálculo *a esa fecha*, usando solo los datos que existían entonces.
- Niveles: Mucho mejor que lo reciente ≥ 75 · Mejor ≥ 60 · Similar ≥ 40 · Peor ≥ 25 · Mucho peor < 25.
- **Qué no mide:** es una medida **relativa** (mejor o peor que el pasado reciente), no absoluta. No incluye deuda ni pobreza.
  Cambiar la ventana o los pesos puede mover mucho el resultado. No es un pronóstico ni asesoramiento financiero.
            """
        )
