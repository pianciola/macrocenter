"""Historia económica · Ministros de Economía.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import streamlit as st

from macrocenter import ministros, presidentes, style


def mostrar(dp: dict | None, *, fotos_ministros, fotos_presidentes) -> None:
    r = ministros.resumen()
    resumen = [("Gestiones", str(r["gestiones"]), f"{r['personas']} personas distintas"),
               ("Duración promedio", r["promedio"], "por gestión"),
               ("La más larga", r["larga"][0].nombre, f"{r['larga'][1]} · {ministros.periodo(r['larga'][0])}"),
               ("La más corta", r["corta"][0].nombre, f"{r['corta'][1]} · {ministros.periodo(r['corta'][0])}")]
    st.markdown(style.ministros(resumen, [], intro=(
        "Quién condujo la economía en cada gobierno, cuánto duró y qué medidas marcaron su gestión. Los hitos son "
        "hechos con fecha, sin valoraciones; las cifras se calculan con las series oficiales.")), unsafe_allow_html=True)
    MS = presidentes.MANDATOS
    opciones = ["Todos"] + [presidentes.CORTO[m.clave] for m in MS]
    elegido = st.segmented_control("Presidente", opciones, default="Todos", key="min_pres",
                                   label_visibility="collapsed") or "Todos"
    fotos_p = fotos_presidentes()
    fotos_m = fotos_ministros()
    grupos = []
    for m in MS:
        corto = presidentes.CORTO[m.clave]
        if elegido not in ("Todos", corto):
            continue
        # con «Todos», cada ministro va una sola vez (con el presidente con el que asumió); filtrando, aparece con todos
        lista = [x for x in ministros.MINISTROS
                 if (x.presidentes[0] == m.clave if elegido == "Todos" else m.clave in x.presidentes)]
        items = []
        for x in lista:
            try:
                ind = ministros.indicadores(x, dp) if dp else None
            except Exception:  # noqa: BLE001 — sin cifras, la tarjeta igual se muestra
                ind = None
            items.append(dict(nombre=x.nombre, iniciales=x.iniciales, foto=ministros.foto_url(x, fotos_m), cargo=x.cargo,
                              periodo=ministros.periodo(x), duracion=ministros.duracion(x.dias),
                              barra=ministros.barra_duracion(x), perfil=x.perfil, hitos=x.hitos,
                              datos=ministros.datos(ind) if ind else [], pico=ministros.pico_texto(ind) if ind else "",
                              actual=x.hasta is None))
        grupos.append(dict(titulo=m.nombre, periodo=m.periodo, foto=fotos_p.get(m.clave, {}).get("url"),
                           nota=ministros.NOTAS.get(m.clave, ""), items=items))
    st.markdown(style.ministros(None, grupos), unsafe_allow_html=True)
    st.caption("Fechas: listado oficial del Ministerio de Economía (CDI). La inflación de cada mes se asigna a quien estaba "
               "en el cargo al cierre de ese mes; entre 2007 y 2015 son las cifras del INDEC intervenido, que distintos "
               "analistas consideran subestimadas. El dólar oficial se muestra desde 1992. Las cifras de un ministro dependen "
               "también del contexto que heredó y de decisiones de otras áreas (BCRA, Congreso, Presidencia).")
