Title: MuseScore 4: guia rápido para edição de partituras
Description: Consulte os principais comandos para inserir notas, cifras, compassos, fórmulas de compasso, anacruse e organizar sistemas no MuseScore 4.
Category: tutoriais
Image: musescore.webp


O MuseScore 4 oferece muitos recursos de edição, mas vários deles ficam espalhados entre atalhos, paletas, propriedades e menus. Enquanto você ainda está se acostumando com o programa, é útil ter uma referência rápida para as tarefas mais comuns.

Este guia reúne procedimentos práticos para continuar escrevendo uma partitura, inserir cifras, mudar a fórmula de compasso, criar anacruse, usar notas pontuadas e organizar a quantidade de compassos em cada sistema.

> **Observação:** neste tutorial, “sistema” significa o conjunto de pentagramas que aparece em uma mesma linha da página. Em uma partitura com Flauta, Sax Alto e Clarinete, por exemplo, os três pentagramas juntos formam um sistema.

## Referência rápida

| Ação | Como fazer | Efeito |
|---|---|---|
| Inserir uma mínima pontuada | `N` → `6` → `.` → inserir a nota | Cria uma nota com duração de 3 tempos em compasso cuja semínima vale 1 tempo |
| Inserir cifra | Selecione a nota ou pausa e pressione `Ctrl + K` | Insere símbolos como `C`, `Am`, `G7`, `F#m7` |
| Avançar para a próxima cifra | Pressione `Espaço` durante a edição da cifra | Move o cursor para a próxima posição |
| Voltar para a cifra anterior | `Shift + Espaço` | Retorna à posição anterior de cifra |
| Adicionar um compasso ao final | `Ctrl + B` | Acrescenta um novo compasso no fim da partitura |
| Adicionar vários compassos | **Adicionar → Compassos → Adicionar compassos…** | Acrescenta vários compassos de uma vez |
| Mudar a fórmula de compasso | Aplique uma fórmula da paleta ao compasso desejado | Altera a métrica a partir daquele ponto |
| Inserir uma anacruse | Ajuste a duração real do primeiro compasso | Cria um primeiro compasso incompleto |
| Enviar um compasso para o sistema seguinte | Selecione o compasso e use `Alt + ↓` | Redistribui visualmente os compassos |
| Trazer um compasso para o sistema anterior | Selecione o compasso e use `Alt + ↑` | Redistribui visualmente os compassos |
| Inserir quebra de sistema | Selecione o compasso e pressione `Enter` | Faz o sistema terminar naquele ponto |
| Remover compassos vazios no final | Use a opção correspondente em **Ferramentas** | Elimina compassos excedentes após o fim da música |
| Inserir ponto de aumento simples | Selecione a nota e pressione `.` | Ativa ou remove um ponto de aumento |
| Inserir ponto de aumento duplo | Habilite o botão de ponto duplo na barra de entrada de notas | Cria uma nota com dois pontos de aumento |
| Mover uma pausa verticalmente | Selecione a pausa e use `↑` ou `↓` | Muda apenas sua posição gráfica |
| Alterar o tempo da música | Use uma marca de tempo da paleta | Define o andamento da reprodução |

---

## 1. Inserindo notas pontuadas

### Mínima pontuada

Uma mínima normalmente vale dois tempos quando a semínima é a unidade de tempo. Com um ponto de aumento, ela passa a valer três.

Para inserir uma mínima pontuada:

1. Pressione `N` para entrar no modo de inserção de notas.
2. Pressione `6` para escolher a mínima.
3. Pressione `.` para adicionar o ponto.
4. Insira a altura da nota.

O resultado será uma **mínima pontuada**, útil para representar três tempos sem precisar escrever uma mínima ligada a uma semínima.

### Dois pontos de aumento

O ponto simples funciona como uma opção liga/desliga. Portanto, pressionar `.` novamente **não cria um segundo ponto**: ele remove o primeiro.

Para usar dois pontos de aumento:

1. Localize a barra de entrada de notas.
2. Abra a configuração da barra pelo ícone de engrenagem.
3. Habilite o comando de **ponto de aumento duplo**.
4. Selecione a nota.
5. Clique no botão correspondente ao ponto duplo.

Uma semínima duplamente pontuada, por exemplo, vale:

- semínima: 1 tempo;
- primeiro ponto: + 1/2 tempo;
- segundo ponto: + 1/4 de tempo;
- total: **1 3/4 de tempo**.

---

## 2. Inserindo cifras

Para inserir cifras de acordes:

1. Selecione a nota ou pausa onde a cifra deve começar.
2. Pressione `Ctrl + K`.
3. Digite a cifra, por exemplo:

```text
C
Am
G7
F#m7
Bb
```

4. Pressione `Espaço` para avançar para a próxima posição.
5. Use `Shift + Espaço` para voltar.

As cifras ficam vinculadas à posição rítmica da partitura, por isso é melhor inseri-las sobre a nota ou pausa correspondente.

---

## 3. Adicionando compassos ao final da música

Se você chegou ao fim da partitura e precisa continuar escrevendo, pressione:

```text
Ctrl + B
```

Cada acionamento acrescenta um novo compasso ao final.

Para adicionar vários de uma vez, use:

**Adicionar → Compassos → Adicionar compassos…**

e informe a quantidade desejada.

---

## 4. Mudando a fórmula de compasso no meio da partitura

Uma mesma música pode mudar de métrica. É possível, por exemplo, começar em `4/2` e depois passar para `4/4`.

Para fazer isso:

1. Clique no primeiro compasso que deverá usar a nova fórmula.
2. Abra **Paletas → Fórmulas de compasso**.
3. Escolha, por exemplo, `4/4`.
4. Dê duplo clique na fórmula ou arraste-a para o compasso.

A fórmula anterior continua valendo nos compassos anteriores. A nova métrica passa a valer a partir do ponto onde foi inserida.

Se a música voltar depois para a fórmula anterior, basta aplicar novamente a fórmula desejada no compasso correspondente.

---

## 5. Criando um primeiro compasso anacrústico

Uma **anacruse** é um compasso inicial incompleto. A música começa antes do primeiro tempo forte, usando apenas parte da duração nominal do compasso.

Exemplo: a música está em `4/4`, mas antes do primeiro compasso completo existe apenas uma semínima.

Nesse caso, o primeiro compasso deve ter duração real de `1/4`, embora a fórmula nominal continue sendo `4/4`.

### Como configurar

1. Clique com o botão direito no primeiro compasso.
2. Abra **Propriedades do compasso**.
3. Mantenha a duração **nominal** correspondente à fórmula da música.
4. Ajuste a duração **real** para a duração da anacruse.

Exemplos:

| Fórmula da música | Duração da anacruse | Duração real do primeiro compasso |
|---|---:|---:|
| 4/4 | 1 semínima | 1/4 |
| 4/4 | 2 semínimas | 2/4 |
| 3/4 | 1 semínima | 1/4 |
| 6/8 | 1 colcheia | 1/8 |
| 6/8 | 3 colcheias | 3/8 |

Assim, o MuseScore passa a tratar corretamente o primeiro compasso como incompleto.

---

## 6. Quantidade de compassos por sistema

Não existe obrigação de usar sempre a mesma quantidade de compassos em cada linha.

Uma música em compasso binário e com escrita pouco densa pode acomodar seis compassos em um sistema, enquanto outra, com notas mais carregadas, pode ficar melhor com quatro.

O objetivo é obter:

- boa legibilidade;
- espaçamento confortável;
- distribuição equilibrada entre as linhas;
- poucas sobras no final da página.

### Inserindo quebras automaticamente

Para organizar a partitura em uma quantidade aproximada de compassos por sistema, use o comando de **adicionar/remover quebras de sistema** no menu de formatação.

Se quiser seis compassos em cada linha, configure uma quebra a cada seis compassos.

### Ajustando manualmente

Para terminar um sistema em um ponto específico:

1. Selecione o compasso onde a linha deve terminar.
2. Pressione `Enter`.

Isso cria uma **quebra de sistema**.

---

## 7. Redistribuindo compassos entre sistemas

Às vezes a música termina deixando apenas um ou dois compassos isolados no último sistema. Não é necessário manter uma distribuição perfeitamente uniforme.

Você pode reorganizar visualmente os compassos.

### Trazer um compasso para o sistema anterior

Selecione o compasso e pressione:

```text
Alt + ↑
```

### Enviar um compasso para o sistema seguinte

Selecione o compasso e pressione:

```text
Alt + ↓
```

Esse recurso é muito útil para evitar um último sistema com apenas um ou dois compassos.

Antes de forçar muitos compassos numa mesma linha, observe se a leitura continua confortável.

---

## 8. Removendo compassos excedentes no fim

Se sobraram sistemas completamente vazios depois do fim da música, não exclua os instrumentos.

Flauta, Sax Alto e Clarinete, por exemplo, devem continuar existindo na partitura. O que precisa ser removido são os **compassos vazios excedentes**.

Use a função de remover compassos vazios no final da partitura disponível no menu **Ferramentas**.

Também é possível selecionar os compassos excedentes e removê-los como estrutura, em vez de simplesmente apagar seu conteúdo.

Apagar apenas as notas ou pausas não reduz o tamanho da partitura: os compassos continuam existindo.

---

## 9. Pausas e silêncios

Uma pausa não pode ser simplesmente arrastada horizontalmente para outro ponto do compasso como se fosse um objeto gráfico.

Sua posição horizontal representa um momento rítmico real.

Se existe:

```text
nota — pausa — nota
```

e a pausa precisa acontecer em outro momento, é necessário ajustar as durações das notas e pausas ao redor dela.

### Mover apenas a aparência da pausa

Se o objetivo é apenas afastá-la verticalmente de outro elemento:

1. Selecione a pausa.
2. Use `↑` ou `↓`.

Isso altera apenas sua posição gráfica, sem mudar o ritmo.

---

## 10. Alterando o andamento

Para definir a velocidade da música:

1. Selecione a nota ou compasso onde o novo andamento começa.
2. Abra **Paletas → Tempo**.
3. Insira uma marca de metrônomo.
4. Edite o valor de BPM.

Exemplo:

```text
♩ = 80
```

A mudança passa a valer a partir daquele ponto.

Uma partitura também pode ter várias mudanças de andamento ao longo da música.

---

## 11. Uma dica importante sobre pentagramas, sistemas e compassos

Esses três termos costumam causar confusão no início:

- **Pentagrama:** conjunto de cinco linhas de um instrumento ou voz.
- **Compasso:** trecho delimitado por barras de compasso.
- **Sistema:** conjunto de todos os pentagramas exibidos juntos em uma linha da página.

Em uma partitura para Flauta, Sax Alto e Clarinete, uma linha contendo os três instrumentos é **um sistema com três pentagramas**.

Por isso, ao tentar “colocar mais compassos no pentagrama”, normalmente o que você realmente quer é **aumentar a quantidade de compassos por sistema**.

---

## 12. Resumo de atalhos úteis

| Atalho | Função |
|---|---|
| `N` | Entrar ou sair do modo de inserção de notas |
| `6` | Selecionar mínima durante a entrada de notas |
| `.` | Ativar ou remover ponto de aumento simples |
| `Ctrl + K` | Inserir cifra |
| `Ctrl + B` | Adicionar compasso ao final |
| `Enter` | Inserir quebra de sistema no ponto selecionado |
| `Alt + ↑` | Mover compasso para o sistema anterior |
| `Alt + ↓` | Mover compasso para o sistema seguinte |
| `↑` / `↓` | Ajustar verticalmente elementos selecionados, como pausas |

---

## Conclusão

No MuseScore, boa parte do trabalho de edição envolve distinguir três coisas:

1. **o conteúdo musical**, como notas, pausas, cifras e fórmulas de compasso;
2. **a duração estrutural**, como anacruses e quantidade de compassos;
3. **a apresentação gráfica**, como quebras de sistema e distribuição dos compassos na página.

Quando essa distinção fica clara, tarefas como criar anacruse, mudar de `4/2` para `4/4`, inserir compassos ou reorganizar o final de um hino tornam-se bem mais simples.

Este guia pode servir como referência rápida durante a edição de novas partituras até que os principais comandos se tornem naturais.
