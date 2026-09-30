# Publicar partituras

Categorias e coleções são pastas. Cada lição é um Markdown. Não é necessário alterar Python para adicionar partituras.

```text
partituras/
├── msa/
│   ├── _index.md
│   └── 107-msa-bb.md
└── metodos/
    ├── _index.md
    └── domingos-pecci/
        ├── _index.md
        └── licao-27.md

assets/music/metodos/domingos-pecci/licao-27/
├── score-1.svg
├── score-2.svg       (se houver mais páginas)
├── score.musicxml   (opcional)
├── score.pdf        (opcional)
├── score.mscz       (opcional)
├── score.mp3        (opcional)
├── score.ogg        (opcional; alternativa ao MP3)
└── timing.json      (opcional; cursor sincronizado)
```

Use letras minúsculas, números e hífens nos nomes de pastas e arquivos Markdown. Títulos visíveis podem conter espaços, acentos e símbolos musicais. A categoria e a coleção vêm das pastas; não preencha `Category` ou `Collection` no Markdown. O leitor reconhece até dois níveis de agrupamento: categoria e coleção.

## Exemplo: Método Domingos Pecci, lição 27

Na raiz do clone:

```sh
mkdir -p partituras/metodos
cp -r templates/partituras/domingos-pecci partituras/metodos/
mkdir -p assets/music/metodos/domingos-pecci/licao-27
```

Execute a cópia apenas para criar uma coleção nova, sem substituir arquivos que você já editou. O modelo começa com `Draft: true`; portanto a lição só será publicada quando você trocar para `false`.

Coloque os arquivos exportados na pasta de assets acima. Para começar, basta **um SVG**, ou um arquivo **MusicXML, PDF ou MSCZ** para download. SVG permite leitura e zoom na própria página. MusicXML sozinho oferece download, sem converter a notação no navegador.

Edite `partituras/metodos/domingos-pecci/licao-27.md`:

```md
Title: Domingos Pecci — Lição 27
Author: Domingos Pecci
Instrument: Clarinete em Si♭
Description: Orientações para estudar a lição 27.
Lesson: 27
Draft: false

## Antes de tocar

Escreva aqui suas orientações sobre ritmo, articulação e andamento.

[Material complementar]({{BASE}}/gem/)
```

Mantenha a linha em branco após os metadados. A URL será:

`/partituras/metodos/domingos-pecci/licao-27/`

O nome do arquivo define o endereço; `Lesson` determina a ordem numérica na coleção (2 antes de 10). Sem `Lesson`, a lição fica antes das numeradas, ordenada pelo título.

## Nome e descrição da coleção

Em `partituras/metodos/domingos-pecci/_index.md`:

```md
Title: Método Domingos Pecci
Description: Lições para o estudo do clarinete.

Aqui você pode escrever uma apresentação do método.
```

Use `_index.md` também para nomear uma categoria. Sem ele, o nome vem da pasta e a coleção é criada quando há lições publicadas. Um índice explícito aparece mesmo sem lições, com indicação de catálogo vazio. Os modelos em `templates/` nunca entram no site.

## Arquivos e opções

O gerador procura os assets em `assets/music/` seguido do mesmo caminho do Markdown, sem `.md`. Para usar outra pasta, informe `Assets: music/minha-pasta` (relativo a `assets/`, sem barra inicial).

| Campo | Como funciona |
|---|---|
| `Title` | Obrigatório para uma lição publicada. |
| `Author`, `Instrument`, `Description` | Informações opcionais exibidas na página. |
| `Lesson` | Inteiro positivo, para ordenar as lições. |
| `Draft: true` | Não gera página nem cartão; arquivos ainda não são exigidos. |
| `Pages` | Opcional: confere a quantidade de SVGs. Normalmente é detectada. |
| `Measures` | Opcional: total de compassos. Detectado do mapa quando há cursor. |
| `Audio: false` | Oculta o player mesmo que haja áudio. Por padrão, detecta MP3/Ogg. |
| `Cursor: false` | Desativa o cursor. Por padrão, detecta timing + áudio + SVGs. |
| `Audio: true` / `Cursor: true` | Exige os arquivos necessários, apontando erro se faltarem. |
| `Legacy` | Para migração de URLs antigas em `musica/`; não é necessário em novas lições. |

Os SVGs devem ser consecutivos: `score-1.svg`, `score-2.svg` etc. Todas as páginas aparecem na leitura, com atalhos e zoom. Para imprimir, use a impressão do navegador. O PDF opcional fica disponível como download independente.

`Draft` oculta o cadastro do catálogo, mas arquivos que você colocar em `assets/` são públicos. Guarde arquivos ainda privados fora de `assets/` até a publicação.

## Áudio e cursor

Exporte `score.mp3` e/ou `score.ogg` pelo MuseScore a partir da mesma revisão da partitura. Basta um dos dois para ativar reprodução e velocidade. Sem `timing.json`, o player funciona sem cursor.

Para gerar o cursor, exporte o JSON de mídia com `--score-media` no MuseScore e passe o JSON puro (sem mensagens de inicialização) ao conversor:

```sh
python scripts/score_timing.py /caminho/media.json assets/music/metodos/domingos-pecci/licao-27
```

Esse comando extrai **todos os SVGs do próprio JSON** e gera `timing.json`, mantendo páginas e coordenadas da mesma exportação. Se já houver SVGs ou timing, confira os arquivos e use `--force` para substituí-los. O áudio e os downloads continuam sendo exportados separadamente da mesma revisão. Não renumere ou recorte os SVGs depois de gerar o mapa.

A escala padrão é 12, correspondente à exportação MSA usada neste projeto. Para outra resolução do MuseScore, informe `--scale`; o conversor valida os limites das posições, mas a sincronização e o alinhamento devem ser conferidos com o áudio no navegador.

No mapa, cada evento tem `time` em segundos, `page` começando em 1, `measure`, e `x`, `y`, `width`, `height` em porcentagens da página. Mapas antigos de uma página podem omitir `page`. O leitor acompanha mudanças de página, repetição e retorno no áudio.

## Conferir e publicar

Com as dependências do README instaladas:

```sh
BASE_PATH='' python build.py
python scripts/check_links.py
python -m http.server 8000 --directory dist
```

Abra `http://localhost:8000/partituras/` para conferir. A geração falha com o nome do cadastro quando falta um arquivo obrigatório ou o mapa é inválido, evitando publicar links quebrados.

```sh
git add partituras/ assets/music/
git commit -m "Adiciona lição 27 do método Domingos Pecci"
git push origin main
```

O GitHub Actions valida, gera e publica o site automaticamente. Não envie `dist/`.
