"""Cached procedural keyframes: original silhouettes, equipment and combat poses."""
import math
from functools import lru_cache
import pygame
from states import Estado as E

class Animation:
    def __init__(self,fps=12):self.fps=fps
    def frame(self,time):return int(time*self.fps)%8

ANIMATION=Animation()

@lru_cache(maxsize=2048)
def sprite(identity:int,state:E,frame:int,released:bool,direction:int):
    s=pygame.Surface((300,230),pygame.SRCALPHA)
    palettes=[((35,51,73),(100,210,250)),((75,31,38),(250,104,84)),((27,56,60),(119,235,196)),((43,37,63),(190,159,250))]
    dark,accent=palettes[identity]
    ink=(9,14,24); white=(231,236,230);skin=(206,169,145)
    cx,feet=140,211
    bob=math.sin(frame*math.pi/4)*2
    moving=state in (E.WALK,E.RUN,E.DASH)
    attack=state in (E.ATTACK_LIGHT,E.ATTACK_HEAVY,E.ATTACK_AIR,E.SPECIAL,E.ULTIMATE,E.GRAB)
    guard=state in (E.BLOCK,E.BLOCKSTUN,E.PARRY)
    height=[142,166,138,151][identity]
    top=feet-height+bob
    lean=12 if moving else (-9 if state==E.HITSTUN else 0)
    if state in (E.JUMP,E.FALL,E.ATTACK_AIR):top+=8
    head=(int(cx+lean),int(top+18))
    shoulder=(cx+lean,top+48);waist=(cx,top+87)
    stride=math.sin(frame*math.pi/4)*(22 if moving else 4)
    if state==E.DASH:stride=33;top+=15
    def poly(color,pts,width=0):pygame.draw.polygon(s,color,pts,width)
    def line(color,a,b,width=2):pygame.draw.line(s,color,a,b,width)
    def circle(color,pos,r,width=0):pygame.draw.circle(s,color,(int(pos[0]),int(pos[1])),r,width)
    if released:
        for i in range(5):
            x=cx-58+i*28;dy=math.sin(frame+i)*12
            poly((*accent,65),[(x,feet),(x-10,top+45+dy),(cx,top-26),(x+19,feet)])
        pygame.draw.ellipse(s,(*accent,100),(cx-70,top-23,140,height+40),2)
    # Trailing fabric, distinct for each silhouette.
    if identity in (0,2):
        poly(dark,[(cx-18,top+44),(cx-68-(20 if moving else 0),top+91),(cx-41,feet-8),(cx+7,top+85)])
        poly(accent,[(cx-20,top+42),(cx-73,top+56+stride/3),(cx-55,top+65+stride/3),(cx-14,top+51)])
    legw=19 if identity in (1,3) else 13
    for side in (-1,1):
        hip=(cx+side*11,top+84);knee=(cx+side*14+side*stride*.6,feet-33);foot=(cx+side*19+side*stride,feet-3)
        line(ink,hip,knee,legw+5);line(ink,knee,foot,legw+5)
        line(dark,hip,knee,legw);line(dark,knee,foot,legw)
        line(white if identity==2 else (75,79,90),(foot[0]-6,foot[1]),(foot[0]+14,foot[1]),8)
    breadth=[24,39,18,32][identity]
    poly(ink,[(shoulder[0]-breadth-3,top+35),(shoulder[0]+breadth+3,top+38),(cx+25,top+94),(cx-29,top+94)])
    poly(dark,[(shoulder[0]-breadth,top+38),(shoulder[0]+breadth,top+40),(cx+22,top+91),(cx-25,top+91)])
    if identity==0:
        poly(white,[(cx-19+lean,top+38),(cx+2,top+75),(cx+11+lean,top+40),(cx+20+lean,top+44),(cx+2,top+89)])
        poly(dark,[(cx-24,top+86),(cx+23,top+86),(cx+34,feet-17),(cx-42,feet-17)])
        line(accent,(cx-19,top+88),(cx+24,top+88),7)
    elif identity==1:
        poly((142,98,91),[(cx-29,top+40),(cx+28,top+40),(cx+18,top+83),(cx-21,top+83)])
        for i in (-1,1):
            poly(white,[(cx+i*23,top+37),(cx+i*53,top+27),(cx+i*45,top+64),(cx+i*28,top+58)])
        line(accent,(cx-10,top+46),(cx+8,top+75),4)
        poly(ink,[(cx-29,top+87),(cx+27,top+87),(cx+40,feet-28),(cx-43,feet-28)])
        for i in range(3):line(accent,(cx-21+i*20,top+92),(cx-28+i*26,feet-29),3)
    elif identity==2:
        poly(white,[(cx-19+lean,top+40),(cx+16+lean,top+40),(cx+24,top+100),(cx+2,top+82),(cx-25,top+110)])
        line(accent,(cx+lean,top+44),(cx+5,top+85),6)
        poly(accent,[(cx-11,top+82),(cx+14,top+82),(cx+13,top+90),(cx-12,top+90)])
    else:
        for yy,ww in [(43,34),(61,30),(79,25)]:
            poly((88,85,114),[(cx-ww,top+yy),(cx+ww,top+yy),(cx+ww-5,top+yy+15),(cx,top+yy+21),(cx-ww+5,top+yy+15)])
            line(accent,(cx-ww+4,top+yy+2),(cx+ww-4,top+yy+2),2)
        poly(dark,[(cx-28,top+91),(cx+28,top+91),(cx+39,feet-10),(cx-34,feet-10)])
    # Neck, face, original hair / horn / helmet designs.
    line(skin,(head[0],head[1]+10),(head[0],head[1]+24),12)
    circle(ink,head,18);circle(skin,head,15)
    if identity==0:
        poly((207,219,223),[(head[0]-19,head[1]),(head[0]-17,head[1]-20),(head[0]-7,head[1]-14),(head[0]-2,head[1]-28),(head[0]+7,head[1]-16),(head[0]+21,head[1]-23),(head[0]+14,head[1]-2),(head[0]+2,head[1]-10)])
    elif identity==1:
        poly(white,[(head[0]-17,head[1]-7),(head[0]-29,head[1]-29),(head[0]-13,head[1]-18),(head[0],head[1]-16),(head[0]+14,head[1]-21),(head[0]+30,head[1]-35),(head[0]+22,head[1]-7)])
        poly(white,[(head[0]-12,head[1]+4),(head[0]+15,head[1]+1),(head[0]+12,head[1]+16),(head[0]-7,head[1]+15)])
        for i in range(3):line(ink,(head[0]+i*5,head[1]+7),(head[0]+i*5,head[1]+14))
    elif identity==2:
        poly((34,56,57),[(head[0]-20,head[1]+8),(head[0]-18,head[1]-17),(head[0]+4,head[1]-24),(head[0]+21,head[1]-11),(head[0]+8,head[1]-3),(head[0]-5,head[1]-8)])
        line(accent,(head[0]-14,head[1]-12),(head[0]+10,head[1]-16),3)
    else:
        poly((115,115,136),[(head[0]-19,head[1]+11),(head[0]-18,head[1]-17),(head[0]+3,head[1]-26),(head[0]+20,head[1]-13),(head[0]+17,head[1]+15),(head[0]+2,head[1]+19)])
        line(ink,(head[0]-8,head[1]),(head[0]+17,head[1]),6)
    line(accent if released or identity==3 else ink,(head[0]+4,head[1]),(head[0]+13,head[1]-1),3)
    hand=(cx+44,top+70)
    if attack:hand=(cx+75+math.sin(frame*.7)*15,top+51)
    if guard:hand=(cx+35,top+35)
    if state==E.VICTORY:hand=(cx+28,top-10)
    if state==E.RELEASE:hand=(cx+64,top+29)
    if state==E.GRAB:hand=(cx+67,top+61)
    if state==E.ATTACK_HEAVY:hand=(cx+45+frame*5,top+23+frame*6)
    if state==E.ATTACK_AIR:hand=(cx+55,top+92)
    line(ink,(shoulder[0]+breadth-2,top+45),hand,18 if identity in (1,3) else 13)
    line(dark,(shoulder[0]+breadth-2,top+45),hand,12)
    circle(skin,hand,7 if identity!=1 else 12)
    if identity==0:
        end=(hand[0]+67,hand[1]+(-38 if attack else 49))
        line(ink,hand,end,8);line(white,hand,end,4)
        line(accent,(hand[0]-5,hand[1]-8),(hand[0]+9,hand[1]+7),5)
    elif identity==1:
        for k in range(3):line(white,(hand[0]+5,hand[1]-7+k*7),(hand[0]+29,hand[1]-15+k*10),4)
    elif identity==2:
        pygame.draw.arc(s,accent,(hand[0]-10,hand[1]-45,49,90),-1.4,1.4,4)
        line(white,(hand[0]+17,hand[1]-43),(hand[0]+17,hand[1]+43),1)
        if attack:line(accent,(hand[0]-14,hand[1]),(hand[0]+60,hand[1]),3)
    else:
        hx,hy=hand
        poly(ink,[(hx-15,hy-29),(hx+26,hy-25),(hx+30,hy+27),(hx+4,hy+51),(hx-18,hy+24)])
        poly((105,104,132),[(hx-10,hy-23),(hx+20,hy-20),(hx+24,hy+23),(hx+4,hy+43),(hx-12,hy+20)])
        line(accent,(hx+3,hy-16),(hx+7,hy+32),3)
    if attack and frame in (1,2,3,4):
        pygame.draw.arc(s,(*accent,205),(cx+20,top+7,129,135),-.9,1.5,5)
        pygame.draw.arc(s,(*white,180),(cx+27,top+15,119,121),-.7,1.2,2)
    if guard:
        pygame.draw.arc(s,(*accent,200),(cx+18,top-3,89,height+14),-1.4,1.4,4)
    if state in (E.KNOCKDOWN,E.DEFEAT):
        s=pygame.transform.rotate(s,-76)
        result=pygame.Surface((300,230),pygame.SRCALPHA)
        result.blit(s,(150-s.get_width()//2,230-s.get_height()+38));s=result
    if state==E.HITSTUN:
        tint=pygame.Surface(s.get_size(),pygame.SRCALPHA);tint.fill((85,50,45,0));s.blit(tint,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
    if direction<0:s=pygame.transform.flip(s,True,False)
    return s


def draw_fighter(s,p):
    pygame.draw.ellipse(s,(8,12,23),(p.rect.centerx-47,572,94,15))
    img=sprite(p.identidade,p.estado_atual,ANIMATION.frame(p.anim_time),p.forma_liberada,p.direcao)
    s.blit(img,(p.rect.centerx-140-(20 if p.direcao<0 else 0),p.rect.bottom-211))

@lru_cache(maxsize=32)
def portrait(identity,size=100):
    img=sprite(identity,E.IDLE,0,False,1)
    top=211-[142,166,138,151][identity]
    crop=img.subsurface((99,max(0,top-25),93,103))
    return pygame.transform.smoothscale(crop,(size,size))
