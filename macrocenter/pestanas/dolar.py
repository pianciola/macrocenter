"""Pestaña «Dólar» del tablero. app.py la dibuja cuando está abierta y le pasa, por nombre, los datos y las
funciones de la página que usa (los parámetros de `mostrar`)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from macrocenter import datos_vista, charts, style


def mostrar(*, VIVO, base100, con_periodo, delta, dol, dol_rec, get, grafico, ultimo) -> None:
    st.markdown(style.intro("Todas las cotizaciones del dólar en la Argentina, del oficial a los financieros.",
                            [("bien", "Sube"), ("mal", "Baja")],
                            "En cada tarjeta, **«vs oficial»** indica cuánto más caro está ese dólar que el oficial (por ejemplo, +2% significa que cuesta un 2% más).", resumen='Cotizaciones, brechas y evolución de los principales dólares.'), unsafe_allow_html=True)
    if dol is not None:
        TIPOS_DOLAR = [
            ("oficial", "Dólar oficial", "Banco Nación, venta minorista"),
            ("mayorista", "Dólar mayorista", "Entre grandes operadores"),
            ("blue", "Dólar blue", "Mercado informal"),
            ("bolsa", "Dólar MEP", "Compra de bonos en bolsa"),
            ("contadoconliqui", "Dólar CCL", "Contado con liquidación"),
            ("cripto", "Dólar cripto", "Vía stablecoins (USDT)"),
            ("tarjeta", "Dólar tarjeta", "Consumos en el exterior: oficial + impuestos"),
        ]
        oficial_hoy = ultimo(dol[["fecha", "oficial"]].dropna().rename(columns={"oficial": "valor"}))
        tarjetas_usd = []
        for clave, nombre, desc in TIPOS_DOLAR:
            s = dol[["fecha", clave, f"{clave}_compra"]].dropna(subset=[clave])
            if s.empty:
                continue
            venta, compra = float(s.iloc[-1][clave]), s.iloc[-1][f"{clave}_compra"]
            tarjetas_usd.append(dict(
                meta=datos_vista.detalle(s, "ArgentinaDatos / DolarApi / CriptoYa", nombre=nombre,
                                        frecuencia="Diaria; consultas intradiarias", unidad="ARS por USD", definicion=desc),
                nombre=nombre, desc=desc, valor=charts.num(venta, 0, pre="$"),
                detalle=f"Compra {charts.num(float(compra), 0, pre='$')} · Venta {charts.num(venta, 0, pre='$')}",
                var=delta(s.rename(columns={clave: "valor"})), sentido="alto",  # cotización: verde si sube
                spark=list(s.tail(30)[clave]),
                chip=None if clave == "oficial" or not oficial_hoy else
                f"{(venta / oficial_hoy - 1) * 100:+.1f}% vs oficial".replace(".", ","),
            ))
        st.markdown(style.cotizaciones(tarjetas_usd), unsafe_allow_html=True)
        dv_ = VIVO.get("dolares")
        hora_ = (f" Último dato del día: {pd.Timestamp(dv_['actualizado'].max()):%d/%m %H:%M} (DolarApi y CriptoYa: MEP y CCL de las operaciones del AL30); se renueva cada 30 segundos."
                 if isinstance(dv_, pd.DataFrame) and not dv_.empty else "")
        st.markdown(style.aclaracion(
            ("Cómo leerlo", "La variación compara con 30 días atrás."),
            ("Fuente", f"ArgentinaDatos.{hora_}")), unsafe_allow_html=True)

        eur, gbp = get("fx:EUR"), get("fx:GBP")
        tarjetas_fx = []
        for df_, nombre, simbolo in ((eur, "Euro", "€"), (gbp, "Libra esterlina", "£")):
            if df_ is not None:
                u = df_.iloc[-1]
                tarjetas_fx.append(dict(
                    meta=datos_vista.detalle(df_, "BCRA", nombre=nombre, frecuencia="Diaria",
                                            unidad=f"ARS por {simbolo}", definicion="Cotización de referencia del BCRA."),
                    nombre=nombre, desc="Cotización de referencia del BCRA",
                    valor=charts.num(float(u["valor"]), 0, pre="$"),
                    detalle=f"1 {simbolo} = US$ {charts.num(float(u['pase']), 2)}",
                    var=delta(df_), sentido="alto", chip=None, spark=list(df_.tail(30)["valor"])))
        if tarjetas_fx:
            st.markdown("#### Otras monedas")
            st.markdown(style.cotizaciones(tarjetas_fx), unsafe_allow_html=True)
            st.markdown(style.aclaracion(
                ("Euro y libra", "Referencia cambiaria del BCRA en pesos por unidad (no es el precio de la casa de cambio).")), unsafe_allow_html=True)

        @st.fragment
        def graficos_dolar() -> None:
            """Período + gráfico de cotizaciones + brecha: al cambiar el período se redibuja solo esto."""
            st.markdown("#### Evolución del dólar")
            r = con_periodo("dolar", dol_rec)
            grafico(charts.lineas(r, {"Oficial": "oficial", "Mayorista": "mayorista", "Blue": "blue", "MEP": "bolsa",
                                      "CCL": "contadoconliqui", "Cripto": "cripto", "Tarjeta": "tarjeta"},
                                  "Cotizaciones del dólar — precio de venta ($)", height=460,
                                  ocultas=("Mayorista", "Cripto", "Tarjeta")))
            st.caption("Tocá un nombre en la leyenda para mostrar u ocultar cada dólar.")
            with st.expander("Brecha cambiaria y evolución relativa"):
                a, b = st.columns(2)
                with a:
                    grafico(charts.lineas(r, {"Blue vs oficial": "brecha_blue", "CCL vs oficial": "brecha_ccl"},
                                          "Brecha cambiaria (%)", yfmt=",.0f"))
                with b:
                    base = base100(r, ["oficial", "blue"])
                    grafico(charts.lineas(base, {"Oficial": "oficial", "Blue": "blue"},
                                          "Evolución base 100 = inicio del período", yfmt=",.0f"))

        graficos_dolar()
        with st.expander("Últimas cotizaciones (venta)"):
            tabla = dol[["fecha", "oficial", "mayorista", "blue", "bolsa", "contadoconliqui", "cripto", "tarjeta",
                         "brecha_blue", "brecha_ccl"]].tail(10).sort_values("fecha", ascending=False).rename(columns={
                "fecha": "Fecha", "oficial": "Oficial", "blue": "Blue", "bolsa": "MEP",
                "contadoconliqui": "CCL", "mayorista": "Mayorista", "cripto": "Cripto", "tarjeta": "Tarjeta",
                "brecha_blue": "Brecha blue %", "brecha_ccl": "Brecha CCL %"})
            filas = [[f"{r['Fecha']:%d/%m/%Y}"] + [charts.num(r[c], 1, suf="%") if c.startswith("Brecha")
                                                   else charts.num(r[c], 0, pre="$") for c in tabla.columns[1:]]
                     for _, r in tabla.iterrows()]
            st.markdown(style.tabla(list(tabla.columns), filas), unsafe_allow_html=True)
