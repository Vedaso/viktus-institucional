<context>
## Projeto: Viktus Web Presence — Fase 2: Redirect Rules Cloudflare

Esta fase adiciona redirects amigáveis para `/financas` e `/spaces` no domínio `viktus.com.br`.
**Risco baixo: rollback é instantâneo via dashboard.**

### Estado atual (antes desta fase)
- `viktus.com.br/*` → Worker `viktus-care-landing` (captura tudo)
- `viktus.com.br/care` → Worker serve landing do Care
- `viktus.com.br/care/privacidade` → Worker serve política (CRÍTICO: referenciado pela Meta/WhatsApp Business)
- `viktus.com.br/care/termos` → Worker serve termos
- `financas.viktus.com.br` → Cloudflare Pages (app em produção)
- `spaces.viktus.com.br` → Cloudflare Workers (app em produção)

### Pré-requisito
A Fase 1 deve estar concluída (site `*.pages.dev` aprovado pelo Victor).
Esta fase NÃO requer que o custom domain já esteja configurado.

### Cloudflare
- Account: `victor_omena@hotmail.com`
- Zone ID: `1d139dddd01f5f87a8d4bff43949f737`
- Zone: `viktus.com.br`

### Precedência de regras no Cloudflare
Worker Routes têm prioridade sobre Redirect Rules. Como o Worker captura `viktus.com.br/*`,
os redirects só funcionarão APÓS a Fase 3 (cutover) — ou se o Worker não capturar o path específico.
**Criar as regras agora é seguro e prepara o terreno para a Fase 3.**
</context>

<task>
### 1. Verificar estado atual das Worker Routes

Antes de criar as rules, documentar as rotas ativas do Worker:

```bash
# Via API (wrangler routes list foi descontinuado no wrangler 4)
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/workers/routes" \
  | python -c "import sys,json; [print(r['pattern'], '->', r.get('script','')) for r in json.load(sys.stdin)['result']]"
```

Se `CLOUDFLARE_API_TOKEN` não estiver no ambiente: criar em `https://dash.cloudflare.com/profile/api-tokens`
com permissões: `Zone.Cache Rules` (Edit), `Zone.Page Rules` (Edit), `Zone.Workers Routes` (Read).

Salvar o output como referência no arquivo `auditoria-worker-routes.txt` em `~/OneDrive/Documentos/Claude/dev/viktus-institucional/`.

### 2. Criar Redirect Rules via Cloudflare API

Criar as seguintes Redirect Rules na zone `1d139dddd01f5f87a8d4bff43949f737`:

**Rule 1: /financas → financas.viktus.com.br**
- Source URL: `viktus.com.br/financas*`
- Target URL: `https://financas.viktus.com.br/`
- Status: 301 (permanent)
- Preserve query string: não

**Rule 2: /spaces → spaces.viktus.com.br**
- Source URL: `viktus.com.br/spaces*`
- Target URL: `https://spaces.viktus.com.br/`
- Status: 301 (permanent)
- Preserve query string: não

Via API Cloudflare (Ruleset de Redirects):

**IMPORTANTE:** Cloudflare permite apenas 1 ruleset por phase por zone. Verificar se já existe antes de criar:
```bash
# Passo 1: verificar se já existe ruleset de redirect na zone
RULESET_ID=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/rulesets" \
  | python -c "
import sys, json
data = json.load(sys.stdin)
rs = [r for r in data['result'] if r.get('phase') == 'http_request_dynamic_redirect']
print(rs[0]['id'] if rs else 'NONE')
")
echo "Ruleset ID: $RULESET_ID"
```

**Se RULESET_ID == NONE** — criar novo ruleset:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/rulesets" \
  -d '{
    "name": "Viktus redirects",
    "kind": "zone",
    "phase": "http_request_dynamic_redirect",
    "rules": [
      {
        "expression": "(http.host eq \"viktus.com.br\" and (http.request.uri.path eq \"/financas\" or starts_with(http.request.uri.path, \"/financas/\")))",
        "action": "redirect",
        "action_parameters": {
          "from_value": {
            "status_code": 301,
            "target_url": { "value": "https://financas.viktus.com.br/" },
            "preserve_query_string": false
          }
        },
        "description": "Redirect /financas para financas.viktus.com.br"
      },
      {
        "expression": "(http.host eq \"viktus.com.br\" and (http.request.uri.path eq \"/spaces\" or starts_with(http.request.uri.path, \"/spaces/\")))",
        "action": "redirect",
        "action_parameters": {
          "from_value": {
            "status_code": 301,
            "target_url": { "value": "https://spaces.viktus.com.br/" },
            "preserve_query_string": false
          }
        },
        "description": "Redirect /spaces para spaces.viktus.com.br"
      }
    ]
  }'
```

**Se RULESET_ID != NONE** — adicionar rules ao ruleset existente (PATCH):
```bash
# Primeiro listar as rules existentes para não perder nenhuma
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/rulesets/$RULESET_ID" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(r['description'], '|', r['expression']) for r in d['result'].get('rules',[])]"

# Adicionar as 2 novas rules PRESERVANDO as existentes (substituir <EXISTING_RULES_JSON> com o output acima)
# Usar o dashboard Cloudflare como alternativa mais segura para edição manual do ruleset existente
```

Alternativa: se preferir usar o dashboard Cloudflare, documentar os passos executados e tirar screenshot das rules criadas.

### 3. Validar que as rules foram criadas

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/1d139dddd01f5f87a8d4bff43949f737/rulesets" \
  | jq '.result[] | select(.phase == "http_request_dynamic_redirect") | .rules[] | {description, expression}'
```

### 4. Smoke test — o que NÃO pode quebrar

Executar todos os testes abaixo. **Se qualquer teste crítico falhar, parar imediatamente.**

```bash
# Paths críticos — devem continuar funcionando (Worker ainda captura tudo)
curl -sI https://viktus.com.br/ | head -3
# Esperado: HTTP/2 200 (servido pelo Worker)

curl -sI https://viktus.com.br/care | head -3
# Esperado: HTTP/2 200 (Worker — landing Care)

curl -sI https://viktus.com.br/care/privacidade | head -3
# Esperado: HTTP/2 200 (Worker — CRÍTICO para WhatsApp Business)

curl -sI https://viktus.com.br/care/termos | head -3
# Esperado: HTTP/2 200 (Worker)

# Apps em produção — não devem ser afetadas
curl -sI https://financas.viktus.com.br/ | head -3
# Esperado: HTTP/2 200

curl -sI https://care.viktus.com.br/app | head -3
# Esperado: HTTP/2 200 ou 307/redirect para login

curl -sI https://spaces.viktus.com.br/ | head -3
# Esperado: HTTP/2 200

# Nota: /financas e /spaces podem não redirecionar ainda se o Worker captura tudo
# Isso é ESPERADO — os redirects ativarão após a Fase 3 (cutover)
```
</task>

<constraints>
- **NÃO** criar redirect para `/care`, `/care/*`, `/privacidade`, `/termos` — esses paths pertencem ao Worker.
- **NÃO** alterar o Worker `viktus-care-landing` nesta fase.
- **NÃO** alterar DNS da zone.
- **NÃO** adicionar custom domain ao Pages `viktus-institucional` nesta fase.
- **NÃO** usar `CLOUDFLARE_API_TOKEN` se não estiver disponível no ambiente — documentar os passos para configuração manual no dashboard como alternativa.
- Se os redirects não funcionarem imediatamente (por causa da precedência do Worker), isso é comportamento esperado — documentar explicitamente.
</constraints>

<rollback>
As Redirect Rules são independentes do Worker. Para desfazer:
1. Acessar Cloudflare dashboard → zone `viktus.com.br` → Rules → Redirect Rules
2. Desativar ou deletar as rules criadas
3. Tempo: < 2 minutos, sem impacto em produção
</rollback>

<criterios-de-aceite>
- [ ] Arquivo `auditoria-worker-routes.txt` criado com as rotas atuais do Worker
- [ ] Redirect Rules criadas na zone (via API ou dashboard documentado)
- [ ] Rule `/financas*` → `https://financas.viktus.com.br/` (301) existe na zone
- [ ] Rule `/spaces*` → `https://spaces.viktus.com.br/` (301) existe na zone
- [ ] `curl -sI https://viktus.com.br/care/privacidade` retorna 200 (não quebrou)
- [ ] `curl -sI https://viktus.com.br/` retorna 200 (não quebrou)
- [ ] `curl -sI https://financas.viktus.com.br/` retorna 200 (app intocado)
- [ ] `curl -sI https://care.viktus.com.br/app` retorna 200 ou redirect de auth (app intocado)
</criterios-de-aceite>
