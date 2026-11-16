# Test 29N: ¿qué medidas te afectan?

Cuestionario abierto y neutral sobre las **elecciones generales de España del 29 de noviembre de 2026**. Pregunta por tu situación socioeconómica y te muestra, para cada candidatura de tu comunidad:

1. **Riesgos indirectos**: lo que las medidas pueden provocar aunque no te toquen directamente (recaudación, gasto sin financiar, precios, empleo, oferta), según tu exposición.
2. **Efecto directo**: qué medidas te favorecen, te perjudican o tienen un efecto incierto.
3. **Financiación**: si el partido dice cuánto cuesta su programa y cómo lo paga.

Cada dato separa **hecho** de **inferencia** y lleva su fuente. No hay puntuación total ni recomendación de voto. El resultado se puede descargar como presentación PDF.

**Web:** https://dvalverderios92.github.io/test-29n/

## Quién lo hace

Daniel, a título personal. No ha colaborado con ningún partido ni recibe financiación de ninguno. La web no guarda respuestas: todo se calcula en el navegador, sin cookies ni analítica. Para avisar de un error: [formulario en GitHub](https://github.com/dvalverderios92/test-29n/issues/new?template=error.yml).

## Estructura

```
index.html            Web (lee data/medidas.json)
motor.js              Motor de evaluación, sin dependencias
pdf.js                Exporta el resultado como presentación PDF 16:9 (jsPDF, cargado bajo demanda)
data/medidas.json     Datos generados: preguntas, medidas, riesgos, partidos, candidaturas, fuentes
tools/gen_data.py     FUENTE DE VERDAD: genera data/medidas.json
tools/pausa.py        Pone la web en pausa durante la jornada de reflexión
programas/            Programas electorales oficiales (PDF) usados como fuente
docs/esquema.md       Especificación del JSON y de las condiciones
docs/metodologia.md   Criterios, controles de sesgo y limitaciones
tests/simetria.js     Pruebas de coherencia y simetría
```

## Actualizar los datos

Edita `tools/gen_data.py` (no el JSON directamente) siguiendo `docs/esquema.md`. Después:

```bash
python3 tools/gen_data.py && node tests/simetria.js
```

Toda medida o riesgo nuevo debe llevar fuente, preferiblemente el programa oficial con su página. GitHub ejecuta las mismas pruebas en cada propuesta de cambio.

## Jornada de reflexión

La web se retira el 28 y el 29 de noviembre de 2026 (jornada de reflexión y día de la votación) y vuelve tras el cierre de los colegios.

## Programas oficiales

Los PDF de `programas/` son documentos públicos de cada partido, incluidos solo como fuente verificable. Son propiedad de sus autores. Si algún partido quiere que se retire su documento, puede pedirlo con el formulario de errores.

## Licencias

- Código (`index.html`, `motor.js`, `pdf.js`, `tests/`, `tools/`): MIT (ver `LICENSE`). © 2026 Daniel Valverde Ríos.
- Datos y textos (`data/`, `docs/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).
