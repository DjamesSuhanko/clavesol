# Adicionar o carrossel a um site existente

O script `adicionar_carrossel.py`, na raiz do projeto ClaveSol, instala o carrossel nos sites existentes que usam o gerador Python ClaveSol. Não cria repositório, não converte partituras e não publica. Preserva o player e o conteúdo do site.

## Instalar

Execute a partir do projeto principal:

```bash
cd /home/djames/Documents/ClaveSol/SITE/clavesol
python3 adicionar_carrossel.py --destino /home/djames/Documents/ClaveSol/SITE/clavesol-cantor-cristao
```

Para outro site, substitua somente o caminho de `--destino`. Pode usar caminhos absolutos ou relativos; coloque entre aspas caminhos com espaços.

O destino deve existir e possuir `build.py` no padrão ClaveSol, com `ROOT`, `OUT`, `BASE` e chamada a `finish_seo` ou `finish_build` no nível principal. O script não é um instalador para qualquer framework: sites com outro gerador precisam de adaptação. Se detectar estrutura incompatível ou arquivos conflitantes, para sem sobrescrevê-los.

## O que é instalado

- `carousel.py`: leitura das imagens e dos textos.
- `carousel_install.py`: inclusão do banner na página inicial gerada.
- `assets/carrossel.css` e `assets/carrossel.mjs`: aparência e navegação.
- `carrossel/padrao.svg` e `carrossel/padrao.txt`: banner usado quando não há imagens numeradas.
- Uma chamada em `build.py`, antes de SEO e cache, para inserir o carrossel e copiar seus arquivos para `dist`.

O banner entra antes da busca da página inicial. Em páginas sem busca, entra no início de `<main>`. Cópias idênticas da entrada, como a página da coleção de um hinário, recebem o mesmo banner. As páginas individuais das músicas e do player permanecem sem carrossel.

Quando existe `.acervo-site.json`, os novos arquivos também são registrados na lista de arquivos gerenciados. As imagens e os `.txt` existentes são preservados. O script guarda uma cópia do `build.py` anterior (e do manifesto, quando houver) em `~/.local/state/clavesol/carrossel/`; o caminho exato aparece ao executar.

Executar novamente após uma instalação feita por este script não duplica o carrossel nem altera arquivos. Se o site já tiver outra integração de carrossel, o script avisa e não modifica nada. Ele instala o recurso; não é um atualizador de instalações existentes.

## Imagens, texto e link

No site de destino, coloque os banners dentro de `carrossel/`:

```text
carrossel/
  01-CantusCaeli.webp
  01-CantusCaeli.txt
  02-Musicool.webp
  02-Musicool.txt
  padrao.svg
  padrao.txt
```

Use imagens de **1600 × 320 pixels**, proporção **5:1**. O site adapta a altura à largura disponível, sem cortar nem deformar a imagem. Outras proporções podem deixar margens. São aceitos WebP, PNG, JPG/JPEG e SVG confiável.

O nome começa com um número, seguido opcionalmente de hífen, espaço ou sublinhado e uma descrição. A ordem é numérica: `02` vem antes de `10`. Não repita o mesmo número em duas imagens. O `.txt` deve ter o mesmo nome-base da imagem.

Exemplo de `01-CantusCaeli.txt`:

```text
Cantus Caeli — conheça o aplicativo.
Link: https://cantuscaeli.clavesol.com.br/
```

O texto aparece sobre a parte inferior da imagem, em uma faixa verde translúcida com letras brancas. A linha `Link:` não é exibida; torna o banner clicável e abre o destino na mesma aba. Use uma URL completa `https://` ou `http://`.

O `.txt` é opcional. Sem ele, não há legenda nem link. Um `.txt` apenas com texto gera legenda sem link; somente `Link:` gera um banner clicável sem legenda. Sem imagens numeradas, aparece `padrao.svg`, usando `padrao.txt` se disponível.

Com duas ou mais imagens, a troca é automática a cada **5 segundos**, com setas e botão **Pausar/Retomar**. A rotação pausa enquanto o mouse está sobre o banner, o foco do teclado está nele ou a aba está oculta. Uma única imagem não apresenta controles.

## Conferir e publicar — exemplo Cantor Cristão

Depois de instalar e adicionar seus banners, gere o site usando o ambiente Python já utilizado pelo projeto:

```bash
cd /home/djames/Documents/ClaveSol/SITE/clavesol-cantor-cristao
BASE_PATH='' /home/djames/Documents/ClaveSol/SITE/clavesol/.venv/bin/python build.py
```

`BASE_PATH=''` é apropriado para o domínio próprio. Para publicação sob um caminho de repositório, mantenha a configuração do workflow existente.

Revise `git status`, inclua os arquivos novos e alterados em um commit e faça push. Inclua `build.py`, os dois módulos Python, os dois arquivos em `assets`, a pasta `carrossel/` e `.acervo-site.json` caso ele tenha sido alterado. Não é necessário versionar `dist`: o workflow existente faz o build. A instalação não executa commit, push ou workflow automaticamente.

Apenas copiar imagens para o servidor não basta: o build precisa rodar novamente para atualizar a lista de banners, as legendas e os links.
