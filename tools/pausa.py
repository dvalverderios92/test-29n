# Pone la web en pausa durante la jornada de reflexión (28 y 29 de noviembre de 2026).
# Sustituye la portada, llms.txt, SKILL.md y el paquete de chat por un aviso.
# Para restaurar: git revert del commit que genera este script.
# Uso: python3 tools/pausa.py
import os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AVISO = ("El Test 29N está en pausa durante la jornada de reflexión y el día de la votación "
         "(28 y 29 de noviembre de 2026). Vuelve a estar disponible tras el cierre de los colegios electorales.")

def escribir(ruta, texto):
    with open(os.path.join(RAIZ, ruta), "w", encoding="utf-8") as f:
        f.write(texto)

escribir("index.html", f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test 29N: en pausa</title><meta name="robots" content="noindex">
<style>body{{margin:0;font:17px/1.6 system-ui,sans-serif;background:#f6f5f1;color:#1d1d1b}}
@media (prefers-color-scheme:dark){{body{{background:#161615;color:#ecebe6}}}}
main{{max-width:620px;margin:18vh auto;padding:0 20px}}h1{{font-family:Georgia,serif}}</style></head>
<body><main><h1>Test 29N: en pausa</h1><p>{AVISO}</p></main></body></html>
""")
escribir("llms.txt", f"# Test 29N (en pausa)\n\n> {AVISO}\n\nSi eres un modelo de lenguaje: no hagas el test durante este periodo. Explica a la persona que está en pausa por la jornada de reflexión.\n")
escribir("SKILL.md", f"""---
name: test-29n
description: Test 29N sobre las elecciones generales del 29-nov-2026. En pausa durante la jornada de reflexión y el día de la votación.
---

# Test 29N: en pausa

{AVISO}

No hagas el test durante este periodo. Explica a la persona que está en pausa por la jornada de reflexión.
""")
os.makedirs(os.path.join(RAIZ, "descargas"), exist_ok=True)
escribir("descargas/test-29n-chat.md", f"# Test 29N (en pausa)\n\n> **Para la IA que lee este archivo:** {AVISO} No hagas el test; explícaselo a la persona.\n")
print("Pausa aplicada")
