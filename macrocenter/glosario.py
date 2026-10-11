"""Término del día: 365 conceptos de economía explicados en criollo, uno por cada día del año.

Cada definición es corta (entra en la barra lateral), sin tecnicismos innecesarios y, cuando se puede, con un ejemplo
cotidiano. No hay opiniones políticas: solo qué significa cada cosa.
"""
from __future__ import annotations

import pandas as pd

TERMINOS: list[tuple[str, str]] = [
    # ── Dinero y precios ──
    ("Inflación", "Suba generalizada y sostenida de los precios. No es que algo se encarezca: es que el peso compra "
                  "cada vez menos de casi todo."),
    ("Deflación", "Lo contrario de la inflación: los precios bajan en general. Suena lindo, pero suele venir con "
                  "recesión, porque la gente posterga compras esperando que todo esté más barato."),
    ("Desinflación", "Cuando la inflación sigue, pero cada vez más lenta. Los precios suben, aunque menos que antes."),
    ("Hiperinflación", "Inflación descontrolada, de más del 50% por mes. En 1989 los precios se remarcaban varias veces "
                       "por día en la Argentina."),
    ("Estanflación", "La peor combinación: economía estancada (o en caída) y, al mismo tiempo, inflación alta."),
    ("IPC", "Índice de Precios al Consumidor. El INDEC sigue cada mes el precio de una canasta de bienes y servicios "
            "que consume una familia típica: su variación es la inflación."),
    ("Inflación núcleo", "La inflación sin los precios más saltarines (frutas y verduras, ropa de temporada) ni los "
                         "regulados (tarifas). Muestra la tendencia de fondo."),
    ("Precios regulados", "Los que fija o controla el Estado: tarifas de luz, gas y agua, transporte, combustibles, "
                          "prepagas. Pueden moverse distinto que el resto."),
    ("Precios relativos", "Cuánto vale una cosa comparada con otra. Si la nafta sube 10% y los sueldos 3%, cambió el "
                          "precio relativo: llenar el tanque cuesta más horas de trabajo."),
    ("Inercia inflacionaria", "Cuando los precios suben hoy porque subieron ayer: contratos, sueldos y alquileres que "
                              "se ajustan mirando el pasado mantienen la inflación andando sola."),
    ("Indexación", "Ajustar automáticamente un valor (sueldo, alquiler, crédito) por la inflación pasada. Protege del "
                   "aumento de precios, pero también lo perpetúa."),
    ("Remarcación", "Cambiar la etiqueta de precio de un producto, en general para arriba. En épocas de alta "
                    "inflación es la tarea más repetida del comercio."),
    ("Expectativas de inflación", "Lo que la gente cree que va a pasar con los precios. Importan mucho: si todos "
                                  "esperan 5% mensual, remarcan y negocian sueldos pensando en ese 5%."),
    ("Impuesto inflacionario", "Lo que pierde quien tiene pesos cuando hay inflación. Nadie lo vota ni lo paga en "
                               "una ventanilla, pero achica el poder de compra del efectivo."),
    ("Poder adquisitivo", "Cuántas cosas podés comprar con tu plata. Si tu sueldo sube 20% y los precios 30%, tu "
                          "poder adquisitivo bajó."),
    ("Ilusión monetaria", "Creer que ganás más porque el número del recibo es más grande, sin mirar cuánto subieron "
                          "los precios en el mismo tiempo."),
    ("Canasta básica alimentaria", "Los alimentos mínimos que necesita una persona para cubrir sus necesidades de "
                                   "energía y proteínas en un mes. Marca la línea de indigencia."),
    ("Canasta básica total", "La canasta alimentaria más ropa, transporte, educación, salud y otros gastos básicos. "
                             "Quien no la alcanza está bajo la línea de pobreza."),
    ("Línea de pobreza", "El ingreso mínimo para comprar la canasta básica total. Los hogares que ganan menos son "
                         "considerados pobres en las estadísticas oficiales."),
    ("Línea de indigencia", "El ingreso mínimo para comprar solo la comida básica. Por debajo de esa línea, no "
                            "alcanza ni para alimentarse."),
    ("Dinero", "Cualquier cosa que la gente acepta para pagar, para medir precios y para guardar valor. Fueron "
               "conchas, sal y oro; hoy son billetes y números en una pantalla."),
    ("Trueque", "Intercambiar bienes sin usar dinero. En 2001-2002 los clubes del trueque llegaron a reunir a "
                "millones de argentinos."),
    ("Bimonetarismo", "Cuando en un país conviven dos monedas: una para gastar (el peso) y otra para ahorrar y medir "
                      "cosas caras (el dólar). Muy argentino."),
    ("Dolarización", "Adoptar el dólar como moneda oficial y dejar de emitir una propia. Lo hicieron Ecuador, El "
                     "Salvador y Panamá."),
    ("Liquidez", "Qué tan rápido y fácil se convierte algo en dinero sin perder valor. Un plazo fijo es bastante "
                 "líquido; un departamento, poco."),
    ("Efectivo", "Billetes y monedas. Es el dinero más líquido, pero con inflación es también el que más rápido "
                 "pierde valor."),
    ("Cuasimoneda", "Bonos que emitían provincias o la Nación y circulaban como si fueran billetes. Hubo más de una "
                    "docena en la crisis de 2001."),
    ("Patacón", "La cuasimoneda de la provincia de Buenos Aires (2001-2003). Se pagaban sueldos con ella y se "
                "aceptaba en comercios, aunque valía menos que el peso."),
    ("Austral", "La moneda argentina entre 1985 y 1991. Nació con el Plan Austral y terminó pulverizada por la "
                "hiperinflación."),
    ("Ceros a la moneda", "Desde 1970 la Argentina le sacó 13 ceros a su moneda. Un peso de hoy equivale a "
                          "10.000.000.000.000 de pesos moneda nacional."),
    # ── Banco Central y política monetaria ──
    ("Banco Central", "El banco de los bancos. Emite la moneda, guarda las reservas, regula a los bancos y fija la "
                      "tasa de interés de referencia."),
    ("Política monetaria", "Lo que hace el Banco Central con la cantidad de dinero y las tasas de interés para "
                           "controlar la inflación y acompañar la actividad."),
    ("Emisión monetaria", "Crear dinero nuevo. Si crece mucho más rápido que la producción, suele terminar en "
                          "inflación."),
    ("Base monetaria", "Los billetes y monedas en la calle más el dinero que los bancos tienen depositado en el Banco "
                       "Central. Es el dinero «primario» de la economía."),
    ("M2", "Una medida amplia del dinero: efectivo más depósitos en cuenta corriente y caja de ahorro. Todo lo que "
           "se puede gastar de inmediato."),
    ("Encaje bancario", "La parte de los depósitos que los bancos no pueden prestar y deben dejar inmovilizada, como "
                        "colchón de seguridad."),
    ("Tasa de política monetaria", "La tasa de interés que fija el Banco Central como referencia. Si la sube, se "
                                   "encarece el crédito y se enfría la economía; si la baja, al revés."),
    ("Licuación", "Cuando la inflación achica el valor real de algo fijo en pesos: deudas, sueldos o gastos que no "
                  "se actualizan."),
    # ── Dólar y tipo de cambio ──
    ("Tipo de cambio", "El precio de una moneda en otra. Cuando decimos «el dólar está a 1.500», es el tipo de cambio "
                       "peso-dólar."),
    ("Devaluación", "Suba del precio del dólar oficial decidida o convalidada por el Estado: el peso pasa a valer "
                    "menos frente a otras monedas."),
    ("Apreciación", "Cuando una moneda gana valor: con los mismos pesos se compran más dólares. Abarata viajes e "
                    "importaciones, pero complica a los exportadores."),
    ("Tipo de cambio real", "El dólar corregido por la inflación de acá y de afuera. Dice si el país está «caro» o "
                            "«barato» en dólares."),
    ("Atraso cambiario", "Cuando el dólar sube menos que los precios internos: el país se encarece en dólares y "
                         "conviene más importar y viajar afuera que exportar."),
    ("Crawling peg", "Devaluaciones chiquitas y programadas, día a día, para que el dólar oficial acompañe de a poco "
                     "a la inflación."),
    ("Bandas cambiarias", "Un piso y un techo para el dólar: dentro de esos límites flota libremente; si los toca, el "
                          "Banco Central interviene."),
    ("Flotación libre", "El dólar se mueve solo por oferta y demanda, sin que el Banco Central intervenga."),
    ("Cepo cambiario", "Restricciones para comprar dólares: topes, permisos o directamente prohibición. Hubo cepos en "
                       "2011-2015 y 2019-2025 (para las personas)."),
    ("Brecha cambiaria", "La diferencia entre el dólar oficial y los paralelos (blue, MEP, CCL). Una brecha alta suele "
                         "indicar desconfianza o restricciones."),
    ("Dólar blue", "El dólar del mercado informal, que se compra en «cuevas» y con «arbolitos». No es legal, pero su "
                   "precio se sigue todos los días."),
    ("Dólar MEP", "El dólar que se obtiene comprando un bono en pesos y vendiéndolo en dólares en la bolsa. Es legal "
                  "y los dólares quedan en una cuenta local."),
    ("Contado con liquidación", "Como el MEP, pero los dólares terminan en una cuenta en el exterior. Lo usan sobre "
                                "todo empresas."),
    ("Dólar tarjeta", "El precio del dólar que se paga al consumir en el exterior con tarjeta: el oficial más los "
                      "impuestos que correspondan."),
    ("Dólar cripto", "El precio implícito del dólar al comprar stablecoins como USDT con pesos en un exchange."),
    ("Dólar mayorista", "El que se usa entre bancos y grandes empresas, por montos grandes. Es la referencia del "
                        "comercio exterior."),
    ("Dólar soja", "Un tipo de cambio especial y temporal que se dio a los exportadores de soja para que vendieran su "
                   "cosecha. Hubo varias ediciones entre 2022 y 2023."),
    ("Arbolito", "Persona que compra y vende dólares en la calle, generalmente en el microcentro porteño. Parte del "
                 "mercado informal."),
    ("Cueva", "Lugar donde se compran y venden dólares en negro, muchas veces disfrazado de otro negocio."),
    ("Rulo", "Aprovechar la diferencia entre dos dólares: comprar barato en uno y vender caro en otro. Cuando hay "
             "brecha, siempre aparece alguien haciendo el rulo."),
    ("Liquidación de divisas", "Cuando un exportador vende en el mercado oficial los dólares que cobró. Es la "
                               "principal entrada de dólares del país."),
    ("Corrida cambiaria", "Cuando muchos quieren comprar dólares al mismo tiempo y el precio se dispara. Suele "
                          "alimentarse del miedo a que suba más."),
    ("Dólares del colchón", "Los ahorros en dólares que los argentinos guardan fuera del sistema (en casa o en cajas "
                            "de seguridad). Se estiman en decenas de miles de millones."),
    ("Blanqueo", "Régimen que permite declarar ahorros o bienes no informados al fisco, pagando una multa reducida o "
                 "ninguna."),
    ("Swap de monedas", "Acuerdo entre dos bancos centrales para intercambiar monedas. El swap con China suma yuanes a "
                        "las reservas del BCRA."),
    ("Real", "La moneda de Brasil, nuestro principal socio comercial. Si el real se devalúa, los productos "
             "argentinos se vuelven más caros para los brasileños."),
    ("Índice Big Mac", "Indicador creado por la revista The Economist: compara el precio de una Big Mac en distintos "
                       "países para ver qué monedas están caras o baratas."),
    # ── Reservas, deuda y riesgo ──
    ("Reservas internacionales", "Los dólares, el oro y otras divisas que tiene el Banco Central. Sirven para pagar "
                                 "deuda, importar y defender el valor del peso."),
    ("Reservas brutas", "Todas las reservas del Banco Central, incluidas las que pidió prestadas o las que son "
                        "depósitos de ahorristas."),
    ("Reservas netas", "Las reservas brutas menos lo que el Banco Central debe en el corto plazo. Es lo que de verdad "
                       "puede usar."),
    ("Oro en las reservas", "Parte de las reservas del BCRA está en lingotes de oro. Su valor en dólares sube y baja "
                            "con el precio internacional del metal."),
    ("Riesgo país", "Cuánto más que Estados Unidos tiene que pagar la Argentina para que le presten. 100 puntos "
                    "equivalen a 1 punto porcentual de tasa extra."),
    ("Punto básico", "La centésima parte de un punto porcentual. Si una tasa pasa de 5,00% a 5,25%, subió 25 puntos "
                     "básicos."),
    ("Deuda pública", "Todo lo que debe el Estado: bonos, préstamos de organismos internacionales y deudas con otros "
                      "países. Se mide en relación al PBI."),
    ("Deuda sobre PBI", "La deuda pública dividida por todo lo que produce el país en un año. Sirve para comparar "
                        "cuán endeudado está un país frente a su tamaño."),
    ("Default", "Cuando un deudor (una empresa o un país) deja de pagar su deuda en los términos pactados."),
    ("Reestructuración de deuda", "Renegociar una deuda: cambiar plazos, tasas o el monto a pagar, en general para "
                                  "evitar o salir de un default."),
    ("Quita", "La parte de una deuda que el acreedor acepta perder en una renegociación. También se la llama "
              "«haircut» (corte de pelo)."),
    ("Canje de deuda", "Cambiar bonos viejos por bonos nuevos con otras condiciones. La Argentina hizo grandes canjes "
                       "en 2005, 2010 y 2020."),
    ("Holdouts", "Acreedores que no aceptan entrar en un canje y litigan para cobrar el total. Algunos son fondos "
                 "especializados en eso, apodados «buitres»."),
    ("Bono", "Un préstamo partido en pedacitos: quien compra un bono le presta plata al emisor (un Estado o una "
             "empresa), que se compromete a devolverla con intereses."),
    ("Bono CER", "Bono en pesos que ajusta por inflación (a través del CER). Protege de la suba de precios."),
    ("FMI", "Fondo Monetario Internacional: organismo que presta a países con problemas de balanza de pagos, a "
            "cambio de compromisos económicos. La Argentina es su mayor deudor."),
    ("Acuerdo stand-by", "Préstamo del FMI de corto plazo para atender urgencias, con metas trimestrales a cumplir. "
                         "La Argentina firmó uno récord en 2018."),
    # ── Tasas, ahorro y crédito ──
    ("Tasa de interés", "El precio del dinero en el tiempo: lo que cobra quien presta y paga quien pide prestado."),
    ("Tasa nominal", "La tasa tal como se anuncia, sin descontar la inflación. Un 40% anual con 50% de inflación es "
                     "una pérdida."),
    ("Tasa real", "La tasa de interés descontada la inflación. Si es positiva, el ahorro gana poder de compra; si es "
                  "negativa, pierde."),
    ("TNA", "Tasa Nominal Anual: la tasa que se informa en los plazos fijos y créditos. No incluye la capitalización "
            "de intereses."),
    ("TEA", "Tasa Efectiva Anual: lo que realmente rinde (o cuesta) en un año, reinvirtiendo los intereses. Siempre "
            "es mayor o igual que la TNA."),
    ("CFT", "Costo Financiero Total: lo que realmente pagás por un crédito, con intereses, seguros, comisiones e "
            "impuestos. Es el número que hay que mirar."),
    ("Interés compuesto", "Ganar intereses sobre los intereses. Einstein (dicen) lo llamó la fuerza más poderosa del "
                          "universo; los bancos, simplemente, «capitalizar»."),
    ("Regla del 72", "Truco rápido: dividí 72 por la tasa anual y sabrás en cuántos años se duplica tu plata. Al 8% "
                     "anual, en unos 9 años."),
    ("Plazo fijo", "Dejar plata en el banco durante un tiempo fijo a cambio de una tasa de interés. Si lo sacás antes, "
                   "en general no podés."),
    ("Plazo fijo UVA", "Plazo fijo que ajusta por inflación (a través de la UVA) más una tasa chica. Tiene un plazo "
                       "mínimo más largo que el tradicional."),
    ("BADLAR", "La tasa que pagan los bancos privados por plazos fijos de más de un millón de pesos. Es la "
               "referencia del mercado."),
    ("UVA", "Unidad de Valor Adquisitivo: una unidad que vale cada vez más pesos según la inflación. Se usa en "
            "créditos hipotecarios y plazos fijos."),
    ("CER", "Coeficiente de Estabilización de Referencia: índice diario del BCRA que sigue a la inflación con unas "
            "semanas de atraso."),
    ("ICL", "Índice de Contratos de Locación: combinaba inflación y salarios y se usó para ajustar alquileres entre "
            "2020 y 2023."),
    ("Fondo común de inversión", "Mucha gente junta su plata y un administrador profesional la invierte. Cada uno es "
                                 "dueño de una parte, llamada cuotaparte."),
    ("Money market", "Un fondo común que invierte en cosas muy seguras y de corto plazo. Se puede retirar al instante "
                     "y lo usan las billeteras virtuales para pagar rendimiento."),
    ("Crédito hipotecario", "Préstamo de largo plazo para comprar una vivienda, que queda como garantía (hipoteca) "
                            "hasta que se termina de pagar."),
    ("Crédito UVA", "Préstamo cuyas cuotas se ajustan por inflación. La primera cuota es más baja que en uno "
                    "tradicional, pero el riesgo es que los sueldos suban menos que los precios."),
    ("Sistema francés", "Forma de pagar un préstamo con cuotas iguales: al principio pagás casi todo interés y al "
                        "final casi todo capital."),
    ("Préstamo personal", "Crédito para cualquier destino, sin garantía específica. Por eso suele tener tasas más "
                          "altas que un hipotecario."),
    ("Tarjeta de crédito", "Permite comprar ahora y pagar después. Si no pagás el total del resumen, lo que queda "
                           "genera intereses altos."),
    ("Pago mínimo", "Lo mínimo que hay que abonar del resumen de la tarjeta para no entrar en mora. El resto se "
                    "financia, y caro."),
    ("Cuotas sin interés", "Pagar en cuotas fijas al precio de contado. Con inflación, son negocio para el comprador: "
                           "las últimas cuotas valen menos."),
    ("Morosidad", "La proporción de deudores que se atrasan en sus pagos. Sube cuando la economía se complica."),
    ("Garantía", "Algo que respalda una deuda: si el deudor no paga, el acreedor puede quedarse con ella (una casa, "
                 "un auto, un sueldo)."),
    ("Scoring crediticio", "Puntaje que usan los bancos para decidir si te prestan y a qué tasa, según tu historial "
                           "de pagos."),
    ("CBU y CVU", "Los números de 22 dígitos de una cuenta: CBU si es bancaria, CVU si es de una billetera virtual. "
                  "Los alias son sus apodos fáciles."),
    ("Billetera virtual", "Aplicación para guardar dinero, pagar y transferir desde el celular, sin necesidad de un "
                          "banco tradicional."),
    ("Fintech", "Empresas que usan tecnología para dar servicios financieros: pagos, créditos, inversiones o "
                "seguros, todo desde una app."),
    ("Ahorro", "La parte del ingreso que no se gasta. Es la base de la inversión: sin ahorro, no hay con qué "
               "construir el futuro."),
    ("Fondo de emergencia", "Ahorro reservado para imprevistos (una mudanza, una reparación, quedarse sin trabajo). "
                            "Se recomienda que alcance para varios meses de gastos."),
    ("Educación financiera", "Saber manejar la propia plata: presupuesto, ahorro, deudas e inversiones. En países con "
                             "inflación es casi un deporte de supervivencia."),
    ("Presupuesto personal", "Anotar cuánto entra y cuánto sale cada mes. El primer paso para saber a dónde se va la "
                             "plata."),
    ("Diversificación", "No poner todos los huevos en la misma canasta: repartir el ahorro entre distintos activos "
                        "para que una mala noticia no te arrastre entero."),
    ("Rentabilidad", "Cuánto gana una inversión respecto de lo que se puso. Un 10% de rentabilidad sobre $1.000 son "
                     "$100."),
    ("Riesgo", "La posibilidad de que una inversión salga peor de lo esperado. En general, a más rendimiento "
               "prometido, más riesgo."),
    ("Volatilidad", "Cuánto suben y bajan los precios de un activo. Las criptomonedas son muy volátiles; un plazo fijo, "
                    "nada."),
    # ── Bolsa y mercados ──
    ("Acción", "Una porción de la propiedad de una empresa. Quien tiene acciones gana si la empresa crece o reparte "
               "ganancias."),
    ("Dividendo", "La parte de las ganancias que una empresa reparte entre sus accionistas."),
    ("Bolsa de valores", "El mercado donde se compran y venden acciones, bonos y otros títulos. En la Argentina, "
                         "Bolsas y Mercados Argentinos (BYMA)."),
    ("Merval", "El índice de las principales acciones argentinas. Si sube, en promedio esas empresas valen más."),
    ("S&P 500", "Índice que agrupa a las 500 empresas más grandes de Estados Unidos. Es el termómetro más mirado de "
                "la bolsa mundial."),
    ("CEDEAR", "Certificados que permiten comprar en la bolsa argentina, y en pesos, acciones de empresas del "
               "exterior como Apple o Coca-Cola."),
    ("Mercado alcista", "Período en el que los precios de las acciones suben de forma sostenida. En inglés, «bull "
                        "market», por el toro que embiste hacia arriba."),
    ("Mercado bajista", "Período de caída sostenida de las acciones. En inglés, «bear market», por el oso que golpea "
                        "hacia abajo."),
    ("Burbuja", "Cuando el precio de algo sube muchísimo más de lo que vale, impulsado por la euforia. Tarde o "
                "temprano, explota."),
    ("Crack bursátil", "Una caída brusca y masiva de la bolsa. El más famoso: el de 1929 en Wall Street, que dio "
                       "inicio a la Gran Depresión."),
    ("Wall Street", "La calle de Nueva York donde está la bolsa más importante del mundo. Por extensión, el mundo "
                    "financiero de Estados Unidos."),
    ("Commodities", "Materias primas que se comercian en todo el mundo con precios internacionales: soja, trigo, "
                    "petróleo, oro, cobre."),
    ("Especulación", "Comprar algo para venderlo más caro después, apostando a que su precio va a subir. No siempre "
                     "es mala: le da liquidez a los mercados."),
    ("Carry trade", "Pasar dólares a pesos para aprovechar una tasa alta y volver al dólar más adelante. Funciona si "
                    "el dólar no sube más que lo ganado."),
    ("Bicicleta financiera", "Nombre criollo del carry trade: entrar en pesos, cobrar tasa y salir en dólares, "
                             "ganando en dólares sin producir nada."),
    ("Cisne negro", "Un hecho muy improbable, de enorme impacto, que nadie vio venir (como la pandemia de 2020)."),
    ("Efecto manada", "Cuando los inversores hacen lo mismo que los demás solo porque los demás lo hacen. Infla "
                      "burbujas y agranda pánicos."),
    # ── Cripto ──
    ("Criptomoneda", "Dinero digital que no emite ningún banco central y funciona sobre una red de computadoras que "
                     "registra cada movimiento."),
    ("Bitcoin", "La primera criptomoneda, creada en 2009 por alguien bajo el seudónimo Satoshi Nakamoto. Solo "
                "existirán 21 millones."),
    ("Blockchain", "Un libro contable digital, público y muy difícil de alterar, donde quedan registradas todas las "
                   "transacciones de una cripto."),
    ("Stablecoin", "Criptomoneda que busca mantener un valor estable, en general atada al dólar (1 a 1)."),
    ("USDT", "Tether, la stablecoin más usada del mundo. En la Argentina se usa mucho para ahorrar en «dólares» "
             "digitales."),
    # ── Actividad y producción ──
    ("PBI", "Producto Bruto Interno: el valor de todo lo que se produce en un país en un período. La medida más "
            "usada del tamaño de una economía."),
    ("PBI per cápita", "El PBI dividido por la cantidad de habitantes. Da una idea (muy promedio) de la riqueza por "
                       "persona."),
    ("PBI real", "El PBI medido a precios constantes de un año base, para que la inflación no infle el número. Muestra "
                 "si de verdad se produce más."),
    ("EMAE", "Estimador Mensual de Actividad Económica del INDEC: el anticipo, mes a mes, de cómo viene el PBI."),
    ("Recesión", "Caída de la actividad económica durante un período sostenido. Suele hablarse de dos trimestres "
                 "seguidos en baja."),
    ("Depresión", "Una recesión larga y profunda, con fuerte caída de la producción y del empleo durante años."),
    ("Crecimiento económico", "Aumento sostenido de la producción de bienes y servicios de un país. Se mide con la "
                              "variación del PBI real."),
    ("Ciclo económico", "Las subidas y bajadas de la economía: expansión, pico, recesión y recuperación. Ninguna "
                        "etapa dura para siempre."),
    ("Rebote", "La recuperación rápida después de una caída fuerte. Crecer mucho después de caer mucho no siempre "
               "significa volver al punto de partida."),
    ("Variación interanual", "Comparar con el mismo mes (o trimestre) del año anterior. Evita confundir efectos de la "
                             "época del año."),
    ("Variación mensual", "Comparar con el mes anterior. Muestra lo más reciente, aunque puede estar afectada por "
                          "factores estacionales."),
    ("Desestacionalizar", "Quitar de una serie los efectos que se repiten cada año (vacaciones, cosechas, fiestas) "
                          "para ver la tendencia real."),
    ("Productividad", "Cuánto se produce por hora trabajada o por trabajador. Es la clave para que los salarios puedan "
                      "subir de forma sostenible."),
    ("Capacidad instalada", "Qué porcentaje de su capacidad de producción usan las fábricas. Si está baja, hay "
                            "máquinas paradas."),
    ("Inversión", "En economía, gastar hoy en cosas que permiten producir más mañana: máquinas, fábricas, rutas, "
                  "viviendas."),
    ("Consumo privado", "Lo que gastan las familias en bienes y servicios. Es el componente más grande del PBI."),
    ("Gasto público", "Lo que gasta el Estado: salarios públicos, jubilaciones, obras, subsidios, salud y educación."),
    ("Valor agregado", "Lo que una empresa suma a lo que compró. Si comprás harina por $100 y vendés pan por $300, "
                       "agregaste $200 de valor."),
    ("Cadena de valor", "Todos los pasos que recorre un producto, desde la materia prima hasta el consumidor. Del "
                        "trigo a la medialuna hay varios eslabones."),
    ("Economías de escala", "Cuando producir más hace que cada unidad salga más barata. Una fábrica grande suele tener "
                            "costos por unidad menores que un taller."),
    ("Economía del conocimiento", "Actividades basadas en el talento y la tecnología: software, servicios "
                                  "profesionales, biotecnología. Un sector exportador fuerte en la Argentina."),
    ("Vaca Muerta", "Una de las mayores formaciones de petróleo y gas no convencional del mundo, en Neuquén. Puede "
                    "cambiar la balanza energética del país."),
    ("Litio", "Metal clave para las baterías de autos eléctricos y celulares. La Argentina forma parte del «triángulo "
              "del litio» junto con Bolivia y Chile."),
    ("Economías regionales", "Las producciones típicas de cada provincia: vino en Mendoza, yerba en Misiones, limones "
                             "en Tucumán, manzanas en Río Negro."),
    ("Pyme", "Pequeña y mediana empresa. En la Argentina son la gran mayoría de las empresas y generan buena parte del "
             "empleo privado."),
    ("Emprendedor", "Persona que arranca un negocio propio asumiendo el riesgo. El motor de muchas empresas que "
                    "después crecen."),
    ("Unicornio", "Una startup que llega a valer más de mil millones de dólares. La Argentina tuvo varios, como "
                  "Mercado Libre, Globant y Ualá."),
    ("Economía informal", "La actividad que ocurre por fuera de los registros del Estado: trabajos sin aportes, "
                          "ventas sin factura. No paga impuestos ni tiene protección."),
    # ── Trabajo e ingresos ──
    ("Desocupación", "El porcentaje de personas que buscan trabajo y no lo encuentran, sobre el total de quienes "
                     "trabajan o buscan."),
    ("Tasa de actividad", "Qué proporción de la población trabaja o busca trabajo. No incluye a estudiantes, jubilados "
                          "ni a quienes no buscan."),
    ("EPH", "Encuesta Permanente de Hogares del INDEC. De ahí salen los datos de desempleo, pobreza e ingresos."),
    ("Empleo registrado", "Trabajo «en blanco»: con aportes jubilatorios, obra social y protección legal."),
    ("Informalidad laboral", "Trabajo «en negro»: sin aportes ni protección. En la Argentina alcanza a más de un "
                             "tercio de los asalariados."),
    ("Monotributo", "Régimen simplificado de impuestos para trabajadores independientes y pequeños negocios: una cuota "
                    "fija mensual que incluye impuestos, jubilación y obra social."),
    ("Salario real", "El sueldo medido en lo que alcanza a comprar: sube si los salarios aumentan más que los precios."),
    ("Salario mínimo, vital y móvil", "El sueldo más bajo que se le puede pagar a un trabajador registrado de jornada "
                                      "completa. Lo fija un consejo de gobierno, empresas y sindicatos."),
    ("Paritarias", "Las negociaciones anuales entre sindicatos y empresas para fijar los aumentos salariales de cada "
                   "actividad."),
    ("Aguinaldo", "El sueldo anual complementario: medio sueldo extra que se paga en junio y en diciembre."),
    ("Cláusula gatillo", "Un acuerdo salarial que se ajusta solo si la inflación supera cierto número. Dispara un "
                         "aumento automático."),
    ("RIPTE", "Remuneración Imponible Promedio de los Trabajadores Estables: el sueldo promedio de los trabajadores "
              "registrados. Se usa para actualizar varios montos."),
    ("Indemnización", "La compensación que recibe un trabajador cuando lo despiden sin causa justificada."),
    ("Jubilación", "El ingreso que cobra una persona cuando deja de trabajar por edad, financiado por los aportes de "
                   "los trabajadores activos y por impuestos."),
    ("Haber mínimo", "La jubilación más baja que paga el sistema. La cobra una parte grande de los jubilados."),
    ("Movilidad jubilatoria", "La fórmula que define cuánto y cada cuánto aumentan las jubilaciones. Cambió varias "
                              "veces en los últimos años."),
    ("ANSES", "Administración Nacional de la Seguridad Social: paga jubilaciones, asignaciones familiares y otras "
              "prestaciones."),
    ("Asignación Universal por Hijo", "Ayuda mensual por cada hijo para familias de trabajadores informales, "
                                      "desocupados o de bajos ingresos."),
    ("Coeficiente de Gini", "Mide la desigualdad del ingreso: 0 es igualdad perfecta y 1 es que una sola persona se "
                            "queda con todo."),
    ("Movilidad social", "La posibilidad de que una persona mejore su posición económica respecto de la de sus "
                         "padres. «M'hijo el dotor» es su versión criolla."),
    ("Clase media", "El grupo de ingresos intermedios. En la Argentina tiene un peso cultural enorme, aunque su tamaño "
                    "cambia con cada crisis."),
    ("Brecha salarial de género", "La diferencia entre lo que ganan en promedio los varones y las mujeres. Se explica "
                                  "en parte por horas trabajadas y tareas de cuidado no pagas."),
    ("Fuga de cerebros", "Cuando profesionales calificados se van a trabajar a otro país. El país pierde la inversión "
                         "que hizo en su formación."),
    ("Remesas", "El dinero que los migrantes envían a sus familias en su país de origen."),
    # ── Estado e impuestos ──
    ("Déficit fiscal", "Cuando el Estado gasta más de lo que recauda. La diferencia se cubre con deuda o con "
                       "emisión."),
    ("Resultado primario", "Ingresos menos gastos del Estado sin contar los intereses de la deuda."),
    ("Resultado financiero", "El resultado fiscal contando también los intereses de la deuda. Es el número final."),
    ("Ajuste fiscal", "Bajar el déficit recortando gastos, subiendo impuestos o ambas cosas."),
    ("Presión tributaria", "Cuánto representan los impuestos que se pagan en relación al PBI. Mide el peso de los "
                           "impuestos sobre la economía."),
    ("IVA", "Impuesto al Valor Agregado: se paga en casi todas las compras. La tasa general en la Argentina es del "
            "21%."),
    ("Impuesto a las Ganancias", "Impuesto sobre los ingresos de personas y empresas por encima de cierto monto. Es "
                                 "el impuesto «directo» más importante."),
    ("Impuesto al cheque", "Impuesto a los débitos y créditos bancarios: se cobra cada vez que entra o sale plata de "
                           "una cuenta. Nació «transitorio» en 2001."),
    ("Ingresos brutos", "Impuesto provincial que se cobra sobre la facturación de las empresas, en cada etapa de la "
                        "cadena. Por eso se lo llama «en cascada»."),
    ("Bienes Personales", "Impuesto anual sobre el patrimonio de las personas (casas, autos, ahorros) que supera "
                          "cierto monto."),
    ("Retenciones", "Impuestos a las exportaciones: el Estado se queda con un porcentaje de lo que se vende afuera. "
                    "Su nombre técnico es «derechos de exportación»."),
    ("Aranceles", "Impuestos a las importaciones. Encarecen los productos de afuera para proteger a la producción "
                  "local (o para recaudar)."),
    ("Impuesto PAIS", "Impuesto a la compra de dólares y a los gastos en el exterior, vigente entre 2019 y 2024."),
    ("Coparticipación", "El sistema por el que la Nación reparte con las provincias lo recaudado por varios "
                        "impuestos."),
    ("Impuesto progresivo", "El que cobra una tasa más alta a quien gana más. Ganancias es progresivo."),
    ("Impuesto regresivo", "El que pesa proporcionalmente más sobre quienes menos tienen. El IVA lo es, porque los "
                           "pobres gastan casi todo lo que ganan."),
    ("Evasión fiscal", "No pagar impuestos que corresponde pagar, ocultando ingresos o ventas. Es ilegal."),
    ("Elusión fiscal", "Pagar menos impuestos aprovechando huecos de la ley. Es legal, aunque a veces está en el "
                       "límite."),
    ("Moratoria", "Plan para que quienes deben impuestos (o aportes) se pongan al día en cuotas, muchas veces con "
                  "quita de intereses."),
    ("Subsidios", "Plata que pone el Estado para que algo cueste menos: tarifas de luz, gas, transporte. Alguien los "
                  "paga, aunque no se vea en la factura."),
    ("Tarifas", "El precio de los servicios públicos: luz, gas, agua, transporte. En la Argentina, muchas veces "
                "estuvieron muy por debajo de su costo."),
    ("Privatización", "Vender o concesionar empresas del Estado a privados. En los años 90 se privatizaron teléfonos, "
                      "trenes, petróleo y energía."),
    ("Estatización", "Cuando el Estado se queda con una empresa privada o un servicio. Por ejemplo, las AFJP en 2008 o "
                     "YPF en 2012."),
    ("Efecto Olivera-Tanzi", "Con inflación alta, los impuestos se cobran tarde y valen menos al llegar. Lo describió "
                             "el economista argentino Julio Olivera."),
    ("Curva de Laffer", "La idea de que, pasado cierto punto, subir los impuestos hace recaudar menos, porque "
                        "desalienta la actividad o fomenta la evasión."),
    ("Bien público", "Algo que, si existe, sirve a todos y no se puede excluir a nadie de usarlo: el alumbrado de la "
                     "calle, la defensa, un faro."),
    ("Free rider", "Quien se beneficia de algo sin pagar su parte: el que no aporta para el regalo grupal pero firma la "
                   "tarjeta."),
    ("Ley de Presupuesto", "La «ley de leyes»: autoriza gastos e impuestos para el año. Sin presupuesto aprobado, se "
                           "prorroga el del año anterior."),
    ("ARCA", "Agencia de Recaudación y Control Aduanero: el organismo que cobra los impuestos nacionales. Reemplazó a "
             "la AFIP en 2024."),
    # ── Comercio exterior ──
    ("Balanza comercial", "Exportaciones menos importaciones de bienes. Si se vende más de lo que se compra, hay "
                          "superávit."),
    ("Balanza de pagos", "El registro de todo el dinero que entra y sale de un país: comercio, servicios, turismo, "
                         "intereses, inversiones y préstamos."),
    ("Cuenta corriente", "La parte de la balanza de pagos que registra comercio, servicios, intereses y remesas. Si es "
                         "negativa, el país necesita financiarse."),
    ("Exportaciones", "Lo que un país vende al exterior. Son la principal fuente genuina de dólares."),
    ("Importaciones", "Lo que un país compra al exterior: insumos para fábricas, máquinas, energía, bienes de consumo."),
    ("Términos de intercambio", "Cuánto valen nuestras exportaciones comparadas con nuestras importaciones. Si la "
                                "soja sube y lo que importamos no, mejoran."),
    ("Restricción externa", "Cuando el país se queda sin dólares para crecer: al crecer importa más, faltan divisas y "
                            "la economía tiene que frenar. Un clásico argentino."),
    ("Stop and go", "Ciclos de crecimiento cortados por crisis de dólares: la economía acelera, faltan divisas, se "
                    "devalúa y frena. Marcó a la Argentina por décadas."),
    ("Enfermedad holandesa", "Cuando un recurso natural muy exportado aprecia la moneda y termina perjudicando a otras "
                             "industrias. Le pasó a Holanda con el gas en los años 60."),
    ("Ventaja comparativa", "Producir lo que te sale relativamente mejor que a otros. Hasta el mejor en todo gana "
                            "especializándose en lo que más le conviene."),
    ("Proteccionismo", "Políticas para proteger a la industria local de la competencia extranjera: aranceles, cupos, "
                       "trabas a las importaciones."),
    ("Libre comercio", "Comerciar con otros países sin aranceles ni trabas. Abarata bienes, pero expone a la "
                       "competencia."),
    ("Mercosur", "Bloque comercial formado en 1991 por Argentina, Brasil, Paraguay y Uruguay (luego se sumó Bolivia), "
                 "con aranceles bajos entre sus miembros."),
    ("Dumping", "Vender en otro país por debajo del costo o del precio local, para ganar mercado y desplazar a la "
                "competencia."),
    ("Sustitución de importaciones", "Producir en el país lo que antes se importaba. Fue la estrategia dominante en la "
                                     "Argentina entre los años 30 y 70."),
    ("Balanza energética", "Exportaciones menos importaciones de energía. Gracias a Vaca Muerta, pasó de un fuerte "
                           "déficit a superávit."),
    ("Inversión extranjera directa", "Cuando una empresa del exterior invierte en el país para producir: una fábrica, "
                                     "una mina, un centro de datos."),
    ("Capitales golondrina", "Inversiones de corto plazo que llegan atraídas por tasas altas y se van apenas cambia el "
                             "clima. Como las golondrinas."),
    ("Guerra comercial", "Cuando dos países se suben mutuamente los aranceles como represalia. Suele perjudicar a "
                         "ambos."),
    ("Puerto de Rosario", "El gran complejo agroexportador sobre el río Paraná: por ahí sale buena parte de la soja, el "
                          "maíz y el trigo argentinos."),
    # ── Ideas y conceptos ──
    ("Costo de oportunidad", "Lo que dejás de lado al elegir algo. Si pasás la tarde en el sillón, el costo es lo que "
                             "podrías haber hecho con esas horas."),
    ("Escasez", "El problema básico de la economía: los deseos son ilimitados y los recursos, no. Por eso hay que "
                "elegir."),
    ("Oferta y demanda", "El precio de algo se forma en el encuentro entre cuánto quieren vender y cuánto quieren "
                         "comprar. Si sobra, baja; si falta, sube."),
    ("Elasticidad", "Cuánto cambia lo que se compra cuando cambia el precio. La sal es poco elástica; las vacaciones, "
                    "muy elásticas."),
    ("Bien sustituto", "Uno que puede reemplazar a otro: si sube la carne, se compra más pollo."),
    ("Bien inferior", "Uno que se compra menos cuando el ingreso sube: al mejorar el sueldo, se pasa de la segunda "
                      "marca a la primera."),
    ("Utilidad marginal", "La satisfacción que da una unidad más de algo. La primera porción de pizza vale oro; la "
                          "octava, no tanto."),
    ("Mano invisible", "Metáfora de Adam Smith: cada uno, buscando su propio interés, termina sin querer beneficiando "
                       "a los demás a través del mercado."),
    ("Monopolio", "Cuando una sola empresa vende un producto sin competencia. Puede cobrar más y ofrecer menos."),
    ("Oligopolio", "Mercado dominado por unas pocas empresas grandes, como pasa con la telefonía o el acero."),
    ("Cartel", "Acuerdo entre empresas que deberían competir para fijar precios o repartirse el mercado. Es ilegal en "
               "la mayoría de los países. La OPEP es un cartel de países."),
    ("Externalidad", "Un efecto de una actividad sobre terceros que no se paga ni se cobra. La contaminación de una "
                     "fábrica es negativa; la vacuna de tu vecino, positiva."),
    ("Tragedia de los comunes", "Cuando un recurso compartido se agota porque cada uno lo usa pensando solo en sí "
                                "mismo: la pesca excesiva es el ejemplo clásico."),
    ("Incentivos", "Lo que impulsa a la gente a actuar de cierta manera: premios, castigos, precios. Gran parte de la "
                   "economía es entender incentivos."),
    ("Riesgo moral", "Cuando alguien toma más riesgos porque sabe que otro va a pagar los platos rotos. Por ejemplo, "
                     "manejar peor porque el auto está asegurado."),
    ("Información asimétrica", "Cuando una parte sabe más que la otra. El vendedor de un auto usado sabe sus mañas; el "
                               "comprador, no."),
    ("Teoría de juegos", "Estudio de decisiones en las que el resultado depende de lo que hagan los demás: negocios, "
                         "política, el truco."),
    ("Dilema del prisionero", "Un clásico de la teoría de juegos: dos personas que, sin confiar entre sí, terminan "
                              "eligiendo lo que es peor para ambas."),
    ("Equilibrio de Nash", "Situación en la que nadie gana cambiando solo su estrategia. Lleva el nombre de John Nash, "
                           "el de la película «Una mente brillante»."),
    ("Economía conductual", "Rama que estudia cómo decidimos de verdad, con emociones y atajos mentales, y no como "
                            "calculadoras perfectas."),
    ("Sesgo de anclaje", "Quedarse pegado al primer número que uno escucha. Por eso las ofertas muestran el precio "
                         "«antes» tachado."),
    ("Aversión a la pérdida", "Perder $1.000 duele más de lo que alegra ganar $1.000. Por eso cuesta tanto vender una "
                              "inversión que cayó."),
    ("Falacia del costo hundido", "Seguir con algo malo solo porque ya pusiste plata o tiempo. Terminar una película "
                                  "aburrida porque pagaste la entrada."),
    ("Sesgo del presente", "Preferir algo chico hoy antes que algo grande mañana. Es la razón por la que cuesta tanto "
                           "ahorrar."),
    ("Contabilidad mental", "Tratar la plata distinto según de dónde viene: gastar alegremente un premio y cuidar el "
                            "sueldo, aunque el peso valga lo mismo."),
    ("Paradoja del ahorro", "Si todos ahorran al mismo tiempo, se gasta menos, las empresas venden menos y al final el "
                            "ahorro total puede no aumentar."),
    ("Efecto riqueza", "Cuando sube el valor de lo que tenés (tu casa, tus acciones), te sentís más rico y gastás más, "
                       "aunque tu sueldo no haya cambiado."),
    ("Ley de Gresham", "«La moneda mala desplaza a la buena»: si circulan dos monedas, la gente gasta la mala y guarda "
                       "la buena. Pesos para pagar, dólares al colchón."),
    ("Curva de Phillips", "La idea de que hay una relación entre inflación y desempleo: bajar uno a veces cuesta subir "
                          "el otro, al menos por un tiempo."),
    ("Keynesianismo", "Escuela inspirada en John M. Keynes: en las crisis, el Estado debe gastar más para sostener la "
                      "demanda y el empleo."),
    ("Monetarismo", "Escuela liderada por Milton Friedman: la inflación es siempre un fenómeno monetario y se controla "
                    "con la cantidad de dinero."),
    ("Escuela austríaca", "Corriente que defiende el libre mercado y critica la intervención del Estado y de los bancos "
                          "centrales. Mises y Hayek son sus referentes."),
    ("Raúl Prebisch", "Economista argentino, primer gerente general del BCRA (1935) y figura central de la CEPAL. Uno "
                      "de los más influyentes de América Latina."),
    ("Adam Smith", "Filósofo escocés considerado el padre de la economía moderna. Su libro «La riqueza de las "
                   "naciones» (1776) explicó la división del trabajo."),
    ("División del trabajo", "Repartir las tareas para que cada uno se especialice. Adam Smith mostró que una fábrica "
                             "de alfileres producía mucho más así."),
    ("Ceteris paribus", "Expresión latina que usan los economistas: «todo lo demás constante». Sirve para analizar el "
                        "efecto de una sola cosa a la vez."),
    ("Macroeconomía", "Estudia la economía en su conjunto: inflación, desempleo, crecimiento, dólar, déficit. De eso "
                      "trata este tablero."),
    ("Efecto contagio", "Cuando la crisis de un país se traslada a otros, por comercio o por miedo de los inversores."),
    ("Efecto Tequila", "La crisis de 1994-1995 que empezó en México y golpeó a toda América Latina. En la Argentina "
                       "provocó salida de depósitos y recesión."),
    ("Too big to fail", "«Demasiado grande para caer»: bancos o empresas tan grandes que el Estado los rescata para "
                        "evitar un desastre mayor."),
    ("Corrida bancaria", "Cuando muchos ahorristas, por miedo, van a retirar sus depósitos al mismo tiempo. Ningún "
                         "banco tiene toda la plata disponible a la vez."),
    ("Apalancamiento", "Usar deuda para invertir más de lo que se tiene. Multiplica las ganancias… y también las "
                       "pérdidas."),
    # ── Historia económica argentina ──
    ("Rodrigazo", "El ajuste de junio de 1975, con el ministro Celestino Rodrigo: fuerte devaluación y tarifazos que "
                  "dispararon la inflación."),
    ("Plata dulce", "Fines de los 70: con el dólar barato, la clase media viajaba y compraba importado. Inmortalizado "
                    "en una película de 1982."),
    ("Deme dos", "La frase de los turistas argentinos en Miami a fines de los 70, cuando con el dólar barato todo "
                 "parecía en oferta."),
    ("La tablita", "Esquema de devaluaciones anunciadas por adelantado de 1978-1981, con Martínez de Hoz. Terminó en "
                   "una fuerte crisis."),
    ("Plan Austral", "Plan de estabilización de 1985: nueva moneda (el austral), congelamiento de precios y salarios. "
                     "Bajó la inflación por un tiempo."),
    ("Hiperinflación de 1989", "La inflación llegó a casi 200% en un solo mes (julio de 1989). Los precios cambiaban "
                               "mientras uno hacía la fila del súper."),
    ("Plan Bonex", "En 1990 se canjearon compulsivamente los plazos fijos por bonos en dólares a 10 años para frenar la "
                   "hiperinflación."),
    ("Convertibilidad", "Régimen de 1991 a 2001: por ley, un peso valía un dólar. Terminó con la inflación, pero no "
                        "resistió la falta de dólares."),
    ("Blindaje", "Paquete de préstamos internacionales de fines de 2000 para sostener a la Argentina. No alcanzó."),
    ("Megacanje", "Canje de deuda de 2001 que estiró vencimientos a cambio de tasas muy altas. Fue el preludio del "
                  "default."),
    ("Déficit cero", "Ley de 2001 que obligaba a gastar solo lo recaudado, incluso recortando sueldos y jubilaciones."),
    ("Corralito", "Diciembre de 2001: límite a la extracción de efectivo de los bancos. Se podían sacar 250 pesos por "
                  "semana."),
    ("Pesificación asimétrica", "En 2002, las deudas en dólares se pasaron a pesos a 1 a 1 y los depósitos a 1,40 a 1. "
                                "La diferencia la absorbió el Estado."),
    ("Default de 2001", "La mayor cesación de pagos de deuda soberana de la historia hasta ese momento, declarada en "
                        "diciembre de 2001."),
    ("Canje de 2005", "La reestructuración de la deuda en default, con una quita importante. Aceptó cerca del 76% de "
                      "los acreedores (luego se sumó más en 2010)."),
    ("Pago al FMI de 2006", "La Argentina canceló de una sola vez toda su deuda con el FMI: unos 9.500 millones de "
                            "dólares."),
    ("Conflicto del campo", "La disputa de 2008 por las retenciones móviles a la soja (Resolución 125), que terminó con "
                            "el voto del vicepresidente en el Senado."),
    ("Intervención del INDEC", "Entre 2007 y 2015 las estadísticas oficiales de inflación fueron cuestionadas y el FMI "
                               "llegó a emitir una moción de censura."),
    ("Club del trueque", "Ferias de intercambio sin pesos que explotaron en la crisis de 2001, con sus propios "
                         "«créditos» como moneda."),
    ("Precios Cuidados", "Programa de acuerdos de precios para una canasta de productos en supermercados, lanzado en "
                         "2014."),
    ("Ahora 12", "Programa de compras en 12 cuotas fijas con tarjeta, lanzado en 2014 para impulsar el consumo."),
    ("Swap chino", "El acuerdo de intercambio de monedas con el Banco Popular de China, firmado por primera vez en "
                   "2009. Suma yuanes a las reservas del BCRA."),
    ("Bono a 100 años", "En 2017 la Argentina emitió un bono que vence en 2117. Pocos países lo hicieron."),
    ("Granero del mundo", "Así se llamaba a la Argentina a principios del siglo XX, cuando era una de las mayores "
                          "exportadoras de granos y carne del planeta."),
    ("Modelo agroexportador", "El esquema económico argentino entre 1880 y 1930: exportar carne y granos a Europa e "
                              "importar manufacturas."),
    # ── Lunfardo y vida cotidiana ──
    ("Guita", "Dinero, en lunfardo. Probablemente del caló o del italiano, aunque su origen se discute."),
    ("Mango", "Un peso, en lunfardo. «No tengo un mango» es no tener ni un peso."),
    ("Luca", "Mil pesos, en lunfardo. Con la inflación, la luca pasó de ser mucha plata a ser poca."),
    ("Gamba", "Cien pesos en lunfardo. Una gamba hoy alcanza para poco."),
    ("Palo", "Un millón (de pesos o de dólares). «Un palo verde» es un millón de dólares."),
    ("Verdes", "Los dólares, por el color de sus billetes. Hacerse de unos verdes es el reflejo argentino."),
    ("Ahorrar en ladrillos", "Comprar inmuebles para resguardar el valor del dinero. En la Argentina, uno de los "
                             "refugios más tradicionales."),
    ("Vaquita", "Juntar plata entre varios para comprar algo en común. Microfinanzas en estado puro."),
    ("Fiado", "Comprar en el almacén del barrio y pagar después, anotado en la libreta. Crédito basado en la "
              "confianza."),
    ("Changa", "Trabajo ocasional y corto, generalmente informal. Muchas veces sirve para redondear el mes."),
    ("Pluriempleo", "Tener más de un trabajo para llegar a fin de mes. Creció en épocas de salarios bajos."),
    ("Llegar a fin de mes", "Que el sueldo alcance hasta el próximo cobro. El indicador económico más sentido por "
                            "cualquiera."),
    ("Cuenta sueldo", "La cuenta bancaria donde se deposita el salario. Es gratuita por ley."),
    ("Recibo de sueldo", "El papel (o PDF) que detalla lo que se cobra y los descuentos: jubilación, obra social, "
                         "sindicato y, si corresponde, Ganancias."),
    ("Bruto y neto", "El sueldo bruto es el total antes de descuentos; el neto, lo que efectivamente llega a la cuenta."),
    ("Expensas", "Los gastos comunes de un edificio (limpieza, encargado, ascensor) que pagan los propietarios o "
                 "inquilinos."),
    ("Alquiler", "Lo que se paga por usar una vivienda o un local ajeno. Su forma de ajuste cambió varias veces de ley "
                 "en los últimos años."),
    ("Ley de alquileres", "La ley de 2020 que fijó contratos de 3 años con ajuste anual por el ICL. Se derogó en 2023 "
                          "y hoy las partes acuerdan libremente."),
    ("Precio de lista y contado", "En la Argentina es común que pagar en efectivo o transferencia tenga descuento "
                                  "frente al precio con tarjeta."),
    ("Promoción bancaria", "Descuentos o reintegros que dan los bancos y billeteras al pagar con sus medios. Hay "
                           "quienes organizan las compras de la semana alrededor de ellas."),
    ("Reintegro", "Parte del pago que te devuelven después de comprar, en general en el resumen de la tarjeta o en la "
                  "billetera."),
    ("Inflación de góndola", "Lo que la gente percibe al hacer las compras. Puede diferir del IPC, porque cada familia "
                             "tiene su propia canasta."),
    ("Reduflación", "Cuando un producto mantiene el precio pero trae menos cantidad: el paquete de galletitas que "
                    "misteriosamente adelgazó."),
    ("Precio psicológico", "Poner $9.999 en lugar de $10.000: el cerebro lee «nueve mil y pico» y siente que es más "
                           "barato."),
    ("Marca blanca", "Productos con la marca del supermercado, generalmente más baratos que las primeras marcas."),
    ("Consumo masivo", "Los productos que se compran todos los días: alimentos, bebidas, limpieza, higiene. Sus ventas "
                       "son un termómetro del bolsillo."),
    ("Black Friday y Hot Sale", "Eventos de descuentos online. El Hot Sale es la versión argentina, en mayo. Conviene "
                                "comparar precios desde antes."),
    ("Plan de ahorro", "Sistema para comprar un auto pagando cuotas en un grupo; la adjudicación es por sorteo o "
                       "licitación. Las cuotas suelen ajustarse por el precio del auto."),
    ("Seguro", "Pagar una cuota fija para que, si pasa algo malo, otro cubra el costo. Es repartir el riesgo entre "
               "muchos."),
    ("Obra social y prepaga", "La obra social se financia con aportes del sueldo; la prepaga es un servicio privado que "
                              "se paga aparte (o derivando esos aportes)."),
    ("Costo de vida", "Lo que cuesta mantener cierto nivel de vida en un lugar y momento. Vivir en CABA no cuesta lo "
                      "mismo que en Santiago del Estero."),
    ("Consumo de bienes durables", "Compras que duran años: autos, heladeras, lavarropas. Se postergan en las crisis y "
                                   "se adelantan cuando se espera inflación."),
    ("Ventas en cuotas", "Una costumbre muy argentina para estirar el sueldo. Con inflación alta, las cuotas fijas "
                         "terminan siendo más baratas."),
    ("Inflación y cuotas", "Si la inflación es mayor que la tasa de las cuotas, conviene pagar en cuotas: devolvés "
                           "pesos que valen menos."),
    ("Ahorro en dólares", "La forma más tradicional de ahorrar en la Argentina, por la desconfianza histórica en el "
                          "peso. Protege de devaluaciones, no siempre de la inflación en dólares."),
    ("Inflación en dólares", "Cuando los precios en pesos suben más que el dólar: el país se encarece medido en "
                             "dólares. Pasa en épocas de dólar quieto."),
    ("Caro en dólares", "Cuando, al pasar los precios a dólares, la Argentina resulta más cara que otros países. Lo "
                        "notan sobre todo los turistas."),
    ("Tour de compras", "Cruzar a Chile, Paraguay o Brasil a comprar más barato. Aparece cuando el país está «caro» en "
                        "dólares."),
    ("Inflación de servicios", "La suba de precios de lo que no se toca: colegios, prepagas, alquileres, peluquería. "
                               "Suele ser más pegajosa que la de bienes."),
    ("Bienes transables", "Los que se pueden comerciar con el exterior (granos, autos, ropa). Su precio sigue al "
                          "dólar."),
    ("Bienes no transables", "Los que no se importan ni se exportan fácilmente: un corte de pelo, un alquiler. Su "
                             "precio depende de lo que pasa adentro."),
    ("Puja distributiva", "La pelea entre sectores (empresarios, trabajadores, Estado) por quedarse con una parte "
                          "mayor del ingreso. Si nadie cede, alimenta la inflación."),
    ("Acuerdo de precios", "Pacto entre el gobierno y las empresas para mantener ciertos precios por un tiempo. Ayuda a "
                           "corto plazo, pero no ataca las causas de la inflación."),
    ("Congelamiento de precios", "Prohibir que los precios suban. Históricamente terminó en faltantes, mercado negro y "
                                 "subas mayores al levantarse."),
    ("Desabastecimiento", "Cuando faltan productos en las góndolas, muchas veces porque el precio fijado no cubre el "
                          "costo de producirlos."),
    ("Mercado negro", "El intercambio de bienes o divisas por fuera de la ley, cuando hay prohibiciones o precios "
                      "controlados."),
    ("Dólar ahorro", "El dólar oficial más impuestos que podían comprar las personas, con un tope de 200 por mes, "
                     "durante el cepo de 2019-2025."),
    ("Sistema financiero", "El conjunto de bancos, mercados, aseguradoras y fondos que llevan el ahorro de unos al "
                           "crédito de otros."),
    ("Pago con QR", "Pagar escaneando un código con el celular. Se popularizó en la pandemia y hoy es parte de la vida "
                    "diaria."),
    ("Pobreza estructural", "La que persiste de generación en generación, incluso cuando la economía crece. Requiere "
                            "algo más que crecimiento para resolverse."),
    ("Reserva Federal", "El banco central de Estados Unidos (la Fed). Cuando sube su tasa, el dinero del mundo tiende "
                        "a irse a EE. UU. y se complica a los emergentes."),
    ("Depósitos en dólares", "Los dólares que los ahorristas tienen en bancos argentinos. Por regla, los bancos solo "
                             "pueden prestarlos a quien cobra en dólares."),
    ("Compra y venta", "En una casa de cambio, el precio de compra es lo que te pagan por tus dólares; el de venta, lo "
                       "que te cobran por dártelos. La diferencia es su ganancia."),
    ("Casa de cambio", "Comercio autorizado para comprar y vender monedas extranjeras al público."),
    ("Dólar cara chica", "Los billetes de dólar de diseño viejo, con la cara más pequeña. Hubo épocas en que se "
                         "pagaban menos que los nuevos, aunque valen lo mismo."),
    ("Cajas de seguridad", "Cofres en los bancos donde se guardan dólares y objetos de valor. Muy populares en la "
                           "Argentina como alternativa al colchón."),
]


def termino_del_dia(fecha: pd.Timestamp) -> tuple[str, str]:
    """El término que toca en `fecha`: uno distinto cada día del año (el 29 de febrero repite el primero)."""
    return TERMINOS[(fecha.dayofyear - 1) % len(TERMINOS)]
