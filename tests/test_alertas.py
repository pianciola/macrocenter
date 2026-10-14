"""Cuándo se dispara una alerta y cómo se redacta (sin red ni Buttondown)."""
import pandas as pd

from macrocenter import alertas

HOY = pd.Timestamp("2026-10-14")


def _ahora(**ventas):
    return pd.DataFrame([{"casa": c, "compra": v, "venta": v, "actualizado": pd.Timestamp("2026-10-14 11:30")}
                         for c, v in ventas.items()])


HIST = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-10", "2026-10-13", "2026-10-14"]),
                     "oficial": [1500.0, 1500.0, 1600.0], "blue": [1500.0, 1550.0, 9999.0],
                     "bolsa": [1500.0, 1500.0, 1500.0]})


def test_avisa_solo_lo_que_supera_su_umbral_contra_el_cierre_anterior():
    r = alertas.detectar(_ahora(oficial=1520, blue=1600, bolsa=1450), HIST, None, None, HOY)
    # oficial +1,3% (umbral 2%) no; blue +3,2% contra 1.550 (el dato de hoy del historial no cuenta) sí;
    # MEP -3,3% sí
    assert [a["clave"] for a in r] == ["blue", "bolsa"]
    assert round(r[0]["var"], 1) == 3.2 and r[0]["antes"] == 1550


def test_un_dato_de_otro_dia_no_dispara_nada():
    viejo = _ahora(blue=2000).assign(actualizado=pd.Timestamp("2026-10-13 17:00"))
    assert alertas.detectar(viejo, HIST, None, None, HOY) == []


def test_riesgo_pais():
    ahora = pd.DataFrame({"fecha": [HOY], "valor": [945.0]})
    hist = pd.DataFrame({"fecha": pd.to_datetime(["2026-10-13"]), "valor": [900.0]})
    r = alertas.detectar(None, None, ahora, hist, HOY)
    assert r and r[0]["clave"] == "riesgo"
    assert alertas.frase(r[0]) == "Riesgo país: subió 5,0% respecto del cierre anterior, de 900 puntos a 945 puntos."


def test_frase_neutra_y_formato_argentino():
    a = dict(clave="blue", nombre="Dólar blue", antes=1550.0, ahora=1480.0, var=-4.516)
    assert alertas.frase(a) == "Dólar blue: bajó 4,5% respecto del cierre anterior, de $1.550 a $1.480."


def test_cada_instrumento_se_avisa_una_vez_por_dia():
    s = alertas.asunto([dict(nombre="Dólar blue"), dict(nombre="Dólar MEP")], HOY)
    assert s == "Alerta MacroCenter 14/10: Dólar blue, Dólar MEP"
    assert alertas.ya_avisadas([s, "Alerta MacroCenter 13/10: Riesgo país", "Resumen semanal"], HOY) == \
        {"Dólar blue", "Dólar MEP"}


def test_el_cuerpo_escapa_html():
    c = alertas.cuerpo([dict(clave="blue", nombre="<b>x</b>", antes=1.0, ahora=2.0, var=100.0)], "11:30",
                       "https://a.b/?ver=tablero/dolar")
    assert "<b>x</b>" not in c and "&lt;b&gt;" in c


def test_monitor_solo_manda_si_el_filtro_quedo_confirmado():
    import alertas as monitor_alertas  # monitor/alertas.py

    bueno = {"filters": monitor_alertas.filtro("tag_1")}
    assert monitor_alertas.filtro_confirmado(bueno, "tag_1")
    assert not monitor_alertas.filtro_confirmado({"filters": {}}, "tag_1")
    assert not monitor_alertas.filtro_confirmado({}, "tag_1")
    assert not monitor_alertas.filtro_confirmado(bueno, "tag_2")
    o = {"filters": {**monitor_alertas.filtro("tag_1"), "predicate": "or"}}
    assert not monitor_alertas.filtro_confirmado(o, "tag_1")
