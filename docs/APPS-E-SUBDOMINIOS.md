# Apps e sites em subdomínios

A página `/apps/` fica no menu imediatamente depois de GEM. Seus cards apontam diretamente para os sites dos aplicativos e usam a busca das outras listagens. O catálogo é `apps.json`; não é necessário criar um artigo. Os artigos existentes em Links continuam disponíveis.

## Cadastrar um card

Na raiz do repositório ClaveSol:

```bash
python3 criar_app.py \
  --titulo 'Meu App' \
  --texto 'Descrição curta do aplicativo.' \
  --imagem '/caminho/completo/capa.webp' \
  --link 'https://meuapp.clavesol.com.br/'
```

O script aceita WebP, PNG e JPEG. Capas fora de `assets/` são copiadas para `assets/<slug>.<extensão>`; arquivos já dentro de assets são reutilizados. Use preferencialmente uma capa horizontal, com o conteúdo principal centralizado: o card preenche a área da imagem com recorte.

O identificador é derivado do título. Use `--slug meu-app` para definir outro e `--atualizar` para alterar um card existente. Para trocar o título mantendo o mesmo card, informe o slug original. O script não sobrescreve uma imagem diferente: copie a nova capa com outro nome para assets e passe esse caminho. A ordem dos itens em `apps.json` define a ordem dos cards; excluir um item remove o card.

Título e descrição são texto simples, escapados na renderização. Os links devem começar por `https://` ou `http://`. A imagem, o título e o botão abrem o mesmo destino na aba atual.

Valide, revise e faça commit dos arquivos alterados, incluindo a capa:

```bash
.venv/bin/python build.py
.venv/bin/python scripts/check_links.py
```

Nenhum commit ou push é feito pelo script de cards.

## Criar o site e o repositório de um app

`criar_site_app.py` usa o modelo versionado em `templates/app-site/`, com o visual creme, verde e dourado do ClaveSol. Gera página inicial, contato, privacidade, alias `/privacy.html`, 404, sitemap, CNAME e workflow do GitHub Pages. Só `dist/` é publicado. O build do novo site usa somente a biblioteca padrão do Python 3.10 ou mais recente.

Preparação local, sem criar nada no GitHub:

```bash
python3 criar_site_app.py \
  --repositorio DjamesSuhanko/meu-app \
  --diretorio /home/djames/Documents/meu-app \
  --dominio meuapp.clavesol.com.br \
  --titulo 'Meu App' \
  --texto 'Ferramentas musicais para acompanhar sua prática.' \
  --autor 'Djames Suhanko' \
  --email 'djames.suhanko@gmail.com' \
  --imagem '/caminho/completo/logo.webp' \
  --politica-html '/caminho/completo/politica.html'
```

A pasta de destino deve ser nova. `--autor`, `--imagem` e `--politica-html` são opcionais. Sem imagem, usa o logo ClaveSol. Sem política, cria uma página identificada como pendente, sem inventar declarações sobre privacidade. Antes de divulgar essa URL como política definitiva, substitua o conteúdo e marque `privacy_ready: true` em `site.json`.

A política pode ser um fragmento com um único `<h1>` ou um documento HTML com o conteúdo dentro de `<main>`. O texto fornecido é preservado. `--conteudo-html arquivo.html` acrescenta um fragmento à apresentação inicial; use títulos de nível h2 ou inferior nesse trecho. Estes arquivos HTML são conteúdo editorial de confiança, não são sanitizados.

Para criar **também o repositório público**, enviar o commit inicial e configurar Pages, adicione `--github` ao comando de geração. Requer `git`, GitHub CLI (`gh`) autenticado (`gh auth login`) e permissão de criação no dono informado. Uma identidade git já configurada é preservada; se faltar, o autor/email informados são configurados apenas nesse novo repositório.

Se preparou localmente antes, ou se a operação no GitHub falhou, execute o mesmo comando com `--retomar-github` no lugar de `--github`. A retomada usa os arquivos existentes, verifica domínio/repositório e não os recria. Não use essa opção para adotar um repositório remoto diferente. Se houve alterações locais após o primeiro commit, revise e faça commit delas antes de retomar o envio.

O commit inicial contém `[skip ci]`: o primeiro deploy fica para você. Depois da preparação:

1. Na Cloudflare, configure o CNAME do subdomínio para `djamessuhanko.github.io` (ou `<dono>.github.io`), no modo somente DNS.
2. Em GitHub → Settings → Pages, confira o domínio e a origem GitHub Actions, já definidos pelo script.
3. Em Actions → **Publicar aplicativo** → **Run workflow**, publique.
4. Habilite **Enforce HTTPS** em Pages quando o certificado estiver disponível.

O script não altera a Cloudflare, não dispara workflow e não acompanha a publicação. Pushes posteriores em `main` publicam automaticamente.

No novo repositório, edite `site.json` para título, descrição, autor e email; `content/home.html` para apresentação; e `content/privacy.html` para a política. Para mudar o domínio depois, atualize `site.json`, CNAME, Pages e DNS em conjunto.

```bash
cd /home/djames/Documents/meu-app
python3 build.py
python3 -m http.server 8000 --directory dist
```

Abra `http://localhost:8000`. Para disponibilizar esse app no blog, rode também `criar_app.py`: gerar o site não insere automaticamente um card.
