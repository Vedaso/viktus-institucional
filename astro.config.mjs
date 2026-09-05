// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  // O Cloudflare Pages serve /rota/ e responde 308 para /rota. Com 'always' o dev server
  // exige a mesma forma, então link sem barra falha aqui e não em produção.
  trailingSlash: 'always',
  site: 'https://viktus.com.br',
  // /cv é link não listado: fica fora do sitemap para não ser indexado por descoberta.
  integrations: [sitemap({ filter: (page) => !page.includes('/cv') })],
});
