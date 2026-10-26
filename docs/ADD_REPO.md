cd ~/Documents/PROJETO

**(criar o .gitignore. ex:**

**dist/**
**.venv/**
__pycache__/

**)**

git init -b main
git add .
git commit -m "Versão inicial do PROJETO"



cd ~/Documents/PROJETO

**Apenas se ainda não estiver autenticado:**

gh auth login

**Cria o repositório, configura origin e envia o commit:**

gh repo create Mose --private --source=. --remote=origin --push



Enviar alterações:

git add .
git commit -m "Descrição das alterações"
git push



**Autenticação HTTPS. Vai solicitar autenticação no browser. PEGAR O CÓDIGO GERADO NO CONSOLE E COLAR NO BROWSER. Invés do QR Code, usar app authenticator na última etapa** .

