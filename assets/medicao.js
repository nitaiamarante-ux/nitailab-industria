/* Medição própria do site Nitai Lab (29/10/2026). Sem cookies, sem IP: o servidor recebe só o que está abaixo.
   Envia para o nl-tracker. Não envia em localhost, em file: nem no navegador do dono (localStorage nl_dono = "1"). */
(function () {
  "use strict";
  var ENDPOINT = "https://nl-tracker.nitai-amarante.workers.dev/event";
  var loc = window.location;
  if (loc.protocol !== "http:" && loc.protocol !== "https:") return;
  var host = (loc.hostname || "").toLowerCase();
  if (host === "localhost" || host === "127.0.0.1" || host === "[::1]" || host === "::1" || host === "0.0.0.0" ||
      host.slice(-10) === ".localhost") return;

  function ler(chave, st) { try { return window[st].getItem(chave); } catch (e) { return null; } }
  function gravar(chave, valor, st) { try { window[st].setItem(chave, valor); } catch (e) {} }

  if (ler("nl_dono", "localStorage") === "1") return;

  function limpa(s) {
    return String(s || "").toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 30);
  }
  function param(nome) {
    try { return new URLSearchParams(loc.search).get(nome); } catch (e) { return null; }
  }
  function hostDe(url) {
    if (!url) return "";
    try { return new URL(url).hostname.toLowerCase().replace(/^www\./, ""); } catch (e) { return ""; }
  }
  function eh(h, d) { return h === d || h.slice(-(d.length + 1)) === "." + d; }

  /* classificação igual à da Virtut, com as origens que interessam a este site */
  function classifica(referrer) {
    var o = limpa(param("o"));
    if (o) return "link-" + o;
    var utm = String(param("utm_source") || "").toLowerCase();
    if (utm) {
      if (utm.indexOf("chatgpt") === 0) return "ia-chatgpt";
      if (utm.indexOf("perplexity") === 0) return "ia-perplexity";
      if (utm.indexOf("copilot") === 0) return "ia-copilot";
      if (utm.indexOf("gemini") === 0) return "ia-gemini";
      if (utm.indexOf("claude") === 0) return "ia-claude";
      var u = limpa(utm);
      if (u) return "link-" + u;
    }
    var h = hostDe(referrer);
    if (h && h !== host.replace(/^www\./, "")) {
      if (eh(h, "chatgpt.com") || eh(h, "chat.openai.com")) return "ia-chatgpt";
      if (eh(h, "perplexity.ai")) return "ia-perplexity";
      if (eh(h, "copilot.microsoft.com")) return "ia-copilot";
      if (eh(h, "gemini.google.com")) return "ia-gemini";
      if (eh(h, "claude.ai")) return "ia-claude";
      if (h.indexOf("google.") !== -1) return "busca-google";
      if (h.indexOf("bing.") !== -1) return "busca-bing";
      if (eh(h, "duckduckgo.com") || h.indexOf("yahoo.") !== -1 || eh(h, "ecosia.org") || eh(h, "baidu.com") ||
          eh(h, "yandex.com") || eh(h, "yandex.ru") || eh(h, "search.brave.com") || eh(h, "sogou.com") || eh(h, "so.com") ||
          eh(h, "naver.com") || eh(h, "startpage.com")) return "busca-outra";
      if (eh(h, "linkedin.com") || eh(h, "lnkd.in")) return "linkedin";
      if (eh(h, "wa.me") || eh(h, "whatsapp.com") || eh(h, "web.whatsapp.com")) return "whatsapp";
      if (eh(h, "mail.google.com") || eh(h, "outlook.live.com") || eh(h, "outlook.office.com") || eh(h, "outlook.office365.com") ||
          h.indexOf("mail.yahoo.") !== -1 || eh(h, "mail.zoho.com") || eh(h, "zoho.com")) return "email";
      return "outro";
    }
    if (String(param("utm_medium") || "").toLowerCase() === "email") return "email";
    return "direto";
  }

  var origem = ler("nl_origem", "sessionStorage");
  if (!origem) {
    origem = classifica(document.referrer);
    gravar("nl_origem", origem, "sessionStorage");
  }

  var vid = ler("nl_vid", "localStorage");
  if (!vid) {
    vid = Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
    gravar("nl_vid", vid, "localStorage");
  }

  var lang = ((document.documentElement.lang || "pt").slice(0, 2).toLowerCase());
  var pagina = (loc.pathname || "/").replace(/index\.html$/, "");
  var refHost = hostDe(document.referrer);
  if (refHost === host.replace(/^www\./, "")) refHost = "";

  function envia(tipo, extra) {
    var corpo = { site: "nitailab", tipo: tipo, pagina: pagina, lang: lang, origem: origem, vid: vid, ref: refHost };
    if (extra) for (var k in extra) corpo[k] = extra[k];
    var texto = JSON.stringify(corpo);
    try {
      /* text/plain evita preflight de CORS; o worker lê com request.json() e não olha o content-type */
      if (navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([texto], { type: "text/plain;charset=UTF-8" }))) return;
    } catch (e) {}
    try {
      fetch(ENDPOINT, { method: "POST", body: texto, headers: { "Content-Type": "text/plain;charset=UTF-8" }, keepalive: true, credentials: "omit" })
        .catch(function () {});
    } catch (e) {}
  }

  /* visita */
  envia("nl_visita");

  /* rolagem: 50% e 90%, uma vez cada por página */
  var marcos = { 50: false, 90: false };
  function rolagem() {
    var de = document.documentElement, alt = Math.max(de.scrollHeight, document.body.scrollHeight);
    if (!alt) return;
    var pct = ((window.pageYOffset || de.scrollTop || 0) + (window.innerHeight || de.clientHeight || 0)) / alt * 100;
    [50, 90].forEach(function (m) {
      if (!marcos[m] && pct >= m) { marcos[m] = true; envia("nl_rolagem", { pct: m }); }
    });
    if (marcos[50] && marcos[90]) window.removeEventListener("scroll", rolagem);
  }
  window.addEventListener("scroll", rolagem, { passive: true });

  /* cliques, por delegação */
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a") : null;
    if (!a) return;
    var acao = a.getAttribute("data-acao") || "";
    var href = (a.getAttribute("href") || "").toLowerCase();
    if (a.closest(".aviso-lang")) return envia("nl_aviso_idioma");
    if (a.closest(".lang") || a.closest(".lang-lista")) return envia("nl_idioma");
    var tipo = "";
    if (acao.indexOf("email-") === 0) tipo = "nl_email";
    else if (acao.indexOf("whatsapp-") === 0) tipo = "nl_whatsapp";
    else if (acao.indexOf("pdf-") === 0) tipo = "nl_pdf";
    else if (href.indexOf("linkedin.com") !== -1) tipo = "nl_linkedin";
    else if (href.indexOf("mailto:") === 0) tipo = "nl_email";
    else if (href.indexOf("wa.me/") !== -1 || href.indexOf("whatsapp.com") !== -1) tipo = "nl_whatsapp";
    else if (href.split("?")[0].slice(-4) === ".pdf") tipo = "nl_pdf";
    if (tipo) envia(tipo);
    /* GA4 (aditivo): só existe se o gtag foi carregado (fora de localhost e do modo dono) */
    try {
      if (window.gtag) {
        if (tipo === "nl_email") gtag("event", "generate_lead", { metodo: "email" });
        else if (tipo === "nl_whatsapp") gtag("event", "generate_lead", { metodo: "whatsapp" });
        else if (tipo === "nl_pdf") gtag("event", "pdf_download");
        else if (tipo === "nl_linkedin") gtag("event", "linkedin_click");
      }
    } catch (e) {}
  }, true);
})();
