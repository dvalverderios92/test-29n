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

for (const a of perfiles) {
  const r = T.evaluate(D, a);
  for (const p of r.partidos) {
    if (p.recuento.en_contra) perjudica[p.id]++;
    if (p.recuento.a_favor) favorece[p.id]++;
    if (p.recuento.riesgos_altos || (p.recuento.riesgos_medios && territorial(p.id))) riesgoAlto[p.id]++;
    if (!p.riesgos.length) sinRiesgos++;
    p.medidas.forEach(m => medidasVistas.add(m.id + ':' + m.valor));
    p.riesgos.forEach(x => nivelesVistos.add(x.id + ':' + x.exposicion_usuario.nivel));
  }
}

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
  ok(ev('cataluna').notas.some(n => /ERC/.test(n)), 'Cataluña: aviso de partidos territoriales no incluidos');
  ok(ev('madrid').notas.every(n => !/ERC|PNV|BNG/.test(n)), 'Madrid: sin avisos de partidos territoriales ajenos');
  ok(['andalucia', 'galicia', 'canarias'].every(r => ev(r).notas.some(n => /SALF/.test(n))), 'Aviso general de candidaturas no incluidas en todas las comunidades');
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

// Fuentes
ok(Object.values(D.fuentes).every(f => /^https:\/\//.test(f.url)), 'Todas las fuentes usan https');

console.log(`\nNiveles de exposición alcanzados: ${nivelesVistos.size}`);
console.log(fallos ? `\n${fallos} fallos` : '\nTodo correcto');
process.exit(fallos ? 1 : 0);
