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

- Muchas medidas proceden de resúmenes de prensa que citan los programas. Se están contrastando, página a página, con los programas oficiales guardados en `programas/`.
- Muchas medidas carecen de cifras. En ese caso, el efecto es incierto o se indica «sin cifras».
- Frente Amplio y Podemos no habían publicado programa en la fecha de corte.
- Los niveles de exposición son juicios de los autores, explícitos en `data/medidas.json` y discutibles. Por eso son abiertos.
- Cobertura territorial desigual: el único partido territorial incluido es Coalición Canaria. ERC, Junts, PNV, EH Bildu, BNG, Compromís y otras candidaturas (como SALF) aún no están incluidos; el resultado lo avisa expresamente según la comunidad de quien responde. Se irán incorporando con la revisión diaria. Se aceptan contribuciones.

## Cómo proponer cambios

Toda medida, riesgo o exposición nueva debe llevar al menos una fuente enlazada (preferiblemente el programa oficial o un organismo independiente: AIReF, Banco de España, CNMC, Funcas, universidades). Si añades un riesgo a un partido, revisa si la misma lógica aplica a medidas equivalentes de otros partidos.
