# Fighting — Eclipse: Spirit Clash

Reformulação do projeto Python/Pygame enviado: um jogo de luta 2D local com quatro personagens originais, atmosfera espiritual noturna, combate com frames ativos, PVP/PVE e partidas até duas vitórias.

## Começar no Windows

Requisitos: Python 3.10 ou superior, teclado e uma tela. Validado com Python 3.12.14 e pygame-ce 2.5.8. Sem dependência de imagens, músicas, internet durante o jogo ou placa gráfica dedicada.

1. Extraia o ZIP inteiro.
2. Abra a pasta `Fighting`.
3. Execute `INSTALAR.cmd` uma vez (precisa de internet para baixar a dependência).
4. Execute `JOGAR.cmd`.

Ou, no terminal dentro dessa pasta:

```powershell
py -3 -m pip install -r requirements.txt
py -3 game.py
```

Linux/macOS:

```bash
python3 -m pip install -r requirements.txt
python3 game.py
```

Use um ambiente virtual se o sistema impedir instalação global. O pacote usa **pygame-ce**, que fornece o módulo `pygame`. Não é necessário instalar também o pacote `pygame` clássico.

**Este pacote contém código executável pelo Python e atalhos `.cmd`, não um `.exe` Windows pré-compilado.** O ambiente de validação é Linux. O script opcional `GERAR_EXE.cmd` pode gerar uma distribuição Windows na sua máquina com PyInstaller; esse empacotamento não foi validado aqui.

## Seleção e fluxo

- Enter na abertura.
- Tab alterna PVE/PVP. F2 alterna Fácil/Normal/Difícil.
- P1: A/D escolhem; F confirma. P2: setas esquerda/direita escolhem; J confirma.
- No PVE, você também escolhe e confirma o personagem da CPU.
- Enter inicia após as duas confirmações.
- Primeiro a conquistar dois rounds vence. Cada round tem 99 segundos.
- No fim do tempo, vence a maior **porcentagem** de vida restante. Empate ou K.O. duplo repete o round sem pontuar.
- Enter na vitória faz revanche; Esc retorna à seleção.
- Esc pausa. Backspace na pausa retorna à seleção. Perder o foco da janela pausa e limpa as teclas pressionadas.

## Controles

| Ação | P1 | P2 |
|---|---|---|
| Andar | A / D | Setas esquerda / direita |
| Pular | W | Seta cima |
| Defender | Segurar S | Segurar seta baixo |
| Ataque fraco / aéreo | F | J |
| Ataque forte | G | K |
| Agarrão | V | N |
| Especial 1 | R | U |
| Especial 2 | T | I |
| Dash | Shift esquerdo | Shift direito |
| Correr | Ctrl esquerdo + direção | Ctrl direito + direção |
| Parry | C | M |
| Liberação | Q | O |
| Supremo | E | L |
| Técnica exclusiva liberada | X | Vírgula |

- **F1:** mostra todos os comandos e suspende a luta enquanto a ajuda está aberta.
- **F11:** janela/tela cheia. Janela redimensionável com proporção preservada.
- **F8:** liga/desliga tremor da câmera.
- **F9:** silencia/reativa áudio. **− / +:** volume.
- Dash com direção recua ou avança; sem direção segue para onde o personagem olha.
- Ataques, salto, dash e técnicas usam eventos de pressão. Segurar uma tecla não repete golpes.
- Dois jogadores podem esbarrar no limite físico de teclas simultâneas de alguns teclados (ghosting).

## Combate

Todos os golpes possuem preparação, fase ativa e recuperação. O acerto ocorre durante a fase ativa; cada golpe/projétil acerta o mesmo adversário no máximo uma vez. Hitbox, hurtbox e pushbox são separados. A física roda a 120 passos por segundo e a apresentação busca 60 FPS.

O buffer guarda cada comando por 150 ms. Normais que acertaram podem ser cancelados em outro normal, especial ou supremo; golpes que erraram precisam terminar sua recuperação. Dano de combo escala em 12% por acerto, com piso de 35%. O contador desaparece depois de 1,05 s sem acerto.

Três sequências testadas com cada personagem, de perto, pressionando o próximo golpe após o acerto:

1. Fraco → fraco → fraco.
2. Fraco → fraco → forte.
3. Fraco → forte → especial 1.

Essas são rotas de encadeamento, não comandos especiais de quarto de círculo. Alcance, posição e tempo de pressão continuam importando.

Defesa exige estar de frente, reduz dano para chip e gasta stamina. Stamina esgotada quebra a guarda. O agarrão ignora defesa e parry, exige proximidade e ambos no chão. Parry custa 18 stamina e tem janela inicial de aproximadamente 110 ms; Kurogane tem 180 ms. Um parry corpo a corpo atordoa o atacante. Ataques contra a preparação de outro golpe recebem bônus e exibem COUNTER.

Ataques fortes causam queda; a recuperação de levantar tem invulnerabilidade breve. Dash custa 23 stamina. A stamina regenera; correr é mais rápido, mas não concede invulnerabilidade.

## Personagens

| Personagem | Vida | Papel e passiva | Especiais | Supremo / exclusivo |
|---|---:|---|---|---|
| Kensei | 110 | Espadachim equilibrado; ganha mais reiatsu ao acertar | Lâmina lunar: projétil; Passo cortante: avanço ofensivo | Mil luas / Lua infinita |
| Vastor | 145 | Colosso lento; armadura durante preparação/atividade do forte | Investida carmesim; Abalo sísmico: onda rasteira | Sol devastador / Quebra-mundo |
| Zephyr | 90 | Atirador veloz e frágil; maior invulnerabilidade no dash | Flecha astral: projétil, diagonal no ar; Selo de caça: armadilha temporária | Chuva estelar / Estrela cadente |
| Kurogane | 130 | Guardião resistente; parry prolongado e reiatsu ao bloquear | Pulso de repulsão; Bastião: absorção por 2,5 s | Juízo de ferro / Muralha eterna |

Kensei tem cabelo claro, túnica e espada; Vastor é mais alto e largo, com máscara, chifres e garras; Zephyr usa casaco claro, echarpe e arco; Kurogane usa elmo, placas e escudo. São desenhos procedurais originais e não sprites de Bleach ou MUGEN.

## Reiatsu e liberação

- Reiatsu inicial: 45. Especial 1 custa 22; especial 2 custa 30; supremo custa 75.
- Liberação custa 70, dura 10 s e termina com 3 s de exaustão.
- Exaustão suspende regeneração de reiatsu e reduz movimento.
- Liberação altera aura, concede uma introdução invulnerável curta, aumenta alcance/movimento/dano e habilita o golpe exclusivo (15 reiatsu, cooldown de 2 s).
- Kurogane liberado ganha absorção adicional; com Bastião ativo, reflete projéteis e troca corretamente seu proprietário.
- Liberar consome o recurso: escolher entre transformação, supremo e especiais é parte do combate.

## Visual, IA e áudio

Cenário original em camadas: céu, lua, nuvens em movimento, montanhas, construções distantes, colunas, pátio, névoa e pontos espirituais. Câmera acompanha o centro da luta; zoom discreto em liberação/supremos próximos. Há partículas com duração e gravidade, anéis, arcos de corte, afterimages de dash, flash, hit stop, tremor e vinheta. Geometria estática e quadros procedurais são armazenados em cache.

HUD com retratos, nomes, vida atrasada, reiatsu, stamina, cooldowns, liberação, exaustão, combos, timer e vitórias. Poses de ataque, movimento, defesa, dano, queda, liberação e vitória.

IA decide por distância, arquétipo, recursos e ameaça. Reage a projéteis, mantém distância com Zephyr, aproxima-se com os demais, bloqueia ameaças próximas, pune recuperação e usa combos/liberação. Dificuldades mudam o intervalo de decisão (320/190/105 ms), tamanho das sequências e uso de parry; não aumentam o dano.

Efeitos sonoros simples são sintetizados localmente. Arquivos opcionais em `assets/audio` substituem os sons. `menu.ogg` e `arena.ogg` são carregados se existirem; nenhuma música comercial ou externa está incluída. Ausência de dispositivo de áudio não impede a execução. F9 e volume controlam áudio durante o jogo.

## Arquivos

**Modificados/refatorados:**

- `game.py`: loop, janela, navegação, pausa e renderização.
- `constants.py`: resolução, chão, limites, tempo e cores.
- `personagem_base.py`: estados, recursos, ações, física, dano e reset.
- `personagem_humano.py`: adaptador de controle por teclado.
- `seu_personagem.py`: quatro classes originais com perfis distintos.
- `projetil.py`: movimento, dono, expiração, colisão e reflexão.

**Criados:**

- `states.py`: enums da luta e do fluxo.
- `combat.py`: dados de golpes e tempos.
- `match.py`: rounds, placar, colisões e resolução de acertos.
- `input_manager.py`: teclas mantidas e eventos únicos.
- `animation.py`: poses procedurais, cache e retratos.
- `arena.py`, `camera.py`, `effects.py`: cenário, câmera, partículas e impacto.
- `hud.py`: HUD, seleção, abertura e controles.
- `ai.py`: decisões por arquétipo/dificuldade.
- `audio.py`: áudio opcional e efeitos sintetizados.
- `requirements.txt`, `INSTALAR.cmd`, `JOGAR.cmd`, `GERAR_EXE.cmd`.
- `tests/test_game.py`, `VALIDACAO.md`, `README.md` e `previews/*.png`.

O arquivo original `.7z` está preservado sem alterações em `backup-original/`, no nível acima da pasta do jogo. O projeto continua em Python/Pygame e mantém os nomes das quatro classes; a API interna de atualização agora recebe delta time e não usa os antigos contadores em frames.

## Testes

Dentro de `Fighting`:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

No Linux sem janela:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python game.py --smoke 120
```

Veja `VALIDACAO.md` para o resultado, ambiente e limites da validação.

## Limitações reais desta versão

- Não há executável Windows pré-compilado, rede, gamepad nem remapeamento por interface.
- Defesa é única, sem distinção alta/baixa; não há disparo carregável por segurar a tecla nem sistema de comandos direcionais complexos.
- A técnica de contra-ataque de Kensei usa o parry comum, sem um terceiro especial dedicado. A IA não é adaptativa nem aprende padrões do jogador.
- Quadros são poses procedurais estilizadas, não animação desenhada quadro a quadro de nível comercial. Alguns estados compartilham a pose-base; câmera de liberação e especiais é breve, sem cutscene elaborada.
- O efeito decisivo usa hit stop, partículas e flash; não há um sistema separado de slow motion do K.O.
- Supremos causam um acerto por ativação; nomes como “Chuva estelar” não representam uma barragem multi-hit.
- A liberação tem modificadores comuns e técnica exclusiva por personagem; apenas Kurogane acrescenta uma interação defensiva exclusiva de reflexão.
- Música completa e gravações de voz não estão incluídas. As opções de áudio/tremor não persistem entre execuções.
- Balanceamento inicial e testes automatizados não substituem sessões humanas em teclados reais. Windows, tela cheia física e saída de áudio real não foram testados neste ambiente.

## Créditos

Base: arquivos enviados pelo usuário. Reformulação: código e arte procedural produzidos para este projeto. Biblioteca: pygame-ce (LGPL). Fontes: fontes disponíveis no sistema via Pygame, com fallback padrão; nenhuma fonte externa foi incorporada. Sem personagens, logos, imagens ou músicas copiados das referências.
