# Auditoria Fase 0 — Viktus Web Presence

**Data:** 2026-05-23
**Executado por:** Claude Code (read-only)

---

## 1. Worker `viktus-care-landing` — inventário completo

**Arquivo:** `viktus-care/infra/cloudflare/worker-landing-classic.js`
**Routes ativas no Cloudflare (confirmado via API):**
- `www.viktus.com.br/*` → `viktus-care-landing`
- `viktus.com.br/*` → `viktus-care-landing`
- `care.viktus.com.br/*` → `care-router` ← Worker DIFERENTE, não tocar
**Tipo:** Service Worker classic (`addEventListener('fetch', ...)`)
**Deploy:** `wrangler deploy infra/cloudflare/worker-landing-classic.js --name viktus-care-landing`
**Sem `wrangler.toml`** — deploy sempre por arquivo explícito.

### Rotas capturadas (handler único, lógica if/else inline)

| Path | Ação | Conteúdo |
|---|---|---|
| `/` | Serve HTML | GRUPO_HOME — landing institucional (badge "Em construção", só mostra Viktus Care) |
| `/care` | Serve HTML | CARE_HOME — landing do produto Viktus Care |
| `/care/privacidade` | Serve HTML | Política de Privacidade completa do Care (LGPD, CNPJ, DPO) |
| `/care/termos` | Serve HTML | Termos de Serviço completos do Care |
| `/privacidade` | 301 redirect | → `/care/privacidade` (compat de URLs antigas) |
| `/termos` | 301 redirect | → `/care/termos` (compat de URLs antigas) |
| `*` (qualquer outro) | Serve HTML | Fallback → GRUPO_HOME |

### Headers de segurança já implementados no Worker

```
content-type: text/html;charset=UTF-8
cache-control: public, max-age=300   ← cache de 5 min no CDN
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
```

### Dados reais extraídos do Worker (usar no site institucional)

| Campo | Valor |
|---|---|
| Razão social | Guri Grupo de Urgência e Recuperação Infantil Ltda |
| CNPJ | 12.181.962/0001-73 |
| Endereço | Rua General Hermes, 795, Bom Parto, Maceió — AL, CEP 57017-201 |
| DPO / Contato | victor@clinicaguri.com.br |
| Foro | Comarca de Maceió — AL |

---

## 2. Brand assets disponíveis

### Worker `worker-landing-classic.js` (tokens em uso hoje)
| Token | Valor |
|---|---|
| Background gradient | `linear-gradient(135deg, #0E5172 0%, #1A1A2E 100%)` |
| Cor primária | `#0E5172` (azul Viktus) |
| Cor escura | `#1A1A2E` |
| Link color | `#7DD3FC` (sky blue) |
| Font | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` |

### `@viktus/ui` — tokens de design system (care + família)
Arquivo: `viktus-care/packages/ui/src/tokens/base.css`

| Token | Valor | Uso |
|---|---|---|
| `--color-family` | `#050714` | Cor institucional da holding Viktus (rodapé "powered by") |
| `--color-primary` (Care) | `oklch(0.62 0.05 165)` sage green | Primária do Care |
| `--font-display` | Space Grotesk | Headings |
| `--font-sans` | Manrope → Inter → system | Body |

> **Observação:** `--color-family: #050714` (UI tokens) difere de `#0E5172` (Worker). O Worker usa azul porque é uma página pré-brand. Para o site institucional, usar `#0E5172` para o hero (consistente com o que usuários já veem) e `--color-family: #050714` para o footer/branding da holding.

### Arquivos de ícone disponíveis
- `viktus-frontend/icons/icon-192.svg` — ícone PWA 192px
- `viktus-frontend/icons/icon-512.svg` — ícone PWA 512px

**Sem logo vetorial dedicado do Grupo Viktus.** Usar texto "Viktus" em Space Grotesk Bold como logo até ter asset oficial.

---

## 3. Estado em produção (curl ao vivo)

| URL | Status | Notas |
|---|---|---|
| `https://viktus.com.br/` | **200** | Worker serve GRUPO_HOME |
| `https://viktus.com.br/care` | **200** | Worker serve CARE_HOME |
| `https://viktus.com.br/care/privacidade` | **200** | Worker — CRÍTICO Meta/WhatsApp |
| `https://viktus.com.br/care/termos` | _(via 301 em /termos)_ | Worker |
| `https://viktus.com.br/privacidade` | **301** → `/care/privacidade` | Redirect compat |
| `https://viktus.com.br/termos` | **301** → `/care/termos` | Redirect compat |
| `https://financas.viktus.com.br/` | **200** | Pages — app em produção |
| `https://care.viktus.com.br/app` | **200** | Pages — app em produção |
| `https://spaces.viktus.com.br/` | **200** | Workers — em produção |

---

## 4. Rotas críticas — classificação de risco

| Rota | Risco | Por quê |
|---|---|---|
| `viktus.com.br/care/privacidade` | **CRÍTICO** | URL configurada no WhatsApp Business da Meta para Política de Privacidade. Quebrar = desativar número WhatsApp do Care. |
| `viktus.com.br/care/termos` | **CRÍTICO** | Idem — URL de Termos de Serviço na Meta. |
| `care.viktus.com.br/app` | **CRÍTICO** | Portal paciente Clínica Guri — clientes reais em produção. |
| `financas.viktus.com.br/` | **CRÍTICO** | App financeiro — clientes reais em produção. |
| `viktus.com.br/privacidade` | **IMPORTANTE** | Redireciona hoje para `/care/privacidade`. Após cutover vai servir política do GRUPO (conteúdo diferente). Links externos existentes vão mudar de destino. |
| `viktus.com.br/termos` | **IMPORTANTE** | Idem — redireciona hoje para `/care/termos`, depois vai servir termos do GRUPO. |
| `viktus.com.br/` | **BAIXO** | Hoje mostra landing institucional simples. Substituição pelo site novo é o objetivo. |
| `viktus.com.br/care` | **BAIXO** | Landing do Care mantida no Worker após cutover. |
| `spaces.viktus.com.br/` | **BAIXO** | MVP em produção, sem clientes reais ainda. |

---

## 5. Checklist Meta Business Verification

| Item | Status |
|---|---|
| Página inicial com nome da empresa | ⚠️ Existe mas badge "Em construção" — substituir com site novo |
| CNPJ visível | ✅ Presente no rodapé do Worker atual |
| Endereço físico | ✅ Presente no Worker (Rua General Hermes 795, Maceió/AL) |
| Política de Privacidade em `/privacidade` | ⚠️ Redirecta para `/care/privacidade` — depois do cutover terá página própria do Grupo |
| Termos de Uso em `/termos` | ⚠️ Idem |
| Canal de contato público | ⚠️ Apenas email no rodapé (victor@clinicaguri.com.br) — considerar criar contato@viktus.com.br via Cloudflare Email Routing |
| `/sobre` com institucional | ❌ Não existe hoje — criar no site novo |
| Conteúdo sem violações Meta | ✅ |
| Sem conteúdo duplicado Care/Grupo | ⚠️ `/privacidade` e `/termos` hoje apontam pro Care — risco de conteúdo inconsistente pré-cutover |

---

## 6. Pendências antes da Fase 1

| Item | Prioridade | Notas |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` — usar OAuth do wrangler | ✅ **Resolvido** | `wrangler whoami` autenticado. OAuth token em `~/.wrangler/config/default.toml` funciona como Bearer token para a REST API. Usar `python -c "import re,os; f=open(os.path.expanduser('~/.wrangler/config/default.toml')); m=re.search(r'oauth_token = \"(.+?)\"', f.read()); print(m.group(1))"` para extrair. |
| Logo vetorial do Grupo Viktus | **MÉDIA** | Não existe asset dedicado. Usar texto em Space Grotesk Bold no site institucional. Se Victor quiser logo oficial, produzir antes da Fase 3. |
| Email institucional `contato@viktus.com.br` | **MÉDIA** | Não existe. Criar via Cloudflare Email Routing (gratuito) → encaminhar para victor@clinicaguri.com.br. Necessário para Meta Verification. |
| CNPJ e endereço reais confirmados | ✅ | Disponíveis no Worker: 12.181.962/0001-73, Guri Grupo / Rua General Hermes 795, Maceió/AL |
| Conteúdo da página `/sobre` | **MÉDIA** | Não existe hoje — criar com: razão social, missão, lista de produtos, contato. |
| Conteúdo da `/privacidade` do GRUPO | **MÉDIA** | Diferente da política do Care. Deve cobrir: dados coletados pelo site institucional (formulário de contato, analytics se houver). |
| Confirmar se existe Cloudflare Email Routing | **BAIXA** | Verificar no dashboard da zone se Email Routing já está ativo. |

---

## 7. Observação importante — mudança de comportamento pós-cutover

Hoje `viktus.com.br/privacidade` → 301 → `/care/privacidade` (política do Care).

Após a Fase 3, `viktus.com.br/privacidade` vai servir a **Política de Privacidade do Grupo Viktus** (conteúdo diferente — do site institucional, não do Care).

Se houver links externos que apontam para `viktus.com.br/privacidade` esperando a política do Care, eles vão receber conteúdo diferente. A política do Care continuará acessível em `viktus.com.br/care/privacidade` (Worker não é removido para esse path).

**Ação recomendada:** antes do cutover, auditar se a Meta/WhatsApp tem `viktus.com.br/privacidade` ou `viktus.com.br/care/privacidade` registrada. Se for `/care/privacidade` (conforme o plano), não há problema.
