# Preparar os arquivos de uma partitura

Este roteiro começa com uma partitura pronta no MuseScore (`.mscz`) e termina
com a pasta de arquivos usada pelo Clave Sol. Para o player com som gerado e
cursor, não é necessário criar MP3 ou Ogg.

## O que será criado

Para a lição cadastrada em:

```text
partituras/metodos/domingos-pecci/clarinete-20p40.md
```

a pasta correspondente é:

```text
assets/music/metodos/domingos-pecci/clarinete-20p40/
├── score.musicxml   obrigatório para gerar o som
├── score-1.svg      primeira página visível no site
├── score-2.svg      segunda página, se existir
├── timing.json      posições do cursor e tempos
├── score.pdf        opcional para download
└── score.mscz       opcional para download e edição
```

O arquivo `sequence.json` não deve ser criado nem editado. O gerador do site o
produz automaticamente a partir de `score.musicxml` durante a publicação.

## 1. Conferir a partitura no MuseScore

O arquivo `.mscz` usado aqui deve conter somente a lição que será publicada.
Se o arquivo reunir um método inteiro, salve uma cópia contendo apenas a lição;
caso contrário, páginas, duração e player abrangerão o método inteiro.

Abra o `.mscz` e confirme:

1. instrumento e transposição;
2. fórmula de compasso, armadura, notas e pausas;
3. andamento escrito na partitura;
4. número e ordem das páginas;
5. reprodução do começo ao fim.

O andamento precisa estar realmente configurado no MuseScore. Um texto como
“Moderato” sem uma marca de metrônomo não fornece uma velocidade ao player.

O som gerado atende lições com notas, pausas, acordes, vozes, ligaduras de
prolongamento e instrumentos transpositores. Repetições, casas, saltos,
ornamentos e percussão devem usar áudio gravado; consulte a seção
“Quando usar áudio gravado” no final deste roteiro.

## 2. Entrar na raiz do repositório

No terminal:

```sh
cd /home/djames/Documents/ClaveSol/site/clavesol
```

Defina o arquivo original e a pasta da lição. Para o teste atual, o arquivo já
está neste caminho:

```sh
score_source="/home/djames/Documents/MuseScore4/Scores/DomingosPecci.mscz"
asset_dir="assets/music/metodos/domingos-pecci/clarinete-20p40"
mkdir -p "$asset_dir"
```

O valor de `asset_dir` deve repetir o caminho do Markdown depois de
`partituras/`, sem a extensão `.md`.

## 3. Exportar o MusicXML

No Linux deste computador, o executável está em
`/home/djames/bin/musescore`:

```sh
/home/djames/bin/musescore -o "$asset_dir/score.musicxml" "$score_source"
```

Também é possível usar a interface do MuseScore: **Arquivo → Exportar**,
escolher **MusicXML não comprimido** e salvar com o nome exato
`score.musicxml` dentro da pasta da lição.

Não use o formato comprimido `.mxl`, pois o gerador procura especificamente
`score.musicxml`.

## 4. Gerar as páginas e o cursor

O comando `--score-media` do MuseScore reúne as páginas SVG e as posições da
reprodução em um JSON temporário:

```sh
QT_QPA_PLATFORM=offscreen /home/djames/bin/musescore \
  --score-media "$score_source" \
  > /tmp/clarinete-20p40-media.json \
  2> /tmp/clarinete-20p40-musescore.log
```

Confirme que o resultado é um JSON válido:

```sh
python -m json.tool /tmp/clarinete-20p40-media.json > /dev/null
```

Agora converta esse arquivo para o formato do site:

```sh
python scripts/score_timing.py \
  /tmp/clarinete-20p40-media.json \
  "$asset_dir"
```

O resultado esperado é semelhante a:

```text
2 página(s), 86 posições, 52 segundos
```

O conversor cria `score-1.svg`, as demais páginas numeradas e `timing.json`.
Esses arquivos vêm da mesma exportação e, por isso, o cursor fica alinhado à
imagem.

Se estiver atualizando uma lição e os arquivos já existirem, use:

```sh
python scripts/score_timing.py \
  /tmp/clarinete-20p40-media.json \
  "$asset_dir" \
  --force
```

Se a nova versão tiver menos páginas, o conversor avisará sobre SVGs
excedentes. Confira a nova quantidade antes de remover as páginas antigas.

## 5. Adicionar downloads opcionais

Para oferecer PDF:

```sh
/home/djames/bin/musescore -o "$asset_dir/score.pdf" "$score_source"
```

Para oferecer também o arquivo editável do MuseScore:

```sh
cp "$score_source" "$asset_dir/score.mscz"
```

Esses dois arquivos são opcionais e não interferem no player.

## 6. Conferir o cadastro Markdown

O arquivo `partituras/metodos/domingos-pecci/clarinete-20p40.md` pode ficar
assim:

```md
Title: Domingos Pecci — Lição 20, página 40
Author: Domingos Pecci
Instrument: Clarinete em Si♭
Description: Orientações e partitura para estudar a lição 20 da página 40.
Lesson: 20
Playback: generated
Cursor: true
Draft: false

## Orientações de estudo

O segundo pentagrama usa os superagudos. Pule-o, se desejar, mas é interessante
conhecer e praticar esse registro.
```

`Playback: generated` e `Cursor: true` tornam a intenção explícita. Mesmo sem
esses campos, o site detecta MusicXML e mapa de cursor automaticamente.

Não é necessário preencher `Assets` quando a pasta segue o mesmo caminho do
Markdown. Também não é necessário preencher `Pages` ou `Measures`: o gerador
detecta esses valores.

## 7. Validar antes de publicar

Com o ambiente Python do projeto ativado:

```sh
BASE_PATH='' python build.py
python scripts/check_links.py
python -m http.server 8000 --directory dist
```

Abra no navegador:

```text
http://localhost:8000/partituras/metodos/domingos-pecci/clarinete-20p40/
```

Confira estes pontos:

- todas as páginas aparecem e estão legíveis;
- o andamento exibido corresponde ao MuseScore;
- reproduzir, pausar, avançar e voltar funcionam;
- o cursor acompanha a nota correta;
- 50%, 75%, 125% e 150% alteram a velocidade sem mudar a afinação;
- “Mudo para solfejo” silencia o som, mas mantém relógio e cursor;
- PDF e MuseScore aparecem como downloads somente quando foram adicionados.

Encerre o servidor com `Ctrl+C`.

## 8. Publicar

Veja primeiro o que será enviado:

```sh
git status --short
```

Adicione somente o cadastro e a pasta dessa lição:

```sh
git add \
  partituras/metodos/domingos-pecci/clarinete-20p40.md \
  assets/music/metodos/domingos-pecci/clarinete-20p40/
git commit -m "Adiciona lição 20 do método Domingos Pecci"
git push origin main
```

O GitHub Actions valida, gera e publica o site. A pasta `dist/` não deve entrar
no commit.

## Quando atualizar uma partitura

Depois de alterar notas, compassos, transposição, andamento ou diagramação no
MuseScore, repita as exportações de `score.musicxml`, `--score-media`, SVGs e
`timing.json`. Todos precisam vir da mesma versão do `.mscz`.

Se o site informar que MusicXML e `timing.json` têm durações diferentes, uma
das exportações ficou antiga. Refaça os passos 3 e 4.

## Quando usar áudio gravado

Se a partitura tiver repetições, casas, saltos, ornamentos, percussão ou se for
importante preservar o som do Muse Sounds, exporte `score.mp3` ou `score.ogg`
para a mesma pasta e use no Markdown:

```md
Playback: recorded
```

O `timing.json` continua opcional. Se ele existir, deve ser produzido da mesma
revisão e com o mesmo andamento do áudio.
