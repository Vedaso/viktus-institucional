/**
 * Gate de build: o artefato precisa saber dizer qual commit ele é.
 *
 * POR QUE ISTO EXISTE: em 17/07/2026 um deploy de um `dist/` velho reverteu esta produção, e
 * ninguém percebeu, porque o site antigo também devolve HTTP 200. A partir de 27/07 o runbook de
 * deploy (viktus-monitor, coletor/deploys.json) confere identidade depois de publicar — ele busca
 * viktus.com.br e procura o commit que acabou de subir. Se a `<meta name="build-commit">` não
 * estiver no HTML, aquele smoke reprova sempre e o deploy é revertido por engano.
 *
 * Ou seja: este check não protege o site, protege o deploy automático de se enganar. Ele falha o
 * build ANTES de tocar produção, que é o único momento em que falhar é barato.
 *
 * Também é o requisito 7 do contrato de admissão (`py admissao.py` no viktus-monitor): até hoje o
 * `build` deste repo era `astro build` puro, sem nenhuma verificação encadeada — o único dos
 * projetos com runbook nessa situação.
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const DIST = 'dist';
const META = /<meta\s+name=["']build-commit["']\s+content=["']([^"']+)["']/i;

function htmls(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = join(dir, e.name);
    return e.isDirectory() ? htmls(p) : e.name.endsWith('.html') ? [p] : [];
  });
}

let paginas;
try {
  paginas = htmls(DIST);
} catch {
  console.error(`check-build: ${DIST}/ não existe. Rode depois do astro build.`);
  process.exit(1);
}

if (paginas.length === 0) {
  console.error(`check-build: nenhum .html em ${DIST}/. O build não produziu página nenhuma.`);
  process.exit(1);
}

const sem = [];
const valores = new Set();
for (const p of paginas) {
  const m = META.exec(readFileSync(p, 'utf8'));
  if (!m) sem.push(p);
  else valores.add(m[1]);
}

if (sem.length) {
  console.error(`check-build: ${sem.length} de ${paginas.length} páginas sem <meta name="build-commit">.`);
  console.error(sem.slice(0, 5).map((p) => `  ${p}`).join('\n'));
  console.error('A meta vem do Layout.astro. Página que não usa o Layout precisa declarar a sua.');
  process.exit(1);
}

if (valores.size > 1) {
  console.error(`check-build: páginas com commits diferentes: ${[...valores].join(', ')}.`);
  console.error('Isso significa dist/ misturando build novo com sobra de build antigo. Apague dist/ e refaça.');
  process.exit(1);
}

const commit = [...valores][0];

// 'dev' é o valor honesto de um build local sem GIT_COMMIT — e é justamente o que não pode ser
// publicado, porque o smoke do runbook procura um commit de verdade.
if (commit === 'dev') {
  if (process.env.CI || process.env.GIT_COMMIT) {
    console.error('check-build: build marcado como "dev" num contexto de publicação.');
    console.error('Exporte GIT_COMMIT antes do build: GIT_COMMIT=$(git rev-parse --short HEAD) npm run build');
    process.exit(1);
  }
  console.log(`check-build: ${paginas.length} páginas, commit "dev" (build local — não publicável).`);
  process.exit(0);
}

if (!/^[0-9a-f]{7,40}$/.test(commit)) {
  console.error(`check-build: build-commit "${commit}" não parece um hash de commit.`);
  process.exit(1);
}

console.log(`check-build: ${paginas.length} páginas, todas marcadas com ${commit}.`);
