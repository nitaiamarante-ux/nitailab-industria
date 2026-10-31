/* Mapa v5 "da origem ao destino". JS puro, sem biblioteca. Le o bloco JSON #m5-dados.
   Mapa em canvas (leve a cada quadro); rotulos, selos e trilha em HTML (nitidos em qualquer zoom).
   Uma camera que sai do Brasil inteiro, aproxima no trecho de terra e abre pro mundo no mar.
   Relogio proprio: pausar congela tudo (camera, carga, leitura). Prova por URL: ?c=<id>&e=<etapa 1..n>&tour=0&t=<ms extra> */
(function () {
  "use strict";
  var raiz = document.getElementById("corredores"), dEl = document.getElementById("m5-dados");
  if (!raiz || !dEl) return;
  var D; try { D = JSON.parse(dEl.textContent); } catch (e) { return; }
  // No site a geometria (~500 KB) fica em arquivo separado e so baixa quando a pessoa chega perto do mapa.
  if (!D.geo && D.geoUrl) {
    var baixou = false, baixa = function () {
      if (baixou) return; baixou = true;
      fetch(D.geoUrl).then(function (r) { return r.json(); }).then(function (g) { for (var k in g) D[k] = g[k]; iniciar(); }).catch(function () {});
    };
    if ("IntersectionObserver" in window) {
      var ob = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { ob.disconnect(); baixa(); } }, { rootMargin: "900px 0px" });
      ob.observe(raiz);
    } else baixa();
    return;
  }
  iniciar();
  function iniciar() {
  var cv = document.getElementById("m5-tela"), ctx0 = cv && cv.getContext && cv.getContext("2d");
  if (!ctx0 || !window.Path2D) return;
  var ctx = ctx0;                         // sem canvas: fica a lista em HTML
  document.documentElement.classList.add("m5-js");
  var ui = D.ui, COR = D.cor, CAD = D.cadeias, LEGS = D.legs, PIN = D.pinos;
  var palco = document.getElementById("m5-palco");
  var camRot = document.getElementById("m5-rotulos"), filme = document.getElementById("m5-filme"), trilha = document.getElementById("m5-trilha");
  var ctrl = document.getElementById("m5-ctrl"), texto = document.getElementById("m5-texto"), info = document.getElementById("m5-info");
  var chips = [].slice.call(raiz.querySelectorAll(".m5-chip"));
  var calmo = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;   // aparelho pediu menos movimento
  var reduz = false;                                                                          // a viagem e a rota continuam; so a camera fica curta
  var qs = new URLSearchParams(location.search);

  function mede(acao, extra) {
    var d = { acao: acao }; for (var k in extra) d[k] = extra[k];
    try { if (window.nlMede) window.nlMede("nl_mapa", d); } catch (e) {}
    try { if (window.gtag) gtag("event", "mapa_" + acao, extra); } catch (e) {}
  }
  function el(tag, at, pai) { var e = document.createElement(tag); for (var k in at) e.setAttribute(k, at[k]); if (pai) pai.appendChild(e); return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ic(m) { return '<svg class="m5-ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#m5-i-' + m + '"/></svg>'; }
  function celular() { return palco.clientWidth < 620; }
  function ease(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
  function suaveIO(t) { return t * t * (3 - 2 * t); }

  /* ------------------------------------------------------------ geometria (Path2D uma vez so) */
  var G = D.geo, GP = { paises: new Path2D(G.paises), br: new Path2D(G.br), ouro: new Path2D(G.ouro), outras: new Path2D(G.outras), dest: {} };
  for (var k in G.dest) GP.dest[k] = new Path2D(G.dest[k]);
  var vis = { ouro: .6, dest: {} };                           // propriedades visuais animadas
  for (k in G.dest) vis.dest[k] = 0;

  /* ------------------------------------------------------------ relogio que pausa */
  var tarefas = [], tocando = true, visivel = true, relogio = 0, ultimo = 0, raf = 0, geracao = 0, sujo = true;
  var nLaco = 0, tPinta = 0, nBase = 0;
  function laco(now) {
    raf = 0; nLaco++; now = performance.now();          // relogio real (o carimbo do quadro pode ser sintetico)
    var dt = ultimo ? Math.min(now - ultimo, 110) : 16; ultimo = now;   // aparelho lento: anda aos saltos, mas no tempo certo
    if (tocando && visivel && !document.hidden) relogio += dt;
    var vivas = [];
    for (var i = 0; i < tarefas.length; i++) {
      var t = tarefas[i]; if (t.ger !== geracao && t.ger !== -1) continue;
      var rel = t.livre ? now : relogio;                      // tarefas "livres" (fades) nao param no pause
      if (t.ini == null) t.ini = rel;
      var u = t.dur ? Math.min(1, (rel - t.ini) / t.dur) : 1;
      if (t.f) t.f(u);
      if (u >= 1) { if (t.ok) t.ok(); } else vivas.push(t);
    }
    tarefas = vivas;
    var tp = performance.now(); pinta(); tPinta += performance.now() - tp;
    if (tarefas.length) raf = requestAnimationFrame(laco); else ultimo = 0;
  }
  function liga() { if (!raf) raf = requestAnimationFrame(laco); }
  function anima(dur, f, fixo) {
    var g = geracao;
    return new Promise(function (ok) { tarefas.push({ dur: (reduz && !fixo) ? 0 : dur, f: f, ok: ok, ger: g }); liga(); });
  }
  function espera(ms) { return anima(ms, null, true); }       // tempo de leitura vale mesmo sem movimento
  function solta(obj, chave, para, dur) {                     // transicao visual independente do roteiro
    var de = obj[chave]; if (de === para) return;
    tarefas.push({ dur: reduz ? 0 : dur, livre: true, ger: -1, f: function (u) { obj[chave] = de + (para - de) * suaveIO(u); } }); liga();
  }
  function vivo(g) { return g === geracao; }

  /* ------------------------------------------------------------ camera */
  var W = 1, H = 1, DPR = 1, vb = { x: D.br[0], y: D.br[1], w: D.br[2], h: D.br[3] }, alvo = D.br;
  function mede() {
    W = palco.clientWidth || 1; H = palco.clientHeight || 1; DPR = Math.min(W < 620 ? 1.5 : 2, window.devicePixelRatio || 1);
    base.width = Math.round(W * DPR); base.height = Math.round(H * DPR); chaveBase = "";
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); cv.style.width = W + "px"; cv.style.height = H + "px";
  }
  function margens() {
    var cel = celular(), fh = filme.hidden ? 0 : filme.offsetHeight - 8;
    return { t: cel ? 16 : 30, b: fh + (cel ? 18 : 30), l: cel ? 16 : 36, r: cel ? 16 : 36 };
  }
  function enquadra(b) {
    var m = margens(), aw = Math.max(40, W - m.l - m.r), ah = Math.max(40, H - m.t - m.b);
    var s = Math.min(aw / b[2], ah / b[3]), cx = b[0] + b[2] / 2, cy = b[1] + b[3] / 2;
    return { x: cx - (m.l + aw / 2) / s, y: cy - (m.t + ah / 2) / s, w: W / s, h: H / s };
  }
  function camera(box, g) {
    alvo = box; var a = vb, b = enquadra(box);
    var acx = a.x + a.w / 2, acy = a.y + a.h / 2, bcx = b.x + b.w / 2, bcy = b.y + b.h / 2;
    var zr = Math.abs(Math.log(b.w / a.w)), dist = Math.hypot(bcx - acx, bcy - acy) / Math.max(a.w, b.w);
    var dur = Math.min(2800, 1000 + zr * 520 + dist * 1100);
    if (zr < .04 && dist < .03) dur = 500;
    if (calmo) dur = Math.min(dur, 650);
    return anima(dur, function (u) {
      var e = ease(u), w = a.w * Math.pow(b.w / a.w, e);
      // o centro anda em proporcao a escala: sensacao de voo, sem o mapa "escorregar" de lado
      var kk = Math.abs(b.w - a.w) > 1e-6 ? (w - a.w) / (b.w - a.w) : e;
      var cx = acx + (bcx - acx) * kk, cy = acy + (bcy - acy) * kk;
      vb = { x: cx - w / 2, y: cy - (w * H / W) / 2, w: w, h: w * H / W };
    });
  }
  function tela(xy) { return [(xy[0] - vb.x) / vb.w * W, (xy[1] - vb.y) / vb.h * H]; }

  /* ------------------------------------------------------------ pernas */
  var cache = {};
  function prep(id) {
    if (cache[id]) return cache[id];
    var L = LEGS[id], p = L.p, acc = [0];
    for (var i = 1; i < p.length; i++) acc.push(acc[i - 1] + Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]));
    return (cache[id] = { id: id, m: L.m, p: p, acc: acc, len: acc[acc.length - 1], esm: L.esm || "" });
  }
  function ponto(c, f) {
    var t = c.len * Math.max(0, Math.min(1, f)), lo = 0, hi = c.acc.length - 1;
    while (hi - lo > 1) { var mi = (lo + hi) >> 1; if (c.acc[mi] < t) lo = mi; else hi = mi; }
    var seg = c.acc[hi] - c.acc[lo] || 1, u = (t - c.acc[lo]) / seg;
    return { i: lo, x: c.p[lo][0] + (c.p[hi][0] - c.p[lo][0]) * u, y: c.p[lo][1] + (c.p[hi][1] - c.p[lo][1]) * u };
  }
  var tracos = [];                                            // {c, f, a}
  function traco(id) {
    for (var i = 0; i < tracos.length; i++) if (tracos[i].c.id === id && !tracos[i].saindo) return tracos[i];
    var t = { c: prep(id), f: 0, a: 1 }; tracos.push(t); return t;
  }
  function desenha(id, f) { traco(id).f = f; }
  function limpaRotas() {
    tracos.forEach(function (t) {
      t.saindo = true;
      tarefas.push({ dur: reduz ? 0 : 650, livre: true, ger: -1, f: function (u) { t.a = 1 - u; }, ok: function () { tracos = tracos.filter(function (x) { return x !== t; }); } });
    });
    liga();
  }

  /* ------------------------------------------------------------ cargas (o ponto de luz que anda) */
  var cargas = [];
  function novaCarga(id, comSelo, modo) {
    var k = { c: prep(id), f: 0, selo: null };
    if (comSelo) { k.selo = el("div", { "class": "m5-selo" }, camRot); k.selo.innerHTML = ic(modo); }
    cargas.push(k); return k;
  }
  function limpaCargas() { cargas.forEach(function (k) { if (k.selo) k.selo.remove(); }); cargas = []; }

  /* ------------------------------------------------------------ pintura */
  var ESTILO = {
    ferro: { luz: [COR.ouro, .22, 11], linha: ["#E4CB97", 1, 3], dash: null },
    rodo: { luz: [COR.creme, .07, 7], linha: [COR.creme, .9, 2], dash: [5, 5] },
    mar: { luz: [COR.ouro, .14, 9], linha: ["#E4CB97", 1, 2.6], dash: [.1, 7] }
  };
  function rgba(hex, a) { var n = parseInt(hex.slice(1), 16); return "rgba(" + (n >> 16) + "," + (n >> 8 & 255) + "," + (n & 255) + "," + a + ")"; }
  function caminho(c, f) {
    var q = ponto(c, f); ctx.beginPath(); ctx.moveTo(c.p[0][0], c.p[0][1]);
    for (var i = 1; i <= q.i; i++) ctx.lineTo(c.p[i][0], c.p[i][1]);
    ctx.lineTo(q.x, q.y); return q;
  }
  function tinta(cor, a, c) {
    if (!c.esm) return rgba(cor, a);
    var p0 = c.p[0], p1 = c.p[c.p.length - 1], gr = ctx.createLinearGradient(p0[0], p0[1], p1[0], p1[1]);
    if (c.esm === "ini") { gr.addColorStop(0, rgba(cor, 0)); gr.addColorStop(c.m === "mar" ? .3 : .6, rgba(cor, a)); gr.addColorStop(1, rgba(cor, a)); }
    else { gr.addColorStop(0, rgba(cor, a)); gr.addColorStop(.4, rgba(cor, a)); gr.addColorStop(1, rgba(cor, 0)); }
    return gr;
  }
  // mapa-base em cache: so repinta paises, Brasil e malha quando a camera ou a cor mudam
  var base = document.createElement("canvas"), bctx = base.getContext("2d"), chaveBase = "";
  function pintaBase(s, px) {
    var dk = ""; for (var k in vis.dest) dk += vis.dest[k].toFixed(3) + ",";
    var chave = [vb.x.toFixed(3), vb.y.toFixed(3), vb.w.toFixed(3), W, H, vis.ouro.toFixed(3), dk].join("|");
    if (chave === chaveBase) return true;
    var agora = performance.now();
    if (custoBase > 24 && agora - quandoBase < 180) { clearTimeout(tBase); tBase = setTimeout(function () { pinta(); }, 190); return false; }
    chaveBase = chave; nBase++; quandoBase = agora; vbBase = { x: vb.x, y: vb.y, w: vb.w };
    var c0 = ctx; ctx = bctx;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.fillStyle = COR.mar; ctx.fillRect(0, 0, W, H);
    ctx.setTransform(DPR * s, 0, 0, DPR * s, -vb.x * s * DPR, -vb.y * s * DPR);
    ctx.lineJoin = "round"; ctx.lineCap = "round";
    // paises
    ctx.fillStyle = COR.pais; ctx.fill(GP.paises); ctx.strokeStyle = COR.paisb; ctx.lineWidth = px; ctx.stroke(GP.paises);
    for (var k in GP.dest) {
      var v = vis.dest[k];
      ctx.fillStyle = v > .01 ? mistura(COR.pais, "#3E321F", v) : COR.pais; ctx.fill(GP.dest[k]);
      ctx.strokeStyle = v > .01 ? rgba(COR.ouro, .25 + .65 * v) : COR.paisb; ctx.lineWidth = (1 + v * .6) * px; ctx.stroke(GP.dest[k]);
    }
    // Brasil (IBGE): sempre um tom acima do resto do mundo
    ctx.fillStyle = COR.terra; ctx.fill(GP.br); ctx.strokeStyle = COR.uf; ctx.lineWidth = .9 * px; ctx.stroke(GP.br);
    // ferrovias
    ctx.globalAlpha = .45; ctx.strokeStyle = COR.outras; ctx.lineWidth = px; ctx.stroke(GP.outras);
    ctx.globalAlpha = vis.ouro; ctx.strokeStyle = COR.ouro; ctx.lineWidth = 1.6 * px; ctx.stroke(GP.ouro);
    ctx.globalAlpha = 1; ctx = c0; custoBase = performance.now() - agora;
    return true;
  }
  var custoBase = 0, quandoBase = -1e9, vbBase = null, tBase = 0;
  function pinta() {
    var s = W / vb.w, px = 1 / s;
    var fresca = pintaBase(s, px);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (fresca) ctx.drawImage(base, 0, 0);
    else {                                                    // aparelho lento em pleno voo: escala a ultima imagem nitida
      var k = vbBase.w / vb.w;
      ctx.fillStyle = COR.mar; ctx.fillRect(0, 0, cv.width, cv.height);
      ctx.drawImage(base, (vbBase.x - vb.x) / vb.w * W * DPR, (vbBase.y - vb.y) / vb.w * W * DPR, cv.width * k, cv.height * k);
    }
    ctx.setTransform(DPR * s, 0, 0, DPR * s, -vb.x * s * DPR, -vb.y * s * DPR);
    ctx.lineJoin = "round"; ctx.lineCap = "round";
    // rotas da cadeia
    tracos.forEach(function (t) {
      if (t.f <= 0 || t.a <= 0) return;
      var e = ESTILO[t.c.m]; ctx.globalAlpha = t.a;
      caminho(t.c, t.f);
      ctx.setLineDash([]); ctx.strokeStyle = tinta(e.luz[0], e.luz[1], t.c); ctx.lineWidth = e.luz[2] * px; ctx.stroke();
      ctx.setLineDash(e.dash ? [e.dash[0] * px, e.dash[1] * px] : []);
      ctx.strokeStyle = tinta(e.linha[0], e.linha[1], t.c); ctx.lineWidth = e.linha[2] * px; ctx.stroke();
    });
    ctx.setLineDash([]); ctx.globalAlpha = 1;
    // cargas
    cargas.forEach(function (kk) {
      if (kk.f <= 0 || kk.f >= 1) return;
      var q = ponto(kk.c, kk.f), r = (kk.c.m === "rodo" ? 9 : 16) * px;
      var o = kk.c.esm === "ini" ? Math.min(1, kk.f * 5) : (kk.c.esm === "fim" ? Math.min(1, (1 - kk.f) * 4) : 1);
      ctx.globalAlpha = o;
      var gr = ctx.createRadialGradient(q.x, q.y, 0, q.x, q.y, r);
      gr.addColorStop(0, rgba(COR.creme, .95)); gr.addColorStop(.3, rgba(COR.ouro, .55)); gr.addColorStop(1, rgba(COR.ouro, 0));
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(q.x, q.y, r, 0, 6.2832); ctx.fill();
      ctx.fillStyle = COR.creme; ctx.beginPath(); ctx.arc(q.x, q.y, (kk.c.m === "rodo" ? 2.2 : 3.4) * px, 0, 6.2832); ctx.fill();
      ctx.globalAlpha = 1;
    });
    sobrepoe();
  }
  function mistura(a, b, t) {
    var x = parseInt(a.slice(1), 16), y = parseInt(b.slice(1), 16);
    var r = (x >> 16) + ((y >> 16) - (x >> 16)) * t, g = (x >> 8 & 255) + ((y >> 8 & 255) - (x >> 8 & 255)) * t, bb = (x & 255) + ((y & 255) - (x & 255)) * t;
    return "rgb(" + Math.round(r) + "," + Math.round(g) + "," + Math.round(bb) + ")";
  }

  /* ------------------------------------------------------------ rotulos, selos, transbordo (HTML) */
  var rotEls = {}, visiveis = {}, foco = {}, transb = null;
  function rotulo(id) {
    if (rotEls[id]) return rotEls[id];
    var p = PIN[id], e = el("div", { "class": "m5-pin m5-pin-" + p.t + " m5-lado-" + p.lado + (p.cel === 0 ? " m5-sem-cel" : "") }, camRot);
    var marca = (p.t === "pais" || p.t === "mar" || p.t === "regiao" || p.t === "alerta") ? "" : (p.t === "cidade" ? '<i class="m5-ponto"></i>' : '<i class="m5-marca">' + ic(p.t) + "</i>");
    e.innerHTML = '<i class="m5-onda"></i><i class="m5-onda m5-onda2"></i>' + marca + '<span class="m5-nome"><b>' + esc(p.n) + "</b>" + (p.s ? "<small>" + esc(p.s) + "</small>" : "") + "</span>";
    return (rotEls[id] = e);
  }
  function sobrepoe() {
    var z = W / vb.w;
    for (var id in rotEls) {
      var e = rotEls[id], p = PIN[id];
      if (visiveis[id]) {
        var s = tela(p.xy), dentro = s[0] > -80 && s[0] < W + 80 && s[1] > -50 && s[1] < H + 50;
        if (p.lado === "c" || p.lado === "a") {                                    // rotulo centralizado nunca corta na borda do quadro
          if (!e._w) { var nm = e.querySelector(".m5-nome"); e._w = nm ? nm.offsetWidth : 0; }
          if (e._w) s = [Math.max(e._w / 2 + 10, Math.min(W - e._w / 2 - 10, s[0])), s[1]];
        }
        e.style.transform = "translate3d(" + s[0].toFixed(1) + "px," + s[1].toFixed(1) + "px,0)";
        e.classList.toggle("m5-on", dentro); e.classList.toggle("m5-sem-nome", z < p.z); e.classList.toggle("m5-foco", !!foco[id]);
        if (p.lado === "d" || p.lado === "e") {                 // rotulo encostou na borda: vira de lado
          if (!e._w) { var nm2 = e.querySelector(".m5-nome"); e._w = nm2 ? nm2.offsetWidth : 120; }
          var vira = p.lado === "d" ? s[0] + 24 + e._w > W - 6 : s[0] - 24 - e._w < 6;   // vira so se a largura real nao couber
          e.classList.toggle("m5-lado-d", vira ? p.lado === "e" : p.lado === "d"); e.classList.toggle("m5-lado-e", vira ? p.lado === "d" : p.lado === "e");
        }
        e.classList.toggle("m5-mini", z < Math.min(p.z, 5) * .4 && (p.t === "terminal" || p.t === "usina" || p.t === "cidade" || p.t === "mina"));
      } else e.classList.remove("m5-on", "m5-foco");
    }
    cargas.forEach(function (k) {
      if (!k.selo) return;
      if (k.f <= 0 || k.f >= 1) { k.selo.classList.remove("m5-on"); return; }
      var q = ponto(k.c, k.f), s = tela([q.x, q.y]);
      k.selo.style.transform = "translate3d(" + s[0].toFixed(1) + "px," + s[1].toFixed(1) + "px,0)"; k.selo.classList.add("m5-on");
    });
    if (transb) { var s2 = tela(PIN[transb.pin].xy); transb.e.style.transform = "translate3d(" + s2[0].toFixed(1) + "px," + s2[1].toFixed(1) + "px,0)"; }
  }
  function mostraPinos(ids, focos) {
    visiveis = {}; foco = {};
    ids.forEach(function (id) { rotulo(id); visiveis[id] = true; });
    (focos || []).forEach(function (id) { foco[id] = true; });
    sobrepoe();
  }
  function transbordo(pin, de, para) {
    tiraTransbordo();
    var e = el("div", { "class": "m5-transb" }, camRot);
    e.innerHTML = '<span class="m5-tb">' + ic(de) + '<svg class="m5-seta" viewBox="0 0 16 8" aria-hidden="true"><path d="M1 4h12M10 1l3 3-3 3"/></svg>' + ic(para) + "</span>";
    transb = { e: e, pin: pin }; sobrepoe();
    requestAnimationFrame(function () { e.classList.add("m5-on"); });
  }
  function tiraTransbordo() { if (transb) { var e = transb.e; e.classList.remove("m5-on"); setTimeout(function () { e.remove(); }, 400); transb = null; } }

  /* ------------------------------------------------------------ interface */
  var atual = -1, etapa = -1, auto = true, fim = false;
  function montaCtrl() {
    ctrl.hidden = false;
    ctrl.innerHTML = '<button type="button" class="m5-bt" data-a="tocar"></button><button type="button" class="m5-bt m5-bt-txt" data-a="geral" aria-label="' + esc(ui.geralRot) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><span>' + esc(ui.geral) + '</span></button>';
    ctrl.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      if (b.dataset.a === "geral") { auto = false; visaoGeral(); return; }
      if (fim) { auto = false; tocar(atual < 0 ? 0 : atual, 0); return; }
      if (atual < 0 && !naAbertura) { auto = true; tocar(primeira(), 0); return; }
      tocando = !tocando; raiz.classList.toggle("m5-pausa", !tocando); atualizaBotao(); liga();
    });
    atualizaBotao();
  }
  function atualizaBotao() {
    var b = ctrl.querySelector('[data-a="tocar"]'); if (!b) return;
    var modo = fim ? "repetir" : (tocando && (atual >= 0 || naAbertura) ? "pausar" : "tocar");
    var d = { tocar: "M8 5.5v13l10.5-6.5Z", pausar: "M8.5 5.5v13M15.5 5.5v13", repetir: "M5 12a7 7 0 1 0 2.1-5M5 4.5V9h4.5" }[modo];
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + d + '" fill="' + (modo === "tocar" ? "currentColor" : "none") + '" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    b.setAttribute("aria-label", ui[modo]); b.title = ui[modo];
  }
  function montaTrilha(c) {
    var h = "";
    c.passos.forEach(function (p, i) {
      if (i) h += '<span class="m5-elo" aria-hidden="true"><i></i></span>';
      h += '<button type="button" class="m5-etapa" data-e="' + i + '" aria-label="' + esc(ui.etapa + " " + (i + 1) + " " + ui.de + " " + c.passos.length + ": " + p.n) + '">' +
           '<span class="m5-eic">' + ic(p.m) + '</span><span class="m5-enome">' + esc(p.n) + "</span></button>";
    });
    trilha.innerHTML = h; filme.hidden = false;
  }
  function marcaTrilha(i) {
    [].forEach.call(trilha.querySelectorAll(".m5-etapa"), function (b, k) {
      b.classList.toggle("m5-feita", k < i); b.classList.toggle("m5-agora", k === i); b.setAttribute("aria-current", k === i ? "step" : "false");
    });
  }
  function enchElo(i, u) {                                    // o elo entre a etapa i e a i+1 enche junto com a viagem
    var e = trilha.querySelectorAll(".m5-elo i");
    [].forEach.call(e, function (x, k) { x.style.transform = "scaleX(" + (k < i ? 1 : (k === i ? u : 0)) + ")"; });
  }
  function escreveTexto(c, i) {
    if (!c) { texto.innerHTML = '<p class="m5-dica">' + esc(ui.escolha) + ".</p>"; return; }
    var p = c.passos[i];
    texto.innerHTML = '<p class="m5-tcab"><span class="m5-tic">' + ic(p.m) + "</span>" + esc(ui.etapa + " " + (i + 1) + " " + ui.de + " " + c.passos.length) + " · <b>" + esc(p.n) + '</b></p><p class="m5-tfrase">' + esc(p.t) + "</p>" + (p.t2 ? '<p class="m5-tsub">' + esc(p.t2) + "</p>" : "");
    texto.classList.toggle("m5-trava", p.m === "trava"); info.classList.toggle("m5-so-cta", p.m === "trava");
    texto.classList.remove("m5-entra"); void texto.offsetWidth; texto.classList.add("m5-entra");
  }
  function escreveInfo(c) {
    if (!c) { info.innerHTML = ""; return; }
    var msg = ui.msg.replace("{carga}", c.carga.toLowerCase()).replace("{servico}", (c.servico || "").toLowerCase());
    var ct = D.contato || { tipo: "whatsapp", tel: D.tel }, mail = ct.tipo === "email";
    var href = mail ? "mailto:" + ct.email + "?subject=" + encodeURIComponent(ct.assunto || "") + "&body=" + encodeURIComponent(msg)
                    : "https://wa.me/" + ct.tel + "?text=" + encodeURIComponent(msg);
    info.innerHTML = '<p class="m5-papel"><b>' + esc(ui.papel) + ".</b> " + esc(c.papel) + "</p>" +
      (c.servico ? '<p class="m5-serv">' + esc(ui.ajudo) + ': <b>' + esc(c.servico) + "</b></p>" : "") +
      '<a class="m5-botao" data-msg-fixa="1" data-acao="' + (mail ? "email" : "whatsapp") + "-mapa-" + c.id + '" href="' + esc(href) + '"' + (mail ? "" : ' target="_blank" rel="noopener"') + ">" + esc(ui.botao) + "</a>";
  }
  function marcaChips(i) { chips.forEach(function (b, k) { b.setAttribute("aria-pressed", k === i ? "true" : "false"); }); }

  /* ------------------------------------------------------------ roteiro */
  var MOV = ["rodo", "ferro", "mar"];
  function modoVizinho(c, i, passo) { for (var k = i + passo; k >= 0 && k < c.passos.length; k += passo) if (MOV.indexOf(c.passos[k].m) >= 0) return c.passos[k].m; return null; }
  function pinosAte(c, i) { return c.passos[Math.min(i, c.passos.length - 1)].pin.slice(); }   // so os rotulos da etapa atual
  function durViagem(ids) {
    var m = LEGS[ids[0]].m, maior = 0;
    ids.forEach(function (id) { maior = Math.max(maior, prep(id).len); });
    if (m === "rodo") return Math.max(2400, Math.min(4600, 1800 + maior * 20));
    if (m === "ferro") return Math.min(5200, 2800 + maior * 6);
    return Math.min(7800, 3200 + maior * 2.6);
  }
  function leitura(t) { return Math.max(2000, t.length * 44); }

  async function rodaEtapa(ci, i, g) {
    var c = CAD[ci], p = c.passos[i];
    etapa = i; marcaTrilha(i); enchElo(i, 0); escreveTexto(c, i); tiraTransbordo();
    mede("etapa", { cadeia: c.id, etapa: i + 1, de: c.passos.length, auto: auto ? 1 : 0 });
    mostraPinos(pinosAte(c, i), []);
    await camera(p.cam, g); if (!vivo(g)) return;
    mostraPinos(pinosAte(c, i), p.foco);
    var gasto = 0;
    if (p.m === "mar" && c.origem && c.origem.length) c.origem.forEach(function (d) { solta(vis.dest, d, .75, 900); });
    if (p.legs.length) {
      var principal = p.legs.reduce(function (a, b) { return prep(b).len > prep(a).len ? b : a; }, p.legs[0]);
      var ks = p.legs.map(function (id) { traco(id); return novaCarga(id, id === principal, p.m); });
      var dur = durViagem(p.legs);
      await anima(dur, function (u) {
        var e = p.m === "rodo" ? easeOut(u) : ease(u);
        ks.forEach(function (k, j) { k.f = e; desenha(p.legs[j], e); });
        enchElo(i, u);
      });
      if (!vivo(g)) return;
      limpaCargas();
      if (p.m === "mar" && c.destino.length) { c.destino.forEach(function (d) { solta(vis.dest, d, 1, 900); }); mostraPinos(pinosAte(c, i), p.foco); }
      gasto = dur;
    } else {
      var de = modoVizinho(c, i, -1), para = modoVizinho(c, i, 1);
      if (p.foco.length && de && para && de !== para) transbordo(p.foco[0], de, para);   // so quando ha troca de modal de fato
      await anima(900, function (u) { enchElo(i, u); });
    }
    await espera(Math.max(1300, leitura(p.t) - gasto * .55));
  }

  async function tocar(ci, i0) {
    geracao++; var g = geracao;
    tarefas = tarefas.filter(function (t) { return t.ger === -1; });
    fim = false; tocando = true; raiz.classList.remove("m5-pausa"); raiz.classList.add("m5-ativo");
    var c = CAD[ci], nova = ci !== atual || i0 === 0;
    atual = ci; marcaChips(ci); escreveInfo(c); atualizaBotao(); ctrl.classList.add("m5-com-geral");
    limpaCargas(); tiraTransbordo();
    if (nova) { limpaRotas(); for (var d in vis.dest) solta(vis.dest, d, 0, 500); montaTrilha(c); }
    solta(vis, "ouro", .24, 600);
    // ao pular para uma etapa: o que vem antes ja fica desenhado; o resto volta a zero
    c.passos.forEach(function (p, k) { p.legs.forEach(function (id) { desenha(id, k < i0 ? 1 : 0); }); });
    if (!nova) c.destino.forEach(function (d) { solta(vis.dest, d, 0, 300); });
    liga();
    for (var i = Math.min(i0, c.passos.length - 1); i < c.passos.length; i++) { await rodaEtapa(ci, i, g); if (!vivo(g)) return; }
    mostraPinos(pinosAte(c, c.passos.length - 1), c.destino); marcaTrilha(c.passos.length);
    if (auto && !reduz) { await espera(3200); if (!vivo(g)) return; tocar((ci + 1) % CAD.length, 0); }
    else { fim = true; atualizaBotao(); }
  }

  // ordem por idioma: o estrangeiro ve o pais dele acender primeiro
  function primeira() {
    var l = (document.documentElement.lang || "pt").slice(0, 2), alvo = { zh: "graos", en: "gusa" }[l] || "graos", ix = 0;
    CAD.forEach(function (c, i) { if (c.id === alvo) ix = i; }); return ix;
  }
  // abertura: todas as cadeias desenhando juntas (a escala em 5 segundos), depois o mergulho na primeira
  var naAbertura = false;
  async function abertura() {
    geracao++; var g = geracao; naAbertura = true; atualizaBotao(); tarefas = tarefas.filter(function (t) { return t.ger === -1; });
    raiz.classList.add("m5-ativo"); solta(vis, "ouro", .24, 600);
    texto.innerHTML = '<p class="m5-tfrase">' + esc(ui.intro) + "</p>"; texto.classList.remove("m5-entra"); void texto.offsetWidth; texto.classList.add("m5-entra");
    var ids = [], box = [1e9, 1e9, -1e9, -1e9], dests = [];
    CAD.forEach(function (c) {
      c.passos.forEach(function (p) { p.legs.forEach(function (id) { if (ids.indexOf(id) < 0) ids.push(id); }); });
      dests = dests.concat(c.destino);
    });
    ids.forEach(function (id) { prep(id).p.forEach(function (q) { box[0] = Math.min(box[0], q[0]); box[1] = Math.min(box[1], q[1]); box[2] = Math.max(box[2], q[0]); box[3] = Math.max(box[3], q[1]); }); });
    var w = box[2] - box[0], h = box[3] - box[1];
    mostraPinos([], []);
    await camera([box[0] - w * .04, box[1] - h * .06, w * 1.08, h * 1.12], g); if (!vivo(g)) return;
    await anima(2600, function (u) { var e = ease(u); ids.forEach(function (id) { desenha(id, e); }); }); if (!vivo(g)) return;
    dests.forEach(function (d) { solta(vis.dest, d, .8, 700); });
    await espera(1700); if (!vivo(g)) return;
    naAbertura = false; tocar(primeira(), 0);
  }
  function visaoGeral() {
    geracao++; var g = geracao; tarefas = tarefas.filter(function (t) { return t.ger === -1; });
    atual = -1; etapa = -1; fim = false; tocando = true; raiz.classList.remove("m5-ativo", "m5-pausa");
    limpaCargas(); tiraTransbordo(); limpaRotas(); for (var d in vis.dest) solta(vis.dest, d, 0, 500); solta(vis, "ouro", .6, 600);
    marcaChips(-1); ctrl.classList.remove("m5-com-geral"); filme.hidden = true; escreveTexto(null); escreveInfo(null); mostraPinos(D.geral, []); atualizaBotao();
    camera(D.br, g);
  }

  /* ------------------------------------------------------------ eventos */
  chips.forEach(function (b, i) { b.addEventListener("click", function () { auto = false; mede("escolhe", { cadeia: CAD[i].id }); tocar(i, 0); }); });
  trilha.addEventListener("click", function (e) { var b = e.target.closest(".m5-etapa"); if (!b || atual < 0) return; auto = false; tocar(atual, +b.dataset.e); });
  var rz, med = "";
  function reenquadra() { var m = palco.clientWidth + "x" + palco.clientHeight; if (m === med) return; med = m; mede(); vb = enquadra(alvo); chaveBase = ""; pinta(); }
  if ("ResizeObserver" in window) new ResizeObserver(function () { clearTimeout(rz); rz = setTimeout(reenquadra, 60); }).observe(palco);
  else window.addEventListener("resize", function () { clearTimeout(rz); rz = setTimeout(reenquadra, 120); });
  var comecou = false;
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      visivel = es[0].isIntersecting;
      if (visivel) {
        liga();
        if (!comecou && !reduz && qs.get("tour") !== "0") { comecou = true; setTimeout(function () { if (atual < 0 && auto) abertura(); }, 900); }
      }
    }, { threshold: 0.4 }).observe(palco);
  }
  document.addEventListener("visibilitychange", function () { if (!document.hidden) liga(); });

  /* ------------------------------------------------------------ partida */
  mede(); montaCtrl(); vb = enquadra(D.br); mostraPinos(D.geral, []); escreveTexto(null); pinta();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { for (var id in rotEls) rotEls[id]._w = 0; sobrepoe(); });
  var pc = qs.get("c");
  if (pc) { CAD.forEach(function (c, i) { if (c.id === pc) { comecou = true; auto = false; tocar(i, Math.max(0, (+qs.get("e") || 1) - 1)); } }); }
  if (location.hash === "#diag") {
    var dg = el("div", { "class": "m5-diag" }, palco), qn = 0, t1 = performance.now();
    (function f() { qn++; requestAnimationFrame(f); })();
    setInterval(function () {
      var t2 = performance.now(), fps = Math.round(qn * 1000 / (t2 - t1)); qn = 0; t1 = t2;
      dg.textContent = "calmo=" + calmo + " visivel=" + visivel + " tocando=" + tocando + " qps=" + fps + " relogio=" + Math.round(relogio / 1000) + "s tarefas=" + tarefas.length + " dpr=" + DPR + " " + W + "x" + H;
    }, 1000);
  }
  window.__m5 = { estado: function () { return { nBase: nBase, nLaco: nLaco, tPinta: Math.round(tPinta), visivel: visivel, tocando: tocando, relogio: relogio, atual: atual, etapa: etapa, vb: vb, tarefas: tarefas.length }; } };
  }
})();
