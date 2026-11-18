/*
 * Motor del Test 29N. Sin dependencias. Funciona en navegador (window.Test29N) y en Node (require).
 * Aplica las reglas declarativas de data/medidas.json a un objeto de respuestas.
 * Especificación de las condiciones: docs/esquema.md
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Test29N = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function has(a, k) { return Object.prototype.hasOwnProperty.call(a, k) && a[k] !== undefined && a[k] !== null; }

  function evalCond(c, ans, named) {
    if (!c) return true;
    if (c.siempre) return true;
    if (c.ref) {
      if (!named[c.ref]) throw new Error('Condición desconocida: ' + c.ref);
      return evalCond(named[c.ref], ans, named);
    }
    if (c.all) return c.all.every(function (x) { return evalCond(x, ans, named); });
    if (c.any) return c.any.some(function (x) { return evalCond(x, ans, named); });
    if (c.not) return !evalCond(c.not, ans, named);
    if (c.q) {
      if (!has(ans, c.q)) return false;           // pregunta no respondida u oculta
      var v = ans[c.q];
      if ('eq' in c) return v === c.eq;
      if ('in' in c) return c['in'].indexOf(v) !== -1;
      if ('gte' in c) return v >= c.gte;
      if ('lte' in c) return v <= c.lte;
      if ('includes' in c) return Array.isArray(v) && v.indexOf(c.includes) !== -1;
      if ('includesAny' in c) return Array.isArray(v) && c.includesAny.some(function (x) { return v.indexOf(x) !== -1; });
      throw new Error('Operador desconocido en ' + JSON.stringify(c));
    }
    throw new Error('Condición mal formada: ' + JSON.stringify(c));
  }

  function visibleQuestions(data, ans) {
    return data.preguntas.filter(function (q) { return !q.mostrar_si || evalCond(q.mostrar_si, ans, data.condiciones); });
  }

  // Elimina respuestas de preguntas que han quedado ocultas (p. ej., tras cambiar una respuesta anterior).
  function cleanAnswers(data, ans) {
    var out = {}, vis = visibleQuestions(data, ans);
    vis.forEach(function (q) { if (has(ans, q.id)) out[q.id] = ans[q.id]; });
    // segunda pasada por si una respuesta eliminada ocultaba otra
    var vis2 = visibleQuestions(data, out), res = {};
    vis2.forEach(function (q) { if (has(out, q.id)) res[q.id] = out[q.id]; });
    return res;
  }

  function firstMatch(list, ans, named) {
    for (var i = 0; i < list.length; i++) if (evalCond(list[i].si, ans, named)) return list[i];
    return null;
  }

  var NIVEL = { alta: 3, media: 2, baja: 1 };

  function evaluate(data, rawAns) {
    var ans = cleanAnswers(data, rawAns), named = data.condiciones;
    var riskById = {};
    data.riesgos.forEach(function (r) { riskById[r.id] = r; });

    var partidos = data.partidos
      .filter(function (p) { return !p.ambito_si || evalCond(p.ambito_si, ans, named); })
      .slice().sort(function (a, b) { return a.nombre.localeCompare(b.nombre, 'es'); })
      .map(function (p) {
        var medidas = [], universales = [], riesgosMap = {};
        data.medidas.filter(function (m) { return m.partido === p.id; }).forEach(function (m) {
          // Los riesgos indirectos se recogen de TODAS las medidas del partido,
          // te afecten o no directamente: ese es su sentido.
          (m.riesgos || []).forEach(function (link) {
            var rid = typeof link === 'string' ? link : link.id;
            var esc = typeof link === 'string' ? 'amplia' : (link.escala || 'amplia');
            var acc = riesgosMap[rid] = riesgosMap[rid] || { medidas: [], amplia: false };
            acc.medidas.push(m.id);
            if (esc === 'amplia') acc.amplia = true;
          });
          if (m.universal) { universales.push(m); return; }
          var e = firstMatch(m.efectos, ans, named);
          if (e) medidas.push(Object.assign({}, m, { valor: e.valor, efecto: e.texto }));
        });
        var riesgos = Object.keys(riesgosMap).map(function (rid) {
          var r = riskById[rid], acc = riesgosMap[rid], ex = Object.assign({}, firstMatch(r.exposicion, ans, named));
          // Si todas las medidas que activan el riesgo son de alcance acotado, la exposición no pasa de "media".
          if (!acc.amplia && ex.nivel === 'alta') {
            ex.nivel = 'media';
            ex.texto += ' (Rebajado a media: en este partido solo lo activan medidas de alcance acotado.)';
          }
          return Object.assign({}, r, { exposicion_usuario: ex, medidas_origen: acc.medidas, escala: acc.amplia ? 'amplia' : 'acotada' });
        }).sort(function (a, b) {
          return (NIVEL[b.exposicion_usuario.nivel] || 0) - (NIVEL[a.exposicion_usuario.nivel] || 0);
        });
        return {
          id: p.id, nombre: p.nombre, programa: p.programa, financiacion: p.financiacion,
          recuento: {
            a_favor: medidas.filter(function (x) { return x.valor > 0; }).length,
            en_contra: medidas.filter(function (x) { return x.valor < 0; }).length,
            incierto: medidas.filter(function (x) { return x.valor === 0; }).length,
            riesgos_altos: riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'alta'; }).length,
            riesgos_medios: riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'media'; }).length
          },
          medidas: medidas, universales: universales, riesgos: riesgos,
          sociales: (data.medidas_sociales || []).filter(function (m) { return m.partido === p.id; })
        };
      });
    // Candidaturas reales de la comunidad: fusiones (varios partidos en una papeleta), cambios de nombre y exclusiones.
    var avisos = [];
    (data.candidaturas || []).filter(function (c) { return evalCond(c.si, ans, named); }).forEach(function (c) {
      if (c.tipo === 'renombrar') {
        partidos.forEach(function (p) { if (p.id === c.partido) { p.nombre_partido = p.nombre; p.nombre = c.nombre; } });
        if (c.nota) avisos.push(c.nombre + ': ' + c.nota);
      } else if (c.tipo === 'excluir') {
        partidos = partidos.filter(function (p) { return p.id !== c.partido; });
        if (c.nota) avisos.push(c.nota);
      } else if (c.tipo === 'fusion') {
        var miembros = partidos.filter(function (p) { return c.partidos.indexOf(p.id) !== -1; });
        if (!miembros.length) return;
        // Nombre del partido en esa comunidad (p. ej., la federación territorial de un partido estatal)
        var nm = function (p) { return (c.alias && c.alias[p.id]) || p.nombre; };
        var rmap = {};
        miembros.forEach(function (p) {
          p.riesgos.forEach(function (r) {
            var prev = rmap[r.id];
            if (!prev || (NIVEL[r.exposicion_usuario.nivel] || 0) > (NIVEL[prev.exposicion_usuario.nivel] || 0)) {
              rmap[r.id] = Object.assign({}, r, { medidas_origen: (prev ? prev.medidas_origen : []).concat(r.medidas_origen) });
            } else prev.medidas_origen = prev.medidas_origen.concat(r.medidas_origen);
          });
        });
        var meds = [], univ = [], soc = [];
        miembros.forEach(function (p) {
          p.sociales.forEach(function (m) { soc.push(Object.assign({}, m, { de: nm(p) })); });
          p.medidas.forEach(function (m) { meds.push(Object.assign({}, m, { de: nm(p) })); });
          p.universales.forEach(function (m) { univ.push(Object.assign({}, m, { de: nm(p) })); });
        });
        var riesgos = Object.keys(rmap).map(function (k) { return rmap[k]; })
          .sort(function (a, b) { return (NIVEL[b.exposicion_usuario.nivel] || 0) - (NIVEL[a.exposicion_usuario.nivel] || 0); });
        var fusion = {
          id: c.id, nombre: c.nombre, integrantes: c.integrantes, partidos_test: miembros.map(function (p) { return nm(p); }),
          programa: { titulo: 'Candidatura conjunta', fecha: null, estado: 'coalicion', nota: c.integrantes + '. ' + c.nota },
          financiacion: { cuantifica: 'varias', resumen: miembros.map(function (p) { return nm(p) + ': ' + p.financiacion.resumen; }).join(' '),
            fuentes: [].concat.apply([], miembros.map(function (p) { return p.financiacion.fuentes; })) },
          medidas: meds, universales: univ, riesgos: riesgos, sociales: soc, fuentes_candidatura: c.fuentes
        };
        fusion.recuento = {
          a_favor: meds.filter(function (x) { return x.valor > 0; }).length,
          en_contra: meds.filter(function (x) { return x.valor < 0; }).length,
          incierto: meds.filter(function (x) { return x.valor === 0; }).length,
          riesgos_altos: riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'alta'; }).length,
          riesgos_medios: riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'media'; }).length
        };
        partidos = partidos.filter(function (p) { return c.partidos.indexOf(p.id) === -1; }).concat([fusion]);
        var nombres = miembros.map(function (p) { return nm(p); });
        avisos.push('En tu comunidad, ' + (nombres.length > 1 ? nombres.slice(0, -1).join(', ') + ' y ' + nombres[nombres.length - 1] : nombres[0]) + ' no tienen papeleta propia: concurren dentro de ' + c.nombre + ' (' + c.integrantes + '). Sus medidas aparecen juntas en esa candidatura, así que su recuento suma las de varios partidos y no es comparable con el de los demás.');
      }
    });
    partidos.sort(function (a, b) { return a.nombre.localeCompare(b.nombre, 'es'); });

    // Matriz de riesgos: filas = riesgos, columnas = partidos, celda = nivel de exposición (o null si el partido no lo activa).
    var matriz = data.riesgos.map(function (r) {
      var fila = { id: r.id, titulo: r.titulo, corto: r.corto || r.titulo, evidencia: r.evidencia, niveles: {} };
      partidos.forEach(function (p) {
        var x = p.riesgos.filter(function (y) { return y.id === r.id; })[0];
        fila.niveles[p.id] = x ? x.exposicion_usuario.nivel : null;
      });
      return fila;
    }).filter(function (f) { return Object.keys(f.niveles).some(function (k) { return f.niveles[k]; }); })
      .sort(function (a, b) {
        var m = function (f) { return Math.max.apply(null, Object.keys(f.niveles).map(function (k) { return NIVEL[f.niveles[k]] || 0; })); };
        return m(b) - m(a);
      });

    var notas = avisos.concat((data.notas || []).filter(function (n) { return evalCond(n.si, ans, named); }).map(function (n) { return n.texto; }));

    // Derechos y protecciones: solo los temas elegidos, sin valoración a favor o en contra.
    var elegidos = Array.isArray(ans.temas) ? ans.temas : [];
    var derechos = (data.temas_sociales || []).filter(function (t) { return elegidos.indexOf(t.id) !== -1; }).map(function (t) {
      return {
        id: t.id, nombre: t.nombre,
        partidos: partidos.map(function (p) {
          return { id: p.id, nombre: p.nombre, sin_programa: !!(p.programa && p.programa.estado === 'sin_programa'),
            medidas: (p.sociales || []).filter(function (m) { return m.tema === t.id; }) };
        })
      };
    });

    return { meta: data.meta, respuestas: ans, partidos: partidos, matriz_riesgos: matriz, notas: notas, derechos: derechos };
  }

  // Temas que se proponen marcados de partida, según las respuestas anteriores.
  function suggestTopics(data, ans) {
    return (data.temas_sociales || []).filter(function (t) { return t.sugerir_si && evalCond(t.sugerir_si, ans, data.condiciones); })
      .map(function (t) { return t.id; });
  }

  // Resumen en lenguaje llano de un partido: misma plantilla para todos.
  function resumenPartido(p) {
    var c = p.recuento, y = function (a) { return a.length > 1 ? a.slice(0, -1).join(', ') + ' y ' + a[a.length - 1] : (a[0] || ''); };
    var med;
    if (!c.a_favor && !c.en_contra && !c.incierto) med = 'Ninguna medida te afecta directamente.';
    else med = c.a_favor + (c.a_favor === 1 ? ' medida a tu favor, ' : ' medidas a tu favor, ') + c.en_contra + ' en contra y ' + c.incierto + (c.incierto === 1 ? ' incierta.' : ' inciertas.');
    var temas = p.medidas.filter(function (m) { return m.valor < 0; }).map(function (m) { return m.tema; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
    var contra = temas.length ? 'En contra: ' + y(temas) + '.' : '';
    var altos = p.riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'alta'; }).map(function (r) { return r.corto || r.titulo; });
    var nm = p.riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'media'; }).length;
    var rie = (altos.length ? 'Te afectan mucho: ' + y(altos) + '. ' : '') + (nm ? nm + (altos.length ? (nm === 1 ? ' riesgo más te afecta algo.' : ' riesgos más te afectan algo.') : (nm === 1 ? ' riesgo te afecta algo.' : ' riesgos te afectan algo.')) : (altos.length ? '' : 'Ningún riesgo te afecta mucho ni algo.'));
    rie = rie.trim();
    return { medidas: med, contra: contra, riesgos: rie };
  }

  return { evalCond: evalCond, visibleQuestions: visibleQuestions, cleanAnswers: cleanAnswers, evaluate: evaluate, suggestTopics: suggestTopics, resumenPartido: resumenPartido };
});
