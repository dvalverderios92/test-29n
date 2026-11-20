# Metodología

## Qué mide y qué no

El test responde a una pregunta concreta: **¿cómo me afectarían a mí las principales medidas de cada partido?** Lo hace en tres capas que no se suman entre sí.

1. **Efecto directo.** El impacto económico personal e inmediato de una medida según las respuestas (pagar más o menos impuestos, cobrar una ayuda, ver limitada una renta…). Toma tres valores: a favor (+1), en contra (−1) o incierto (0).
2. **Riesgos indirectos.** Lo que una medida puede provocar aunque no te toque directamente: menos recaudación, gasto sin financiar, traslado de ayudas a precios, efectos sobre el empleo o la oferta de alquiler, inseguridad jurídica. Se recogen de **todas** las medidas del partido y se gradúan por la **exposición** de quien responde (alta, media o baja).
3. **Financiación.** Si el partido cuantifica el coste de su programa y de dónde sale el dinero.

No mide la viabilidad política, la probabilidad de que una medida se apruebe, ni valores no económicos. No es una recomendación de voto.

## Por qué tres capas

La primera versión solo medía el efecto directo, y eso sesgaba el resultado. Si solo se cuenta el efecto directo:

- cualquier rebaja de impuestos sale «a favor» de quien paga ese impuesto, aunque su coste recaiga en los servicios públicos que esa persona usa;
- cualquier gasto nuevo sale «a favor» de quien lo recibe, aunque nadie diga cómo se paga;
- cualquier regulación sale «a favor» de quien protege ahora, aunque pueda reducir la oferta para quien llegue después.

En los tres casos, el sesgo favorece a quien promete más sin decir cuánto cuesta, sea cual sea su ideología. La capa de riesgos existe para corregirlo.

## Controles de sesgo

- **Simetría de los riesgos fiscales.** Las rebajas sin financiar activan `rebaja_sin_financiar`, con exposición alta para quien depende mucho de servicios públicos. El gasto sin financiar activa `gasto_sin_financiar`, con exposición alta para rentas altas y grandes patrimonios. Así, cada promesa sin financiación expone sobre todo a quien probablemente pagaría su factura.
- **Riesgos en ambas direcciones en vivienda.** Los topes y prórrogas activan `tope_alquiler_oferta` y su eliminación activa `fin_topes_alquiler`. Los dos están marcados como evidencia disputada y citan estudios en sentidos distintos.
- **Las ayudas a la demanda se tratan igual las proponga quien las proponga** (IVA reducido, aval o hucha del PP, préstamo TU CASA del PSOE, ITP 0 de Vox, ayudas de CC): todas activan `ayuda_demanda_precio`.
- **Escala.** Cada vínculo entre una medida y un riesgo es «amplio» (impuesto o programa general, o coste grande publicado) o «acotado» (colectivo concreto o medida condicional). Un riesgo activado solo por medidas acotadas no pasa de exposición media. Así se evita, por ejemplo, que una deducción condicional pese lo mismo que una rebaja general del IRPF.
- **Peso de los riesgos.** Los resultados empiezan por la tabla comparativa de riesgos indirectos y, dentro de cada partido, los riesgos van antes que el efecto directo. Es una decisión deliberada: el efecto directo es fácil de ver y los riesgos no.
- **Mismo formato para todos.** Mismo orden de secciones, orden alfabético, sin puntuación total ni ranking.
- **Etiquetas de evidencia.** `hecho` (dato verificable), `consenso`, `disputada` e `inferencia` (razonamiento de los autores sin estudio específico). Una inferencia nunca se presenta como hecho.
- **Etiquetas de origen.** `programa` (programa del 29N), `campaña` (anuncio o declaración) y `previa` (posición anterior no confirmada).
- **Prueba automática.** `tests/simetria.js` recorre miles de perfiles y comprueba, entre otras cosas, que ningún partido sale sin riesgos y que todo partido tiene al menos un perfil al que perjudica directamente.

## Limitaciones conocidas

- **Jerarquía de fuentes, igual en todos los bloques:** 1) el programa oficial del 29N, con su página (carpeta `programas/`); 2) si el programa no recoge el asunto o el partido no tiene programa, anuncios de campaña del 29N; 3) si tampoco hay, posiciones anteriores (programas o declaraciones previas). Cada medida indica su origen y enlaza a su fuente. Las cifras que el programa no da y aparecen en prensa se atribuyen a esa fuente.
- Muchas medidas carecen de cifras. En ese caso, el efecto es incierto o se indica «sin cifras».
- Candidaturas conjuntas (desde la v2.12, mismo criterio en todas): se incluyen las medidas de un partido cuando forma parte de la coalición inscrita o encabeza la lista por acuerdo; no, cuando solo aporta candidatos independientes. Por eso Podemos entra en Unidad del Pueblo Canario y en Compromís-Front Valencià, pero no en la lista de ERC (Cataluña) ni en la de Ara Més-Front Ampli (Baleares). En Melilla no presenta lista.
- Los niveles de exposición son juicios de los autores, explícitos en `data/medidas.json` y discutibles. Por eso son abiertos.
- Cobertura territorial desigual: los partidos territoriales incluidos son Coalición Canaria, ERC (desde la v2.7, en Cataluña y, dentro de Ara Més-Front Ampli, en Baleares; su programa está en catalán y los resúmenes son traducciones), el BNG (desde la v2.11, en Galicia; su programa está en gallego y los resúmenes son traducciones), EH Bildu (desde la v2.12, en el País Vasco y Navarra), el PNV (desde la v2.13, en el País Vasco) y Compromís (desde la v2.15, dentro de Compromís-Front Valencià; usa el programa común de la candidatura, en valenciano, y los resúmenes son traducciones). SALF, desde la v2.12, en todas las comunidades salvo Cantabria. Junts y otras candidaturas aún no están incluidos; el resultado lo avisa expresamente según la comunidad de quien responde. Se irán incorporando con la revisión diaria. Se aceptan contribuciones.

## Cómo proponer cambios

Toda medida, riesgo o exposición nueva debe llevar al menos una fuente enlazada (preferiblemente el programa oficial o un organismo independiente: AIReF, Banco de España, CNMC, Funcas, universidades). Si añades un riesgo a un partido, revisa si la misma lógica aplica a medidas equivalentes de otros partidos.

## Derechos y protecciones (desde la v2.6)

Bloque aparte y opcional sobre temas sociales: igualdad y violencia contra las mujeres, derechos LGTBIQ+, racismo y pueblo gitano, migración, discapacidad, familia, modelo educativo, aborto y final de la vida, religión y laicidad, y mundo rural.

- **Sin valoración.** En lo económico se puede decir si pagas más o menos. En lo social, la misma medida la valoran al revés personas en la misma situación, así que el test no marca nada como «a favor» o «en contra». Cada medida es un resumen fiel del programa oficial, con su número y un enlace a la página del PDF.
- **Preguntas sensibles opcionales.** Género, pertenencia al colectivo LGTBIQ+, minoría étnica, discapacidad y religión. Todas tienen «Prefiero no contestar». Solo sirven para dejar marcados de partida los temas de la última pregunta: no cambian ninguna medida ni riesgo, y no aparecen en el PDF ni en el texto copiado. Las pruebas automáticas lo comprueban.
- **Simetría.** Los temas incluyen asuntos que priorizan votantes de sensibilidades distintas, y se recogen con el mismo criterio para todos los partidos. Si no hay nada ni en el programa ni en otras fuentes consultadas, se indica así.
- **Partidos sin programa o temas que el programa no trata.** Se aplica la misma jerarquía: anuncios de campaña y, si no hay, posiciones anteriores (por ejemplo, el aborto en el caso del BNG, con su programa europeo de 2024). Si no hay nada en ninguna fuente consultada, se indica así.

## Plazo, coste y criterios de redacción (desde la v2.8)

- **Plazo y coste.** Solo se indican cuando la fuente los da, en el campo `detalle` (tabla `DETALLE` del generador). Si no hay, la web y el PDF dicen una vez, para todos los partidos: «Salvo que se indique, el partido no fija plazo ni coste para cada medida». Las cifras de campaña se atribuyen («según el partido en campaña»).
- **Misma redacción para todos.** No se añaden acotaciones como «sin concretar» o «sin umbrales» a unas medidas y no a otras. Lo que la medida no concreta se ve en el propio texto.
- **Financiación.** El resumen de cada partido sigue la misma estructura: si cuantifica el coste total, qué cifras da y de dónde dice sacar el dinero. Sin valoraciones de terceros (Gobierno, oposición o analistas) aplicadas solo a algunos partidos.
- **Zonas tensionadas (desde la v2.14).** Que una zona no esté declarada no significa que no pueda estarlo: la declaración depende de que se pida y de que la apruebe la administración competente, en cualquier comunidad. Si el inquilino responde que su zona no está declarada pero los alquileres han subido mucho, el riesgo de eliminar las zonas tensionadas le afecta algo (no poco). Para él, las medidas que las derogan tienen un efecto incierto, y las que las refuerzan se valoran igual que para los demás inquilinos, porque solo le llegarían si su zona se declara.
- **Vocabulario.** Los términos propios de cada partido se mantienen solo cuando resumen su propuesta; el test no los usa en sus propios textos.

## Presentación del resultado (desde la v2.10)

- **Resumen en un minuto:** una línea por partido, en orden alfabético y con la misma plantilla (`resumenPartido` en `motor.js`): medidas a favor, en contra e inciertas; los temas de las que van en contra; los riesgos que te afectan mucho, por su nombre, y cuántos te afectan algo.
- **Lenguaje llano:** «te afecta mucho, algo, poco» en lugar de «exposición alta, media, baja», y la evidencia como «comprobado», «la mayoría de expertos coincide», «los expertos discrepan» o «deducción del test».
- **PDF:** primero la presentación (portada, resumen, riesgos, una diapositiva por partido y «antes de decidir») y después un anexo con el detalle. En la diapositiva de cada partido, la misma regla para todos: primero las medidas en contra, después las inciertas y después las a favor, hasta seis; el resto va al anexo.
