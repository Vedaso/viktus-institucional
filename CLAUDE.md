# Viktus Institucional

Site institucional do Grupo Viktus em `viktus.com.br`. Apresenta os produtos da família
com status em tempo real e serve como âncora para Meta Business Verification.

## Stack
- **Framework:** Astro 4+ (`output: 'static'`)
- **Deploy:** Cloudflare Pages
- **Domínio:** `viktus.com.br` (e `www.viktus.com.br`)
- **Repo:** `Vedaso/viktus-institucional`

## Produtos da família Viktus
| Produto | URL | Status |
|---|---|---|
| Viktus Finanças | `financas.viktus.com.br` | Em produção |
| Viktus Care | `care.viktus.com.br` | Em produção |
| Viktus Spaces | `spaces.viktus.com.br` | Em produção |
| Viktus Estudos | `estudos.viktus.com.br` | Em produção |
| Viktus Telas | `telas.viktus.com.br` | Em produção (Super Pizza) |


A home nova (aprovada pelo Victor em 18/11/2026) mostra 6 produtos: Finanças, Care, Spaces, Telas,
Agro e Tráfego (o Tráfego entrou por decisão dele nessa data, revendo a de 02/10). Argus segue fora.

**Sem Guri e sem CNPJ no site** (Victor, 18/11/2026: "tirar apenas do site, deixar no resto dos docs
por hora"). Privacidade e Termos citam só "Viktus" + contato@; voltam a ter razão social e CNPJ quando
o CNPJ da Viktus sair (aberto na Contajá). Atenção: a verificação da Meta usava o CNPJ no rodapé.

## Home (`src/pages/index.astro`) é GERADA
Não edite à mão. A fonte é `~/OneDrive/Documentos/Claude/scripts/viktus-institucional/preview-nova-home.py`:
`py preview-nova-home.py . src/pages/index.astro site` (grava também `public/produtos/*.png` e
`public/vendor/gsap.min.js`). Tema automático pelo aparelho (escuro/claro). Os botões de conversa
abrem o chat de ideias até existir o número de WhatsApp.

## Cloudflare
- Zone ID: `1d139dddd01f5f87a8d4bff43949f737`
- Account: `victor_omena@hotmail.com`
- Quem serve `viktus.com.br` e `www.viktus.com.br`: **este projeto Pages** (`viktus-institucional`).
  Mexer no Astro muda o site público.
- Worker `viktus-care-landing`: só na rota `viktus.com.br/care*` (arquivo: `viktus-care/infra/cloudflare/worker-landing-classic.js`).
  Não alcança a raiz — o fallback interno dele só roda dentro desse padrão de rota.
- **NÃO confundir com** `workers/care-router/` — rota `care.viktus.com.br/*` (produto diferente)
- Medido na API da Cloudflare em 27/07/2026 (rotas de Worker da zona + domínios do projeto Pages).

## Rota crítica — NÃO remover
`viktus.com.br/care/privacidade` e `viktus.com.br/care/termos` são servidos pelo Worker
`viktus-care-landing` e referenciados pelo Meta/WhatsApp Business do Care. Não mover.

## Comandos
```bash
npm run dev         # dev local
npm run build       # build estático para dist/ + gate de identidade
```

## Deploy
Push na `main` publica: `.github/workflows/deploy.yml` builda com `GIT_COMMIT`, manda para o
Pages e só passa depois de achar aquele commit na `<meta name="build-commit">` de
viktus.com.br. Deploy verde é deploy provado.

À mão, quando for preciso:
```bash
GIT_COMMIT=$(git rev-parse --short HEAD) npm run build
npx wrangler pages deploy dist/ --project-name viktus-institucional --branch main
```
Sem `GIT_COMMIT` o build sai marcado como `dev` e `scripts/check-build.mjs` avisa — esse build
não vai para produção.

Os secrets `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` estão no repo no GitHub; a fonte
deles é `Claude/secrets/cloudflare.env`.

## Estrutura
`src/layouts/Site.astro` é a casca de todas as páginas (head, marca, nav, rodapé, reveal) e
carrega `src/styles/site.css`. O que é de uma página só vive em `src/styles/<nome>.css`,
importado depois. Uma página é só conteúdo dentro de `<Site title description path>` — `path`
sempre com barra final, que é a forma que o Pages serve.

Até 05/09/2026 cada página tinha a sua cópia de tudo isso, com as fontes e as fotos em base64
dentro do CSS. Se algo parecer duplicado de novo, é regressão.

## Histórico
Os prompts das fases 0 a 4 e a auditoria de julho estão em `docs/historico/`.
Plano completo: `~/OneDrive/Documentos/Obsidian Vault/Viktus Institucional/`.
