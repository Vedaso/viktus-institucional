# Fontes das imagens

Os PNG originais dos retratos. O site serve os `.webp` equivalentes em `public/profile/`:
mesma imagem, 72 KB no lugar de 677 KB, com diferença máxima de 7/255 num canal.

Reeditou o PNG? Regere o webp e troque o arquivo publicado:

```sh
py -c "from PIL import Image; Image.open('docs/fontes/victor-mascara.png').save('public/profile/victor-mascara.webp','WEBP',quality=92,method=6)"
```
