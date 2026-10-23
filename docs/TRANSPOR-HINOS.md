# Mudar a escrita sem mudar a música

`~/Documents/ClaveSol/SITE/clavesol/transpor_hinos.py`

Este script altera a **tonalidade escrita**, preservando a tonalidade sonora, as alturas, os tempos e as durações das notas. Muda a armadura e as notas escritas e compensa a diferença na transposição do instrumento. O timbre/programa MIDI e as claves, incluindo Sol oitava abaixo, permanecem como estavam.

Isso produz uma partitura para instrumento transpositor: uma pessoa que a ler em um instrumento não transpositor poderá tocar em outra altura. Para obter uma partitura de concerto em Dó, o hino precisa já soar em Dó. No hino 52, a armadura de concerto é Dó e a configuração original tinha transposição de flauta contralto; a correção para escrita em Dó zera essa transposição.

## Uso

```bash
cd ~/Documents/ClaveSol/SITE/clavesol
.venv/bin/python transpor_hinos.py \
  ../clavesol-hinos-do/assets/music/hinos/do/hino-52/score.mscz \
  --tonalidade C
```

Cria `FIX-score.mscz` ao lado do original. Nunca sobrescreve a entrada nem uma saída FIX já existente. Uma entrada FIX gera FIX-FIX. A miniatura antiga é removida, pois retratava outra escrita.

- `--tonalidade`: obrigatória; tonalidade **escrita inicial**, maior. Aceita Cb, Gb, Db, Ab, Eb, Bb, F, C, G, D, A, E, B, F# e C#. Modulações posteriores são deslocadas pelo mesmo intervalo, não apagadas.
- `--vozes`: opcional, padrão `1,2,3,4`. Aceita os pares completos `1,2` (pentagrama superior) ou `3,4` (inferior), ou os quatro. Não aceita apenas uma voz, pois a compensação se aplica ao instrumento inteiro. Não precisa separar notas reunidas em acordes.
- `--musescore`: executável; padrão `~/bin/musescore`. Não é o nome do arquivo de saída.
- `--saida`: caminho opcional do MSCZ de saída. Sem ele usa `FIX-<entrada>`. Não sobrescreve arquivos e não pode ser combinado com `--to-site`.
- `--to-site`: exporta e substitui os assets cadastrados, conforme abaixo.

**`--up` e `--down` foram removidos.** Eles permitiam alterar a música. Agora o intervalo é deduzido da armadura original e da desejada; usa o intervalo mais próximo, preservando a altura sonora. A origem e a saída são exportadas pelo MuseScore em área temporária e comparadas pelo mesmo parser usado no site. Não há opção para ignorar essa verificação. Se som, letra, compassos ou claves divergirem, a saída não é publicada.

As dependências são o ambiente Python `.venv` do site e o MuseScore instalado. É uma verificação das notas MIDI e de seus tempos/durações, não uma comparação de arquivos WAV sintetizados.

## Exemplo em duas passadas, quando necessário

```bash
.venv/bin/python transpor_hinos.py /caminho/score.mscz --tonalidade C --vozes 1,2
.venv/bin/python transpor_hinos.py /caminho/FIX-score.mscz --tonalidade C --vozes 3,4
```

Para o hino 52 basta uma passada com todas as vozes. A nota superior inicial fica Sol4. No pentagrama inferior, o tenor fica Sol3 no MusicXML, desenhado na posição de Sol4 devido à clave Sol oitava abaixo. O Lá do teste antigo alterava o som e não é mantido.

## Preparação do site

**`--to-site` não foi executado nos testes.** Exige uma entrada na pasta cadastrada `assets/music/hinos/<coleção>/hino-N/`, em repositório com `hinario.json` e cadastro Markdown correspondente.

```bash
.venv/bin/python transpor_hinos.py \
  ../clavesol-hinos-do/assets/music/hinos/do/hino-52/score.mscz \
  --tonalidade C --to-site
```

Primeiro transforma e verifica a igualdade sonora. Depois salva backup durável dos assets e do cadastro em `~/Documents/ClaveSol/backups-transposicao/<data-hora>/`. Reutiliza `criar_licao.prepare` para exportar MusicXML, SVGs, cursor/timing e PDF quando já cadastrado, validando os dados. Substitui `score.mscz` e os exports oficiais, sem prefixo FIX. Por fim executa `build.py`, recriando `dist/`, inclusive `sequence.json` e o site, com `BASE_PATH=''` para hospedagem na raiz do domínio.

Não executa comandos Git: revisão, commit e push ficam com o usuário. Se o build final falhar após a importação, os assets podem já estar atualizados; o backup permanece e o comando retorna erro. O importador preserva arquivos auxiliares: mova as cópias FIX para fora de assets antes de publicar caso não queira distribuí-las.

## Limites

Suporta MSCZ com uma única partitura e SATB em dois pentagramas, cada um em um Part, e armadura inicial explícita. Rejeita seleção parcial de um par, som de concerto ativado, mudanças de instrumento, cifras sem fundamental estruturada (exceto `*` e N.C.), armaduras customizadas/atonais e transposições que excedam os limites de acidentes ou notas suportados. Não modifica nomes de notas em textos livres.

Alterar a escrita é diferente de corrigir notas que já soam erradas: este comando deliberadamente preserva o som original. O nome do instrumento no cadastro permanece; seus campos numéricos de transposição são os ajustados.

## Teste no hino 52

As cópias antigas `FIX-score.mscz` e `FIX-FIX-score.mscz`, que alteravam a música, foram removidas com autorização. Foi gerado um novo `FIX-score.mscz` a partir do original, que permaneceu intacto.

A exportação confirmou **258 notas sonoras idênticas**, inclusive seus tempos e durações. Armaduras escritas em Dó; transposição de instrumento zerada; claves preservadas. A suíte também verifica escritas em Bb e Eb, seleção por pares, idempotência, preservação do arquivo original e rejeição dos parâmetros antigos e de sobrescrita.

```bash
.venv/bin/python tests/transpor-hinos.test.py
```

## Correção em lote do hinário Dó

`corrigir_hinario_do.py` aplica a correção de escrita a cada hino usando **sua própria armadura de concerto**, sem escolher uma única tonalidade para todo o hinário. Exige a configuração de origem confirmada: transposição cromática −5 e diatônica −3 nos dois instrumentos. O hino 52 é sempre ignorado.

```bash
.venv/bin/python corrigir_hinario_do.py --destino ~/Documents/ClaveSol/correcoes-hinario-do/novo-lote
```

O destino deve ser novo, fora dos assets. Cada pasta de hino recebe `original.mscz` (backup) e, somente após validação no MuseScore, `FIX-score.mscz`. `relatorio.json` lista tonalidades, notas, hashes das origens, arquivos ausentes e eventuais falhas. O comando retorna erro se qualquer hino falhar; não publica resultados inválidos. Usa três processos de exportação concorrentes por padrão (`--jobs 1` a `4`). Não modifica assets, não gera o site e não executa Git.

Para preparar uma cópia validada posteriormente, coloque-a na pasta cadastrada do hino e use o script individual com `--tonalidade` correspondente ao relatório e `--to-site`. Não execute esse procedimento sobre arquivos com status de erro. A cópia já está na tonalidade desejada, portanto a transformação é idempotente. A publicação em lote do site não é executada por este comando.

### Aplicação completa do lote ao site

`aplicar_correcao_hinario_do.py --lote <pasta-do-lote> --trabalho <pasta-nova>` exporta os 479 hinos em cópia isolada do repositório, compara as sequências sonoras com o site atual, sincroniza SVGs/cursor, gera o build completo e só então aplica os assets/cadastros e `dist/`. O hino 52 é preservado. As origens devem corresponder aos hashes do lote; alterações concorrentes cancelam a aplicação. Backup durável em `<trabalho>/backup`; estado em `status.json`; log do build em `build.log`. Falhas de exportação/build não alteram o repositório; falhas durante a aplicação fazem rollback dos arquivos já substituídos. Não executa Git. Durante a fase final de aplicação, aguarde `status: concluido` antes de fazer commit.


## Transpor cifras junto com as notas

As cifras estruturadas do MuseScore acompanham o intervalo da escrita. O script transpõe a fundamental e o baixo de inversões (por exemplo, G7/B → F7/A), preservando qualidade, extensões e demais informações. Suporta tanto `harmonyInfo` das versões recentes quanto os campos diretos das versões antigas. Asteriscos de introdução e marcadores N.C. permanecem intactos. Cifras digitadas como texto livre não são adivinhadas: o script pede revisão manual.

Na validação, os dois arquivos são exportados pelo MuseScore; além das notas, o programa compara as fundamentais e baixos em altura de concerto e a qualidade das cifras. Não há reprodução sonora durante o teste.

Exemplo: escrita em Sol para Si♭ → escrita em Fá para Dó:

```bash
.venv/bin/python transpor_hinos.py \
  ../sol-gesu-clarinete-Bb-tom-G-2026.mscz \
  --tonalidade F \
  --saida ../sol-gesu-C-tom-F.mscz
```

Nesse arquivo, o pentagrama superior passa de −2 para 0 semitons de transposição. O inferior, originalmente de clarinete baixo, passa de −14 para −12: conserva a oitava grave original. A escrita e as cifras ficam em Fá, mas o pentagrama inferior ainda soa uma oitava abaixo do escrito. O script conserva as claves e os nomes/timbres dos instrumentos; não converte automaticamente essa configuração de oitava em outra clave.
