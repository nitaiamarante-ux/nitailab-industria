# Nitai Lab Indústria

Site de uma página do Nitai Morais: mineração e logística da mina ao porto (viabilidade de lote, netback, due diligence, estruturação logística) + diagnóstico operacional (TPS).

- URL: https://industria.nitailab.com.br (repo público `nitaiamarante-ux/nitailab-industria`, GitHub Pages da branch `main`, raiz; domínio próprio já configurado no Pages)
- HTML estático puro, sem build. Fontes do kit `nitai_lab` em `fontes.css` (base64, sem CDN).
- `apresentacao_nitai_lab_industria.pdf` = apresentação PJ, gerada de `_nitai_lab/frentes/minerio/site/apresentacao/apresentacao.html`.

## LEIA ANTES DE MEXER
- Intenção da página (para quem, pergunta, saída, fatos com fonte, o que fica fora do público): `_nitai_lab/frentes/minerio/site/INTENCAO_site_industria.md`.
- Método: `_nitai_lab/_commons/produtos/planta_do_site/SUPERFICIE.md` e `_commons/design/METODO_design.md`. Gate: `python3 _commons/design/gate/gate_visual.py index.html --marca nitai_lab`.
- Direção escura escolhida pelo Nitai em 28/10/2026 (`data-d="escura"` no `<html>`); as regras da clara ficam no CSS como reserva.
- ⛔ Nada de canal chinês, intermediadoras, ouro, logos de clientes ou números sem fonte na `BASE_CURRICULO_NITAI.md`.

## Publicar
`git add -A && git commit && git push` (Pages publica sozinho). DNS: CNAME `industria` → `nitaiamarante-ux.github.io` no Registro.br.

Histórico: 22/04/2026 primeira versão (escura, com logos); 28/10/2026 frente de mineração e logística, kit da marca, logos removidos, apresentação PDF.
