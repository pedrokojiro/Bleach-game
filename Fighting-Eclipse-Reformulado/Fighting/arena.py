"""Layered original moonlit courtyard; static geometry is cached."""
import math
import random
import pygame
from constants import *

ARENAS={'soul_society':'Soul Society', 'karakura':'Karakura', 'hueco_mundo':'Hueco Mundo'}

class ArenaVisual:
    def __init__(self,identifier='soul_society'):
        if identifier not in ARENAS:raise ValueError(identifier)
        self.identifier=identifier
        self.name=ARENAS[identifier]
        self.time=0
        self.sky=pygame.Surface((1280,720))
        for y in range(720):
            t=min(1,y/580)
            pygame.draw.line(self.sky,(int(9+15*t),int(17+22*t),int(35+28*t)),(0,y),(1280,y))
        rng=random.Random(17)
        for _ in range(140):
            x,y=rng.randrange(1280),rng.randrange(450)
            pygame.draw.circle(self.sky,(80,111,134),(x,y),rng.choice([1,1,2]))
        glow=pygame.Surface((320,320),pygame.SRCALPHA)
        for r in range(155,69,-5):pygame.draw.circle(glow,(104,166,191,2+(155-r)//12),(160,160),r)
        self.sky.blit(glow,(760,8))
        pygame.draw.circle(self.sky,(211,224,218),(920,168),68)
        pygame.draw.circle(self.sky,(186,207,206),(905,155),14)
        pygame.draw.circle(self.sky,(195,215,213),(940,187),20)
        self.world=pygame.Surface((ARENA_WIDTH,720),pygame.SRCALPHA)
        for x in (80,390,1240,1570):
            pygame.draw.rect(self.world,(21,31,46),(x,330,34,250))
            pygame.draw.rect(self.world,(41,57,68),(x,330,7,250))
            pygame.draw.polygon(self.world,(11,23,38),[(x-52,339),(x+17,291),(x+93,339)])
            pygame.draw.line(self.world,(70,89,98),(x-52,339),(x+93,339),3)
        for x in range(0,ARENA_WIDTH,105):
            pygame.draw.rect(self.world,(32,44,57),(x,499,97,80))
            pygame.draw.line(self.world,(74,90,95),(x,500),(x+97,500),2)
            pygame.draw.rect(self.world,(12,24,38),(x+12,514,70,35),2)
        pygame.draw.rect(self.world,(36,46,57),(0,580,ARENA_WIDTH,140))
        pygame.draw.line(self.world,(150,160,156),(0,581),(ARENA_WIDTH,581),3)
        for x in range(-200,ARENA_WIDTH+200,100):
            pygame.draw.line(self.world,(17,28,42),(x,584),(x-170,720),3)
        for y in (607,648,704):pygame.draw.line(self.world,(20,32,44),(0,y),(ARENA_WIDTH,y),3)
        for _ in range(90):
            x,y=rng.randrange(ARENA_WIDTH),rng.randrange(590,720)
            pygame.draw.line(self.world,(47,57,64),(x,y),(x+rng.randrange(8,34),y+2),1)
        self.fog=pygame.Surface((1280,720),pygame.SRCALPHA)
        for y in range(420,578,4):
            pygame.draw.line(self.fog,(109,145,159,max(0,18-int(abs(y-510)/5))),(0,y),(1280,y),4)
        self.vignette=pygame.Surface((1280,720),pygame.SRCALPHA)
        for i in range(35):pygame.draw.rect(self.vignette,(0,5,15,max(0,38-i)),(i*4,i*3,1280-i*8,720-i*6),4)
        if identifier!='soul_society':
            self.world.fill((0,0,0,0))
            if identifier=='karakura':
                for x in range(0,ARENA_WIDTH,160):
                    height=rng.randrange(130,290)
                    pygame.draw.rect(self.world,(25,34,55),(x,580-height,145,height))
                    for xx in range(x+15,x+135,26):
                        for yy in range(600-height,540,35):
                            pygame.draw.rect(self.world,(194,163,94),(xx,yy,10,16))
                pygame.draw.rect(self.world,(33,38,49),(0,580,ARENA_WIDTH,140))
                pygame.draw.line(self.world,(208,197,162),(0,585),(ARENA_WIDTH,585),4)
                for x in range(0,ARENA_WIDTH,140):pygame.draw.rect(self.world,(185,180,158),(x,650,75,5))
            else:
                self.sky.fill((8,12,22))
                pygame.draw.circle(self.sky,(226,233,235),(930,125),65)
                pygame.draw.circle(self.sky,(8,12,22),(950,110),57)
                pygame.draw.rect(self.world,(186,195,204),(0,580,ARENA_WIDTH,140))
                for x in range(0,ARENA_WIDTH,220):
                    pygame.draw.polygon(self.world,(109,124,142),[(x,580),(x+35,405),(x+51,570)])
                    pygame.draw.line(self.world,(109,124,142),(x+30,470),(x-35,420),7)
                for y in (615,660,700):pygame.draw.line(self.world,(146,161,179),(0,y),(ARENA_WIDTH,y-10),2)

    def atualizar(self,dt):self.time+=dt

    def desenhar(self,s,camera_x=210):
        s.blit(self.sky,(0,0))
        for layer in range(2 if self.identifier=='soul_society' else 0):
            col=(19+layer*4,30+layer*5,46+layer*6)
            off=-camera_x*(.08+layer*.10)
            for i in range(8):
                x=i*240+off-120;y=370+layer*80
                pygame.draw.polygon(s,col,[(x-150,580),(x+45,y-55),(x+200,580)])
                if layer==1:
                    pygame.draw.rect(s,col,(x,y-60,93,160))
                    for tier in range(3):
                        yy=y-70+tier*34
                        pygame.draw.polygon(s,col,[(x-30,yy+18),(x+47,yy-13),(x+121,yy+18)])
        # Wispy cloud bands slide at different depths.
        for i in range(5):
            x=(i*327+self.time*(4+i))%1550-200
            pygame.draw.line(s,(44,61,77),(x,170+i*42),(x+180,163+i*42),2)
        s.blit(self.world,(-int(camera_x),0))
        s.blit(self.fog,(0,0))
        for i in range(26):
            x=(i*67+math.sin(self.time*.4+i)*35-camera_x*.25)%1280
            y=290+(i*43-self.time*(9+i%4))%290
            pygame.draw.circle(s,(86,140,158),(int(x),int(y)),1)
