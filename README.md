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
