# Atualizar o player nos quatro repositórios

A origem é `clavesol`. Faça as alterações nele e rode, dentro dessa pasta:

```bash
.venv/bin/python scripts/sincronizar_player.py
```

O comando sincroniza os três hinários irmãos (`../clavesol-hinos-bb`, `../clavesol-hinos-eb`, `../clavesol-hinos-do`) e valida os quatro projetos com testes do player, build e verificação de links. Use Python 3.12+, com as dependências do blog instaladas, e Node.js. O script procura no PATH e, neste computador, também no runtime instalado pelo Codex. Se necessário, informe `--node /caminho/para/node`.

Para conferir diferenças sem modificar nada:

```bash
.venv/bin/python scripts/sincronizar_player.py --check
```

Para sincronizar, validar, fazer commit e push com um único comando:

```bash
.venv/bin/python scripts/sincronizar_player.py --publicar
```

A publicação exige branch main, nenhum arquivo staged e os origins esperados. Só os arquivos listados em `SHARED` no script (JavaScript do player, módulos, CSS, gerador das páginas musicais e testes compartilhados) são copiados. A documentação e o próprio script também entram no commit do blog. Os pushes enviam todos os commits locais pendentes de main; revise-os antes de usar `--publicar`. Os deploys ficam a cargo dos workflows Actions existentes. Se algum push falhar, os anteriores podem já ter sido enviados; corrija o problema e execute novamente.

Partituras, áudios, imagens, dados dos hinários, build.py e configurações de domínio não são copiados. Alterações locais diferentes nos arquivos de destino interrompem a operação antes de qualquer cópia. Alterações já commitadas nesses arquivos podem ser substituídas pela versão do blog; mantenha o blog como origem das melhorias comuns. Arquivos idênticos são ignorados. A execução padrão não cria commits nem faz push.

## Andamento numérico

No player sintetizado, o campo **Andamento (♩ BPM)** aceita números, inclusive decimais. A unidade é a semínima; por exemplo, se a partitura indica semínima pontuada = 60, o campo inicia em 90 semínimas por minuto. A indicação original permanece ao lado para referência.

O botão **Andamento original** restaura o andamento inicial. Digitar e confirmar o valor com Enter ou sair do campo altera o som e o cursor juntos, preservando a posição da reprodução. Valores vazios, inválidos ou fora da faixa de 0,1 a 4 vezes o andamento original são descartados, mantendo o último valor válido. Mudanças de andamento escritas na partitura continuam proporcionais. Áudio gravado sem referência de BPM mantém o seletor de velocidade existente.

## Fermatas

O player sintetizado prolonga em 50% o intervalo das notas e pausas com fermata. Marcas simultâneas ou sobrepostas entre vozes são combinadas, sem multiplicar o prolongamento. Som, cursor, busca e ajuste de BPM usam o mesmo relógio. É uma interpretação simples para estudo, não uma reprodução dos fatores personalizados do MuseScore. O MusicXML original e o timing exportado permanecem intactos; o build inclui as marcações na sequência e o navegador aplica a duração adicional. O conversor `musicxml_audio.py` e seu teste de fermatas também são sincronizados.
