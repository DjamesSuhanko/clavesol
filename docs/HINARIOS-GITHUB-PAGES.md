# Hinários no GitHub Pages

Os repositórios `DjamesSuhanko/clavesol-hinos-bb`, `DjamesSuhanko/clavesol-hinos-eb` e `DjamesSuhanko/clavesol-hinos-do` contêm 241 partituras aferidas cada um. As pastas locais ficam ao lado deste projeto, em `~/Documents/ClaveSol/site/`. Cada um mantém a aparência, player, cursor, SEO e atualização de cache do blog.

## Exemplo: ativar Bb

1. Abra https://github.com/DjamesSuhanko/clavesol-hinos-bb/settings/pages.
2. Em **Build and deployment**, selecione **GitHub Actions** em **Source**. Não crie outro workflow: o repositório já contém o arquivo necessário.
3. Deixe **Custom domain** vazio.
4. Abra a aba **Actions**, selecione **Publicar hinário** e clique em **Run workflow**. Selecione a branch `main` e confirme **Run workflow**.
5. Aguarde o resultado verde. O endereço será https://djamessuhanko.github.io/clavesol-hinos-bb/.
6. Abra um hino e teste Reproduzir.

Repita para `clavesol-hinos-eb` e `clavesol-hinos-do`. O primeiro commit tem `[skip ci]` para aguardar a configuração do Pages. Depois da ativação, novos pushes em `main` acionam a publicação automaticamente.

## Ativar a troca no blog

A migração no blog foi preparada em um commit local, sem push, para não interromper o acesso enquanto os Pages novos não estiverem ativos. Depois de confirmar os três sites, publique o commit do blog com `git push origin main`, dentro da pasta `clavesol`.

Os cards Bb, Eb, C e Outros mantêm aparência e ordem. Apenas os links Explorar dos três primeiros apontam diretamente aos novos sites; os títulos e endereços antigos encaminham ao destino correspondente. Outros permanece no blog.

## Armazenamento e manutenção

O blog deixa de publicar os assets transferidos. Seu histórico Git ainda guarda versões antigas; esta operação não reescreve o histórico. Cada novo repositório tem apenas o próprio hinário. Use o script `criar_licao.py` no repositório de destino, conforme seu README. Componentes compartilhados são cópias: melhorias futuras do player e CSS devem ser replicadas nos três projetos.

Referência oficial: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
