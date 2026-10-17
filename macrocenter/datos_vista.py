"""Metadatos visibles de las observaciones, sin consultas adicionales de red."""
from __future__ import annotations

from html import escape
import pandas as pd


def detalle(serie, fuente: str, *, hoy=None, max_dias: int | None = None,
            frecuencia: str = "", unidad: str = "", definicion: str = "", nombre: str = "") -> str:
    ficha = ""
    campos = [("Frecuencia", frecuencia), ("Unidad", unidad), ("Qué mide", definicion)]
    if any(v for _, v in campos):
        filas = "".join(f'<dt>{escape(k)}</dt><dd>{escape(v)}</dd>' for k, v in campos if v)
        ficha = (f'<details class="mc-ficha"><summary>Ficha del indicador'
                 f'{": " + escape(nombre) if nombre else ""}</summary><dl>{filas}</dl></details>')
    def sin_fecha():
        return (f'<div class="mc-dato-meta"><span>Fuente: {escape(fuente)}</span>'
                f'<span>Fecha no disponible</span>{ficha}</div>')
    if not isinstance(serie, pd.DataFrame) or "fecha" not in serie:
        return sin_fecha() if fuente or ficha else ""
    hoy = pd.Timestamp(hoy) if hoy is not None else pd.Timestamp.now(tz="America/Argentina/Buenos_Aires")
    hoy = hoy.tz_localize(None).normalize() if hoy.tzinfo else hoy.normalize()
    def local(valor):
        fecha = pd.to_datetime(valor, errors="coerce")
        if pd.isna(fecha):
            return pd.NaT
        return fecha.tz_convert("America/Argentina/Buenos_Aires").tz_localize(None) if fecha.tzinfo else fecha
    try:
        fechas = pd.to_datetime(serie["fecha"], errors="coerce", format="mixed")
        if isinstance(fechas.dtype, pd.DatetimeTZDtype):
            fechas = fechas.dt.tz_convert("America/Argentina/Buenos_Aires").dt.tz_localize(None)
        elif not pd.api.types.is_datetime64_any_dtype(fechas):
            fechas = pd.to_datetime(serie["fecha"].map(local))
    except (ValueError, TypeError):
        fechas = pd.to_datetime(serie["fecha"].map(local))
    fechas = fechas.dropna().drop_duplicates().sort_values()
    fechas = fechas[fechas <= hoy + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)]
    if fechas.empty:
        return sin_fecha()
    paso = fechas.diff().dt.total_seconds().div(86400).median() if len(fechas) > 1 else float("nan")
    limite = max_dias if max_dias is not None else (10 if paso <= 3 else 120 if paso <= 45 else 180 if paso <= 120 else 550)
    ultima = fechas.iloc[-1]
    aviso = '<span class="mc-dato-atrasado">Dato con rezago</span>' if (hoy - ultima.normalize()).days > limite else ""
    return (f'<div class="mc-dato-meta"><span>Fuente: {escape(fuente)}</span>'
            f'<span>Último dato: {ultima:%d/%m/%Y}</span>{aviso}{ficha}</div>')


# Frecuencia de la observación publicada; no es el intervalo de consulta de la web.
FICHAS = {
    "Dólar oficial": ("Diaria", "ARS por USD", "Precio de venta minorista del dólar oficial."),
    "Dólar blue": ("Diaria", "ARS por USD", "Precio de venta de referencia en el mercado informal."),
    "Dólar MEP": ("Diaria", "ARS por USD", "Tipo de cambio implícito de operaciones con bonos liquidadas en el país."),
    "Dólar CCL": ("Diaria", "ARS por USD", "Tipo de cambio implícito de operaciones con liquidación en el exterior."),
    "Brecha blue / oficial": ("Diaria", "%", "(Dólar blue / dólar oficial − 1) × 100. Su cambio se expresa en puntos porcentuales."),
    "Reservas (USD M)": ("Diaria", "Millones de USD", "Reservas internacionales brutas del BCRA; no equivale a reservas netas disponibles."),
    "Riesgo país (pb)": ("Diaria", "Puntos básicos", "Diferencial de rendimiento de deuda soberana frente a bonos del Tesoro estadounidense; 100 pb equivalen a 1 punto porcentual."),
    "BADLAR (TNA)": ("Diaria", "% nominal anual", "Tasa BADLAR de depósitos a plazo fijo de bancos privados. No es una tasa efectiva anual."),
    "Pases 1 día (TNA)": ("Diaria mientras se publicaba", "% nominal anual", "Tasa histórica de pases a un día del BCRA. Revisá la fecha: puede tratarse de una serie discontinuada."),
    "UVA": ("Diaria", "ARS por UVA", "Unidad de Valor Adquisitivo que se actualiza con el CER, vinculado a la inflación con rezago."),
    "Inflación mensual": ("Mensual", "%", "Variación del IPC nacional respecto del mes anterior."),
    "Inflación interanual": ("Mensual", "%", "Variación del IPC nacional respecto del mismo mes del año anterior."),
    "Inflación esperada 12 m": ("Mensual", "%", "Expectativa de inflación a 12 meses relevada en el REM del BCRA. Es una expectativa, no inflación observada."),
    "Actividad mensual": ("Mensual", "%", "Variación del EMAE desestacionalizado frente al mes anterior. La serie puede revisarse."),
    "EMAE interanual": ("Mensual", "%", "Variación del Estimador Mensual de Actividad Económica frente al mismo mes del año anterior."),
    "Desocupación (EPH)": ("Trimestral", "% de la población económicamente activa", "Personas sin ocupación que buscan trabajo. EPH del INDEC, 31 aglomerados urbanos."),
    "Salarios interanual": ("Mensual", "%", "Variación interanual del índice de salarios total del INDEC."),
    "Salario real interanual": ("Mensual", "%", "Variación salarial descontada la inflación: ((1 + variación nominal) / (1 + inflación) − 1) × 100, con ambas tasas en decimales."),
    "RIPTE": ("Mensual", "ARS por mes", "Remuneración imponible promedio de trabajadores estables; no representa a todos los trabajadores."),
    "Salario mínimo": ("Mensual", "ARS por mes", "Salario mínimo vital y móvil mensual para jornada completa."),
    "Haber mínimo jubilatorio": ("Mensual", "ARS por mes", "Haber mínimo del régimen general; no incluye bonos extraordinarios."),
}

# Nombres usados en las vistas de detalle: misma definición que en Resumen.
for alias, original in {
    "Esperada 12 meses (REM)": "Inflación esperada 12 m", "EMAE · var. mensual": "Actividad mensual",
    "EMAE · var. interanual": "EMAE interanual", "Salarios · var. interanual": "Salarios interanual",
    "Salario real · interanual": "Salario real interanual", "Riesgo país": "Riesgo país (pb)",
}.items():
    FICHAS[alias] = FICHAS[original]
FICHAS.update({
    "PBI · var. interanual": ("Trimestral", "%", "Variación del PBI a precios constantes frente al mismo trimestre del año anterior."),
    "Base monetaria": ("Diaria", "Billones de ARS", "Efectivo en circulación y depósitos de los bancos en el BCRA. Monto nominal, sin descontar inflación."),
    "M2 privado · var. interanual": ("Diaria", "%", "Variación interanual del promedio móvil de 30 días del M2 privado: efectivo y depósitos a la vista privados."),
    "Préstamos al sector privado": ("Diaria", "Billones de ARS", "Saldo de préstamos al sector privado. Monto nominal, sin descontar inflación."),
    "Exportaciones del mes (USD M)": ("Mensual", "Millones de USD", "Valor de las exportaciones de bienes del mes, según el intercambio comercial argentino del INDEC."),
    "Importaciones del mes (USD M)": ("Mensual", "Millones de USD", "Valor de las importaciones de bienes del mes. Una suba no se interpreta automáticamente como una mejora o un deterioro."),
    "Saldo del mes (USD M)": ("Mensual", "Millones de USD", "Exportaciones menos importaciones de bienes del mes."),
    "Saldo 12 meses (USD M)": ("Mensual", "Millones de USD", "Suma de los saldos comerciales de los últimos doce meses."),
    "IPIM · mensual": ("Mensual", "%", "Variación mensual del Índice de Precios Internos al por Mayor del INDEC."),
    "IPIM · interanual": ("Mensual", "%", "Variación del IPIM frente al mismo mes del año anterior."),
    "IPP · mensual": ("Mensual", "%", "Variación mensual del Índice de Precios al Productor del INDEC."),
    "Máximo del período (USD M)": ("Diaria", "Millones de USD", "Mayor nivel de reservas brutas registrado en el período seleccionado."),
})
