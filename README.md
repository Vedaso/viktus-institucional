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

Um push na `main` publica: `.github/workflows/deploy.yml` faz o build com `GIT_COMMIT`,
manda o `dist/` para o Pages e só passa depois de encontrar aquele commit na
`<meta name="build-commit">` de `viktus.com.br`. Ou seja, um deploy verde é um deploy provado.

À mão, quando for preciso:

```sh
GIT_COMMIT=$(git rev-parse --short HEAD) npm run build
npx wrangler pages deploy dist/ --project-name viktus-institucional --branch main
```

`npm run build` sem `GIT_COMMIT` marca as páginas como `dev` e não deve ir para produção —
`scripts/check-build.mjs` avisa.

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
