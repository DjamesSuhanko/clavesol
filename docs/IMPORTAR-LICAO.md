# Criar uma lição a partir do MuseScore

Na raiz do projeto, escolha o destino. Para um **método**, execute:

```sh
python3 criar_licao.py "/caminho/completo/clarinete-20p40.mscz" \
  --metodo domingos-pecci --licao 20 --commit
```

Para o **MSA**, use `--msa`, sem nome de método:

```sh
python3 criar_licao.py "/caminho/completo/108-msa-bb.mscz" \
  --msa --licao 108 --commit
```

`--metodo NOME` e `--msa` são alternativas: não podem ser usados juntos.
Troque o caminho pelo arquivo **daquela lição**, já salvo no MuseScore. O
script não altera o original. Se omitir ambas as opções, ele mantém a seleção
interativa por **número** entre os métodos existentes. Para MSA, informe
explicitamente `--msa`; nesse modo não há pergunta sobre método. Sem `--commit`, prepara
os arquivos e mostra os comandos para revisar, adicionar, commitar e publicar.
Com `--commit`, depois de uma importação bem-sucedida basta:

```sh
git push origin main
```

O script nunca faz push. A publicação acontece pelo GitHub Actions após o push.
O commit inclui somente a lição e os índices de sua coleção/categoria;
alterações de outros arquivos já colocadas no staging são preservadas.

## O que ele faz

- Identifica a lição pelo nome do `.mscz`, normalizado para minúsculas e hífens.
- Exporta `score.musicxml`, todas as páginas `score-1.svg`, `score-2.svg` etc.
- Gera `timing.json` e copia o original para `score.mscz`, para download.
- Com `--pdf`, também exporta `score.pdf`.
- Cria o Markdown da lição, já com `Playback: generated`, `Cursor: true` e
  `Draft: false`; autor e instrumento vêm do MusicXML quando disponíveis.
- Cria os índices da categoria e do método caso ainda não existam. No modo
  `--msa`, cria somente `partituras/msa/_index.md` se necessário, preservando
  um índice MSA que já exista.
- Valida a lição e o catálogo completo antes de instalar os arquivos.

Não cria MP3/Ogg. `sequence.json` será gerado automaticamente na publicação.
O `.mscz` deve conter apenas a lição. Repetições e outros recursos não
suportados pelo sintetizador são rejeitados, sem instalar uma lição parcial.
O título padrão é o nome do arquivo; use `--titulo` para personalizar.

## Cada lição tem sua pasta

Para `clarinete-20p40.mscz`, com `--metodo domingos-pecci`:

```text
partituras/metodos/domingos-pecci/clarinete-20p40.md
assets/music/metodos/domingos-pecci/clarinete-20p40/
    score.musicxml
    score-1.svg
    timing.json
    score.mscz
```

Uma segunda lição, por exemplo `clarinete-21p41.mscz`, gera outro Markdown e
outra pasta. Nenhum original precisa se chamar como o método. Use `--slug`
para escolher um identificador diferente do nome do arquivo.

Para `108-msa-bb.mscz`, com `--msa`:

```text
partituras/msa/108-msa-bb.md
assets/music/msa/108-msa-bb/
    score.musicxml
    score-1.svg
    timing.json
    score.mscz
```

A página será `/partituras/msa/108-msa-bb/`. `--pdf`, `--titulo`, `--slug`,
`--licao`, `--atualizar` e `--commit` funcionam nos dois modos.
`--nome-metodo` é exclusivo para métodos e não é aceito com `--msa`.

## Atualizar uma lição ou completar um Markdown existente

Sem `--atualizar`, o script recusa destinos existentes. Para completar seu
cadastro `clarinete-20p40.md` ou reexportar uma lição:

```sh
python3 criar_licao.py "/caminho/completo/clarinete-20p40.mscz" \
  --metodo domingos-pecci --licao 20 --atualizar --pdf --commit
```

Para atualizar uma lição MSA existente:

```sh
python3 criar_licao.py "/caminho/completo/107-msa-bb.mscz" \
  --msa --slug 107-msa-bb --licao 107 --atualizar --pdf --commit
```

Cadastros antigos que já tenham `Assets` personalizado mantêm essa pasta.
Por exemplo, a lição 107 pode continuar em `assets/music/107-msa-bb/`;
o importador não a move para `assets/music/msa/107-msa-bb/`. Também preserva
`Legacy`, para manter os endereços antigos. O commit usa o caminho real dos
assets, sem incluir os índices de métodos no caso de uma lição MSA.

O texto e os metadados editoriais existentes são preservados. O script ativa
som gerado, cursor e publicação (`Draft: false`), e atualiza contagens de páginas
ou compassos se esses campos existirem. `--titulo` e `--licao` substituem os
respectivos valores somente quando informados.

Os exports antigos são substituídos; páginas excedentes, gravações MP3/Ogg e
sequências antigas são removidas nessa pasta. Um PDF existente é reexportado.
Arquivos adicionais não pertencentes aos exports são preservados. Use como
origem o seu `.mscz` de trabalho, fora da pasta de assets.

## Instalação e execução

Neste computador, o ambiente `.venv` já está preparado na raiz do projeto.
`python3 criar_licao.py` usa esse ambiente automaticamente se o Python do
sistema não tiver Markdown. Em outra máquina, prepare um ambiente virtual
com Python 3.10 ou posterior e instale `requirements.txt`.

O MuseScore precisa estar instalado. O script procura `musescore`/`mscore`
no PATH, a variável `MUSESCORE`, ou `~/bin/musescore`. Também aceita
`--musescore /caminho/do/executavel`. As exportações têm limite de 180 segundos
por comando.

Execute `python3 criar_licao.py --help` para consultar todas as opções.
Para uma coleção nova, `--nome-metodo "Método Domingos Pecci"` define seu
nome visível. `--licao 20` define a ordem numérica, sem tentar inferir números
de nomes ambíguos como `20p40`.

## Duração e erros de validação

O importador normaliza o arredondamento da duração do MuseScore quando a
diferença para o MusicXML é de até meio segundo: usa a duração precisa do
MusicXML e mantém intactos os tempos e as coordenadas de cada posição.
Também verifica se todas as posições cabem nessa duração. Isso trata o caso
151 s / 151,2 s sem modificar o player ou sua validação.

Diferenças maiores interrompem a importação. Confira a partitura e o andamento.
`--tempo` permite informar semínimas por minuto quando necessário, mas o mapa
exportado também precisa corresponder a esse andamento; prefira configurar
uma marca de metrônomo no MuseScore.

Se outra lição incompleta bloquear o catálogo, finalize-a ou marque seu
Markdown como `Draft: true`. O script não desativa nem altera outras lições
para fazer a validação passar. Em caso de falha de exportação ou validação,
os arquivos existentes da lição permanecem intactos.
