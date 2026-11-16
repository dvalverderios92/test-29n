/*
 * Exporta el resultado del Test 29N como presentación PDF (16:9) en el navegador.
 * Usa jsPDF (cargado bajo demanda desde cdnjs) y las fuentes estándar del PDF (Helvetica).
 * Identidad: papeleta (papel blanco, tinta, casillas). Sin colores de partido.
 */
(function (root) {
  'use strict';
  var JSPDF_URL = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
  var W = 720, H = 405, M = 36;                       // puntos: 10 × 5,625 pulgadas
  var TINTA = [31, 26, 18], TINTA2 = [91, 79, 60], PAPEL = [255, 253, 246], SEPIA = [228, 211, 174], LINEA = [185, 162, 116];

  // Caracteres que Helvetica (WinAnsi) no tiene
  function limpio(s) {
    return String(s == null ? '' : s)
      .replace(/[−‐‑]/g, '-').replace(/→/g, '->').replace(/[≤]/g, '<=').replace(/[≥]/g, '>=')
      .replace(/ /g, ' ').replace(/[^\x09\x0a\x0d\x20-\x7e -ÿ€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ]/g, '');
  }

  function cargar() {
    return new Promise(function (ok, ko) {
      if (root.jspdf && root.jspdf.jsPDF) return ok(root.jspdf.jsPDF);
      var s = document.createElement('script');
      s.src = JSPDF_URL; s.async = true;
      s.onload = function () { root.jspdf && root.jspdf.jsPDF ? ok(root.jspdf.jsPDF) : ko(new Error('jsPDF no disponible')); };
      s.onerror = function () { ko(new Error('No se pudo cargar la librería de PDF')); };
      document.head.appendChild(s);
    });
  }

  function generar(D, R, jsPDF) {
    var doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: [W, H], compress: true });
    doc.setProperties({ title: 'Test 29N: lo que te juegas', subject: 'Resultado personal del Test 29N', creator: 'Test 29N' });
    var primera = true;
    var fecha = D.meta.fecha_corte.split('-').reverse().join('/');

    // ---------- utilidades ----------
    function color(c, tipo) { if (tipo === 'f') doc.setFillColor(c[0], c[1], c[2]); else if (tipo === 'd') doc.setDrawColor(c[0], c[1], c[2]); else doc.setTextColor(c[0], c[1], c[2]); }
    function fuente(tam, negrita) { doc.setFont('helvetica', negrita ? 'bold' : 'normal'); doc.setFontSize(tam); }
    function lineas(txt, ancho, tam, negrita) { fuente(tam, negrita); return doc.splitTextToSize(limpio(txt), ancho); }
    function escribir(ls, x, y, tam, negrita, col) { fuente(tam, negrita); color(col || TINTA); doc.text(ls, x, y, { baseline: 'top', lineHeightFactor: 1.25 }); return y + ls.length * tam * 1.25; }
    function nueva(oscura) {
      if (!primera) doc.addPage([W, H], 'landscape'); primera = false;
      color(oscura ? TINTA : PAPEL, 'f'); doc.rect(0, 0, W, H, 'F');
    }
    function titulo(t, sub) {
      var y = escribir(lineas(t, W - 2 * M, 24, true), M, M - 4, 24, true);
      if (sub) y = escribir(lineas(sub, W - 2 * M, 12), M, y + 4, 12, false, TINTA2);
      return y + 14;
    }
    // Casillas (motivo de la papeleta)
    function casilla(x, y, s, tipo) {
      doc.setLineWidth(1.6); color(TINTA, 'd'); doc.setLineDashPattern([], 0);
      if (tipo === 'alta' || tipo === 'menos') { color(TINTA, 'f'); doc.rect(x, y, s, s, 'FD'); }
      else if (tipo === 'inc') { doc.setLineDashPattern([2, 2], 0); doc.rect(x, y, s, s, 'S'); doc.setLineDashPattern([], 0); }
      else doc.rect(x, y, s, s, 'S');
      if (tipo === 'media') {                       // trama diagonal dentro de la casilla
        doc.setLineWidth(1); var p = 4;
        for (var k = p; k < 2 * s; k += p) {
          var ax = x + Math.max(0, k - s), ay = y + Math.min(k, s), bx = x + Math.min(k, s), by = y + Math.max(0, k - s);
          doc.line(ax, ay, bx, by);
        }
      }
      if (tipo === 'x') { doc.setLineWidth(2.2); doc.line(x + s * .2, y + s * .2, x + s * .8, y + s * .8); doc.line(x + s * .8, y + s * .2, x + s * .2, y + s * .8); }
      if (tipo === 'mas') { doc.setLineWidth(2); doc.line(x + s * .25, y + s / 2, x + s * .75, y + s / 2); doc.line(x + s / 2, y + s * .25, x + s / 2, y + s * .75); }
      if (tipo === 'menos') { doc.setLineWidth(2); color(PAPEL, 'd'); doc.line(x + s * .25, y + s / 2, x + s * .75, y + s / 2); }
      if (tipo === 'inc') { fuente(s * .7, true); color(TINTA); doc.text('?', x + s / 2, y + s / 2, { align: 'center', baseline: 'middle' }); }
    }
    var NIVEL = { alta: 'Exposición alta', media: 'Exposición media', baja: 'Exposición baja' };
    var EVID = { hecho: 'Hecho', 'hecho+inferencia': 'Hecho + inferencia', consenso: 'Consenso', disputada: 'Evidencia disputada', inferencia: 'Inferencia' };
    var FIN = { varias: 'Según cada partido', no: 'No cuantifica su programa', cifras_propias: 'Cifras propias sin verificar', fuera_del_programa: 'Cifras fuera del programa', si: 'Cuantifica su programa' };

    // ---------- 1. Portada ----------
    nueva(true);
    escribir(lineas('Elecciones generales del 29 de noviembre de 2026', 420, 13, true), M, M, 13, true, SEPIA);
    var y = escribir(lineas('Lo que te juegas el 29N', 430, 44, true), M, 90, 44, true, PAPEL);
    var perfil = ['region', 'lab', 'viv', 'ing'].map(function (id) {
      var q = D.preguntas.filter(function (x) { return x.id === id; })[0], v = R.respuestas[id];
      var o = q && q.opciones.filter(function (x) { return x.valor === v; })[0];
      return o ? o.texto : null;
    }).filter(Boolean);
    y = escribir(lineas('Tu perfil: ' + perfil.join('; ') + '.', 430, 13), M, y + 18, 13, false, SEPIA);
    escribir(lineas('Datos a ' + fecha + ', versión ' + D.meta.version + '. No es una recomendación de voto: no hay ranking ni puntuación.', 430, 11), M, H - M - 28, 11, false, SEPIA);
    // gran casilla con X
    color(PAPEL, 'd'); doc.setLineWidth(5); doc.rect(W - M - 170, 95, 170, 170, 'S');
    doc.setLineWidth(9); doc.line(W - M - 140, 125, W - M - 30, 235); doc.line(W - M - 30, 125, W - M - 140, 235);

    // ---------- 2. Cómo leerlo ----------
    nueva(false);
    y = titulo('Cómo leer este resultado', 'Tres capas que no se suman entre sí. Cada dato separa el hecho (lo que propone el partido) de la inferencia (cómo te afecta).');
    var capas = [
      ['Los riesgos que corres', 'Lo que una medida puede provocar aunque no te toque: menos recaudación, gasto sin financiar, precios, empleo, oferta.'],
      ['Lo que ganas o pierdes', 'Las medidas que te favorecen, te perjudican o tienen un efecto incierto en tu bolsillo.'],
      ['Quién dice cómo pagarlo', 'Si cada partido cuantifica su programa y de dónde sale el dinero.']];
    var colW = (W - 2 * M - 40) / 3;
    capas.forEach(function (c, i) {
      var x = M + i * (colW + 20);
      casilla(x, y, 22, 'x');
      var yy = escribir(lineas(c[0], colW, 15, true), x, y + 32, 15, true);
      escribir(lineas(c[1], colW, 12), x, yy + 4, 12, false, TINTA2);
    });
    var yl = H - M - 112;
    color(SEPIA, 'f'); doc.roundedRect(M, yl, W - 2 * M, 104, 6, 6, 'F');
    [['Exposición a cada riesgo', [['alta', 'Alta'], ['media', 'Media'], ['baja', 'Baja']]],
     ['Efecto de cada medida', [['mas', 'A tu favor'], ['menos', 'En tu contra'], ['inc', 'Incierto']]]].forEach(function (g, f) {
      var fy = yl + 14 + f * 32;
      escribir([g[0]], M + 14, fy + 3, 12, true);
      g[1].forEach(function (it, i) { var x = M + 220 + i * 130; casilla(x, fy, 18, it[0]); escribir([it[1]], x + 26, fy + 3, 12, false); });
    });
    escribir(lineas('Partidos en orden alfabético. Detalle y fuentes en ' + D.meta.url_canonica, W - 2 * M - 28, 11), M + 14, yl + 80, 11, false, TINTA2);

    // ---------- 3. Matriz de riesgos ----------
    var filas = R.matriz_riesgos, porPag = 5, ab = { cc: 'CC', fa: 'FA', pod: 'Podemos', pp: 'PP', psoe: 'PSOE', vox: 'Vox', upc: 'UPC', compromis: 'Compromís', ara_mes: 'Ara Més' };
    for (var ini = 0; ini < filas.length; ini += porPag) {
      nueva(false);
      y = titulo('Tus riesgos indirectos, comparados' + (ini ? ' (continuación)' : ''), 'Cuánto te expone tu situación a cada riesgo, según las medidas de cada partido. Raya: el partido no lo activa.');
      var c0 = 330, cw = (W - 2 * M - c0) / R.partidos.length;
      fuente(12, true); color(TINTA);
      R.partidos.forEach(function (p, j) { doc.text(limpio(ab[p.id] || p.nombre), M + c0 + j * cw + cw / 2, y, { align: 'center', baseline: 'top' }); });
      y += 22; color(TINTA, 'd'); doc.setLineWidth(1.6); doc.line(M, y - 4, W - M, y - 4);
      var alto = (H - M - 14 - y) / porPag;
      filas.slice(ini, ini + porPag).forEach(function (f, k) {
        var fy = y + k * alto;
        var ls = lineas(f.titulo, c0 - 16, 12, true).slice(0, 2);
        var yy = escribir(ls, M, fy + Math.max(6, (alto - ls.length * 15 - 13) / 2), 12, true);
        escribir([limpio(EVID[f.evidencia] || f.evidencia)], M, yy + 1, 10, false, TINTA2);
        R.partidos.forEach(function (p, j) {
          var n = f.niveles[p.id], cx = M + c0 + j * cw + cw / 2;
          if (n) casilla(cx - 9, fy + alto / 2 - 9, 18, n);
          else { color(LINEA, 'd'); doc.setLineWidth(1.4); doc.line(cx - 7, fy + alto / 2, cx + 7, fy + alto / 2); }
        });
        color(LINEA, 'd'); doc.setLineWidth(.6); doc.line(M, fy + alto, W - M, fy + alto);
      });
    }

    // ---------- 4. Por partido: riesgos y medidas ----------
    var LIM = H - M;
    function lista(tituloBase, sub, elementos, resumen, pie) {
      var cont = 0;
      function pagina() { nueva(false); return titulo(tituloBase + (cont++ ? ' (continuación)' : ''), cont === 1 ? sub : null); }
      var pieL = pie ? lineas(pie, W - 2 * M - 28, 11) : [], pieH = pie ? pieL.length * 13.75 + 16 : 0;
      var resL = resumen ? lineas(resumen, W - 2 * M - 34, 12) : [], resH = resumen ? resL.length * 15 + 10 : 0;
      var yy = pagina();
      if (!elementos.length && !resumen) yy = escribir(lineas('Ninguna medida recogida te afecta directamente según tus respuestas.', W - 2 * M, 14), M, yy, 14, false, TINTA2) + 10;
      elementos.forEach(function (e, k) {
        var cab = lineas(e.cab, W - 2 * M - 34, 14, true), det = lineas(e.det, W - 2 * M - 34, 10.5);
        var alto = cab.length * 17.5 + det.length * 13.125 + 8;
        var reserva = (k === elementos.length - 1) ? resH + pieH : 0;
        if (yy + alto + reserva > LIM && yy + alto > LIM - pieH) yy = pagina();
        else if (yy + alto > LIM) yy = pagina();
        casilla(M, yy + 1, 16, e.marca);
        var y2 = escribir(cab, M + 30, yy, 14, true);
        yy = escribir(det, M + 30, y2 + 1, 10.5, false, TINTA2) + 8;
      });
      if (resumen) { if (yy + resH > LIM - pieH) yy = pagina(); yy = escribir(resL, M + 30, yy, 12, false, TINTA2) + 10; }
      if (pie) {
        if (yy + pieH > LIM + 6) yy = pagina();
        color(SEPIA, 'f'); doc.roundedRect(M, H - M - pieH, W - 2 * M, pieH, 5, 5, 'F');
        escribir(pieL, M + 14, H - M - pieH + 8, 11, false, TINTA);
      }
    }
    R.partidos.forEach(function (p) {
      var importantes = p.riesgos.filter(function (r) { return r.exposicion_usuario.nivel !== 'baja'; });
      var bajos = p.riesgos.filter(function (r) { return r.exposicion_usuario.nivel === 'baja'; });
      lista(limpio(p.nombre) + ': los riesgos que corres',
        'Lo que sus medidas pueden provocar aunque no te toquen, ordenado por tu exposición.',
        importantes.map(function (r) {
          return { marca: r.exposicion_usuario.nivel, cab: r.titulo, det: NIVEL[r.exposicion_usuario.nivel] + ', ' + (EVID[r.evidencia] || r.evidencia).toLowerCase() + '. ' + r.exposicion_usuario.texto };
        }),
        bajos.length ? (importantes.length ? 'Con exposición baja: ' : 'Todos con exposición baja: ') + bajos.map(function (r) { return r.titulo; }).join('; ') + '.' : null, null);
      var orden = function (v) { return v > 0 ? 0 : v < 0 ? 1 : 2; };
      var meds = p.medidas.slice().sort(function (a, b) { return orden(a.valor) - orden(b.valor); });
      lista(limpio(p.nombre) + ': lo que ganas o pierdes',
        'En negrita, cómo te afectaría (inferencia del test). Debajo, lo que propone el partido.',
        meds.map(function (m) {
          return { marca: m.valor > 0 ? 'mas' : m.valor < 0 ? 'menos' : 'inc', cab: m.tema + ': ' + m.efecto, det: (m.de ? 'Propuesta de ' + m.de + ': ' : 'Propuesta: ') + m.texto };
        }), null,
        (p.programa.estado === 'publicado' ? 'Programa: ' + p.programa.titulo + '. ' : p.programa.estado === 'coalicion' ? 'Candidatura conjunta: ' + p.integrantes + '. ' : 'Sin programa publicado: anuncios de campaña y posiciones previas. ') + 'Financiación: ' + (FIN[p.financiacion.cuantifica] || '') + '. ' + p.financiacion.resumen);
    });

    // ---------- 5. Notas y límites ----------
    nueva(true);
    y = escribir(lineas('Antes de decidir', W - 2 * M, 26, true), M, M, 26, true, PAPEL) + 14;
    var notas = R.notas.concat([
      'Muchas medidas salen de resúmenes de prensa y se están contrastando con los programas oficiales. Comprueba en el original lo que vaya a pesar en tu decisión.',
      'El número de medidas no mide su peso, y los riesgos indirectos no se suman a los efectos directos.',
      'Este resultado no es una recomendación de voto. Detalle, fuentes y metodología: ' + D.meta.url_canonica]);
    notas.forEach(function (n) {
      var ls = lineas(n, W - 2 * M - 30, 12);
      if (y + ls.length * 15 > H - M) return;
      color(PAPEL, 'd'); doc.setLineWidth(1.4); doc.rect(M, y + 1, 12, 12, 'S');
      y = escribir(ls, M + 24, y, 12, false, SEPIA) + 8;
    });

    // ---------- Numeración ----------
    var total = doc.getNumberOfPages();
    for (var i = 2; i <= total; i++) {
      doc.setPage(i); fuente(9); color(i === total ? SEPIA : TINTA2);
      doc.text(limpio('Test 29N, página ' + i + ' de ' + total), W - M, H - 16, { align: 'right' });
    }
    return doc;
  }

  root.Test29NPDF = {
    descargar: function (D, R) {
      return cargar().then(function (jsPDF) {
        var doc = generar(D, R, jsPDF);
        doc.save('test-29n-resultado.pdf');
        return doc.getNumberOfPages();
      });
    }
  };
})(typeof self !== 'undefined' ? self : this);
