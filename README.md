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

## Importar uma lição do MuseScore

Use `python3 criar_licao.py "/caminho/licao.mscz" --metodo domingos-pecci --commit`.
O script prepara os arquivos, valida o catálogo e cria o commit; depois basta
`git push origin main`. Veja o [guia do importador](docs/IMPORTAR-LICAO.md),
incluindo atualização de lições e instalação.

## Partituras migradas

A coleção musical do modelo Manual do Maker foi copiada integralmente, incluindo a partitura 107 — MSA — Bb, de P. Bona, seu SVG, MusicXML, MP3, Ogg e mapa de 172 posições. O endereço `/musica/msa/107-msa-bb/` foi preservado. A origem foi mantida intacta para evitar interromper links existentes.

`music_pages.py` monta o leitor a partir dos cadastros em `partituras/`. `assets/music.js` controla zoom, velocidade e cursor em uma ou várias páginas. Áudio, downloads e cursor são opcionais; os controles só aparecem quando existem arquivos correspondentes. O som é gerado no navegador a partir do MusicXML, com controle de andamento e modo mudo para solfejo. Cursor e notas usam o mesmo relógio. MP3/Ogg ficam opcionais com `Playback: recorded`; não há reprodução automática.

Veja [como cadastrar categorias, métodos e lições](docs/PARTITURAS.md). O modelo de Domingos Pecci está em `templates/partituras/domingos-pecci/`, fora do catálogo publicado.

Para sair de uma partitura pronta no MuseScore e criar `score.musicxml`, os
SVGs e o cursor, use o [roteiro de preparação dos assets](docs/PREPARAR-ASSETS-PARTITURA.md).

Os quatro textos iniciais em Markdown foram preparados para esta primeira versão; não são artigos migrados do acervo. A seção Luthier aguarda os dados reais dos serviços e contato.

## Domínio clavesol.com.br

O site pode ser revisado primeiro no endereço do GitHub Pages. Para ativar o domínio, configure os registros DNS recomendados pelo GitHub e o campo Custom domain nas configurações Pages do repositório. A ação usa automaticamente o caminho correto fornecido pelo GitHub. Nenhuma alteração de DNS é feita pelo gerador.

## Créditos de fotografias

- Clarinete (destaque): https://unsplash.com/s/photos/clarinet — imagem Unsplash photo-1573871665247-2b556aa23460.

- Violino: https://unsplash.com/s/photos/violin — imagem Unsplash photo-1492563817904-5f1dc687974f.
- Partitura no piano: Jez Timms, https://unsplash.com/photos/sheet-music-sitting-on-top-of-a-piano-o0eWmlCT1Zk.
- Fotos sob a licença Unsplash: https://unsplash.com/license.

As fontes Google Fonts são opcionais; fontes locais substitutas mantêm o site legível. O site não inclui analytics nem cookies próprios.

## Atualizações e cache

O gerador adiciona `?v=<hash>` às URLs dos arquivos locais: CSS, JavaScript, imagens, áudio, MusicXML e mapa do cursor. O hash muda quando o arquivo muda; o módulo importado pelo player também é versionado. Os arquivos originais continuam com nomes simples em `assets/`.

Cada publicação gera `version.json`. Ao abrir a página ou voltar a uma aba (no máximo uma consulta por minuto), um pequeno script verifica se existe uma versão diferente e oferece **Atualizar** ou **Depois**. Os links internos de páginas levam `_cs=<versão>`, preservando a versão ao navegar; downloads e links externos não são alterados. A versão aceita fica registrada no armazenamento local do navegador, quando disponível. Ao entrar ou voltar pelo histórico a uma página antiga, o script recupera automaticamente uma versão já aceita, após confirmá-la no manifesto. Uma consulta ao voltar à aba nunca provoca recarga automática durante a leitura ou reprodução. Se uma URL já pedir a versão atual e o servidor ainda entregar HTML antigo, o script oferece tentativa manual com uma URL nova, sem entrar em ciclo de recargas. Falhas de rede não impedem a leitura.

O HTML ainda respeita o cache HTTP da hospedagem, atualmente de 10 minutos no GitHub Pages. O aviso só funciona em páginas que já receberam esta implementação; páginas antigas podem precisar de uma atualização manual inicial. Ao mudar o domínio no Pages, execute novamente a ação de publicação para regenerar o caminho base.
