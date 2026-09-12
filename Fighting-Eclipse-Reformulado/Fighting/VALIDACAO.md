# Validação da entrega

## Ambiente

- Linux, Python 3.12.14, pygame-ce 2.5.8 / SDL 2.32.10.
- Vídeo e áudio SDL dummy para inicialização automatizada e captura de telas.
- Testes não dependem de imagens, músicas ou efeitos sonoros externos.

## Resultado

**17 testes automatizados passaram.**

Cobertura:

1. Navegação: abertura → seleção → confirmações → luta → pausa/ajuda → vitória → revanche, com renderização das telas.
2. Os quatro personagens em PVE nos três níveis (12 combinações de personagem/dificuldade).
3. Defesa com chip, parry sem dano e agarrão ignorando a guarda.
4. Cancelamento negado quando o golpe não acertou.
5. Ativação e recuperação de todos os oito tipos de golpe de cada personagem.
6. Movimento idêntico em simulações com renderização a 30, 60 e 144 FPS.
7. Uma única ação por pressão mesmo ao receber KEYDOWN repetido.
8. Queda, transição para levantar e recuperação.
9. Exclusão do proprietário e reflexão com troca de dono dos projéteis.
10. Separação de pushboxes e limites da arena.
11. Liberação, exaustão e limpeza de buffer/cooldowns/recursos no reset.
12. Acertos corpo a corpo simultâneos e K.O. duplo.
13. Emissão/expiração de projéteis e armadilhas; duração da barreira.
14. Ausência de dano no startup e ausência de acertos repetidos da mesma ativação.
15. Três sequências de três acertos executadas na simulação com cada personagem: LLL, LLH, LHS1.
16. Empate sem pontuação, repetição do round e vitória ao chegar a dois rounds.
17. Desempate de tempo por porcentagem de vida, não pelo valor absoluto.

Checagem de sintaxe/importação: `python -m compileall -q .`.
Inicialização: `python game.py --smoke 120`, com SDL dummy.
Inspeção visual das capturas de seleção, arena e ajuda; imagens incluídas em `previews/`.

A medição local de 120 ciclos de atualização/renderização sem limitador consumiu aproximadamente 0,55 s (driver dummy, 1280×720). Isso não é uma promessa de desempenho em qualquer computador ou em tela cheia.

## Limites da evidência

Não foi realizada uma sessão humana de jogo em Windows, nem teste com teclado físico de dois jogadores, dispositivo real de áudio ou monitor em tela cheia. O atalho Windows e a receita opcional de PyInstaller são fornecidos, mas não foram executados neste Linux. A jogabilidade e o balanceamento continuam sujeitos a avaliação humana.

Veja o README para controles, instalação, lista de arquivos e os recursos avançados do briefing que não foram implementados nesta versão.
