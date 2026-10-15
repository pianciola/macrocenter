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

Orden de las pestañas: Resumen, después el ala financiera (Dólar, Bolsas, Cripto, Tasas y riesgo país, Dinero y crédito) y
luego Inflación, Actividad y PBI, Reservas, Salarios, Resultado fiscal y Comercio exterior. Cada una vive en su archivo
de `macrocenter/pestanas/`.

| Pestaña | Contenido |
|---|---|
| Resumen | Indicadores clave personalizables, un gráfico a elección |
| Salarios | Índice de salarios INDEC, salario real vs inflación, RIPTE, salario mínimo, haber mínimo; pobreza (EPH, por semestre) y canastas básicas de una familia tipo |
| Cripto | Principales criptomonedas en USD y pesos, historial por moneda y precio del USDT en cada exchange argentino |
| Bolsas | Merval, bolsas de EE. UU., Europa, Asia y Latinoamérica, más oro, petróleo y soja; comparación base 100 |
| Dólar | Los 7 dólares (oficial, mayorista, blue, MEP, CCL, cripto, tarjeta) con compra, venta, variación y brecha; euro y libra esterlina (referencia BCRA); gráficos y brecha cambiaria; formulario para anotarse en las alertas por mail |
| Reservas | Reservas brutas del BCRA y variación mensual; balance cambiario (cuenta corriente, cuenta financiera y compra neta de dólares de personas y empresas) |
| Actividad y PBI | PBI trimestral, EMAE (original y desestacionalizado), desocupación |
| Inflación | Inflación mensual/interanual, REM, por región (INDEC) y por provincia (Ciudad de Buenos Aires, Santa Fe, Mendoza, Tucumán, San Luis, Chaco y Neuquén; una provincia con más de 6 meses sin publicar no se muestra), UVA, CER, UVI, ICL, dólar vs inflación |
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
- **Rendimientos pasados**: cuánto valdría hoy un monto invertido hace 1 mes a 5 años en plazo fijo, UVA, dólar MEP, Merval,
  S&P 500 y bitcoin, contra la inflación (CER).
- **Plazo fijo vs. UVA**: calculadora con la inflación de empate entre los dos.
- **Glosario**: los términos básicos, tomados del glosario de la app.

## Historia económica (línea de tiempo)

La sección **Historia económica** (barra lateral → *Explorar*) recorre desde Alfonsín hasta hoy: foto, hito y cómo recibió → cómo dejó la inflación,
el PBI, la desocupación, el dólar, las reservas y el riesgo país. Todo se calcula con las series oficiales
(`macrocenter/presidentes.py`); las fotos se piden en el momento a Wikipedia / Wikimedia Commons. La pestaña explica
los criterios y límites (por ejemplo, la inflación 2007-2015 es la del INDEC intervenido).

## Interactivo

La sección **Herramientas** (barra lateral → *Explorar*; `macrocenter/interactivo.py`) tiene cuatro herramientas, de a una por vez:

- **¿Cuánto valían tus pesos?** — un monto y una fecha (desde 1992): qué fue de esa plata según la inflación, el dólar
  oficial y la UVA.
- **Comparador de épocas** — dos momentos cualesquiera (asunciones, hoy u otra fecha) lado a lado.
- **Ajuste de alquileres** — monto inicial, fecha de inicio y frecuencia: cronograma de ajustes y alquiler actual según
  ICL, IPC nacional, IPC GBA, CER o salarios, y el mismo contrato comparado con cada índice.
- **Viaje en el tiempo** — un deslizador de fecha (1984 a hoy) que muestra quién gobernaba y cómo estaba el país, con
  botón para reproducirlo hasta hoy.

## Período de los gráficos y descargas

Cada gráfico importante (el de Resumen, el del dólar, el de reservas y el de bolsas) tiene sus propios botones de período.
Cada gráfico tiene al lado del título un botón **CSV** que baja sus datos para Excel (punto y coma, coma decimal).

## Enlaces para compartir

La dirección sigue a lo que se mira: `?ver=tablero/dolar`, `?ver=herramientas/ajuste-de-alquileres`,
`?ver=inversiones/glosario`, etc. Copiarla y mandarla abre la misma pantalla. Un enlace inválido abre el tablero.

## Indicadores personalizables

En Resumen, **Personalizar** permite elegir cuáles de los ~20 indicadores se muestran en "Indicadores clave"
y en qué orden. La elección se guarda en `.macrocenter_prefs.json` (junto a `app.py`); borrar ese archivo
restablece los de siempre. Para sumar uno al catálogo, agregarlo en `CATALOGO` dentro de `app.py`.

## Franja superior

Arriba de todo desliza una franja con datos clave (dólares, euro, riesgo país, reservas, inflación, cripto, bolsas). Se frena al pasar el mouse.

## Noticias

El botón **Noticias** de la barra lateral abre una ventana con las últimas novedades del Banco Central, del
Ministerio de Economía y del INDEC (sus informes técnicos, según el calendario de difusión). Ninguno ofrece API ni
RSS de noticias, así que se lee el listado público de cada sitio (`macrocenter/news.py`); si cambian el diseño, la ventana avisa y deja el enlace a la fuente.

## Modo oscuro

Menú **⋮ → Settings → Theme**: *Light*, *Dark* o *Use system setting* (por defecto sigue al sistema). Las paletas
están definidas en `.streamlit/config.toml`.

Nota: el BCRA no registra tasa de política monetaria después del 10/7/2025; se muestra esa historia y la tasa de
pases a 1 día como referencia vigente.

## Fuentes (APIs públicas, sin clave)

- **BCRA** — API Estadísticas v4.0 (`api.bcra.gob.ar/estadisticas/v4.0`)
- **Datos Argentina** — API de Series de Tiempo (`apis.datos.gob.ar/series/api`): INDEC / MECON
- **ArgentinaDatos** — cotizaciones del dólar y riesgo país (`api.argentinadatos.com`)

El dólar y el riesgo país se consultan cada 30 segundos (DolarApi y CriptoYa, quedándose con el dato más reciente de cada dólar; ArgentinaDatos), cripto y bolsas cada 5 minutos, y la página abierta se redibuja sola cuando llega algo nuevo. Las series oficiales se cachean 1 hora; el botón *Refrescar datos* (en el pie) fuerza una nueva descarga de todo.

## Pie de página

Una barra fina queda siempre pegada al borde inferior de la ventana, en cualquier pestaña o pantalla: estado en vivo,
suscripción al resumen semanal, términos, privacidad, el panel **Acerca de** (marca, fuentes de datos, aviso de
rezago) y *Refrescar datos*. Lo secundario se oculta según el ancho real disponible; los botones nunca se achican.

## Agregar un indicador

1. Sumar el id en `BCRA_IDS` o `SERIES_IDS` (`macrocenter/data.py`). El catálogo del BCRA se lista en
   `https://api.bcra.gob.ar/estadisticas/v4.0/monetarias`; las series del INDEC se buscan en
   `https://apis.datos.gob.ar/series/api/search/?q=...`.
2. Se descarga solo con `cargar_todo()`; graficarlo con `charts.lineas` / `charts.barras` en la pestaña que corresponda
   (`macrocenter/pestanas/`). Si la función de la pestaña necesita algo nuevo de `app.py`, se suma como parámetro de
   `mostrar` (después del asterisco) y `abrir` se lo pasa solo.

## Publicarla en internet (Streamlit Community Cloud)

1. Subir esta carpeta a un repositorio de GitHub (el `.gitignore` ya deja afuera el entorno `.venv`, las preferencias y el caché).
2. En https://share.streamlit.io: *Create app*, elegir el repositorio, rama `main` y archivo principal `app.py`. Usa `requirements.txt`.
3. Antes de difundirla: completar `CONTACTO` y `DOMICILIO` en `macrocenter/legal.py` y hacer revisar los textos legales.

Publicada, no se guardan archivos de preferencias: lo que cada visitante elige (indicadores) vale solo para su sesión.
Las noticias leídas las recuerda el propio navegador en su almacenamiento local (`mc_leidas`: identificadores de 8
caracteres, sin datos personales). `run.bat` define `MACROCENTER_LOCAL=1`, que activa el guardado local y limita el acceso a esta computadora.

## Robustez

Si una fuente se cae o devuelve datos raros, esa parte se omite sin mostrar ningún aviso de error al visitante y el resto de la página sigue funcionando; las fallas quedan registradas (macrocenter/avisos.py) y el monitor te avisa por mail. No quedan pegadas en el caché: se reintenta cada minuto, y si la fuente devuelve una serie vacía se usa el último dato bueno guardado.
Con el servidor recién prendido, las descargas en vivo (dólar, cripto, bolsas, noticias) arrancan todas juntas y en paralelo con las series. Si CoinGecko limita pedidos, el historial de cada cripto sale de Yahoo Finance (y si ambos fallan, del último historial bueno).
Se probó con caídas de red, respuestas corruptas, datos nulos, ceros, duplicados y desordenados, entradas extremas, preferencias rotas y ráfagas de clics.
Si la API de datos.gob.ar devuelve una serie sin sus últimos meses (pasa: guarda respuestas viejas), se completa con el
archivo oficial de esa serie en la misma plataforma.

## Copia de respaldo

Cada 3 horas GitHub Actions baja todas las series (`monitor/semilla.py`) y deja una copia en la rama `datos`
(`semilla.json.gz`, JSON comprimido: leerla no puede ejecutar código). Con el servidor recién prendido la página arranca
con esa copia y actualiza de fondo, y si una fuente se cae usa su último dato de ahí. Publicar en `datos` no reinicia la
página (Streamlit Cloud solo mira `main`).

## Alertas por mail

En la pestaña Dólar hay un campo para anotarse: el mail va directo del navegador a Buttondown con la etiqueta
`alertas` (la página no lo ve). Cada 30 minutos, de lunes a viernes de 10 a 18, `monitor/alertas.py` revisa si el
dólar oficial se movió 2 % o más contra el cierre anterior, el blue, el MEP o el CCL 3 % o más, o el riesgo país 5 % o
más, y avisa una vez por día por instrumento. El mail se crea como borrador con el filtro de la etiqueta y solo se manda
si Buttondown confirma ese filtro: nunca le llega a toda la lista por error.

## Pruebas y monitor

- `python -m pytest tests` corre las pruebas sin red; con `MACROCENTER_RED=1` también la app entera con datos reales.
  GitHub las corre en cada publicación (`.github/workflows/pruebas.yml`).
- El monitor (cada 6 horas) revisa la página, que cada fuente responda, que **ninguna serie esté desactualizada** para
  su frecuencia (diaria: 10 días; mensual: 180; trimestral: 300; anual: 900) y que todas las pantallas se dibujen. Si
  algo falla, GitHub te manda un mail.
