# Nitai Lab · Logística e Operações

Site da frente minério/logística do Nitai Morais: logística de granéis e carga industrial no Brasil, da origem ao porto; desempenho da operação (TPS); verificação (due diligence técnica e logística).

- URL hoje: https://industria.nitailab.com.br. Decidido em 28/10/2026 que vira a raiz `nitailab.com.br` (ver `_nitai_lab/_commons/norte/AVISO_dominio_raiz_2026-10-28.md`, ordem da virada).
- HTML estático gerado: **edite `_fonte/gerar.py` (conteúdo) e `assets/site.css` (visual), depois `python3 _fonte/gerar.py`**. Não edite os `index.html` à mão (o gerador sobrescreve).
- Fotos: só licença livre, crédito no rodapé (`fotos/FONTES.md`; originais no SSD F, `fotos/_NO_SSD_F.md`). Logos: `logos/FONTES.md`. Cliente sem logo de qualidade fica fora.
- Pastas com `_` não são publicadas pelo Pages. `_prova/` fica fora do git.
- O CSS entra como `site.css?v=<hash>` (calculado pelo gerador): mudou o CSS, rode o gerador, senão o navegador mistura página nova com CSS velho do cache (bug dos ícones gigantes, 28/10).

## LEIA ANTES DE MEXER
- Guia: `_nitai_lab/frentes/minerio/site/GUIA_norteador_site_e_produtos.md` (D4 = o que não aparece; número OU local, nunca os dois).
- Método: `_nitai_lab/_commons/produtos/planta_do_site/SUPERFICIE.md` e `_commons/design/METODO_design.md`. Gate: `python3 _commons/design/gate/gate_visual.py <pagina>/index.html --marca nitai_lab` em cada página.
- Prévia local com links funcionando: `python3 -m http.server 8765` na raiz do repo.

## Línguas (PT fonte, EN, ZH)
- O português é a fonte. Todo texto visível passa por `T()` em `_fonte/gerar.py`; EN (`/en/`) e ZH chinês simplificado (`/zh/`) saem de `_fonte/traducoes/en.json` e `zh.json`, no formato `{"<sha1(pt)[:12]>": {"pt": "...", "tr": "..."}}`.
- Mudou qualquer texto em português: o hash muda, a tradução some do JSON e **o build trava (exit 1, nada é gravado)** até EN e ZH serem atualizados. Pendências: `_fonte/traducoes/PENDENTES.json` (por pendente traz `parecido`, a tradução antiga mais próxima, pra ver o que mudou) e a contagem por língua no terminal.
- `python3 _fonte/gerar.py --rascunho` gera mesmo assim, com o PT no lugar do que falta: só pra prévia local, **nunca publicar** (o diretório `en/` e `zh/` fica com texto em português).
- `--podar` apaga dos JSONs as entradas órfãs (hash que nenhum texto usa mais); sem a flag elas só são listadas no aviso.
- Em EN/ZH a ação principal é e-mail (WhatsApp só no rodapé). PDFs: se existir `apresentacoes/en/<nome>.pdf` (ou `zh/`) o site usa; senão usa o PT.
- Política de privacidade e 404 só em PT.
- Nomes próprios em ZH (29/10): em caracteres, com o original entre parênteses quando ajuda a busca. Vale = 淡水河谷; Tubarão = 图巴朗港; EFVM = 维多利亚-米纳斯铁路; FCA = 中大西洋铁路; cidades transliteradas (阿拉瓜里, 皮拉波拉, 贝洛奥里藏特...). VLI, TPS, TSSC, CNPJ, CFEM e ANM ficam em sigla (explicadas na 1ª menção). Para não deixar caractere sozinho na linha: `<span class="nb">` na tradução.
- Seletor de língua (29/10): pílula com globo, língua atual preenchida em dourado. No celular: globo + língua atual na barra do topo (`<details class="lang-sel">`), e a pílula também dentro do menu.
- Aviso de língua (29/10): navegador em outra língua e a página existe nela (lê os `<link hreflang>`) = barra discreta acima do conteúdo, uma vez só (`localStorage nl_lang_aviso`), sem redirecionar.
- Celular (29/10): abertura com a foto inteira em cima (3:2, sem degradê nem texto por cima), título e botão principal logo abaixo, parágrafo depois do botão; botões com a largura do texto; secundário vira link sublinhado. Referências que embasaram: `_nitai_lab/frentes/minerio/site/pesquisa/referencias_celular_2026-10-29/LEIA.md`.

## Publicar
`python3 _fonte/gerar.py && git add -A && git commit && git push` (Pages publica sozinho).

Histórico: 22/04/2026 primeira versão; 28/10/2026 tarde: frente de mineração (uma página); 28/10/2026 noite: site de 8 páginas, estilo "relatório de campo", marca Logística e Operações.

## Medição e SEO/GEO (29/10/2026)
Plano: `_nitai_lab/frentes/minerio/site/PLANO_inteligencia_site_2026-10-29.md`.
- **`assets/medicao.js`** (entra em toda página gerada, PT/EN/ZH, com `?v=<hash>` como o CSS; não entra nos 3 redirecionamentos). Envia para `https://nl-tracker.nitai-amarante.workers.dev/event` (`site:"nitailab"`), por `sendBeacon` em `text/plain` (sem preflight), com fallback `fetch keepalive`. Sem cookies, sem IP. Código aleatório em `localStorage nl_vid`.
- Eventos: `nl_visita` (ao carregar), `nl_rolagem` (50 e 90, uma vez cada, campo `pct`), `nl_email` / `nl_whatsapp` / `nl_pdf` (clique com `data-acao` `email-`, `whatsapp-`, `pdf-`; na falta, pelo `href`), `nl_linkedin`, `nl_idioma` (`.lang a`, `.lang-lista a`), `nl_aviso_idioma` (`.aviso-lang a`). Origem na 1ª página da sessão (`sessionStorage nl_origem`): `ia-*`, `busca-*`, `linkedin`, `whatsapp`, `email`, `direto`, `outro`, ou `link-<x>` com `?o=<x>` / `utm_source`.
- Não envia em localhost, em `file:` nem se `localStorage.nl_dono === "1"`.
- **Modo dono:** pasta `eu-<chave>/` (noindex, fora do sitemap e do robots) grava `nl_dono=1`. A chave fica só no nome da pasta e em `_fonte/.dono_chave` (no .gitignore); o link completo está em `~/.secrets/nitailab_dono.txt`. Abrir uma vez em cada aparelho.
- **GEO:** `llms.txt` (EN com bloco PT, escrito à mão) e `robots.txt` com robôs de IA liberados (gerado por `robots()` em `gerar.py`).
- **IndexNow:** `<chave>.txt` na raiz e `_fonte/indexnow.py`, que envia todas as URLs do `sitemap.xml`. **Rodar depois de cada push que muda páginas**, quando o `<chave>.txt` já responde 200: `python3 _fonte/indexnow.py`.
- **GA4 (30/10/2026):** `GA4_ID = "G-5LR59PRVKW"` no topo de `_fonte/gerar.py` (propriedade própria do site, conta "Nitai Lab" `a389968396`, login nitai.amarante@gmail.com). O gtag é injetado no `<head>` de toda página gerada (PT/EN/ZH), não nos redirecionamentos nem em `eu-<chave>/`, e só carrega fora de localhost/`file:` e se `localStorage.nl_dono !== "1"`. Eventos disparados em `assets/medicao.js`, além do que vai ao nl-tracker: `generate_lead` (parâmetro `metodo` = email|whatsapp), `pdf_download`, `linkedin_click`. **Clarity (30/10/2026):** `CLARITY_ID = "z5zi7ieu6b"` no `gerar.py` (projeto "nitailab.com.br Logística"); entra no mesmo script, com a mesma trava de dono/localhost; vazio = não entra. Os projetos do Clarity estão no mesmo login e há também `w78jx5irys` (Resgate) e `umyg2q09xw` ("Instagram Destravado", de terceiro): não usar esses dois aqui.
- Política de privacidade: seção 7 (medição própria) acrescentada; 30/10 acrescentado parágrafo do GA4; o texto anterior não foi alterado (atende o app OAuth `nitai-lab`).

## Mensagem inteligente do WhatsApp/e-mail (29/10/2026 noite)
- Cada botão continua com a mensagem fixa da página no `href` (fallback sem JS; `MSG_PAGINA` em `gerar.py`). **`assets/mensagem.js`** (defer, `?v=<hash>`) reescreve o `href` no clique (capture) de `data-acao` `whatsapp-*` (troca `text` do wa.me) e `email-*` (troca só o `body` do mailto).
- Trilha em `sessionStorage nl_trilha` = `{p:[páginas de conteúdo por recência], pdf:bool}` (logistica, operacao, verificacao, casos, sobre; início e contato não entram; PDF = clique em `data-acao` `pdf-*`).
- Texto: `Oi, Nitai! Vi no seu site {lista}. {Baixei a apresentação. }{intenção}`; lista = página atual primeiro, depois as outras, máx. 3; intenção = do último serviço visitado, senão da página atual; lista vazia = mantém o href fixo.
- Fragmentos vêm de `<script type="application/json" id="msg-zap">` (função `config_msg()` em `gerar.py`, todos via `T()`, junções por língua no dicionário `JUNCAO`). Mudou texto = trava de tradução como sempre.
- A função `monta()` é exportada para Node (`require("assets/mensagem.js")`) para teste. Não depende do `medicao.js`; funciona em modo dono.
