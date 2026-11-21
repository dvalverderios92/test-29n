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
    doc.setProperties({ title: 'Test 29N: cómo te afecta', subject: 'Resultado personal del Test 29N', creator: 'Test 29N' });
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
    var NIVEL = { alta: 'Te afecta mucho', media: 'Te afecta algo', baja: 'Te afecta poco' };
    var EVID = { hecho: 'Comprobado', 'hecho+inferencia': 'Comprobado y deducción del test', consenso: 'La mayoría de expertos coincide', disputada: 'Los expertos discrepan', inferencia: 'Deducción del test' };
    var FIN = { varias: 'Según cada partido', no: 'No cuantifica su programa', cifras_propias: 'Cifras propias', fuera_del_programa: 'Cifras fuera del programa', si: 'Cuantifica su programa' };
    var resumenDe = function (p) { return root.Test29N.resumenPartido(p); };
    var LIM = H - M;
    // ---------- 1. Portada ----------
    nueva(true);
    escribir(lineas('Elecciones generales del 29 de noviembre de 2026', 420, 13, true), M, M, 13, true, SEPIA);
    var y = escribir(lineas('Cómo te afecta el 29N', 430, 44, true), M, 90, 44, true, PAPEL);
    var perfil = ['region', 'lab', 'viv', 'ing'].map(function (id) {
      var q = D.preguntas.filter(function (x) { return x.id === id; })[0], v = R.respuestas[id];
      var o = q && q.opciones.filter(function (x) { return x.valor === v; })[0];
      return o ? o.texto : null;
    }).filter(Boolean);
    y = escribir(lineas('Tu perfil: ' + perfil.join('; ') + '.', 430, 13), M, y + 18, 13, false, SEPIA);
    escribir(lineas('Datos revisados el ' + fecha + ', versión ' + D.meta.version + '. No es una recomendación de voto: no hay ranking ni puntuación.', 430, 11), M, H - M - 28, 11, false, SEPIA);
    // gran casilla con X
    color(PAPEL, 'd'); doc.setLineWidth(5); doc.rect(W - M - 170, 95, 170, 170, 'S');
    doc.setLineWidth(9); doc.line(W - M - 140, 125, W - M - 30, 235); doc.line(W - M - 30, 125, W - M - 140, 235);

    // ---------- 2. Tu resultado en un minuto ----------
    (function () {
      var bloques = R.partidos.map(function (p) {
        var r = resumenDe(p);
        var rie = r.riesgos;
        return { nombre: p.nombre + (p.partidos_test ? ' (candidatura conjunta)' : ''), lin: [[r.medidas, false], [r.contra, true], [rie, false]].filter(function (x) { return x[0]; }) };
      });
      var ncol = bloques.length > 6 ? 4 : bloques.length > 4 ? 3 : bloques.length > 1 ? 2 : 1, gap = ncol === 4 ? 18 : 24, colW = (W - 2 * M - gap * (ncol - 1)) / ncol, tl = ncol === 4 ? 9.5 : ncol === 3 ? 10.5 : 12, tc = ncol === 4 ? 12 : 14;
      var medir = function (b) {
        var cab = lineas(b.nombre, colW - 4, tc, true), cuerpo = b.lin.map(function (l) { return [lineas(l[0], colW - 4, tl, l[1]), l[1]]; });
        return { cab: cab, cuerpo: cuerpo, alto: cab.length * tc * 1.25 + cuerpo.reduce(function (a, c) { return a + c[0].length * tl * 1.25 + 2; }, 0) + 16 };
      };
      var ms = bloques.map(medir), filas = [];
      for (var k = 0; k < ms.length; k += ncol) filas.push(ms.slice(k, k + ncol));
      nueva(false);
      var yy = titulo('Tu resultado en un minuto', 'Partidos en orden alfabético. Lo que te favorece o perjudica directamente y los riesgos que más te afectan.');
      filas.forEach(function (fila, n) {
        var alto = Math.max.apply(null, fila.map(function (b) { return b.alto; }));
        if (yy + alto > LIM && n) { nueva(false); yy = titulo('Tu resultado en un minuto (continuación)', null); }
        fila.forEach(function (b, c) {
          var x = M + c * (colW + gap);
          color(TINTA, 'd'); doc.setLineWidth(1.6); doc.line(x, yy, x + colW, yy);
          var y2 = escribir(b.cab, x, yy + 6, tc, true);
          b.cuerpo.forEach(function (cc) { y2 = escribir(cc[0], x, y2 + 1, tl, cc[1], cc[1] ? TINTA : TINTA2) + 1; });
        });
        yy += alto;
      });
    })();

    // ---------- 3. Riesgos comparados ----------
    var ab = { cc: 'CC', fa: 'FA', pod: 'Podemos', pp: 'PP', psoe: 'PSOE', vox: 'Vox', upc: 'UPC', compromis: 'Compromís', ara_mes: 'Ara Més', erc: 'ERC', bng: 'BNG', bildu: 'EH Bildu', salf: 'SALF' };
    var toca = function (f) { return R.partidos.some(function (p) { var n = f.niveles[p.id]; return n === 'alta' || n === 'media'; }); };
    var f1 = R.matriz_riesgos.filter(toca), f2 = R.matriz_riesgos.filter(function (f) { return !toca(f); });
    (function () {
      var porPag = 10;
      for (var ini = 0; ini < Math.max(f1.length, 1); ini += porPag) {
        nueva(false);
        var y = titulo('Riesgos: lo que podría pasar además' + (ini ? ' (continuación)' : ''), ini ? null : 'Efectos que una medida puede tener aunque no te toque directamente. Cada casilla dice cuánto te afectaría con ese partido.');
        var c0 = 300, cw = (W - 2 * M - c0) / R.partidos.length;
        fuente(12, true); color(TINTA);
        R.partidos.forEach(function (p, j) { doc.text(limpio(ab[p.id] || p.nombre), M + c0 + j * cw + cw / 2, y, { align: 'center', baseline: 'top' }); });
        y += 20; color(TINTA, 'd'); doc.setLineWidth(1.6); doc.line(M, y - 4, W - M, y - 4);
        var trozo = f1.slice(ini, ini + porPag), ult = ini + porPag >= f1.length;
        var pie = ult ? [lineas('Leyenda: casilla negra, te afecta mucho; rayada, algo; vacía, poco; raya, no aplica.' + (f2.length ? ' Además, te afectan poco o no aplican: ' + f2.map(function (f) { return f.corto; }).join(', ') + '.' : ''), W - 2 * M, 11)] : [];
        var pieH = ult ? pie[0].length * 13.75 + 10 : 0;
        if (!trozo.length) escribir(lineas('Ningún riesgo te afecta mucho ni algo con ningún partido.', W - 2 * M, 14), M, y + 6, 14, false, TINTA2);
        var alto = Math.min(44, (LIM - pieH - y) / Math.max(trozo.length, 1)), tt = alto < 32 ? 12 : 13, conEv = alto >= 30;
        trozo.forEach(function (f, k) {
          var fy = y + k * alto;
          var yy = escribir(lineas(f.corto, c0 - 12, tt, true).slice(0, 1), M, fy + Math.max(3, (alto - tt * 1.25 - (conEv ? 12 : 0)) / 2), tt, true);
          if (conEv) escribir([limpio(EVID[f.evidencia] || f.evidencia)], M, yy + 1, 9.5, false, TINTA2);
          R.partidos.forEach(function (p, j) {
            var n = f.niveles[p.id], cx = M + c0 + j * cw + cw / 2;
            if (n) casilla(cx - 9, fy + alto / 2 - 9, 18, n);
            else { color(LINEA, 'd'); doc.setLineWidth(1.4); doc.line(cx - 7, fy + alto / 2, cx + 7, fy + alto / 2); }
          });
          color(LINEA, 'd'); doc.setLineWidth(.6); doc.line(M, fy + alto, W - M, fy + alto);
        });
        if (ult) escribir(pie[0], M, LIM - pieH + 6, 11, false, TINTA2);
      }
    })();

    // ---------- 4. Una diapositiva por partido (misma regla para todos) ----------
    var MAXMED = 6, orden = function (v) { return v < 0 ? 0 : v === 0 ? 1 : 2; };
    R.partidos.forEach(function (p) {
      var r = resumenDe(p);
      nueva(false);
      var y = titulo(p.nombre, r.medidas + ' ' + r.riesgos);
      var meds = p.medidas.slice().sort(function (a, b) { return orden(a.valor) - orden(b.valor); });
      var pieTxt = 'Cómo dice pagarlo: ' + (FIN[p.financiacion.cuantifica] || p.financiacion.cuantifica) + '. Lo que propone cada medida, con su página, está en el anexo.';
      var pieL = lineas(pieTxt, W - 2 * M - 28, 11), pieH = pieL.length * 13.75 + 16;
      var mostradas = 0;
      if (!meds.length) escribir(lineas('Ninguna medida recogida te afecta directamente según tus respuestas.', W - 2 * M, 14), M, y, 14, false, TINTA2);
      for (var k = 0; k < meds.length && k < MAXMED; k++) {
        var m = meds[k], cab = lineas(m.tema + ': ' + m.efecto, W - 2 * M - 34, 13, true);
        var restan = meds.length - k - 1, notaH = restan ? 18 : 0;
        if (y + cab.length * 16.25 + 8 + notaH > LIM - pieH) break;
        casilla(M, y + 1, 16, m.valor > 0 ? 'mas' : m.valor < 0 ? 'menos' : 'inc');
        y = escribir(cab, M + 30, y, 13, true) + 8; mostradas++;
      }
      if (meds.length > mostradas) escribir(lineas('Y ' + (meds.length - mostradas) + (meds.length - mostradas === 1 ? ' medida más' : ' medidas más') + ' en el anexo.', W - 2 * M - 30, 12), M + 30, y, 12, false, TINTA2);
      color(SEPIA, 'f'); doc.roundedRect(M, H - M - pieH, W - 2 * M, pieH, 5, 5, 'F');
      escribir(pieL, M + 14, H - M - pieH + 8, 11, false, TINTA);
    });

    // ---------- 5. Antes de decidir ----------
    nueva(true);
    y = escribir(lineas('Antes de decidir', W - 2 * M, 26, true), M, M, 26, true, PAPEL) + 14;
    var notas = R.notas.concat([
      'Las medidas salen de los programas oficiales, con su página. Si el programa no recoge algo, se usan anuncios de campaña o posiciones anteriores, y así se indica. Comprueba en el original lo que vaya a pesar en tu decisión.',
      'El número de medidas no mide su peso, y los riesgos no se suman a lo que ganas o pierdes.',
      'Este resultado no es una recomendación de voto. Detalle, fuentes y metodología: ' + D.meta.url_canonica]);
    notas.forEach(function (n) {
      var ls = lineas(n, W - 2 * M - 30, 12);
      if (y + ls.length * 15 > H - M) return;
      color(PAPEL, 'd'); doc.setLineWidth(1.4); doc.rect(M, y + 1, 12, 12, 'S');
      y = escribir(ls, M + 24, y, 12, false, SEPIA) + 8;
    });

    // ---------- ANEXO ----------
    nueva(true);
    escribir(lineas('Anexo', W - 2 * M, 40, true), M, 120, 40, true, PAPEL);
    escribir(lineas('El detalle: cómo leer el resultado, los riesgos explicados y lo que propone cada partido en cada medida, con su fuente.', 460, 14), M, 180, 14, false, SEPIA);

    // Cómo leer
    nueva(false);
    y = titulo('Cómo leer este resultado', 'Tres partes que no se suman entre sí. Cada medida separa lo que propone el partido de cómo te afectaría (deducción del test).');
    var capas = [
      ['Lo que ganas o pierdes', 'Las medidas que te favorecen, te perjudican o tienen un efecto incierto en tu bolsillo.'],
      ['Riesgos: lo que podría pasar además', 'Efectos que una medida puede tener aunque no te toque: menos recaudación, gasto sin pagar, precios, empleo, oferta.'],
      ['Cómo dice pagarlo', 'Si cada partido calcula lo que cuesta su programa y de dónde sale el dinero.']];
    var colW = (W - 2 * M - 40) / 3;
    capas.forEach(function (c, i) {
      var x = M + i * (colW + 20);
      casilla(x, y, 22, 'x');
      var yy = escribir(lineas(c[0], colW, 15, true), x, y + 32, 15, true);
      escribir(lineas(c[1], colW, 12), x, yy + 4, 12, false, TINTA2);
    });
    var yl = H - M - 112;
    color(SEPIA, 'f'); doc.roundedRect(M, yl, W - 2 * M, 104, 6, 6, 'F');
    [['Cuánto te afecta un riesgo', [['alta', 'Mucho'], ['media', 'Algo'], ['baja', 'Poco']]],
     ['Efecto de cada medida', [['mas', 'A tu favor'], ['menos', 'En tu contra'], ['inc', 'Incierto']]]].forEach(function (g, f) {
      var fy = yl + 14 + f * 32;
      escribir([g[0]], M + 14, fy + 3, 12, true);
      g[1].forEach(function (it, i) { var x = M + 220 + i * 130; casilla(x, fy, 18, it[0]); escribir([it[1]], x + 26, fy + 3, 12, false); });
    });
    escribir(lineas('Partidos en orden alfabético. Detalle y fuentes en ' + D.meta.url_canonica, W - 2 * M - 28, 11), M + 14, yl + 80, 11, false, TINTA2);

    function lista(tituloBase, sub, elementos, resumen, pie) {
      var cont = 0;
      function pagina() { nueva(false); return titulo(tituloBase + (cont++ ? ' (continuación)' : ''), cont === 1 ? sub : null); }
      var pieL = pie ? lineas(pie, W - 2 * M - 28, 11) : [], pieH = pie ? pieL.length * 13.75 + 16 : 0;
      var resL = resumen ? lineas(resumen, W - 2 * M - 34, 12) : [], resH = resumen ? resL.length * 15 + 10 : 0;
      var yy = pagina();
      if (!elementos.length && !resumen) yy = escribir(lineas('Ninguna medida recogida te afecta directamente según tus respuestas.', W - 2 * M, 14), M, yy, 14, false, TINTA2) + 10;
      elementos.forEach(function (e, k) {
        var cab = lineas(e.cab, W - 2 * M - 34, 13, true), det = lineas(e.det, W - 2 * M - 34, 11);
        var alto = cab.length * 16.25 + det.length * 13.75 + 8;
        var reserva = (k === elementos.length - 1) ? resH + pieH : 0;
        if (yy + alto + reserva > LIM && yy + alto > LIM - pieH) yy = pagina();
        else if (yy + alto > LIM) yy = pagina();
        casilla(M, yy + 1, 16, e.marca);
        var y2 = escribir(cab, M + 30, yy, 13, true);
        yy = escribir(det, M + 30, y2 + 1, 11, false, TINTA2) + 8;
      });
      if (resumen) { if (yy + resH > LIM - pieH) yy = pagina(); yy = escribir(resL, M + 30, yy, 12, false, TINTA2) + 10; }
      if (pie) {
        if (yy + pieH > LIM + 6) yy = pagina();
        color(SEPIA, 'f'); doc.roundedRect(M, H - M - pieH, W - 2 * M, pieH, 5, 5, 'F');
        escribir(pieL, M + 14, H - M - pieH + 8, 11, false, TINTA);
      }
    }

    // Riesgos explicados (una vez, no por partido)
    var NORD = { alta: 3, media: 2, baja: 1 };
    var maxNivel = function (f) { var m = null; R.partidos.forEach(function (p) { var n = f.niveles[p.id]; if (n && (!m || NORD[n] > NORD[m])) m = n; }); return m; };
    if (f1.length) lista('Los riesgos, explicados', 'Qué puede pasar y qué dicen los expertos. La casilla indica el nivel más alto con algún partido.',
      f1.map(function (f) {
        var rd = D.riesgos.filter(function (x) { return x.id === f.id; })[0] || {};
        return { marca: maxNivel(f), cab: f.corto + ' (' + (EVID[f.evidencia] || f.evidencia).toLowerCase() + ')', det: rd.que_pasa || f.titulo };
      }), null, null);

    // Todas las medidas de cada partido, con lo que propone
    R.partidos.forEach(function (p) {
      var meds = p.medidas.slice().sort(function (a, b) { return orden(a.valor) - orden(b.valor); });
      lista(limpio(p.nombre) + ': todas sus medidas que te afectan',
        'En negrita, cómo te afectaría (deducción del test). Debajo, lo que propone. Salvo que se indique, sin plazo ni coste.',
        meds.map(function (m) {
          return { marca: m.valor > 0 ? 'mas' : m.valor < 0 ? 'menos' : 'inc', cab: m.tema + ': ' + m.efecto, det: (m.de ? 'Propuesta de ' + m.de + ': ' : 'Propone: ') + m.texto + (m.detalle && m.detalle.plazo ? ' Plazo: ' + m.detalle.plazo + '.' : '') + (m.detalle && m.detalle.coste ? ' Coste: ' + m.detalle.coste + '.' : '') + (m.nota_candidatura ? ' ' + m.nota_candidatura : '') + (m.pagina ? ' (p. ' + m.pagina + ' del programa)' : m.origen === 'campaña' ? ' (anuncio de campaña)' : m.origen === 'previa' ? ' (posición anterior)' : '') };
        }), null,
        (p.programa.estado === 'publicado' ? 'Programa: ' + p.programa.titulo + '. ' : p.programa.estado === 'coalicion' ? 'Candidatura conjunta: ' + p.integrantes + '. ' : 'Sin programa publicado: anuncios de campaña y posiciones anteriores. ') + 'Cómo dice pagarlo: ' + (FIN[p.financiacion.cuantifica] || p.financiacion.cuantifica) + '. ' + p.financiacion.resumen);
    });

    // Derechos y protecciones (sin valoración)
    (R.derechos || []).forEach(function (t) {
      lista('Derechos y protecciones: ' + t.nombre,
        'Lo que propone cada partido, resumido de su programa oficial. Sin valoración a favor o en contra.',
        t.partidos.map(function (p) {
          return { marca: 'baja', cab: p.nombre,
            det: p.medidas.length ? p.medidas.map(function (m) { return (m.de ? m.de + ': ' : '') + m.texto + ' (' + (m.pagina ? (m.num ? 'medida ' + m.num + ', ' : '') + 'p. ' + m.pagina : (m.origen === 'campaña' ? 'anuncio de campaña' : 'posición anterior') + (m.referencia ? ': ' + m.referencia : '')) + ')'; }).join(' ')
              : 'No se han encontrado propuestas sobre este tema ni en su programa ni en otras fuentes consultadas.' };
        }), null, null);
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
