# Publicar partituras

Para gerar o cadastro e os assets a partir de um `.mscz`, use o
[importador automático de lições](IMPORTAR-LICAO.md).

Categorias e coleções são pastas. Cada lição é um Markdown. Não é necessário alterar Python para adicionar partituras.

Para o processo completo, começando no arquivo `.mscz`, siga o
[roteiro para preparar os arquivos da partitura](PREPARAR-ASSETS-PARTITURA.md).

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

O `.mscz` original pode se chamar `clarinete-20p40.mscz`, `licao-27.mscz`
ou outro nome escolhido por você. Cada lição tem seu próprio original,
cadastro Markdown e pasta de assets. A cópia opcional para download chama-se
`score.mscz` **dentro da pasta de cada lição**; isso não exige renomear o original.
O método corresponde à pasta da coleção e ao seu `_index.md`.

## Exemplo: Método Domingos Pecci, lição 27

Na raiz do clone:

```sh
mkdir -p partituras/metodos
cp -r templates/partituras/domingos-pecci partituras/metodos/
mkdir -p assets/music/metodos/domingos-pecci/licao-27
```

Execute a cópia apenas para criar uma coleção nova, sem substituir arquivos que você já editou. O modelo começa com `Draft: true`; portanto a lição só será publicada quando você trocar para `false`.

Coloque os arquivos exportados na pasta de assets acima. Para começar, basta **um SVG**, ou um arquivo **MusicXML, PDF ou MSCZ** para download. SVG permite leitura e zoom na própria página. MusicXML sozinho oferece download e som gerado no navegador; para exibir a notação, forneça também os SVGs.

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
| `Playback: generated` | Gera o som a partir de `score.musicxml`. É o padrão quando esse arquivo existe. |
| `Playback: recorded` | Usa `score.mp3` e/ou `score.ogg` exportado no MuseScore. |
| `Playback: none` | Oculta o player, mantendo leitura e downloads. |
| `Tempo: 60` | Opcional: substitui o andamento por 60 semínimas/minuto. Sem esse campo, usa o andamento do MusicXML. |
| `Audio: false` | Forma antiga de ocultar o player. `Playback`, se informado, tem prioridade. |
| `Cursor: false` | Desativa o cursor. Por padrão, detecta timing + player + SVGs. |
| `Audio: true` / `Cursor: true` | Exige os arquivos necessários, apontando erro se faltarem. |
| `Legacy` | Para migração de URLs antigas em `musica/`; não é necessário em novas lições. |

Os SVGs devem ser consecutivos: `score-1.svg`, `score-2.svg` etc. Todas as páginas aparecem na leitura, com atalhos e zoom. Para imprimir, use a impressão do navegador. O PDF opcional fica disponível como download independente.

`Draft` oculta o cadastro do catálogo, mas arquivos que você colocar em `assets/` são públicos. Guarde arquivos ainda privados fora de `assets/` até a publicação.

## Áudio e cursor

Exporte `score.musicxml` pelo MuseScore. O gerador converte as notas automaticamente em `sequence.json`, e o navegador produz o som com um timbre simples de estudo. Não precisa exportar MP3/Ogg para cada lição. Quando usa som gerado, as gravações da pasta não entram na publicação; os originais locais são preservados.

O player permite reproduzir, pausar, voltar ao início, avançar para um trecho e mudar a velocidade entre 50% e 150%, sem mudar a afinação. **Mudo para solfejo** silencia o som mantendo tempo e cursor. O relógio mostra a posição na lição no andamento original; a velocidade altera o tempo real necessário para percorrê-la. Não há reprodução automática.

O andamento vem do MusicXML, inclusive unidades pontuadas e mudanças durante a peça. Se não houver andamento, informe `Tempo` em semínimas por minuto. O suporte inclui notas, pausas, acordes, vozes, ligaduras de prolongamento e transposição do instrumento. Não reproduz o realismo, os efeitos e a expressividade do MuseScore. Repetições, casas, saltos, notas de adorno e percussão exigem `Playback: recorded`; a geração rejeita esses recursos para evitar uma reprodução incompleta.

Para usar uma gravação, informe `Playback: recorded` e exporte `score.mp3` e/ou `score.ogg` pelo MuseScore a partir da mesma revisão da partitura. Sem MusicXML, o áudio gravado é detectado automaticamente. Sem `timing.json`, ambos os modos funcionam sem cursor.

Para gerar o cursor, exporte o JSON de mídia com `--score-media` no MuseScore e passe o JSON puro (sem mensagens de inicialização) ao conversor:

```sh
/home/djames/bin/musescore --score-media /caminho/partitura.mscz \
  > /tmp/media.json 2> /tmp/musescore.log
python scripts/score_timing.py /tmp/media.json assets/music/metodos/domingos-pecci/licao-27
```

Esse comando extrai **todos os SVGs do próprio JSON** e gera `timing.json`, mantendo páginas e coordenadas da mesma exportação. Se já houver SVGs ou timing, confira os arquivos e use `--force` para substituí-los. Exporte o MusicXML (ou o áudio gravado, conforme o modo) e os downloads separadamente, sempre da mesma revisão. No modo gerado, a duração do mapa deve coincidir com a sequência; ao alterar o andamento ou a partitura, reexporte também o mapa. Não renumere ou recorte os SVGs depois de gerar o mapa.

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
