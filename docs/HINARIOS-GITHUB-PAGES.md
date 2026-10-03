# Hinários no GitHub Pages

Cada hinário tem seu próprio repositório e mantém aparência, player, cursor, SEO e cache do Clave Sol:

| Hinário | Repositório | Endereço publicado |
| --- | --- | --- |
| Bb | `DjamesSuhanko/clavesol-hinos-bb` | https://bb.clavesol.com.br/ |
| C | `DjamesSuhanko/clavesol-hinos-do` | https://c.clavesol.com.br/ |
| Eb | `DjamesSuhanko/clavesol-hinos-eb` | https://eb.clavesol.com.br/ |

As pastas locais ficam em `~/Documents/ClaveSol/site/`, ao lado de `clavesol`.

## Publicação

Os três Pages estão configurados com **Source: GitHub Actions**, domínio personalizado e HTTPS. Um push na branch `main` executa o workflow **Publicar hinário**. Também é possível iniciá-lo pela aba Actions → Publicar hinário → Run workflow → main.

Os cards do blog continuam em Partituras → Hinos. O arquivo `external_hymns.json` guarda os endereços e os slugs de cada coleção para as contagens e os redirecionamentos dos links antigos. Outros permanece dentro do blog.

## Manutenção

Use `criar_licao.py` dentro do repositório do hinário para adicionar uma partitura. Para distribuir melhorias comuns do player e do importador, consulte `docs/SINCRONIZAR-PLAYER.md`. O script não copia partituras de um hinário para outro.

O blog não publica os assets desses três hinários. Seu histórico Git ainda guarda versões antigas; a separação não reescreveu esse histórico.

Referência oficial: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
