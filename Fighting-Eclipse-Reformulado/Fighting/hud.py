"""Arcade typography, fighter selection, control reference and match HUD."""
import math
from functools import lru_cache
import pygame
from constants import WHITE,GOLD,CYAN,RED
from animation import portrait,sprite
from states import Estado as E,Fluxo as F
from seu_personagem import PERFIS

@lru_cache(maxsize=24)
def font(size):return pygame.font.SysFont('DejaVu Sans',size,bold=True)

def text(s,value,pos,size=20,color=WHITE,center=False):
    img=font(size).render(str(value),True,color)
    s.blit(img,img.get_rect(center=pos) if center else pos)

def panel(s,rect,color=(16,26,42),edge=(62,83,102)):
    x,y,w,h=rect
    pts=[(x+15,y),(x+w,y),(x+w,y+h-15),(x+w-15,y+h),(x,y+h),(x,y+15)]
    pygame.draw.polygon(s,color,pts);pygame.draw.polygon(s,edge,pts,1)

def bar(s,x,y,w,h,value,color,reverse=False):
    pygame.draw.rect(s,(9,17,28),(x,y,w,h))
    width=round(w*max(0,min(1,value)))
    pygame.draw.rect(s,color,(x+w-width if reverse else x,y,width,h))

CONTROLS=[
 ('Movimento / pulo / defesa','A D / W / S','← → / ↑ / ↓'),
 ('Fraco / forte / agarrão','F / G / V','J / K / N'),
 ('Especial 1 / especial 2','R / T','U / I'),
 ('Dash / correr','Shift esq. / Ctrl esq.','Shift dir. / Ctrl dir.'),
 ('Parry / liberação','C / Q','M / O'),
 ('Supremo / técnica liberada','E / X','L / vírgula'),
]

def controls(s):
    panel(s,(160,142,960,448),(10,19,33),CYAN)
    text(s,'COMANDOS', (640,181),30,WHITE,True)
    text(s,'AÇÃO',(200,220),16,GOLD);text(s,'JOGADOR 1',(660,220),16,CYAN);text(s,'JOGADOR 2',(895,220),16,RED)
    for i,(label,p1,p2) in enumerate(CONTROLS):
        y=257+i*39
        text(s,label,(200,y),17);text(s,p1,(650,y),16);text(s,p2,(892,y),16)
    text(s,'F1 fechar  •  Esc pausa  •  F11 tela cheia  •  F8 tremor  •  F9 som  •  − / + volume',(640,540),16,GOLD,True)


def draw_hud(s,m):
    for i,p in enumerate(m.players):
        x=36 if i==0 else 772
        color=p.cor_base
        panel(s,(x,22,472,130),(13,22,36),color)
        s.blit(portrait(p.identidade,78),(x+9,35))
        text(s,p.nome.upper(),(x+100,31),24)
        text(s,f'{int(p.vida):03} / {p.vida_maxima}',(x+336,41),14,color)
        bar(s,x+101,69,351,22,p.vida_atrasada/p.vida_maxima,(174,70,80),i==1)
        width=int(351*p.vida/p.vida_maxima)
        pygame.draw.rect(s,(221,224,198),(x+101+351-width if i==1 else x+101,69,width,22))
        bar(s,x+101,99,351,8,p.reiatsu/p.reiatsu_maximo,color,i==1)
        bar(s,x+101,114,351,5,p.stamina/100,GOLD,i==1)
        text(s,f'REI {int(p.reiatsu)}   STM {int(p.stamina)}',(x+101,125),10,color)
        for w in range(2):
            xx=550-w*26 if i==0 else 730+w*26
            pygame.draw.polygon(s,GOLD if m.wins[i]>w else (44,56,72),[(xx,102),(xx+8,110),(xx,118),(xx-8,110)])
        if p.forma_liberada:
            text(s,f'LIBERADO  {p.tempo_liberacao:.1f}s',(x+10,160),16,GOLD)
        elif p.exaustao:text(s,f'EXAUSTÃO  {p.exaustao:.1f}s',(x+10,160),16,RED)
        if p.contador_combo>=2:
            text(s,f'{p.contador_combo} HITS',(x+20,235),35,color)
            text(s,f'{p.dano_combo:.0f} DANO',(x+24,278),15)
        if p.tempo_mensagem>0:text(s,p.mensagem,(x+236,202),19,color,True)
        cds=[f'{key}: {value:.1f}' for key,value in p.cooldowns.items() if value>.05]
        if cds:text(s,'  '.join(cds),(x+10,675),12,color)
    text(s,f'{math.ceil(m.time):02}',(640,62),48,WHITE,True)
    text(s,f'ROUND {m.round}',(640,112),13,GOLD,True)
    text(s,'F1 COMANDOS  /  ESC PAUSA',(640,694),12,(144,167,184),True)
    if m.phase==F.INTRO:
        word=f'ROUND {m.round}' if m.phase_time>.65 else 'FIGHT'
        text(s,word,(640,315),76,GOLD if m.phase_time>.65 else WHITE,True)
        text(s,f'{m.players[0].nome.upper()}  /  {m.players[1].nome.upper()}',(640,385),18,WHITE,True)
    elif m.phase==F.KO:text(s,m.result,(640,318),46,RED,True)
    elif m.phase==F.VICTORY:
        panel(s,(300,246,680,245),(11,20,33),GOLD)
        text(s,m.players[m.winner].nome.upper()+' VENCE',(640,307),44,GOLD,True)
        text(s,f'{m.wins[0]}  —  {m.wins[1]}',(640,369),28,WHITE,True)
        text(s,'ENTER  REVANCHE     /     ESC  SELEÇÃO',(640,441),19,WHITE,True)


def draw_title(s,time):
    text(s,'FIGHTING  /  CONFRONTO ESPIRITUAL',(95,85),17,CYAN)
    text(s,'ECLIPSE',(83,194),116,WHITE)
    text(s,'SPIRIT CLASH',(92,327),52,GOLD)
    pygame.draw.line(s,CYAN,(98,412),(620,412),3)
    text(s,'QUATRO DESTINOS. UMA ARENA.',(98,436),18,WHITE)
    text(s,'ENTER  /  INICIAR',(98,549),25,GOLD)
    text(s,'F1  COMANDOS      F11  TELA CHEIA',(98,601),14,(156,179,193))
    img=sprite(0,E.IDLE,int(time*8)%8,True,1)
    img=pygame.transform.smoothscale(img,(690,529))
    s.blit(img,(680,141))


def draw_select(s,selected,confirmed,mode,difficulty):
    text(s,'ESCOLHA SEU DESTINO',(640,63),43,WHITE,True)
    text(s,f'TAB  {mode}     /     F2  {("FÁCIL","NORMAL","DIFÍCIL")[difficulty]}',(640,112),18,GOLD,True)
    for i,index in enumerate(selected):
        p=PERFIS[index];x=54 if i==0 else 674
        panel(s,(x,152,552,444),(13,23,38),p.cor)
        text(s,f'P{i+1}  /  '+('PRONTO' if confirmed[i] else 'SELECIONE'),(x+24,172),16,p.cor)
        s.blit(portrait(index,150),(x+13,211))
        text(s,p.nome.upper(),(x+186,211),32)
        text(s,p.titulo,(x+186,258),14,p.cor)
        text(s,p.dificuldade,(x+186,285),14,GOLD)
        text(s,p.descricao,(x+24,370),15)
        text(s,f'VIDA {p.vida}    ATAQUE {p.dano}    DEFESA {int(p.defesa*100)}%',(x+24,408),16)
        text(s,f'VELOCIDADE {p.velocidade}    REIATSU {p.reiatsu}',(x+24,435),16)
        text(s,p.passiva,(x+24,471),13,p.cor)
        names=[('Lâmina lunar','Passo cortante'),('Investida carmesim','Abalo sísmico'),('Flecha astral','Selo de caça'),('Pulso de repulsão','Bastião')][index]
        text(s,'TÉCNICAS  /  '+ ' • '.join(names),(x+24,510),13)
        text(s,'A / D   escolher     F   confirmar' if i==0 else '← / →   escolher     J   confirmar',(x+24,556),16,GOLD)
    text(s,'ENTER  LUTAR (após confirmar ambos)    /    F1  COMANDOS',(640,639),18,WHITE,True)
    text(s,'No PVE, escolha e confirme também o adversário.',(640,679),14,(151,171,187),True)
