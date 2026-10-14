"""Cripto.

app.py la dibuja con `abrir` y le pasa, por nombre, los datos y las funciones de la página que usa (los
parámetros de `mostrar` después del asterisco)."""
from __future__ import annotations

import streamlit as st

from macrocenter import charts, style
from macrocenter.carga import historia_cripto


def mostrar(
    *, _nombre_exchange, _usd_cripto, cargar_cripto, dol, falla, grafico, selector_categoria,
    selector_periodo, ultimo,
) -> None:
    cr = cargar_cripto()
    mercado, usdt = cr["mercado"], cr["usdt"]
    st.caption("Las principales criptomonedas, en dólares y en pesos, y a cuánto se compra y vende el USDT en los "
               "exchanges argentinos. Se actualiza cada 5 minutos. Verde: sube; rojo: baja.")
    if isinstance(mercado, str) or mercado.empty:
        falla(f"no se pudo cargar el mercado de criptomonedas ({mercado})")
    else:
        tarjetas = []
        for _, c in mercado.iterrows():
            tarjetas.append(dict(
                nombre=c["nombre"], desc=c["simbolo"], valor=_usd_cripto(c["usd"]),
                detalle=f"≈ {charts.num(c['ars'], 0, pre='$')}" if c["ars"] == c["ars"] else "en pesos: s/d",
                var=c["cambio_24h"], var_txt="24 h", extras=[("7 d", c["cambio_7d"])], sentido="alto",
                spark=list(c["spark"]), ))
        st.markdown(style.cotizaciones(tarjetas), unsafe_allow_html=True)

        monedas = mercado[~mercado["simbolo"].isin(["USDT", "USDC"])].head(6)  # las estables no tienen qué graficar
        st.markdown("#### Historial de precios")
        elegida = selector_categoria("Moneda", list(monedas["simbolo"]), "cripto",
                                     defecto=monedas["simbolo"].iloc[0]) or monedas["simbolo"].iloc[0]
        rangos = {"1 mes": 30, "3 meses": 90, "1 año": 365}
        rango = selector_periodo("cripto", "1 año", opciones=list(rangos))
        fila = monedas[monedas["simbolo"] == elegida]
        if not fila.empty:
            hist = historia_cripto(fila.iloc[0]["id"], rangos.get(rango, 365))
            if isinstance(hist, str) or hist.empty:
                falla(f"no se pudo cargar el historial de {fila.iloc[0]['nombre']} ({hist})")
            else:
                # decimales según el precio: con ",.0f" las monedas de menos de US$ 1 (TRX, DOGE, ADA) mostraban «0» en el eje
                tope = float(hist["valor"].abs().max() or 0)
                fmt_c = ",.0f" if tope >= 100 else ",.2f" if tope >= 1 else ",.4f"
                grafico(charts.lineas(hist, {f"{fila.iloc[0]['nombre']} (US$)": "valor"},
                                      f"{fila.iloc[0]['nombre']} en dólares — {rango.lower()}", yfmt=fmt_c, height=340))
        st.caption("El historial gratuito de CoinGecko llega hasta 1 año atrás.")

    st.subheader("USDT en pesos, exchange por exchange")
    if isinstance(usdt, str) or usdt.empty:
        falla(f"no se pudieron cargar los precios del USDT ({usdt})")
    else:
        oficial_hoy = ultimo(dol[["fecha", "oficial"]].dropna().rename(columns={"oficial": "valor"})) if dol is not None else None
        mejor_compra, mejor_venta = usdt.iloc[0], usdt.sort_values("venta", ascending=False).iloc[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("Compra más baja", charts.num(float(mejor_compra["compra"]), 0, pre="$"),
                  f"en {_nombre_exchange(mejor_compra['exchange'])}", delta_color="off", delta_arrow="off", border=True)
        k2.metric("Venta más alta", charts.num(float(mejor_venta["venta"]), 0, pre="$"),
                  f"en {_nombre_exchange(mejor_venta['exchange'])}", delta_color="off", delta_arrow="off", border=True)
        if oficial_hoy:
            k3.metric("Contra el oficial", f"{(mejor_compra['compra'] / oficial_hoy - 1) * 100:+.1f}%".replace(".", ","),
                      "con la compra más baja", delta_color="off", delta_arrow="off", border=True)
        filas = [[_nombre_exchange(r["exchange"]), charts.num(float(r["compra"]), 0, pre="$"),
                  charts.num(float(r["venta"]), 0, pre="$"),
                  (f"{(r['compra'] / oficial_hoy - 1) * 100:+.1f}%".replace(".", ",") if oficial_hoy else "s/d")]
                 for _, r in usdt.head(10).iterrows()]
        st.markdown(style.tabla_simple(["Exchange", "Comprar USDT", "Vender USDT", "Compra vs oficial"], filas),
                    unsafe_allow_html=True)
        st.caption("Precios sin comisiones, de CriptoYa. «Comprar» es lo que pagás por cada USDT; «Vender», lo que recibís. "
                   "No es una recomendación de inversión.")
