# MacroCenter

Tablero de la economía argentina hecho con Streamlit + Plotly, de Juan Manuel Pianciola. En vivo: https://macrocenter-argentina.streamlit.app/ · Repo: github.com/pianciola/macrocenter · Local: `run.bat`. Responder siempre en español.

## Reglas del dueño (no negociables)
- **Privacidad y seguridad:** la página no puede comprometer datos de los visitantes ni ser fácil de vulnerar. Los mails los guarda solo Buttondown; la página nunca los ve.
- **Datos personales del dueño:** solo se muestra el contacto juanpianciola06@gmail.com y el domicilio «Ciudad Autónoma de Buenos Aires». Nada más.
- **Datos por API:** no cargar datos a mano; todo sale de las APIs públicas.
- **Colores:** verde = bueno, rojo = malo. Excepción: cotizaciones (verde sube, rojo baja).
- **Neutralidad:** los textos no juzgan; informan.
- **Sin avisos de error para el visitante:** las fallas se registran (`macrocenter/avisos.py`), no se muestran.
- **Clave de Buttondown:** vive en el secreto de GitHub `BUTTONDOWN_API_KEY`. Nunca pedirla ni escribirla.

## Estructura
- `app.py`: orquesta la página (barra lateral, pie fijo, pestañas, estado compartido). `abrir()` le pasa a cada pantalla, por nombre, lo que su `mostrar(*, ...)` declara.
- `macrocenter/pestanas/`: una pestaña o pantalla por archivo.
- `macrocenter/carga.py`: descarga, cachés compartidos, disco y copia de respaldo.
- `macrocenter/data.py`: fuentes y series (`BCRA_IDS`, `SERIES_IDS`, `tareas_principales`).
- `macrocenter/style.py`: todo el CSS/HTML; `charts.py`: gráficos; `semilla.py` / `alertas.py`: respaldo y alertas.
- `monitor/`: scripts de GitHub Actions. `tests/`: pruebas. `.github/workflows/`: Pruebas, Monitor, Semilla, Alertas, Boletín.

## Cómo trabajar
- Para agregar un indicador: ver README («Agregar un indicador»).
- Después de cambiar `macrocenter/*.py`, reiniciar el servidor local; Streamlit no recarga módulos.
- Probar: `python -m pytest tests` (sin red); con `MACROCENTER_RED=1` también la app entera.
- Publicar: `gh` ya está logueado como pianciola. Clonar el repo en un directorio temporal, copiar los cambios, commit y `git push origin main`.
- **Después de cada push hay que reiniciar la app** en share.streamlit.io (⋮ → Reboot); si no, queda con módulos viejos y falla. Verificar el sitio en vivo.

## Trampas conocidas
- La API de datos.gob.ar guarda respuestas rotas por URL exacta: `data.serie()` prueba variantes y completa con el archivo oficial si faltan meses.
- `position: fixed` no funciona dentro del contenedor principal (usa `container-type`): el pie es `sticky` con `display: contents` en su envoltorio.
- CoinGecko limita pedidos (429): el historial cae a Yahoo Finance.
- Streamlit Cloud: el menú «Manage app», el avatar y la corona no se pueden ocultar desde la app.
