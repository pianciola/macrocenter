# Revisión del modo celular

## Alcance

- Las 12 pestañas del tablero, las 3 secciones de inversiones, las 3 de historia y las 3 herramientas.
- Anchos reales de contenido del navegador de 320, 390 y 430 píxeles; temas claro y oscuro.
- 63 recorridos de las 21 vistas en tres configuraciones: 320 oscuro, 390 oscuro y 430 claro. Cuatro recorridos adicionales en 390 claro.
- Términos y privacidad en 390 claro, y tres pantallas en horizontal, 844 × 390: 72 comprobaciones registradas, incluyendo repeticiones.
- Comprobación adicional de escritorio a 1300 px para descartar regresiones.

La evidencia de geometría y carga quedó en `.pytest_cache/auditoria-movil-20261017.json`. El ancho se comprobó con `innerWidth`, compensando el zoom del navegador; no se confundió el tamaño solicitado a la herramienta con el ancho CSS efectivo.

## Problemas encontrados y corregidos

| Problema | Corrección |
|---|---|
| La reserva de espacio para el menú restaba 52 px a los paneles completos. | Se limita el ancho del listado de pestañas, conservando los paneles al 100 %. En 320 px el panel recuperó de 232 a 284 px. |
| En horizontal, la flecha derecha invadía el texto del carrusel. | Carriles separados para texto, flechas y menú; sin pérdida de ancho del contenido. |
| Cifras fiscales truncadas con puntos suspensivos y variaciones partidas en demasiadas líneas. | Indicadores en una columna cuando el contenido disponible es de hasta 340 px; cifras completas y capaces de envolver su unidad. Se mantienen dos columnas cuando caben. |
| Botones, períodos y enlaces CSV con alturas de 26–32 px. | Controles principales de 44 px en pantallas pequeñas y dispositivos de puntero táctil. Ayudas secundarias con al menos 32 px. |
| El pie perdía espacio y sus controles eran difíciles de pulsar en teléfonos pequeños. | Controles de 44 px; suscripción como icono con nombre accesible en anchos de hasta 360 px, manteniendo el espacio para la interfaz de Streamlit Cloud. |
| El tirador de fecha de Viaje en el tiempo medía 12 px. | Zona táctil de 44 px con separación respecto de los bordes. |
| Apertura y cierre del menú lateral sin nombre accesible claro. | Etiquetas explícitas y objetivos de 44 px. |
| Destinos del menú de secciones con una zona de enlace pequeña. | Filas de 44 px, sección actual identificada y desplazamiento vertical propio del panel, también en horizontal. |

El input de rango que React Aria mantiene dentro de un contenedor oculto de 1 px no es un desborde visible. Se inspeccionaron sus ancestros y su recorte antes de clasificarlo como esperado.

## Pruebas interactivas

- Abrir el menú lateral, elegir Herramientas y comprobar su cierre automático.
- Abrir el menú de secciones en horizontal, desplazarlo y acceder al último destino.
- Cambiar el monto de inversiones a $250.000 y el período a tres meses: resultado y encabezado recalculados.
- Cambiar monto, índice y frecuencia del alquiler: resultado recalculado.
- Mover la fecha de Viaje en el tiempo mediante el teclado.
- Abrir tablas y desplazar horizontalmente la de exchanges: el cuadro desplaza su contenido y la página conserva su ancho.
- Abrir Acerca de y comprobar que su contenido cabe.
- Ocultar y restaurar la barra inferior.

## Verificación y límites

Suite local: 62 pruebas aprobadas; 33 pruebas de red opcionales omitidas. Compilación de Python verificada. El recorrido manual de la app se realizó por separado.

Esta revisión usa un navegador con anchos móviles. No sustituye una prueba en un teléfono físico con Safari o Chrome, teclado virtual, gestos del sistema y áreas seguras reales. No se cambiaron cálculos, fuentes de datos, preferencias ni credenciales.
