# Godot Edition — guia de execução e migração

## Estado da entrega

Projeto independente em `godot/`, Godot 4.7.2 / GDScript / renderizador Compatibility. A versão Python e seu executável em `dist/` permanecem preservados. Não há campanha, progressão ou multiplayer online nesta versão.

Cinco lutadores, três arenas, PVP local, PVE e treino. O recorte Kensei/Vastor passou em 42 verificações antes de liberar o elenco completo. O conjunto completo passou em 104 verificações de combate, 40 de sistemas e 20 vetores de comparação Python/Godot. São verificações automatizadas, não uma certificação de balanceamento ou equivalência completa.

## Jogar

Windows: abra `godot/export/windows/BleachGodot.exe`. Não requer Python nem o editor Godot. O executável antigo continua em `dist/BleachSpiritualCrossroads.exe`.

Web: sirva toda a pasta `godot/export/web`, não apenas index.html. A partir da raiz:

```powershell
.\.venv\Scripts\python.exe -m http.server 8077 --bind 127.0.0.1 --directory godot/export/web
```

Abra http://localhost:8077. Não abra por `file://`. A exportação usa WebAssembly/WebGL 2 sem threads. O navegador pode exigir um clique para liberar áudio. Atalhos reservados pelo navegador podem interferir; use os menus para opções. O armazenamento depende de o navegador permitir persistência local.

## Controles Godot

Enter abre a seleção/inicia a partida. A/D mudam P1; setas mudam P2; Tab alterna modo. Arena, paleta e opções estão nos botões. Os controles abaixo são da edição Godot, não do executável Python.

| Ação | P1 | P2 |
|---|---|---|
| Mover / pular / defender | A D / W / S | Setas |
| Leve / forte / agarrar | F / G / V | J / K / N |
| Especial 1 / 2 | R / T | U / I |
| Dash / correr | Shift / Ctrl | Ponto / barra |
| Parry / transformar | C / Q | M / O |
| Supremo / técnica da forma | E / X | L / vírgula |

Esc pausa; F1 abre configurações; F11 alterna tela cheia. Zephyr carrega o primeiro especial segurando a tecla e dispara ao soltar.

Gamepad: analógico esquerdo move; A pula, B forte, X leve, Y especial; LB defende, RB dash; L2 especial 2, R2 supremo; clique esquerdo parry, clique direito forma; Back técnica exclusiva; direcional para cima agarra e para baixo corre; Start pausa. Índices são os normalizados do Godot. Dois dispositivos correspondem a P1/P2. Os botões de menu aceitam navegação padrão do Godot. Todas as ações de combate podem ser remapeadas em Configurações, inclusive eixos e gatilhos. Evite atribuições conflitantes: esta interface não troca automaticamente ações duplicadas.

## Treino e customização

- F5: reset de posições, recursos, formas, recargas e projéteis.
- F6: parado, defesa, defesa após primeiro acerto, parry automático ou CPU.
- F7: recursos infinitos; F8: hitbox vermelha, hurtbox azul, pushbox verde.
- F9: grava até 15 segundos; os comandos de P1 controlam o boneco durante a gravação. Pressione novamente para terminar.
- F10: reproduz a gravação em loop; pressione novamente para parar. A gravação fica somente na memória da partida.

HUD mostra histórico, dano, combo e tempos do golpe a 120 quadros de simulação por segundo. A vantagem é **estimada**, calculada pelo stun do alvo menos o restante do ataque; não mede vantagem real com todos os efeitos de distância, projéteis e recuperação.

Configurações incluem música, efeitos, tremor, flash, resolução, tela cheia, duração do round, vitórias necessárias, dificuldade e multiplicador de vida no treino. A vida configurada é aplicada no reset; restauração automática ocorre após terminar o combo. Preferências são salvas em `user://preferences.json`, no diretório de dados do Godot no Windows e no armazenamento do navegador na Web. As configurações do Python são independentes.

## Editar e gerar builds

O editor e templates usados neste checkout estão em `.tools/godot`, ignorados pelo Git. Para reproduzir em outra máquina, obtenha editor Windows x86-64 e export templates **da mesma versão 4.7.2**, nas distribuições oficiais do Godot. Extraia o editor em `.tools/godot` e os templates em `.tools/godot/templates`. Os presets referenciam os templates Windows x86-64 e Web sem threads nessa pasta.

```powershell
.\tools\build_godot.ps1
```

O script copia `content/` para `godot/content/`, importa recursos, executa as três suítes e exporta Windows/Web. Pare se houver erro. `-Godot caminho` permite indicar outro editor compatível; ajuste os caminhos dos templates nos presets se necessário. Abra `godot/project.godot` no editor após copiar o conteúdo. O build contém os dados; editar o JSON da raiz exige novo build.

`tools/export_content.py --stage` também faz somente a cópia dos JSON. **Sem `--stage`, o exportador regenera os dados e recursos a partir da referência Python, sobrescrevendo customizações nesses arquivos.** Use essa opção apenas para atualizar deliberadamente o snapshot de referência.

## Organização e expansão

- `content/characters`: perfis, atributos, origem, afiliação, mobilidade, passivas e referências.
- `content/moves`: golpes, custos, fases, janelas de acerto e hitboxes; tempos em segundos.
- `content/forms`: custos, duração, multiplicadores e capacidades das formas.
- `content/arenas`: catálogo das arenas; as três apresentações estão em `arena_view.gd`.
- `content/palettes`, `effects`, `audio`: cores, impacto e referências de som.
- `scripts/combat`: simulação e resolução explícita de colisões/rounds.
- `controllers`, `ai`, `data`: entrada, decisões e carregamento/persistência.
- `presentation`: atlas animados e cenários. `main.gd` integra fluxo, interface, áudio e efeitos; essa integração ainda pode ser subdividida.

Para novo lutador, copie os JSON de um existente, altere IDs/perfil/kit/golpes/formas e registre o ID em `content/manifest.json`. Forneça os dois atlas indicados: oito colunas, uma linha por estado de `animation_states`. Pode reutilizar um atlas provisório existente. Habilidades reutilizam tipos como melee, projectile, rush, trap e barrier; um comportamento novo requer implementação e testes, não apenas um novo nome no JSON. Não há condicionais por ID de lutador no núcleo de combate.

O carregador rejeita arquivos ausentes, tipos incorretos, campos necessários, números inválidos e janelas de acerto fora da fase ativa, com localização do problema. Isso não constitui um editor visual de conteúdo nem um esquema JSON exaustivo. O Python legado permanece usando seus dados originais: os JSON são um snapshot interoperável, não uma mudança silenciosa da especificação legada.

Novas arenas podem entrar no catálogo, mas geometria artística nova requer apresentação adicional. As dimensões competitivas continuam fixas (1700, chão 580); os campos width/floor do catálogo documentam esses valores e não alteram a física nesta versão.

## Regras preservadas e diferenças

Simulação a 120 Hz; aceleração 2300, gravidade 1900, impulso de salto -740, corrida 1,3×. Dash usa velocidade/duração/custo/invulnerabilidade do kit. Vida e reiatsu máximos vêm do perfil, reiatsu inicial 45, stamina máxima 100. Regeneração normal vem do perfil/kit; defesa regenera 7/s e drena 12/s. Exaustão reduz velocidade para 72% e interrompe regeneração normal de reiatsu.

Buffer de 150 ms, até quatro entradas. Ataques têm startup/ativo/recuperação; normais confirmados permitem cancelamento. Hitbox, hurtbox e pushbox separadas; cada janela só acerta uma vez. O dano de combo reduz 12% por acerto até o piso de 35%; janela de combo 1,05 s. Defesa frontal causa 15% de chip e consome 80% do dano base em stamina; guarda zerada sofre 0,7 s de stun. Parry respeita janela do kit, ganha 15 reiatsu e pune atacante corpo a corpo por 0,42 s. Agarrão ignora defesa/parry, exige chão e proximidade. Queda padrão 0,65 s seguida de levantar invulnerável por 0,25 s.

Formas usam custos e durações extraídos do Python, introdução invulnerável de 0,7 s, exaustão e limpeza no K.O./reset. Projéteis preservam proprietário e reflexão; supremos usam múltiplas janelas. IA decide por arquétipo, distância e recursos. Round padrão de 99 s, duas vitórias, empate por percentual de vida repete round.

Os 20 vetores comparam movimento, salto, dash e transformação dos cinco lutadores, com tolerância 0,001 para posições/recursos e igualdade de estado. Não comparam cada sequência possível de combate. Diferenças intencionais: áudio/visual desacoplados, opções ampliadas, gravação de treino, coordenadas em ponto flutuante Godot, comandos P2 sem distinguir modificadores esquerdo/direito e hitstun/blockstun configuráveis por golpe. A câmera lenta do K.O. é uma desaceleração dos efeitos visuais; não altera resultados da simulação.

## Qualidade e limites

Capturas reproduzíveis: execute o editor com `--path godot --script tests/visual_review.gd`. Saídas em `godot/qa`, ignoradas pelo Git. Foram inspecionados abertura, seleção, configurações, treino, três arenas e formas. Arte: atlas provisórios originais derivados do desenho procedural legado, retratos recortados dos próprios sprites, cenários procedurais em camadas, iluminação e partículas. Não são sprites finais desenhados quadro a quadro; Shikai/Bankai ainda compartilham o atlas de forma.

Windows foi renderizado nesta máquina via ANGLE (Intel HD Graphics 4600). Web foi testada no navegador integrado: abertura, seleção de Zephyr, treino, disparo com dano no boneco e transformação Vollständig. Não houve erros/avisos no console durante esse teste; isso não implica testes em Firefox/Safari/mobile. Gamepads foram testados por eventos sintéticos, sem hardware físico. Ainda faltam sessão humana prolongada, avaliação de áudio, balanceamento competitivo e arte final. Campanha, progressão, rede, retratos exclusivos e cinematografia elaborada são próximos incrementos, não funcionalidades concluídas.

### Registro de build — 11/09/2026

- Windows: 111.047.616 bytes; SHA-256 `3A8B5027572CA412BAAF1FC2DA49F56D0AB5227C3D4254171BF911C7665E3A41`.
- Web: aproximadamente 41,6 MB sem compressão HTTP; WASM 39.514.754 bytes e pacote 1.779.124 bytes. Arquivos `.import` gerados no diretório de saída não são necessários para hospedagem.
- Executável final: teste gráfico de treino por 120 quadros, saída 0, ciclo completo de 18,17 s nesta máquina. Esse tempo inclui inicialização, fallback ANGLE, execução e encerramento; não é medida isolada de tempo até o primeiro quadro. O log contém somente o aviso de fallback do driver, sem erro de script.
- Build anterior em modo sem vídeo: ciclo de 3,36 s. A inicialização Web não foi cronometrada isoladamente.
- 36 testes Python novamente aprovados. Godot: 104 verificações de combate, 40 de sistemas e 20 vetores de referência aprovados. A última alteração foi apenas a troca de uma seta sem glifo por `>` no histórico, seguida de reexportação e teste do executável.
