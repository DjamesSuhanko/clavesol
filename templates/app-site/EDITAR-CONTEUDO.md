# Editar o conteúdo do site

Edite os arquivos da pasta `content/`:

- `apresentacao.md`: texto descritivo livre sobre o aplicativo.
- `index.md`: nome, frase curta, capa e blocos de privacidade e contato existentes.
- `privacy.md`: política de privacidade.
- `contact.md`: contato.

Não edite `dist/`: ela é recriada pelo build. Os templates HTML cuidam somente da apresentação visual.

## Onde escrever sobre o aplicativo

Abra **`content/apresentacao.md`**. Escreva apenas Markdown, sem cabeçalho de configuração:

```markdown
## Conheça o aplicativo

Aqui você escreve a apresentação, com quantos parágrafos precisar.

### Recursos

- Primeiro recurso.
- Segundo recurso.

![Tela do aplicativo]({{BASE}}/assets/minha-imagem.webp)
```

O texto aparece em uma região própria **abaixo do topo com o nome, a capa e os botões**, e **acima de “Seus dados no aplicativo” e “Fale com o desenvolvedor”**. Títulos e parágrafos permanecem juntos como um artigo; não viram cards. O restante da página permanece intacto. Se o arquivo estiver vazio ou contiver somente comentários, essa região não aparece.

## Configuração do topo

`content/index.md` mantém `Title`, `Description` e `Image`. `Description` é apenas a frase curta abaixo do nome do app. O corpo desse arquivo mantém os blocos de privacidade e contato; não precisa ser alterado para escrever a apresentação.

## Formatação e imagens

Use `**negrito**`, `*itálico*`, listas, links e tabelas Markdown. Guarde imagens em `assets/` e insira:

```markdown
![Descrição da imagem]({{BASE}}/assets/minha-imagem.webp)
```

Use `{{BASE}}/contato/` e `{{BASE}}/privacidade/` para links internos. O gerador ajusta a base do endereço. Na política e no contato, mantenha exatamente um título `#`; subseções usam `##`.

## Conferir e publicar

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python build.py
python -m http.server 8000 --directory dist
```

Abra http://localhost:8000. Se houver `scripts/check_site.py`, execute `python scripts/check_site.py` para verificar os links locais. Depois de revisar, faça commit e push; o workflow instala Markdown e publica normalmente. A URL `/privacidade/` e o alias `/privacy.html` continuam iguais.
