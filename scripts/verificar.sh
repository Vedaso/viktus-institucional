#!/usr/bin/env bash
#
# verificar.sh - everything that is not the deploy. Replaces the build step of
# .github/workflows/deploy.yml (19/11/2026, Victor: "remove isso do github testes locais e
# deploy pela maquina"). publicar.sh runs this first.
#
#   bash scripts/verificar.sh
#
# Builds with GIT_COMMIT set to the 7-char short HEAD (the same form the build-commit meta and the
# production proof use; with the full SHA they would not match). `npm run build` already runs the
# identity gate scripts/check-build.mjs, which fails when a page lacks the meta or dist/ mixes
# commits. Exit code 0 only when every step passed.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

[ -d node_modules ] || { printf '\n> npm ci\n'; npm ci; }

COMMIT=$(git rev-parse --short=7 HEAD)
printf '\n> build (GIT_COMMIT=%s) + check-build gate\n' "$COMMIT"
GIT_COMMIT="$COMMIT" npm run build

printf '\nOK: build and gate passed for %s.\n' "$COMMIT"
