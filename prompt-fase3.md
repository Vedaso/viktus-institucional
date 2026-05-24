<context>
## Projeto: Viktus Web Presence — Fase 3: Cutover viktus.com.br

**ATENÇÃO: Esta é a fase de maior risco. Executar em horário de baixo tráfego (ex: madrugada de quarta).**
**Ter rollback documentado e testado ANTES de começar.**

### Pré-requisitos obrigatórios (verificar antes de iniciar)
1. ✅ Fase 1 concluída: site `viktus-institucional` aprovado pelo Victor em `*.pages.dev`
2. ✅ Fase 2 concluída: Redirect Rules para `/financas` e `/spaces` criadas
3. ✅ Snapshot do Worker atual disponível (via `wrangler deployments list`)

### O que esta fase faz
1. Aponta `viktus.com.br` e `www.viktus.com.br` para o Pages `viktus-institucional`
2. Edita o Worker `viktus-care-landing` para remover o catch-all `viktus.com.br/*`
3. Mantém no Worker apenas as rotas `/care`, `/care/privacidade`, `/care/termos`
4. Executa smoke test completo para confirmar que nada quebrou

### O que NÃO muda
- `care.viktus.com.br` — não tocado
- `financas.viktus.com.br` — não tocado
- `spaces.viktus.com.br` — não tocado
- Conteúdo do Worker `care-router` do Care — não tocado
- Banco de dados de qualquer produto — não tocado

### Cloudflare
- Account: `victor_omena@hotmail.com`
- Zone ID: `1d139dddd01f5f87a8d4bff43949f737`
- Worker a editar: `viktus-care-landing`
- **Arquivo real do Worker:** `~/OneDrive/Documentos/Claude/dev/viktus-care/infra/cloudflare/worker-landing-classic.js`
- **ATENÇÃO:** `workers/care-router/` é um Worker DIFERENTE (`care.viktus.com.br`) — NÃO editar
- Pages project: `viktus-institucional` (criado na Fase 1)
</context>

<task>
### PASSO 0 — Salvar snapshot do Worker atual

```bash
# Salvar deployment ID atual (para rollback via wrangler)
npx wrangler deployments list --name viktus-care-landing --json \
  | python -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if d else 'NO_DEPLOYMENTS')" \
  > ~/OneDrive/Documentos/Claude/dev/viktus-institucional/worker-snapshot-pre-cutover.txt
cat ~/OneDrive/Documentos/Claude/dev/viktus-institucional/worker-snapshot-pre-cutover.txt
# Deve imprimir um UUID — se imprimir NO_DEPLOYMENTS, parar e investigar

# Fazer git commit do Worker antes de editar (alternativa mais segura de rollback)
cd ~/OneDrive/Documentos/Claude/dev/viktus-care
git add infra/cloudflare/
git commit -m "chore: snapshot Worker viktus-care-landing pre-cutover fase3"
```

### PASSO 1 — Adicionar custom domains ao Pages

```bash
# Adicionar viktus.com.br ao projeto Pages
npx wrangler pages domain add viktus.com.br --project-name viktus-institucional

# Adicionar www.viktus.com.br
npx wrangler pages domain add www.viktus.com.br --project-name viktus-institucional
```

Aguardar propagação DNS (Cloudflare proxy é quase instantâneo, mas aguardar 30-60s).

Verificar que DNS está proxied (pré-requisito — se não estiver, o Pages custom domain vai falhar):
```bash
dig viktus.com.br +short
# Deve retornar IPs do Cloudflare (104.x.x.x ou similar), não IP direto de servidor
```

Verificar que o site institucional está sendo servido:
```bash
curl -sI https://viktus.com.br/ | grep -E "^HTTP|^cf-ray|^server"
# Deve retornar HTTP/2 200 e cf-ray (confirma que Cloudflare está servindo o Pages)
# Se ainda retornar conteúdo do Worker — aguardar mais 60s e tentar novamente
```

### PASSO 2a — Remover a Worker Route `viktus.com.br/*` do Cloudflare

**Este passo é obrigatório.** Apenas editar o JS do Worker não basta — a route no painel Cloudflare
continua interceptando o tráfego até ser removida explicitamente.

Listar routes ativas do Worker para obter o Route ID:
```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/workers/routes" \
  | python -c "import sys,json; [print(r['id'], r['pattern'], r.get('script','')) for r in json.load(sys.stdin)['result']]"
```

Identificar a route com pattern `viktus.com.br/*` (associada a `viktus-care-landing`) e deletá-la:
```bash
ROUTE_ID="<ID da route viktus.com.br/*>"
curl -s -X DELETE -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/workers/routes/$ROUTE_ID"
# Esperado: {"result":{"id":"..."},"success":true}
```

Manter as routes de `/care/*` associadas ao Worker (não deletar).

### PASSO 2b — Editar Worker `viktus-care-landing`

**Arquivo correto:** `~/OneDrive/Documentos/Claude/dev/viktus-care/infra/cloudflare/worker-landing-classic.js`
**NÃO usar** `workers/care-router/` — esse é o Worker para `care.viktus.com.br` (produto diferente).

**Edição necessária no `worker-landing-classic.js`:**
O arquivo usa `addEventListener('fetch', ...)` com lógica `if/else if` inline para rotas.
Remover os blocos que servem conteúdo para `/` e `/sobre`.
Manter APENAS os handlers para:
- path `/care` (landing do Care)
- path `/care/privacidade` ← CRÍTICO, não remover
- path `/care/termos` ← CRÍTICO, não remover
- redirects `/privacidade` → `/care/privacidade` e `/termos` → `/care/termos` (manter para compatibilidade)

**Fazer deploy do Worker editado:**
```bash
cd ~/OneDrive/Documentos/Claude/dev/viktus-care
npx wrangler deploy infra/cloudflare/worker-landing-classic.js \
  --name viktus-care-landing \
  --compatibility-date 2024-01-01
```

### PASSO 2c — Purge de cache pós-cutover

Após o deploy do Worker e da route removida, forçar purge do cache Cloudflare para `viktus.com.br`:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/purge_cache" \
  -d '{"hosts":["viktus.com.br","www.viktus.com.br"]}'
# Esperado: {"result":{"id":"..."},"success":true}
```

### PASSO 2d — Criar redirect www → root (SEO)

Adicionar Redirect Rule para evitar conteúdo duplicado entre `www.viktus.com.br` e `viktus.com.br`:
```bash
# Verificar se já existe redirect www→root na zone (consultar ruleset de redirects)
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/rulesets" \
  | python -c "import sys,json; [print(r['id'], r['phase']) for r in json.load(sys.stdin)['result']]"
```

Adicionar rule `www → root` ao ruleset de redirects existente (PATCH no ruleset encontrado na Fase 2):
- Expression: `(http.host eq "www.viktus.com.br")`
- Action: redirect 301 para `https://viktus.com.br${http.request.uri.path}`

### PASSO 3 — Smoke test completo

Executar TODOS os testes. Se qualquer teste com ← CRÍTICO falhar, executar ROLLBACK imediatamente.

```bash
echo "=== SITE INSTITUCIONAL (Pages) ==="
curl -sI https://viktus.com.br/ | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

curl -sI https://viktus.com.br/sobre | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

curl -sI https://viktus.com.br/privacidade | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

curl -sI https://viktus.com.br/termos | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

curl -sI https://viktus.com.br/contato | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

echo "=== WORKER CARE (deve continuar) ==="
curl -sI https://viktus.com.br/care | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200 (Worker)

curl -sI https://viktus.com.br/care/privacidade | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200 (Worker) ← CRÍTICO para WhatsApp Business

curl -sI https://viktus.com.br/care/termos | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200 (Worker)

echo "=== REDIRECTS (Fase 2) ==="
curl -sI https://viktus.com.br/financas | grep -E "^HTTP|^location"
# Esperado: HTTP/2 301, location: https://financas.viktus.com.br/

curl -sI https://viktus.com.br/spaces | grep -E "^HTTP|^location"
# Esperado: HTTP/2 301, location: https://spaces.viktus.com.br/

echo "=== APPS EM PRODUÇÃO (devem continuar intocados) ==="
curl -sI https://financas.viktus.com.br/ | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200 ← CRÍTICO

curl -sI https://care.viktus.com.br/app | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200 ou redirect de auth ← CRÍTICO

curl -sI https://spaces.viktus.com.br/ | grep -E "^HTTP|^location"
# Esperado: HTTP/2 200

echo "=== TESTE CONCLUÍDO ==="
```

### PASSO 4 — Validação adicional

Após smoke test passar, verificar manualmente em browser:
- Abrir `https://viktus.com.br/` no Chrome e confirmar hero institucional com 3 cards
- Clicar no link "Acessar sistema" do card Finanças → deve ir para `financas.viktus.com.br`
- Clicar no link "Conheça o produto" do Care → deve ir para `care.viktus.com.br`
- Verificar que `financas.viktus.com.br` faz login normalmente
- Enviar mensagem de teste no WhatsApp Business do Care e confirmar resposta do bot
</task>

<rollback>
## Procedimento de Rollback (< 10 minutos)

Execute se qualquer teste crítico falhar ou se houver problema pós-cutover.

### Passo 1: Remover custom domain do Pages (instantâneo)
```bash
npx wrangler pages domain remove viktus.com.br --project-name viktus-institucional
npx wrangler pages domain remove www.viktus.com.br --project-name viktus-institucional
```
Isso faz o DNS voltar para o Worker automaticamente.

### Passo 2: Restaurar Worker (se foi editado)

**Opção A — via wrangler (se o deployment ID foi salvo):**
```bash
DEPLOY_ID=$(cat ~/OneDrive/Documentos/Claude/dev/viktus-institucional/worker-snapshot-pre-cutover.txt)
npx wrangler rollback "$DEPLOY_ID" --name viktus-care-landing
```

**Opção B — via git (mais confiável):**
```bash
cd ~/OneDrive/Documentos/Claude/dev/viktus-care
# Checar commit do snapshot (feito no PASSO 0)
git log --oneline -5 infra/cloudflare/worker-landing-classic.js
# Restaurar o arquivo para o commit do snapshot
git checkout HEAD~1 -- infra/cloudflare/worker-landing-classic.js
# Re-deployar
npx wrangler deploy infra/cloudflare/worker-landing-classic.js \
  --name viktus-care-landing --compatibility-date 2024-01-01
```

### Passo 2b: Restaurar a Worker Route (se foi removida)
```bash
# Re-adicionar a route viktus.com.br/* para o Worker viktus-care-landing
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/workers/routes" \
  -d '{"pattern":"viktus.com.br/*","script":"viktus-care-landing"}'
```

### Passo 3: Verificar que voltou ao estado anterior
```bash
curl -sI https://viktus.com.br/ | head -3
# Deve retornar 200 com o conteúdo antigo do Worker
curl -sI https://viktus.com.br/care/privacidade | head -3
# Deve retornar 200
```

**Tempo estimado de rollback completo: < 10 minutos.**
</rollback>

<constraints>
- **NUNCA** remover os handlers `/care/privacidade` e `/care/termos` do Worker — isso quebra o WhatsApp Business.
- **NÃO** executar esta fase sem aprovação explícita do Victor.
- **NÃO** executar em horário de pico de uso dos apps (preferir madrugada).
- **NÃO** fazer os dois passos (custom domain + editar Worker) em paralelo — fazer em sequência com verificação entre cada passo.
- Se o smoke test falhar em qualquer item ← CRÍTICO, executar rollback IMEDIATAMENTE sem tentar corrigir on-the-fly.
- Salvar o snapshot do Worker ANTES de qualquer edição.
</constraints>

<criterios-de-aceite>
- [ ] Arquivo `worker-snapshot-pre-cutover.txt` existe com deployment ID de referência
- [ ] `curl -sI https://viktus.com.br/` → `HTTP/2 200` (Pages, não Worker)
- [ ] `curl -sI https://viktus.com.br/sobre` → `HTTP/2 200`
- [ ] `curl -sI https://viktus.com.br/privacidade` → `HTTP/2 200`
- [ ] `curl -sI https://viktus.com.br/care` → `HTTP/2 200` (Worker ainda serve)
- [ ] `curl -sI https://viktus.com.br/care/privacidade` → `HTTP/2 200` ← CRÍTICO
- [ ] `curl -sI https://viktus.com.br/financas` → `HTTP/2 301` com `location: https://financas.viktus.com.br/`
- [ ] `curl -sI https://viktus.com.br/spaces` → `HTTP/2 301` com `location: https://spaces.viktus.com.br/`
- [ ] `curl -sI https://financas.viktus.com.br/` → `HTTP/2 200` ← CRÍTICO
- [ ] `curl -sI https://care.viktus.com.br/app` → `HTTP/2 200` ou redirect auth ← CRÍTICO
- [ ] `curl -sI https://spaces.viktus.com.br/` → `HTTP/2 200`
- [ ] WhatsApp Business do Care respondeu a mensagem de teste
- [ ] Commit do estado pré-cutover do Worker existe no repo `viktus-care`
</criterios-de-aceite>
