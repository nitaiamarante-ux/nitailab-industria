# Nitai Lab · Logística e Operações

Site da frente minério/logística do Nitai Morais: logística de granéis e carga industrial no Brasil, da origem ao porto; desempenho da operação (TPS); verificação (due diligence técnica e logística).

- URL hoje: https://industria.nitailab.com.br. Decidido em 28/10/2026 que vira a raiz `nitailab.com.br` (ver `_nitai_lab/_commons/norte/AVISO_dominio_raiz_2026-10-28.md`, ordem da virada).
- HTML estático gerado: **edite `_fonte/gerar.py` (conteúdo) e `assets/site.css` (visual), depois `python3 _fonte/gerar.py`**. Não edite os `index.html` à mão (o gerador sobrescreve).
- Fotos: só licença livre, crédito no rodapé (`fotos/FONTES.md`; originais no SSD F, `fotos/_NO_SSD_F.md`). Logos: `logos/FONTES.md`. Cliente sem logo de qualidade fica fora.
- Pastas com `_` não são publicadas pelo Pages. `_prova/` fica fora do git.

## LEIA ANTES DE MEXER
- Guia: `_nitai_lab/frentes/minerio/site/GUIA_norteador_site_e_produtos.md` (D4 = o que não aparece; número OU local, nunca os dois).
- Método: `_nitai_lab/_commons/produtos/planta_do_site/SUPERFICIE.md` e `_commons/design/METODO_design.md`. Gate: `python3 _commons/design/gate/gate_visual.py <pagina>/index.html --marca nitai_lab` em cada página.
- Prévia local com links funcionando: `python3 -m http.server 8765` na raiz do repo.

## Publicar
`python3 _fonte/gerar.py && git add -A && git commit && git push` (Pages publica sozinho).

Histórico: 22/04/2026 primeira versão; 28/10/2026 tarde: frente de mineração (uma página); 28/10/2026 noite: site de 8 páginas, estilo "relatório de campo", marca Logística e Operações.
