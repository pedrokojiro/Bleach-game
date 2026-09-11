"""Arcade typography, fighter selection, control reference and match HUD."""
import math
from functools import lru_cache
import pygame
from constants import WHITE,GOLD,CYAN,RED
from animation import portrait,sprite
from states import Estado as E,Fluxo as F
from seu_personagem import PERFIS
from catalog import KITS

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

ACTION_NAMES={'left':'Esquerda','right':'Direita','jump':'Pulo','guard':'Defesa','light':'Ataque fraco','heavy':'Ataque forte','special':'Especial 1 / carregar','special2':'Especial 2','grab':'Agarrão','dash':'Passo / esquiva','parry':'Parry','release':'Forma / avançar forma','ultimate':'Supremo','exclusive':'Técnica da forma','run':'Correr'}

def controls(s,maps=None):
    from input_manager import MAPS
    maps=maps or MAPS
    panel(s,(140,30,1000,660),(10,19,33),CYAN)
    text(s,'COMANDOS / F3 REMAPEAR',(640,63),28,GOLD,True)
    for j,action in enumerate(maps[0]):
        y=104+j*31
        text(s,ACTION_NAMES[action],(185,y),17)
        for i in range(2):text(s,pygame.key.name(maps[i][action]).upper(),(650+i*250,y),16,CYAN if i==0 else RED)
    text(s,'Quincy: segure Especial 1 e solte para disparar. Forma: pressione novamente para Bankai.',(640,596),14,GOLD,True)
    text(s,'Gamepad: A fraco / B forte / X especial / Y especial 2 / LB defesa / RB passo',(640,626),14,WHITE,True)
    text(s,'Treino: F5 reinicia / F6 boneco / F7 recursos. F8 tremor / F9 som / F11 tela cheia',(640,658),13,GOLD,True)
def draw_hud(s,m):
    pygame.draw.rect(s,(10,18,31),(0,657,1280,63))
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
            text(s,f'{p.form.name}  {p.tempo_liberacao:.1f}s',(x+10,160),16,GOLD)
        elif p.exaustao:text(s,f'EXAUSTÃO  {p.exaustao:.1f}s',(x+10,160),16,RED)
        if p.contador_combo>=2:
            text(s,f'{p.contador_combo} HITS',(x+20,235),35,color)
            text(s,f'{p.dano_combo:.0f} DANO',(x+24,278),15)
        if p.tempo_mensagem>0:text(s,p.mensagem,(x+236,202),19,color,True)
        cds=[f'{p.moves[key].nome}: {value:.1f}' for key,value in p.cooldowns.items() if value>.05]
        if cds:text(s,'  '.join(cds),(x+10,675),12,color)
    text(s,'∞' if m.mode=='TREINO' else f'{math.ceil(m.time):02}',(640,62),48,WHITE,True)
    text(s,'TREINO' if m.mode=='TREINO' else f'ROUND {m.round}',(640,112),13,GOLD,True)
    footer='F5 REINICIAR / F6 BONECO: '+m.training_dummy+' / F7 RECURSOS: '+('∞' if m.training_resources else 'NORMAL') if m.mode=='TREINO' else 'F1 COMANDOS / F3 REMAPEAR / ESC PAUSA'
    text(s,footer,(640,694),12,WHITE,True)
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
    text(s,'FAN GAME / PERSONAGENS ORIGINAIS',(95,85),17,CYAN)
    text(s,'BLEACH',(83,194),116,WHITE)
    text(s,'SPIRITUAL CROSSROADS',(92,327),32,GOLD)
    pygame.draw.line(s,CYAN,(98,412),(620,412),3)
    text(s,'CINCO DESTINOS. TRÊS MUNDOS.',(98,436),18,WHITE)
    text(s,'ENTER  /  INICIAR',(98,549),25,GOLD)
    text(s,'F1  COMANDOS      F11  TELA CHEIA',(98,601),14,(156,179,193))
    img=sprite(0,E.IDLE,int(time*8)%8,True,1)
    img=pygame.transform.smoothscale(img,(690,529))
    s.blit(img,(680,141))

def draw_select(s,selected,confirmed,mode,difficulty,arena='Soul Society'):
    text(s,'BLEACH / ESCOLHA SEU DESTINO',(640,38),30,WHITE,True)
    text(s,f'TAB {mode} / F2 {("FÁCIL","NORMAL","DIFÍCIL")[difficulty]} / F4 ARENA: {arena}',(640,82),17,GOLD,True)
    # A paged grid expands with the catalog; selections may be on separate pages.
    for side,index in enumerate(selected):
        p=PERFIS[index];kit=KITS[p.id];x=34+side*620
        panel(s,(x,118,592,378),(13,23,38),p.cor)
        s.blit(portrait(p.id,105),(x+16,136))
        text(s,p.nome.upper(),(x+135,138),29)
        text(s,p.titulo,(x+135,181),15,p.cor)
        text(s,f'P{side+1} / '+('PRONTO' if confirmed[side] else 'SELECIONE'),(x+135,214),16,GOLD)
        text(s,f'{kit.origin.value} / {kit.affiliation}',(x+18,257),14,p.cor)
        text(s,f'Estilo: {kit.archetype} / {kit.mobility.name}',(x+18,283),15)
        text(s,p.passiva,(x+18,310),14)
        text(s,' / '.join(spec[0] for spec in kit.specials),(x+18,340),16,p.cor)
        for j,form in enumerate(kit.forms):
            text(s,f'{form.name} · {form.cost:g} reiatsu · {form.duration:g}s',(x+18,370+j*24),14,GOLD)
        text(s,f'VIDA {p.vida} / REIATSU {p.reiatsu} / {p.dificuldade}',(x+18,430),15)
        text(s,'A/D escolher · F confirmar' if side==0 else '←/→ escolher · J confirmar',(x+18,467),15,GOLD)
        page=index//6
        for cell in range(6):
            idx=page*6+cell
            if idx>=len(PERFIS):break
            xx=x+(cell%3)*198;yy=509+(cell//3)*53
            chosen=idx==index
            panel(s,(xx,yy,190,46),(32,46,67) if chosen else (12,22,36),PERFIS[idx].cor if chosen else (55,70,88))
            text(s,PERFIS[idx].nome,(xx+12,yy+12),16,PERFIS[idx].cor if chosen else WHITE)
    text(s,'ENTER LUTAR / F1 AJUDA / F3 REMAPEAR',(640,638),19,GOLD,True)
    hint='TREINO: P1 pratica; escolha o boneco como P2.' if mode=='TREINO' else 'PVE: confirme também a CPU. Gamepad: LB/RB escolhem, A confirma, Start inicia.'
    text(s,hint,(640,676),14,WHITE,True)
