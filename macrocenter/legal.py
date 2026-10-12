"""Términos y Condiciones y Política de Privacidad de MacroCenter.

Redactados conforme al marco normativo argentino aplicable (Ley N.º 25.326 de Protección de los Datos Personales y su
Decreto Reglamentario N.º 1558/2001, Ley N.º 11.723 de Propiedad Intelectual, Ley N.º 24.240 de Defensa del Consumidor,
Código Civil y Comercial de la Nación). Describen lo que la aplicación hace realmente: no tiene registro de usuarios,
formularios ni publicidad; cuenta visitas de forma agregada y sin cookies con GoatCounter; la lista del boletín
semanal por mail (opcional) la guarda Buttondown, nunca la aplicación.

IMPORTANTE: es un texto base. Antes de publicar el sitio en internet de forma abierta conviene que lo revise un/a
abogado/a (en especial el domicilio legal y el medio de contacto, que se completan en CONTACTO y DOMICILIO).
"""
from __future__ import annotations

MARCA = "MacroCenter"
RESPONSABLE = "Juan Manuel Pianciola"
ACTUALIZACION = "12 de octubre de 2026"
CONTACTO = "juanpianciola06@gmail.com"
DOMICILIO = "Ciudad Autónoma de Buenos Aires"

_CONTACTO_TXT = (f"Podés comunicarte a **{CONTACTO}**." if CONTACTO
                 else "Podés comunicarte por el canal de contacto que el responsable del sitio informe en el lugar donde se publique "
                      "esta aplicación.")

TERMINOS = {
    "titulo": "Términos y Condiciones de Uso",
    "intro": (f"Estos Términos y Condiciones regulan el acceso y el uso de **{MARCA}** (en adelante, «el Sitio» o «la Aplicación»), "
              f"un tablero de información macroeconómica de la República Argentina desarrollado y administrado por "
              f"**{RESPONSABLE}** (en adelante, «el Responsable»). Al acceder o utilizar el Sitio, el usuario declara haber leído, "
              "comprendido y aceptado estos Términos. Si no está de acuerdo, deberá abstenerse de utilizarlo."),
    "secciones": [
        ("1. Objeto y descripción del servicio",
         ["El Sitio ofrece, de manera gratuita, la visualización de indicadores económicos y financieros (tipo de cambio, reservas, "
          "inflación, actividad, salarios, tasas, riesgo país, criptoactivos, mercados bursátiles y noticias oficiales), junto con "
          "herramientas de consulta y simulación. La información se obtiene automáticamente de fuentes públicas y se presenta con "
          "fines exclusivamente informativos y educativos."]),
        ("2. Carácter informativo: no constituye asesoramiento",
         ["Nada de lo publicado en el Sitio constituye asesoramiento financiero, de inversión, legal, contable, impositivo ni de "
          "ningún otro tipo, ni una oferta, invitación o recomendación para comprar, vender o mantener activos, divisas, valores "
          "negociables o criptoactivos, en los términos de la Ley N.º 26.831 de Mercado de Capitales y las normas de la Comisión "
          "Nacional de Valores.",
          "El usuario es el único responsable de las decisiones que adopte con base en la información del Sitio y deberá consultar "
          "con profesionales matriculados antes de tomar decisiones económicas."]),
        ("3. Fuentes, exactitud y actualización de los datos",
         ["Los datos provienen de terceros, entre ellos el Banco Central de la República Argentina (BCRA), el Instituto Nacional de "
          "Estadística y Censos (INDEC), el Ministerio de Economía de la Nación, ArgentinaDatos, CoinGecko, CriptoYa, Yahoo Finance y "
          "Wikipedia/Wikimedia Commons. El Responsable no controla esas fuentes ni garantiza que sus datos sean exactos, completos, "
          "oportunos o libres de errores.",
          "Los precios y cotizaciones se muestran **a modo de referencia**, pueden tener demoras o ser revisados por sus emisores, y "
          "no necesariamente reflejan los valores efectivos de una operación. Algunos valores (por ejemplo, el dólar blue, el dólar "
          "cripto y los precios del USDT por plataforma) son relevamientos de terceros y no cotizaciones oficiales. Las series de "
          "inflación del período 2007-2015 corresponden a las cifras oficiales difundidas por el INDEC en ese lapso, cuya "
          "confiabilidad fue cuestionada por diversos analistas."]),
        ("4. Indicadores propios y calificación macroeconómica",
         ["La «calificación macroeconómica», los puntajes, la comparación entre mandatos y demás indicadores elaborados por el "
          "Sitio son medidas **orientativas**, construidas con una metodología propia y con criterios que implican decisiones "
          "discrecionales (ventanas de comparación, ponderaciones, selección de variables). No son una calificación crediticia, "
          "una opinión técnica oficial ni un pronóstico."]),
        ("5. Criptoactivos y riesgos",
         ["La información sobre criptoactivos es meramente informativa. Estos activos presentan una volatilidad elevada y riesgos "
          "específicos, incluida la posible pérdida total del capital. El Sitio no intermedia, custodia ni ejecuta operaciones con "
          "criptoactivos ni con ningún otro activo."]),
        ("6. Propiedad intelectual",
         [f"El diseño, la marca y el logotipo de {MARCA}, el código fuente, la estructura, los textos propios y los indicadores "
          f"elaborados por el Sitio son propiedad de {RESPONSABLE} y están protegidos por la Ley N.º 11.723 de Propiedad Intelectual "
          "y demás normas aplicables. Queda prohibida su reproducción, distribución, modificación o uso comercial sin autorización "
          "previa y por escrito.",
          "Los datos, marcas, imágenes y contenidos de terceros pertenecen a sus respectivos titulares y se utilizan conforme a las "
          "condiciones de cada fuente. Las fotografías de personas públicas provienen de Wikimedia Commons y se rigen por sus "
          "licencias libres."]),
        ("7. Uso permitido",
         ["El usuario se compromete a utilizar el Sitio de buena fe y conforme a la ley. Queda prohibido: (a) intentar acceder sin "
          "autorización a los sistemas, vulnerar o eludir medidas de seguridad; (b) realizar extracciones masivas o automatizadas "
          "que afecten el funcionamiento del Sitio o de las fuentes de datos; (c) introducir código malicioso; (d) presentar "
          "como propia la información o los indicadores del Sitio; y (e) utilizar el Sitio para fines ilícitos."]),
        ("8. Enlaces y contenidos de terceros",
         ["El Sitio puede incluir enlaces a páginas de terceros (organismos oficiales, medios, plataformas). El Responsable no "
          "controla ni responde por su contenido, disponibilidad, políticas de privacidad ni prácticas."]),
        ("9. Disponibilidad del servicio",
         ["El servicio se presta «tal como está» y según disponibilidad. El Responsable no garantiza el funcionamiento ininterrumpido "
          "ni la ausencia de errores, y podrá modificar, suspender o discontinuar total o parcialmente el Sitio en cualquier "
          "momento, sin que ello genere derecho a indemnización."]),
        ("10. Limitación de responsabilidad",
         ["En la máxima medida permitida por la legislación vigente, el Responsable no será responsable por daños directos o "
          "indirectos, lucro cesante, pérdida de oportunidades o de datos derivados del uso o de la imposibilidad de uso del Sitio, "
          "ni de la utilización de información de terceros. Lo dispuesto en esta cláusula no afecta los derechos irrenunciables que "
          "la Ley N.º 24.240 de Defensa del Consumidor y el Código Civil y Comercial de la Nación reconocen a los usuarios que "
          "revistan el carácter de consumidores."]),
        ("11. Protección de datos personales",
         ["El tratamiento de la información se rige por la Política de Privacidad, que forma parte integrante de estos Términos."]),
        ("12. Modificaciones",
         ["El Responsable podrá modificar estos Términos en cualquier momento. La versión vigente será la publicada en el Sitio, "
          "con indicación de su fecha de actualización. El uso continuado del Sitio implica la aceptación de los cambios."]),
        ("13. Ley aplicable y jurisdicción",
         ["Estos Términos se rigen por las leyes de la República Argentina. Toda controversia será sometida a los tribunales "
          "ordinarios competentes de la República Argentina. Cuando el usuario sea consumidor, será competente el tribunal del "
          "lugar de su domicilio o el que resulte de las normas de orden público aplicables."]),
        ("14. Contacto",
         [_CONTACTO_TXT + (f" Domicilio: {DOMICILIO}." if DOMICILIO else "")]),
    ],
}

PRIVACIDAD = {
    "titulo": "Política de Privacidad",
    "intro": (f"La presente Política de Privacidad describe cómo **{MARCA}** trata la información de quienes lo utilizan, en "
              "cumplimiento de la Ley N.º 25.326 de Protección de los Datos Personales, su Decreto Reglamentario N.º 1558/2001 y "
              f"demás normativa aplicable. El responsable del tratamiento es **{RESPONSABLE}**."),
    "secciones": [
        ("1. Qué datos personales recopilamos",
         ["**Ninguno de forma deliberada.** El Sitio no exige registro, no tiene cuentas de usuario ni formularios, y no solicita "
          "nombre, correo electrónico, documento, datos de pago ni ningún otro dato personal. Tampoco incorpora publicidad "
          "ni mecanismos de seguimiento individual del comportamiento de los usuarios. La única excepción es el boletín "
          "semanal opcional, que gestiona un tercero y se describe más abajo.",
          "Para saber cuántas personas usan el Sitio y qué secciones resultan más útiles, se cuentan las visitas de forma "
          "**agregada y anónima** con **GoatCounter** (goatcounter.com), un servicio de estadísticas que **no usa cookies** ni "
          "identifica a las personas. Registra la sección visitada, la página de procedencia, el tipo de navegador y de sistema "
          "operativo, el tamaño de pantalla y el país aproximado (deducido de la dirección IP, que no se guarda). Para distinguir "
          "visitas únicas usa un identificador temporal que no permite reconocer a nadie y se descarta a las pocas horas. El "
          "Responsable solo accede a totales, nunca a datos de una persona en particular.",
          "**Boletín semanal (opcional).** Quien quiera recibir por correo el resumen semanal puede suscribirse con su dirección "
          "de correo electrónico. La suscripción **no se hace en el Sitio**: el enlace «Suscribirme» lleva a la página de "
          "**Buttondown** (buttondown.com), el servicio que guarda la lista de suscriptores y envía los correos. El Sitio nunca "
          "recibe ni almacena direcciones de correo. Solo se pide la dirección de correo; la suscripción requiere confirmarla "
          "desde un enlace enviado a esa casilla, y cada correo incluye un enlace para darse de baja en un clic. El Responsable "
          "puede ver la lista de direcciones suscriptas y estadísticas de envío (por ejemplo, cantidad de aperturas), y la usa "
          "**exclusivamente** para enviar el boletín: no la vende, no la cede y no la usa para otros fines."]),
        ("2. Información técnica",
         ["Como ocurre en cualquier servicio web, el servidor donde se ejecuta la aplicación puede registrar de forma automática "
          "datos técnicos de la conexión (por ejemplo, dirección IP, fecha y hora, tipo de navegador) en registros operativos "
          "destinados a la seguridad y al diagnóstico de fallas. Estos registros no se utilizan para identificar personas ni se "
          "combinan con otras bases de datos, y se conservan solo por el tiempo que defina el entorno de ejecución."]),
        ("3. Datos que se guardan en el equipo",
         ["Para recordar preferencias, la aplicación puede guardar en archivos locales del equipo donde se ejecuta (i) la selección "
          "de indicadores que el usuario elige ver y (ii) las noticias marcadas como leídas. No contienen datos personales y "
          "pueden eliminarse en cualquier momento borrando los archivos «.macrocenter_prefs.json» y «.macrocenter_leidas.json».",
          "El navegador puede conservar, además, almacenamiento técnico estrictamente necesario para el funcionamiento (por ejemplo, "
          "la preferencia de tema claro u oscuro y la sesión de la interfaz). No se utilizan cookies publicitarias ni de seguimiento."]),
        ("4. Servicios y conexiones con terceros",
         ["Para obtener los datos, el servidor de la aplicación consulta fuentes públicas (BCRA, INDEC, Ministerio de Economía, "
          "ArgentinaDatos, CoinGecko, CriptoYa, Yahoo Finance y Wikipedia). En esas consultas no se envían datos del usuario.",
          "Algunos contenidos (por ejemplo, las fotografías de Wikimedia Commons) son cargados directamente por el navegador desde "
          "los servidores de esos terceros, que pueden recibir datos técnicos de la conexión como la dirección IP. El Sitio "
          "indica al navegador que no envíe la página de origen (referrer), pero el tratamiento que realicen esos terceros se rige "
          "por sus propias políticas de privacidad.",
          "Las direcciones de quienes se suscriben al boletín se alojan en los servidores de Buttondown, en los Estados Unidos, "
          "cuyo tratamiento se rige además por su política de privacidad (buttondown.com/legal/privacy). Al suscribirse, el "
          "usuario presta su consentimiento expreso para ese alojamiento.",
          "El conteo de visitas descripto en el punto 1 también lo realiza el navegador, conectándose a los servidores de "
          "GoatCounter, cuyo tratamiento se rige por su política de privacidad (goatcounter.com/help/privacy). Quien prefiera que "
          "no se cuente su visita puede bloquear el dominio «goatcounter.com» con un bloqueador de contenido: el Sitio funciona igual."]),
        ("5. Finalidad y base del tratamiento",
         ["La información técnica y las preferencias locales se utilizan únicamente para el funcionamiento, la seguridad y la "
          "mejora del Sitio. Dado que no se recopilan datos personales de los usuarios, no se requiere su consentimiento "
          "para el funcionamiento ordinario del servicio. Si en el futuro se incorporaran funciones que traten datos personales, "
          "se informará previamente y se requerirá el consentimiento libre, expreso e informado, de acuerdo con el artículo 5 de la "
          "Ley N.º 25.326.",
          "La dirección de correo de quien se suscribe al boletín se trata solo para enviarle ese boletín, sobre la base de su "
          "consentimiento libre, expreso e informado, que presta al suscribirse y confirmar la suscripción y que puede revocar "
          "en cualquier momento dándose de baja."]),
        ("6. Transferencias y cesión de datos",
         ["El Responsable no vende, cede ni transfiere datos personales a terceros. No se realizan transferencias internacionales "
          "de datos personales a países u organismos que no proporcionen niveles de protección adecuados, conforme al artículo 12 "
          "de la Ley N.º 25.326. Lo indicado en el punto 4 sobre conexiones técnicas del navegador con servicios del exterior no "
          "constituye una cesión por parte del Responsable. El alojamiento de la lista del boletín en Buttondown (punto 4) "
          "se realiza con el consentimiento expreso de cada suscriptor."]),
        ("7. Seguridad",
         ["Se aplican medidas técnicas y organizativas razonables para proteger el Sitio: ejecución restringida al equipo local por "
          "defecto, protección contra solicitudes falsificadas entre sitios (XSRF), validación y escape de los contenidos "
          "provenientes de terceros, validación de los enlaces mostrados, ocultamiento de detalles técnicos en los errores, "
          "versiones de dependencias fijadas y auditadas contra vulnerabilidades conocidas, y ausencia de almacenamiento de "
          "credenciales. Ningún sistema es completamente invulnerable; el Responsable no puede garantizar una seguridad absoluta."]),
        ("8. Derechos de los titulares de los datos",
         ["Conforme a los artículos 14, 15 y 16 de la Ley N.º 25.326, el titular de los datos personales puede ejercer los derechos "
          "de acceso (en forma gratuita a intervalos no inferiores a seis meses, salvo que acredite un interés legítimo), "
          "rectificación, actualización y supresión. Para hacerlo o para realizar consultas sobre esta política: " + _CONTACTO_TXT[0].lower() + _CONTACTO_TXT[1:],
          "**La AGENCIA DE ACCESO A LA INFORMACIÓN PÚBLICA, en su carácter de Órgano de Control de la Ley N.º 25.326, tiene la "
          "atribución de atender las denuncias y reclamos que interpongan quienes resulten afectados en sus derechos por "
          "incumplimiento de las normas vigentes en materia de protección de datos personales.**"]),
        ("9. Menores de edad",
         ["El Sitio no está dirigido a niños y niñas ni recopila deliberadamente datos personales de menores de edad."]),
        ("10. Conservación",
         ["Los archivos de preferencias se conservan hasta que el usuario los elimine. Los registros técnicos se conservan por el "
          "tiempo que defina el entorno donde se ejecute la aplicación y no más de lo necesario para su finalidad. Las "
          "estadísticas de visitas son totales anónimos y se conservan mientras el Sitio esté en funcionamiento. La dirección "
          "de correo de cada suscriptor se conserva mientras siga suscripto; al darse de baja deja de recibir el boletín y "
          "puede pedir su eliminación definitiva escribiendo al contacto indicado en el punto 8."]),
        ("11. Cambios en esta política",
         ["Esta Política puede actualizarse periódicamente. La versión vigente es la publicada en el Sitio, con su fecha de "
          "actualización. Se recomienda revisarla con frecuencia."]),
    ],
}

PAGINAS = {"terminos": TERMINOS, "privacidad": PRIVACIDAD}
