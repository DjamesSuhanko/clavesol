# Clave Sol

Blog musical estático, gerado com Python + Markdown e publicado no GitHub Pages. Não usa banco de dados, servidor de aplicação ou painel administrativo.

## Escrever um artigo

Crie um arquivo em `content/`, por exemplo `meu-artigo.md`:

```md
Title: Meu título
Description: Um resumo curto do artigo.
Category: artigos
Image: piano.jpg

## Primeiro assunto

Escreva aqui em Markdown.
```

Categorias aceitas: `gem`, `artigos`, `luthier`, `links`, `tutoriais`. `Image` é opcional e aponta para um arquivo em `assets/`. O nome do arquivo define o endereço `/artigos/meu-artigo/`. Os artigos entram automaticamente na seção indicada e no índice Artigos. Os três primeiros arquivos, em ordem de nome, aparecem na página inicial. Links internos em Markdown devem começar com `{{BASE}}/` para funcionar no domínio próprio e no endereço de projeto do GitHub Pages.

Edite pelo GitHub e faça commit na branch `main`. A ação Publicar Clave Sol gera e publica o site automaticamente.

## Desenvolvimento local

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
BASE_PATH='' python build.py
python scripts/check_links.py
python -m http.server 8000 --directory dist
```

## Partituras migradas

A coleção musical do modelo Manual do Maker foi copiada integralmente, incluindo a partitura 107 — MSA — Bb, de P. Bona, seu SVG, MusicXML, MP3, Ogg e mapa de 172 posições. O endereço `/musica/msa/107-msa-bb/` foi preservado. A origem foi mantida intacta para evitar interromper links existentes.

`music_pages.py` monta o leitor. `assets/music.js` controla zoom, velocidade e cursor. Execute `node tests/music.test.mjs` para validar sincronização. As posições usam o relógio do áudio; não há reprodução automática. Novas partituras precisam dos arquivos de áudio, SVG e mapa exportados da mesma versão do original. Atualmente o leitor suporta uma página por partitura.

Os quatro textos iniciais em Markdown foram preparados para esta primeira versão; não são artigos migrados do acervo. A seção Luthier aguarda os dados reais dos serviços e contato.

## Domínio clavesol.com.br

O site pode ser revisado primeiro no endereço do GitHub Pages. Para ativar o domínio, configure os registros DNS recomendados pelo GitHub e o campo Custom domain nas configurações Pages do repositório. A ação usa automaticamente o caminho correto fornecido pelo GitHub. Nenhuma alteração de DNS é feita pelo gerador.

## Créditos de fotografias

- Violino: https://unsplash.com/s/photos/violin — imagem Unsplash photo-1492563817904-5f1dc687974f.
- Partitura no piano: Jez Timms, https://unsplash.com/photos/sheet-music-sitting-on-top-of-a-piano-o0eWmlCT1Zk.
- Fotos sob a licença Unsplash: https://unsplash.com/license.

As fontes Google Fonts são opcionais; fontes locais substitutas mantêm o site legível. O site não inclui analytics nem cookies próprios.
