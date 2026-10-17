"""Catálogo de indicadores; recibe las series cargadas sin hacer consultas de red."""

DESTINOS = {"Dólar": "dolar", "Tasas": "tasas-y-riesgo-pais", "Precios": "inflacion-y-dinero",
            "Actividad": "actividad-y-pbi", "Ingresos": "salarios"}


def ruta(clave, grupo):
    destino = {"reservas": "reservas", "riesgo": "tasas-y-riesgo-pais",
               "paro": "salarios"}.get(clave, DESTINOS.get(grupo, "resumen"))
    return f"?ver=tablero/{destino}"


def construir(*, _MES, _kpi, badlar, brecha_df, dol_s, emae_ia, emae_m, haber_min, infl_ia, infl_m, paro_pct, pases, rem, reservas, riesgo, ripte, sal_ia, sal_real_df, smvm, uva):
    return {
        "oficial": ("Dólar", "Dólar oficial", _kpi(dol_s.get("oficial"), dec=0, pre="$", help="Precio de venta", fuente='DolarApi / ArgentinaDatos')),
        "blue": ("Dólar", "Dólar blue", _kpi(dol_s.get("blue"), dec=0, pre="$", help="Precio de venta", fuente='DolarApi / ArgentinaDatos')),
        "mep": ("Dólar", "Dólar MEP", _kpi(dol_s.get("bolsa"), dec=0, pre="$", help="Precio de venta", fuente='CriptoYa / ArgentinaDatos')),
        "ccl": ("Dólar", "Dólar CCL", _kpi(dol_s.get("contadoconliqui"), dec=0, pre="$", help="Precio de venta", fuente='CriptoYa / ArgentinaDatos')),
        "brecha": ("Dólar", "Brecha blue / oficial", _kpi(brecha_df, "brecha_blue", modo="abs", dec=1, suf="%", d_suf=" pp", color="inverse", fuente='ArgentinaDatos · cálculo propio')),
        "reservas": ("Sector externo", "Reservas (USD M)", _kpi(reservas, dec=0, color="normal", fuente='BCRA')),
        "riesgo": ("Sector externo", "Riesgo país (pb)", _kpi(riesgo, modo="abs", dec=0, d_suf=" pb", color="inverse", d_dec=0, fuente='ArgentinaDatos · EMBI')),
        "badlar": ("Tasas", "BADLAR (TNA)", _kpi(badlar, modo="abs", dec=1, suf="%", d_suf=" pp", color="off", fuente='BCRA')),
        "pases": ("Tasas", "Pases 1 día (TNA)", _kpi(pases, modo="abs", dec=1, suf="%", d_suf=" pp", color="off",
                                                     help="Tasa de pases a un día del BCRA. Consultá la fecha del dato: "
                                                          "la serie puede haber dejado de publicarse.", fuente='BCRA')),
        "uva": ("Tasas", "UVA", _kpi(uva, dec=2, pre="$", color="off", fuente='BCRA')),
        "infl_m": ("Precios", "Inflación mensual", _kpi(infl_m, dec=1, suf="%", color="inverse", **_MES, fuente='INDEC · vía BCRA')),
        "infl_ia": ("Precios", "Inflación interanual", _kpi(infl_ia, dec=1, suf="%", color="inverse", **_MES, fuente='INDEC · vía BCRA')),
        "rem": ("Precios", "Inflación esperada 12 m", _kpi(rem, dec=1, suf="%", color="inverse", **_MES, fuente='BCRA')),
        "emae_m": ("Actividad", "Actividad mensual", _kpi(emae_m, dec=1, suf="%", color="normal",
                                                        help="EMAE desestacionalizado, variación contra el mes anterior", **_MES, fuente='INDEC · cálculo propio')),
        "emae": ("Actividad", "EMAE interanual", _kpi(emae_ia, dec=1, suf="%", color="normal", **_MES, fuente='INDEC')),
        "paro": ("Actividad", "Desocupación (EPH)", _kpi(paro_pct, dec=1, suf="%", color="inverse", dias=80, modo="abs",
                                                          d_suf=" pp", d_txt="vs trim. ant.", fuente='INDEC · EPH')),
        "sal_nom": ("Ingresos", "Salarios interanual", _kpi(sal_ia, dec=1, suf="%", color="normal",
                                                            help="Índice de salarios INDEC, total", **_MES, fuente='INDEC')),
        "salario_real": ("Ingresos", "Salario real interanual", _kpi(sal_real_df, "real", dec=1, suf="%", color="normal",
                                                                     help="Salarios nominales descontada la inflación", **_MES, fuente='INDEC · cálculo propio')),
        "ripte": ("Ingresos", "RIPTE", _kpi(ripte, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.", fuente='Secretaría de Trabajo · datos.gob.ar')),
        "smvm": ("Ingresos", "Salario mínimo", _kpi(smvm, dias=25, dec=0, pre="$", color="normal", d_txt="vs mes ant.", fuente='Secretaría de Trabajo · datos.gob.ar')),
        "haber": ("Ingresos", "Haber mínimo jubilatorio", _kpi(haber_min, dias=25, dec=0, pre="$", color="normal",
                                                               d_txt="vs mes ant.", fuente='ANSES · datos.gob.ar')),
    }
