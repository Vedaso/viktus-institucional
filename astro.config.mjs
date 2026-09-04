// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  site: 'https://viktus.com.br',
  // /cv é link não listado: fica fora do sitemap para não ser indexado por descoberta.
  integrations: [sitemap({ filter: (page) => !page.includes('/cv') })],
});
