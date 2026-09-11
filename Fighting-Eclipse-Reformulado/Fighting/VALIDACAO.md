# Validação — Spiritual Crossroads

Data: 11 de setembro de 2026.

## Ambiente e referência

Windows, Python 3.13.5, pygame-ce 2.5.8, SDL 2.32.10, ambiente isolado `.venv`. Antes da implementação, os 17 testes originais passaram. Vídeo e áudio usam drivers SDL dummy nas verificações automatizadas.

## Resultado atual

36 testes aprovados: os 17 testes do núcleo (agora iterando o catálogo ampliado) e 19 testes de integração da adaptação.

Inicialização adicional: `game.py --smoke 120` terminou com código 0 após 120 quadros, com vídeo e áudio dummy. `git diff --check` não identificou erros de whitespace.

O executável Windows com o modo treino foi gerado com PyInstaller 6.22.2 e testado com `--smoke 120`: código de saída 0. Tamanho: 16.003.538 bytes. SHA-256: `A3233ABB057BAFC31B2F241E797AE2726F5A006FD532DE870C5CADC40D3E96F9`.

Cobertura adicional: IDs e classificação; custos e transições Shikai/Bankai; duração, exaustão, persistência por round e limpeza no K.O.; mobilidades e passivas; flecha carregável e interrupção; janelas e limite de múltiplos acertos; reflexão com atualização de posição e dono; pares do catálogo em PVP/PVE com encerramento controlado; três partidas naturais de IA até a vitória (Kensei/Vastor, Zephyr/Kurogane, Akari/Zephyr); decisões de distância, defesa e forma da IA; persistência e JSON inválido; remapeamento pela interface; entrada, combinação de botões e desconexão de gamepad; cancelamento de carga após pausa/limpeza; renderização da seleção, arenas, ajuda e configurações; ciclo de seleção do treino, tempo/rounds infinitos, recuperação após K.O., recursos, reinício, estados do boneco e atalhos da interface.

As combinações com encerramento controlado forçam o K.O. após uma simulação inicial para testar o ciclo de rounds; somente o teste de partidas naturais aguarda o combate da IA decidir o vencedor. Isso não mede balanceamento competitivo.

## Inspeção visual

`qa_preview.py` gera abertura, seleção de todos os personagens, três arenas, ajuda, remapeamento e modo treino em `qa-output/`. Capturas de seleção e arenas inspecionadas; o rodapé recebeu fundo escuro para garantir contraste em Hueco Mundo.

## Limites

Não houve sessão humana de gameplay, teclado de dois jogadores, monitor em tela cheia física ou áudio real. Gamepad foi validado com eventos simulados; índices variam entre modelos/driver e não há remapeamento de gamepad por interface. O executável foi gerado e inicializado automaticamente, mas ainda não passou por uma sessão humana. A arte continua procedural. Os cenários têm geometrias visuais distintas e colisão competitiva idêntica.

O ZIP da raiz, o backup original e as capturas antigas de `previews/` permanecem históricos; as alterações atuais estão nos fontes do checkout.
