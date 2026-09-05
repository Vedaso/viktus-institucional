<context>
## Projeto: Viktus Web Presence — Fase 1: Site institucional em staging

Esta fase cria o novo site institucional do Grupo Viktus do zero.
**Nenhum produto em produção é tocado nesta fase.**

### Família de produtos Viktus
| Produto | URL | Status | Badge |
|---|---|---|---|
| Viktus Finanças | `https://financas.viktus.com.br` | Em produção | `producao` |
| Viktus Care | `https://care.viktus.com.br` | Em produção | `producao` |
| Viktus Spaces | `https://spaces.viktus.com.br` | Em desenvolvimento | `desenvolvimento` |

### Objetivo desta fase
Criar o repo `viktus-institucional` em `~/OneDrive/Documentos/Claude/dev/viktus-institucional/`
com Astro 6+ estático, publicar no Cloudflare Pages com domínio temporário (`*.pages.dev`).
**NÃO adicionar custom domain `viktus.com.br` ainda — isso é a Fase 3.**

### Contexto Cloudflare
- Conta: `victor_omena@hotmail.com`
- Zone ID viktus.com.br: `1d139dddd01f5f87a8d4bff43949f737`
- Modelos de deploy: `viktus-frontend` (Cloudflare Pages estático), `viktus-spaces` (Workers OpenNext)
- Para este projeto, usar **Cloudflare Pages** (não Workers)

### Brand Viktus
Se o arquivo `auditoria-fase0.md` existe em `~/OneDrive/Documentos/Claude/dev/viktus-institucional/`,
consulte-o para brand assets. Caso contrário, usar os tokens reais do Worker em produção:
- Cor primária: `#0E5172` (azul Viktus — extraído de `worker-landing-classic.js`)
- Cor secundária: `#1A1A2E` (azul escuro)
- Gradiente padrão: `linear-gradient(135deg, #0E5172 0%, #1A1A2E 100%)`
- Link color: `#7DD3FC` (sky blue)
- Fonte: sistema (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Logo: texto "Viktus" em fonte bold até design oficial estar disponível
</context>

<task>
### 1. Inicializar o projeto Astro

No diretório `~/OneDrive/Documentos/Claude/dev/viktus-institucional/`:

Verificar Node 20.3+ antes de começar (Astro 6 exige):
```bash
node --version  # deve ser v20.3.0 ou superior
```

```bash
npm create astro@latest . -- --template minimal --typescript strict --no-git --install --skip-houston --yes
```

Instalar dependências de desenvolvimento:
```bash
npm install -D wrangler @astrojs/sitemap
```

### 2. Configurar `astro.config.mjs`

**IMPORTANTE:** `output: 'static'` não usa adapter — o adapter `@astrojs/cloudflare` é para Workers/SSR
e é incompatível com build estático. O deploy é feito diretamente via `wrangler pages deploy dist/`.

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  site: 'https://viktus.com.br',
  integrations: [sitemap()],
});
```

### 3. Criar `src/content/produtos.json`

```json
[
  {
    "id": "financas",
    "name": "Viktus Finanças",
    "tagline": "Gestão financeira multi-tenant para PMEs",
    "description": "Controle contas a pagar e receber, fluxo de caixa e antecipações com visibilidade total do seu negócio.",
    "url": "https://financas.viktus.com.br",
    "status": "producao",
    "ctaLabel": "Acessar sistema"
  },
  {
    "id": "care",
    "name": "Viktus Care",
    "tagline": "Relacionamento clínica-paciente multicanal",
    "description": "Comunicação com pacientes via WhatsApp, SMS e email com histórico unificado e automação inteligente.",
    "url": "https://care.viktus.com.br",
    "status": "producao",
    "ctaLabel": "Conheça o produto"
  },
  {
    "id": "spaces",
    "name": "Viktus Spaces",
    "tagline": "Gestão de espaços e salas comerciais",
    "description": "Locação, controle de acesso e pagamentos integrados para espaços compartilhados e consultórios.",
    "url": "https://spaces.viktus.com.br",
    "status": "desenvolvimento",
    "ctaLabel": "Em breve"
  }
]
```

### 4. Criar `src/styles/tokens.css`

Definir variáveis CSS com os tokens do brand Viktus. Incluir: cores, tipografia, espaçamento, border-radius, sombras. Manter compatível com os outros produtos da família.

### 5. Criar componentes

**`src/components/ProductCard.astro`**
Props TypeScript:
```ts
interface Props {
  name: string;
  tagline: string;
  description: string;
  url: string;
  status: 'producao' | 'desenvolvimento' | 'em-breve';
  ctaLabel: string;
}
```
- Badge visual para cada status: "Em produção" (verde), "Em desenvolvimento" (amarelo/laranja), "Em breve" (cinza)
- CTA desabilitado visualmente para status `em-breve`
- Link externo (`target="_blank" rel="noopener"`) para status `producao`

**`src/components/Nav.astro`** — logo Viktus + links: Sobre, Contato

**`src/components/Footer.astro`** — copyright, links legais (/privacidade, /termos), CNPJ placeholder

### 6. Criar páginas

**`src/pages/index.astro`**
Seções (nesta ordem):
1. Hero: "Grupo Viktus — Software para gestão de negócios"
2. Produtos: 3 cards usando `ProductCard.astro` com dados de `produtos.json`
3. Sobre: quem somos, missão (2-3 parágrafos)
4. Contato: email institucional ou formulário simples (sem backend — `mailto:`)

**`src/pages/sobre.astro`** — institucional completo com CNPJ placeholder (`00.000.000/0000-00`), endereço, missão, produtos

**`src/pages/privacidade.astro`** — Política de Privacidade do GRUPO Viktus (não duplicar a do Care). Mencionar quais dados coleta o site institucional (analytics, contato). Incluir: responsável pelos dados, LGPD, direitos do titular, contato DPO.

**`src/pages/termos.astro`** — Termos de Uso do site institucional viktus.com.br (não dos produtos individuais)

**`src/pages/contato.astro`** — Link de contato via `<a href="mailto:contato@viktus.com.br">` e `<a href="https://wa.me/...">`. Sem formulário POST — não há backend e `action="mailto:"` não funciona em mobile.

### 7. Configurar `public/`

- `public/robots.txt` — permitir todos os crawlers, `Sitemap: https://viktus.com.br/sitemap-index.xml` (gerado pela integração `@astrojs/sitemap`)
- `public/_headers` — headers de segurança para todas as rotas:
  ```
  /*
    X-Frame-Options: DENY
    X-Content-Type-Options: nosniff
    Referrer-Policy: strict-origin-when-cross-origin
    Permissions-Policy: camera=(), microphone=(), geolocation=()
  ```
- `public/favicon.ico` — favicon simples (pode ser SVG inline convertido)
- `public/og-image.png` — Open Graph 1200x630px (pode ser placeholder com texto "Grupo Viktus")

### 8. Configurar meta tags globais

Em cada página, incluir:
- `<title>` descritivo
- `<meta name="description">`
- `<meta property="og:title">`, `og:description`, `og:image`, `og:url`
- `<link rel="canonical">`

### 9. Build e verificação local

```bash
npm run build
# Verificar que dist/ foi criado com todas as páginas HTML
ls dist/

# Preview local (sem wrangler, usando Astro preview):
npm run preview

# Ou via wrangler pages (requer wrangler instalado):
npx wrangler pages dev dist/
```

Verificar que todas as páginas carregam sem erro 404.

### 10. Deploy no Cloudflare Pages (staging)

```bash
npx wrangler pages deploy dist/ --project-name viktus-institucional
```

Se o projeto não existir, criar primeiro:
```bash
npx wrangler pages project create viktus-institucional
```

**NÃO adicionar custom domain `viktus.com.br` — apenas usar o domínio `*.pages.dev` gerado.**

### 11. Inicializar git e fazer push

```bash
git init
git add .
git commit -m "feat: initial Astro site for Grupo Viktus institutional"
gh repo create Vedaso/viktus-institucional --public --push --source .
```
</task>

<constraints>
- **NÃO** adicionar custom domain `viktus.com.br` ao projeto Pages nesta fase.
- **NÃO** editar o Worker `viktus-care-landing` ou qualquer outro Worker existente.
- **NÃO** alterar DNS da zone `1d139dddd01f5f87a8d4bff43949f737`.
- **NÃO** criar SSR (server-side rendering) — `output: 'static'` é obrigatório.
- **NÃO** criar conta, serviço ou API externa nova.
- **NÃO** duplicar o conteúdo de `/care/privacidade` do Care — são políticas diferentes.
- Astro 4+, TypeScript strict, sem frameworks JS de UI (sem React/Vue/Svelte) — Astro puro.
- CNPJ e endereço podem ser placeholder para aprovação do Victor antes de publicar dados reais.
</constraints>

<criterios-de-aceite>
- [ ] `npm run build` completa sem erros
- [ ] `npx wrangler pages dev dist/` serve todas as páginas localmente
- [ ] Deploy no Cloudflare Pages com URL `*.pages.dev` acessível
- [ ] `https://viktus-institucional.pages.dev/` → 200, hero com 3 cards de produto visíveis
- [ ] `https://viktus-institucional.pages.dev/sobre` → 200
- [ ] `https://viktus-institucional.pages.dev/privacidade` → 200
- [ ] `https://viktus-institucional.pages.dev/termos` → 200
- [ ] `https://viktus-institucional.pages.dev/contato` → 200
- [ ] Cards de Finanças e Care têm badge "Em produção" (verde)
- [ ] Card de Spaces tem badge "Em desenvolvimento" (laranja/amarelo)
- [ ] Links dos produtos apontam para os subdomínios corretos
- [ ] Repo `Vedaso/viktus-institucional` existe no GitHub com o código
- [ ] `financas.viktus.com.br` continua respondendo normalmente (não foi tocado)
- [ ] `care.viktus.com.br/app` continua respondendo normalmente (não foi tocado)
- [ ] `viktus.com.br/` continua sendo servido pelo Worker antigo (não foi tocado)
</criterios-de-aceite>
