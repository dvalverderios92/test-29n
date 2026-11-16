# Pone la web en pausa durante la jornada de reflexión (28 y 29 de noviembre de 2026).
# Sustituye la portada por un aviso.
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
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<style>body{{margin:0;font:17px/1.6 Archivo,system-ui,sans-serif;background:#E4D3AE;color:#1F1A12}}
@media (prefers-color-scheme:dark){{body{{background:#1B1711;color:#F3E8D0}}}}
main{{max-width:620px;margin:18vh auto;padding:0 20px}}h1{{font-stretch:125%;font-weight:850;font-size:clamp(2rem,9vw,3.4rem);line-height:1.05;letter-spacing:-.02em}}</style></head>
<body><main><h1>Test 29N: en pausa</h1><p>{AVISO}</p></main></body></html>
""")
print("Pausa aplicada")
