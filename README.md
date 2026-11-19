# viktus.com.br

Site institucional do Grupo Viktus, em Astro estático, publicado no Cloudflare Pages.
É a âncora do domínio: `viktus.com.br` e `www.viktus.com.br` são servidos por este projeto.

## Rodar

```sh
npm install
npm run dev        # http://localhost:4321
npm run build      # dist/ + o gate de identidade do build
```

## Publicar

Sem GitHub Actions desde 19/11/2026. Decisão do Victor: "remove isso do github testes locais e
deploy pela maquina" (a cobrança do GitHub travou em 18/11 e todo job falhava em segundos). O
Actions está desativado no repo e o workflow antigo está em `.github/workflows-desligados/`.
**Push na `main` não publica.** Do MASTER:

```sh
bash scripts/verificar.sh   # build com GIT_COMMIT (7 caracteres do HEAD) + gate check-build
bash scripts/publicar.sh    # verificar + wrangler pages deploy + prova do commit no ar
```

A prova busca `viktus.com.br` por até 2 minutos e exige que a `<meta name="build-commit">` seja o
commit que acabou de subir; um deploy verde é um deploy provado. O `publicar.sh` recusa rodar com
arquivo rastreado diferente do HEAD (a meta mentiria); `ALLOW_DIRTY=1` força.

`npm run build` sem `GIT_COMMIT` marca as páginas como `dev` e não deve ir para produção —
`scripts/check-build.mjs` avisa. O token vem de `Claude/secrets/cloudflare.env`, lido por parser.

## Como o site é montado

| | |
|---|---|
| `src/layouts/Site.astro` | a casca de todas as páginas: head, marca, navegação, rodapé, reveal |
| `src/styles/site.css` | o CSS de todo o site, carregado uma vez |
| `src/styles/*.css` | o que é de uma página só, importado depois do `site.css` |
| `src/pages/*.astro` | só o conteúdo, dentro de `<Site>` |
| `public/` | fontes, capturas e marcas, servidas como arquivo |

Uma página nova é um `.astro` em `src/pages/` que envolve o conteúdo em `<Site>` com
`title`, `description` e `path` — o `path` sempre com barra final, que é a forma que o
Pages serve.

## Onde mais mexer muda o site

- `public/_headers` — cabeçalhos de segurança e a política de cache dos ativos.
- `astro.config.mjs` — `site`, `trailingSlash` e o sitemap (o `/cv` fica fora dele).
- `CLAUDE.md` — o que a Cloudflare serve em cada rota, incluindo as do Worker do Care,
  que **não** são deste projeto.
