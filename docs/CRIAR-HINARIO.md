# Criar um subdomínio de partituras

O script `criar_hinario.py`, na raiz do ClaveSol, prepara um site independente com a aparência do hinário Bb, busca, partituras e o mesmo player. Acrescenta um carrossel **somente na entrada do acervo**, acima da busca. As páginas individuais do player não recebem carrossel.

## Comando completo

```bash
cd ~/Documents/ClaveSol/SITE/clavesol
.venv/bin/python criar_hinario.py \
  --origem /caminho/das/partituras \
  --destino /home/djames/Documents/ClaveSol/SITE/clavesol-exemplo \
  --arquivos musicxml \
  --dominio exemplo \
  --titulo 'Meu acervo' \
  --descricao 'Partituras para estudar e tocar.' \
  --repositorio DjamesSuhanko/clavesol-exemplo
```

Isso prepara `exemplo.clavesol.com.br`, cria um **repositório público**, envia os arquivos e configura GitHub Pages. Não executa o workflow. Use `--somente-local` para preparar e visualizar sem ações no GitHub. Para enviar depois, repita sem esse parâmetro.

`--destino` pode existir: arquivos alheios são preservados e não são enviados pelo script. Arquivos com nomes conflitantes com o modelo interrompem a preparação antes da cópia. Um repositório Git preexistente não criado por este script é recusado. Origem e destino precisam ser pastas separadas, sem uma conter a outra.

Se omitir `--repositorio`, usa o usuário autenticado no GitHub CLI e o nome da pasta de destino. No modo somente local, o dono padrão é DjamesSuhanko; prefira informar `--repositorio` para outro usuário. O domínio recebe somente o prefixo (`exemplo`), não a URL inteira. `--titulo` e `--descricao` são opcionais.

## Tipos de entrada

- `--arquivos musicxml`: aceita `.musicxml` e `.xml`. Copia o MusicXML original sem reconvertê-lo. O MuseScore ainda é necessário para gerar a representação SVG e as posições do cursor.
- `--arquivos mid`: aceita `.mid` e `.midi`; usa MuseScore para gerar MusicXML, páginas e cursor.
- `--arquivos mscz`: usa MuseScore para gerar MusicXML, páginas e cursor.

Não gera PDF. Não copia nem publica MID, MSCZ ou MSCX. **O único download oferecido é MusicXML**. SVG, sequência JSON e timing fazem parte do player.

O título é extraído do MusicXML (`work-title` ou `movement-title`); na ausência, usa o nome do arquivo. Subpastas da origem são percorridas e integram o identificador, para separar arquivos homônimos em diretórios diferentes. Nomes que resultem no mesmo identificador interrompem a importação. O título e demais metadados podem ser editados em `partituras/hinos/acervo/*.md`.

O processamento usa os mesmos validadores de notas, repetições, fermatas, introdução e sincronização do ClaveSol. MIDI não contém toda a informação editorial de uma partitura: o MuseScore interpreta sua notação. Arquivos incompatíveis são registrados, não são publicados com um player quebrado. A execução continua com os seguintes; no fim, qualquer erro impede envio ao GitHub por padrão. `--ignorar-incompativeis` permite enviar apenas os funcionais. Consulte sempre o resumo.

## Requisitos

- Python 3.12 e as dependências do blog (`.venv` / `requirements.txt`).
- MuseScore instalado; padrão `~/bin/musescore`. Outro executável: `--musescore /caminho/MuseScore`.
- Git e GitHub CLI autenticado (`gh auth login`) para criação remota.
- O autor/email do Git existente é preservado; se faltar, configura localmente `--autor` e `--email` (padrões: Djames Suhanko e djames.suhanko@gmail.com).

## Retomada, atualizações e backup

Repita o mesmo comando para retomar. Importações concluídas com a mesma entrada e os mesmos arquivos de saída são ignoradas. Se a entrada ou a saída mudou, use `--atualizar` para reimportar; a versão anterior é copiada para `.importacao/backups/` antes da substituição. Isso substitui também os metadados da partitura: preserve edições manuais antes de reimportar.

O arquivo `.importacao/resumo.json` lista preparados, ignorados e erros. `.importacao/manifest.json` guarda os hashes de importação. Essa pasta é local e ignorada pelo Git. Para ver mensagens enquanto executa, redirecione para um log:

```bash
.venv/bin/python -u criar_hinario.py ... > /caminho/importacao.log 2>&1
```

O exemplo com `...` é esquemático: substitua pelos parâmetros do comando completo. O script executa em primeiro plano; você pode iniciá-lo com `nohup` se quiser deixá-lo em segundo plano. Ele não acompanha o deploy do GitHub.

Se houver falha no GitHub, arquivos e commits permanecem locais. Repita o comando. Não há force-push, sobrescrita de repositórios remotos alheios ou envio automático de arquivos arbitrários do destino. Commits preparados pelo script incluem `[skip ci]`; o primeiro deploy fica manual. Não altere `.acervo-site.json` (identidade e lista de arquivos gerenciados).

## Carrossel

Coloque as imagens **no destino**, dentro de `carrossel/`:

```text
carrossel/
  01.webp
  01.txt
  02.jpg
  02.txt
  padrao.svg
  padrao.txt
```

Aceita WebP, PNG, JPEG e SVG. O nome, sem extensão, deve conter apenas números: `01`, `02`, `03`, etc. A ordem é **numérica** (2 antes de 10). Não use dois arquivos com o mesmo número. Os `.txt` opcionais contêm a descrição acessível de cada imagem. SVG deve ser uma imagem de sua confiança, sem scripts.

O `padrao.svg` é uma imagem original verde e dourada do ClaveSol. É usada automaticamente quando não existe imagem numerada; não a remova. O fallback não aparece junto com banners personalizados.

**Tamanho sugerido: 1600 × 320 pixels (5:1)**. A área tem entre 120 e 240 pixels de altura, conforme a tela. As imagens ficam inteiras, sem cortar textos; formatos diferentes podem deixar margens laterais. Mantenha pouco texto e fontes grandes para leitura no celular. Não há rotação automática: o visitante usa os botões ou as setas do teclado. Uma única imagem é exibida sem controles.

Imagens e `.txt` devem entrar no commit. Ao adicionar banners depois, faça commit e push no repositório do acervo ou execute novamente o criador. O build lê `carrossel/` a cada execução.

## Prévia local

No destino:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python build.py
python scripts/check_links.py
python -m http.server 8000 --directory dist
```

Abra http://localhost:8000. O título e a descrição ficam em `partituras/hinos/acervo/_index.md`. Não edite `dist/`: ela é recriada. O domínio está em `CNAME` e `seo.json`.

## Publicar no Pages

1. Na Cloudflare, crie o CNAME do subdomínio apontando para `djamessuhanko.github.io` (ou o dono informado), em modo **somente DNS**.
2. No repositório, confira **Settings → Pages**: origem GitHub Actions e domínio personalizado, já configurados pelo script.
3. Abra **Actions → Publicar acervo → Run workflow**.
4. Quando o certificado estiver disponível, habilite **Enforce HTTPS**.

Não é necessário MuseScore no workflow: a preparação é local e o GitHub gera o site a partir do MusicXML, SVGs e cursor já validados. O script não altera a Cloudflare e não cria card no blog principal. Os hinários Bb, Eb e Dó existentes permanecem intactos.


## Origem organizada por compositor

A organização é automática. Passe a pasta que contém os diretórios dos autores:

```text
classico-mudar/
  Bach/
    musica.musicxml
  Beethoven/
    musica.musicxml
  Chopin/
    Noturnos/
      noturno.musicxml
```

A entrada terá cards **Bach**, **Beethoven**, **Chopin**, com a quantidade de partituras e busca por compositor. Ao abrir um card, aparece a lista das músicas daquele compositor com sua própria busca. Subpastas adicionais, como `Chopin/Noturnos`, continuam dentro de Chopin. O nome da primeira pasta é usado na navegação; se o MusicXML não tiver autor preenchido, ele também preenche `Author` no cadastro. Um autor informado na partitura é preservado.

Espaços no começo/fim dos nomes são removidos apenas na apresentação e na geração dos identificadores; as pastas de origem não são renomeadas. Músicas com o mesmo nome em compositores diferentes permanecem separadas. Pastas diferentes que gerem o mesmo identificador são recusadas quando seus nomes de apresentação forem diferentes.

Arquivos soltos na raiz aparecem em **Outras partituras** quando também há compositores. Se só houver arquivos soltos, permanece a lista única tradicional. O carrossel aparece apenas na entrada principal, nunca nas páginas de compositor ou player.

```bash
.venv/bin/python criar_hinario.py \
  --origem /home/djames/Documents/ClaveSol/SITE/classico-mudar \
  --destino /home/djames/Documents/ClaveSol/SITE/clavesol-classicos \
  --arquivos musicxml \
  --dominio classicos \
  --titulo 'Música clássica' \
  --repositorio DjamesSuhanko/clavesol-classicos
```

Troque `musicxml` por `mid` ou `mscz` conforme os arquivos. Pode acrescentar `--somente-local` para conferir primeiro.

O agrupamento fica em `compositores.json`; as URLs dos players e os arquivos importados permanecem nos mesmos locais. Ao repetir o comando num destino criado pela versão anterior do script, o build é atualizado com backup e os compositores são cadastrados sem reconverter importações intactas. Se `build.py` tiver alterações manuais, a atualização é interrompida para preservá-las. O resumo conta essas músicas como ignoradas na conversão, embora a navegação e eventuais autores vazios sejam atualizados.
