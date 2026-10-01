# SEO e miniaturas de compartilhamento

SEO não depende de um único arquivo entregue ao buscador. O site agora usa
`seo.json` como configuração; `seo.py` transforma essa configuração e os dados
dos artigos em metadados no HTML de cada página, durante `python build.py`.
Tudo está disponível sem executar JavaScript.

## O que o build gera

- Descrição própria para artigos, categorias e partituras.
- Open Graph: título, descrição, imagem, tipo, idioma e URL da página.
- Twitter Cards com imagem grande.
- URL canônica absoluta, sem os parâmetros de cache ou navegação.
- Dados estruturados JSON-LD: WebSite, WebPage ou BlogPosting, conforme a página.
- `dist/sitemap.xml` com páginas públicas e URLs canônicas únicas.
- `dist/robots.txt` com o endereço do sitemap e acesso permitido aos robôs.
- `noindex` na página de erro 404, que também não entra no sitemap.

As rotas antigas de partituras em `/musica/` continuam funcionando, mas seus
metadados apontam para a página correspondente em `/partituras/`.
Não são inventadas datas de publicação, avaliações ou autoria dos artigos.
Os metadados ajudam os serviços a entender o conteúdo; não garantem posição
nos resultados ou uma apresentação específica em todos os aplicativos.

## Configuração do site

Edite `seo.json`:

| Campo | Uso |
|---|---|
| `site_url` | Origem pública, por exemplo `https://clavesol.com.br`, sem subpasta. |
| `site_name` | Nome do site. |
| `description` | Descrição usada quando a página não possui um resumo próprio. |
| `default_image` | Caminho relativo a `assets/`; atualmente `clarinet.jpg`. |
| `default_image_alt` | Descrição visual da imagem padrão. |
| `social_profiles` | Perfis oficiais associados ao site nos dados estruturados da página inicial. |

A variável `SITE_URL` pode substituir `site_url`. O caminho de publicação
continua vindo de `BASE_PATH`. Exemplo para um endereço de projeto:

```sh
SITE_URL='https://usuario.github.io' BASE_PATH='/clavesol' python build.py
BASE_PATH='/clavesol' python scripts/check_links.py
```

Não inclua `/clavesol` em `SITE_URL` e `BASE_PATH` ao mesmo tempo.
A publicação atual usa o domínio de `seo.json` e o `BASE_PATH` da ação do
GitHub Pages. Se o domínio mudar, atualize a configuração antes de publicar.
Em hospedagem sob uma subpasta, o `robots.txt` precisa estar na raiz do domínio
para orientar robôs; o arquivo gerado dentro da subpasta não controla essa raiz.
Nesse caso, o sitemap pode ser enviado diretamente ao Search Console.

## Imagem de cada artigo

A ordem de escolha é:

1. `SocialImage`, quando preenchido.
2. `Image`, a mesma capa usada no card.
3. `default_image`, definida em `seo.json`.

Exemplo de cabeçalho:

```text
Title: Meu artigo
Description: Um resumo específico do que o leitor encontrará nesta página.
Category: artigos
Image: piano.jpg
SocialImage: clarinet.jpg
SocialImageAlt: Detalhe das chaves de um clarinete
```

`SocialImage` é opcional e não altera a capa do card. Todos os caminhos de
imagem são relativos a `assets/`, sem barra inicial ou `{{BASE}}`. O build
interrompe a geração se a imagem indicada não existir ou usar um formato não
aceito: JPG, PNG, WebP ou GIF. Prefira JPG ou PNG para maior compatibilidade
entre serviços. Uma composição horizontal de 1200 × 630 pixels é uma boa
opção editorial para capas dedicadas ao compartilhamento; não é uma exigência
do gerador. Evite detalhes ou texto importante perto das bordas.

Uma imagem no corpo do artigo não vira miniatura automaticamente. Isso evita,
por exemplo, escolher um QR Code Pix como capa sem você ter pedido.

As URLs de imagem incluem um hash do arquivo. Quando a imagem muda, sua URL
de cache muda, sem precisar renomear o arquivo.

## Publicar e conferir

```sh
. .venv/bin/activate
python tests/seo.test.py
python build.py
python scripts/check_links.py
```

Faça commit dos arquivos de origem e push como de costume. Não envie `dist/`:
a ação do GitHub reconstrói o site. Os aplicativos precisam acessar a página
e a imagem publicadas; eles não enxergam a prévia em localhost.

Depois que a publicação terminar:

1. Confira o código-fonte da URL pública: procure `og:image`, `og:title`,
   `og:description` e `canonical`.
2. Abra a URL indicada por `og:image` e confirme que ela mostra a imagem.
3. Faça um novo compartilhamento para conferir a prévia no aplicativo desejado.
4. No Facebook, utilize o [Sharing Debugger](https://developers.facebook.com/tools/debug/)
   para inspecionar a leitura da página publicada.
5. No [Google Search Console](https://search.google.com/search-console), envie
   o endereço `https://clavesol.com.br/sitemap.xml`, se ainda não estiver cadastrado.

Uma prévia antiga pode continuar no cache do serviço que recebeu o link.
O botão “Atualização disponível” do blog atualiza a navegação no site; não
controla o cache das redes sociais. Não há garantia de atualização imediata
de mensagens ou publicações que já foram enviadas.

## Referências

- [Protocolo Open Graph](https://ogp.me/).
- [Sitemaps no Google Search Central](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
