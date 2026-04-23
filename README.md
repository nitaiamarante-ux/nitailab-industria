# Nitai Lab Indústria

Landing page da frente de consultoria em operações industriais do Nitai Morais.

- URL de destino: https://industria.nitailab.com.br
- Stack: HTML estático puro (sem build)
- Hospedagem: GitHub Pages

## Deploy (passo a passo)

### 1. Criar repositório no GitHub

Em github.com/nitaiamarante-ux (ou onde for sua conta), criar repositório público chamado `nitailab-industria`.

### 2. Push do conteúdo

```bash
cd /mnt/c/Users/Lenovo/projetos/nitailab-industria
git init
git add .
git commit -m "landing page inicial Nitai Lab Indústria"
git branch -M main
git remote add origin git@github.com:<usuario>/nitailab-industria.git
git push -u origin main
```

### 3. Ativar GitHub Pages

Em `Settings > Pages` do repositório:
- Source: `Deploy from a branch`
- Branch: `main` / pasta `/ (root)`
- Custom domain: `industria.nitailab.com.br`
- Enforce HTTPS: sim (depois que propagar)

### 4. Configurar DNS

No painel do registrador do domínio nitailab.com.br, adicionar registro CNAME:

```
Tipo: CNAME
Nome: industria
Valor: <usuario>.github.io
TTL: 3600
```

Propagação leva de minutos a algumas horas.

## Estrutura

- `index.html` — página única, CSS inline, conteúdo completo
- `favicon.svg` — mesmo favicon do nitailab.com.br (consistência visual)
- `CNAME` — arquivo lido pelo GitHub Pages pra apontar o domínio customizado
- `README.md` — este arquivo

## Manutenção

Qualquer atualização (texto, número, contato): editar `index.html`, commit, push. Deploy automático via GitHub Actions padrão do Pages.
