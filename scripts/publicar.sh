#!/usr/bin/env bash
#
# publicar.sh - build, deploy to Cloudflare Pages and PROVE production is this commit, from this
# machine. Replaces .github/workflows/deploy.yml (19/11/2026, Victor: "remove isso do github
# testes locais e deploy pela maquina").
#
#   bash scripts/publicar.sh
#
# The proof exists because on 17/07/2026 a deploy of a stale dist/ reverted production and nobody
# noticed: the old site also answers 200. So after the deploy this fetches viktus.com.br and demands
# the build-commit meta to equal the commit just shipped.
#
# The meta carries HEAD, so a tracked file modified on top of HEAD would make it lie: the script
# refuses to run in that case (ALLOW_DIRTY=1 overrides, knowingly).
#
# Token comes from Claude/secrets/cloudflare.env (parsed, never sourced: values may hold shell
# metacharacters). Nothing is hardcoded.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [ -n "$(git status --porcelain --untracked-files=no)" ] && [ "${ALLOW_DIRTY:-0}" != "1" ]; then
  echo "x tracked files differ from HEAD: the build-commit meta would not describe what ships."
  echo "  Commit first, or run with ALLOW_DIRTY=1."
  git status --short --untracked-files=no
  exit 1
fi

ENV_FILE="${CLOUDFLARE_ENV:-$HOME/OneDrive/Documentos/Claude/secrets/cloudflare.env}"
[ -f "$ENV_FILE" ] || { echo "missing $ENV_FILE"; exit 1; }
for k in CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID; do
  v=$(grep -E "^$k=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '\r')
  # The vault file may quote values (KEY="value"); strip one pair of surrounding quotes.
  v="${v#[\"\']}"; v="${v%[\"\']}"
  [ -n "$v" ] || { echo "$k not found in $ENV_FILE"; exit 1; }
  export "$k=$v"
done
# Otherwise wrangler prefers the global key over the token.
unset CLOUDFLARE_GLOBAL_API_KEY CLOUDFLARE_AUTH_EMAIL

bash scripts/verificar.sh

ESPERADO=$(git rev-parse --short=7 HEAD)

printf '\n> deploy viktus-institucional\n'
npx --yes wrangler@4 pages deploy dist/ --project-name viktus-institucional --branch main

printf '\n> proving production is %s\n' "$ESPERADO"
for tentativa in $(seq 1 12); do
  visto=$(curl -sf "https://viktus.com.br/?cb=$(date +%s)" \
    | grep -o 'name="build-commit" content="[^"]*"' \
    | sed 's/.*content="//;s/"//') || visto=''
  if [ "$visto" = "$ESPERADO" ]; then
    echo "OK: production is at $visto"
    exit 0
  fi
  echo "attempt $tentativa: production answers '$visto', expected '$ESPERADO'"
  sleep 10
done
echo "x production did not reach $ESPERADO after 2 minutes"
exit 1
