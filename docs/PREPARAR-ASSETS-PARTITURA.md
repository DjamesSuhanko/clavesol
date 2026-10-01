# Preparar os arquivos de uma partitura

Este roteiro começa com uma partitura pronta no MuseScore (`.mscz`) e termina
com a pasta de arquivos usada pelo Clave Sol. Para o player com som gerado e
cursor, não é necessário criar MP3 ou Ogg.

## Um arquivo original por lição

O método é uma coleção, não o nome obrigatório do arquivo MuseScore.
Crie e salve **cada lição separadamente**, por exemplo:

```text
MuseScore4/Scores/domingos-pecci/
├── clarinete-20p40.mscz
└── clarinete-21p41.mscz
```

São exemplos de nomes e caminhos, não arquivos já criados. Você pode usar
outros nomes nos originais; `score_source` deve apontar para a lição desejada.
Não use um arquivo existente chamado `DomingosPecci.mscz` como substituto
para uma lição que você ainda vai escrever.

O catálogo e os arquivos exportados ficam em duas árvores separadas, ambas
partindo da **raiz do repositório**:

```text
partituras/metodos/domingos-pecci/
├── _index.md                 apresentação do método (uma vez)
├── clarinete-20p40.md         cadastro da lição 20
└── clarinete-21p41.md         cadastro da lição 21

assets/music/metodos/domingos-pecci/
├── clarinete-20p40/
│   ├── score.musicxml
│   ├── score-1.svg
│   ├── timing.json
│   └── score.mscz            cópia opcional da lição 20
└── clarinete-21p41/
    ├── score.musicxml
    ├── score-1.svg
    ├── timing.json
    └── score.mscz            cópia opcional da lição 21
```

`score.mscz` é apenas o nome padronizado da cópia oferecida para download
pelo site. **Não renomeie seu original para isso.** As cópias podem ter o mesmo
nome porque cada uma fica em sua própria pasta de lição. O mesmo vale para
`score.musicxml`, `score-1.svg` e `timing.json`.

Não crie `assets/` dentro de `partituras/metodos/domingos-pecci/`. Isso não
é o caminho que o gerador procura. Cada Markdown produz uma página
independente, como `/partituras/metodos/domingos-pecci/clarinete-20p40/`.

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

Depois de escrever e salvar a lição, defina seu arquivo original e a pasta
de destino. O caminho abaixo é um exemplo: ajuste para onde você salvou
**essa lição**. Execute os passos seguintes no mesmo terminal:

```sh
score_source="/home/djames/Documents/MuseScore4/Scores/domingos-pecci/clarinete-20p40.mscz"
lesson_key="metodos/domingos-pecci/clarinete-20p40"
asset_dir="assets/music/$lesson_key"
mkdir -p "$asset_dir"
```

`lesson_key` repete o caminho do Markdown depois de `partituras/`, sem `.md`.
Para a próxima lição, mude `score_source` e `lesson_key`; os demais comandos
continuam iguais. Não reutilize a pasta de saída da lição anterior.

Antes de exportar, confira:

```sh
test -f "$score_source" && printf 'Arquivo de origem encontrado\n'
```

Se não aparecer a confirmação, pare e corrija o caminho. Não é necessário
que o nome original corresponda ao nome do método ou ao nome padronizado
`score.mscz`.

Os comandos `python` abaixo pressupõem um ambiente virtual ativado com
as dependências de `requirements.txt`. Neste computador, o Python do sistema
não tem o comando `python` nem o pacote Markdown; somente trocar para
`python3` não resolve essa dependência. Para esta sessão, pode usar o ambiente
já preparado:

```sh
. /home/djames/Documents/Codex/2026-09-30/s/work/runtime/bin/activate
python -c 'import markdown; print("Ambiente pronto")'
```

Esse ambiente pertence à área de trabalho desta sessão. Se ele for removido,
prepare outro ambiente virtual com `requirements.txt` antes de continuar.

## 3. Exportar o MusicXML

No Linux deste computador, o executável está em
`/home/djames/bin/musescore`:

```sh
QT_QPA_PLATFORM=offscreen /home/djames/bin/musescore -o "$asset_dir/score.musicxml" "$score_source"
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
media_dir="$(mktemp -d)"
QT_QPA_PLATFORM=offscreen /home/djames/bin/musescore \
  --score-media "$score_source" \
  > "$media_dir/media.json" \
  2> "$media_dir/musescore.log"
```

Confirme que o resultado é um JSON válido:

```sh
python -m json.tool "$media_dir/media.json" > /dev/null
```

Agora converta esse arquivo para o formato do site:

```sh
python scripts/score_timing.py \
  "$media_dir/media.json" \
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
  "$media_dir/media.json" \
  "$asset_dir" \
  --force
```

Se a nova versão tiver menos páginas, o conversor avisará sobre SVGs
excedentes. Confira a nova quantidade antes de remover as páginas antigas.

## 5. Adicionar downloads opcionais

Para oferecer PDF:

```sh
QT_QPA_PLATFORM=offscreen /home/djames/bin/musescore -o "$asset_dir/score.pdf" "$score_source"
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
Draft: true

## Orientações de estudo

O segundo pentagrama usa os superagudos. Pule-o, se desejar, mas é interessante
conhecer e praticar esse registro.
```

Mantenha `Draft: true` enquanto escreve a lição e prepara os arquivos.
Quando os assets estiverem completos, mude para `Draft: false` **antes**
da validação local: rascunhos são ignorados pelo gerador.

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

Adicione o cadastro e a pasta dessa lição. Na primeira lição do método,
inclua também seu `_index.md` para publicar o nome e a descrição da coleção:

```sh
git add \
  partituras/metodos/domingos-pecci/_index.md \
  "partituras/$lesson_key.md" \
  "$asset_dir/"
git commit -m "Adiciona lição 20 do método Domingos Pecci"
git push origin main
```

O GitHub Actions valida, gera e publica o site. A pasta `dist/` não deve entrar
no commit.

## Quando atualizar uma partitura

Depois de alterar notas, compassos, transposição, andamento ou diagramação no
MuseScore, repita as exportações de `score.musicxml`, `--score-media`, SVGs e
`timing.json`. Todos precisam vir da mesma versão do `.mscz`.

Se o site informar que MusicXML e `timing.json` têm durações diferentes,
confira primeiro se vieram da mesma revisão. **Esse erro também pode ocorrer
por arredondamento do MuseScore**, mesmo com exportações corretas.

A validação atual aceita diferença de até 0,05 segundo. No teste anterior
com um arquivo existente, o MusicXML resultou em 151,2 s e o mapa em 151 s;
esses arquivos seriam rejeitados. A alteração que ampliava a tolerância foi
revertida, portanto esse impedimento continua presente. Isso não valida nem
invalida a lição que você ainda vai criar: ela precisa ser testada separadamente.

Reexportar não resolve necessariamente um arredondamento. Não altere o
andamento nem os tempos manualmente para ocultar o erro; registre os dois
valores para uma correção funcional específica. Este roteiro não modifica
o player nem a validação.

## Quando usar áudio gravado

Se a partitura tiver repetições, casas, saltos, ornamentos, percussão ou se for
importante preservar o som do Muse Sounds, exporte `score.mp3` ou `score.ogg`
para a mesma pasta e use no Markdown:

```md
Playback: recorded
```

O `timing.json` continua opcional. Se ele existir, deve ser produzido da mesma
revisão e com o mesmo andamento do áudio.
