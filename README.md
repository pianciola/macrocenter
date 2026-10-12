# MacroCenter

Tablero de datos macroeconómicos de Argentina hecho con Streamlit + Plotly.

## Cómo correrlo

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

En Windows alcanza con hacer doble clic en `run.bat` (una vez creado el entorno).
Si cambiás el código, cerrá y volvé a abrir `run.bat`: Streamlit no recarga los módulos de `macrocenter/`.

## Qué muestra

| Pestaña | Contenido |
|---|---|
| Inicio | Indicadores clave personalizables, un gráfico a elección |
| Calificación | Nota 0-100 hoy vs. hace 3 m / 6 m / 1 año / 2 años, evolución, detalle por pilar y driver |
| Salarios | Índice de salarios INDEC, salario real vs inflación, RIPTE, salario mínimo, haber mínimo |
| Cripto | Principales criptomonedas en USD y pesos, historial por moneda y precio del USDT en cada exchange argentino |
| Bolsas | Merval, bolsas de EE. UU., Europa, Asia y Latinoamérica, más oro, petróleo y soja; comparación base 100 |
| Dólar | Los 7 dólares (oficial, mayorista, blue, MEP, CCL, cripto, tarjeta) con compra, venta, variación y brecha; euro y libra esterlina (referencia BCRA); gráficos y brecha cambiaria |
| Reservas | Reservas brutas del BCRA y variación mensual |
| Actividad y PBI | PBI trimestral, EMAE (original y desestacionalizado), desocupación |
| Precios y UVA | Inflación mensual/interanual, REM, UVA, CER, UVI, ICL, UVA vs dólar |
| Tasas y riesgo país | BADLAR, TAMAR, plazo fijo, préstamos personales, riesgo país |
| Dinero y crédito | Base monetaria, M2 privado, préstamos al sector privado |
| Comercio exterior | Exportaciones, importaciones, saldo comercial |

## Navegación: Tablero, Ahorro e inversiones, Herramientas e Historia económica

La barra lateral tiene una sección **Explorar** que cambia la pantalla principal entre el **Tablero** (con sus pestañas),
**Ahorro e inversiones**, las **Herramientas** y la **Historia económica**. Las tres últimas no ocupan pestañas; se
vuelve con *← Volver al tablero*.

## Ahorro e inversiones

Sección informativa (`macrocenter/inversiones.py`), sin recomendaciones: las listas van por orden alfabético y cada
pantalla aclara sus supuestos.

- **Tasas de hoy**: plazo fijo a 30 días por banco, fondos money market (rendimiento de los últimos 30 días) y
  rendimientos que informan billeteras y plataformas, contra la inflación esperada (REM del BCRA). Datos de ArgentinaDatos.
- **Cómo les fue**: cuánto valdría hoy un monto invertido hace 1 mes a 5 años en plazo fijo, UVA, dólar MEP, Merval,
  S&P 500 y bitcoin, contra la inflación (CER).
- **Plazo fijo vs. UVA**: calculadora con la inflación de empate entre los dos.
- **Conceptos**: los términos básicos, tomados del glosario.

## Historia económica (línea de tiempo)

La sección **Historia económica** (barra lateral → *Explorar*) recorre desde Alfonsín hasta hoy: foto, hito y cómo recibió → cómo dejó la inflación,
el PBI, la desocupación, el dólar, las reservas y el riesgo país. Todo se calcula con las series oficiales
(`macrocenter/presidentes.py`); las fotos se piden en el momento a Wikipedia / Wikimedia Commons. La pestaña explica
los criterios y límites (por ejemplo, la inflación 2007-2015 es la del INDEC intervenido).

## Interactivo

La sección **Herramientas** (barra lateral → *Explorar*; `macrocenter/interactivo.py`) tiene cuatro herramientas y la calificación macro, de a una por vez:

- **¿Cuánto valían tus pesos?** — un monto y una fecha (desde 1992): qué fue de esa plata según la inflación, el dólar
  oficial y la UVA.
- **Comparador de épocas** — dos momentos cualesquiera (asunciones, hoy u otra fecha) lado a lado.
- **Ajuste de alquileres** — monto inicial, fecha de inicio y frecuencia: cronograma de ajustes y alquiler actual según
  ICL, IPC nacional, IPC GBA, CER o salarios, y el mismo contrato comparado con cada índice.
- **Viaje en el tiempo** — un deslizador de fecha (1984 a hoy) que muestra quién gobernaba y cómo estaba el país, con
  botón para reproducirlo hasta hoy.

## Período de los gráficos

Cada gráfico importante (el de Inicio, el del dólar, el de reservas y el de bolsas) tiene sus propios botones de período.

## Indicadores personalizables

En Inicio, **Personalizar** permite elegir cuáles de los ~20 indicadores se muestran en "Indicadores clave"
y en qué orden. La elección se guarda en `.macrocenter_prefs.json` (junto a `app.py`); borrar ese archivo
restablece los de siempre. Para sumar uno al catálogo, agregarlo en `CATALOGO` dentro de `app.py`.

## Franja superior

Arriba de todo desliza una franja con datos clave (dólares, euro, riesgo país, reservas, inflación, cripto, bolsas). Se frena al pasar el mouse.

## Noticias

El botón **Noticias BCRA y Economía** de la barra lateral abre una ventana con las últimas novedades del Banco
Central y del Ministerio de Economía. Ninguno ofrece API ni RSS de noticias, así que se lee el listado público de
cada sitio (`macrocenter/news.py`); si cambian el diseño, la ventana avisa y deja el enlace a la fuente.

## Modo oscuro

Menú **⋮ → Settings → Theme**: *Light*, *Dark* o *Use system setting* (por defecto sigue al sistema). Las paletas
están definidas en `.streamlit/config.toml`.

## Calificación macro

Cada driver (inflación, REM, reservas, riesgo país, brecha, saldo comercial, EMAE, desocupación, salario real)
recibe un puntaje de 0 a 100 según qué tan bien queda su valor frente a su propia historia de los últimos
5 años (percentil, invertido si "menos es mejor"). Se promedian por pilar (Precios, Externo, Actividad,
Ingresos) y los pilares, con igual peso, dan la nota total. El mismo cálculo "a una fecha pasada" permite comparar
con períodos anteriores. Es una medida relativa y descriptiva, no un pronóstico. Ver `macrocenter/score.py`.

Nota: el BCRA no registra tasa de política monetaria después del 10/7/2025; se muestra esa historia y la tasa de
pases a 1 día como referencia vigente.

## Fuentes (APIs públicas, sin clave)

- **BCRA** — API Estadísticas v4.0 (`api.bcra.gob.ar/estadisticas/v4.0`)
- **Datos Argentina** — API de Series de Tiempo (`apis.datos.gob.ar/series/api`): INDEC / MECON
- **ArgentinaDatos** — cotizaciones del dólar y riesgo país (`api.argentinadatos.com`)

El dólar y el riesgo país se consultan cada minuto (DolarApi y ArgentinaDatos), cripto y bolsas cada 5 minutos, y la página abierta se redibuja sola cuando llega algo nuevo. Las series oficiales se cachean 1 hora; el botón *Refrescar datos* (en el pie) fuerza una nueva descarga de todo.

## Agregar un indicador

1. Sumar el id en `BCRA_IDS` o `SERIES_IDS` (`macrocenter/data.py`). El catálogo del BCRA se lista en
   `https://api.bcra.gob.ar/estadisticas/v4.0/monetarias`; las series del INDEC se buscan en
   `https://apis.datos.gob.ar/series/api/search/?q=...`.
2. Se descarga solo con `cargar_todo()`; graficarlo con `charts.lineas` / `charts.barras` en `app.py`.

## Publicarla en internet (Streamlit Community Cloud)

1. Subir esta carpeta a un repositorio de GitHub (el `.gitignore` ya deja afuera el entorno `.venv`, las preferencias y el caché).
2. En https://share.streamlit.io: *Create app*, elegir el repositorio, rama `main` y archivo principal `app.py`. Usa `requirements.txt`.
3. Antes de difundirla: completar `CONTACTO` y `DOMICILIO` en `macrocenter/legal.py` y hacer revisar los textos legales.

Publicada, no se guardan archivos de preferencias: lo que cada visitante elige (indicadores, noticias leídas) vale solo para
su sesión. `run.bat` define `MACROCENTER_LOCAL=1`, que activa el guardado local y limita el acceso a esta computadora.

## Robustez

Si una fuente se cae o devuelve datos raros, esa parte muestra un aviso y el resto de la página sigue funcionando; las fallas no quedan pegadas en el caché (se reintenta cada minuto).
Se probó con caídas de red, respuestas corruptas, datos nulos, ceros, duplicados y desordenados, entradas extremas, preferencias rotas y ráfagas de clics.
