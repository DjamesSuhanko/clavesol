# Introdução no player

Os botões “Hino completo” e “Introdução *” selecionam o trecho; use “Reproduzir” para começar. Trocar o trecho pausa e volta ao início. Sem asterisco identificado, a opção Introdução toca o arquivo completo e informa isso na tela.

O build lê o asterisco (* ou ∗) em direções e símbolos de harmonia do MusicXML e grava `introEnd` em `sequence.json`. O limite inclui a duração da nota marcada, suas ligaduras e o prolongamento de fermatas usado pelo player. É usada a primeira ocorrência na sequência executada, mesmo com ritornelos; o andamento escolhido pelo usuário afeta a velocidade, mantendo o ponto musical final.

Nos hinários Bb, C e Eb, o hino 6 tem introdução até 16 segundos no andamento original, dentro de uma execução completa de 176 segundos. O recurso é do player sintetizado online e não modifica o CantusCaeli.

Validação: `python tests/introduction.test.py`, `node tests/music-player.test.mjs` e `node tests/music-synth.test.mjs`.
