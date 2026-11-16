# Esquema de `data/medidas.json`

Un solo archivo JSON con estas claves de primer nivel:

| Clave | Contenido |
|---|---|
| `meta` | Título, versión, `fecha_corte`, aviso y glosarios (`valores`, `evidencia`, `origen`). |
| `condiciones` | Condiciones con nombre, reutilizables con `{"ref": "nombre"}`. |
| `preguntas` | Cuestionario, en orden. |
| `partidos` | Partido, estado del programa y financiación declarada. |
| `riesgos` | Efectos indirectos reutilizables, con nivel de evidencia y exposición según el perfil. |
| `medidas` | Medidas por partido, con sus efectos directos y los riesgos que activan. |
| `fuentes` | Diccionario `id → {titulo, url, fecha}`. |

## Preguntas

```json
{"id":"viv","texto":"¿Cómo es tu vivienda habitual?","tipo":"unica",
 "opciones":[{"valor":"alquiler","texto":"Vivo de alquiler"}],
 "mostrar_si":{"ref":"..."}, "ayuda":"...", "ninguno":"ninguno"}
```

- `tipo`: `unica` (un valor) o `multi` (lista de valores).
- `mostrar_si` (opcional): la pregunta solo se hace si la condición se cumple con las respuestas previas.
- `ninguno` (solo en `multi`): un valor que excluye a los demás.

Las respuestas forman un objeto `{id_pregunta: valor}`. Las respuestas a preguntas ocultas se descartan.

## Condiciones

Una condición es un objeto con una de estas formas:

| Forma | Se cumple si… |
|---|---|
| `{"siempre": true}` | siempre |
| `{"ref": "nombre"}` | se cumple la condición con nombre `condiciones.nombre` |
| `{"all": [c1, c2]}` | se cumplen todas |
| `{"any": [c1, c2]}` | se cumple alguna |
| `{"not": c}` | no se cumple `c` |
| `{"q": "id", "eq": v}` | la respuesta es igual a `v` |
| `{"q": "id", "in": [v1, v2]}` | la respuesta está en la lista |
| `{"q": "id", "gte": n}` / `"lte"` | la respuesta numérica es ≥ / ≤ `n` |
| `{"q": "id", "includes": v}` | la respuesta (lista) contiene `v` |
| `{"q": "id", "includesAny": [..]}` | la respuesta (lista) contiene alguno |

**Regla clave:** si la pregunta `q` no tiene respuesta (no se hizo o la persona no contestó), cualquier comparación sobre ella es **falsa**.

## Medidas

```json
{"id":"pp-179","partido":"pp","tema":"IRPF","texto":"…","num":"179",
 "origen":"programa|campaña|previa","fuentes":["rankia"],
 "efectos":[{"si":COND,"valor":1,"texto":"…"}, …],
 "riesgos":[{"id":"rebaja_sin_financiar","escala":"amplia|acotada"}], "universal":false}
```

- **Efecto directo:** se recorre `efectos` en orden y gana el primero cuya condición se cumple. `valor` vale `1` (a favor), `-1` (en contra) o `0` (incierto o no aplica directamente). Si ninguno se cumple, la medida no afecta a la persona y no se muestra.
- `universal: true`: la medida afecta a casi todos por igual. No tiene efectos personales, pero sí aporta riesgos.
- `riesgos`: riesgos indirectos que la medida activa **para el partido**, afecte o no a la persona. La `escala` vale `amplia` (impuesto o programa general, o coste grande publicado) o `acotada` (colectivo concreto o medida condicional).

## Riesgos

```json
{"id":"rebaja_sin_financiar","titulo":"…","evidencia":"hecho|hecho+inferencia|consenso|disputada|inferencia",
 "que_pasa":"…","fuentes":[…],
 "exposicion":[{"si":COND,"nivel":"alta|media|baja","texto":"…"}, …]}
```

Para cada partido se reúnen los riesgos de **todas** sus medidas, se eliminan duplicados y, para cada uno, gana la primera `exposicion` cuya condición se cumple. La última entrada siempre es `{"siempre":true}`, así que todo riesgo tiene un nivel.

**Regla de escala:** si todos los vínculos de un riesgo en un partido son `acotada`, una exposición `alta` baja a `media`.

**Matriz de riesgos:** el motor devuelve también `matriz_riesgos`, con una fila por riesgo y una columna por partido; cada celda es el nivel de exposición, o `null` si el partido no activa ese riesgo.

## Notas

```json
"notas":[{"si":COND,"texto":"…"}]
```

Avisos contextuales (desempleo, IVA en Canarias, dependencia…) que se muestran cuando se cumple su condición. Así, la web y los asistentes de IA muestran exactamente los mismos avisos.

## Partidos

```json
{"id":"pp","nombre":"PP","ambito_si":COND?,
 "programa":{"titulo":"…","fecha":"AAAA-MM-DD|null","estado":"publicado|sin_programa","nota":"…"},
 "financiacion":{"cuantifica":"no|si|cifras_propias|fuera_del_programa","resumen":"…","fuentes":[…]}}
```

`ambito_si` limita un partido territorial a quien cumpla la condición (p. ej., Coalición Canaria solo para residentes en Canarias). Los partidos se muestran en orden alfabético.
