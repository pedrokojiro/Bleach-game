# Bleach — Spiritual Crossroads

## Nova edição Godot

A migração jogável está em `godot/`, com cinco personagens, três arenas, PVP/PVE/treino e exportações Windows/Web. Consulte [GODOT.md](GODOT.md) para execução, controles, customização, builds, testes e limitações. O executável novo é `godot/export/windows/BleachGodot.exe`. A documentação abaixo descreve a **versão Python preservada**.

Jogo de luta 2D local em Python/pygame-ce, com cinco personagens originais ambientados no universo de Bleach. PVP no mesmo computador e PVE contra IA. Arte e efeitos procedurais: nenhuma mídia externa é necessária.

## Jogar no Windows

1. Instale Python 3.10 ou superior.
2. Execute `INSTALAR.cmd` nesta pasta para preparar o ambiente isolado `.venv` (requer internet).
3. Execute `JOGAR.cmd` nesta pasta.

Neste checkout, o ambiente já foi preparado e validado com Python 3.13.5 e pygame-ce 2.5.8. O executável atual está em `dist\BleachSpiritualCrossroads.exe`.

Para recriar o executável Windows, execute `GERAR_EXE.cmd` na raiz. O resultado único é gravado em `dist\BleachSpiritualCrossroads.exe`.

Alternativa no PowerShell, a partir desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Fighting-Eclipse-Reformulado/Fighting/requirements.txt
.\.venv\Scripts\python.exe Fighting-Eclipse-Reformulado/Fighting/game.py
```

Linux/macOS: `python3 -m venv .venv`, instale o mesmo arquivo de requisitos com `.venv/bin/python -m pip install -r ...` e execute `game.py` com esse interpretador.

## Seleção e controles

Enter abre a seleção. A/D e F escolhem/confirmam P1; setas esquerda/direita e J escolhem/confirmam P2. No PVE e no treino, confirme também o adversário/boneco. Enter inicia quando ambos estiverem prontos.

- Tab: alterna PVE, PVP e TREINO. F2: dificuldade. F4: arena, na seleção.
- F1: ajuda com os comandos atuais. F3: remapeamento de teclado, com a partida suspensa.
- No remapeamento: ↑/↓ escolhem a ação; Tab escolhe o jogador; Enter captura a nova tecla; Esc cancela ou sai. Teclas globais e de menu são reservadas; conflitos dentro do mesmo jogador trocam as duas ações. Evite atribuir a mesma tecla aos dois jogadores.
- Esc: pausa. Backspace na pausa: seleção. Enter na vitória: revanche; Esc: seleção.
- F8: tremor. F9: som. −/+: volume. F11: tela cheia.

### Modo treino

Selecione `TREINO` com Tab, escolha o lutador do P1 e o boneco como P2 e confirme ambos. Não há cronômetro, rounds ou tela de K.O. A vida é restaurada automaticamente ao chegar a zero.

- F5: restaura vida, formas, recargas e posições, e remove projéteis.
- F6: alterna o boneco entre `PARADO`, `DEFESA` e `CPU`. A opção CPU usa a dificuldade selecionada com F2.
- F7: liga ou desliga reiatsu e stamina infinitos. O padrão é ligado.

O contador de combo e o dano acumulado permanecem visíveis, permitindo testar rotas, custos, transformações, defesa e reação da IA. Esc pausa e Backspace volta à seleção como nos outros modos.

| Ação | P1 padrão | P2 padrão |
|---|---|---|
| Movimento / pulo / defesa | A D / W / S | ← → / ↑ / ↓ |
| Fraco / forte / agarrão | F / G / V | J / K / N |
| Especial 1 / especial 2 | R / T | U / I |
| Passo / corrida | Shift esquerdo / Ctrl esquerdo | Shift direito / Ctrl direito |
| Parry / forma | C / Q | M / O |
| Supremo / técnica da forma | E / X | L / vírgula |

Zephyr carrega Especial 1 enquanto a tecla estiver pressionada: até 1 segundo, até o dobro de dano, com até 10 de custo adicional. Solte para disparar. Dano recebido, pausa/limpeza dos controles e desconexão cancelam a carga. Os demais personagens disparam normalmente ao pressionar.

### Gamepad

Até dois joysticks SDL podem ser conectados, inclusive durante a execução. O mapeamento usa índices convencionais de botões, e pode variar conforme o dispositivo/driver:

| Entrada convencional | Ação |
|---|---|
| Analógico esquerdo ou direcional horizontal | Mover |
| Direcional para cima | Pular |
| A / B / X / Y (0–3) | Fraco / forte / especial 1 / especial 2 |
| LB / RB (4–5) | Defesa / passo |
| Back (6) / Start (7) | Parry / iniciar, pausar ou revanche |
| Clique esquerdo / direito (8–9) | Agarrão / forma |
| LB + A / B / X / Y | Pulo / agarrão / técnica da forma / supremo |

Na seleção, LB/RB escolhem e A confirma o jogador associado ao controle; Start inicia. O teclado continua disponível para configurar modo, arena e CPU. Corrida também está disponível no teclado; dispositivos com botões extras podem usar botão 13. O remapeamento por interface é de **teclado**, não de gamepad. Os eventos de controle foram simulados em testes, sem validação de hardware físico.

Som, volume, tremor e teclas persistem em `Fighting-Eclipse-Reformulado/Fighting/settings.json`, ignorado pelo Git. Arquivo ausente ou inválido usa os padrões; falhas de gravação mostram aviso. Tela cheia e seleção de arena não persistem.

## Elenco e estratégia

| Personagem | Origem / afiliação | Pontos fortes e limitações | Formas |
|---|---|---|---|
| Kensei | Alma; Shinigami independente | Alcance e reiatsu extra ao acertar. Equilibrado; exige escolher entre gastar em técnicas e avançar a forma. | Shikai: Tsukikage → Bankai: Mugen Tsukikage |
| Vastor | Hollow transformado em Arrancar; Hueco Mundo | Armadura no forte, pequena cura por acerto e Cero. Lento e vulnerável na recuperação. | Resurrección: Devorador |
| Zephyr | Humano; Quincy independente | Flecha carregável, armadilha, Hirenkyaku e regeneração de reishi na forma. Pouca vida; deve preservar distância. | Vollständig: Sternflug |
| Kurogane | Humano; Fullbringer independente | Escudo familiar é seu objeto de afinidade. Parry prolongado, reiatsu ao bloquear e barreira. Mobilidade limitada. | Fullbring: Iron Oath; barreira reflete projéteis durante a forma |
| Akari | Humana espiritual; Vigilantes de Karakura | Palma ofensiva, talismã, recuperação de stamina e esquiva econômica. Sem armadura ou reflexão; depende de posicionamento. | Foco absoluto, uma postura de combate |

Cada personagem tem dois especiais, supremo de três acertos e técnica exclusiva da forma. Os nomes de personagens, armas, organizações locais e técnicas autorais são design deste fan game. Kensei é o protótipo original, **não** uma representação de Kensei Muguruma. Custos, durações, cura de Vastor e estágios são adaptações de jogabilidade, não uma descrição exaustiva das regras canônicas.

Hollow e Arrancar têm classificações distintas no catálogo; o representante jogável inicial é Arrancar. Não há um sexto Hollow puro nesta entrega. Quincy e Fullbringer compartilham origem humana, com afiliações e kits diferentes.

## Combate e formas

Física a 120 Hz, apresentação a 60 FPS. Hitbox, hurtbox e pushbox separadas; buffer de 150 ms; normais confirmados podem cancelar; golpes que erram recuperam normalmente. Defesa frontal tem chip e consome stamina; agarrão exige proximidade e chão. Parry, quedas, levantar invulnerável e K.O. simultâneo continuam suportados.

Primeiro a duas vitórias vence. Round de 99 segundos. Tempo compara percentual de vida. Empate repete o round. Arenas não mudam atributos ou colisão competitiva.

Reiatsu inicial: 45. Especiais básicos: 22/30; supremo: 75; técnica de forma: 15. Transformar custa 70, exceto Foco absoluto (55). Bankai exige Shikai ativo e mais 55 reiatsu; após a introdução, pressione Forma novamente quando tiver recurso. Shikai regenera 2/s para permitir construir a transição. Bankai dura 8 s, Foco 9 s, demais formas 10 s; ao terminar há exaustão configurável. Formas concedem introdução invulnerável de 0,7 s. K.O. e reset limpam a forma.

As formas alteram alcance, velocidade, dano e técnica; algumas acrescentam absorção, regeneração e reflexão. Bankai modifica a técnica exclusiva para dois acertos. A infraestrutura aceita duração zero para forma persistente por round, embora todas as formas do elenco atual sejam temporárias.

Supremos usam três janelas explícitas de acerto. Corpo a corpo limita cada janela a um acerto por adversário; supremo de projéteis emite três projéteis independentes. Cada projétil só acerta uma vez e respeita proprietário/reflexão.

## Arenas

Soul Society: pátio e arquitetura espiritual. Karakura: rua e prédios iluminados. Hueco Mundo: deserto claro, lua crescente e árvores minerais. Todos compartilham os mesmos limites físicos. Wandenreich e Garganta são expansões planejadas.

## Estrutura e expansão

O código permanece em `Fighting-Eclipse-Reformulado/Fighting` para preservar os caminhos existentes. Os atalhos e este README na raiz identificam a versão de trabalho.

- `catalog.py`: origem, afiliação, arquétipo, mobilidade, formas e kits por ID estável.
- `seu_personagem.py`: perfis, catálogo e fábrica; `ELENCO` é derivado do catálogo. Nomes antigos permanecem como fábricas de compatibilidade.
- `combat.py`: dados dos golpes, custos e cronograma de acertos.
- `personagem_base.py`: recursos, estados, passivas parametrizadas e transições.
- `match.py` / `projetil.py`: colisões, janelas de acerto, propriedade e rounds.
- `input_manager.py` / `ai.py`: comandos humanos e IA por estilo, alcance e recursos.
- `animation.py` / `arena.py` / `hud.py`: apresentação. Os visuais usam estilos nomeados, independentes dos IDs de combate.
- `settings.py`: leitura validada e gravação por substituição atômica.

Para adicionar personagem, crie um perfil com ID único e um kit com o mesmo ID, reutilize ou acrescente um estilo em `VISUALS`. A seleção paginada, fábrica e testes iteram o catálogo. Para novos comportamentos de habilidade, acrescente a resolução correspondente no sistema de combate; não inclua condições por personagem. Acrescente cenários no catálogo `ARENAS` e na apresentação de `ArenaVisual`.

O ZIP da raiz e `backup-original/Fighting-original.7z` são arquivos históricos preservados, não são a distribuição atualizada. Os antigos `previews/` também são históricos. Caches `.pyc` foram retirados do versionamento, permanecem regeneráveis no disco e estão no `.gitignore`.

## Verificação

Na pasta do jogo:

```powershell
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
$env:SDL_VIDEODRIVER='dummy'
$env:SDL_AUDIODRIVER='dummy'
..\..\.venv\Scripts\python.exe game.py --smoke 120
..\..\.venv\Scripts\python.exe qa_preview.py
```

Capturas atuais são geradas em `qa-output/`, ignorado pelo Git. Consulte `Fighting-Eclipse-Reformulado/Fighting/VALIDACAO.md` para evidências e limites.

## Próximos marcos

Treinamento com exibição de hitboxes; balanceamento com jogadores; sprites desenhados e animações mais expressivas; controles normalizados e remapeáveis para mais gamepads; história/arcade; progressão e desbloqueios; elenco ampliado; rede.

A entrega é um protótipo jogável. Não inclui campanha, aprendizado adaptativo da IA, áudio de voz, música licenciada, sprites comerciais ou multiplayer online. O executável Python está em `dist/BleachSpiritualCrossroads.exe`.
