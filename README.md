# Test 29N: ¿qué medidas te afectan?

Cuestionario abierto y neutral sobre las **elecciones generales de España del 29 de noviembre de 2026**. Pregunta por tu situación socioeconómica y te muestra, partido por partido:

1. **Efecto directo**: qué medidas te favorecen, te perjudican o tienen un efecto incierto.
2. **Riesgos indirectos**: lo que las medidas pueden provocar aunque no te toquen directamente (recaudación, gasto sin financiar, precios, empleo, oferta), según tu exposición.
3. **Financiación**: si el partido dice cuánto cuesta su programa y cómo lo paga.

Cada dato separa **hecho** de **inferencia** y lleva su fuente. No hay puntuación total ni recomendación de voto.

**Web:** https://dvalverderios92.github.io/test-29n/

## Cómo usarlo

**En el navegador:** abre la web y responde.

**Con tu asistente de IA** (Claude, ChatGPT, Gemini, un agente propio…):

- Desde la web, pulsa «Abrir en ChatGPT» o «Abrir en Claude»: se abre el chat con la instrucción ya escrita.
- Con cualquier otra IA, copia la instrucción de la web o adjunta el paquete `descargas/test-29n-chat.md` (instrucciones, motor y datos en un único archivo).
- Gemini: [Gem del Test 29N](https://gemini.google.com/gem/1jjjGM5yY05jS_uJGa-R4ZZlTcCUx4aVH?usp=sharing) (cómo se creó y cómo actualizarlo: `docs/gem.md`).
- En Claude puedes instalarlo como *skill*: descarga el repositorio como ZIP y súbelo como skill. `SKILL.md` está en la raíz.
- Para agentes con ejecución de código:

  ```bash
  node -e 'const T=require("./motor.js"),D=require("./data/medidas.json");console.log(JSON.stringify(T.evaluate(D,{"region":"madrid","edad":"26-35","lab":"asal_ind","ing":2,"dep_pub":"media","viv":"alquiler","tens":"si","comprar":true,"otras":0,"hijos":["ninguno"],"planHijos":false,"dep":"no","patr":1,"ahorro":1,"bolsa":false,"herencia":false,"nac":"es"}),null,1))'
  ```

## Estructura

```
index.html            Web interactiva (lee data/medidas.json)
motor.js              Motor de evaluación, sin dependencias (navegador y Node)
pdf.js                Exporta el resultado como presentación PDF 16:9 (jsPDF, cargado bajo demanda)
data/medidas.json     Datos generados: preguntas, medidas, riesgos, partidos, fuentes
tools/gen_data.py     FUENTE DE VERDAD: genera data/medidas.json
tools/build_pack.py   Genera descargas/test-29n-chat.md
descargas/            Paquete único para adjuntar a cualquier chat
docs/gem.md           Cómo crear el Gem de Gemini
SKILL.md              Instrucciones para asistentes de IA (formato skill)
llms.txt              Índice para modelos de lenguaje
docs/esquema.md       Especificación del JSON y de las condiciones
docs/metodologia.md   Criterios, controles de sesgo y limitaciones
tests/simetria.js     Pruebas de coherencia y simetría (node tests/simetria.js)
```

## Actualizar los datos

Edita `tools/gen_data.py` (no el JSON directamente) siguiendo `docs/esquema.md`. Después:

```bash
python3 tools/gen_data.py && python3 tools/build_pack.py && node tests/simetria.js
```

Toda medida o riesgo nuevo debe llevar fuente. Cambia `meta.fecha_corte` y `meta.version` en cada actualización.

## Fecha de corte y estado

Datos a **16 de noviembre de 2026**. En esa fecha habían publicado programa PP (10-nov), Vox (12-nov), PSOE (15-nov) y Coalición Canaria (9-nov). Frente Amplio y Podemos no lo habían hecho; sus medidas proceden de anuncios de campaña y posiciones previas, y se marcan así.

## Jornada de reflexión

La web se retira el 28 y el 29 de noviembre de 2026 (jornada de reflexión y día de la votación) y vuelve después del cierre de los colegios.

## Licencias

- Código (`index.html`, `motor.js`, `tests/`, `tools/`): MIT (ver `LICENSE`). © 2026 Daniel Valverde Ríos.
- Datos y textos (`data/`, `docs/`, `SKILL.md`, `llms.txt`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).

Las medidas resumen documentos de los partidos y artículos de prensa enlazados; esos documentos son propiedad de sus autores.
