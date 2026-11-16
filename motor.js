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
          medidas: medidas, universales: universales, riesgos: riesgos
        };
      });
    // Matriz de riesgos: filas = riesgos, columnas = partidos, celda = nivel de exposición (o null si el partido no lo activa).
    var matriz = data.riesgos.map(function (r) {
      var fila = { id: r.id, titulo: r.titulo, evidencia: r.evidencia, niveles: {} };
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

    var notas = (data.notas || []).filter(function (n) { return evalCond(n.si, ans, named); }).map(function (n) { return n.texto; });

    return { meta: data.meta, respuestas: ans, partidos: partidos, matriz_riesgos: matriz, notas: notas };
  }

  return { evalCond: evalCond, visibleQuestions: visibleQuestions, cleanAnswers: cleanAnswers, evaluate: evaluate };
});
