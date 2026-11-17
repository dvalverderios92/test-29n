# Genera data/medidas.json. ESTE ARCHIVO ES LA FUENTE DE VERDAD del Test 29N.
# Uso: python3 tools/gen_data.py   (escribe data/medidas.json)
# Después: node tests/simetria.js
import json, sys, os

def Q(q, **kw):
    d = {"q": q}; d.update(kw); return d
def ALL(*c): return {"all": list(c)}
def ANY(*c): return {"any": list(c)}
def NOT(c): return {"not": c}
def R(name): return {"ref": name}
ALWAYS = {"siempre": True}

COND = {
 "asalariado": Q("lab", **{"in": ["asal_ind", "asal_temp"]}),
 "trabaja": Q("lab", **{"in": ["asal_ind", "asal_temp", "autonomo", "empresario"]}),
 "empleador": Q("emp", eq=True),
 "empresario": Q("lab", eq="empresario"),
 "parado": Q("lab", eq="parado"),
 "estudiante": Q("lab", eq="estudiante"),
 "pensionista": Q("lab", eq="pension"),
 "pension_no_contributiva": Q("pensTipo", eq="nocontrib"),
 "autonomo": Q("lab", eq="autonomo"),
 "quiere_emprender": Q("emprender", eq=True),
 "autonomo_o_futuro": ANY(Q("lab", eq="autonomo"), Q("emprender", eq=True)),
 "renta_smi": Q("ing", eq=1),
 "renta_baja": Q("ing", lte=2),
 "renta_alta": Q("ing", gte=5),
 "paga_irpf": ALL(Q("ing", gte=2), Q("lab", **{"in": ["asal_ind", "asal_temp", "autonomo", "empresario", "pension"]})),
 "joven_18_35": Q("edad", **{"in": ["18-25", "26-35"]}),
 "menor_40": Q("edad", **{"in": ["18-25", "26-35", "36-40"]}),
 "edad_41_64": Q("edad", eq="41-64"),
 "con_hijos": Q("hijos", includesAny=["h0_3", "h3_7", "h8_17"]),
 "hijos_0_3": Q("hijos", includes="h0_3"),
 "hijos_menores_8": Q("hijos", includesAny=["h0_3", "h3_7"]),
 "quiere_hijos": Q("planHijos", eq=True),
 "quizas_hijos": Q("planHijos", eq="ns"),
 "cuida_dependiente": Q("dep", **{"in": ["personal", "profesional", "ambas"]}),
 "paga_cuidados_profesionales": Q("dep", **{"in": ["profesional", "ambas"]}),
 "inquilino": Q("viv", eq="alquiler"),
 "inquilino_tensionada": ALL(Q("viv", eq="alquiler"), Q("tens", **{"in": ["si", "ns"]})),
 "busca_vivienda_asequible": Q("viv", **{"in": ["alquiler", "familia"]}),
 "quiere_comprar": Q("comprar", eq=True),
 "tiene_otras_viviendas": Q("otras", gte=1),
 "varias_viviendas": Q("otras", gte=2),
 "gran_tenedor": Q("otras", eq=3),
 "casero": ALL(Q("otras", gte=1), Q("otrasTipo", includes="alquila")),
 "pequeno_casero": ALL(Q("otras", eq=1), Q("otrasTipo", includes="alquila")),
 "vivienda_turistica": Q("otrasTipo", includes="turistica"),
 "patrimonio_mas_1M": Q("patr", gte=3),
 "patrimonio_300k_1M": Q("patr", eq=2),
 "ahorro_mas_300k": Q("ahorro", eq=4),
 "ahorro_alto": Q("ahorro", gte=3),
 "invierte_bolsa": Q("bolsa", eq=True),
 "herencia": Q("herencia", eq=True),
 "espanol": Q("nac", eq="es"),
 "extranjero": Q("nac", **{"in": ["ue", "nue"]}),
 "extracomunitario": Q("nac", eq="nue"),
 "arraigo_corto": ALL(Q("nac", **{"in": ["ue", "nue"]}), Q("arraigo", eq="lt3")),
 "envia_remesas": Q("remesas", eq=True),
 "canarias": Q("region", eq="canarias"),
 "cataluna": Q("region", eq="cataluna"),
 "baleares": Q("region", eq="baleares"),
 "sin_iva": Q("region", **{"in": ["canarias", "ceuta", "melilla"]}),
 "empadronado_10_canarias": Q("empad", eq=True),
 "depende_servicios_publicos": Q("dep_pub", **{"in": ["alta", "media"]}),
 "depende_mucho_servicios": Q("dep_pub", eq="alta"),
}

QUESTIONS = [
 {"id": "region", "texto": "¿En qué comunidad o ciudad autónoma vives?", "opciones": [["andalucia", "Andalucía"], ["aragon", "Aragón"], ["asturias", "Asturias"], ["baleares", "Illes Balears"], ["canarias", "Canarias"], ["cantabria", "Cantabria"], ["castilla_leon", "Castilla y León"], ["castilla_mancha", "Castilla-La Mancha"], ["cataluna", "Cataluña"], ["valencia", "Comunitat Valenciana"], ["extremadura", "Extremadura"], ["galicia", "Galicia"], ["madrid", "Comunidad de Madrid"], ["murcia", "Región de Murcia"], ["navarra", "Navarra"], ["pais_vasco", "País Vasco"], ["rioja", "La Rioja"], ["ceuta", "Ceuta"], ["melilla", "Melilla"]]},
 {"id": "empad", "texto": "¿Llevas 10 años o más empadronado/a en Canarias?", "mostrar_si": R("canarias"), "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "edad", "texto": "¿Qué edad tienes?", "opciones": [["18-25", "18–25"], ["26-35", "26–35"], ["36-40", "36–40"], ["41-64", "41–64"], ["65+", "65 o más"]]},
 {"id": "lab", "texto": "¿Cuál es tu situación laboral principal?", "opciones": [["asal_ind", "Asalariado/a con contrato indefinido"], ["asal_temp", "Asalariado/a temporal o fijo discontinuo"], ["autonomo", "Autónomo/a"], ["empresario", "Empresario/a (sociedad)"], ["parado", "En paro"], ["pension", "Jubilado/a o pensionista"], ["estudiante", "Estudiante"], ["otro", "Otra situación (cuidados, inactividad…)"]]},
 {"id": "emp", "texto": "¿Tienes personas contratadas a tu cargo?", "mostrar_si": Q("lab", **{"in": ["autonomo", "empresario"]}), "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "emprender", "texto": "¿Te planteas darte de alta como autónomo/a en los próximos años?", "mostrar_si": NOT(Q("lab", **{"in": ["autonomo", "empresario", "pension"]})), "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "pensTipo", "texto": "¿Qué tipo de pensión cobras?", "mostrar_si": R("pensionista"), "opciones": [["contrib", "Contributiva (jubilación, viudedad…)"], ["nocontrib", "No contributiva"]]},
 {"id": "ing", "texto": "¿Cuáles son tus ingresos brutos anuales (trabajo, prestación o pensión)?", "ayuda": "Aproximado. El salario mínimo a jornada completa son 17.094 € brutos al año en 2026: si cobras eso o menos, elige el primer tramo.", "opciones": [[1, "Hasta 17.500 €"], [2, "17.500 – 25.000 €"], [3, "25.000 – 40.000 €"], [4, "40.000 – 60.000 €"], [5, "60.000 – 100.000 €"], [6, "Más de 100.000 €"]]},
 {"id": "dep_pub", "texto": "¿Cuánto dependes de los servicios y prestaciones públicas?", "ayuda": "Sanidad y educación públicas, prestaciones (paro, IMV, pensión, ayudas), vivienda pública. Sirve para valorar los efectos indirectos de las medidas sobre la recaudación.", "opciones": [["alta", "Mucho: uso sanidad/educación públicas y cobro (o podría necesitar) prestaciones o ayudas"], ["media", "Algo: uso sanidad o educación públicas, pero no prestaciones"], ["baja", "Poco: uso sobre todo servicios privados"]]},
 {"id": "viv", "texto": "¿Cómo es tu vivienda habitual?", "opciones": [["alquiler", "Vivo de alquiler"], ["hipoteca", "En propiedad, con hipoteca"], ["propio", "En propiedad, sin hipoteca"], ["familia", "Con mi familia o en vivienda cedida"]]},
 {"id": "tens", "texto": "¿Tu vivienda está en una zona declarada «tensionada»?", "ayuda": "Son zonas donde se pueden limitar las rentas del alquiler.", "mostrar_si": R("inquilino"), "opciones": [["si", "Sí"], ["no", "No"], ["ns", "No lo sé"]]},
 {"id": "comprar", "texto": "¿Quieres comprar vivienda (para vivir) en los próximos años?", "mostrar_si": NOT(Q("viv", eq="propio")), "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "otras", "texto": "Además de tu vivienda habitual, ¿cuántas viviendas tienes?", "opciones": [[0, "Ninguna"], [1, "1 o 2"], [2, "De 3 a 9"], [3, "10 o más"]]},
 {"id": "otrasTipo", "multi": True, "texto": "¿Qué haces con ellas?", "ayuda": "Puedes marcar varias.", "mostrar_si": R("tiene_otras_viviendas"), "opciones": [["alquila", "Las alquilo como vivienda habitual"], ["turistica", "Alguna es vivienda turística/vacacional"], ["vacia", "Alguna está vacía o es de uso propio"]]},
 {"id": "hijos", "multi": True, "ninguno": "ninguno", "texto": "¿Tienes hijos/as a tu cargo? ¿De qué edades?", "ayuda": "Puedes marcar varias.", "opciones": [["h0_3", "Menores de 3 años"], ["h3_7", "De 3 a 7 años"], ["h8_17", "De 8 a 17 años"], ["ninguno", "No tengo hijos a cargo"]]},
 {"id": "planHijos", "texto": "¿Piensas tener un hijo/a (o adoptar) en los próximos años?", "mostrar_si": NOT(Q("edad", eq="65+")), "opciones": [[True, "Sí"], ["ns", "No lo sé todavía"], [False, "No"]]},
 {"id": "dep", "texto": "¿Tienes a tu cargo a una persona mayor dependiente?", "ayuda": "Distingue entre cuidarla tú y pagar cuidados profesionales (residencia, ayuda a domicilio, cuidador/a contratado/a): algunas medidas solo cubren lo segundo.", "opciones": [["no", "No"], ["personal", "Sí, la cuido yo (o mi familia)"], ["profesional", "Sí, pago cuidados profesionales"], ["ambas", "Sí, ambas cosas"]]},
 {"id": "patr", "texto": "¿Cuál es tu patrimonio total aproximado (vivienda incluida, menos deudas)?", "opciones": [[1, "Menos de 300.000 €"], [2, "300.000 € – 1 millón"], [3, "1 – 3 millones"], [4, "Más de 3 millones"]]},
 {"id": "ahorro", "texto": "¿Cuánto ingresas al año por rentas del ahorro (intereses, dividendos, plusvalías)?", "opciones": [[1, "Nada o menos de 6.000 €"], [2, "6.000 – 50.000 €"], [3, "50.000 – 300.000 €"], [4, "Más de 300.000 €"]]},
 {"id": "bolsa", "texto": "¿Compras acciones de grandes empresas cotizadas?", "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "herencia", "texto": "¿Esperas recibir o dejar una herencia o donación importante?", "opciones": [[True, "Sí"], [False, "No"]]},
 {"id": "nac", "texto": "¿Cuál es tu nacionalidad?", "ayuda": "Algunas propuestas distinguen por nacionalidad o por arraigo en el acceso a ayudas.", "opciones": [["es", "Española"], ["ue", "De otro país de la UE"], ["nue", "De fuera de la UE"]]},
 {"id": "arraigo", "texto": "¿Cuánto tiempo llevas empadronado/a en España?", "mostrar_si": R("extranjero"), "opciones": [["lt3", "Menos de 3 años"], ["3a10", "Entre 3 y 10 años"], ["gt10", "Más de 10 años"]]},
 {"id": "remesas", "texto": "¿Envías dinero a familiares en otro país?", "mostrar_si": R("extranjero"), "opciones": [[True, "Sí"], [False, "No"]]}, {"id": "genero", "sensible": True, "texto": "¿Cuál es tu género?", "ayuda": "Pregunta opcional. Solo sirve para proponerte temas al final: no cambia ningún resultado, no sale de tu navegador y no aparece en el PDF.", "opciones": [["mujer", "Mujer"], ["hombre", "Hombre"], ["nobinaria", "Persona no binaria"], ["nc", "Prefiero no contestar"]]},
 {"id": "lgtbi", "sensible": True, "texto": "¿Formas parte del colectivo LGTBIQ+?", "ayuda": "Pregunta opcional. Solo sirve para proponerte temas al final: no cambia ningún resultado, no sale de tu navegador y no aparece en el PDF.", "opciones": [["si", "Sí"], ["no", "No"], ["nc", "Prefiero no contestar"]]},
 {"id": "etnia", "sensible": True, "texto": "¿Perteneces a una minoría étnica o eres una persona racializada (por ejemplo, del pueblo gitano)?", "ayuda": "Pregunta opcional. Solo sirve para proponerte temas al final: no cambia ningún resultado, no sale de tu navegador y no aparece en el PDF.", "opciones": [["si", "Sí"], ["no", "No"], ["nc", "Prefiero no contestar"]]},
 {"id": "disc", "sensible": True, "texto": "¿Tienes una discapacidad, o convives con alguien que la tenga?", "ayuda": "Pregunta opcional. Solo sirve para proponerte temas al final: no cambia ningún resultado, no sale de tu navegador y no aparece en el PDF.", "opciones": [["si", "Sí"], ["no", "No"], ["nc", "Prefiero no contestar"]]},
 {"id": "relig", "sensible": True, "texto": "¿Practicas alguna religión?", "ayuda": "Pregunta opcional. Solo sirve para proponerte temas al final: no cambia ningún resultado, no sale de tu navegador y no aparece en el PDF.", "opciones": [["si", "Sí"], ["no", "No"], ["nc", "Prefiero no contestar"]]},
 {"id": "temas", "multi": True, "ninguno": "ninguno", "texto": "¿Sobre qué temas quieres ver también lo que propone cada partido?", "ayuda": "Ya están marcados los que pueden tocarte por tus respuestas; cámbialos como quieras. Se muestran aparte y sin valorar si te favorecen.", "opciones": "TEMAS"},
]
TEMAS_SOC = [
 {"id": "igualdad", "nombre": "Igualdad y violencia contra las mujeres", "sugerir_si": Q("genero", **{"in": ["mujer", "nobinaria"]})},
 {"id": "lgtbi", "nombre": "Derechos LGTBIQ+", "sugerir_si": ANY(Q("lgtbi", eq="si"), Q("genero", eq="nobinaria"))},
 {"id": "racismo", "nombre": "Racismo, discriminación y pueblo gitano", "sugerir_si": Q("etnia", eq="si")},
 {"id": "migracion", "nombre": "Migración, asilo y nacionalidad", "sugerir_si": R("extranjero")},
 {"id": "discapacidad", "nombre": "Discapacidad", "sugerir_si": Q("disc", eq="si")},
 {"id": "familia", "nombre": "Familia, natalidad y conciliación", "sugerir_si": ANY(R("con_hijos"), R("quiere_hijos"))},
 {"id": "educacion", "nombre": "Modelo educativo", "sugerir_si": Q("hijos", includesAny=["h3_7", "h8_17"])},
 {"id": "vida", "nombre": "Aborto y final de la vida", "sugerir_si": None},
 {"id": "religion", "nombre": "Religión y laicidad", "sugerir_si": Q("relig", eq="si")},
 {"id": "rural", "nombre": "Mundo rural y despoblación", "sugerir_si": None},
]
for q in QUESTIONS:
    if q["opciones"] == "TEMAS":
        q["opciones"] = [[t["id"], t["nombre"]] for t in TEMAS_SOC] + [["ninguno", "Ninguno"]]
for q in QUESTIONS:
    q["tipo"] = "multi" if q.pop("multi", False) else "unica"
    q["opciones"] = [{"valor": v, "texto": t} for v, t in q["opciones"]]

SRC = {
 "rankia": ["Rankia: Programas electorales del 29-N, qué propone cada partido en economía", "https://www.rankia.com/blog/opiniones/7550647-programas-electorales-29-n-que-propone-cada-partido-economia", "2026-11-16"],
 "telemadrid": ["Telemadrid: Del alquiler a los impuestos, qué proponen las cinco candidaturas", "https://www.telemadrid.es/elecciones/generales/2026/alquiler-impuestos-candidaturas-propuestas-29n_1_2816509.html", "2026-11-16"],
 "brains": ["Brains RE News: Qué propone cada partido en vivienda (29N)", "https://brainsre.news/que-propone-cada-partido-vivienda-elecciones-29n/", "2026-10"],
 "moncloa_vp": ["Moncloa.com: Vox y PP despliegan sus propuestas económicas para el 29N", "https://www.moncloa.com/2026/10/16/propuestas-economicas-vox-pp-29n-3449552/", "2026-10-16"],
 "queproponen": ["Qué Proponen: PSOE para el 29N", "https://queproponen.es/partidos/psoe", "2026-11"],
 "democrata_pp": ["Demócrata: Programa del PP para el 29N", "https://www.democrata.es/elecciones-generales-espana/programa-electoral-pp-29n-propuestas/", "2026-11-10"],
 "democrata_vox": ["Demócrata: Programa electoral de Vox 2026", "https://www.democrata.es/elecciones-generales-espana/programa-electoral-vox-2026-propuestas-pdf/", "2026-11-13"],
 "vox_web": ["Vox: «Es sentido común», medidas para el 29N (web del partido)", "https://www.voxespana.es/abascal/es-sentido-comun-estas-son-las-medidas-de-vox-para-el-29n-20261112", "2026-11-12"],
 "pe_vox": ["Política Electoral: Programa de Vox 2026 (costes estimados del IRPF)", "https://www.politicaelectoral.com/es/espana/generales-2026/nacional/vox", "2026-10"],
 "vox_coste": ["101TV: Vox cifra en 120.000 millones el coste de su plan fiscal", "https://101tvsevilla.es/vox-cifra-en-120-000-millones-el-coste-de-su-plan-fiscal-y-propone-financiarlo-con-recortes/", "2026-11-06"],
 "democrata_fa": ["Demócrata: El Frente Amplio promete expropiar viviendas a fondos y gravar grandes fortunas", "https://www.democrata.es/actualidad/frente-amplio-promete-expropiar-viviendas-fondos-buitre-elevar-impuestos-grandes-fortunas/", "2026-11"],
 "marcos_fa": ["Blog Marcos Ramírez: Programa del Frente Amplio en el 29N (recopilación de anuncios)", "https://blog.marcosramirez.info/programa-electoral-frente-amplio-29n/", "2026-11-15"],
 "democrata_pod": ["Demócrata: Qué propone Irene Montero", "https://www.democrata.es/politica/propone-irene-montero-con-quien-quiere-presentarse-claves-su-candidatura/", "2026-10"],
 "pe_cc": ["Política Electoral: Programa de Coalición Canaria 2026", "https://www.politicaelectoral.com/es/espana/generales-2026/nacional/cc", "2026-10"],
 "eldiario_cc": ["Canarias Ahora: CC y Primero Canarias presentan su programa", "https://www.eldiario.es/canariasahora/politica/cc-canarias-presenta-programa-electoral-29n_1_13650673.html", "2026-11-09"],
 "ara_prioridad": ["Ara: El PP llevará al Congreso la «prioridad nacional» basada en el arraigo", "https://es.ara.cat/politica/pp-lleva-congreso-prioridad-nacional-recibir-ayudas-pactada-vox_1_5714383.html", "2026-04"],
 "airef_ajuste": ["Vozpópuli: La AIReF recomienda medidas por el 0,6 % del PIB", "https://www.vozpopuli.com/economia/sanchez-endosara-a-feijoo-un-ajuste-milmillonario-en-los-primeros-meses-de-legislatura.html", "2026"],
 "esade_alq": ["EsadeEcPol: Los efectos de la limitación de precios de los alquileres en Cataluña", "https://www.esade.edu/ecpol/es/publicaciones/los-efectos-de-la-limitacion-de-precios-de-los-alquileres-en-cataluna/", "2023-02-09"],
 "iec_alq": ["Revista Catalana d'Administració Pública: Los efectos de la regulación de precios del alquiler (Arcarazo y Palomera)", "https://revistes.iec.cat/index.php/RCAP/article/download/156571/153999/188763", "2025-12"],
 "funcas_viv": ["Funcas: Evidencia comparada sobre políticas de vivienda", "https://www.funcas.es/descargar/229323/", "2026"],
 "bde_smi": ["Banco de España: Los efectos del SMI en el empleo, nueva evidencia para España (2021)", "https://ideas.repec.org/p/bde/opaper/2113.html", "2021"],
 "ocde_smi": ["Crónica Económica: resumen de evaluaciones del SMI (cita estudio de la OCDE)", "https://cronicaeconomica.com/?p=23731", "2024"],
 "esade_iva": ["Forbes: La mitad del ahorro de la rebaja del IVA de alimentos fue a las rentas más altas (EsadeEcPol)", "https://forbes.es/?p=256357", "2023"],
 "iva_coste": ["El Observador: Cómo impacta en Hacienda la rebaja del IVA de alimentos", "https://www.elobservador.com.uy/espana/como-impacta-en-hacienda-la-rebaja-del-iva-de-alimentos-2023115102439", "2023-11-05"],
 "bbva_jornada": ["Vozpópuli: BBVA Research alerta del impacto de la reducción de jornada", "https://www.vozpopuli.com/economia/macroeconomia/bbva-research-alerta-reduccion-jornada-laboral-restara-6-decimas-pib-8-empleo.html", "2024"],
 "fedea_jornada": ["Vozpópuli: Fedea advierte de efectos de reducir la jornada por ley", "https://www.vozpopuli.com/economia/fedea-reducir-jornada-aumentara-horas-extra-contratos-pocas-horas-fraude.html", "2024"],
 "salto_jornada": ["El Salto (opinión): la reducción de jornada costará poco y traerá crecimiento", "https://www.elsaltodiario.com/reduccion-jornada/laboral-375-horas-semanales-costara-poco-empresas-sera-fuente-bienestar-crecimiento", "2025"],
 "democrata_listas": ["Demócrata: La izquierda alternativa solo logra listas unitarias en Baleares y la Comunidad Valenciana tras registrar sus candidaturas", "https://www.democrata.es/en/current-events/the-alternative-left-only-achieves-unitary-lists-in-baleares-and-comunidad-valenciana-after-registering-its-candidacies/", "2026-11-02"],
 "manifiesto_upc": ["Unidad del Pueblo Canario: Manifiesto electoral (PDF)", "https://github.com/dvalverderios92/test-29n/blob/main/programas/manifiesto-upc.pdf", "2026-11"],
 "upc": ["Diario de Avisos: NC-BC, Podemos, IUC y Movimiento Sumar concurrirán como Unidad del Pueblo Canario", "https://diariodeavisos.elespanol.com/2026/10/29n-unidad-del-pueblo-canario/", "2026-10"],
 "diari_fa": ["Diari de Tarragona: Frente Amplio y Podemos concurrirán por separado salvo acuerdos territoriales", "https://www.diaridetarragona.com/espana/273314/frente-amplio-concurriran-separado-catalunya-madrid.html", "2026-11"],
 "eldiario_fa": ["elDiario.es: el mapa de candidaturas de la izquierda por comunidades", "https://www.eldiario.es/1_cf5cc6", "2026-11"],
 "cnmc_suelo": ["CNMC: Estudio sobre la transformación urbanística del suelo para vivienda", "https://www.cnmc.es/sites/default/files/6658260.pdf", "2025"],
}
SRC.update({
 "pod_ue24": ["Podemos: Programa de las elecciones europeas 2024", "https://podemos.info/programa-podemos-elecciones-europeas-2024", "2024-05"],
 "ara_feijoo": ["Ara: Feijóo promete reabrir el debate del aborto y reformar la ley de eutanasia", "https://es.ara.cat/politica/elecciones-generales/feijoo-promete-reabrir-debate-aborto-reformar-ley-eutanasia_1_5887953.html", "2026-10-23"],
 "que_feijoo": ["Qué!: Feijóo promete revisar el aborto, integrar Igualdad y atar el SMI al acuerdo con la patronal", "https://que.es/2026/10/23/feijoo-aborto-igualdad-smi", "2026-10-23"],
 "que_voxdesreg": ["Qué!: Vox propone una derogación masiva de leyes: reforma laboral, igualdad y vivienda", "https://www.que.es/2026/06/28/vox-derogacion-masiva-leyes/", "2026-06-28"],
 "debate_vox23": ["El Debate: Vox promete derogar las leyes del aborto y la eutanasia (programa del 23J)", "https://www.eldebate.com/sociedad/20230708/vox-apuesta-vida-promete-derogar-leyes-aborto-eutanasia_126854.html", "2023-07-08"],
 "aci_psoe19": ["ACI Prensa: El PSOE incluye en su programa denunciar los acuerdos con la Santa Sede (elecciones de noviembre de 2019)", "https://www.aciprensa.com/noticias/psoe-amenaza-con-denunciar-acuerdos-entre-santa-sede-y-espana-27988", "2019-10"],
 "democrata_erc": ["Demócrata: ERC lleva el referéndum de autodeterminación al 29N y exige la financiación singular y el traspaso de Rodalies", "https://www.democrata.es/elecciones-generales-espana/programa-electoral-erc-29n-referendum/", "2026-11-05"],
 "nacio_erc_disc": ["Nació Digital: ERC vol augmentar les pensions per discapacitat almenys fins al 80 % del salari mínim", "https://naciodigital.cat/politica/erc-vol-augmentar-les-pensions-per-discapacitat-almenys-fins-al-80-del-salari-minim.html", "2025-04-17"],
 "salto_aborto": ["El Salto: El Congreso rechaza las enmiendas a la totalidad de PP y Vox a incluir el aborto en la Constitución", "https://www.elsaltodiario.com/derechos-reproductivos/congreso-rechaza-enmiendas-totalidad-pp-vox-incluir-aborto-constitucion", "2026-04-30"],
 "maldita_psoe21": ["Maldita: El PSOE y la Iglesia católica: Concordato, laicidad e inmatriculaciones", "https://maldita.es/malditahemeroteca/20210726/psoe-iglesia-catolica-religion-vaticano", "2021-07-26"],
})
PDFS = {"pp": ("pp.pdf", "PP: La Reconstrucción Nacional"), "psoe": ("psoe.pdf", "PSOE: La fuerza de seguir avanzando"), "vox": ("vox.pdf", "Vox: Es sentido común"), "fa": ("frente-amplio.pdf", "Frente Amplio: Programa electoral 2026"), "cc": ("coalicion-canaria.pdf", "Coalición Canaria: Defiende Canarias"), "erc": ("erc.pdf", "ERC: Pel país. Per la gent. Pel futur (programa al Congrés 2026, en catalán)")}
for k, (f, t) in PDFS.items():
    SRC["pdf_" + k] = [t + " (programa oficial, PDF)", "https://dvalverderios92.github.io/test-29n/programas/" + f, "2026-11"]
SOURCES = {k: {"titulo": v[0], "url": v[1], "fecha": v[2]} for k, v in SRC.items()}

# ---------- Efectos indirectos (riesgos) ----------
RISKS = [
 {"id": "rebaja_sin_financiar", "titulo": "Rebajas de impuestos sin coste ni financiación cuantificados",
  "evidencia": "hecho+inferencia",
  "que_pasa": "Menos recaudación. La AIReF ya pide un ajuste en torno al 0,6 % del PIB (unos 10.000 millones), y una rebaja sin financiar lo agranda. Ese ajuste puede salir de recortes de gasto, más deuda u otros impuestos. Ningún programa dice de cuál.",
  "fuentes": ["airef_ajuste", "rankia", "democrata_pp", "democrata_vox"],
  "exposicion": [
   {"si": R("depende_mucho_servicios"), "nivel": "alta", "texto": "Si el ajuste recae en el gasto, te afecta más porque dependes de servicios y prestaciones públicas."},
   {"si": R("depende_servicios_publicos"), "nivel": "media", "texto": "Usas servicios públicos: un recorte de gasto te llegaría en parte."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Dependes poco de servicios públicos, pero un mayor déficit o deuda afecta a toda la economía."}]},
 {"id": "gasto_sin_financiar", "titulo": "Nuevo gasto sin coste ni financiación cuantificados (o con cifras solo del propio partido)",
  "evidencia": "hecho+inferencia",
  "que_pasa": "Más gasto sin una fuente de ingresos verificada. Puede acabar en más deuda, en subidas de impuestos más amplias de lo anunciado, en recortes de otras partidas o en que la medida no llegue a aplicarse completa.",
  "fuentes": ["airef_ajuste", "rankia", "marcos_fa"],
  "exposicion": [
   {"si": ANY(R("renta_alta"), R("patrimonio_mas_1M")), "nivel": "alta", "texto": "Con tus ingresos o patrimonio, eres de quienes más probablemente pagarían la factura si se suben impuestos más allá de lo anunciado."},
   {"si": Q("ing", gte=3), "nivel": "media", "texto": "Con tus ingresos, podrías acabar pagando parte de la factura si se suben impuestos más allá de lo anunciado."},
   {"si": R("depende_servicios_publicos"), "nivel": "media", "texto": "Si no se financia, la medida que te beneficia podría retrasarse o recortarse, o salir de otras partidas que también usas."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Un mayor déficit o deuda afecta a toda la economía."}]},
 {"id": "ayuda_demanda_precio", "titulo": "Ayudas a la compra o al alquiler que pueden trasladarse al precio",
  "evidencia": "consenso",
  "que_pasa": "Funcas resume la evidencia comparada así: los subsidios a la demanda se capitalizan en los precios cuando la oferta no puede crecer deprisa. Parte de la ayuda puede acabar en manos del vendedor o del casero.",
  "fuentes": ["funcas_viv"],
  "exposicion": [
   {"si": ANY(R("quiere_comprar"), R("inquilino")), "nivel": "media", "texto": "El ahorro real para ti puede ser menor que el anunciado si los precios suben."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta sobre todo a quien compra o alquila."}]},
 {"id": "tope_alquiler_oferta", "titulo": "Topes, congelaciones o prórrogas de alquiler: efecto sobre la oferta",
  "evidencia": "disputada",
  "que_pasa": "Evidencia disputada. EsadeEcPol estudió el control de rentas catalán de 2020. Halló unos precios medios un 5 % más bajos, concentrados en los pisos caros, pero un 10 % menos de contratos firmados, y los pisos más baratos subieron hacia el índice. Otro análisis (Arcarazo y Palomera, 2025) concluye que una regulación bien diseñada y aplicada es eficaz.",
  "fuentes": ["esade_alq", "iec_alq"],
  "exposicion": [
   {"si": R("inquilino"), "nivel": "media", "texto": "Si mantienes tu contrato, te protege. Si tienes que buscar otro piso, podrías encontrar menos oferta."},
   {"si": R("busca_vivienda_asequible"), "nivel": "media", "texto": "Si vas a buscar alquiler, la oferta disponible podría ser menor (efecto en discusión)."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta sobre todo a quien busca alquiler."}]},
 {"id": "fin_topes_alquiler", "titulo": "Eliminar topes y zonas tensionadas: efecto sobre las rentas",
  "evidencia": "disputada",
  "que_pasa": "Los partidos que lo proponen sostienen que más oferta y seguridad jurídica bajarán los precios, pero es una previsión. El mismo estudio de EsadeEcPol encontró que el tope sí rebajó las rentas de los pisos caros. Quitarlo puede encarecer las renovaciones en zonas tensionadas.",
  "fuentes": ["esade_alq", "cnmc_suelo"],
  "exposicion": [
   {"si": R("inquilino_tensionada"), "nivel": "alta", "texto": "Al renovar o cambiar de piso podrías afrontar subidas que hoy están limitadas."},
   {"si": R("inquilino"), "nivel": "baja", "texto": "Fuera de zonas tensionadas, el efecto directo es pequeño."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta sobre todo a inquilinos en zonas tensionadas."}]},
 {"id": "smi_empleo", "titulo": "Subidas del salario mínimo: efecto sobre el empleo",
  "evidencia": "disputada",
  "que_pasa": "Para la subida del 22 % de 2019, la OCDE estimó un +5,8 % de renta para los afectados y un −0,6 % de empleo. El Banco de España halló efectos más negativos en horas trabajadas y en la contratación de jóvenes. Subidas mucho mayores (por ejemplo, a 1.800 €) quedan fuera de lo estudiado, así que su efecto es más incierto.",
  "fuentes": ["ocde_smi", "bde_smi"],
  "exposicion": [
   {"si": ANY(R("parado"), ALL(R("joven_18_35"), R("renta_baja"))), "nivel": "media", "texto": "Si buscas empleo de salario bajo, podría haber algo menos de contratación (efecto pequeño en subidas moderadas, incierto en grandes)."},
   {"si": R("empleador"), "nivel": "media", "texto": "Más coste laboral si tienes plantilla en salarios bajos."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Efecto general pequeño según las evaluaciones disponibles."}]},
 {"id": "jornada_ley", "titulo": "Reducción de jornada por ley sin bajar el sueldo",
  "evidencia": "disputada",
  "que_pasa": "BBVA Research y Fedea advierten de más costes y posibles efectos sobre el empleo y la actividad, sobre todo en pymes. Otros economistas sostienen que mejorará la productividad y el crecimiento. Cuanto mayor sea la reducción (35, 32 o 30 horas), más incierto es el efecto.",
  "fuentes": ["bbva_jornada", "fedea_jornada", "salto_jornada"],
  "exposicion": [
   {"si": R("empleador"), "nivel": "alta", "texto": "Subiría tu coste por hora de trabajo."},
   {"si": R("parado"), "nivel": "media", "texto": "Si encarece la contratación, podría ser algo más difícil encontrar empleo."},
   {"si": R("asalariado"), "nivel": "baja", "texto": "Te beneficia directamente; el riesgo es que tu empresa ajuste por otra vía (horas extra, contratación)."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta sobre todo a asalariados y empresas."}]},
 {"id": "iva_poco_focalizado", "titulo": "Rebajas de IVA en alimentos: poco focalizadas",
  "evidencia": "consenso",
  "que_pasa": "La rebaja de 2023 se trasladó a los precios casi entera (más del 90 % según EsadeEcPol), pero cinco de cada diez euros dejados de recaudar fueron al 40 % de hogares con más renta. Solo de enero a septiembre de 2023 costó 1.294 millones.",
  "fuentes": ["esade_iva", "iva_coste"],
  "exposicion": [
   {"si": R("sin_iva"), "nivel": "baja", "texto": "En tu territorio no se aplica el IVA, pero sí soportas el coste en la recaudación estatal."},
   {"si": ALL(R("renta_baja"), R("depende_servicios_publicos")), "nivel": "media", "texto": "Tu ahorro sería pequeño en euros frente a su coste, que compite con el gasto en servicios que usas."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Ahorro real pero repartido de forma poco progresiva."}]},
 {"id": "irpf_reparto", "titulo": "Rebaja amplia del IRPF: reparto y coste muy inciertos",
  "evidencia": "hecho",
  "que_pasa": "Vox no da tipos en el programa. Las estimaciones de coste de su modelo de 2025 van de 46.000 millones (Vox) a 85.000 millones (Ministerio de Hacienda). Un análisis citado por Moncloa.com estima que quien cobra el SMI no notaría diferencia y que un contribuyente con un millón de euros ahorraría más de 200.000 €.",
  "fuentes": ["pe_vox", "moncloa_vp", "vox_coste"],
  "exposicion": [
   {"si": ALL(R("renta_baja"), R("depende_servicios_publicos")), "nivel": "alta", "texto": "Ganarías poco en IRPF y dependes de servicios que tendrían que absorber un coste muy grande."},
   {"si": R("renta_baja"), "nivel": "media", "texto": "Ganarías poco en IRPF frente al coste total."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Ganarías más en IRPF; el riesgo está en cómo se cubre el coste."}]},
 {"id": "prioridad_legal", "titulo": "Prioridad nacional o por arraigo en ayudas: alcance jurídico incierto",
  "evidencia": "hecho",
  "que_pasa": "Vox la plantea por nacionalidad. El PP, por arraigo (empadronamiento y cotizaciones), «dentro de la legalidad vigente», sin umbrales publicados. Una propuesta de Vox se rechazó en el Congreso en junio de 2026 con el voto del PP. El alcance real dependería de cómo se legisle y de los tribunales.",
  "fuentes": ["vox_web", "democrata_pp", "ara_prioridad", "brains"],
  "exposicion": [
   {"si": R("extranjero"), "nivel": "alta", "texto": "Te afectaría directamente en el acceso a ayudas y servicios."},
   {"si": ALWAYS, "nivel": "baja", "texto": "No te afecta directamente."}]},
 {"id": "expropiacion_plazos", "titulo": "Expropiaciones de vivienda: coste y plazos inciertos",
  "evidencia": "inferencia",
  "que_pasa": "La Constitución (art. 33.3) exige indemnización en toda expropiación, así que tiene coste público, y es previsible que se recurra en los tribunales. No hemos encontrado una estimación independiente de coste ni de plazos. El beneficio para inquilinos llegaría, en su caso, a medio plazo.",
  "fuentes": ["democrata_fa", "democrata_pod"],
  "exposicion": [
   {"si": R("busca_vivienda_asequible"), "nivel": "media", "texto": "La vivienda pública que podría beneficiarte tardaría en llegar y su coste no está calculado."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta sobre todo a grandes propietarios y a las cuentas públicas."}]},
 {"id": "pensiones_transicion", "titulo": "Cambio a un sistema de pensiones mixto con capitalización",
  "evidencia": "inferencia",
  "que_pasa": "Vox no publica la fórmula ni la financiación. Inferencia: si parte de las cotizaciones se desvía a cuentas de capitalización, durante la transición hay que seguir pagando las pensiones actuales con menos ingresos. Ese hueco habría que cubrirlo con impuestos, deuda o ajustes en las prestaciones.",
  "fuentes": ["moncloa_vp", "rankia"],
  "exposicion": [
   {"si": R("pensionista"), "nivel": "media", "texto": "Perderías la garantía de subida con el IPC sin conocer la fórmula que la sustituye."},
   {"si": ALL(R("trabaja"), R("menor_40")), "nivel": "media", "texto": "Parte de tu futura pensión dependería de mercados financieros, con reglas aún desconocidas."},
   {"si": ALWAYS, "nivel": "baja", "texto": "Afecta a las cuentas de la Seguridad Social en la transición."}]},
]

# ---------- Partidos ----------
PARTIES = [
 {"id": "cc", "nombre": "Coalición Canaria", "ambito_si": R("canarias"),
  "programa": {"titulo": "Defiende Canarias", "fecha": "2026-11-09", "estado": "publicado", "nota": "10 causas y 100 acciones. Solo se presenta en Canarias."},
  "financiacion": {"cuantifica": "no", "resumen": "En las fuentes consultadas no aparece coste ni financiación. Buena parte de sus medidas reclama financiación al Estado.", "fuentes": ["pe_cc", "eldiario_cc"]}},
 {"id": "erc", "nombre": "ERC", "ambito_si": ANY(R("cataluna"), R("baleares")),
  "programa": {"titulo": "Pel país. Per la gent. Pel futur.", "fecha": "2026-11-05", "estado": "publicado", "nota": "Programa en catalán, pensado para Cataluña. Lista propia solo en Cataluña, donde lleva candidatos independientes de Podemos; en Baleares concurre dentro de Ara Més-Front Ampli."},
  "financiacion": {"cuantifica": "no", "resumen": "No cuantifica el coste total ni lo que recaudarían sus subidas de impuestos. Da algunas cifras de gasto (vivienda, al menos el 1,5 % del PIB; educación, el 6 % del PIB; prestación por crianza desde 200 € por familia) y señala como fuentes la tributación de grandes fortunas, banca y energéticas y de las rentas del capital.", "fuentes": ["pdf_erc", "democrata_erc"]}},
 {"id": "fa", "nombre": "Frente Amplio",
  "programa": {"titulo": "Programa electoral 2026", "fecha": None, "estado": "publicado", "nota": "Programa publicado en noviembre. Las cifras de coste son de campaña."},
  "financiacion": {"cuantifica": "cifras_propias", "resumen": "Da cifras propias sin verificación independiente: unos 20.000 M€/año en pensiones, financiados con un impuesto del 2 % a patrimonios de más de 1 M€, la subida del tope de cotización (7.000–8.500 M€) y la tributación mínima de grandes empresas. Estima más de 10.000 M€ con el impuesto a fortunas.", "fuentes": ["marcos_fa", "democrata_fa"]}},
 {"id": "pod", "nombre": "Podemos",
  "programa": {"titulo": "Paz, casa y trabajo (lema)", "fecha": None, "estado": "sin_programa", "nota": "Sin programa publicado a 16-nov-2026: anuncios de campaña y posiciones previas."},
  "financiacion": {"cuantifica": "no", "resumen": "En las fuentes consultadas no aparece coste ni financiación de sus medidas.", "fuentes": ["democrata_pod", "telemadrid"]}},
 {"id": "pp", "nombre": "PP",
  "programa": {"titulo": "La Reconstrucción Nacional", "fecha": "2026-11-10", "estado": "publicado", "nota": "249 medidas."},
  "financiacion": {"cuantifica": "no", "resumen": "No incluye memoria económica (Rankia ve financiación parcial en algunas medidas). Remite a una auditoría del gasto en los primeros 100 días y promete reducir déficit y deuda sin precisar ajustes. Las únicas cifras son de inversión: más de 300.000 M€ en infraestructuras en 15 años y 40.000 M€ en agua.", "fuentes": ["democrata_pp", "rankia"]}},
 {"id": "psoe", "nombre": "PSOE",
  "programa": {"titulo": "La fuerza de seguir avanzando", "fecha": "2026-11-15", "estado": "publicado", "nota": "Más de 370 compromisos."},
  "financiacion": {"cuantifica": "no", "resumen": "No cuantifica el coste total ni lo que recaudarían los nuevos impuestos. Señala como fuentes los grandes patrimonios, las rentas del capital, las tecnológicas, las transacciones financieras y la lucha contra el fraude.", "fuentes": ["rankia"]}},
 {"id": "vox", "nombre": "Vox",
  "programa": {"titulo": "Es sentido común", "fecha": "2026-11-12", "estado": "publicado", "nota": "115 medidas."},
  "financiacion": {"cuantifica": "fuera_del_programa", "resumen": "El programa no cuantifica costes ni tipos. Su portavoz económico cifra el paquete fiscal en unos 120.000 M€, a cubrir con recortes de subvenciones y gasto autonómico. Para su IRPF de 2025, Hacienda estima 85.000 M€ frente a los 46.000 M€ de Vox.", "fuentes": ["democrata_vox", "vox_coste", "pe_vox"]}},
]

def M(id, p, tema, texto, num, origen, fuentes, efectos, riesgos=(), universal=False):
    d = {"id": id, "partido": p, "tema": tema, "texto": texto, "num": num, "origen": origen, "fuentes": list(fuentes), "riesgos": list(riesgos)}
    if universal: d["universal"] = True; d["efectos"] = []
    else: d["efectos"] = [{"si": s, "valor": v, "texto": t} for s, v, t in efectos]
    return d

IGIC = "En tu territorio no se aplica el IVA (Canarias: IGIC; Ceuta y Melilla: IPSI), así que no te afectaría directamente."
CASERO_GANA = "Como casero/a, desaparecerían los límites a la renta que puedes pedir."
MEAS = [
# ===== PP =====
M("pp-177", "pp", "IRPF", "Exención de IRPF por ley para quien cobre el salario mínimo; el umbral sube con el SMI.", "177", "programa", ["rankia", "democrata_pp"],
  [(ALL(R("trabaja"), R("renta_smi")), 1, "Con ingresos en torno al SMI no pagarías IRPF (o se garantizaría por ley la exención si ya la tienes).")], ["rebaja_sin_financiar"]),
M("pp-178", "pp", "IRPF", "Actualizar la tarifa del IRPF con la inflación.", "178", "programa", ["rankia"],
  [(R("paga_irpf"), 1, "Evita pagar más IRPF solo porque tu sueldo o pensión suba con los precios.")], ["rebaja_sin_financiar"]),
M("pp-179", "pp", "IRPF", "Rebaja del IRPF a jóvenes de 18 a 35 años: 100 % el primer año, 75 % el segundo, 50 % el tercero y 25 % el cuarto.", "179", "programa", ["rankia", "democrata_pp"],
  [(ALL(R("joven_18_35"), ANY(R("trabaja"), R("estudiante"), R("parado"), R("quiere_emprender"))), 1, "Por tu edad, pagarías mucho menos IRPF durante cuatro ejercicios al trabajar.")], ["rebaja_sin_financiar"]),
M("pp-180", "pp", "IVA", "IVA del 0 % en alimentos básicos (incluidos carne, pescado y conservas) mientras dure la crisis de inflación.", "180", "programa", ["rankia"],
  [(R("sin_iva"), 0, IGIC), (ALWAYS, 1, "Abarataría tu cesta de la compra.")], ["iva_poco_focalizado", "rebaja_sin_financiar"]),
M("pp-181", "pp", "Empresa", "Deducción íntegra en Sociedades, el mismo año, de inversiones en maquinaria, digitalización, IA, software o patentes.", "181", "programa", ["rankia"],
  [(R("empresario"), 1, "Tu sociedad pagaría menos impuestos el año que invierta.")], ["rebaja_sin_financiar"]),
M("pp-170", "pp", "Autónomos", "Sin cuota a la Seguridad Social el primer año como autónomo, ni el segundo si no se alcanza el SMI; bonificación del 100 % de la cotización del primer trabajador contratado durante un año.", "170-171", "programa", ["rankia", "democrata_pp"],
  [(R("quiere_emprender"), 1, "Si te das de alta, te ahorrarías la cuota al empezar."),
   (ALL(R("autonomo"), NOT(R("empleador"))), 1, "Si contratas a tu primer trabajador, no pagarías su cotización (la cuota cero es para nuevas altas).")], ["rebaja_sin_financiar"]),
M("pp-171", "pp", "Autónomos", "Sin obligación de cobrar ni declarar IVA si se factura menos de 85.000 € al año.", "171", "programa", ["rankia"],
  [(ALL(ANY(R("autonomo_o_futuro"), R("empresario")), R("sin_iva")), 0, IGIC),
   (ANY(R("autonomo_o_futuro"), R("empresario")), 1, "Menos papeleo y, si vendes a particulares, precios más competitivos.")], ["rebaja_sin_financiar"]),
M("pp-145", "pp", "Vivienda", "Derogar la Ley de Vivienda, incluidas las zonas tensionadas y el índice de precios del alquiler; un millón de viviendas con licencias en tres meses y silencio positivo.", "144-145", "programa", ["rankia", "democrata_pp"],
  [(R("casero"), 1, CASERO_GANA),
   (R("inquilino_tensionada"), -1, "Perderías el tope de renta que da la zona tensionada."),
   (R("inquilino"), 0, "Fuera de zona tensionada, el efecto directo es pequeño; el indirecto depende de la oferta."),
   (R("quiere_comprar"), 0, "Si se construye más, podría moderar precios a medio plazo (previsión, no efecto directo).")], ["fin_topes_alquiler"]),
M("pp-153", "pp", "Vivienda", "Menores de 40 años: IVA del 4 % en la primera vivienda, aval público de hasta el 20 % y «Hucha Hogar Joven» (hasta 2.000 €/año con deducción del 20 %).", "153-155", "programa", ["rankia", "democrata_pp"],
  [(ALL(R("menor_40"), R("quiere_comprar"), R("sin_iva")), 1, "Te ayudarían el aval y la hucha; la rebaja de IVA no te aplica (IGIC/IPSI)."),
   (ALL(R("menor_40"), R("quiere_comprar")), 1, "Te ayudaría con la entrada y la hipoteca.")], ["ayuda_demanda_precio", "rebaja_sin_financiar"]),
M("pp-156a", "pp", "Vivienda", "Deducción en el IRPF para inquilinos.", "156", "programa", ["rankia"],
  [(R("inquilino"), 1, "Recuperarías parte de lo que pagas de alquiler (importe no detallado).")], ["ayuda_demanda_precio", "rebaja_sin_financiar"]),
M("pp-156b", "pp", "Vivienda", "«Tres años+»: ventaja fiscal a caseros que renueven tres años con subidas por debajo del IPC.", "156", "programa", ["rankia", "democrata_pp"],
  [(R("casero"), 1, "Pagarías menos impuestos si mantienes la renta contenida.")], ["rebaja_sin_financiar"]),
M("pp-okupa", "pp", "Vivienda", "Ley para que el propietario recupere en 48 horas su vivienda ocupada; no pagaría suministros ni impuestos mientras dure la ocupación.", "157", "programa", ["brains", "democrata_pp"],
  [(R("tiene_otras_viviendas"), 1, "Más protección para tus viviendas, sobre todo si alguna está vacía.")]),
M("pp-arraigo", "pp", "Ayudas", "Prioridad en determinadas ayudas y prestaciones para quien tenga un arraigo real con España (empadronamiento, cotización, permanencia), no basada solo en la nacionalidad. Sin umbrales publicados.", "98", "programa", ["democrata_pp", "ara_prioridad"],
  [(R("arraigo_corto"), -1, "Con poco tiempo empadronado/a, podrías quedar por detrás o fuera de algunas ayudas."),
   (R("extranjero"), 0, "Con varios años de residencia y cotización probablemente no te afecte; depende de los umbrales.")], ["prioridad_legal"]),
M("pp-108", "pp", "Pensiones", "Revalorización anual de las pensiones con el IPC.", "108", "programa", ["rankia"],
  [(R("pensionista"), 1, "Mantiene el criterio actual (ya fijado por ley): tu pensión sube con los precios.")]),
M("pp-114", "pp", "Dependencia", "Deducción del 40 % de lo que se pague por atención profesional a un mayor dependiente; Pacto de Estado por la Dependencia con el 50 % de aportación estatal.", "114", "programa", ["rankia", "democrata_pp"],
  [(R("paga_cuidados_profesionales"), 1, "Recuperarías el 40 % de lo que pagas en cuidados profesionales y aumentaría la financiación estatal de la dependencia."),
   (R("cuida_dependiente"), 0, "La deducción solo cubre el gasto en cuidados profesionales, no el cuidado familiar; el aumento de la aportación estatal sí podría mejorar las prestaciones de dependencia.")], ["rebaja_sin_financiar", "gasto_sin_financiar"]),
M("pp-163", "pp", "Familia", "Escuela infantil de 0 a 3 años gratuita al final de la legislatura.", "163", "programa", ["rankia"],
  [(ANY(R("hijos_0_3"), R("quiere_hijos")), 1, "Te ahorrarías la escuela infantil (llegaría al final de la legislatura).")], ["gasto_sin_financiar"]),
M("pp-familia", "pp", "Familia", "Deducción familiar única, reembolsable y de abono mensual, que incluiría al concebido no nacido.", "158-159", "programa", ["democrata_pp"],
  [(ANY(R("con_hijos"), R("quiere_hijos")), 1, "Cobrarías una deducción mensual por tus hijos aunque no pagues IRPF suficiente (importe no detallado).")], ["rebaja_sin_financiar"]),
M("pp-horas", "pp", "Empleo", "Elevar el límite de horas extra.", None, "campaña", ["moncloa_vp"],
  [(R("asalariado"), 0, "Puede darte más ingresos, pero también jornadas más largas: depende de tu caso."),
   (R("empleador"), 1, "Más flexibilidad para cubrir picos de trabajo.")]),
M("pp-mutuas", "pp", "Empleo", "Reforzar el papel de las mutuas en la gestión de las bajas (incapacidad temporal) y premiar a las empresas que mejor la gestionen; hasta el 100 % de la base reguladora en enfermedades graves y largas.", "175", "programa", ["moncloa_vp"],
  [(R("asalariado"), 0, "Si enfermas de gravedad cobrarías más; en bajas comunes, las mutuas ganarían peso en su gestión (sin detalle de cómo)."),
   (R("empleador"), 1, "Bajas posiblemente más cortas en tu plantilla.")]),
M("pp-220", "pp", "Sanidad", "Al menos 4.500 médicos más en Atención Primaria y Plan Nacional de Salud Mental 2027-2037.", "220, 223", "programa", ["rankia", "telemadrid"], [], ["gasto_sin_financiar"], universal=True),
M("pp-infra", "pp", "Inversión", "Más de 300.000 M€ en infraestructuras en 15 años (con capital privado) y hasta 40.000 M€ en agua hasta 2030.", "117, 126", "programa", ["rankia"], [], ["gasto_sin_financiar"], universal=True),
M("pp-228", "pp", "Energía", "Eliminar el calendario de cierre nuclear y el impuesto del 7 % sobre la producción eléctrica.", "228-229", "programa", ["rankia"], [], ["rebaja_sin_financiar"], universal=True),

# ===== PSOE =====
M("psoe-130", "psoe", "Ahorro", "Subir hasta el 35 % el tipo de las rentas del capital superiores a 300.000 €.", "130", "programa", ["rankia"],
  [(R("ahorro_mas_300k"), -1, "Pagarías más por tus rentas del ahorro.")]),
M("psoe-134", "psoe", "Familia", "Convertir el mínimo por hijo del IRPF en un crédito reembolsable (unos 2 millones de hogares).", "134", "programa", ["rankia"],
  [(ALL(R("con_hijos"), R("renta_baja")), 1, "Con tu renta, cobrarías la parte del mínimo por hijos que hoy no puedes aprovechar."),
   (R("con_hijos"), 0, "Con tu renta seguramente ya aprovechas el mínimo entero: poco cambio.")], ["gasto_sin_financiar"]),
M("psoe-88", "psoe", "IRPF", "Deducción estatal en el IRPF que se activaría cuando suban los precios.", "88", "programa", ["rankia"],
  [(R("paga_irpf"), 1, "Te compensaría parte de la inflación (umbrales e importes no publicados).")], ["rebaja_sin_financiar"]),
M("psoe-135", "psoe", "Ahorro", "Impuesto sobre transacciones financieras del 0,2 % al 0,4 % en cotizadas de más de 1.000 millones; más impuestos a tecnológicas, viajes de lujo y cotizadas con sueldos de directivos muy altos.", "131-135", "programa", ["rankia"],
  [(R("invierte_bolsa"), -1, "Cada compra de acciones de esas empresas te costaría un poco más.")]),
M("psoe-127", "psoe", "Patrimonio", "Más tributación a grandes patrimonios y rentas del capital para financiar la prestación por crianza.", "127", "programa", ["rankia"],
  [(R("patrimonio_mas_1M"), -1, "Con tu patrimonio es probable que pagues más (tipos no concretados)."),
   (R("ahorro_alto"), -1, "Con tus rentas del capital es probable que pagues más.")]),
M("psoe-42", "psoe", "Vivienda", "Movilizar el 1 % del PIB al año en vivienda y crear un parque público estatal de 100.000 viviendas.", "38, 42", "programa", ["rankia"],
  [(R("busca_vivienda_asequible"), 1, "Más vivienda pública de alquiler asequible a la que optar.")], ["gasto_sin_financiar"]),
M("psoe-67", "psoe", "Vivienda", "Préstamo «TU CASA» de hasta 50.000 € sin intereses para la entrada (10.000 M€).", "67", "programa", ["rankia"],
  [(R("quiere_comprar"), 1, "Te financiaría la entrada sin intereses.")], ["ayuda_demanda_precio", "gasto_sin_financiar"]),
M("psoe-61", "psoe", "Vivienda", "Contratos de alquiler más largos y congelación temporal de rentas por encima del índice en zonas tensionadas; regular el alquiler de temporada y por habitaciones.", "61-62", "programa", ["rankia", "telemadrid"],
  [(R("casero"), -1, "Limitaría las subidas y alargaría los contratos de tus viviendas en zonas tensionadas."),
   (R("inquilino_tensionada"), 1, "Más estabilidad y freno a las subidas de tu alquiler."),
   (R("inquilino"), 1, "Contratos más largos; la congelación solo aplica en zonas tensionadas.")], ["tope_alquiler_oferta"]),
M("psoe-70", "psoe", "Vivienda", "Impuesto progresivo a grandes tenedores y fondos que no destinen viviendas al alquiler asequible; impuesto a solares residenciales sin edificar.", "53, 70, 72", "programa", ["rankia"],
  [(R("gran_tenedor"), -1, "Con 10 o más viviendas podrías entrar en este impuesto.")]),
M("psoe-turis", "psoe", "Vivienda", "Consolidar las bonificaciones fiscales a los propietarios que bajen el alquiler y permitir a los ayuntamientos un recargo por pernoctación en viviendas turísticas.", "66, 73", "programa", ["brains"],
  [(ALL(R("vivienda_turistica"), R("casero")), 0, "La bonificación te favorecería en tus alquileres; en la vivienda turística, tus huéspedes podrían pagar un recargo municipal."),
   (R("vivienda_turistica"), 0, "Tus huéspedes podrían pagar un recargo municipal por noche, si tu ayuntamiento lo aplica."),
   (R("casero"), 1, "Pagarías menos si mantienes la renta contenida.")]),
M("psoe-108", "psoe", "Empleo", "Jornada de 37,5 horas con objetivo de 35, sin pérdida salarial.", "108", "programa", ["rankia"],
  [(R("asalariado"), 1, "Trabajarías menos horas por el mismo sueldo."),
   (R("empleador"), -1, "Te subiría el coste por hora de tu plantilla.")], ["jornada_ley"]),
M("psoe-87", "psoe", "Empleo", "Salario mínimo siempre por encima del 60 % del salario medio.", "87", "programa", ["rankia"],
  [(ALL(R("asalariado"), R("renta_baja")), 1, "Tu sueldo subiría si está cerca del mínimo."),
   (R("empleador"), -1, "Más coste si tienes plantilla con salarios bajos.")], ["smi_empleo"]),
M("psoe-110", "psoe", "Empleo", "Endurecer la indemnización por despido improcedente y recuperar los salarios de tramitación.", "110-111", "programa", ["rankia"],
  [(R("asalariado"), 1, "Más protección económica si te despiden de forma improcedente."),
   (R("empleador"), -1, "Despedir sin causa te costaría más."),
   (R("parado"), 0, "más protección cuando encuentres empleo; algunos economistas advierten que encarecer el despido frena la contratación indefinida.")]),
M("psoe-becario", "psoe", "Empleo", "Aprobar el Estatuto del Becario y reconocer a los becarios la protección por desempleo.", "113, 118", "programa", ["queproponen"],
  [(R("estudiante"), 1, "Más derechos si haces prácticas.")]),
M("psoe-100", "psoe", "Pensiones", "Blindar en la Constitución la revalorización de las pensiones con el IPC.", "100", "programa", ["rankia"],
  [(R("pensionista"), 1, "La subida con los precios pasaría de ley ordinaria a garantía constitucional, más difícil de cambiar.")]),
M("psoe-105", "psoe", "Familia", "Cuatro semanas de permiso parental pagadas al 100 % para menores de ocho años.", "105", "programa", ["rankia"],
  [(ALL(ANY(R("hijos_menores_8"), R("quiere_hijos")), R("trabaja")), 1, "Podrías cogerlo cobrando el sueldo íntegro.")], ["gasto_sin_financiar"]),
M("psoe-192", "psoe", "Familia", "Prestación estatal por crianza para unos 8 millones de menores.", "192", "programa", ["rankia"],
  [(R("con_hijos"), 1, "Cobrarías una ayuda por tus hijos (importe no detallado).")], ["gasto_sin_financiar"]),
M("psoe-193", "psoe", "Familia", "«Cuenta de Futuro» de 1.000 € por niño al nacer.", "193", "programa", ["rankia"],
  [(R("quiere_hijos"), 1, "Recibirías 1.000 € por cada nacimiento.")], ["gasto_sin_financiar"]),
M("psoe-136", "psoe", "Sanidad", "Financiación sanitaria pública en torno al 7 % del PIB; primera consulta psicológica gratuita en un máximo de 30 días.", "136, 143", "programa", ["rankia", "telemadrid"], [], ["gasto_sin_financiar"], universal=True),
M("psoe-229", "psoe", "Territorio", "Nuevo modelo autonómico con 21.000 M€ adicionales y asunción parcial de 83.000 M€ de deuda autonómica; 19.000 M€ para ferrocarril hasta 2030.", "128, 229, 231", "programa", ["rankia"], [], ["gasto_sin_financiar"], universal=True),

# ===== VOX =====
M("vox-3a", "vox", "IRPF", "Rebajar y simplificar el IRPF, con tipos más bajos según el número de hijos. El programa no concreta tipos ni tramos.", "2", "programa", ["rankia", "democrata_vox"],
  [(ALL(R("paga_irpf"), R("con_hijos")), 1, "Pagarías menos IRPF, y más rebaja por tener hijos. Cuánto, no se sabe."),
   (R("paga_irpf"), 1, "Pagarías menos IRPF. Cuánto, no se sabe: el programa no da tipos."),
   (ALL(R("trabaja"), R("renta_smi")), 0, "Con ingresos cercanos al SMI apenas notarías diferencia.")], ["irpf_reparto", "rebaja_sin_financiar"]),
M("vox-3b", "vox", "IVA", "Rebajar los tipos general y reducido del IVA, sobre todo en productos de primera necesidad.", "2", "programa", ["rankia", "democrata_vox"],
  [(R("sin_iva"), 0, IGIC), (ALWAYS, 1, "Abarataría tu compra (sin tipos concretos).")], ["iva_poco_focalizado", "rebaja_sin_financiar"]),
M("vox-3c", "vox", "Empresa", "Rebajar el Impuesto de Sociedades.", "2", "programa", ["rankia"],
  [(R("empresario"), 1, "Tu sociedad pagaría menos (sin tipo concreto).")], ["rebaja_sin_financiar"]),
M("vox-3d", "vox", "Autónomos", "Cuota cero para autónomos que no alcancen el SMI y cuota progresiva desde 50 € por encima.", "2", "programa", ["rankia", "vox_web"],
  [(ALL(R("autonomo_o_futuro"), R("renta_baja")), 1, "Con tus ingresos pagarías poco o nada de cuota."),
   (R("autonomo_o_futuro"), 0, "Por encima del SMI la cuota sería progresiva; si pagas más o menos que hoy depende de una escala no publicada.")], ["rebaja_sin_financiar"]),
M("vox-34", "vox", "Vivienda", "Primera vivienda de una familia española: IVA del 0 % si es nueva y bonificación del 100 % del ITP si es de segunda mano.", "34", "programa", ["rankia", "vox_web"],
  [(ALL(R("quiere_comprar"), R("extranjero")), 0, "La web del partido habla de «familia española»: no está claro que te aplique."),
   (ALL(R("quiere_comprar"), R("sin_iva")), 1, "Te ahorrarías el ITP si compras usada; el IVA no aplica en tu territorio."),
   (R("quiere_comprar"), 1, "Te ahorrarías el impuesto de la compra.")], ["ayuda_demanda_precio", "rebaja_sin_financiar"]),
M("vox-28", "vox", "Vivienda", "Derogar la Ley de Vivienda y reformar la Ley del Suelo; desalojo de okupas en menos de 24 horas.", "28-31", "programa", ["rankia"],
  [(R("casero"), 1, CASERO_GANA),
   (R("tiene_otras_viviendas"), 1, "Más protección frente a la okupación de tus viviendas."),
   (R("inquilino_tensionada"), -1, "Perderías el tope de renta de la zona tensionada."),
   (R("inquilino"), 0, "Fuera de zona tensionada, el efecto directo es pequeño.")], ["fin_topes_alquiler"]),
M("vox-35", "vox", "Vivienda", "Fiscalidad agravada para compradores de fuera de la UE y para operaciones especulativas de fondos.", "35", "programa", ["rankia"],
  [(ALL(R("extracomunitario"), R("quiere_comprar")), -1, "Si compras como no comunitario/a, pagarías más impuestos."),
   (R("gran_tenedor"), 0, "Podría afectarte si tus operaciones se consideran especulativas (sin definición publicada).")]),
M("vox-18", "vox", "Prioridad nacional", "Acceso preferente de españoles a vivienda pública, guarderías, bonos de comedor y transporte, ayudas y servicios sociales; el IMV, solo para españoles.", "18-25", "programa", ["rankia", "vox_web"],
  [(R("extranjero"), -1, "Pasarías por detrás en vivienda pública, guarderías, becas y ayudas, y perderías el acceso al IMV."),
   (ALL(R("espanol"), ANY(R("busca_vivienda_asequible"), R("con_hijos"), R("estudiante"), R("renta_baja"), R("parado"))), 1, "Tendrías prioridad frente a residentes extranjeros en ayudas y servicios que podrías usar.")], ["prioridad_legal"]),
M("vox-remesas", "vox", "Prioridad nacional", "Gravamen sobre las remesas de inmigrantes.", "18-25", "programa", ["rankia", "vox_web"],
  [(R("envia_remesas"), -1, "Pagarías un impuesto por el dinero que envías a tu familia.")]),
M("vox-7", "vox", "Pensiones", "Avanzar hacia un modelo de pensiones mixto con capitalización y vincularlas a productividad y natalidad. No figura en el programa del 29N, que solo promete garantizar su sostenibilidad con crecimiento económico (medida 7); lo recogen la prensa y declaraciones del partido.", None, "campaña", ["rankia", "moncloa_vp"],
  [(R("pensionista"), 0, "Sustituiría la garantía de subida con el IPC por otros criterios sin fórmula publicada."),
   (ALL(R("trabaja"), R("menor_40")), 0, "Parte de tu futura pensión podría depender de la capitalización; no hay detalles.")], ["pensiones_transicion"]),
M("vox-94", "vox", "Familia", "Plan de natalidad y cotizaciones pagadas por el Estado a quienes cuidan hijos.", "94", "programa", ["rankia"],
  [(ANY(R("con_hijos"), R("quiere_hijos")), 1, "El Estado pagaría tus cotizaciones durante el tiempo de cuidado.")], ["gasto_sin_financiar"]),
M("vox-laboral", "vox", "Empleo", "Derogar la legislación laboral del Gobierno (incluida la reforma laboral de 2021).", "8", "programa", ["telemadrid", "rankia"],
  [(Q("lab", eq="asal_temp"), 0, "La reforma de 2021 limitó los contratos temporales; no se detalla qué la sustituiría. Con contrato temporal o fijo discontinuo, te toca de lleno."),
   (R("asalariado"), 0, "La reforma de 2021 limitó los contratos temporales; no se detalla qué la sustituiría."),
   (R("empleador"), 0, "Podría darte más flexibilidad de contratación; depende de la norma que la sustituya.")]),
M("vox-sucesiones", "vox", "Patrimonio", "Suprimir los impuestos de Patrimonio, Sucesiones y Donaciones y la plusvalía municipal.", None, "previa", ["pe_vox", "brains"],
  [(ANY(Q("patr", gte=2), R("herencia")), 1, "Pagarías menos al heredar, donar o por tu patrimonio (depende de lo que ya bonifique tu comunidad).")], ["rebaja_sin_financiar"]),
M("vox-4", "vox", "Territorio", "Alivio fiscal para Canarias, Baleares y zonas en riesgo de despoblación.", "4, 6", "programa", ["rankia", "vox_web"],
  [(ANY(R("canarias"), R("baleares")), 0, "Te afectaría, pero los resúmenes no detallan en qué consiste.")], ["rebaja_sin_financiar"]),
M("vox-8", "vox", "Energía", "Rebajar los impuestos de la electricidad y mantener las nucleares, con estudios para nuevas centrales.", "8", "programa", ["rankia"], [], ["rebaja_sin_financiar"], universal=True),

# ===== FRENTE AMPLIO =====
M("fa-fortunas", "fa", "Patrimonio", "Que los patrimonios de más de 1 millón paguen como mínimo un 2 % (reforma del Impuesto de Grandes Fortunas, con mínimo exento de 700.000 €) y un 3 % anual los de más de 50 millones.", None, "programa", ["democrata_fa", "marcos_fa"],
  [(R("patrimonio_mas_1M"), -1, "Con tu patrimonio pagarías este impuesto."),
   (R("patrimonio_300k_1M"), 0, "Por debajo de 1 millón de patrimonio neto no lo pagarías.")]),
M("fa-rentas", "fa", "IRPF", "Más tramos del IRPF desde 120.000 € y tipo marginal de hasta el 52 % desde 300.000 €; acercar la tributación de las rentas del capital a la del trabajo; tipo mínimo real del 20 % en Sociedades.", None, "programa", ["democrata_fa", "marcos_fa"],
  [(Q("ing", eq=6), -1, "Si tus ingresos superan los 120.000 €, pagarías más IRPF."),
   (R("ahorro_alto"), -1, "Tus rentas del ahorro tributarían más.")]),
M("fa-irpf", "fa", "IRPF", "Bajar el IRPF a las rentas del trabajo de hasta 27.000 €: quien cobre el salario mínimo no pagaría y la rebaja decrece hasta esa cifra.", None, "programa", [],
  [(ALL(R("trabaja"), R("renta_baja")), 1, "Pagarías menos IRPF por tu sueldo (o nada si cobras el salario mínimo).")], ["rebaja_sin_financiar"]),
M("fa-tope", "fa", "Cotizaciones", "Seguir elevando progresivamente el tope máximo de cotización a la Seguridad Social y una aportación adicional de las empresas más automatizadas.", None, "programa", ["marcos_fa"],
  [(ALL(R("asalariado"), R("renta_alta")), -1, "Cotizarías por una parte mayor de tu salario por encima de la base máxima actual (unos 60.000 €)."),
   (ALL(R("empleador"), Q("ing", gte=4)), -1, "Subiría el coste de tus empleados con sueldos altos.")]),
M("fa-pension", "fa", "Pensiones", "Pensión mínima igual al salario mínimo y edad de jubilación de vuelta a los 65 años (coste estimado por el partido en campaña: unos 20.000 M€/año).", None, "programa", ["marcos_fa"],
  [(ALL(R("pensionista"), R("renta_smi")), 1, "Tu pensión subiría hasta el salario mínimo."),
   (R("pensionista"), 0, "Tu pensión ya supera el mínimo; no cambia directamente."),
   (ALL(R("trabaja"), ANY(R("edad_41_64"), Q("edad", eq="36-40"))), 1, "Podrías jubilarte a los 65 sin penalización.")], ["gasto_sin_financiar"]),
M("fa-viv", "fa", "Vivienda", "Ley de expropiación de viviendas a propietarios corporativos (por fases: más de 1.000, más de 700 y más de 50 viviendas), no a particulares, para ampliar el parque público.", None, "programa", ["democrata_fa", "marcos_fa"],
  [(R("gran_tenedor"), 0, "Afecta a fondos y empresas, no a particulares; si tus viviendas están en una sociedad, podrías estar afectado."),
   (R("busca_vivienda_asequible"), 1, "Más vivienda pública de alquiler asequible a la que optar.")], ["expropiacion_plazos", "gasto_sin_financiar"]),
M("fa-acum", "fa", "Vivienda", "Impuesto del 10 % sobre el valor de los pisos: a las empresas desde el primero y a los particulares desde el cuarto, si sus viviendas valen en conjunto más de 800.000 €.", None, "programa", ["telemadrid"],
  [(R("varias_viviendas"), -1, "Con cuatro viviendas o más lo pagarías si su valor conjunto supera los 800.000 €."),
   (R("tiene_otras_viviendas"), 0, "Con hasta tres viviendas en total no lo pagarías como particular.")]),
M("fa-indef", "fa", "Vivienda", "Contrato de alquiler indefinido por defecto; regular la huelga de alquileres y reconocer a los sindicatos de inquilinas.", None, "programa", ["marcos_fa"],
  [(R("casero"), -1, "Tus inquilinos podrían quedarse indefinidamente y organizarse para negociar la renta."),
   (R("inquilino"), 1, "No tendrías que irte al acabar el contrato y tendrías más fuerza para negociar.")], ["tope_alquiler_oferta"]),
M("fa-autonomos", "fa", "Autónomos", "Cotización fija bonificada para autónomos cuyos ingresos reales no lleguen al salario mínimo.", None, "programa", ["telemadrid"],
  [(ALL(R("autonomo_o_futuro"), R("renta_smi")), 1, "Pagarías una cuota fija bonificada."),
   (R("autonomo_o_futuro"), 0, "Por encima del salario mínimo no te aplicaría.")]),
M("fa-smi", "fa", "Empleo", "Salario mínimo fijado por ley en el 60 % del salario medio neto y jornada máxima de 32 horas semanales sin bajar el sueldo (37,5 horas de inmediato).", None, "programa", ["democrata_fa", "marcos_fa"],
  [(R("asalariado"), 1, "Menos horas por el mismo sueldo y, si cobras cerca del mínimo, más salario."),
   (R("empleador"), -1, "Más coste laboral por hora.")], ["smi_empleo", "jornada_ley"]),
M("fa-sanidad", "fa", "Sanidad", "Incluir gafas, audífonos, dentista y atención integral a la menopausia en la sanidad pública.", None, "programa", ["telemadrid", "marcos_fa"], [], ["gasto_sin_financiar"], universal=True),

# ===== PODEMOS =====
M("pod-smi", "pod", "Empleo", "Salario mínimo de 1.800 € fijado por ley.", None, "campaña", ["telemadrid", "democrata_pod"],
  [(ALL(R("asalariado"), R("renta_baja")), 1, "Tu sueldo subiría bastante si estás cerca del mínimo."),
   (R("empleador"), -1, "Subiría mucho el coste de tu plantilla en salarios bajos.")], ["smi_empleo"]),
M("pod-jornada", "pod", "Empleo", "Reducir la jornada sin bajar el sueldo (Telemadrid cita 30 horas semanales; otras informaciones, 35 o 37).", None, "campaña", ["telemadrid", "democrata_pod"],
  [(R("asalariado"), 1, "Menos horas por el mismo sueldo."),
   (R("empleador"), -1, "Te subiría el coste por hora.")], ["jornada_ley"]),
M("pod-30", "pod", "Vivienda", "Ley para que ningún hogar dedique más del 30 % de su renta al alquiler.", None, "previa", ["brains"],
  [(R("casero"), -1, "La renta que cobras quedaría limitada por los ingresos de tu inquilino."),
   (R("inquilino"), 1, "Tu alquiler no podría superar el 30 % de tus ingresos.")], ["tope_alquiler_oferta"]),
M("pod-40", "pod", "Vivienda", "Rebaja del 40 % de los alquileres (exigida en 2024 y 2025 para negociar los Presupuestos).", None, "previa", ["brains"],
  [(R("casero"), -1, "Cobrarías bastante menos renta."),
   (R("inquilino"), 1, "Pagarías bastante menos de alquiler.")], ["tope_alquiler_oferta"]),
M("pod-fondos", "pod", "Vivienda", "Contratos más largos, más protección frente a desahucios, expropiación del uso de viviendas de fondos y prohibición de comprar vivienda sin finalidad residencial.", None, "previa", ["brains", "democrata_pod"],
  [(R("casero"), -1, "Menos margen para recuperar o actualizar tus viviendas alquiladas, y no podrías comprar más como inversión."),
   (R("tiene_otras_viviendas"), -1, "No podrías comprar más viviendas como inversión."),
   (R("inquilino"), 1, "Más estabilidad en tu vivienda."),
   (R("quiere_comprar"), 0, "menos competencia de inversores al comprar; el efecto en precios es incierto.")], ["expropiacion_plazos", "tope_alquiler_oferta"]),
M("pod-gasto", "pod", "Gasto público", "Rechazar el aumento del gasto militar y destinar más a sanidad, educación, cuidados y clima.", None, "campaña", ["democrata_pod"], [], ["gasto_sin_financiar"], universal=True),

# ===== COALICIÓN CANARIA =====
M("cc-empad", "cc", "Vivienda", "Exigir diez años de empadronamiento en Canarias para comprar vivienda (quince si no son continuos) y limitar a dos las viviendas por persona en municipios distintos. No figura en el programa del 29N.", None, "previa", ["pe_cc"],
  [(ALL(R("quiere_comprar"), R("empadronado_10_canarias")), 1, "tendrías menos competencia de compradores de fuera."),
   (R("quiere_comprar"), -1, "No podrías comprar en Canarias hasta cumplir los años de empadronamiento."),
   (R("varias_viviendas"), -1, "Limitaría tus futuras compras de vivienda.")]),
M("cc-alq", "cc", "Vivienda", "Rechazar la renovación automática de alquileres y proteger a los pequeños propietarios. El programa del 29N solo recoge incentivos fiscales a pequeños propietarios que alquilen a precio asequible (acción 24).", None, "previa", ["pe_cc"],
  [(R("pequeno_casero"), 1, "Mantienes el control sobre tus contratos."),
   (R("inquilino"), 0, "No tendrías renovación automática del contrato; CC apuesta por ayudas y más oferta.")]),
M("cc-viv", "cc", "Vivienda", "Fondo estatal de ocho años para vivienda pública y asequible en Canarias y línea estatal de vivienda joven, alquiler asequible y cooperativas.", "22, 25", "programa", ["pe_cc", "eldiario_cc"],
  [(ANY(R("busca_vivienda_asequible"), R("quiere_comprar")), 1, "Más ayudas y vivienda pública a tu alcance (sin cifras).")], ["ayuda_demanda_precio", "gasto_sin_financiar"]),
M("cc-empleo", "cc", "Empleo", "Mantener el Plan Integral de Empleo de Canarias y un plan cuatrienal de empleo para menores de 35 años.", "31, 45", "programa", ["pe_cc"],
  [(ANY(R("parado"), ALL(R("joven_18_35"), NOT(R("trabaja")))), 1, "Más recursos de empleo para ti."),
   ], ["gasto_sin_financiar"]),
M("cc-pens", "cc", "Pensiones", "Que las pensiones no contributivas sumen el complemento canario sin tributar ni perder ingresos, y que Canarias pueda tramitar el Ingreso Mínimo Vital.", "16, 19", "programa", ["pe_cc"],
  [(ALL(R("pensionista"), R("pension_no_contributiva")), 1, "Cobrarías el complemento canario sin que te descuenten de la pensión."),
   (ALL(R("renta_smi"), Q("lab", **{"in": ["parado", "otro", "estudiante"]})), 1, "Te sería más fácil acceder al IMV si cumples los requisitos.")]),
M("cc-transp", "cc", "Transporte", "Consolidar el descuento de residente del 75 % y actualizar las ayudas al transporte de mercancías.", "75, 80", "programa", ["pe_cc"],
  [(R("canarias"), 1, "Mantienes el descuento en vuelos y barcos; la cesta de la compra podría abaratarse.")]),
M("cc-03", "cc", "Familia", "Más financiación estatal para plazas públicas gratuitas de 0 a 3 años.", "14", "programa", ["pe_cc"],
  [(ANY(R("hijos_0_3"), R("quiere_hijos")), 1, "Te ahorrarías la escuela infantil.")], ["gasto_sin_financiar"]),
M("cc-agua", "cc", "Agua y sanidad", "Compensaciones estatales actualizadas por el sobrecoste del agua desalada y por el coste sanitario de la insularidad.", "10, 66", "programa", ["pe_cc"], [], ["gasto_sin_financiar"], universal=True),

# ===== ERC (programa en catalán; resúmenes traducidos) =====
M("erc-69a", "erc", "Ahorro", "Subir del 30 % al 35 % el tipo máximo del IRPF sobre las ganancias de capital.", "69", "programa", ["democrata_erc"],
  [(R("ahorro_mas_300k"), -1, "Pagarías más por tus rentas del ahorro del tramo más alto.")]),
M("erc-69b", "erc", "IRPF", "Rebajar los tipos del IRPF sobre el trabajo en los tramos inferiores a 35.000 €. El programa no concreta tipos.", "69", "programa", ["democrata_erc"],
  [(ALL(R("paga_irpf"), Q("ing", lte=3)), 1, "Pagarías menos IRPF por tu trabajo o pensión. Cuánto, no se sabe: no da tipos."),
   (R("paga_irpf"), 0, "La rebaja es para los tramos inferiores a 35.000 €; si te alcanza en parte depende de cómo se diseñe.")], ["rebaja_sin_financiar"]),
M("erc-70", "erc", "IVA", "Rebajar el IVA de los alimentos básicos y los productos de higiene, y suprimir buena parte de los tipos reducidos y deducciones por encima de la media europea.", "70", "programa", ["democrata_erc"],
  [(R("sin_iva"), 0, IGIC), (ALWAYS, 1, "Abarataría tu compra básica (sin tipos concretos); otros productos con IVA reducido podrían encarecerse.")], ["iva_poco_focalizado", "rebaja_sin_financiar"]),
M("erc-74", "erc", "Patrimonio", "Hacer permanente el impuesto temporal de solidaridad de las grandes fortunas, con un tipo más alto por encima de 10 millones de euros y un tramo nuevo desde 100 millones.", "74", "programa", ["democrata_erc"],
  [(Q("patr", eq=4), -1, "Con más de 3 millones de patrimonio seguirías pagando este impuesto de forma permanente (más por encima de 10 millones)."),
   (R("patrimonio_mas_1M"), 0, "El impuesto actual empieza en 3 millones de patrimonio neto; por debajo no lo pagarías.")]),
M("erc-59", "erc", "Vivienda", "Subir el IVA y el ITP de la compra de vivienda que no vaya a ser residencia habitual (uso turístico, temporada, segunda residencia o vacía) y bajarlos cuando sea primera residencia; IVA del 21 % en el alquiler turístico.", "59-60", "programa", ["democrata_erc"],
  [(R("vivienda_turistica"), -1, "Tus alquileres turísticos pasarían a llevar un IVA del 21 %."),
   (R("quiere_comprar"), 1, "Pagarías menos impuestos al comprar tu vivienda habitual (tipos no concretados)."),
   (R("tiene_otras_viviendas"), 0, "Si compras otra vivienda que no sea residencia habitual, pagarías más IVA o ITP.")], ["ayuda_demanda_precio", "rebaja_sin_financiar"]),
M("erc-56", "erc", "Vivienda", "Dedicar al menos el 1,5 % del PIB a políticas de vivienda, transferido a las comunidades para ampliar el parque público de alquiler, y traspasar a la Generalitat los inmuebles de la Sareb y Casa 47.", "56-57", "programa", ["democrata_erc"],
  [(R("busca_vivienda_asequible"), 1, "Más vivienda pública de alquiler asequible a la que optar.")], ["gasto_sin_financiar"]),
M("erc-66", "erc", "Empleo", "Salario mínimo estatal al 60 % del salario medio bruto y competencia para que la Generalitat fije un salario mínimo catalán de 1.460 €.", "66-67", "programa", ["democrata_erc"],
  [(ALL(R("asalariado"), R("renta_baja")), 1, "Tu sueldo subiría si estás cerca del mínimo."),
   (R("empleador"), -1, "Más coste si tienes plantilla con salarios bajos.")], ["smi_empleo"]),
M("erc-105", "erc", "Empleo", "Jornada máxima de 37,5 horas semanales sin reducción salarial.", "105", "programa", ["democrata_erc"],
  [(R("asalariado"), 1, "Trabajarías menos horas por el mismo sueldo."),
   (R("empleador"), -1, "Te subiría el coste por hora de tu plantilla.")], ["jornada_ley"]),
M("erc-103", "erc", "Empleo", "Recuperar la indemnización por despido improcedente de 45 días por año (máximo 42 mensualidades) y los salarios de tramitación, y una indemnización adicional sin tope en los despidos sin causa.", "103-104", "programa", [],
  [(R("asalariado"), 1, "Más protección económica si te despiden de forma improcedente."),
   (R("empleador"), -1, "Despedir sin causa te costaría más."),
   (R("parado"), 0, "más protección cuando encuentres empleo; algunos economistas advierten que encarecer el despido frena la contratación indefinida.")]),
M("erc-106", "erc", "Pensiones", "Blindar la revalorización de las pensiones con la inflación y actualizarlas con el IPC de cada territorio.", "106-107", "programa", ["democrata_erc"],
  [(R("pensionista"), 1, "Mantendrías la subida con los precios, calculada con el IPC de tu territorio: si allí suben más que la media, tu pensión subiría algo más (y al revés).")]),
M("erc-112", "erc", "Autónomos", "Cuotas de autónomos según ingresos reales, con cuotas reducidas por debajo del salario mínimo (con aportación de los Presupuestos) y nuevos tramos para ingresos de más de 6.000 € al mes.", "112", "programa", [],
  [(ALL(R("autonomo_o_futuro"), R("renta_smi")), 1, "Con tus ingresos pagarías una cuota reducida."),
   (ALL(R("autonomo"), Q("ing", eq=6)), -1, "Con ingresos altos podrías entrar en los nuevos tramos de más de 6.000 € al mes."),
   (R("autonomo_o_futuro"), 0, "Tu cuota dependería de tus ingresos reales; la escala no está publicada.")], ["gasto_sin_financiar"]),
M("erc-68", "erc", "Familia", "Prestación universal por crianza desde 200 € por familia, más alta en territorios con mayor coste de vida, como Cataluña.", "68", "programa", ["democrata_erc"],
  [(R("con_hijos"), 1, "Cobrarías al menos 200 € por familia (el programa no aclara si es al mes; la prensa habla de 200 € mensuales)."),
   (R("quiere_hijos"), 1, "La cobrarías al tener hijos.")], ["gasto_sin_financiar"]),
]


# --- "No lo sé" en planHijos: añade un efecto incierto a cada medida que dependa de quiere_hijos
import copy as _copy
def _swap(c):
    if isinstance(c, dict):
        return {k: (("quizas_hijos" if v == "quiere_hijos" else v) if k == "ref" else _swap(v)) for k, v in c.items()}
    if isinstance(c, list): return [_swap(x) for x in c]
    return c
for m in MEAS:
    src = [e for e in m["efectos"] if "quiere_hijos" in json.dumps(e["si"])]
    if src:
        e = src[0]
        m["efectos"].append({"si": _swap(_copy.deepcopy(e["si"])), "valor": 0, "texto": "Solo si finalmente tienes un hijo (o uno más): " + e["texto"][0].lower() + e["texto"][1:]})

# --- Escala de cada vínculo medida→riesgo. "amplia": impuesto o programa general / coste grande publicado.
# "acotada": colectivo concreto o medida condicional. Si todos los vínculos de un riesgo son acotados,
# la exposición máxima del riesgo para ese partido baja de "alta" a "media".
ACOTADA = {
 ("pp-177","rebaja_sin_financiar"),("pp-179","rebaja_sin_financiar"),("pp-181","rebaja_sin_financiar"),
 ("pp-170","rebaja_sin_financiar"),("pp-171","rebaja_sin_financiar"),("pp-153","rebaja_sin_financiar"),
 ("pp-156a","rebaja_sin_financiar"),("pp-156b","rebaja_sin_financiar"),("pp-114","rebaja_sin_financiar"),
 ("pp-familia","rebaja_sin_financiar"),("fa-irpf","rebaja_sin_financiar"),("psoe-88","rebaja_sin_financiar"),
 ("vox-3d","rebaja_sin_financiar"),("vox-34","rebaja_sin_financiar"),("vox-4","rebaja_sin_financiar"),
 ("psoe-134","gasto_sin_financiar"),("psoe-105","gasto_sin_financiar"),("psoe-193","gasto_sin_financiar"),
 ("vox-94","gasto_sin_financiar"),("cc-viv","gasto_sin_financiar"),("cc-empleo","gasto_sin_financiar"),
 ("cc-03","gasto_sin_financiar"),("cc-agua","gasto_sin_financiar"),
 ("erc-69b","rebaja_sin_financiar"),("erc-59","rebaja_sin_financiar"),("erc-112","gasto_sin_financiar"),
}
for m in MEAS:
    m["riesgos"] = [{"id": r, "escala": "acotada" if (m["id"], r) in ACOTADA else "amplia"} for r in m["riesgos"]]

# Candidaturas reales en la papeleta del Congreso, por comunidad. Fuente: listas registradas (prensa, 2-nov-2026).
# tipo "fusion": varios partidos del test concurren juntos; "renombrar": otro nombre en la papeleta; "excluir": no presenta lista.
CANDIDATURAS = [
 {"tipo": "fusion", "id": "upc", "si": Q("region", eq="canarias"), "partidos": ["fa", "pod"],
  "nombre": "Unidad del Pueblo Canario",
  "integrantes": "Nueva Canarias-Bloque Canarista, Podemos Canarias, Izquierda Unida Canaria, Movimiento Sumar Canarias y Partido Verde Canarias",
  "nota": "Candidatura conjunta. El test usa las medidas estatales de Frente Amplio y Podemos; las propuestas propias de Nueva Canarias-Bloque Canarista aún no están incluidas.",
  "fuentes": ["manifiesto_upc", "upc", "democrata_listas"]},
 {"tipo": "fusion", "id": "compromis", "si": Q("region", eq="valencia"), "partidos": ["fa", "pod"],
  "nombre": "Compromís-Front Valencià",
  "integrantes": "Compromís, Podemos, los partidos del Frente Amplio y Esquerra Republicana del País Valencià",
  "nota": "Candidatura conjunta. El test usa las medidas estatales de Frente Amplio y Podemos; las propuestas propias de Compromís aún no están incluidas.",
  "fuentes": ["democrata_listas", "diari_fa"]},
 {"tipo": "fusion", "id": "ara_mes", "si": Q("region", eq="baleares"), "partidos": ["fa", "pod", "erc"],
  "nombre": "Ara Més-Front Ampli",
  "integrantes": "Més per Mallorca, Més per Menorca, Ara Eivissa, los partidos del Frente Amplio y ERC; Podemos va como independiente dentro de la lista",
  "nota": "Candidatura conjunta. El test usa las medidas estatales de Frente Amplio y Podemos, y las de ERC, tomadas de su programa para Cataluña (en catalán; los resúmenes son traducciones). Las propuestas propias de Ara Més aún no están incluidas.",
  "fuentes": ["democrata_listas", "diari_fa"]},
 {"tipo": "renombrar", "si": Q("region", eq="cataluna"), "partido": "fa", "nombre": "Comuns-Frente Amplio", "fuentes": ["democrata_listas"]},
 {"tipo": "excluir", "si": Q("region", eq="cataluna"), "partido": "pod",
  "nota": "Podemos no presenta lista propia en Cataluña: lleva candidatos independientes en la lista de ERC.", "fuentes": ["democrata_listas"]},
 {"tipo": "renombrar", "si": Q("region", eq="aragon"), "partido": "fa", "nombre": "CHA-Frente Amplio Aragón",
  "nota": "En la provincia de Teruel no presenta lista.", "fuentes": ["diari_fa", "democrata_listas"]},
 {"tipo": "renombrar", "si": Q("region", eq="andalucia"), "partido": "fa", "nombre": "Frente Amplio por Andalucía", "fuentes": ["eldiario_fa"]},
 {"tipo": "excluir", "si": Q("region", **{"in": ["ceuta", "melilla"]}), "partido": "fa",
  "nota": "Frente Amplio no presenta lista en Ceuta ni en Melilla.", "fuentes": ["democrata_listas"]},
 {"tipo": "renombrar", "si": Q("region", eq="canarias"), "partido": "cc", "nombre": "Coalición Canaria-Primero Canarias", "fuentes": ["eldiario_cc"]},
]

NOTAS = [
 {"si": R("parado"), "texto": "Desempleo: las fuentes consultadas no recogen medidas concretas de los partidos estatales sobre la prestación por desempleo. Si es tu prioridad, revisa ese capítulo en cada programa."},
 {"si": R("sin_iva"), "texto": "IVA: en tu territorio no se aplica (Canarias: IGIC; Ceuta y Melilla: IPSI). Las rebajas de IVA aparecen como inciertas para ti, aunque su coste en la recaudación estatal sí cuenta en los riesgos."},
 {"si": R("cuida_dependiente"), "texto": "Dependencia: comprueba si cada medida cubre el cuidado familiar o solo el gasto en cuidados profesionales."},
 {"si": Q("region", eq="cataluna"), "texto": "Partidos no incluidos: en Cataluña también se presenta Junts. Este test aún no recoge sus medidas; consulta su programa. ERC sí está incluido (su programa está en catalán; los resúmenes son traducciones)."},
 {"si": Q("region", eq="pais_vasco"), "texto": "Partidos no incluidos: en el País Vasco también se presentan PNV (programa publicado en noviembre) y EH Bildu (sin programa a la fecha de corte). Este test aún no recoge sus medidas; consulta sus programas."},
 {"si": Q("region", eq="navarra"), "texto": "Partidos no incluidos: en Navarra también se presenta EH Bildu (sin programa a la fecha de corte), entre otras candidaturas territoriales. Este test aún no recoge sus medidas."},
 {"si": Q("region", eq="galicia"), "texto": "Partidos no incluidos: en Galicia también se presenta el BNG (programa publicado el 3-nov). Este test aún no recoge sus medidas; consulta su programa."},
 {"si": Q("region", eq="valencia"), "texto": "Candidatura conjunta: en la Comunitat Valenciana, Frente Amplio y Podemos concurren dentro de Compromís-Front Valencià. El test muestra sus medidas estatales; las propias de Compromís aún no están incluidas."},
 {"si": ALWAYS, "texto": "Candidaturas no incluidas: además de los partidos territoriales, se presentan otras candidaturas, como Se Acabó La Fiesta (SALF), cuyo «Contrato Electoral 29N» aún no se ha incorporado. Este test recoge los partidos con medidas detalladas en las fuentes consultadas."},
]
# ---------------------------------------------------------------------------
# Derechos y protecciones: medidas sociales, sin valoración a favor/en contra.
# (partido, tema, número en el programa o None, página del PDF, resumen fiel)
# ---------------------------------------------------------------------------
SOC = [
 # PP
 ("pp", "igualdad", "28", 17, "Más medios contra la violencia de género: las pulseras de alejamiento pasan a depender de Interior, más unidades especializadas, protección también para los hijos de las víctimas y rendición de cuentas anual del Pacto de Estado."),
 ("pp", "igualdad", "29", 17, "Ley integral contra la trata y criterios comunes en toda España frente a la mutilación genital femenina y los matrimonios forzados."),
 ("pp", "igualdad", "115", 35, "Eliminar los obstáculos que frenan la trayectoria de las mujeres y revisar las normas que, a su juicio, han generado inseguridad jurídica en nombre de la igualdad."),
 ("pp", "lgtbi", "111", 35, "Combatir la discriminación por orientación sexual, entre otras causas, y seguir luchando contra la LGTBIfobia."),
 ("pp", "lgtbi", "115", 35, "Revisar la Ley Trans y eliminar la libre autodeterminación registral del sexo. El sexo biológico sería el criterio en las categorías deportivas femeninas."),
 ("pp", "racismo", "111", 35, "Combatir cualquier discriminación por origen, sexo, edad, discapacidad, orientación sexual o religión."),
 ("pp", "migracion", "42", 19, "Prohibir por ley las regularizaciones masivas. El arraigo sería excepcional y el empadronamiento, por sí solo, no daría acceso a ayudas no urgentes."),
 ("pp", "migracion", "41", 19, "Cupos anuales de trabajadores extranjeros según sectores y capacidad de acogida, solo con países que colaboren en los retornos."),
 ("pp", "migracion", "43", 19, "Compromiso de integración obligatorio para renovar la residencia temporal: aprender español y conocer la Constitución."),
 ("pp", "migracion", "141", 39, "Nueva Ley de Nacionalidad con más requisitos (español, historia, valores constitucionales, sin antecedentes) y trato preferente a los países de la Hispanidad."),
 ("pp", "discapacidad", "112", 35, "Atención temprana, asistencia personal, vivienda con apoyos y empleo inclusivo. Pensiones de discapacidad compatibles con el empleo y más jubilación anticipada para personas con síndrome de Down."),
 ("pp", "discapacidad", "213", 51, "No cerrar los centros de educación especial; las familias participarían en la decisión de escolarización."),
 ("pp", "familia", "159", 44, "Medidas para tener los hijos deseados: el concebido no nacido contaría para las ayudas familiares, congelación de óvulos para mujeres jóvenes y revisión de los límites de edad en reproducción asistida."),
 ("pp", "familia", "165", 45, "Reconocimiento común en toda España de las familias monoparentales y conciliación adaptada a quien cría en solitario."),
 ("pp", "educacion", "212", 51, "Libre elección de colegio en todo el municipio. No se eliminaría ningún concierto donde haya demanda y los conciertos durarían al menos seis años."),
 ("pp", "educacion", "133", 38, "Currículos de Historia elaborados con las Reales Academias; el alumnado estudiaría la Constitución, la Transición y el daño del terrorismo."),
 ("pp", "vida", "226", 53, "Ley nacional de cuidados paliativos, para que nadie se vea empujado a acelerar su muerte por falta de alternativas. No menciona el aborto."),
 ("pp", "religion", "43", 19, "Prohibir el burka y el niqab en los espacios públicos."),
 ("pp", "rural", "196", 49, "Menos impuestos a quien vive, invierte y produce en el medio rural; los jóvenes no pagarían impuestos al comprar vivienda en municipios despoblados."),
 ("pp", "rural", "105", 34, "Ayudas directas a los municipios de menos de 250 habitantes para sostener sus servicios básicos."),
 ("pp", "rural", "204", 50, "Plan nacional para la mujer rural y del mar (vivienda, financiación, titularidad, formación)."),
 # PSOE
 ("psoe", "igualdad", "333", 82, "Nueva Estrategia Estatal contra las Violencias Machistas."),
 ("psoe", "igualdad", "335", 82, "Ley Orgánica contra la Violencia Vicaria."),
 ("psoe", "igualdad", "338", 82, "Ayudas a los huérfanos de la violencia de género hasta los 26 años."),
 ("psoe", "igualdad", "350", 84, "Incluir las violencias digitales en la Ley integral contra la violencia de género, más allá de la pareja o expareja."),
 ("psoe", "igualdad", "343", 83, "Programa estatal de salida, protección y reparación para mujeres en servidumbre por deudas dentro de la prostitución."),
 ("psoe", "lgtbi", "412", 97, "La Ley 4/2023 (Ley Trans y LGTBI) como mínimo común en toda España, y una nueva Ley de Familias que reconozca su diversidad."),
 ("psoe", "lgtbi", "414", 97, "Penalizar en el Código Penal las llamadas terapias de conversión."),
 ("psoe", "lgtbi", "415", 97, "Inclusión social y laboral de las personas trans, con acceso y continuidad de los tratamientos hormonales."),
 ("psoe", "lgtbi", "368", 89, "Máxima protección jurídica del matrimonio igualitario, junto al aborto y la eutanasia."),
 ("psoe", "racismo", "392", 93, "Desarrollar la Ley Zerolo y poner en marcha la Autoridad Independiente para la Igualdad de Trato y la No Discriminación."),
 ("psoe", "racismo", "394", 93, "Pacto de Estado contra los discursos y delitos de odio."),
 ("psoe", "racismo", "398", 94, "Más financiación para la Estrategia Nacional del Pueblo Gitano 2021-2030 y la lucha contra el antigitanismo."),
 ("psoe", "migracion", "388", 92, "Plan de Integración y Ciudadanía 2026-2030 con 500 millones iniciales."),
 ("psoe", "migracion", "389", 92, "Más vías legales y seguras de protección internacional, con reasentamiento y visados humanitarios."),
 ("psoe", "migracion", "391", 93, "Sistema de acogida reforzado, con especial protección de los menores que llegan solos."),
 ("psoe", "discapacidad", "205", 57, "Aplicar plenamente la reforma de discapacidad y dependencia (Ley 4/2026) para reducir las listas de espera."),
 ("psoe", "discapacidad", "208", 58, "Más asistencia personal, centros de día y programas de respiro familiar."),
 ("psoe", "discapacidad", "124", 43, "Hacer cumplir la reserva del 2 % de empleo para personas con discapacidad, con más inspección."),
 ("psoe", "familia", "325", 80, "Permisos parentales y por cuidados retribuidos, extendidos a familias monoparentales y autónomos; adaptación y reducción de jornada para cuidar a menores hasta los 16 años."),
 ("psoe", "familia", "199", 57, "Ley de Familias, con reconocimiento y protección de las familias monoparentales."),
 ("psoe", "familia", "196", 56, "Marco estatal de ayudas para productos y cuidados en los primeros 1.000 días de crianza."),
 ("psoe", "educacion", "344", 83, "Coeducación y educación afectivo-sexual obligatorias en todas las etapas."),
 ("psoe", "educacion", "158", 52, "Más becas y un máximo de alumnos por aula, con doble cómputo del alumnado con necesidades especiales."),
 ("psoe", "vida", "327", 81, "Reforma del artículo 43 de la Constitución para blindar el derecho al aborto."),
 ("psoe", "vida", "147", 50, "Garantizar el ejercicio efectivo del derecho a la eutanasia según la ley vigente."),
 ("psoe", "rural", "233", 61, "Servicios públicos de calidad con independencia del lugar de residencia y medidas para fijar y atraer población en la España rural."),
 ("psoe", "rural", "278", 71, "Vivienda asequible en el medio rural: alquiler para nuevos residentes y rehabilitación de viviendas vacías."),
 ("psoe", "rural", "163", 52, "Proteger y reforzar la escuela rural pública."),
 # Vox
 ("vox", "igualdad", "47", 30, "Derogar las leyes de género, que considera que criminalizan a los hombres, y aprobar normas que protejan a las mujeres víctimas de violencia, en especial de maltrato."),
 ("vox", "igualdad", "87", 46, "Más prevención, protección policial y judicial y asistencia integral a las mujeres frente a la violencia y las agresiones sexuales."),
 ("vox", "igualdad", "99", 52, "Combatir la brecha maternal: formación, promoción y reincorporación de las madres que interrumpieron su carrera."),
 ("vox", "migracion", "9", 15, "Ninguna llegada más de inmigrantes; prohibir las regularizaciones masivas y que quien entra de forma ilegal pueda regularizarse."),
 ("vox", "migracion", "11", 15, "Suprimir el arraigo y revocar las vías rápidas de acceso a la nacionalidad."),
 ("vox", "migracion", "13", 15, "Remigración: plan de retorno para extranjeros que no contribuyan o vivan de subsidios."),
 ("vox", "migracion", "18", 19, "Prioridad nacional: acceso preferente de los españoles a vivienda pública, guarderías, ayudas y servicios sociales."),
 ("vox", "discapacidad", "95", 52, "Más bonificaciones y deducciones para personas con discapacidad, fin de las barreras arquitectónicas y menos burocracia para reconocer la discapacidad."),
 ("vox", "familia", "94", 51, "Plan nacional de natalidad: los beneficios de las familias numerosas se extenderían a todas desde el primer hijo, y el Estado cotizaría por quien se dedique a cuidar a sus hijos."),
 ("vox", "educacion", "67", 41, "Libre elección de centro en todos los niveles."),
 ("vox", "educacion", "69", 41, "Derogar la LOMLOE y eliminar contenidos ideológicos ajenos a las materias."),
 ("vox", "educacion", "66", 41, "Garantizar la educación en español en todo el territorio, con currículo y evaluaciones únicas."),
 ("vox", "educacion", "70", 42, "Número máximo por aula de alumnos de otras culturas o con poco dominio del español, y aulas de nivelación aparte."),
 ("vox", "vida", "98", 52, "Defensa de la vida desde la concepción hasta la muerte natural, objeción de conciencia de sanitarios y farmacéuticos y más cuidados paliativos."),
 ("vox", "religion", "71", 42, "Prohibir el burka y el niqab en los espacios públicos y donde se presten servicios públicos."),
 ("vox", "religion", "72", 42, "Fin de los menús halal en los comedores escolares."),
 ("vox", "religion", "104", 56, "Proteger las tradiciones religiosas y populares de España."),
 ("vox", "rural", "24", 20, "Plan de inversiones para recuperar barrios, municipios y provincias abandonados."),
 # Frente Amplio (apartados sin numerar: se cita la página)
 ("fa", "igualdad", None, 38, "Al menos un 5 % del presupuesto no financiero del Estado para políticas de igualdad, y un 10 % más cada año contra las violencias machistas."),
 ("fa", "igualdad", None, 38, "Suspensión cautelar automática de las visitas del progenitor investigado por violencia machista, vicaria o sexual."),
 ("fa", "igualdad", None, 38, "Acceso prioritario a vivienda pública para mujeres víctimas de violencia machista."),
 ("fa", "lgtbi", None, 123, "Desplegar la Ley Trans y reconocer a las personas no binarias."),
 ("fa", "lgtbi", None, 123, "Atención sanitaria a las personas trans despatologizada y basada en el consentimiento informado."),
 ("fa", "lgtbi", None, 123, "Observatorio estatal y estrategia contra la LGTBQAifobia (así la llama el programa) en deporte, cultura, empleo y educación."),
 ("fa", "racismo", None, 126, "Ley integral contra el racismo y Estatuto del Pueblo Gitano."),
 ("fa", "racismo", None, 143, "Restringir las paradas de identificación policial y prohibirlas para aplicar la Ley de Extranjería."),
 ("fa", "racismo", None, 128, "Comisión parlamentaria de estudio sobre el racismo estructural."),
 ("fa", "migracion", None, 126, "Procedimiento estable y permanente de regularización en la Ley de Extranjería."),
 ("fa", "migracion", None, 126, "Derogar el rechazo en frontera."),
 ("fa", "migracion", None, 127, "Cerrar los Centros de Internamiento de Extranjeros (CIE)."),
 ("fa", "migracion", None, 128, "Derecho de voto y a ser elegidos de los migrantes residentes en las elecciones municipales."),
 ("fa", "discapacidad", None, 26, "Desarrollar plenamente la Ley 4/2026: accesibilidad universal, vida independiente y autonomía personal."),
 ("fa", "discapacidad", None, 32, "Un 60 % más de becas para alumnado con necesidades específicas, incluida la discapacidad."),
 ("fa", "familia", None, 24, "Permiso por nacimiento de 20 semanas intransferibles por progenitor y permiso parental retribuido hasta 10 semanas."),
 ("fa", "familia", None, 123, "Reconocimiento de las familias diversas."),
 ("fa", "educacion", None, 31, "Hoja de ruta para que todo el alumnado pueda ir a la pública; mientras coexistan, prohibir las cuotas obligatorias en los concertados."),
 ("fa", "educacion", None, 37, "Coeducación y educación sexoafectiva en las aulas."),
 ("fa", "educacion", None, 150, "Ningún concierto ni subvención para escuelas que segreguen por sexo o por motivos religiosos."),
 ("fa", "vida", None, 28, "Reformar el artículo 43 de la Constitución para incluir el derecho al aborto y garantizarlo en centros públicos de todas las comunidades."),
 ("fa", "vida", None, 150, "Recoge el derecho a la interrupción del embarazo, a la eutanasia y al suicidio asistido, junto a una Ley de Libertad de Conciencia."),
 ("fa", "religion", None, 150, "Revisar los Acuerdos de 1979 con la Santa Sede y suprimir la financiación pública y las exenciones fiscales de las confesiones religiosas."),
 ("fa", "religion", None, 150, "Recuperar para el Estado los bienes inmatriculados por la Iglesia católica de interés histórico-artístico."),
 ("fa", "religion", None, 150, "Ley de Libertad de Conciencia que sustituya a la Ley de Libertad Religiosa."),
 ("fa", "rural", None, 97, "II Estrategia estatal frente al Reto Demográfico y fondos europeos específicos contra la despoblación."),
 ("fa", "rural", None, 98, "Adaptar la sanidad a las zonas de baja densidad de población."),
 ("fa", "rural", None, 32, "Reforzar la escuela pública rural contra la despoblación."),
 # Coalición Canaria
 ("cc", "igualdad", "17", 10, "Financiación estatal para aplicar el Pacto de Estado contra la violencia de género en todas las islas."),
 ("cc", "racismo", "86", 19, "Combatir los discursos racistas y financiar programas de convivencia intercultural."),
 ("cc", "migracion", "82", 18, "Que el Estado y la UE asuman los costes del salvamento y la acogida en la ruta atlántica."),
 ("cc", "migracion", "83", 19, "Traslados automáticos a otras comunidades cuando un territorio de llegada supere su capacidad."),
 ("cc", "migracion", "84", 19, "Financiación estable para atender a los menores extranjeros no acompañados acogidos en Canarias."),
 ("cc", "discapacidad", "20", 10, "Que los programas estatales y europeos de vivienda, transporte y empleo en Canarias incorporen la accesibilidad."),
 ("cc", "familia", "15", 9, "Programas estatales contra la pobreza infantil mientras Canarias esté por encima de la media."),
 ("cc", "educacion", "21", 10, "Programas estatales de inversión en infraestructuras educativas."),
 # ERC (programa en catalán; resúmenes traducidos)
 ("erc", "igualdad", "88", 24, "Reformar la Ley Orgánica 1/2004 para cubrir todas las violencias machistas, incluidas la económica, la vicaria y la digital; regulación específica de la violencia vicaria y peritajes digitales gratuitos."),
 ("erc", "igualdad", "89", 24, "Ley integral contra la trata y la explotación de seres humanos, con derechos para las víctimas sea cual sea su situación administrativa y un fondo estatal que garantice sus indemnizaciones."),
 ("erc", "lgtbi", "93", 24, "Reconocer legalmente las identidades no binarias, sin requisitos patologizantes."),
 ("erc", "lgtbi", "94", 24, "Eliminar las discriminaciones en la filiación de las familias de dos madres y de las personas trans y no binarias."),
 ("erc", "lgtbi", "95", 24, "Reforzar la prohibición de las prácticas de conversión y castigar penalmente los casos graves o coercitivos."),
 ("erc", "racismo", "99", 25, "Combatir la discriminación racial y étnica en el empleo, la vivienda y el acceso a bienes y servicios, con más garantías legales y protección para quien denuncia."),
 ("erc", "racismo", "101", 25, "Perseguir las organizaciones que fomenten de forma organizada el odio, la discriminación y la violencia por origen o pertenencia étnica."),
 ("erc", "migracion", "35", 14, "Traspaso a Cataluña de todas las competencias en migración y asilo; rechaza los centros de retorno en terceros países y las deportaciones automáticas."),
 ("erc", "migracion", "51", 17, "Ampliar las vías legales y seguras de migración y protección internacional, y una nueva Ley de asilo que impida externalizar las solicitudes a terceros países."),
 ("erc", "familia", "68", 21, "Prestación universal por crianza desde 200 € por familia, más alta en territorios con mayor coste de vida, como Cataluña."),
 ("erc", "familia", "92", 24, "Equiparar las familias monoparentales a las numerosas en beneficios fiscales, sociales y laborales."),
 ("erc", "familia", "111", 26, "Ampliar los permisos parentales retribuidos."),
 ("erc", "educacion", "17", 10, "Escuela pública, laica, gratuita y de calidad, con el catalán como lengua vehicular, e impedir que el Estado imponga porcentajes lingüísticos a los centros."),
 ("erc", "educacion", "19", 11, "Destinar el 6 % del PIB a educación, con menos alumnos por aula y mejores salarios para el profesorado."),
 ("erc", "educacion", "20", 11, "Financiación estatal para que la escuela de 0 a 3 años sea pública, universal y gratuita, de forma progresiva."),
 ("erc", "vida", None, 23, "En la introducción de su apartado feminista defiende «garantizar los derechos sexuales y reproductivos», sin una medida numerada sobre el aborto ni sobre la eutanasia."),
 ("erc", "religion", "8", 8, "Aplicar el IBI a todas las propiedades de las confesiones religiosas, sin excepciones y dejando sin efecto los Acuerdos de 1979 con la Santa Sede y sus actualizaciones de 2023, así como los de 1992 con otras confesiones."),
 ("erc", "religion", "3", 8, "Suprimir del Código Penal el delito de ofensa a los sentimientos religiosos."),
 ("erc", "rural", "156", 32, "Descentralizar la PAC y los fondos europeos agrarios, pesqueros y de desarrollo rural, con recursos suficientes en el marco financiero 2028-2034."),
 ("erc", "rural", "167", 33, "Fondo estatal para municipios propietarios forestales, para financiar la gestión de los bosques y la prevención de grandes incendios."),
 ("cc", "rural", "74", 17, "Servicios, conectividad e inversiones del Estado adaptados a la doble insularidad y a los municipios rurales."),
]
# Cuando el programa del 29N no dice nada sobre un tema: anuncios de campaña y, si no hay, posiciones previas.
# (partido, tema, origen, fuentes, referencia, resumen fiel)
SOC_EXT = [
 ("pod", "igualdad", "previa", ["pod_ue24"], "programa europeo de 2024, p. 20 y 25", "Erradicar las violencias machistas y aprobar una directiva europea contra la violencia vicaria."),
 ("pod", "lgtbi", "previa", ["pod_ue24"], "programa europeo de 2024, p. 24", "Libre determinación de género, despatologización de las personas trans y reconocimiento de las personas no binarias."),
 ("pod", "racismo", "previa", ["pod_ue24"], "programa europeo de 2024, p. 25", "Estrategia integral contra el racismo estructural e institucional en la UE."),
 ("pod", "migracion", "previa", ["pod_ue24"], "programa europeo de 2024, p. 49-50", "Vías legales y seguras con reasentamiento, cierre de los centros de internamiento y supresión de Frontex."),
 ("pod", "migracion", "previa", ["pod_ue24"], "programa europeo de 2024, p. 52", "Vincular los derechos a la residencia y no a la nacionalidad, con cobertura sanitaria para todas las personas."),
 ("pod", "discapacidad", "previa", ["pod_ue24"], "programa europeo de 2024, p. 35", "Garantizar el cumplimiento de la Convención de la ONU sobre los Derechos de las Personas con Discapacidad."),
 ("pod", "familia", "previa", ["pod_ue24"], "programa europeo de 2024, p. 27", "Permisos por nacimiento iguales, intransferibles y pagados al 100 %, con un objetivo mínimo de 36 semanas."),
 ("pod", "educacion", "previa", ["pod_ue24"], "programa europeo de 2024, p. 32", "Educación gratuita de 0 a 18 años y medidas contra la segregación escolar, que vincula al peso de la concertada."),
 ("pod", "educacion", "previa", ["pod_ue24"], "programa europeo de 2024, p. 24", "Educación sexual integral para la infancia y la juventud."),
 ("pod", "vida", "previa", ["pod_ue24"], "programa europeo de 2024, p. 18 y 20", "Aborto seguro, libre y gratuito, y derecho a la eutanasia para quien padezca un sufrimiento irreversible."),
 ("pod", "religion", "previa", ["pod_ue24"], "programa europeo de 2024, p. 19-20", "Separar las confesiones religiosas de las estructuras del Estado y eliminar sus privilegios fiscales."),
 ("pod", "rural", "previa", ["pod_ue24"], "programa europeo de 2024, p. 98", "Tener en cuenta la despoblación al repartir los fondos estructurales europeos."),
 ("pp", "vida", "campaña", ["ara_feijoo", "que_feijoo"], "entrevista de Feijóo, 23-10-2026", "Reabrir el debate sobre el aborto de las chicas de 16 y 17 años y reformar la ley de eutanasia."),
 ("vox", "lgtbi", "previa", ["debate_vox23"], "programa de 2023", "Derogar la Ley Trans."),
 ("vox", "lgtbi", "previa", ["que_voxdesreg"], "plan de desregulación, junio de 2026", "Eliminar las normas de igualdad y LGTBI en las empresas, entre una decena de leyes a derogar."),
 ("erc", "discapacidad", "previa", ["nacio_erc_disc"], "proposición de ley en el Parlament de Cataluña, abril de 2025", "Subir las pensiones no contributivas por discapacidad al menos al 80 % del salario mínimo, sin contar los ingresos familiares y exentas de impuestos."),
 ("erc", "vida", "previa", ["salto_aborto"], "debate en el Congreso, 30-4-2026", "En el debate de la reforma constitucional del aborto, su diputada Pilar Vallugera expresó su «apoyo absoluto» al derecho de las mujeres a decidir sobre su propio cuerpo, aunque criticó cómo lo planteaba el Gobierno."),
 ("psoe", "religion", "previa", ["aci_psoe19", "maldita_psoe21"], "programa de 2019 y congreso de 2021", "Revisar los Acuerdos de 1979 con la Santa Sede: en 2019 proponía denunciarlos y en 2021, actualizarlos de forma pactada con la Iglesia."),
]
TEMA_IDS = [t["id"] for t in TEMAS_SOC]
MEAS_SOC = []
for i, (pid, tema, num, pag, txt) in enumerate(SOC):
    assert tema in TEMA_IDS and pid in PDFS, (pid, tema)
    MEAS_SOC.append({"id": "soc-%s-%d" % (pid, i), "partido": pid, "tema": tema,
                     "texto": txt, "num": num, "pagina": pag, "origen": "programa",
                     "url": SRC["pdf_" + pid][1] + "#page=%d" % pag, "fuentes": ["pdf_" + pid]})
for i, (pid, tema, origen, fuentes, ref, txt) in enumerate(SOC_EXT):
    assert tema in TEMA_IDS and origen in ("campaña", "previa") and all(f in SRC for f in fuentes), (pid, tema)
    MEAS_SOC.append({"id": "soc-ext-%s-%d" % (pid, i), "partido": pid, "tema": tema, "texto": txt, "num": None,
                     "pagina": None, "referencia": ref, "origen": origen, "url": SRC[fuentes[0]][1], "fuentes": fuentes})
for t in TEMAS_SOC:
    if t["sugerir_si"] is None: t.pop("sugerir_si")

PROG_PAG = {
 "pp-177": 47, "pp-178": 47, "pp-179": 47, "pp-180": 47, "pp-181": 47, "pp-170": 46, "pp-171": 46,
 "pp-145": 41, "pp-153": 43, "pp-156a": 43, "pp-156b": 43, "pp-okupa": 43, "pp-arraigo": 32, "pp-108": 34,
 "pp-114": 35, "pp-163": 44, "pp-familia": 43, "pp-mutuas": 46, "pp-220": 52, "pp-infra": 36, "pp-228": 54,
 "psoe-130": 48, "psoe-134": 49, "psoe-88": 37, "psoe-135": 48, "psoe-127": 47, "psoe-42": 27, "psoe-67": 31,
 "psoe-61": 30, "psoe-70": 30, "psoe-turis": 31, "psoe-108": 41, "psoe-87": 37, "psoe-110": 41, "psoe-becario": 42,
 "psoe-100": 40, "psoe-105": 40, "psoe-192": 56, "psoe-193": 56, "psoe-136": 49, "psoe-229": 60,
 "vox-3a": 9, "vox-3b": 9, "vox-3c": 9, "vox-3d": 9, "vox-34": 24, "vox-28": 23, "vox-35": 25, "vox-18": 19,
 "vox-remesas": 19, "vox-94": 51, "vox-laboral": 13, "vox-4": 10, "vox-8": 11,
 "fa-fortunas": 45, "fa-rentas": 46, "fa-irpf": 46, "fa-tope": 58, "fa-pension": 57, "fa-viv": 10, "fa-acum": 18,
 "fa-indef": 14, "fa-autonomos": 92, "fa-smi": 51, "fa-sanidad": 27,
 "cc-viv": 10, "cc-empleo": 12, "cc-pens": 10, "cc-transp": 17, "cc-03": 9, "cc-agua": 9,
 "erc-69a": 21, "erc-69b": 21, "erc-70": 21, "erc-74": 22, "erc-59": 19, "erc-56": 19, "erc-66": 20,
 "erc-105": 26, "erc-103": 26, "erc-106": 26, "erc-112": 26, "erc-68": 21,
}
for m in MEAS:
    pag = PROG_PAG.get(m["id"])
    if pag:
        assert m["origen"] == "programa", m["id"]
        m["pagina"] = pag
        m["fuentes"] = ["pdf_" + m["partido"]] + [f for f in m["fuentes"] if f != "pdf_" + m["partido"]]
        m["url"] = SRC["pdf_" + m["partido"]][1] + "#page=%d" % pag
    else:
        assert m["origen"] != "programa" or m["partido"] not in PDFS, ("medida de programa sin página", m["id"])

DATA = {
 "meta": {
  "titulo": "Test 29N: ¿qué medidas te afectan?",
  "url_canonica": "https://dvalverderios92.github.io/test-29n/",
  "url_datos": "https://dvalverderios92.github.io/test-29n/data/medidas.json",
  "version": "2.7.0",
  "fecha_corte": "2026-11-17",
  "eleccion": "Elecciones generales de España, 29 de noviembre de 2026",
  "aviso": "No es una recomendación de voto. Mide el efecto económico directo de las principales medidas sobre la situación de quien responde y señala los riesgos indirectos documentados (financiación, efectos sobre precios, empleo u oferta), en las dos direcciones. Aparte, y sin valorar si favorecen o perjudican, resume lo que propone cada partido sobre los temas sociales que se elijan, con la página de su programa. Muchas medidas proceden de resúmenes de prensa y se están contrastando con los programas oficiales (carpeta programas/ del repositorio); compruébalas en el original.",
  "valores": {"1": "a favor", "-1": "en contra", "0": "efecto incierto o no aplica directamente"},
  "evidencia": {"hecho": "Dato verificable (cifra, texto del programa o votación).", "consenso": "La literatura económica citada coincide en lo esencial.", "disputada": "Hay estudios serios en sentidos distintos.", "inferencia": "Razonamiento de los autores del test sin estudio específico citado.", "hecho+inferencia": "El dato es verificable; a quién afecta es una inferencia."},
  "origen": {"programa": "Programa electoral publicado para el 29N", "campaña": "Anuncio de campaña o declaración", "previa": "Posición anterior del partido (no confirmada para el 29N)"},
  "orden_partidos": "alfabético por nombre",
 },
 "condiciones": COND,
 "preguntas": QUESTIONS,
 "partidos": PARTIES,
 "riesgos": RISKS,
 "notas": NOTAS,
 "candidaturas": CANDIDATURAS,
 "medidas": MEAS,
 "temas_sociales": TEMAS_SOC,
 "medidas_sociales": MEAS_SOC,
 "fuentes": SOURCES,
}

# Validación básica
ids = {r["id"] for r in RISKS}
for m in MEAS:
    for r in m["riesgos"]: assert r["id"] in ids, (m["id"], r)
    for f in m["fuentes"]: assert f in SOURCES, (m["id"], f)
for r in RISKS:
    for f in r["fuentes"]: assert f in SOURCES, (r["id"], f)
for p in PARTIES:
    for f in p["financiacion"]["fuentes"]: assert f in SOURCES, p["id"]

def chk(c):
    if "ref" in c: assert c["ref"] in COND, c["ref"]
    for k in ("all", "any"):
        for x in c.get(k, []): chk(x)
    if "not" in c: chk(c["not"])
for m in MEAS:
    for e in m["efectos"]: chk(e["si"])
for r in RISKS:
    for e in r["exposicion"]: chk(e["si"])
for q in QUESTIONS:
    if "mostrar_si" in q: chk(q["mostrar_si"])
for t in TEMAS_SOC:
    if "sugerir_si" in t: chk(t["sugerir_si"])
for c in CANDIDATURAS:
    for f in c["fuentes"]: assert f in SOURCES, c
    chk(c["si"])

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "medidas.json")
json.dump(DATA, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(MEAS), "medidas,", len(RISKS), "riesgos")
