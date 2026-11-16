# Genera data/medidas.json. ESTE ARCHIVO ES LA FUENTE DE VERDAD del Test 29N.
# Uso: python3 tools/gen_data.py   (escribe data/medidas.json)
# Después: python3 tools/build_pack.py && node tests/simetria.js
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
 {"id": "ing", "texto": "¿Cuáles son tus ingresos brutos anuales (trabajo, prestación o pensión)?", "ayuda": "Aproximado. El primer tramo equivale más o menos al salario mínimo o menos.", "opciones": [[1, "Menos de 17.000 €"], [2, "17.000 – 25.000 €"], [3, "25.000 – 40.000 €"], [4, "40.000 – 60.000 €"], [5, "60.000 – 100.000 €"], [6, "Más de 100.000 €"]]},
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
 {"id": "remesas", "texto": "¿Envías dinero a familiares en otro país?", "mostrar_si": R("extranjero"), "opciones": [[True, "Sí"], [False, "No"]]},
]
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
 "cnmc_suelo": ["CNMC: Estudio sobre la transformación urbanística del suelo para vivienda", "https://www.cnmc.es/sites/default/files/6658260.pdf", "2025"],
}
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
 {"id": "fa", "nombre": "Frente Amplio",
  "programa": {"titulo": "La vida por delante (lema)", "fecha": None, "estado": "sin_programa", "nota": "Sin programa publicado a 16-nov-2026: anuncios de campaña y posiciones previas de Sumar."},
  "financiacion": {"cuantifica": "cifras_propias", "resumen": "Da cifras propias sin verificación independiente: unos 20.000 M€/año en pensiones, financiados con un impuesto del 2 % a patrimonios de más de 1 M€, el fin del tope de cotización (7.000–8.500 M€) y la tributación mínima de grandes empresas. Estima más de 10.000 M€ con el impuesto a fortunas.", "fuentes": ["marcos_fa", "democrata_fa"]}},
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
M("pp-170", "pp", "Autónomos", "Sin cuota a la Seguridad Social el primer año como autónomo, ni el segundo si no se alcanza el SMI; bonificación del 100 % de la cotización del primer trabajador contratado.", "170", "programa", ["rankia", "democrata_pp"],
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
M("pp-okupa", "pp", "Vivienda", "Ley para desalojar viviendas okupadas en 48 horas.", None, "programa", ["brains", "democrata_pp"],
  [(R("tiene_otras_viviendas"), 1, "Más protección para tus viviendas, sobre todo si alguna está vacía.")]),
M("pp-arraigo", "pp", "Ayudas", "Criterios de arraigo (empadronamiento y cotizaciones, no solo nacionalidad) para acceder a determinadas ayudas y prestaciones. Sin umbrales publicados.", None, "programa", ["democrata_pp", "ara_prioridad"],
  [(R("arraigo_corto"), -1, "Con poco tiempo empadronado/a, podrías quedar por detrás o fuera de algunas ayudas."),
   (R("extranjero"), 0, "Con varios años de residencia y cotización probablemente no te afecte; depende de los umbrales.")], ["prioridad_legal"]),
M("pp-108", "pp", "Pensiones", "Revalorización anual de las pensiones con el IPC.", "108", "programa", ["rankia"],
  [(R("pensionista"), 1, "Mantiene el criterio actual (ya fijado por ley): tu pensión sube con los precios.")]),
M("pp-114", "pp", "Dependencia", "Deducción del 40 % de lo que se pague por atención profesional a un mayor dependiente; Pacto de Estado por la Dependencia con el 50 % de aportación estatal.", "114", "programa", ["rankia", "democrata_pp"],
  [(R("paga_cuidados_profesionales"), 1, "Recuperarías el 40 % de lo que pagas en cuidados profesionales y aumentaría la financiación estatal de la dependencia."),
   (R("cuida_dependiente"), 0, "La deducción solo cubre el gasto en cuidados profesionales, no el cuidado familiar; el aumento de la aportación estatal sí podría mejorar las prestaciones de dependencia.")], ["rebaja_sin_financiar", "gasto_sin_financiar"]),
M("pp-163", "pp", "Familia", "Escuela infantil de 0 a 3 años gratuita al final de la legislatura.", "163", "programa", ["rankia"],
  [(ANY(R("hijos_0_3"), R("quiere_hijos")), 1, "Te ahorrarías la escuela infantil (llegaría al final de la legislatura).")], ["gasto_sin_financiar"]),
M("pp-familia", "pp", "Familia", "Deducción familiar única, reembolsable y de abono mensual, que incluiría al concebido no nacido.", None, "programa", ["democrata_pp"],
  [(ANY(R("con_hijos"), R("quiere_hijos")), 1, "Cobrarías una deducción mensual por tus hijos aunque no pagues IRPF suficiente (importe no detallado).")], ["rebaja_sin_financiar"]),
M("pp-horas", "pp", "Empleo", "Elevar el límite de horas extra.", None, "campaña", ["moncloa_vp"],
  [(R("asalariado"), 0, "Puede darte más ingresos, pero también jornadas más largas: depende de tu caso."),
   (R("empleador"), 1, "Más flexibilidad para cubrir picos de trabajo.")]),
M("pp-mutuas", "pp", "Empleo", "Que las mutuas puedan dar las altas médicas.", None, "campaña", ["moncloa_vp"],
  [(R("asalariado"), 0, "Puede acortar las bajas; también resta peso al médico de la sanidad pública en esa decisión."),
   (R("empleador"), 1, "Bajas posiblemente más cortas en tu plantilla.")]),
M("pp-220", "pp", "Sanidad", "Al menos 4.500 médicos más en Atención Primaria y Plan Nacional de Salud Mental 2027-2037.", "220", "programa", ["rankia", "telemadrid"], [], ["gasto_sin_financiar"], universal=True),
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
M("psoe-42", "psoe", "Vivienda", "Movilizar el 1 % del PIB al año en vivienda y crear un parque público estatal de 100.000 viviendas (Casa 47).", "38, 42", "programa", ["rankia"],
  [(R("busca_vivienda_asequible"), 1, "Más vivienda pública de alquiler asequible a la que optar.")], ["gasto_sin_financiar"]),
M("psoe-67", "psoe", "Vivienda", "Préstamo «TU CASA» de hasta 50.000 € sin intereses para la entrada (10.000 M€).", "67", "programa", ["rankia"],
  [(R("quiere_comprar"), 1, "Te financiaría la entrada sin intereses.")], ["ayuda_demanda_precio", "gasto_sin_financiar"]),
M("psoe-61", "psoe", "Vivienda", "Contratos de alquiler más largos y congelación temporal de rentas por encima del índice en zonas tensionadas; regular el alquiler de temporada y por habitaciones.", "61-62", "programa", ["rankia", "telemadrid"],
  [(R("casero"), -1, "Limitaría las subidas y alargaría los contratos de tus viviendas en zonas tensionadas."),
   (R("inquilino_tensionada"), 1, "Más estabilidad y freno a las subidas de tu alquiler."),
   (R("inquilino"), 1, "Contratos más largos; la congelación solo aplica en zonas tensionadas.")], ["tope_alquiler_oferta"]),
M("psoe-70", "psoe", "Vivienda", "Impuesto progresivo a grandes tenedores y fondos que no destinen viviendas al alquiler asequible; impuesto a solares residenciales sin edificar.", "53, 70, 72", "programa", ["rankia"],
  [(R("gran_tenedor"), -1, "Con 10 o más viviendas podrías entrar en este impuesto.")]),
M("psoe-turis", "psoe", "Vivienda", "Bonificar a los caseros que contengan la renta y subir la tributación de los pisos turísticos.", None, "campaña", ["brains"],
  [(ALL(R("vivienda_turistica"), R("casero")), 0, "La bonificación te favorecería en tus alquileres y la subida a pisos turísticos te perjudicaría."),
   (R("vivienda_turistica"), -1, "Pagarías más por tu vivienda turística."),
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
M("psoe-becario", "psoe", "Empleo", "Aprobar el Estatuto del Becario.", None, "campaña", ["queproponen"],
  [(R("estudiante"), 1, "Más derechos si haces prácticas.")]),
M("psoe-100", "psoe", "Pensiones", "Blindar en la Constitución la revalorización de las pensiones con el IPC.", "100", "programa", ["rankia"],
  [(R("pensionista"), 1, "La subida con los precios pasaría de ley ordinaria a garantía constitucional, más difícil de cambiar.")]),
M("psoe-105", "psoe", "Familia", "Cuatro semanas de permiso parental pagadas al 100 % para menores de ocho años.", "105", "programa", ["rankia"],
  [(ALL(ANY(R("hijos_menores_8"), R("quiere_hijos")), R("trabaja")), 1, "Podrías cogerlo cobrando el sueldo íntegro.")], ["gasto_sin_financiar"]),
M("psoe-192", "psoe", "Familia", "Prestación estatal por crianza para unos 8 millones de menores.", "192", "programa", ["rankia"],
  [(R("con_hijos"), 1, "Cobrarías una ayuda por tus hijos (importe no detallado).")], ["gasto_sin_financiar"]),
M("psoe-193", "psoe", "Familia", "«Cuenta de Futuro» de 1.000 € por niño al nacer.", "193", "programa", ["rankia"],
  [(R("quiere_hijos"), 1, "Recibirías 1.000 € por cada nacimiento.")], ["gasto_sin_financiar"]),
M("psoe-136", "psoe", "Sanidad", "Financiación sanitaria pública en torno al 7 % del PIB; primera consulta psicológica gratuita en un máximo de 30 días.", "136", "programa", ["rankia", "telemadrid"], [], ["gasto_sin_financiar"], universal=True),
M("psoe-229", "psoe", "Territorio", "Nuevo modelo autonómico con 21.000 M€ adicionales y asunción parcial de 83.000 M€ de deuda autonómica; 19.000 M€ para ferrocarril hasta 2030.", "128, 229, 231", "programa", ["rankia"], [], ["gasto_sin_financiar"], universal=True),

# ===== VOX =====
M("vox-3a", "vox", "IRPF", "Rebajar y simplificar el IRPF, con tipos más bajos según el número de hijos. El programa no concreta tipos ni tramos.", "3", "programa", ["rankia", "democrata_vox"],
  [(ALL(R("paga_irpf"), R("con_hijos")), 1, "Pagarías menos IRPF, y más rebaja por tener hijos. Cuánto, no se sabe."),
   (R("paga_irpf"), 1, "Pagarías menos IRPF. Cuánto, no se sabe: el programa no da tipos."),
   (ALL(R("trabaja"), R("renta_smi")), 0, "Con ingresos cercanos al SMI apenas notarías diferencia.")], ["irpf_reparto", "rebaja_sin_financiar"]),
M("vox-3b", "vox", "IVA", "Rebajar los tipos general y reducido del IVA, sobre todo en productos de primera necesidad.", "3", "programa", ["rankia", "democrata_vox"],
  [(R("sin_iva"), 0, IGIC), (ALWAYS, 1, "Abarataría tu compra (sin tipos concretos).")], ["iva_poco_focalizado", "rebaja_sin_financiar"]),
M("vox-3c", "vox", "Empresa", "Rebajar el Impuesto de Sociedades.", "3", "programa", ["rankia"],
  [(R("empresario"), 1, "Tu sociedad pagaría menos (sin tipo concreto).")], ["rebaja_sin_financiar"]),
M("vox-3d", "vox", "Autónomos", "Cuota cero para autónomos que no alcancen el SMI y cuota progresiva desde 50 € por encima.", "3", "programa", ["rankia", "vox_web"],
  [(ALL(R("autonomo_o_futuro"), R("renta_baja")), 1, "Con tus ingresos pagarías poco o nada de cuota."),
   (R("autonomo_o_futuro"), 0, "Por encima del SMI la cuota sería progresiva; si pagas más o menos que hoy depende de una escala no publicada.")], ["rebaja_sin_financiar"]),
M("vox-34", "vox", "Vivienda", "Primera vivienda de una familia española: IVA del 0 % si es nueva y bonificación del 100 % del ITP si es de segunda mano.", "34", "programa", ["rankia", "vox_web"],
  [(ALL(R("quiere_comprar"), R("extranjero")), 0, "La web del partido habla de «familia española»: no está claro que te aplique."),
   (ALL(R("quiere_comprar"), R("sin_iva")), 1, "Te ahorrarías el ITP si compras usada; el IVA no aplica en tu territorio."),
   (R("quiere_comprar"), 1, "Te ahorrarías el impuesto de la compra.")], ["ayuda_demanda_precio", "rebaja_sin_financiar"]),
M("vox-28", "vox", "Vivienda", "Derogar la Ley de Vivienda y reformar la Ley del Suelo; desalojo de okupas en menos de 24 horas.", "28-32", "programa", ["rankia"],
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
M("vox-7", "vox", "Pensiones", "Vincular las pensiones a productividad y natalidad y avanzar hacia un modelo mixto con capitalización. Sin financiación detallada.", "7", "programa", ["rankia", "moncloa_vp"],
  [(R("pensionista"), 0, "Sustituiría la garantía de subida con el IPC por otros criterios sin fórmula publicada."),
   (ALL(R("trabaja"), R("menor_40")), 0, "Parte de tu futura pensión podría depender de la capitalización; no hay detalles.")], ["pensiones_transicion"]),
M("vox-94", "vox", "Familia", "Plan de natalidad y cotizaciones pagadas por el Estado a quienes cuidan hijos.", "94", "programa", ["rankia"],
  [(ANY(R("con_hijos"), R("quiere_hijos")), 1, "El Estado pagaría tus cotizaciones durante el tiempo de cuidado.")], ["gasto_sin_financiar"]),
M("vox-laboral", "vox", "Empleo", "Derogar la legislación laboral del Gobierno (incluida la reforma laboral de 2021).", None, "programa", ["telemadrid", "rankia"],
  [(Q("lab", eq="asal_temp"), 0, "La reforma de 2021 limitó los contratos temporales; no se detalla qué la sustituiría. Con contrato temporal o fijo discontinuo, te toca de lleno."),
   (R("asalariado"), 0, "La reforma de 2021 limitó los contratos temporales; no se detalla qué la sustituiría."),
   (R("empleador"), 0, "Podría darte más flexibilidad de contratación; depende de la norma que la sustituya.")]),
M("vox-sucesiones", "vox", "Patrimonio", "Suprimir los impuestos de Patrimonio, Sucesiones y Donaciones y la plusvalía municipal.", None, "previa", ["pe_vox", "brains"],
  [(ANY(Q("patr", gte=2), R("herencia")), 1, "Pagarías menos al heredar, donar o por tu patrimonio (depende de lo que ya bonifique tu comunidad).")], ["rebaja_sin_financiar"]),
M("vox-4", "vox", "Territorio", "Alivio fiscal para Canarias, Baleares y zonas en riesgo de despoblación.", "4, 6", "programa", ["rankia", "vox_web"],
  [(ANY(R("canarias"), R("baleares")), 0, "Te afectaría, pero los resúmenes no detallan en qué consiste.")], ["rebaja_sin_financiar"]),
M("vox-8", "vox", "Energía", "Rebajar los impuestos de la electricidad y mantener las nucleares, con estudios para nuevas centrales.", "8", "programa", ["rankia"], [], ["rebaja_sin_financiar"], universal=True),

# ===== FRENTE AMPLIO =====
M("fa-fortunas", "fa", "Patrimonio", "Impuesto a patrimonios de más de 1 millón de euros, con tipos del 2 % y el 3 %.", None, "campaña", ["democrata_fa", "marcos_fa"],
  [(R("patrimonio_mas_1M"), -1, "Con tu patrimonio pagarías este impuesto."),
   (R("patrimonio_300k_1M"), 0, "Estás cerca del umbral: depende de cómo se compute la vivienda habitual (sin detalle).")]),
M("fa-rentas", "fa", "IRPF", "«Contrarreforma fiscal» para que las rentas más altas aporten más; tributación mínima efectiva de grandes empresas. Sin cifras.", None, "campaña", ["democrata_fa", "marcos_fa"],
  [(ANY(R("renta_alta"), R("ahorro_alto")), -1, "Con tus ingresos es probable que pagues más (tramos no publicados).")]),
M("fa-tope", "fa", "Cotizaciones", "Eliminar progresivamente el tope máximo de cotización a la Seguridad Social.", None, "campaña", ["marcos_fa"],
  [(ALL(R("asalariado"), R("renta_alta")), -1, "Cotizarías por todo tu salario, no solo hasta la base máxima (unos 60.000 €)."),
   (ALL(R("empleador"), Q("ing", gte=4)), -1, "Subiría el coste de tus empleados con sueldos altos.")]),
M("fa-pension", "fa", "Pensiones", "Ninguna pensión por debajo del salario mínimo y jubilación como máximo a los 65 años (coste estimado por el partido: unos 20.000 M€/año).", None, "campaña", ["marcos_fa"],
  [(ALL(R("pensionista"), R("renta_smi")), 1, "Tu pensión subiría hasta el salario mínimo."),
   (R("pensionista"), 0, "Tu pensión ya supera el mínimo; no cambia directamente."),
   (ALL(R("trabaja"), ANY(R("edad_41_64"), Q("edad", eq="36-40"))), 1, "Podrías jubilarte a los 65 sin penalización.")], ["gasto_sin_financiar"]),
M("fa-viv", "fa", "Vivienda", "Ley para expropiar viviendas a fondos de inversión (por fases: más de 1.000, más de 700 y más de 50 viviendas), no a particulares; 1 % del PIB para el parque público.", None, "campaña", ["democrata_fa", "marcos_fa"],
  [(R("gran_tenedor"), 0, "Afecta a fondos y empresas, no a particulares; si tus viviendas están en una sociedad, podrías estar afectado."),
   (R("busca_vivienda_asequible"), 1, "Más vivienda pública de alquiler asequible a la que optar.")], ["expropiacion_plazos", "gasto_sin_financiar"]),
M("fa-acum", "fa", "Vivienda", "Impuesto del 10 % a la acumulación de viviendas (umbral no publicado).", None, "campaña", ["telemadrid"],
  [(R("varias_viviendas"), -1, "Con varias viviendas podrías pagarlo (umbral no publicado)."),
   (R("tiene_otras_viviendas"), 0, "No está claro desde cuántas viviendas se aplicaría.")]),
M("fa-indef", "fa", "Vivienda", "Contratos de alquiler indefinidos; legalizar las huelgas de alquileres y reconocer a los sindicatos de inquilinas.", None, "campaña", ["marcos_fa"],
  [(R("casero"), -1, "Tus inquilinos podrían quedarse indefinidamente y organizarse para negociar la renta."),
   (R("inquilino"), 1, "No tendrías que irte al acabar el contrato y tendrías más fuerza para negociar.")], ["tope_alquiler_oferta"]),
M("fa-autonomos", "fa", "Autónomos", "Bonificar las cuotas de autónomos con bajos ingresos y simplificar trámites.", None, "campaña", ["telemadrid"],
  [(ALL(R("autonomo_o_futuro"), R("renta_baja")), 1, "Pagarías menos cuota."),
   (R("autonomo_o_futuro"), 0, "Por tus ingresos quizá no entres en la bonificación (umbral no publicado).")]),
M("fa-smi", "fa", "Empleo", "Volver a subir el salario mínimo (sin cifra) y semana laboral de 32 horas.", None, "campaña", ["democrata_fa", "marcos_fa"],
  [(R("asalariado"), 1, "Menos horas por el mismo sueldo y, si cobras cerca del mínimo, más salario."),
   (R("empleador"), -1, "Más coste laboral por hora.")], ["smi_empleo", "jornada_ley"]),
M("fa-sanidad", "fa", "Sanidad", "Incluir gafas, audífonos, dentista y atención integral a la menopausia en la sanidad pública.", None, "campaña", ["telemadrid", "marcos_fa"], [], ["gasto_sin_financiar"], universal=True),

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
M("cc-empad", "cc", "Vivienda", "Exigir diez años de empadronamiento en Canarias para comprar vivienda (quince si no son continuos) y limitar a dos las viviendas por persona en municipios distintos.", None, "programa", ["pe_cc"],
  [(ALL(R("quiere_comprar"), R("empadronado_10_canarias")), 1, "tendrías menos competencia de compradores de fuera."),
   (R("quiere_comprar"), -1, "No podrías comprar en Canarias hasta cumplir los años de empadronamiento."),
   (R("varias_viviendas"), -1, "Limitaría tus futuras compras de vivienda.")]),
M("cc-alq", "cc", "Vivienda", "Rechazar la renovación automática de alquileres y proteger a los pequeños propietarios.", None, "programa", ["pe_cc"],
  [(R("pequeno_casero"), 1, "Mantienes el control sobre tus contratos."),
   (R("inquilino"), 0, "No tendrías renovación automática del contrato; CC apuesta por ayudas y más oferta.")]),
M("cc-viv", "cc", "Vivienda", "Financiación estatal para vivienda pública, ayudas a la compra y al alquiler, y apoyo a la emancipación juvenil.", None, "programa", ["pe_cc", "eldiario_cc"],
  [(ANY(R("busca_vivienda_asequible"), R("quiere_comprar")), 1, "Más ayudas y vivienda pública a tu alcance (sin cifras).")], ["ayuda_demanda_precio", "gasto_sin_financiar"]),
M("cc-empleo", "cc", "Empleo", "Mantener el Plan Integral de Empleo de Canarias y un plan para menores de 35 años; bonificar cotizaciones a empresas que suban salarios por encima del convenio.", None, "programa", ["pe_cc"],
  [(ANY(R("parado"), ALL(R("joven_18_35"), NOT(R("trabaja")))), 1, "Más recursos de empleo para ti."),
   (R("empleador"), 1, "Pagarías menos cotizaciones si subes sueldos.")], ["gasto_sin_financiar"]),
M("cc-pens", "cc", "Pensiones", "Pensiones según el coste de la vida (Pacto de Toledo) y que las no contributivas sumen el complemento canario sin perder ingresos; mejor acceso al IMV.", None, "programa", ["pe_cc"],
  [(ALL(R("pensionista"), R("pension_no_contributiva")), 1, "Cobrarías el complemento canario sin que te descuenten de la pensión."),
   (R("pensionista"), 1, "Tu pensión seguiría al coste de la vida."),
   (ALL(R("renta_smi"), Q("lab", **{"in": ["parado", "otro", "estudiante"]})), 1, "Te sería más fácil acceder al IMV si cumples los requisitos.")]),
M("cc-transp", "cc", "Transporte", "Consolidar el descuento de residente del 75 % y actualizar las ayudas al transporte de mercancías.", None, "programa", ["pe_cc"],
  [(R("canarias"), 1, "Mantienes el descuento en vuelos y barcos; la cesta de la compra podría abaratarse.")]),
M("cc-03", "cc", "Familia", "Educación infantil de 0 a 3 años gratuita, con plazas públicas suficientes.", None, "programa", ["pe_cc"],
  [(ANY(R("hijos_0_3"), R("quiere_hijos")), 1, "Te ahorrarías la escuela infantil.")], ["gasto_sin_financiar"]),
M("cc-agua", "cc", "Agua y sanidad", "Que el Estado compense el precio del agua desalada hasta igualarlo con la Península y cubra el sobrecoste sanitario de la insularidad.", None, "programa", ["pe_cc"], [], ["gasto_sin_financiar"], universal=True),
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
 ("pp-familia","rebaja_sin_financiar"),("psoe-88","rebaja_sin_financiar"),
 ("vox-3d","rebaja_sin_financiar"),("vox-34","rebaja_sin_financiar"),("vox-4","rebaja_sin_financiar"),
 ("psoe-134","gasto_sin_financiar"),("psoe-105","gasto_sin_financiar"),("psoe-193","gasto_sin_financiar"),
 ("vox-94","gasto_sin_financiar"),("cc-viv","gasto_sin_financiar"),("cc-empleo","gasto_sin_financiar"),
 ("cc-03","gasto_sin_financiar"),("cc-agua","gasto_sin_financiar"),
}
for m in MEAS:
    m["riesgos"] = [{"id": r, "escala": "acotada" if (m["id"], r) in ACOTADA else "amplia"} for r in m["riesgos"]]

NOTAS = [
 {"si": R("parado"), "texto": "Desempleo: las fuentes consultadas no recogen medidas concretas de los partidos estatales sobre la prestación por desempleo. Si es tu prioridad, revisa ese capítulo en cada programa."},
 {"si": R("sin_iva"), "texto": "IVA: en tu territorio no se aplica (Canarias: IGIC; Ceuta y Melilla: IPSI). Las rebajas de IVA aparecen como inciertas para ti, aunque su coste en la recaudación estatal sí cuenta en los riesgos."},
 {"si": R("cuida_dependiente"), "texto": "Dependencia: comprueba si cada medida cubre el cuidado familiar o solo el gasto en cuidados profesionales."},
 {"si": Q("region", eq="cataluna"), "texto": "Partidos no incluidos: en Cataluña también se presentan ERC (programa publicado el 5-nov) y Junts (sin programa a la fecha de corte). Este test aún no recoge sus medidas; consulta sus programas."},
 {"si": Q("region", eq="pais_vasco"), "texto": "Partidos no incluidos: en el País Vasco también se presentan PNV (programa publicado en noviembre) y EH Bildu (sin programa a la fecha de corte). Este test aún no recoge sus medidas; consulta sus programas."},
 {"si": Q("region", eq="navarra"), "texto": "Partidos no incluidos: en Navarra también se presenta EH Bildu (sin programa a la fecha de corte), entre otras candidaturas territoriales. Este test aún no recoge sus medidas."},
 {"si": Q("region", eq="galicia"), "texto": "Partidos no incluidos: en Galicia también se presenta el BNG (programa publicado el 3-nov). Este test aún no recoge sus medidas; consulta su programa."},
 {"si": Q("region", eq="valencia"), "texto": "Partidos no incluidos: en la Comunitat Valenciana también se presenta Compromís–Front Valencià. Este test aún no recoge sus medidas; consulta su programa."},
 {"si": ALWAYS, "texto": "Candidaturas no incluidas: además de los partidos territoriales, se presentan otras candidaturas, como Se Acabó La Fiesta (SALF), cuyo «Contrato Electoral 29N» aún no se ha incorporado. Este test recoge los partidos con medidas detalladas en las fuentes consultadas."},
]
DATA = {
 "meta": {
  "titulo": "Test 29N: ¿qué medidas te afectan?",
  "url_canonica": "https://dvalverderios92.github.io/test-29n/",
  "url_datos": "https://dvalverderios92.github.io/test-29n/data/medidas.json",
  "gem_url": "https://gemini.google.com/gem/1jjjGM5yY05jS_uJGa-R4ZZlTcCUx4aVH?usp=sharing",
  "version": "2.3.0",
  "fecha_corte": "2026-11-16",
  "eleccion": "Elecciones generales de España, 29 de noviembre de 2026",
  "aviso": "No es una recomendación de voto. Mide el efecto económico directo de las principales medidas sobre la situación de quien responde y señala los riesgos indirectos documentados (financiación, efectos sobre precios, empleo u oferta), en las dos direcciones. Las medidas proceden de resúmenes de prensa que citan los programas; compruébalas en el original.",
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
 "medidas": MEAS,
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

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "medidas.json")
json.dump(DATA, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(MEAS), "medidas,", len(RISKS), "riesgos")
