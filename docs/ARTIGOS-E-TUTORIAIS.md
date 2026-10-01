# Criar artigos e tutoriais no Clave Sol

Artigos e tutoriais são arquivos Markdown (`.md`) dentro de `content/`, na
raiz do projeto. Você escreve o texto, adiciona as imagens se desejar, confere
a prévia e publica pelo Git. Não precisa alterar Python nem usar
`criar_licao.py`: esse script é exclusivo para partituras.

## 1. Escolher o tipo de conteúdo e o nome do arquivo

- Use `Category: artigos` para textos explicativos, análises e apresentações.
- Use `Category: tutoriais` para instruções e procedimentos passo a passo.

Ambos ficam diretamente em `content/`. Não crie uma subpasta `tutoriais/`
ali: o gerador atual só lê os arquivos `content/*.md`.

Exemplos de nomes:

```text
content/06-organizar-o-estudo.md
content/07-praticar-com-o-cursor.md
```

Use minúsculas, números e hífens, sem espaços ou acentos no nome do arquivo.
O título visível pode ter acentos e pontuação normalmente. O prefixo numérico
é opcional; ele ajuda a definir a ordem dos cartões. Use dois ou três dígitos
consistentemente para que a ordem alfabética acompanhe a numérica.

O nome do arquivo define a URL. Mesmo um tutorial tem endereço em `/artigos/`:

| Arquivo | Endereço publicado | Onde aparece |
|---|---|---|
| `06-organizar-o-estudo.md` | `/artigos/06-organizar-o-estudo/` | Artigos |
| `07-praticar-com-o-cursor.md` | `/artigos/07-praticar-com-o-cursor/` | Tutoriais e Artigos |

A página Artigos reúne todos os textos, inclusive os de outras categorias.
A página Tutoriais filtra somente os que têm `Category: tutoriais`.
Os três primeiros arquivos, em ordem alfabética pelo nome, aparecem na página
inicial. A data de publicação não determina essa ordem.

## 2. Criar o Markdown

Abra a raiz do projeto no terminal:

```sh
cd /home/djames/Documents/ClaveSol/site/clavesol
```

No seu editor de texto, crie o arquivo escolhido dentro de `content/` e cole
um dos modelos abaixo. Confira antes se esse nome já existe para não
sobrescrever outro conteúdo.

### Modelo de artigo

Arquivo: `content/06-organizar-o-estudo.md`

```md
Title: Como organizar o estudo musical
Description: Uma rotina simples para combinar leitura, ritmo e prática no instrumento.
Category: artigos
Image: piano.jpg

## Defina o objetivo

Escolha uma passagem e estabeleça o que deseja melhorar: ritmo, afinação
ou continuidade da execução.

## Divida a prática em etapas

- Leia a partitura antes de tocar.
- Comece em um andamento confortável.
- Repita os trechos que precisam de atenção.

## Continue praticando

Encontre material para estudar na [estante de partituras]({{BASE}}/partituras/).
```

### Modelo de tutorial

Arquivo: `content/07-praticar-com-o-cursor.md`

```md
Title: Como praticar com o cursor da partitura
Description: Abra uma lição, ajuste a velocidade e use o modo mudo para solfejar.
Category: tutoriais
Image: piano.jpg

## O que você vai precisar

Uma lição com player e cursor disponíveis na
[estante de partituras]({{BASE}}/partituras/).

## 1. Abra uma lição

Escolha a partitura e localize os controles de reprodução.

## 2. Ajuste a velocidade

Selecione uma velocidade confortável e clique em **Reproduzir**.
Para interromper, clique em **Pausar**.

## 3. Pratique o solfejo

Marque **Mudo para solfejo**. O cursor continua indicando as posições
da partitura enquanto o som permanece silenciado.

## Resultado esperado

Você consegue acompanhar a lição no andamento escolhido e alternar
entre ouvir e solfejar.
```

`piano.jpg` já existe em `assets/`, portanto esses modelos não exigem imagens
novas. Edite os exemplos para escrever seu próprio conteúdo.

## 3. Preencher os campos do cabeçalho

Os campos ficam no começo do arquivo, **sem delimitadores `---`**. Deixe uma
linha em branco entre o último campo e o texto. Use um valor por linha.

| Campo | O que preencher | Comportamento atual |
|---|---|---|
| `Title` | Título completo do texto. | Aparece no cartão, na página e no título da aba. |
| `Description` | Resumo curto, preferencialmente uma ou duas frases. | Aparece no cartão e abaixo do título da página. Não substitui a descrição HTML global do site. |
| `Category` | Uma das categorias da tabela abaixo. | Determina a seção em que o texto aparece. Um valor desconhecido interrompe a geração. |
| `Image` | Caminho relativo a `assets/`, sem barra inicial. | Opcional: imagem do cartão. Sem o campo, aparece a ilustração de clave. |

Preencha sempre `Title`, `Description` e `Category`, mesmo que o gerador não
aponte todos os campos vazios como erro.

Categorias editoriais aceitas:

| Valor de `Category` | Seção |
|---|---|
| `artigos` | Artigos |
| `tutoriais` | Tutoriais |
| `gem` | GEM — Grupo de Ensino Musical |
| `doacoes` | Doações |
| `luthier` | Luthier |
| `links` | Links — Aplicativos musicais |

`msa`, `hinos` e `metodos` são agrupamentos da estante de partituras, não
valores aceitos no campo `Category` de um artigo. Para escrever sobre eles,
escolha uma categoria editorial e inclua um link para a partitura.

O campo `Date` é lido, mas atualmente não é exibido nem usado para ordenar.
Não há exibição automática de `Author`, tags, agendamento ou múltiplas
categorias por texto. Se quiser uma assinatura ou uma data visível, escreva-a
no próprio corpo do artigo.

## 4. Formatar o texto

O título principal já vem de `Title`. Comece as seções com `##` e use `###`
para subseções. Elas alimentam automaticamente o índice lateral **Nesta
leitura**; não precisa escrevê-lo manualmente.

````md
## Uma seção

Texto com **negrito**, *itálico* e `nome de comando`.

### Uma subseção

1. Primeiro passo.
2. Segundo passo.

- Um item.
- Outro item.

> Uma observação sobre o exercício.

| Recurso | Uso |
|---|---|
| Velocidade | Ajustar o andamento de estudo |

```text
Um exemplo ou trecho de comando
```
````

Separe parágrafos e listas por linhas em branco. Use títulos curtos e
informativos para que o índice lateral fique fácil de consultar.

## 5. Adicionar imagens

A imagem do cabeçalho `Image` aparece **no cartão da listagem**. Ela não é
inserida automaticamente no corpo do artigo.

Para uma imagem própria, copie o arquivo para `assets/`. Uma organização
possível é:

```text
assets/artigos/07-praticar-com-o-cursor/
    capa.jpg
    controles.png
```

Nesse caso, use no cabeçalho:

```text
Image: artigos/07-praticar-com-o-cursor/capa.jpg
```

Para mostrar uma captura dentro do texto, escreva:

```md
![Controles de reprodução com a opção Mudo para solfejo]({{BASE}}/assets/artigos/07-praticar-com-o-cursor/controles.png)
```

Esse exemplo exige que o arquivo `controles.png` exista. Para evitar que uma
captura larga ultrapasse a área do texto, também pode usar HTML explícito:

```html
<img src="{{BASE}}/assets/artigos/07-praticar-com-o-cursor/controles.png"
     alt="Controles de reprodução com a opção Mudo para solfejo"
     style="max-width:100%;height:auto" loading="lazy">
```

Prefira imagens com tamanho de arquivo adequado à web e confira a legibilidade
na prévia. As imagens dos cartões são recortadas para preencher o espaço;
evite colocar texto importante perto das bordas da capa. Inclua a descrição
visual em `alt` nas imagens do corpo e os créditos quando cabíveis.

## 6. Inserir links, vídeos e materiais para download

Para páginas e arquivos do próprio site, use `{{BASE}}` no corpo do Markdown.
O gerador substitui esse marcador pelo caminho correto tanto no domínio
próprio quanto em um endereço de projeto do GitHub Pages.

```md
[Partituras]({{BASE}}/partituras/)
[Hinos]({{BASE}}/partituras/hinos/)
[Um tutorial]({{BASE}}/artigos/07-praticar-com-o-cursor/)
```

Só inclua links para páginas que já existam ou que você esteja criando junto.
O link para Hinos, por exemplo, exige que essa categoria tenha sido cadastrada.

Links externos usam a URL completa:

```md
[Site do MuseScore Studio](https://musescore.org/pt-br)
[Tutoriais oficiais](https://musescore.org/en/tutorials)
```

Para um vídeo, faça um link com título descritivo e a URL do vídeo desejado.
O blog não transforma automaticamente links de vídeo em players incorporados.

Para disponibilizar um PDF, coloque-o em `assets/` e faça um link para ele:

```md
[Abrir material de apoio em PDF]({{BASE}}/assets/artigos/07-praticar-com-o-cursor/material.pdf)
```

O exemplo exige a criação do PDF nesse caminho. Não aponte links para arquivos
em `~/Documents`, `file://` ou caminhos absolutos do seu computador: os leitores
não terão acesso a eles. Não coloque `{{BASE}}` no campo `Image`; ali o caminho
já é relativo a `assets/`.

## 7. Trabalhar em rascunho

**Artigos e tutoriais ainda não têm suporte a `Draft: true`.** Esse campo
funciona nas partituras, mas é ignorado pelo gerador de artigos. Todo `.md`
colocado diretamente em `content/` entra no build.

Enquanto escreve, mantenha o arquivo fora de `content/`, por exemplo na sua
pasta pessoal de rascunhos. Quando quiser ver a prévia no site, copie-o para
`content/`, mas só o inclua no commit de publicação quando estiver pronto.

Não use `git add .` para publicar um texto: isso pode incluir outros trabalhos
em andamento. Arquivos de `assets/` são copiados para o site mesmo sem um
artigo apontando para eles; envie apenas materiais que pretende disponibilizar.

## 8. Conferir a prévia local

Na raiz do projeto, ative o ambiente já preparado neste computador:

```sh
cd /home/djames/Documents/ClaveSol/site/clavesol
. .venv/bin/activate
BASE_PATH='' python build.py
python scripts/check_links.py
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Se o ambiente ainda não tiver as dependências, execute
`python -m pip install -r requirements.txt` após ativá-lo.

Abra o endereço que corresponde ao arquivo criado, por exemplo:

```text
http://127.0.0.1:8000/artigos/07-praticar-com-o-cursor/
```

Confira o título, o resumo, as seções, o índice lateral, os links, as imagens
e a categoria de listagem. Reduza a largura da janela para verificar a leitura
em telas menores. O verificador de links ajuda a detectar caminhos locais
inexistentes; não substitui a revisão visual nem a conferência de links externos.

Depois de editar o Markdown, execute `python build.py` e
`python scripts/check_links.py` novamente, em outro terminal com o ambiente
ativado, e recarregue a página. Não há recarga automática ao salvar. Encerre o
servidor com `Ctrl+C` quando terminar. Nunca edite os arquivos de `dist/`:
essa pasta é recriada a cada build.

## 9. Fazer commit e publicar

Confira primeiro suas alterações:

```sh
git status --short
git diff -- content/07-praticar-com-o-cursor.md
```

`git diff` não mostra o conteúdo de arquivos novos ainda não rastreados;
abra esses arquivos no editor para revisá-los.

Adicione apenas o texto que está pronto:

```sh
git add content/07-praticar-com-o-cursor.md
```

Se criou uma pasta com imagens ou PDFs para ele, adicione-a também:

```sh
git add assets/artigos/07-praticar-com-o-cursor/
```

Pule o último comando se estiver usando somente `piano.jpg` ou outros assets
que já estejam no repositório. Revise a área de staging antes do commit para
não incluir alterações alheias a essa publicação:

```sh
git diff --cached --stat
git diff --cached
```

Quando ela contiver somente o que você quer publicar:

```sh
git commit -m "Adiciona tutorial de prática com o cursor"
git push origin main
```

O push publica **todos os commits locais pendentes**, não apenas o último.
A ação **Publicar Clave Sol**, na aba Actions do GitHub, valida e gera o site.
Após sua conclusão, confira o endereço publicado:

```text
https://clavesol.com.br/artigos/07-praticar-com-o-cursor/
```

Se o site mostrar **Atualização disponível**, aceite a atualização. Uma aba
com HTML antigo pode precisar de uma recarga para exibir a nova publicação.

## 10. Atualizar um texto existente

Edite o mesmo `.md`, gere a prévia, confira e publique pelo mesmo processo.
Manter o nome do arquivo preserva a URL. Alterar `Category` muda a seção em
que o texto aparece, mas a página continua em `/artigos/<nome-do-arquivo>/`.

Renomear ou apagar o arquivo muda ou remove a URL. O gerador não cria
redirecionamentos automaticamente: confira antes os links que apontam para
essa página. Para adicionar uma categoria editorial além das seis existentes,
é necessária uma alteração no gerador; escrever um novo valor em `Category`
não cria a categoria.

## 11. Cards em Doações, Luthier e Links

As três categorias usam o mesmo sistema de artigos: cada arquivo `.md` em
`content/` cria um card que abre o texto completo. O nome do arquivo continua
definindo a URL `/artigos/<nome>/`. Esses textos também aparecem no índice
Artigos, junto com os das demais categorias.

- **Doações:** use `Category: doacoes`. Crie um arquivo por modalidade,
  como instrumentos, dinheiro ou materiais. No texto, explique o que é aceito
  e como contribuir. Inclua os contatos ou dados de pagamento que deseja publicar.
- **Luthier:** use `Category: luthier`. Crie um arquivo para cada serviço
  ou instrumento, detalhando atendimento, escopo e contato quando disponíveis.
- **Links:** use `Category: links`. Escreva seus comentários sobre o aplicativo
  e inclua o link externo no corpo. O card leva ao artigo, e o artigo leva ao
  aplicativo. Não existe um campo de cabeçalho especial para o link externo.

Enquanto Doações e Luthier estiverem sem artigos, aparece uma mensagem de
apresentação. Ela desaparece automaticamente quando o primeiro card é publicado.

### Exemplo de Luthier

Salve como `content/luthier-regulagem-violino.md` e substitua as orientações
entre colchetes pelos dados reais antes de publicar:

```md
Title: Regulagem de violino
Description: Conheça o serviço de regulagem e os detalhes do atendimento.
Category: luthier
Image: violin.jpg

## Sobre o serviço

[Descreva o serviço que você oferece e quais instrumentos atende.]

## Atendimento

[Informe a região e o contato para avaliação.]
```

### Exemplo de Doações

Salve como `content/doacoes-instrumentos.md` e preencha os dados reais:

```md
Title: Doação de instrumentos
Description: Saiba como contribuir com instrumentos musicais.
Category: doacoes

## Quais instrumentos são aceitos

[Informe os instrumentos e as condições em que podem ser recebidos.]

## Como combinar a entrega

[Informe o contato e as orientações de entrega.]
```

### Exemplo de Links

Os arquivos `content/links-musescore-studio.md`, `content/links-audacity.md`
e `content/links-friture.md` substituem a antiga lista fixa. Você pode editar
esses textos para acrescentar seus comentários e imagens. Para um novo app:

```md
Title: Nome do aplicativo
Description: Uma frase sobre a finalidade do aplicativo.
Category: links

## Meus comentários

[Escreva sua experiência e as observações que deseja compartilhar.]

## Acessar o aplicativo

[Visitar o site oficial](https://example.com/)
```

Substitua `https://example.com/` pelo endereço real antes de publicar.
O canal Clave Sol Music está no rodapé de todas as páginas; esse link é
definido no template compartilhado em `build.py`.
