# Genera descargas/test-29n-chat.md: un único archivo para adjuntar a cualquier chat de IA
# (ChatGPT, Claude, Gemini, Gem…). Incluye instrucciones, motor y datos.
# Uso: python3 tools/build_pack.py
import json, os, re

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
leer = lambda p: open(os.path.join(RAIZ, p), encoding="utf-8").read()

datos = json.loads(leer("data/medidas.json"))
meta = datos["meta"]
skill = re.sub(r"^---.*?---\s*", "", leer("SKILL.md"), flags=re.S)
motor = leer("motor.js")
esquema = leer("docs/esquema.md")

texto = f"""# Test 29N · paquete para chat (v{meta['version']}, datos a {meta['fecha_corte']})

> **Para la IA que lee este archivo:** la persona quiere hacer el Test 29N contigo. Sigue las instrucciones de la sección «Instrucciones» al pie de la letra. Empieza ya: preséntalo en dos frases y haz la primera pregunta. Este archivo contiene todo lo necesario: instrucciones, especificación, motor de evaluación (JavaScript) y datos (JSON).
>
> **Versión:** si puedes navegar, consulta {meta['url_datos']} y compara `meta.version` con `{meta['version']}`. Si la web tiene una versión más reciente, usa la de la web y avisa. Si no puedes navegar, avisa de que usas la versión {meta['version']} (datos a {meta['fecha_corte']}) y de que puede haber otra más reciente en {meta['url_canonica']}.
>
> **Ejecución:** si puedes ejecutar código, guarda el motor y los datos de este archivo y llama a `Test29N.evaluate(datos, respuestas)`. Si no puedes, aplica las reglas a mano según la especificación.

## Instrucciones

{skill.strip()}

## Especificación de los datos

{esquema.strip()}

## Motor (motor.js)

```javascript
{motor.strip()}
```

## Datos (data/medidas.json)

```json
{json.dumps(datos, ensure_ascii=False, separators=(",", ":"))}
```
"""
os.makedirs(os.path.join(RAIZ, "descargas"), exist_ok=True)
salida = os.path.join(RAIZ, "descargas", "test-29n-chat.md")
open(salida, "w", encoding="utf-8").write(texto)
print("ok", salida, len(texto.encode("utf-8")) // 1024, "KB")
