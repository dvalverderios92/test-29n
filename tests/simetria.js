// Pruebas de coherencia y simetría. Uso: node tests/simetria.js
'use strict';
const path = require('path');
const T = require(path.join(__dirname, '..', 'motor.js'));
const D = require(path.join(__dirname, '..', 'data', 'medidas.json'));

let fallos = 0;
const ok = (c, msg) => { if (!c) { fallos++; console.log('✗ ' + msg); } else console.log('✓ ' + msg); };

// Generador pseudoaleatorio con semilla, para resultados reproducibles
let s = 29112026; const rnd = () => ((s = (s * 1103515245 + 12345) % 2147483648) / 2147483648);
function perfilAleatorio() {
  const a = {};
  for (const q of D.preguntas) {
    if (q.mostrar_si && !T.evalCond(q.mostrar_si, a, D.condiciones)) continue;
    const vals = q.opciones.map(o => o.valor);
    if (q.tipo === 'multi') {
      const sel = vals.filter(v => v !== q.ninguno && rnd() < 0.4);
      a[q.id] = sel.length ? sel : (q.ninguno ? [q.ninguno] : [vals[0]]);
    } else a[q.id] = vals[Math.floor(rnd() * vals.length)];
  }
  return a;
}

const N = 20000, perfiles = Array.from({ length: N }, perfilAleatorio);
const ids = D.partidos.map(p => p.id).concat((D.candidaturas || []).filter(c => c.tipo === 'fusion').map(c => c.id));
const perjudica = Object.fromEntries(ids.map(i => [i, 0]));
const riesgoAlto = Object.fromEntries(ids.map(i => [i, 0]));
const favorece = Object.fromEntries(ids.map(i => [i, 0]));
const territorial = id => { const p = D.partidos.find(x => x.id === id); return !p || !!p.ambito_si; };
const medidasVistas = new Set(), nivelesVistos = new Set();
let sinRiesgos = 0;
const vistosSolos = new Set();

for (const a of perfiles) {
  const r = T.evaluate(D, a);
  for (const p of r.partidos) {
    vistosSolos.add(p.id);
    if (p.recuento.en_contra) perjudica[p.id]++;
    if (p.recuento.a_favor) favorece[p.id]++;
    if (p.recuento.riesgos_altos || (p.recuento.riesgos_medios && territorial(p.id))) riesgoAlto[p.id]++;
    if (!p.riesgos.length) sinRiesgos++;
    p.medidas.forEach(m => medidasVistas.add(m.id + ':' + m.valor));
    p.riesgos.forEach(x => nivelesVistos.add(x.id + ':' + x.exposicion_usuario.nivel));
  }
}

// Partidos que solo concurren dentro de una candidatura conjunta (p. ej., Compromís, v2.15): se comprueban
// con sus propias medidas, evaluándolos sin las candidaturas, para que la simetría se mida partido a partido.
const soloEnFusion = D.partidos.map(p => p.id).filter(id => !vistosSolos.has(id));
if (soloEnFusion.length) {
  const Dsin = Object.assign({}, D, { candidaturas: [] });
  for (const a of perfiles) {
    for (const p of T.evaluate(Dsin, a).partidos.filter(x => soloEnFusion.includes(x.id))) {
      if (p.recuento.en_contra) perjudica[p.id]++;
      if (p.recuento.a_favor) favorece[p.id]++;
      if (p.recuento.riesgos_altos || (p.recuento.riesgos_medios && territorial(p.id))) riesgoAlto[p.id]++;
    }
  }
}
ok(soloEnFusion.every(id => (D.candidaturas || []).some(c => c.tipo === 'fusion' && c.partidos.includes(id))), `Partidos sin papeleta propia en ninguna comunidad: todos dentro de una candidatura conjunta (${soloEnFusion.join(', ') || 'ninguno'})`);

console.log(`\nPerfiles evaluados: ${N}`);
ok(sinRiesgos === 0, 'Ningún partido sale sin riesgos indirectos en ningún perfil');
for (const id of ids) {
  ok(perjudica[id] > 0, `${id}: hay perfiles a los que perjudica directamente (${perjudica[id]})`);
  ok(favorece[id] > 0, `${id}: hay perfiles a los que favorece directamente (${favorece[id]})`);
  ok(riesgoAlto[id] > 0, `${id}: hay perfiles con exposición alta a algún riesgo (media en partidos territoriales, cuyas medidas son de alcance acotado) (${riesgoAlto[id]})`);
}

// Toda medida no universal debe poder activarse
for (const m of D.medidas.filter(m => !m.universal)) {
  ok([1, -1, 0].some(v => medidasVistas.has(m.id + ':' + v)), `medida ${m.id} alcanzable`);
}

// Arquetipos opuestos: todos los partidos deben mostrar algún riesgo de exposición media o alta
const arquetipos = {
  'renta baja, inquilina, dependiente de servicios': { region: 'madrid', edad: '26-35', lab: 'asal_temp', emprender: false, ing: 1, dep_pub: 'alta', viv: 'alquiler', tens: 'si', comprar: true, otras: 0, hijos: ['h0_3'], planHijos: true, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' },
  'renta alta, casera, gran patrimonio': { region: 'madrid', edad: '41-64', lab: 'empresario', emp: true, ing: 6, dep_pub: 'baja', viv: 'propio', otras: 2, otrasTipo: ['alquila'], hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 4, ahorro: 3, bolsa: true, herencia: true, nac: 'es' },
};
for (const [nombre, a] of Object.entries(arquetipos)) {
  const r = T.evaluate(D, a);
  for (const p of r.partidos) {
    ok(p.riesgos.some(x => x.exposicion_usuario.nivel !== 'baja'), `[${nombre}] ${p.nombre}: al menos un riesgo medio o alto`);
  }
}

// Regresiones de la v2.1 (detectadas al probar el test con otro asistente de IA)
{
  const base = { region: 'canarias', empad: true, edad: '26-35', lab: 'parado', emprender: false, ing: 1, dep_pub: 'alta', viv: 'alquiler', tens: 'no', comprar: true, otras: 0, hijos: ['h3_7'], planHijos: 'ns', dep: 'personal', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const r = T.evaluate(D, base), P = id => r.partidos.find(p => p.id === id);
  const pp114 = P('pp').medidas.find(m => m.id === 'pp-114');
  ok(pp114 && pp114.valor === 0, 'Cuidado familiar: la deducción del PP por cuidados profesionales sale como incierta, no a favor');
  const r2 = T.evaluate(D, Object.assign({}, base, { dep: 'profesional' }));
  ok(r2.partidos.find(p => p.id === 'pp').medidas.find(m => m.id === 'pp-114').valor === 1, 'Cuidados profesionales: la deducción del PP sale a favor');
  ok(P('psoe').medidas.some(m => m.id === 'psoe-193' && m.valor === 0), '«No lo sé» en hijos: la Cuenta de Futuro aparece como incierta');
  const rs = P('psoe').riesgos.find(x => x.id === 'rebaja_sin_financiar');
  ok(rs && rs.exposicion_usuario.nivel === 'media', 'Escala: la deducción condicional del PSOE no dispara exposición alta a rebajas sin financiar');
  ok(P('vox').riesgos.find(x => x.id === 'rebaja_sin_financiar').exposicion_usuario.nivel === 'alta', 'Escala: las rebajas generales de Vox mantienen exposición alta');
  ok(r.notas.length >= 2, 'Notas condicionales (desempleo, IVA) incluidas en el resultado del motor');
  ok(r.matriz_riesgos.length > 0 && r.matriz_riesgos.every(f => Object.keys(f.niveles).length === r.partidos.length), 'Matriz de riesgos completa');
}

// Cobertura territorial (v2.3)
{
  const base = { edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'propio', otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const ev = region => T.evaluate(D, Object.assign({ region }, base));
  ok(ev('baleares').partidos.find(p => p.id === 'vox').medidas.some(m => m.id === 'vox-4'), 'Baleares: aparece el alivio fiscal de Vox para las islas');
  ok(!ev('madrid').partidos.some(p => p.id === 'cc'), 'Madrid: Coalición Canaria no aparece');
  ok(ev('cataluna').notas.some(n => /Junts/.test(n)), 'Cataluña: aviso de partidos territoriales no incluidos');
  ok(ev('madrid').notas.every(n => !/ERC|PNV|BNG/.test(n)), 'Madrid: sin avisos de partidos territoriales ajenos');
  ok(['andalucia', 'galicia', 'canarias'].every(r => ev(r).notas.some(n => /Candidaturas no incluidas/.test(n))), 'Aviso general de candidaturas no incluidas en todas las comunidades');
}

// ERC (v2.7): solo en Cataluña
{
  const base = { edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'propio', otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const ids = region => T.evaluate(D, Object.assign({ region }, base)).partidos.map(p => p.id);
  ok(ids('cataluna').includes('erc'), 'Cataluña: aparece ERC');
  ok(['madrid', 'valencia', 'baleares', 'aragon', 'pais_vasco'].every(r => !ids(r).includes('erc')), 'Fuera de Cataluña: ERC no tiene papeleta propia');
  const bal = T.evaluate(D, Object.assign({ region: 'baleares' }, base)).partidos.find(p => p.id === 'ara_mes');
  ok(bal && bal.partidos_test.includes('Esquerra Republicana de les Illes Balears') && !bal.partidos_test.includes('Podemos') && bal.medidas.some(m => m.de === 'Esquerra Republicana de les Illes Balears') && !ids('baleares').includes('erc'), 'Baleares: ERC concurre dentro de Ara Més-Front Ampli, sin papeleta propia');
  const val = T.evaluate(D, Object.assign({ region: 'valencia' }, base)).partidos.find(p => p.id === 'compromis');
  ok(val && val.partidos_test.includes('Esquerra Republicana del País Valencià'), 'Comunitat Valenciana: Esquerra Republicana del País Valencià concurre dentro de Compromís-Front Valencià');
  ok(['madrid', 'aragon', 'pais_vasco', 'canarias'].every(r => !T.evaluate(D, Object.assign({ region: r }, base)).partidos.some(p => (p.partidos_test || []).some(n => /ERC|Esquerra/.test(n)))), 'Fuera de Cataluña, Baleares y la Comunitat Valenciana: ninguna candidatura incluye a ERC');
}

// BNG (v2.11): solo en Galicia
{
  const base = { edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'propio', otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const ev = region => T.evaluate(D, Object.assign({ region }, base));
  ok(ev('galicia').partidos.some(p => p.id === 'bng'), 'Galicia: aparece el BNG');
  ok(['madrid', 'asturias', 'castilla_leon', 'pais_vasco', 'cataluna', 'canarias'].every(r => !ev(r).partidos.some(p => p.id === 'bng' || (p.partidos_test || []).includes('BNG'))), 'Fuera de Galicia: el BNG no aparece');
  ok(ev('galicia').notas.every(n => !/también se presenta el BNG/.test(n)), 'Galicia: ya no avisa de que el BNG no está incluido');
}

// v2.14: zona no declarada con alquileres al alza (vale para cualquier comunidad)
{
  const base = { edad: '26-35', lab: 'asal_ind', ing: 2, dep_pub: 'media', viv: 'alquiler', comprar: false, otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 0, ahorro: 0, bolsa: false, herencia: false, nac: 'es' };
  const nivel = (region, tens, partido) => { const e = T.evaluate(D, Object.assign({ region, tens }, base)); const f = e.matriz_riesgos.find(x => x.id === 'fin_topes_alquiler'); return f && f.niveles[partido]; };
  ok(['madrid', 'canarias', 'andalucia', 'galicia'].every(r => nivel(r, 'no_sube', 'pp') === 'media' && nivel(r, 'no', 'pp') === 'baja' && nivel(r, 'si', 'pp') === 'alta'), 'Zona no declarada con alquileres al alza: el fin de los topes te afecta algo, en cualquier comunidad');
  const ef = (tens, id) => { const e = T.evaluate(D, Object.assign({ region: 'madrid', tens }, base)); for (const p of e.partidos) { const m = p.medidas.find(x => x.id === id); if (m) return m.valor; } };
  ok(ef('no_sube', 'pp-145') === 0 && ef('no_sube', 'vox-28') === 0 && ef('no_sube', 'psoe-61') === 1, 'Zona no declarada con alquileres al alza: derogar es incierto; reforzar, el mismo valor que para otros inquilinos');
}

// v2.12: Podemos (en solitario o en candidatura), EH Bildu y SALF
{
  const base = { edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'propio', otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const ev = region => T.evaluate(D, Object.assign({ region }, base));
  const conPod = r => ev(r).partidos.some(p => p.id === 'pod' || (p.partidos_test || []).includes('Podemos'));
  ok(['madrid', 'andalucia', 'galicia', 'pais_vasco', 'navarra', 'ceuta', 'aragon'].every(r => ev(r).partidos.some(p => p.id === 'pod')), 'Podemos: lista propia donde la presenta (también Ceuta)');
  ok(['canarias', 'valencia'].every(r => conPod(r) && !ev(r).partidos.some(p => p.id === 'pod')), 'Podemos: dentro de la candidatura conjunta en Canarias y la Comunitat Valenciana');
  ok(['cataluna', 'baleares', 'melilla'].every(r => !conPod(r)), 'Podemos: sin medidas en Cataluña, Baleares y Melilla (no presenta lista)');
  ok(ev('pais_vasco').partidos.some(p => p.id === 'pnv') && ['navarra', 'madrid', 'cataluna', 'galicia', 'canarias'].every(r => !ev(r).partidos.some(p => p.id === 'pnv' || (p.partidos_test || []).includes('PNV'))), 'PNV: solo en el País Vasco');
  ok(ev('pais_vasco').notas.every(n => !/también se presenta el PNV/.test(n)), 'País Vasco: ya no avisa de que el PNV no está incluido');
  const val = ev('valencia').partidos.find(p => p.id === 'compromis');
  ok(val && val.partidos_test.includes('Compromís') && val.medidas.some(m => m.de === 'Compromís') && !ev('valencia').partidos.some(p => p.id === 'comp'), 'Compromís (v2.15): en la Comunitat Valenciana, dentro de Compromís-Front Valencià y con sus medidas');
  ok(['madrid', 'cataluna', 'baleares', 'canarias', 'murcia', 'aragon'].every(r => !ev(r).partidos.some(p => p.id === 'comp' || (p.partidos_test || []).includes('Compromís'))), 'Compromís: no aparece fuera de la Comunitat Valenciana');
  ok(ev('valencia').notas.every(n => !/propias de Compromís aún no/.test(n)), 'Comunitat Valenciana: ya no avisa de que las propuestas de Compromís no están incluidas');
  ok(['pais_vasco', 'navarra'].every(r => ev(r).partidos.some(p => p.id === 'bildu')) && ['madrid', 'cataluna', 'galicia'].every(r => !ev(r).partidos.some(p => p.id === 'bildu')), 'EH Bildu: solo en el País Vasco y Navarra');
  ok(!ev('cantabria').partidos.some(p => p.id === 'salf') && ['madrid', 'canarias', 'ceuta'].every(r => ev(r).partidos.some(p => p.id === 'salf')), 'SALF: en todas las comunidades salvo Cantabria');
  ok(ev('pais_vasco').notas.some(n => /SALF solo presenta lista en Álava/.test(n)) && ev('castilla_mancha').notas.some(n => /Ciudad Real/.test(n)), 'SALF: aviso donde no presenta lista en toda la comunidad');
}

// Candidaturas reales (v2.4)
{
  const base = { edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'alquiler', tens: 'no', comprar: false, otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const ids = region => T.evaluate(D, Object.assign({ region }, base)).partidos.map(p => p.id);
  const can = ids('canarias');
  ok(can.includes('upc') && !can.includes('fa') && !can.includes('pod'), 'Canarias: Unidad del Pueblo Canario sustituye a Frente Amplio y Podemos');
  ok(ids('valencia').includes('compromis') && !ids('valencia').includes('pod'), 'Comunitat Valenciana: Compromís-Front Valencià');
  ok(ids('baleares').includes('ara_mes'), 'Baleares: Ara Més-Front Ampli');
  ok(!ids('cataluna').includes('pod') && ids('cataluna').includes('fa'), 'Cataluña: sin lista de Podemos, con Comuns-Frente Amplio');
  ok(!ids('ceuta').includes('fa') && !ids('melilla').includes('fa'), 'Ceuta y Melilla: sin lista de Frente Amplio');
  ok(ids('madrid').includes('fa') && ids('madrid').includes('pod'), 'Madrid: Frente Amplio y Podemos por separado');
  const r = T.evaluate(D, Object.assign({ region: 'canarias' }, base));
  ok(r.matriz_riesgos.every(f => 'upc' in f.niveles && !('fa' in f.niveles)), 'Matriz: columnas según las candidaturas reales');
  ok(r.notas.some(n => /Unidad del Pueblo Canario/.test(n)), 'Aviso de candidatura conjunta');
}

// Derechos y protecciones (v2.6)
{
  const base = { region: 'madrid', edad: '41-64', lab: 'asal_ind', ing: 3, dep_pub: 'media', viv: 'alquiler', tens: 'no', comprar: false, otras: 0, hijos: ['ninguno'], planHijos: false, dep: 'no', patr: 1, ahorro: 1, bolsa: false, herencia: false, nac: 'es' };
  const sens = D.preguntas.filter(q => q.sensible);
  ok(sens.length >= 5 && sens.every(q => q.opciones.some(o => o.valor === 'nc' && /Prefiero no contestar/.test(o.texto))), 'Preguntas sensibles: todas con «Prefiero no contestar»');
  const temasIds = D.temas_sociales.map(t => t.id);
  ok(D.medidas_sociales.every(m => temasIds.includes(m.tema) && (m.origen === 'programa' ? m.pagina > 0 && /#page=\d+$/.test(m.url) : !m.pagina && /^https:/.test(m.url) && m.referencia)), 'Medidas sociales: del programa con página enlazada; el resto con fuente y referencia');
  ok(D.medidas.filter(m => m.origen === 'programa' && D.partidos.find(p => p.id === m.partido).programa.estado === 'publicado').every(m => m.pagina > 0 && /#page=\d+$/.test(m.url)), 'Medidas económicas del programa: todas con página enlazada al PDF oficial');
  ok(D.partidos.find(p => p.id === 'pod').programa.estado === 'publicado' && D.medidas.filter(m => m.partido === 'pod').every(m => m.origen === 'programa') && D.medidas_sociales.filter(m => m.partido === 'pod').every(m => m.origen === 'programa'), 'Podemos (v2.12): todas sus medidas salen de su programa del 29N');
  D.partidos.filter(p => p.programa.estado === 'publicado').forEach(p => ok(D.medidas_sociales.some(m => m.partido === p.id), `${p.nombre}: tiene medidas sociales del programa`));
  // Las respuestas sensibles no cambian nada del resultado económico
  const a = T.evaluate(D, Object.assign({}, base, { temas: ['ninguno'] }));
  const b = T.evaluate(D, Object.assign({}, base, { genero: 'mujer', lgtbi: 'si', etnia: 'si', disc: 'si', relig: 'si', temas: ['ninguno'] }));
  ok(JSON.stringify(a.partidos.map(p => [p.medidas.map(m => m.id + m.valor), p.riesgos.map(r => r.id + r.exposicion_usuario.nivel)])) ===
     JSON.stringify(b.partidos.map(p => [p.medidas.map(m => m.id + m.valor), p.riesgos.map(r => r.id + r.exposicion_usuario.nivel)])), 'Las respuestas sensibles no alteran medidas ni riesgos');
  ok(a.derechos.length === 0, 'Sin temas elegidos no hay bloque de derechos');
  const sg = T.suggestTopics(D, Object.assign({}, base, { genero: 'mujer', lgtbi: 'si', relig: 'nc' }));
  ok(sg.includes('igualdad') && sg.includes('lgtbi') && !sg.includes('religion'), 'Sugerencia de temas según respuestas; «Prefiero no contestar» no sugiere nada');
  const c = T.evaluate(D, Object.assign({}, base, { temas: temasIds }));
  ok(c.derechos.length === temasIds.length && c.derechos.every(t => t.partidos.length === c.partidos.length), 'Cada tema elegido lista todas las candidaturas');
  { const t = c.derechos.find(x => x.id === 'lgtbi').partidos.find(p => p.id === 'salf'); ok(t && t.medidas.length === 0, 'Un partido sin propuestas en un tema aparece igualmente, sin medidas'); }
  ok(c.derechos.every(t => t.partidos.every(p => p.medidas.every(m => !('valor' in m)))), 'Derechos y protecciones: sin valoración a favor o en contra');
  const can = T.evaluate(D, Object.assign({}, base, { region: 'canarias', empad: true, temas: ['lgtbi'] }));
  ok(can.derechos[0].partidos.find(p => p.id === 'upc').medidas.every(m => m.de), 'Candidatura conjunta: cada medida social indica de qué partido es');
}

// Fuentes
ok(Object.values(D.fuentes).every(f => /^https:\/\//.test(f.url)), 'Todas las fuentes usan https');

console.log(`\nNiveles de exposición alcanzados: ${nivelesVistos.size}`);
console.log(fallos ? `\n${fallos} fallos` : '\nTodo correcto');
process.exit(fallos ? 1 : 0);
