/* Mensagem inteligente do WhatsApp/e-mail (29/10/2026): no clique, monta o texto com o caminho da pessoa na sessão.
   Sem JS vale o href fixo da página. Config vem de <script type="application/json" id="msg-zap"> (gerado por gerar.py). */
(function (raiz) {
  "use strict";
  var CONTEUDO = ["logistica", "operacao", "verificacao", "casos", "sobre"];
  var SERVICO = ["logistica", "operacao", "verificacao"];

  function junta(itens, cfg) {
    if (itens.length < 2) return itens.join("");
    return itens.slice(0, -1).join(cfg.v) + cfg.e + itens[itens.length - 1];
  }

  /* trilha = {p: [chaves em ordem de visita], pdf: bool}; atual = chave da página; devolve texto ou "" (manter href fixo) */
  function monta(cfg, trilha, atual) {
    var p = (trilha && trilha.p) || [];
    var lista = [];
    if (CONTEUDO.indexOf(atual) !== -1) lista.push(atual);
    p.forEach(function (k) { if (CONTEUDO.indexOf(k) !== -1 && lista.indexOf(k) === -1) lista.push(k); });
    lista = lista.slice(0, 3);
    if (!lista.length) return "";
    var intencao = "";
    for (var i = p.length - 1; i >= 0; i--) if (SERVICO.indexOf(p[i]) !== -1) { intencao = cfg.intencoes[p[i]]; break; }
    if (!intencao) intencao = cfg.intencoes[atual];
    if (!intencao) return "";
    var nomes = lista.map(function (k) { return cfg.partes[k]; });
    var partes = [cfg.abertura.replace("{lista}", junta(nomes, cfg))];
    if (trilha && trilha.pdf) partes.push(cfg.pdf);
    partes.push(intencao);
    return partes.join(cfg.sep);
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { monta: monta };
  if (typeof document === "undefined") return;

  var cfg = null;
  try { cfg = JSON.parse(document.getElementById("msg-zap").textContent); } catch (e) { return; }
  var CH = "nl_trilha";
  function le() { try { var t = JSON.parse(sessionStorage.getItem(CH)); if (t && t.p) return t; } catch (e) {} return { p: [], pdf: false }; }
  function grava(t) { try { sessionStorage.setItem(CH, JSON.stringify(t)); } catch (e) {} }

  try {
    if (CONTEUDO.indexOf(cfg.pagina) !== -1) {
      var t = le();
      t.p = t.p.filter(function (k) { return k !== cfg.pagina; });
      t.p.push(cfg.pagina);
      grava(t);
    }
  } catch (e) {}

  document.addEventListener("click", function (ev) {
    try {
      var a = ev.target && ev.target.closest ? ev.target.closest("a") : null;
      if (!a) return;
      var acao = a.getAttribute("data-acao") || "";
      if (acao.indexOf("pdf-") === 0) { var t = le(); t.pdf = true; grava(t); return; }
      var zap = acao.indexOf("whatsapp-") === 0, mail = acao.indexOf("email-") === 0;
      if (!zap && !mail) return;
      var texto = monta(cfg, le(), cfg.pagina);
      if (!texto) return;
      var href = a.getAttribute("href") || "", enc = encodeURIComponent(texto);
      if (zap && href.indexOf("wa.me/") !== -1) {
        a.setAttribute("href", href.split("?")[0] + "?text=" + enc);
      } else if (mail && href.toLowerCase().indexOf("mailto:") === 0) {
        var i = href.indexOf("?"), base = i === -1 ? href : href.slice(0, i), qs = i === -1 ? [] : href.slice(i + 1).split("&");
        qs = qs.filter(function (s) { return s && s.indexOf("body=") !== 0; });
        qs.push("body=" + enc);
        a.setAttribute("href", base + "?" + qs.join("&"));
      }
    } catch (e) {}
  }, true);
})(this);
