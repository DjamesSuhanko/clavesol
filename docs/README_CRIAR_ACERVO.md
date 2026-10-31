# criar_acervo.py — atualização do gerador Clave Sol

Esta versão substitui `criar_hinario.py` e mantém os parâmetros anteriores. O arquivo foi revisado para criar **acervos de músicas ou de hinos**, sem transformar todas as coleções em hinários.

## Instalação

Na raiz do projeto principal (`~/Documents/ClaveSol/SITE/clavesol`):

```bash
cp criar_hinario.py criar_hinario.py.bak
cp /caminho/para/criar_acervo.py ./criar_acervo.py
python3 -m py_compile criar_acervo.py
```

O script continua dependendo dos módulos e dos templates **já existentes** no projeto. **Não remova** `templates/hinario-site/` ou `hinario.json`: esses nomes internos são preservados por compatibilidade.

Pré-requisitos: `music_pages.py` e `score_catalog.py` no site principal precisam conter a correção anterior dos rótulos (`Tipo: musicas`), e `templates/hinario-site/build.py` precisa conter a versão que entende a categoria `musicas`. O script verifica esses requisitos na criação de um novo site e mostra um erro claro se faltarem.

## Novo acervo de músicas

```bash
cd ~/Documents/ClaveSol/SITE/clavesol
python3 criar_acervo.py \
  --origem /home/djames/Documents/ABC/choro \
  --destino ../choro \
  --arquivos musicxml \
  --dominio choro \
  --titulo 'Chorinho' \
  --descricao 'Músicas para estudos.' \
  --repositorio DjamesSuhanko/clavesol-chorinho \
  --tipo musicas \
  --ignorar-incompativeis
```

A execução completa:

1. Reutiliza partituras previamente preparadas quando reconhecidas pelo manifesto; processa somente as novas/alteradas.
2. Agrupa músicas nos diretórios `partituras/musicas/<compositor>/` e `assets/music/musicas/<compositor>/`.
3. Executa o build local, configura o repositório e o GitHub Pages da coleção.
4. Registra **localmente** no site principal `partituras/choro/_index.md`, com `Title`, `Description`, `Link` e `Tipo: musicas`.
5. **Não publica o site principal**, não faz commit dele e **não executa o primeiro workflow Pages**. Assim você pode aguardar o DNS e testar o novo domínio antes de incluir o card publicamente.

## Ao terminar e depois de verificar o domínio

Confira o arquivo gerado:

```bash
cat ~/Documents/ClaveSol/SITE/clavesol/partituras/choro/_index.md
```

O esperado é:

```text
Title: Chorinho
Description: Músicas para estudos.
Link: https://choro.clavesol.com.br/
Tipo: musicas
```

Quando o site novo estiver acessível e você quiser publicar o card no site principal:

```bash
cd ~/Documents/ClaveSol/SITE/clavesol
python3 build.py
# Revise o card em dist/partituras/index.html antes de publicar.
git add partituras/choro/_index.md
git commit -m "Inclui Chorinho na estante de partituras"
git push origin main
```

Se a correção dos rótulos ainda não foi publicada no site principal, inclua também os arquivos alterados `score_catalog.py` e `music_pages.py` no commit, após revisar o diff.

## Modos e opções

- `--tipo musicas`: padrão; gera o rótulo **ACERVO MUSICAL** quando registrado como coleção externa.
- `--tipo hinos`: gera `Tipo: hinario` e mantém os caminhos antigos dos hinários.
- `--site-principal /outro/caminho`: altera a pasta que recebe o card (padrão: diretório do script).
- `--sem-cadastro-principal`: não cria/atualiza card no site principal.
- `--somente-local`: não usa GitHub e **não cadastra card** no site principal.
- `--simular`: imprime destinos sem modificar nada.
- `--ignorar-incompativeis`: permite prosseguir com os arquivos válidos quando houver erros de importação.

Se `partituras/<dominio>/_index.md` já existir, o script respeita o título e descrição personalizados; só acrescenta `Tipo` se faltar e se o `Link` concordar. Se apontar para outro URL ou tiver outro tipo, interrompe sem sobrescrever o cadastro.

## Limitações da verificação

Foram validados: sintaxe Python, registro de cards novos, retomada sem duplicação, preservação de índice existente, detecção de conflitos e inicialização de um acervo musical usando templates simulados. Não foi possível executar o MuseScore, o build real do projeto ou as chamadas GitHub nesta máquina. O template do projeto não foi anexado nesta doc; a checagem de compatibilidade exige que ele não use a validação antiga `s.parent=='hinos/'+config['collection']`.

## Carrossel

Aceita nomes numéricos (`01.webp`) ou com descrição após hífen, sublinhado ou espaço (`01-CantusCaeli.webp`). A ordem segue o número inicial. Use o mesmo nome-base para o texto: `01-CantusCaeli.txt`.

As imagens trocam automaticamente a cada **5 segundos**, voltando à primeira após a última. As setas continuam disponíveis. A troca pausa enquanto o mouse estiver sobre o carrossel, houver foco do teclado nele ou a aba estiver oculta. O botão **Pausar/Retomar** permite controlar a rotação.

### Link de destino por banner

No `.txt` de mesmo nome da imagem, mantenha a descrição e acrescente uma linha `Link:` com a URL completa. Exemplo: `carrossel/01.webp` e `carrossel/01.txt`:

```text
Conheça o Musicool, aplicativo Clave Sol.
Link: https://musicool.clavesol.com.br/
```

Ao clicar na imagem, o visitante abre o destino na mesma aba. Use URLs completas com `https://` ou `http://`, inclusive para páginas do próprio site. O texto do `.txt` aparece como legenda sobre a parte inferior da imagem, em uma faixa verde translúcida, e também é acessível a leitores de tela. A linha `Link:` não aparece na legenda. Sem texto, nenhuma faixa é exibida. Sem essa linha (ou com `Link:` vazio), o banner permanece sem link. Os `.txt` antigos, contendo somente descrição, continuam funcionando. O mesmo formato vale para `padrao.txt`.

Inclua a imagem e seu `.txt` no commit e publique o site novamente. Em acervos já criados, é necessário atualizar também `carousel.py`, `assets/carrossel.mjs` e `assets/carrossel.css` com os arquivos de `templates/hinario-site/` do projeto principal; editar apenas o `.txt` não adiciona este recurso à versão antiga do carrossel.
