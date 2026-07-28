# Viktus Institucional

Site institucional do Grupo Viktus em `viktus.com.br`. Apresenta os 3 produtos da família
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
| Viktus Spaces | `spaces.viktus.com.br` | Em desenvolvimento |

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
npm run build       # build estático para dist/
npx wrangler pages deploy dist/ --project-name viktus-institucional
```

## Prompts de implementação
- `prompt-fase0.md` — Auditoria (read-only)
- `prompt-fase1.md` — Criar site em staging
- `prompt-fase2.md` — Redirect Rules Cloudflare
- `prompt-fase3.md` — Cutover `viktus.com.br` (risco médio)
- `prompt-fase4.md` — Meta Business Verification (guia)

## Plano completo
`~/OneDrive/Documentos/Obsidian Vault/Viktus/viktus-web-presence.md`
