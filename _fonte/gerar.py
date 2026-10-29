#!/usr/bin/env python3
"""Gera as páginas estáticas do site Nitai Lab, Logística e Operações (fase 1 do GUIA_norteador, 28/10/2026).

Uso: python3 _fonte/gerar.py   (na raiz do repo). Escreve index.html, <pagina>/index.html, 404.html,
sitemap.xml e robots.txt. O visual mora em assets/site.css. Pastas com "_" não são publicadas pelo Pages.
Regras de conteúdo: GUIA §D4 (número OU local, nunca os dois; nada de canal, ouro, preço), D2 (vocabulário),
sem travessão. Cliente sem logo de qualidade fica fora (Nitai, 28/10).
"""
import difflib
import hashlib
import json
import os
import re
import sys
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://nitailab.com.br"
ZAP = "5531982976006"
EMAIL = "nitai@nitailab.com.br"
LINKEDIN = "https://www.linkedin.com/in/nitai-morais"
PDF = "/apresentacoes/Nitai_Lab_Apresentacao_Institucional.pdf"  # rodapé e ações gerais

# ---- Línguas: PT é a fonte; EN e ZH vêm de _fonte/traducoes/<lang>.json (ver README, seção "Línguas") ----
LANGS = {"pt": {"tag": "pt-BR", "og": "pt_BR", "prefixo": ""},
         "en": {"tag": "en", "og": "en_US", "prefixo": "/en"},
         "zh": {"tag": "zh-Hans", "og": "zh_CN", "prefixo": "/zh"}}
LANG = "pt"
TRAD_DIR = os.path.join(RAIZ, "_fonte", "traducoes")
TRAD = {}       # lang -> {hash: {"pt":..., "tr":...}}
USADOS = {l: set() for l in LANGS}   # hashes consultados no build
PENDENTES = {l: {} for l in LANGS}   # lang -> {hash: pt}
ERROS = []
NAO_TRADUZ = {"Nitai Morais", "Nitai Lab", "LinkedIn", "WhatsApp"}  # nomes próprios: passam direto
SLUGS = ["logistica", "operacao", "verificacao", "casos", "sobre", "contato"]
PAGINAS_L10N = ["/"] + [f"/{s}/" for s in SLUGS]  # as que existem nas 3 línguas


def hash_pt(texto):
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:12]


def carregar_traducoes():
    for lang in LANGS:
        if lang == "pt":
            continue
        caminho = os.path.join(TRAD_DIR, f"{lang}.json")
        TRAD[lang] = json.load(open(caminho, encoding="utf-8")) if os.path.exists(caminho) else {}
        for h, e in TRAD[lang].items():
            if "—" in e.get("tr", "") or "–" in e.get("tr", ""):
                ERROS.append(f"travessão na tradução {lang}/{h}")


def T(texto):
    """Texto em português -> texto da língua corrente. Falta tradução: registra a pendência e devolve o PT."""
    if LANG == "pt" or texto in NAO_TRADUZ or not texto.strip():
        return texto
    h = hash_pt(texto)
    USADOS[LANG].add(h)
    e = TRAD[LANG].get(h)
    if e and e.get("tr"):
        return e["tr"]
    PENDENTES[LANG].setdefault(h, texto)
    return texto


def TF(modelo, **valores):
    """T() de um bloco com marcadores {nome}: o hash é do modelo (estável), os valores entram depois."""
    t = T(modelo)
    for k, v in valores.items():
        if "{" + k + "}" not in t:
            ERROS.append(f"[{LANG}] tradução perdeu o marcador {{{k}}} em: {modelo[:50]!r}")
        t = t.replace("{" + k + "}", v)
    return t


def caminho_lang(lang, caminho):
    """Caminho da mesma página em outra língua. Páginas só em PT (política, 404) levam à home da língua."""
    if caminho not in PAGINAS_L10N:
        caminho = "/"
    return LANGS[lang]["prefixo"] + caminho


def prefixar_links(html):
    """Links internos para páginas ganham o prefixo da língua; assets não."""
    pre = LANGS[LANG]["prefixo"]
    if not pre:
        return html
    return re.sub(r'href="/((?:%s)/)?"' % "|".join(SLUGS), lambda m: f'href="{pre}/{m.group(1) or ""}"', html)


GLOBO = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6">'
         '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9s1.3-6.3 3.8-9z"/></svg>')


def seletor(caminho, classe):
    rot = {"pt": "PT", "en": "EN", "zh": "中文"}
    partes = []
    for l in LANGS:
        atual = ' aria-current="true"' if l == LANG else ""
        partes.append(f'<a href="@@{caminho_lang(l, caminho)}" hreflang="{LANGS[l]["tag"]}" lang="{LANGS[l]["tag"]}"{atual}>{rot[l]}</a>')
    return f'<div class="lang {classe}" role="group" aria-label="Idioma / Language / 语言">{GLOBO}' + "".join(partes) + "</div>"


def seletor_compacto(caminho):
    """Celular (29/10, pedido do Nitai: idioma fora do menu): globo + língua atual na barra do topo, abre a lista."""
    rot = {"pt": "PT", "en": "EN", "zh": "中文"}
    nome = {"pt": "Português", "en": "English", "zh": "中文"}
    itens = ""
    for l in LANGS:
        atual = ' aria-current="true"' if l == LANG else ""
        itens += f'<a href="@@{caminho_lang(l, caminho)}" hreflang="{LANGS[l]["tag"]}" lang="{LANGS[l]["tag"]}"{atual}>{nome[l]}</a>'
    return (f'<details class="lang-sel"><summary aria-label="Idioma / Language / 语言">{GLOBO}<span>{rot[LANG]}</span></summary>'
            f'<div class="lang-lista">{itens}</div></details>')


FOTOS = {
    "trem-min-1": ("Trem carregado de minério de ferro na ferrovia, visto do alto", "trem de minério",
                   "HVL (recortada e espelhada)", "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/",
                   "https://commons.wikimedia.org/wiki/File:Trem_da_Vale_com_minério_de_ferro_na_EFVM_e_BR-381_em_Timóteo_MG.JPG"),
    "panamax-1": ("Navio graneleiro entrando no porto de Santos", "navio graneleiro",
                  "Mike Peel", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
                  "https://commons.wikimedia.org/wiki/File:At_Santos,_Brazil_2018_087.jpg"),
    "panamax-2": ("Navio graneleiro no canal do porto", "navio graneleiro",
                  "Mike Peel", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
                  "https://commons.wikimedia.org/wiki/File:At_Santos,_Brazil_2018_091.jpg"),
    "aco-3": ("Bobinas de aço armazenadas em galpão", "bobinas de aço",
              "Arosset", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
              "https://commons.wikimedia.org/wiki/File:Steel_Coils_-_Leeco_Steel_-_Antonio_Rosset.jpg"),
    "minerio-1": ("Pilhas de minério de ferro com empilhadeira na mina", "minério de ferro",
                  "sarangib", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/",
                  "https://commons.wikimedia.org/wiki/File:Mining-856022.jpg"),
    "minerio-2": ("Pilha de minério de ferro sob correia transportadora", "minério de ferro",
                  "Peter Craven", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/",
                  "https://commons.wikimedia.org/wiki/File:Washed_and_dewatered_iron_ore_fines_are_stockpiled_(6025446558).jpg"),
}

# Fotos do próprio Nitai (celular, terminais e minas onde trabalhou; EXIF/GPS removido na conversão) e retratos do ensaio
# tratado que ele escolheu em 28/10. Intenção de cada uso: frentes/minerio/site/FOTOS_intencao.md.
PROPRIAS = {
    "real-armazem-graos": "Armazém graneleiro por dentro, com grão estocado e pá carregadeira",
    "real-vagoes-terminal": "Vagões graneleiros carregados ao lado da plataforma do terminal",
    "real-planta-mina": "Planta de beneficiamento de minério vista do alto",
    "real-carreta-minerio": "Carreta basculando minério na descarga",
    "real-carregamento-minerio": "Minério sendo carregado em vagões no pátio",
    "real-silos-terminal": "Silos e armazém de um terminal de grãos",
    "real-graos-armazenados": "Granel agrícola armazenado em pilha dentro do armazém",
    "real-kcl-armazenado": "Pilha de cloreto de potássio (KCl) dentro do armazém",
    "real-fio-maquina": "Bobinas de fio-máquina no pátio do terminal",
    "real-nitai-campo-mina": "Nitai Morais em visita técnica a uma planta de beneficiamento de minério",
}

CADEIAS = [
    ("Minério e siderurgia", ["vale", "usiminas", "arcelormittal", "gerdau", "aperam", "agera"]),
    ("Grãos", ["cargill", "adm", "bunge", "ldc", "amaggi", "caramuru", "granol", "sodrugestvo", "mitsui", "chs"]),
    ("Fertilizantes", ["heringer", "eurochem", "yara", "mosaic", "fertipar", "bunge"]),
    ("Combustíveis", ["petrobras", "br", "raizen", "ipiranga"]),
    ("Construção", ["queiroz-galvao"]),
]
NOMES = {"vale": "Vale", "usiminas": "Usiminas", "arcelormittal": "ArcelorMittal", "gerdau": "Gerdau", "aperam": "Aperam",
         "agera": "Agera", "cargill": "Cargill", "adm": "ADM", "bunge": "Bunge", "ldc": "Louis Dreyfus Company",
         "amaggi": "Amaggi", "caramuru": "Caramuru", "granol": "Granol", "sodrugestvo": "Sodrugestvo", "marubeni": "Marubeni",
         "mitsui": "Mitsui", "chs": "CHS", "heringer": "Heringer", "eurochem": "EuroChem", "yara": "Yara", "mosaic": "Mosaic",
         "fertipar": "Fertipar", "petrobras": "Petrobras", "br": "BR", "raizen": "Raízen", "ipiranga": "Ipiranga",
         "queiroz-galvao": "Queiroz Galvão"}
PLACA_ESCURA = {"sodrugestvo"}
ESPELHO = {"trem-min-1"}  # espelhada para o trem ficar à direita, fora do texto (adaptação permitida pela CC BY; crédito diz "espelhada")
LOGO_MAIOR = {"fertipar", "mitsui", "yara"}

MENU = [("logistica", "Logística"), ("operacao", "Operação"), ("verificacao", "Verificação"),
        ("casos", "Casos"), ("sobre", "Sobre"), ("contato", "Contato")]

# Ícones oficiais (simple-icons 13.21.0, CC0): cada botão que leva para fora fala a língua da plataforma (Nitai, 28/10).
IC_ZAP = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>'
IC_IN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
IC_MAIL = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
IC_PDF = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>'
PULSO = '<svg viewBox="0 0 40 20" aria-hidden="true"><path d="M0 12 L8 12 L12 4 L16 16 L20 8 L24 12 L40 12" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def zap(origem, texto="Oi Nitai, vi o site da Nitai Lab e quero conversar."):
    return f"https://wa.me/{ZAP}?text=" + urllib.parse.quote(f"{T(texto)} [{origem}]")


ASSUNTO_EMAIL = "Contato pelo site da Nitai Lab"


def btn_zap(origem, rotulo="Falar no WhatsApp", texto=None, classe="btn btn-zap", topo=False):
    if LANG != "pt":  # comprador estrangeiro não usa WhatsApp: a ação principal vira e-mail (WhatsApp fica só no rodapé)
        corpo_msg = texto or "Oi Nitai, vi o site da Nitai Lab e quero conversar."
        href = f"mailto:{EMAIL}?subject=" + urllib.parse.quote(f"{T(ASSUNTO_EMAIL)} [{origem}]") + "&body=" + urllib.parse.quote(T(corpo_msg))
        rot = T("Enviar e-mail")
        rot_html = f"<span>{rot}</span>" if topo else rot
        # 29/10: o e-mail é a ação principal aqui, então herda o visual do botão do WhatsApp (dourado cheio), não o de botão secundário
        return f'<a class="{classe.replace("btn-zap", "btn-principal")}" data-acao="email-{origem}" href="{href}" aria-label="{rot}">{IC_MAIL}{rot_html}</a>'
    href = zap(origem, texto) if texto else zap(origem)
    return f'<a class="{classe}" data-acao="whatsapp-{origem}" href="{href}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">{IC_ZAP}{rotulo}</a>'


# Três apresentações (28/10, pedido do Nitai: "tem que ter mais de um"); fonte em _nitai_lab/frentes/minerio/site/apresentacao/gerar_decks.py
DECKS = {"institucional": "/apresentacoes/Nitai_Lab_Apresentacao_Institucional.pdf",
         "logistica": "/apresentacoes/Nitai_Lab_Logistica_e_Verificacao.pdf",
         "operacao": "/apresentacoes/Nitai_Lab_Diagnostico_Operacional.pdf"}


def pdf_url(caminho):
    """Em EN/ZH usa /apresentacoes/<lang>/<mesmo nome>.pdf se existir; senão o PDF em português."""
    if LANG != "pt":
        cand = f"/apresentacoes/{LANG}/{os.path.basename(caminho)}"
        if os.path.exists(os.path.join(RAIZ, cand.lstrip("/"))):
            return cand
    return caminho


def deck_de(origem):
    if origem.startswith(("logistica", "verificacao")):
        return DECKS["logistica"]
    if origem.startswith("operacao"):
        return DECKS["operacao"]
    return DECKS["institucional"]


def btn_pdf(origem):
    return f'<a class="btn btn-2" data-acao="pdf-{origem}" href="{pdf_url(deck_de(origem))}" target="_blank" rel="noopener">{IC_PDF}{T("Baixar a apresentação")}</a>'


def abertura(rot, h1, lead, acoes, foto=None, retrato=None):
    rot, h1, lead = T(rot), T(h1), T(lead)
    if retrato:  # retrato do Nitai ao lado, fundido ao fundo por degradê (sem ampliar além do nativo)
        src, alt = retrato
        alt = T(alt)
        return (f'<section class="abre-retrato"><div class="miolo"><div class="ar-texto"><div class="rot">{rot}</div><h1>{h1}</h1>'
                f'<p class="lead">{lead}</p><div class="acoes">{acoes}</div></div>'
                f'<div class="ar-foto"><img src="/fotos/{src}.webp" alt="{alt}" fetchpriority="high"></div></div></section>')
    if foto in PROPRIAS:
        img = f'<img src="/fotos/{foto}.webp" alt="{T(PROPRIAS[foto])}" fetchpriority="high">'
        return (f'<section class="abre">{img}<div class="miolo"><div class="rot">{rot}</div><h1>{h1}</h1>'
                f'<p class="lead">{lead}</p><div class="acoes">{acoes}</div></div></section>')
    if foto:
        alt, leg = T(FOTOS[foto][0]), T(FOTOS[foto][1])
        espelho = ' class="espelho"' if foto in ESPELHO else ""
        img = f'<img src="/fotos/{foto}.webp" alt="{alt}"{espelho} fetchpriority="high">'
        return (f'<section class="abre">{img}<div class="miolo"><div class="rot">{rot}</div><h1>{h1}</h1>'
                f'<p class="lead">{lead}</p><div class="acoes">{acoes}</div></div><div class="legenda">{T("Carga · ")}{leg}</div></section>')
    return (f'<section class="abre sem-foto"><div class="miolo"><div class="rot">{rot}</div><h1>{h1}</h1>'
            f'<p class="lead">{lead}</p><div class="acoes">{acoes}</div></div></section>')


def secao_clientes():
    linhas = []
    for nome, lista in CADEIAS:
        cel = []
        for l in lista:
            cls = ' class="escura"' if l in PLACA_ESCURA else ""
            icl = ' class="maior"' if l in LOGO_MAIOR else ""
            cel.append(f'<div{cls}><img src="/logos/{l}.svg" alt="{NOMES[l]}"{icl}></div>')
        linhas.append(f'<div class="cadeia"><div class="rot">{T(nome)}</div><div class="logos">{"".join(cel)}</div></div>')
    return (f'<section class="faixa clientes"><div class="miolo"><div class="rot">{T("Clientes")}</div><h2>{T("Clientes que atendi")}</h2>'
            f'<p class="sub">{T("Em 16 anos de Vale e VLI, nas cadeias de minério, grãos, fertilizantes e combustíveis.")}</p>'
            f'<div class="cadeias">{"".join(linhas)}</div></div></section>')


def fecho(origem, titulo, texto):
    return (f'<section class="fecho"><div class="miolo"><h2>{T(titulo)}</h2><p>{T(texto)}</p>'
            f'<div class="acoes">{btn_zap(origem)}{btn_pdf(origem)}</div></div></section>')


def faq(itens):
    # perguntas abertas, sem acordeão: resposta visível para quem lê, para o Google e para as IAs
    return '<div class="faq">' + "".join(f'<div class="pr"><h4>{T(q)}</h4><p>{T(r)}</p></div>' for q, r in itens) + "</div>"


def faq_ld(itens):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": T(q),
            "acceptedAnswer": {"@type": "Answer", "text": T(r)}} for q, r in itens]}


def u(caminho):
    return URL + LANGS[LANG]["prefixo"] + caminho


def pessoa():
    return {"@type": "Person", "@id": URL + "/#nitai", "name": "Nitai Morais", "alternateName": "Nitai Pada Amarante Morais",
            "jobTitle": T("Consultor de logística de granéis e operações industriais"),
            "description": T("16 anos no Grupo Vale (Vale e VLI), gestão de terminais integrados a ferrovia e porto."),
            "worksFor": {"@id": URL + "/#empresa"}, "sameAs": [LINKEDIN],
            "address": {"@type": "PostalAddress", "addressRegion": "MG", "addressCountry": "BR"},
            "alumniOf": ["Fundação Getulio Vargas", "PUC Minas", "Fundação Dom Cabral", "FUMEC"]}


def empresa():
    return {"@type": "ProfessionalService", "@id": URL + "/#empresa", "name": "Nitai Lab", "alternateName": T("Nitai Lab Logística e Operações"),
            "sameAs": [LINKEDIN], "slogan": T("Logística de granéis e carga industrial, da origem ao porto"),
            "legalName": "NP Consultoria e Serviços Ltda", "taxID": "68.698.300/0001-20", "url": URL + "/",
            "email": EMAIL, "telephone": "+55 31 98297-6006", "areaServed": "BR", "founder": {"@id": URL + "/#nitai"},
            "address": {"@type": "PostalAddress", "addressRegion": "MG", "addressCountry": "BR"},
            "knowsAbout": [T(x) for x in ["logística de granéis", "logística ferroviária", "logística portuária", "netback",
                                          "due diligence de mineração", "diagnóstico operacional", "Toyota Production System"]]}


def servico(nome, desc, caminho):
    return {"@type": "Service", "name": T(nome), "description": T(desc), "url": u(caminho),
            "provider": {"@id": URL + "/#empresa"}, "areaServed": "BR"}


VERSAO_CSS = hashlib.sha1(open(os.path.join(RAIZ, "assets", "site.css"), "rb").read()).hexdigest()[:8]
VERSAO_JS = hashlib.sha1(open(os.path.join(RAIZ, "assets", "medicao.js"), "rb").read()).hexdigest()[:8]


def pagina(caminho, titulo, descricao, corpo, fotos_usadas, ld, atual=None, origem="site"):
    L = LANGS[LANG]
    titulo, descricao = T(titulo), T(descricao)
    nav = "".join(f'<a href="/{s}/"{" aria-current=\"page\"" if s == atual else ""}>{T(n)}</a>' for s, n in MENU)
    cred = ""
    if fotos_usadas:
        partes = []
        for f in fotos_usadas:
            _, leg, autor, lic, lic_url, fonte = FOTOS[f]
            autor = autor.replace("(recortada e espelhada)", T("(recortada e espelhada)"))
            partes.append(f'<li>{T(leg).capitalize()}: <a href="{fonte}" rel="noopener">{autor}</a>, <a href="{lic_url}" rel="noopener">{lic}</a></li>')
        cred = f'<div class="creditos"><p>{T("Fotos ilustrativas, Wikimedia Commons.")}</p><ul>' + "".join(partes) + "</ul></div>"
    grafo = {"@context": "https://schema.org", "@graph": [pessoa(), empresa()] + ld}
    canon = u(caminho)
    hreflangs = ""
    if caminho in PAGINAS_L10N:
        hreflangs = "".join(f'<link rel="alternate" hreflang="{LANGS[l]["tag"]}" href="{URL}{caminho_lang(l, caminho)}">\n' for l in LANGS)
        hreflangs += f'<link rel="alternate" hreflang="x-default" href="{URL}{caminho}">\n'
    return f"""<!DOCTYPE html>
<html lang="{L["tag"]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<meta name="author" content="Nitai Morais">
<link rel="canonical" href="{canon}">
{hreflangs}<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{L["og"]}">
<meta name="theme-color" content="#1A1814">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/fontes.css">
<link rel="stylesheet" href="/assets/site.css?v={VERSAO_CSS}">
<script defer src="/assets/medicao.js?v={VERSAO_JS}"></script>
<script type="application/ld+json">{json.dumps(grafo, ensure_ascii=False)}</script>
</head>
<body>
<header class="topo"><div class="miolo">
<a class="marca" href="/" aria-label="{T("Nitai Lab, início")}">{PULSO}<b>NITAI LAB</b><span>{T("Logística e Operações")}</span></a>
<nav id="menu" aria-label="{T("Principal")}">{nav}{seletor(caminho, "lang-mob")}</nav>
<div class="topo-acoes">{seletor(caminho, "lang-desk")}{seletor_compacto(caminho)}{btn_zap(origem + "-topo", rotulo="<span><span class=\"so-desk\">Falar no </span>WhatsApp</span>", topo=True)}<button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu"><span></span>{T("Menu")}</button></div>
</div></header>
<main>
{corpo}
</main>
<footer class="rodape"><div class="miolo">
<div class="cols">
<div><a class="marca" href="/">{PULSO}<b>NITAI LAB</b><span>{T("Logística e Operações")}</span></a>
<p class="ent">{T("Logística de granéis e carga industrial no Brasil, da origem ao porto. NP Consultoria e Serviços Ltda, CNPJ 68.698.300/0001-20, Minas Gerais.")}</p></div>
<div><h4>{T("Frentes de atuação")}</h4><ul><li><a href="/logistica/">{T("Logística")}</a></li><li><a href="/operacao/">{T("Operação")}</a></li><li><a href="/verificacao/">{T("Verificação")}</a></li></ul></div>
<div><h4>Nitai Lab</h4><ul><li><a href="/sobre/">{T("Sobre")}</a></li><li><a href="/casos/">{T("Casos")}</a></li><li><a data-acao="pdf-rodape" href="{pdf_url(PDF)}">{T("Apresentação em PDF")}</a></li><li><a href="/politica-de-privacidade/">{T("Política de privacidade")}</a></li></ul></div>
<div><h4>{T("Contato")}</h4><ul><li><a class="com-ic" data-acao="whatsapp-rodape" href="{zap(origem + "-rodape")}" target="_blank" rel="noopener">{IC_ZAP}WhatsApp +55 31 98297-6006</a></li><li><a class="com-ic" data-acao="email-rodape" href="mailto:{EMAIL}">{IC_MAIL}{EMAIL}</a></li><li><a class="com-ic" href="{LINKEDIN}" rel="noopener">{IC_IN}LinkedIn</a></li></ul></div>
</div>
{cred}
</div></footer>
<script>
/* Cabeçalho suspenso (padrão Virtut, SUPERFICIE §4): compacto e claro ao rolar, com histerese (vira em 160 px, volta perto do topo); menu do celular. */
(function(){{var b=document.body,t=document.querySelector(".topo"),m=document.querySelector(".menu-botao");
function rola(){{var y=window.scrollY||0;if(y>160)b.classList.add("rolado");else if(y<6)b.classList.remove("rolado");}}
window.addEventListener("scroll",rola,{{passive:true}});rola();
m.addEventListener("click",function(){{var a=t.classList.toggle("menu-aberto");m.setAttribute("aria-expanded",a?"true":"false");}});}})();
/* Seletor do celular fecha ao tocar fora. Aviso de língua (29/10): navegador em outra língua e a página existe nela = barra discreta, uma vez só, sem redirecionar. */
(function(){{var d=document.querySelector(".lang-sel");if(d)document.addEventListener("click",function(e){{if(d.open&&!d.contains(e.target))d.open=false;}});
var K="nl_lang_aviso";try{{if(localStorage.getItem(K))return;}}catch(e){{}}
var cur=(document.documentElement.lang||"").slice(0,2),nav=((navigator.languages&&navigator.languages[0])||navigator.language||"").toLowerCase(),alvo;
if(nav.indexOf("zh")===0)alvo="zh";else if(nav.indexOf("pt")===0)alvo="pt";else if(nav)alvo="en";
if(!alvo||alvo===cur)return;var tag={{pt:"pt-BR",en:"en",zh:"zh-Hans"}}[alvo],l=document.querySelector('link[rel="alternate"][hreflang="'+tag+'"]');if(!l)return;
var tx={{en:["This page is also available in English.","English"],zh:["本页面有中文版。","中文"],pt:["Esta página também está em português.","Português"]}}[alvo];
var bar=document.createElement("div");bar.className="aviso-lang";bar.lang=tag;
bar.innerHTML='<div class="miolo"><span>'+tx[0]+'</span><a href="'+l.getAttribute("href")+'">'+tx[1]+' →</a><button type="button" aria-label="Fechar / Close">×</button></div>';
function marca(){{try{{localStorage.setItem(K,"1");}}catch(e){{}}}}
bar.querySelector("a").addEventListener("click",marca);bar.querySelector("button").addEventListener("click",function(){{marca();bar.remove();}});
var mn=document.querySelector("main");mn.parentNode.insertBefore(bar,mn);}})();
</script>
</body>
</html>
"""


# Ordem corrigida pelo Nitai (28/10): o terminal de transbordo vem depois da rodovia, não antes do porto. "é assim na vli,
# mas nao quer dizer que é assim em todo lugar": a nota abaixo da linha diz que o arranjo varia.
ROTA = """<section class="rota" aria-label="A cadeia, da origem ao porto"><div class="miolo"><ol>
<li>Origem<small>mina, fazenda, usina</small></li>
<li>Rodovia<small>carreta, bitrem, rodotrem</small></li>
<li>Terminal<small>transbordo, armazém, estoque</small></li>
<li>Ferrovia<small>vagão, janela, tarifa</small></li>
<li>Porto<small>fila, navio, embarque</small></li>
</ol><p class="rota-nota">Arranjo mais comum no granel de exportação. Há cadeias só rodoviárias, por cabotagem ou por hidrovia, e cada uma muda a conta.</p></div></section>"""

REGRAS = """<section class="faixa"><div class="miolo"><div class="rot">Como trabalho</div><h2>Princípios de trabalho</h2>
<div class="ofertas tres">
<div class="oferta"><h3>Tudo por escrito antes</h3><p>Escopo, prazo e valor definidos antes do início. Sem cobrança recorrente sem entrega definida e sem relatório genérico.</p></div>
<div class="oferta"><h3>Confidencialidade nos dois sentidos</h3><p>Contatos e informações recebidos em confiança não mudam de mão. Proponho acordo de confidencialidade e de não contorno, que protege as duas partes e quem fez a apresentação.</p></div>
<div class="oferta"><h3>Conversa antes de proposta</h3><p>A primeira conversa sobre o caso não tem custo. Havendo trabalho, definimos juntos o formato. Não havendo, você sai com uma avaliação objetiva.</p></div>
</div></div></section>"""


def inicio():
    corpo = abertura(
        "Nitai Morais · 16 anos de comercial, logística e operações na Vale e VLI",
        "Logística de granéis e carga industrial, da origem ao porto.",
        "Planejei terminais, ferrovia e porto por dentro e implantei o TPS com a própria Toyota. Hoje apoio empresas que embarcam minério, grãos, fertilizantes e gusa na decisão de rota, custo e risco, e operações de terminal, armazém e planta que precisam reduzir perdas.",
        btn_zap("inicio-abertura") + btn_pdf("inicio-abertura"), "trem-min-1")
    corpo += T(ROTA)
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Escala</div>
<h2>Experiência na escala real da cadeia</h2>
<div class="nums">
<div><b>R$ 500 mi</b><span>por ano de receita nas operações de terminais que planejei</span></div>
<div><b>15 mi t</b><span>de grãos exportados sob o meu planejamento</span></div>
<div><b>1,8 mi t</b><span>de gusa na exportação da carteira que conduzi</span></div>
<div><b>16 anos</b><span>no Grupo Vale, entre Vale e VLI</span></div>
</div></div></section>""")
    corpo += T("""<section class="faixa quem"><div class="miolo quem-grade">
<div class="quem-foto"><img src="/fotos/nitai-retrato-escuro.webp" alt="Nitai Morais"></div>
<div class="quem-texto"><div class="rot">Quem conduz o trabalho</div><h2>Nitai Morais</h2>
<p>Foram 16 anos dentro da cadeia: no comercial da Vale, no planejamento dos terminais da VLI e na gestão de operações com equipes de até 250 pessoas. Planejei capacidade, defendi orçamento, negociei com clientes e implantei o TPS com a consultoria da própria Toyota.</p>
<p>Hoje aplico essa experiência em decisões de rota, custo e risco e em operações que precisam render mais. Cada trabalho é conduzido por mim, do diagnóstico à entrega.</p>
<div class="acoes"><a class="btn btn-2" href="/sobre/">Ver a trajetória</a></div></div>
</div></section>""")
    corpo += secao_clientes()
    corpo += TF("""<section class="faixa sup"><div class="miolo"><div class="rot">Frentes de atuação</div>
<h2>Três frentes, uma mesma base: a operação vista por dentro</h2>
<div class="cartoes">
<a class="cartao" href="/logistica/"><img src="/fotos/real-vagoes-terminal.webp" alt="{alt_vagoes}"><div class="corpo"><span class="rot">Estratégia e estrutura logística</span><span class="q">Rota, custo e risco da carga, da origem ao porto</span><p>Estudo de rota e modal, alternativas, viabilidade, netback e risco logístico.</p><span class="ir">Ver Logística →</span></div></a>
<a class="cartao" href="/operacao/"><img src="/fotos/real-armazem-graos.webp" alt="{alt_armazem}"><div class="corpo"><span class="rot">Desempenho da operação · TPS</span><span class="q">Perdas da operação medidas em reais</span><p>Diagnóstico de 5 dias em terminal, armazém ou planta, com o método Toyota (TPS) e plano de 90 dias.</p><span class="ir">Ver Operação →</span></div></a>
<a class="cartao" href="/verificacao/"><img src="/fotos/real-planta-mina.webp" alt="{alt_planta}"><div class="corpo"><span class="rot">Verificação</span><span class="q">Mina, lote e contraparte documentados antes da assinatura</span><p>Para quem compra e para quem vende: fontes oficiais, laudo lido e capacidade real de escoar a carga.</p><span class="ir">Ver Verificação →</span></div></a>
</div></div></section>""", alt_vagoes=T(PROPRIAS['real-vagoes-terminal']), alt_armazem=T(PROPRIAS['real-armazem-graos']), alt_planta=T(PROPRIAS['real-planta-mina']))
    corpo += T(REGRAS)
    corpo += fecho("inicio-fecho", "Avaliação inicial do seu caso",
                   "Descreva em poucas linhas a carga, a operação ou o negócio. Retorno com uma primeira avaliação e o próximo passo recomendado.")
    ld = [{"@type": "WebSite", "name": "Nitai Lab", "url": u("/"), "inLanguage": LANGS[LANG]["tag"],
           "publisher": {"@id": URL + "/#empresa"}}]
    return pagina("/", "Logística de granéis, da origem ao porto | Nitai Lab",
                  "Consultoria de logística de granéis e carga industrial com 16 anos de Vale e VLI: estratégia e estrutura, desempenho da operação e verificação.",
                  corpo, ["trem-min-1"], ld, origem="inicio")


FAQ_LOG = [
    ("Você trabalha só com minério?", "Não. Trabalhei com minério, grãos, farelo, fertilizantes, gusa, produtos siderúrgicos e combustíveis. A lógica é a mesma: cada trecho tem custo, prazo, capacidade e dono."),
    ("O que é netback?", "É o que sobra para a origem depois de pagar cada trecho até o comprador: frete rodoviário, ferrovia, terminal, porto, frete marítimo, tributos e capital de giro. É o preço mínimo que fecha a conta na mina ou na fazenda."),
    ("Você contrata o frete ou opera a carga?", "Não sou transportador nem agente de carga. Desenho a cadeia, comparo alternativas, coordeno quem opera e acompanho os indicadores do lado de quem tem a carga."),
    ("Atende empresa estrangeira?", "Sim. Para quem compra, vende ou investe no Brasil de fora, faço o papel de olhos locais: quem opera o quê, onde a carga trava e com quem falar."),
]


def logistica():
    corpo = abertura("Estratégia e estrutura logística", "Rota, custo e risco da carga, da origem ao porto.",
                     "Granel se decide na logística. Antes de fechar um contrato de compra, venda ou transporte, mostro a conta trecho a trecho, as alternativas e onde está o risco.",
                     btn_zap("logistica-abertura", texto="Oi Nitai, vi a página de logística do site e quero conversar sobre uma carga.") + btn_pdf("logistica-abertura"),
                     "panamax-1")
    corpo += T(ROTA)
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Escopo</div><h2>Serviços</h2>
<div class="ofertas">
<div class="oferta"><span class="rot">Viabilidade</span><h3>Viabilidade e netback de lote ou de fluxo</h3><p>A conta trecho a trecho, por rota e por cenário de frete e preço. Você sai sabendo o preço mínimo na origem e qual rota vale a pena.</p></div>
<div class="oferta"><span class="rot">Alternativas</span><h3>Estudo de rota e modal</h3><p>Rodovia, ferrovia, cabotagem e porto comparados em custo, prazo, capacidade e risco, com o que confirmar em cotação antes de decidir.</p></div>
<div class="oferta"><span class="rot">Risco</span><h3>Análise de risco logístico</h3><p>Dependência de um só operador, capacidade contratada, take-or-pay, sazonalidade, regulação e a saúde de quem está do outro lado.</p></div>
<div class="oferta"><span class="rot">Estrutura</span><h3>Estruturação e coordenação da cadeia</h3><p>Plano logístico com rota, capacidades e contratos, programação de embarque e acompanhamento do fluxo até o navio ou o cliente final.</p></div>
<div class="oferta"><span class="rot">Entrada no Brasil</span><h3>Apoio local a empresas estrangeiras</h3><p>Para trading, comprador ou investidor estrangeiro: quem opera cada trecho, onde a carga trava, com quem falar e o que conferir antes de assinar.</p></div>
<div class="oferta"><span class="rot">Cargas</span><h3>Granel e carga industrial</h3><p>Minério de ferro e manganês, soja, milho e farelo, fertilizantes como KCl e ureia, gusa e produtos siderúrgicos.</p></div>
</div></div></section>""")
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Cargas</div><h2>Cargas que operei</h2>
<p class="intro">Fotos dos terminais e das minas onde trabalhei. Cada granel tem o seu jeito de armazenar, carregar e escoar.</p>
<div class="mosaico">
<figure><img src="/fotos/real-graos-armazenados.webp" alt="Granel agrícola armazenado em pilha dentro do armazém"><figcaption>Grãos e farelo</figcaption></figure>
<figure><img src="/fotos/real-kcl-armazenado.webp" alt="Pilha de cloreto de potássio (KCl) dentro do armazém"><figcaption>Fertilizante (KCl)</figcaption></figure>
<figure><img src="/fotos/real-carregamento-minerio.webp" alt="Minério sendo carregado em vagões no pátio"><figcaption>Minério de ferro</figcaption></figure>
<figure><img src="/fotos/real-fio-maquina.webp" alt="Bobinas de fio-máquina no pátio do terminal"><figcaption>Siderúrgicos</figcaption></figure>
</div></div></section>""")
    corpo += T("""<section class="faixa sup"><div class="miolo"><div class="rot">A conta</div><h2>O preço na origem é o que sobra depois de cada trecho</h2>
<p class="intro">Quem compra paga o preço de referência menos tudo o que existe entre a origem e o porão do navio. Quem não conhece cada trecho negocia no escuro.</p>
<div class="conta" aria-label="Como se forma o preço na origem">
<div><i>&nbsp;</i><b>Preço de referência</b><span>índice ou cotação, ajustado pela qualidade do lote</span></div>
<div><i>−</i><b>Frete marítimo</b><span>tipo de navio, rota, época</span></div>
<div><i>−</i><b>Porto</b><span>tarifa, estadia, janela</span></div>
<div><i>−</i><b>Ferrovia</b><span>tarifa e capacidade contratada</span></div>
<div><i>−</i><b>Rodovia</b><span>da origem ao terminal</span></div>
<div><i>−</i><b>Tributos e giro</b><span>impostos, câmbio, prazo de recebimento</span></div>
<div><i>=</i><b>Netback</b><span>o que sobra para a origem, o preço mínimo que fecha</span></div>
</div></div></section>""")
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Como funciona</div><h2>Etapas do trabalho</h2>
<ol class="passos">
<li><b>Conversa inicial</b><span>Carga, origem, destino, volume e prazo. Sem custo.</span></li>
<li><b>Escopo por escrito</b><span>O que entra, o que não entra, prazo e valor, antes de começar.</span></li>
<li><b>Entrega</b><span>Dossiê ou plano com a conta, as alternativas e o que confirmar.</span></li>
<li><b>Acompanhamento</b><span>Opcional, se você quiser que eu coordene a execução.</span></li>
</ol>
<div class="duas"><div class="caixa"><span class="rot">De onde vem</span><p>Planejei por dentro a cadeia de grãos e fertilizantes que vai do porto de Tubarão, pelas ferrovias EFVM e FCA, até terminais no interior de Minas e o cliente final, e a de minério e siderúrgicos para as usinas de Minas.</p></div>""")
    corpo += "\n<div><h3>" + T("Perguntas frequentes") + "</h3>" + faq(FAQ_LOG) + "</div></div></div></section>"
    corpo += fecho("logistica-fecho", "Envie os dados da carga para uma primeira avaliação", "Produto, origem, destino e volume. Retorno com a leitura inicial e o que precisa ser confirmado.")
    ld = [servico("Consultoria de logística de granéis", "Rota, modal, alternativas, viabilidade, netback e risco logístico para granéis e carga industrial no Brasil.", "/logistica/"), faq_ld(FAQ_LOG)]
    return pagina("/logistica/", "Consultoria logística ferroviária e portuária | Nitai Lab",
                  "Rota, modal, alternativas, viabilidade e risco logístico para minério, grãos, fertilizantes e siderúrgicos, da origem ao porto.",
                  corpo, ["panamax-1"], ld, atual="logistica", origem="logistica")


FAQ_OP = [
    ("Em que tipo de operação o diagnóstico funciona?", "Terminal, armazém, pátio, mina, usina, fábrica. O método é olhar o chão, medir tempos e movimentos por etapa e transformar cada perda em reais."),
    ("Quanto tempo leva?", "Cinco dias úteis no formato padrão: contexto, campo, esboço, validação com o time e apresentação."),
    ("Preciso parar a operação?", "Não. O trabalho acontece com a operação rodando, junto de operadores, liderança e indicadores."),
    ("Você implanta Lean e TPS?", "Sim. Implantei o Toyota Production System com a TSSC e montei a escola de TPS da VLI. O diagnóstico é a porta de entrada: mostra onde o método rende mais na sua operação. A implantação vem depois, como acompanhamento, com escopo próprio."),
    ("O que acontece depois?", "Você decide: seguir sozinho com o plano, contratar acompanhamento da implantação ou um projeto fechado. Cada um com escopo próprio."),
]


def operacao():
    corpo = abertura("Desempenho da operação · TPS e Lean", "Onde a sua operação perde dinheiro.",
                     "Em terminal, armazém, mina ou fábrica, o ganho grande raramente vem de tecnologia nova. Vem do que ninguém tem paciência de olhar. O método é o Toyota Production System que implantei com a TSSC, a consultoria da própria Toyota, aplicado do jeito que funciona no chão brasileiro.",
                     btn_zap("operacao-abertura", texto="Oi Nitai, vi a página de operação do site e quero conversar sobre a minha operação.") + btn_pdf("operacao-abertura"),
                     "real-armazem-graos")
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Diagnóstico de 5 dias</div><h2>Diagnóstico em cinco dias, com as perdas quantificadas em reais</h2>
<ol class="passos">
<li><b>Onde perde dinheiro</b><span>De três a cinco pontos críticos levantados no chão, com operadores, liderança e indicadores.</span></li>
<li><b>Cada perda em reais</b><span>Cada ponto vem com o valor por mês ou por ano.</span></li>
<li><b>Plano de 90 dias</b><span>Ações em ordem de custo e benefício, com responsáveis.</span></li>
<li><b>Devolutiva ao time</b><span>Apresentação presencial para quem vai executar.</span></li>
</ol></div></section>""")
    corpo += T("""<section class="faixa sup"><div class="miolo"><div class="rot">Temas</div><h2>Principais fontes de perda</h2>
<div class="ofertas">
<div class="oferta"><h3>Capacidade e gargalo</h3><p>A etapa que limita tudo, quase sempre distribuição de papéis e não falta de equipamento.</p></div>
<div class="oferta"><h3>Custo por tonelada</h3><p>Quanto custa cada tonelada movimentada e o que compõe esse número.</p></div>
<div class="oferta"><h3>Contratos e terceiros</h3><p>Serviços operacionais pagos por um escopo que a operação já não usa.</p></div>
<div class="oferta"><h3>Paradas de manutenção</h3><p>Planejamento e controle para parar sem perder a produção programada.</p></div>
</div></div></section>""")
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Resultados</div><h2>Resultados obtidos</h2>
<div class="nums">
<div><b>R$ 3,9 mi</b><span>economizados em um ano, com volume acima do orçado</span></div>
<div><b>R$ 8,1 mi</b><span>a menos no orçamento com o redesenho da descarga de vagões</span></div>
<div><b>+50%</b><span>de corte no orçamento operacional ao longo de três anos</span></div>
<div><b>R$ 2 mi</b><span>por ano de economia na reestruturação de contratos de serviço</span></div>
</div>
<div class="duas" style="margin-top:56px"><div><div class="rot">Método</div><h3 style="margin:10px 0 12px">Toyota Production System com a própria Toyota</h3>
<p class="t2">Liderei a implantação do TPS com consultoria direta da TSSC, o centro da Toyota que leva o método a empresas fora do Japão. O terminal virou a escola de TPS da VLI.</p>
<p class="t2">No Brasil, o TPS costuma chegar pela metade: ferramenta e auditoria. A metade que falta é tratar operador como cabeça pensante. É essa que eu levo.</p></div>
<div class="caixa"><span class="rot">Um teste para fazer amanhã</span><p>Pergunte aos operadores de um turno qual é a maior dificuldade deles na operação. Depois peça que proponham soluções.</p><p>Se você não se surpreender, ou há problema de clima e cultura, ou a operação já está muito afiada.</p></div></div>""")
    corpo += '\n<h3 style="margin-top:56px">' + T("Perguntas frequentes") + "</h3>" + faq(FAQ_OP) + '<div class="acoes"><a class="btn btn-2" href="/casos/">' + T("Ver os casos") + "</a></div></div></section>"
    corpo += fecho("operacao-fecho", "Solicite um diagnóstico", "Informe o tipo de operação e o principal problema. Retorno indicando por onde começar.")
    ld = [servico("Diagnóstico operacional de 5 dias", "Diagnóstico no chão de terminal, armazém ou planta: perdas em reais e plano de 90 dias.", "/operacao/"), faq_ld(FAQ_OP)]
    return pagina("/operacao/", "Consultoria TPS e Lean para operações | Nitai Lab",
                  "Diagnóstico de 5 dias com o Toyota Production System no chão de terminal, armazém ou planta: onde a operação perde dinheiro, em reais, e o plano de 90 dias",
                  corpo, [], ld, atual="operacao", origem="operacao")


FAQ_VER = [
    ("Isso substitui a due diligence jurídica?", "Não. É o complemento técnico e logístico dela. O advogado olha contratos e passivos; eu olho se a mina existe no papel e no chão, se produz o que diz e se a carga consegue chegar ao porto."),
    ("Você emite laudo técnico?", "Não. Laudo de qualidade e de reserva é do laboratório e do geólogo. Eu leio o laudo e digo o que ele significa para a logística e para o preço."),
    ("Quanto tempo leva?", "Um parecer rápido sai em poucos dias. O dossiê completo depende de quantos documentos a outra parte entrega."),
    ("Serve para quem está fora do Brasil?", "Sim. Comprador e investidor estrangeiro costumam pedir exatamente isso antes de qualquer proposta."),
]


def verificacao():
    corpo = abertura("Verificação", "Verificação técnica e logística antes da assinatura.",
                     "O que se comprova em documento oficial e o que a logística permite de verdade, para os dois lados do negócio: quem compra ou investe e quem vende ou capta. Se a carga não consegue sair, o negócio não existe.",
                     btn_zap("verificacao-abertura", texto="Oi Nitai, vi a página de verificação do site e quero conversar sobre uma mina ou um negócio.") + btn_pdf("verificacao-abertura"),
                     "real-planta-mina")
    # Os dois lados (sugestão da avaliação por público, sessão nitai-lab-88, 28/10): o dono de mina não pode ler
    # o Nitai só como o auditor que o comprador manda. Liga a OP-03 (dossiê) e OP-06 (mandato do lado da mina).
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Para quem</div><h2>Os dois lados do mesmo dossiê</h2>
<div class="ofertas">
<div class="oferta"><span class="rot">Quem compra ou investe</span><h3>Segurança antes de assinar</h3><p>Mina, lote e contraparte conferidos em fonte oficial, com o laudo lido e a capacidade real de escoar até o porto. Você sabe o que está comprando e o que pedir antes de seguir.</p></div>
<div class="oferta"><span class="rot">Quem vende ou capta</span><h3>O dossiê pronto antes do pedido</h3><p>Título na ANM, CFEM, licença, laudo lido e capacidade de escoar, organizados antes de o comprador ou o investidor pedirem. Oportunidade documentada negocia melhor e fecha mais rápido.</p></div>
</div></div></section>""")
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">O que é verificado</div><h2>Itens conferidos em fonte oficial</h2>
<div class="ofertas">
<div class="oferta"><span class="rot">ANM</span><h3>Título minerário</h3><p>Se o processo existe na Agência Nacional de Mineração, em nome de quem, em que fase e para qual substância.</p></div>
<div class="oferta"><span class="rot">CFEM</span><h3>Royalty da mineração em dia</h3><p>Quem recolhe a Compensação Financeira pela Exploração Mineral está produzindo e vendendo de fato.</p></div>
<div class="oferta"><span class="rot">Licenças</span><h3>Licença ambiental</h3><p>Se a licença cobre a operação e o volume que estão sendo oferecidos.</p></div>
<div class="oferta"><span class="rot">Contraparte</span><h3>Empresa do outro lado</h3><p>Sócios, tempo de existência, processos e dívidas públicas da empresa que vende ou compra.</p></div>
<div class="oferta"><span class="rot">Laudo</span><h3>Leitura do laudo de qualidade</h3><p>O que o laudo do laboratório diz sobre o teor e o que isso faz com o preço.</p></div>
<div class="oferta"><span class="rot">Logística</span><h3>Capacidade de escoar</h3><p>Se existe caminho, vaga e capacidade para a carga chegar ao porto no volume e no prazo prometidos.</p></div>
</div></div></section>""")
    corpo += T("""<section class="faixa sup"><div class="miolo"><div class="rot">Entregas</div><h2>Entregáveis</h2>
<div class="ofertas">
<div class="oferta"><h3>Parecer rápido</h3><p>Uma página: dá para seguir ou não, e por quê.</p></div>
<div class="oferta"><h3>Dossiê da mina</h3><p>O que está documentado, o que falta e o que pedir antes de assinar.</p></div>
<div class="oferta"><h3>Dossiê da contraparte</h3><p>Quem é a empresa do outro lado e o que pesa contra ela.</p></div>
<div class="oferta"><h3>Dossiê de ativo logístico</h3><p>Terminal, armazém ou contrato de capacidade: o que existe e o que trava.</p></div>
</div>
<div class="caixa" style="margin-top:32px"><span class="rot">O que eu não faço</span><p>Não emito laudo técnico nem parecer jurídico. Trabalho junto do geólogo, do laboratório e do advogado, e cubro o que fica entre eles: a operação e a logística.</p></div>""")
    corpo += '\n<h3 style="margin-top:56px">' + T("Perguntas frequentes") + "</h3>" + faq(FAQ_VER) + "</div></section>"
    corpo += fecho("verificacao-fecho", "Envie a documentação para análise", "Retorno indicando se o negócio se sustenta e quais documentos solicitar antes de seguir.")
    ld = [servico("Due diligence técnica e logística de mineração", "Verificação de mina e de contraparte em fonte oficial (ANM, CFEM, licenças, QSA) e da capacidade de escoar até o porto.", "/verificacao/"), faq_ld(FAQ_VER)]
    return pagina("/verificacao/", "Due diligence de mineração: técnica e logística | Nitai Lab",
                  "Antes de assinar: título na ANM, CFEM, licença, laudo lido, capacidade de escoar e a contraparte. Complemento da due diligence jurídica.",
                  corpo, [], ld, atual="verificacao", origem="verificacao")


def casos():
    corpo = abertura("Casos", "Casos de operação e logística.",
                     "Situações reais da minha trajetória na Vale e na VLI, descritas sem identificar pessoas e sem associar números a locais.",
                     btn_zap("casos-abertura"), "real-kcl-armazenado")
    corpo += TF("""<section class="faixa"><div class="miolo"><div class="casos">
<article class="caso"><img class="caso-foto" src="/fotos/real-carreta-minerio.webp" alt="{a1}"><span class="rot">Minério e siderurgia</span><h3>A caneta no vidro</h3><dl>
<dt>Situação</dt><dd>Um terminal de minério desenhado para carretas simples passou a receber bitrens e rodotrens. A fila ia para a rua, o cliente pressionava e a leitura de todos era: falta gente.</dd>
<dt>O que fiz</dt><dd>Passei uma hora parado num único ponto da operação, só observando. Cada operador era dono de um caminhão, não de uma etapa. Redesenhei os papéis por etapa na parede de vidro da sala de reunião, com o líder de turno, e o desenho virou padrão.</dd>
<dt>Resultado</dt><dd><b>Perto de 50% a mais de capacidade de descarga</b>, com a mesma equipe e sem investimento.</dd></dl></article>
<article class="caso"><img class="caso-foto" src="/fotos/real-vagoes-terminal.webp" alt="{a2}"><span class="rot">Grãos</span><h3>Cada vagão no seu 100%</h3><dl>
<dt>Situação</dt><dd>Frota de vagões heterogênea, carregamento sem padrão e, no pico da safra, demanda maior que a capacidade. Toda tonelada não carregada ia embora.</dd>
<dt>O que fiz</dt><dd>Cada vagão passou a ter a própria meta de peso, medida como porcentagem do seu limite. A reunião de produção saiu do escritório e foi para uma sala dentro da operação, na troca de turno.</dd>
<dt>Resultado</dt><dd><b>Mais de 100 toneladas a mais por trem</b> nos mesmos ativos, e receita adicional de milhões já no primeiro ano.</dd></dl></article>
<article class="caso"><img class="caso-foto" src="/fotos/real-carregamento-minerio.webp" alt="{a3}"><span class="rot">Minério e siderurgia</span><h3>Dez minérios em três pátios</h3><dl>
<dt>Situação</dt><dd>Um terminal funcionava como estoque avançado da composição química de uma siderúrgica, com até dez produtos de minério diferentes.</dd>
<dt>O que fiz</dt><dd>Controle de segregação por produto e por pátio, com rastreabilidade e janelas de descarga.</dd>
<dt>Resultado</dt><dd><b>Sem contaminação cruzada</b>, num terminal do qual dependia o faturamento diário do cliente.</dd></dl></article>
<article class="caso"><img class="caso-foto" src="/fotos/real-silos-terminal.webp" alt="{a4}"><span class="rot">Grãos</span><h3>A recuperação de um terminal</h3><dl>
<dt>Situação</dt><dd>Um terminal de grãos com o pior histórico da unidade em auditoria sanitária.</dd>
<dt>O que fiz</dt><dd>Rotina de gestão integrada, padrão por etapa e acompanhamento próximo como gerente interino.</dd>
<dt>Resultado</dt><dd><b>A maior nota em auditorias sanitárias</b>, a primeira certificação permanente do Ministério da Agricultura para grãos e recordes de produção mensal.</dd></dl></article>
</div></div></section>""", a1=T(PROPRIAS['real-carreta-minerio']), a2=T(PROPRIAS['real-vagoes-terminal']), a3=T(PROPRIAS['real-carregamento-minerio']), a4=T(PROPRIAS['real-silos-terminal']))
    corpo += fecho("casos-fecho", "Situação semelhante na sua operação?", "Descreva o contexto. Indico o primeiro ponto a analisar.")
    return pagina("/casos/", "Casos de operação e logística de granéis | Nitai Lab",
                  "Casos reais de terminal, ferrovia e porto, anonimizados: o desafio, o que foi feito e o resultado em ordem de grandeza.",
                  corpo, [], [{"@type": "CollectionPage", "name": T("Casos"), "url": u("/casos/")}], atual="casos", origem="casos")


def sobre():
    corpo = abertura("Sobre", "Nitai Morais", "16 anos no Grupo Vale, entre a Vale e a VLI, no comercial, no planejamento de terminais integrados a ferrovia e porto e na gestão da operação. Base em Minas Gerais.",
                     btn_zap("sobre-abertura") + f'<a class="btn btn-in" href="{LINKEDIN}" rel="noopener">{IC_IN}LinkedIn</a>', retrato=("nitai-retrato-editorial", "Nitai Morais"))
    corpo += T("""<section class="faixa"><div class="miolo"><div class="rot">Escala</div><h2>Escala da experiência</h2>
<div class="nums">
<div><b>R$ 500 mi</b><span>por ano de receita nas operações de terminais que planejei</span></div>
<div><b>15 mi t</b><span>de grãos exportados sob o meu planejamento</span></div>
<div><b>1,8 mi t</b><span>de gusa na exportação da carteira que conduzi</span></div>
<div><b>250</b><span>pessoas na maior equipe que liderei</span></div>
</div></div></section>""")
    corpo += T("""<section class="faixa sup"><div class="miolo"><div class="rot">Trajetória</div><h2>Trajetória por área de atuação</h2>
<div class="traj">
<div><div class="quando">2024 a hoje<small>Nitai Lab</small></div><div><h3>Consultoria em logística e operações</h3><p>Logística de granéis, viabilidade e verificação para quem compra, vende ou investe, e diagnóstico operacional para a indústria. Pela NP Consultoria e Serviços.</p></div></div>
<div><div class="quando">2022 a 2024<small>VLI</small></div><div><h3>Minério e siderurgia</h3><p>Gestão de planejamento, processos, manutenção e operação dos terminais de Santa Luzia e Ouro Preto, em Minas, com até dez produtos de minério segregados e parada geral planejada sem perder produção. Gerente interino por oito meses.</p></div></div>
<div><div class="quando">2019 a 2022<small>VLI</small></div><div><h3>Planejamento de terminais de grãos e fertilizantes</h3><p>Planejamento de longo, médio e curto prazo dos terminais de Araguari e Pirapora: dimensionamento, defesa de orçamento, investimentos e custos, e novos negócios com a capacidade ociosa e a sazonalidade de cada operação. Implantação do TPS com a TSSC e o primeiro modelo de EBITDA por unidade operacional da empresa. Gerente interino por seis meses.</p></div></div>
<div><div class="quando">2016 a 2019<small>VLI</small></div><div><h3>Cadeia de fertilizantes e recuperação de terminal</h3><p>Planejamento da cadeia do porto de Tubarão, pelas ferrovias EFVM e FCA, até o terminal e o cliente. Recuperação do terminal de grãos de Pirapora até a primeira certificação permanente do Ministério da Agricultura.</p></div></div>
<div><div class="quando">2008 a 2016<small>Vale e VLI</small></div><div><h3>Comercial</h3><p>Atendimento a siderúrgicas e distribuidoras de combustíveis em Belo Horizonte, São Luís e Ouro Branco, incluindo a carteira de gusa e a primeira cobrança de estadia de vagões a um grande cliente. Tricampeão do ranking de atendimento ao cliente.</p></div></div>
</div></div></section>""")
    corpo += T("""<section class="campo"><img src="/fotos/real-nitai-campo-mina.webp" alt="Nitai Morais em visita técnica a uma planta de beneficiamento de minério">
<div class="miolo"><div class="campo-texto"><div class="rot">Em campo</div><h2>Visita técnica a uma planta de beneficiamento de minério</h2>
<p>Verificação também é presença: ver a planta operando, as pilhas, o acesso e o caminho da carga até a ferrovia e o porto.</p>
<div class="acoes"><a class="btn btn-2" href="/verificacao/">Ver Verificação</a></div></div></div></section>""")
    corpo += secao_clientes()
    corpo += T("""<section class="faixa"><div class="miolo"><div class="duas">
<div><div class="rot">Método</div><h2 style="margin-top:14px">TPS com a própria Toyota</h2><p class="t2" style="margin-top:16px">Implantei o Toyota Production System com consultoria direta da TSSC, o centro da Toyota que leva o método a empresas fora do Japão. O terminal virou a escola de TPS da VLI, com imersões de um mês para profissionais da empresa inteira.</p></div>
<div><div class="rot">Formação</div><ul style="margin-top:18px;padding-left:20px;display:grid;gap:8px" class="t2">
<li>MBA em Logística e Supply Chain Management, FGV (em andamento)</li>
<li>Pós-graduação em Engenharia Multimodal, PUC Minas</li>
<li>Escola de Liderança VLI, Fundação Dom Cabral</li>
<li>Negociação Estratégica e Gestão de Conflitos, Ibmec</li>
<li>Administração de Empresas, FUMEC</li>
</ul></div></div></div></section>""")
    corpo += fecho("sobre-fecho", "Contato", "Pelo WhatsApp ou por e-mail. Em caso de indicação, informe quem indicou.")
    ld = [{"@type": "ProfilePage", "name": T("Sobre Nitai Morais"), "url": u("/sobre/"), "mainEntity": {"@id": URL + "/#nitai"}}]
    return pagina("/sobre/", "Nitai Morais, 16 anos de Vale e VLI | Nitai Lab",
                  "Gestão de terminais integrados a ferrovia e porto, TPS com a TSSC, primeiro modelo de EBITDA por unidade da VLI. Base em Minas Gerais.",
                  corpo, [], ld, atual="sobre", origem="sobre")


def contato():
    corpo = abertura("Contato", "Contato e condições de trabalho.",
                     "Atendimento pelo WhatsApp ou por e-mail. A primeira conversa sobre o caso não tem custo.",
                     btn_zap("contato-abertura") + (f'<a class="btn btn-mail" data-acao="email-contato" href="mailto:{EMAIL}">{IC_MAIL}{EMAIL}</a>' if LANG == "pt" else "") + f'<a class="btn btn-in" href="{LINKEDIN}" rel="noopener">{IC_IN}LinkedIn</a>', retrato=("nitai-trabalhando", "Nitai Morais trabalhando no notebook"))
    corpo += T(REGRAS)
    corpo += TF("""<section class="faixa sup"><div class="miolo"><div class="duas">
<div><div class="rot">Para encaminhar</div><h2 style="margin-top:14px">Apresentações em PDF</h2><p class="t2" style="margin-top:14px">Para enviar a quem decide, conforme o assunto.</p>
<ul class="lista-pdf"><li><a href="{d1}" target="_blank" rel="noopener">{ic_pdf}Institucional</a><span>quem sou, frentes, clientes e casos</span></li>
<li><a href="{d2}" target="_blank" rel="noopener">{ic_pdf}Logística e Verificação</a><span>rota, custo, risco e verificação antes da assinatura</span></li>
<li><a href="{d3}" target="_blank" rel="noopener">{ic_pdf}Diagnóstico Operacional</a><span>os 5 dias, entregáveis e resultados</span></li></ul></div>
<div class="caixa"><span class="rot">Quem responde</span><p>Nitai Morais. NP Consultoria e Serviços Ltda, CNPJ 68.698.300/0001-20, Minas Gerais.</p><p>WhatsApp +55 31 98297-6006 · {email} · <a href="{linkedin}" rel="noopener">LinkedIn</a></p></div>
</div></div></section>""", d1=pdf_url(DECKS["institucional"]), d2=pdf_url(DECKS["logistica"]), d3=pdf_url(DECKS["operacao"]), ic_pdf=IC_PDF, email=EMAIL, linkedin=LINKEDIN)
    return pagina("/contato/", "Como trabalho e contato | Nitai Lab",
                  "Escopo, prazo e valor por escrito, confidencialidade nos dois sentidos e resposta pelo WhatsApp ou e-mail.",
                  corpo, [], [{"@type": "ContactPage", "name": T("Contato"), "url": u("/contato/")}], atual="contato", origem="contato")


def politica():
    # Corpo LITERAL da política no ar desde 23/09/2026 (declarada ao Google no app OAuth nitai-lab, Perfil da Empresa).
    # Não editar o texto sem a sessão do Resgate: ver _commons/norte/AVISO_dominio_raiz_2026-10-28.md. Só a moldura é deste site.
    corpo_lit = open(os.path.join(RAIZ, "_fonte", "politica_corpo.html"), encoding="utf-8").read()
    corpo = f'<section class="faixa"><div class="miolo corrido politica"><h1>Política de Privacidade</h1>{corpo_lit}</div></section>'
    return pagina("/politica-de-privacidade/", "Política de Privacidade | Nitai Lab",
                  "Como a Nitai Lab coleta, usa e protege dados pessoais, em conformidade com a LGPD.", corpo, [], [], origem="politica")


def redirecionar(destino):
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>Redirecionando</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{destino}">
<meta http-equiv="refresh" content="0;url={destino}"></head>
<body><p>Esta página mudou para <a href="{destino}">{destino}</a>.</p></body></html>
"""


def erro404():
    corpo = abertura("Página não encontrada", "Essa página não existe.", "Talvez ela tenha mudado de lugar. Estas são as três portas do site:", "", None)
    corpo += T("""<section class="faixa"><div class="miolo"><div class="ofertas tres">
<a class="oferta" href="/logistica/" style="text-decoration:none;color:inherit"><h3>Logística</h3><p>Como a carga chega ao destino, a que custo e com que risco.</p></a>
<a class="oferta" href="/operacao/" style="text-decoration:none;color:inherit"><h3>Operação</h3><p>Onde a operação perde dinheiro.</p></a>
<a class="oferta" href="/verificacao/" style="text-decoration:none;color:inherit"><h3>Verificação</h3><p>Se a mina, o lote ou o parceiro são reais.</p></a>
</div></div></section>""")
    return pagina("/404.html", "Página não encontrada | Nitai Lab", "Essa página não existe. Veja Logística, Operação ou Verificação.", corpo, [], [], origem="404")


def escrever(rel, conteudo):
    caminho = os.path.join(RAIZ, rel)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)


def montar(lang):
    """Gera todas as páginas de uma língua. Devolve {caminho_relativo: html}."""
    global LANG
    LANG = lang
    pre = LANGS[lang]["prefixo"].lstrip("/")
    paginas = {"index.html": inicio(), "logistica/index.html": logistica(), "operacao/index.html": operacao(),
               "verificacao/index.html": verificacao(), "casos/index.html": casos(), "sobre/index.html": sobre(),
               "contato/index.html": contato()}
    if lang == "pt":  # política (texto literal de terceiro) e 404 só em PT
        paginas["politica-de-privacidade/index.html"] = politica()
        paginas["404.html"] = erro404()
    saida = {}
    for rel, html in paginas.items():
        if rel != "politica-de-privacidade/index.html":  # a política é texto literal de terceiro, não se edita
            if "—" in html or "–" in html:
                ERROS.append(f"travessão em {lang}/{rel}")
        html = prefixar_links(html).replace('href="@@', 'href="')
        destino = f"{pre}/{rel}" if pre else rel
        if rel != "404.html":  # caminhos relativos (abrem também fora do servidor); a 404 é servida em qualquer caminho, fica absoluta
            n = "../" * destino.count("/") or "./"
            html = html.replace('="/"', f'="{n}"').replace('="/', f'="{n}')
        saida[destino] = html
    return saida


def sitemap():
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', f"<urlset {ns}>"]
    for c in PAGINAS_L10N:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{LANGS[l]["tag"]}" href="{URL}{caminho_lang(l, c)}"/>' for l in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{URL}{c}"/>'
        for l in LANGS:
            linhas.append(f"<url><loc>{URL}{caminho_lang(l, c)}</loc>{alts}</url>")
    linhas.append(f"<url><loc>{URL}/politica-de-privacidade/</loc></url>")
    return "\n".join(linhas) + "\n</urlset>\n"


ROBOS_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Google-Extended", "Bingbot"]


def robots():
    blocos = ["User-agent: *\nAllow: /\n"] + [f"User-agent: {b}\nAllow: /\n" for b in ROBOS_IA]
    return "\n".join(blocos) + f"\nSitemap: {URL}/sitemap.xml\n"


def checar_traducoes(podar, rascunho):
    """A trava: pendências por língua, órfãs, 'parecido' e PENDENTES.json. Devolve o total de pendências."""
    lista, total = [], 0
    for lang in LANGS:
        if lang == "pt":
            continue
        orfas = {h: e for h, e in TRAD[lang].items() if h not in USADOS[lang]}
        # entrada com tradução vazia também conta como pendente (T já registrou)
        pend = PENDENTES[lang]
        total += len(pend)
        for h, pt in pend.items():
            melhor, mr = None, 0.5
            for oh, oe in orfas.items():
                sm = difflib.SequenceMatcher(None, pt, oe.get("pt", ""))
                if sm.real_quick_ratio() > mr and sm.quick_ratio() > mr:
                    r = sm.ratio()
                    if r > mr:
                        melhor, mr = oe, r
            item = {"lang": lang, "hash": h, "pt": pt}
            if melhor:
                item["parecido"] = {"pt": melhor.get("pt", ""), "tr": melhor.get("tr", ""), "similaridade": round(mr, 2)}
            lista.append(item)
        print(f"[{lang}] pendentes: {len(pend)} | órfãs: {len(orfas)}" + (" (podadas)" if podar and orfas else ""))
        if orfas and not podar:
            for h, e in orfas.items():
                print(f"    órfã {h}: {e.get('pt', '')[:70]!r}")
        if podar and orfas:
            novo = {h: e for h, e in TRAD[lang].items() if h in USADOS[lang]}
            with open(os.path.join(TRAD_DIR, f"{lang}.json"), "w", encoding="utf-8") as f:
                json.dump(novo, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
    os.makedirs(TRAD_DIR, exist_ok=True)
    with open(os.path.join(TRAD_DIR, "PENDENTES.json"), "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return total


if __name__ == "__main__":
    rascunho = "--rascunho" in sys.argv
    podar = "--podar" in sys.argv
    os.makedirs(TRAD_DIR, exist_ok=True)
    carregar_traducoes()
    saida = {}
    for lang in LANGS:  # a ordem importa pouco: tudo é montado em memória e só grava se a trava deixar
        saida.update(montar(lang))
    pend = checar_traducoes(podar, rascunho)
    if ERROS:
        print("ERROS (nada foi gravado):")
        for e in ERROS:
            print("  -", e)
        sys.exit(1)
    if pend and not rascunho:
        print(f"TRAVA: {pend} textos sem tradução. Nada foi gravado. Veja _fonte/traducoes/PENDENTES.json, "
              "traduza em en.json/zh.json e rode de novo (--rascunho gera mesmo assim, só pra prévia local).")
        sys.exit(1)
    for rel, html in saida.items():
        escrever(rel, html)
    RESGATE = "https://resgateseugoogle.nitailab.com.br/"
    for rel, destino in {"resgate-seu-google/index.html": RESGATE, "lp/index.html": RESGATE,
                         "privacidade/index.html": "/politica-de-privacidade/"}.items():
        escrever(rel, redirecionar(destino))  # Pages não faz 301: meta refresh + canonical (como o site-v2 já fazia)
    escrever("sitemap.xml", sitemap())
    escrever("robots.txt", robots())
    print("gerado:", ", ".join(saida))
    if pend:
        print(f"ATENÇÃO --rascunho: {pend} textos ainda em português nas páginas EN/ZH. NÃO PUBLICAR.")
