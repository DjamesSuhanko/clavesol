# Busca nas listagens

A busca filtra os cards da página aberta: artigos, categorias, ferramentas do GEM e partituras. Não pesquisa o texto completo dos artigos nem outras páginas ou subdomínios.

Aceita partes das palavras, ignora maiúsculas e acentos e combina vários termos em qualquer ordem. Por exemplo, `cristao` encontra “Cantor Cristão”.

Nas partituras, pesquisa número da lição/hino, título, autor e instrumento. Números são comparados inteiros: `10` não encontra `110`; `010` equivale a `10`.

O botão “Limpar busca” restaura todos os cards. Sem JavaScript, os cards continuam disponíveis.

Os arquivos compartilhados são `list_search.py`, `assets/list-search.css` e `assets/list-search.mjs`; o script de sincronização do player também os replica para os hinários Bb, Eb e C.
