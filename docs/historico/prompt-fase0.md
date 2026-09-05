<context>
## Projeto: Viktus Web Presence — Fase 0: Auditoria

Você está preparando a implementação de um site institucional para o Grupo Viktus.
Antes de qualquer mudança, esta fase é 100% read-only: inventariar o estado atual.

### Família de produtos Viktus
- **Viktus Finanças** → `financas.viktus.com.br` (Cloudflare Pages, repo `Vedaso/viktus-frontend`)
- **Viktus Care** → `care.viktus.com.br` (Cloudflare Pages + Worker, repo `Vedaso/viktus-care`)
- **Viktus Spaces** → `spaces.viktus.com.br` (Cloudflare Workers via OpenNext, repo `Vedaso/viktus-spaces`)

### Worker crítico em produção
`viktus-care-landing` é um Cloudflare Worker que atualmente gerencia TODAS as rotas de `viktus.com.br/*`.
Ele serve a landing institucional do Grupo e as rotas do produto Care, incluindo documentos legais
referenciados pela Meta/WhatsApp Business (`/care/privacidade`, `/care/termos`).

### O que vai mudar no futuro (contexto apenas)
Será criado um novo repo `Vedaso/viktus-institucional` (Astro + Cloudflare Pages) que vai assumir
`viktus.com.br`. O Worker será editado para manter apenas `/care/*`. Esta fase não faz nada disso —
apenas audita para garantir que a mudança não quebre nada.

### Paths no disco
- Repo viktus-care: `~/OneDrive/Documentos/Claude/dev/viktus-care/`
- Workers do care: `~/OneDrive/Documentos/Claude/dev/viktus-care/workers/`
- Cloudflare zone ID: `1d139dddd01f5f87a8d4bff43949f737`
</context>

<task>
Execute a auditoria completa e produza um relatório de inventário salvo em
`~/OneDrive/Documentos/Claude/dev/viktus-institucional/auditoria-fase0.md`.

### 1. Inventário do Worker `viktus-care-landing`

Localize o código do Worker. Paths conhecidos (em ordem de prioridade):
- `~/OneDrive/Documentos/Claude/dev/viktus-care/infra/cloudflare/worker-landing-classic.js` ← **path real**
- `~/OneDrive/Documentos/Claude/dev/viktus-care/infra/cloudflare/worker-landing.js` ← versão antiga
- **NÃO é** `workers/care-router/` — esse Worker serve `care.viktus.com.br` (rota confirmada no wrangler.toml dele)

Para cada arquivo encontrado, liste:
- Nome do arquivo e caminho
- Todas as rotas/paths capturados (ex: `/`, `/care`, `/care/*`, `viktus.com.br/*`)
- O que cada rota faz (serve HTML? redireciona? proxies para outro serviço?)
- Referências a URLs externas hardcoded

### 2. Inventário de brand assets

Verifique se existem arquivos de identidade visual Viktus em:
- `~/OneDrive/Documentos/Claude/dev/viktus-care/` (logos, tokens CSS, design system)
- `~/OneDrive/Documentos/Claude/dev/viktus-frontend/` (PWA icons, CSS)
- `~/OneDrive/Documentos/Claude/dev/viktus-spaces/` (componente SpacesLogo, brand system)
- `~/OneDrive/Documentos/Obsidian Vault/Viktus/` (briefings visuais)

Liste: arquivos encontrados, formatos, cores principais se visíveis no CSS.

### 2b. Verificar estado real em produção (curl)

Além da inspeção de arquivos locais, confirmar o estado ATUAL do que está deployado:

```bash
curl -sI https://viktus.com.br/ | grep -E "^HTTP|^server|^cf-ray"
curl -sI https://viktus.com.br/care | grep -E "^HTTP|^location"
curl -sI https://viktus.com.br/care/privacidade | grep -E "^HTTP|^location"
curl -sI https://viktus.com.br/privacidade | grep -E "^HTTP|^location"
# Nota: /privacidade atualmente redireciona 301 para /care/privacidade (comportamento do Worker)
# Após a Fase 3, /privacidade vai servir a política do GRUPO (conteúdo diferente, sem redirect)
# Documentar esse risco: links externos que apontam para viktus.com.br/privacidade
# vão mudar de destino após o cutover.

curl -sI https://viktus.com.br/termos | grep -E "^HTTP|^location"
curl -sI https://financas.viktus.com.br/ | grep "^HTTP"
curl -sI https://care.viktus.com.br/app | grep "^HTTP"
curl -sI https://spaces.viktus.com.br/ | grep "^HTTP"
```

Documentar o output de cada URL no `auditoria-fase0.md`.

### 3. Rotas que NÃO podem quebrar

Documente explicitamente as rotas que são críticas e por quê:
- `viktus.com.br/care/privacidade` — referenciada pela Meta/WhatsApp Business do Care
- `viktus.com.br/care/termos` — referenciada pela Meta/WhatsApp Business do Care
- `care.viktus.com.br/app` — portal paciente em produção (Clínica Guri)
- `financas.viktus.com.br/` — app financeiro em produção

### 4. Checklist Meta Business Verification

Documente o que o site `viktus.com.br` precisa ter para passar pela verificação Meta:
- [ ] Página inicial com nome da empresa e descrição
- [ ] Página `/sobre` ou `/about` com CNPJ e endereço físico
- [ ] Política de privacidade em `/privacidade`
- [ ] Termos de uso em `/termos`
- [ ] Informação de contato (email ou formulário)
- [ ] Sem conteúdo duplicado das legais do Care (são políticas diferentes)

### 5. Resumo de riscos

Para cada rota atual do Worker, classifique:
- `CRÍTICO`: quebra WhatsApp Business ou app em produção se não funcionar
- `IMPORTANTE`: afeta UX mas recuperável
- `BAIXO`: pode ser migrado sem urgência
</task>

<constraints>
- Esta fase é 100% read-only. NÃO edite nenhum arquivo.
- NÃO faça deploy, commit, push ou qualquer operação destrutiva.
- NÃO acesse o dashboard Cloudflare — trabalhe apenas com os arquivos locais.
- Se não encontrar o Worker localmente, documente isso no relatório e liste os próximos passos para obtê-lo (ex: `wrangler deployments list`).
- NÃO altere nenhum arquivo nos repos `viktus-care`, `viktus-frontend` ou `viktus-spaces`.
</constraints>

<criterios-de-aceite>
O arquivo `auditoria-fase0.md` deve existir e conter:
- [ ] Lista completa de arquivos do Worker com paths capturados por cada handler
- [ ] Lista de brand assets encontrados (ou declaração explícita de ausência)
- [ ] Tabela de rotas críticas com classificação de risco
- [ ] Checklist Meta Business Verification preenchido com o status atual
- [ ] Seção "Pendências antes da Fase 1" listando o que está faltando (brand kit, conteúdo, etc.)
</criterios-de-aceite>
