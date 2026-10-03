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

Para **hinos**, use `--hinos` e escolha o hinário com `--hinario`:

```sh
python3 criar_licao.py "/caminho/completo/hino-1.mscz" \
  --hinos --hinario bb --licao 1 --pdf --commit
```

`--metodo NOME`, `--msa` e `--hinos` são alternativas: use apenas uma.
`--licao 1` também serve para ordenar os hinos pelo número.
Troque o caminho pelo arquivo **daquela lição**, já salvo no MuseScore. O
script não altera o original. Se omitir as três opções, ele mantém a seleção
interativa por **número** entre os métodos existentes. Para MSA ou Hinos, informe
explicitamente `--msa` ou `--hinos`; esses modos não perguntam o método. Sem `--commit`, prepara
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
  um índice MSA que já exista. Com `--hinos`, faz o equivalente em
  `partituras/hinos/_index.md`, com o título Hinos.
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
`--licao`, `--atualizar` e `--commit` funcionam nos três modos.
`--nome-metodo` é exclusivo para métodos e não é aceito com `--msa` nem `--hinos`.

Para `hino-1.mscz`, com `--hinos`:

```text
partituras/hinos/hino-1.md
assets/music/hinos/hino-1/
    score.musicxml
    score-1.svg
    timing.json
    score.mscz
    score.pdf        (com --pdf)
```

A página será `/partituras/hinos/hino-1/`. A categoria Hinos aparece na
estante de partituras quando o conteúdo for publicado. Cada hino é
independente; o modo Hinos usa o mesmo player e tem as mesmas limitações
musicais dos outros modos, inclusive para repetições.

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

Para atualizar um hino, preservando seu texto:

```sh
python3 criar_licao.py "/caminho/completo/hino-1.mscz" \
  --hinos --licao 1 --atualizar --pdf --commit
```

Cadastros antigos que já tenham `Assets` personalizado mantêm essa pasta.
Por exemplo, a lição 107 pode continuar em `assets/music/107-msa-bb/`;
o importador não a move para `assets/music/msa/107-msa-bb/`. Também preserva
`Legacy`, para manter os endereços antigos. O commit usa o caminho real dos
assets, sem incluir os índices de métodos no caso de uma lição MSA ou de um hino.

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

O importador confere cada posição do cursor com os inícios de notas e pausas
do MusicXML, usando o mesmo relógio que gera o som. Ele exige correspondência
na quantidade e ordem das posições e na distribuição por compasso. Se essa
correspondência falhar, interrompe a importação em vez de tentar adivinhar.

Os tempos de cada posição e a duração final vêm do MusicXML; as coordenadas
e páginas continuam vindo do MuseScore. **Não há multiplicação dos tempos
pela razão entre durações totais.** Uma fermata final ou uma cauda de reprodução
pode aumentar a duração informada pelo MuseScore sem alterar os inícios das
notas anteriores. Comprimir a lição inteira nesse caso causaria desvio crescente.

O som gerado mantém as durações escritas: não acrescenta prolongamento
expressivo de fermatas. O cursor segue essa mesma interpretação. Para preservar
as fermatas e a interpretação sonora do MuseScore, use o fluxo manual com
áudio gravado. `--tempo` altera o andamento do estudo e de seu cursor juntos.

Lições importadas anteriormente com ajuste proporcional precisam ser
reimportadas com `--atualizar`; mudar apenas o script não corrige mapas já
gerados. Exemplo:

```sh
python3 criar_licao.py "/caminho/MSA - 109.mscz" \
  --msa --slug msa-109 --licao 109 --atualizar
```

Se outra lição incompleta bloquear o catálogo, finalize-a ou marque seu
Markdown como `Draft: true`. O script não desativa nem altera outras lições
para fazer a validação passar. Em caso de falha de exportação ou validação,
os arquivos existentes da lição permanecem intactos.

## Hinários por altura: Bb, Eb e C

A página Partituras → Hinos mostra os cards Bb, Eb, C e Outros.
Use `--hinario bb`, `--hinario eb`, `--hinario do` ou `--hinario outros`
junto de `--hinos`. O diretório `do` aparece no site como **C**.

```sh
python criar_licao.py "$HOME/Documents/ClaveSol/lab/Musescore4/bb/hino-1.mscz" --hinos --hinario bb --licao 1 --pdf
python criar_licao.py "$HOME/Documents/ClaveSol/lab/Musescore4/eb/hino-1.mscz" --hinos --hinario eb --licao 1 --pdf
python criar_licao.py "$HOME/Documents/ClaveSol/lab/Musescore4/do/hino-1.mscz" --hinos --hinario do --licao 1 --pdf
```

Nomes iguais são independentes: cada um ocupa
`partituras/hinos/<hinario>/hino-1.md` e
`assets/music/hinos/<hinario>/hino-1/`. Não há transposição automática:
o importador respeita a escrita e a configuração de instrumento do original.
`--hinos` sem `--hinario` mantém o comportamento antigo (diretamente em Hinos);
para conservar a organização nova, sempre informe o hinário.

As seis partituras anteriormente na raiz de Hinos estão em Outros. Seus
endereços antigos continuam acessíveis por `page_aliases.json`, com URL
canônica apontando para a página nova. A configuração não altera os originais
no diretório de trabalho do MuseScore.

### Importação em lote (somente partituras funcionais)

Na raiz do projeto, execute:

```sh
.venv/bin/python scripts/importar_hinarios.py
```

O script usa, por padrão, os originais em
`~/Documents/ClaveSol/lab/Musescore4/{bb,eb,do}` e prepara os resultados em
`~/Documents/ClaveSol/lab/hinarios-para-publicar/`.

Ele executa o mesmo `prepare()` usado pelo importador individual:
MusicXML, SVGs, cursor e cópia do MSCZ. **Não gera PDF, não converte para
WebP e não publica partituras sem player.** Somente hinos com som e cursor
validados entram no resultado. Os incompatíveis são listados em
`relatorio-excluidos.csv`, com o arquivo original e o motivo, para correção.

A execução acontece inteiramente no computador, sem chamadas a IA e sem
consumir o plano do Codex. Usa quatro processos; `--workers 8` permite mais
paralelismo em computadores com memória suficiente. Cada MuseScore pode
consumir bastante memória durante a exportação.

Pode interromper com Ctrl+C e repetir o comando. Arquivos concluídos e
inalterados são reaproveitados. Originais corrigidos são detectados pelo hash;
use `--tentar-excluidos` para tentar também os erros cujo arquivo não mudou.
`--source`, `--stage` e `--musescore` permitem personalizar os caminhos.

Ao terminar, o script grava `CONCLUIDO.json`, `relatorio.json` e o relatório
de exclusões na pasta de resultados. Ele **não modifica o catálogo do site,
não faz commit e não faz push**. Avise que terminou para continuarmos com a
revisão, instalação dos arquivos funcionais e publicação. Os originais
permanecem intactos.


## Hinários em repositórios separados

Os hinários Bb, Eb e C ficam, respectivamente, nos repositórios `clavesol-hinos-bb`, `clavesol-hinos-eb` e `clavesol-hinos-do`, ao lado deste projeto. Execute `criar_licao.py --hinos --hinario bb|eb|do` dentro do repositório correspondente (usando apenas uma dessas opções), com o caminho completo do MSCZ. Faça commit e push nesse repositório. O hinário Outros continua no blog principal.

O arquivo `external_hymns.json` do blog guarda os endereços e os nomes das partituras de cada coleção para manter as contagens dos cards e redirecionar endereços antigos. Ao adicionar um hino, acrescente seu slug à coleção correspondente. Os arquivos musicais não devem ser duplicados no blog.

Consulte `docs/HINARIOS-GITHUB-PAGES.md` para ativar a publicação dos três repositórios.

### Posições invisíveis exportadas pelo MuseScore

O importador trata automaticamente posições extras de cursor com largura zero, como as encontradas nos hinos 4 e 82 de Bb. Elas só são removidas quando explicam exatamente o excesso em relação ao MusicXML. As verificações de ordem, quantidade de compassos e associação das posições aos compassos continuam obrigatórias. O MSCZ original não é alterado. A correção também vale para o importador em lote; para arquivos marcados anteriormente como excluídos, use a opção `--tentar-excluidos` quando decidir executar novamente o lote.

### Ritornelos e casas numeradas

O importador expande ritornelos em uma sequência de execução, mantendo os SVGs originais. Suporta retorno ao início quando não há abertura explícita, ritornelos consecutivos ou aninhados sem ambiguidade, e casas simples ou compartilhadas (`1,2` e depois `3`). Som, cursor, fermatas e BPM acompanham cada passagem; a barra de progresso inclui todas as repetições.

As propriedades de reprodução precisam concordar com a impressão: escrever “1.2.” sobre uma casa não configura automaticamente as passagens 1 e 2. Casas incompletas, conflitantes entre partes ou ritornelos sem fechamento são rejeitados com um diagnóstico. D.C., D.S., Coda e Fine como comandos de salto ainda não estão implementados; uma barra final comum é suportada. O importador não deduz esses comandos a partir de textos decorativos.

Antes de gravar qualquer asset, o percurso completo, a quantidade de posições e a associação de cada posição à sua passagem são conferidos contra a exportação do MuseScore. Não há PDF nem áudio gravado nesse processo.

No hino 226 de Bb, foram ajustadas apenas as passagens da casa “1.2.” e as três execuções do ritornelo. Backup original: `~/Documents/ClaveSol/lab/backups/hino-226-bb-20261003-001004/hino-226.mscz`.

### Tentar novamente somente as pastas de faltantes

Para processar `bb-falta`, `do-falta` e `eb-falta`, preservando os destinos corretos `bb`, `do` e `eb`:

```bash
.venv/bin/python scripts/importar_hinarios.py --somente-faltantes \
  --source ~/Documents/ClaveSol/lab/Musescore4 \
  --stage ~/Documents/ClaveSol/lab/hinarios-faltantes-2026-10-03 \
  --workers 4
```

O lote continua sem publicar e sem gerar PDFs: prepara apenas os casos com player e cursor válidos, com relatório dos demais. Uma pasta de resultados nova evita reutilizar resultados de versões antigas do importador. Para retomar a mesma execução, use o mesmo comando; para repetir tentativas anteriormente excluídas nessa pasta de resultados, acrescente `--tentar-excluidos`.
