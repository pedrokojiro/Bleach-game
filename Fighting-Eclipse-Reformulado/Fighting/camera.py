import math
import random
import pygame
from constants import ARENA_WIDTH

class Camera:
    def __init__(self):self.x=210.;self.zoom=1.;self.shake_enabled=True
    def update(self,dt,players):
        target=max(0,min(ARENA_WIDTH-1280,sum(p.rect.centerx for p in players)/2-640))
        self.x+=(target-self.x)*(1-math.exp(-dt*5))
        close=abs(players[0].x-players[1].x)<650
        special=any(p.forma_liberada or (p.acao and p.acao.custo>=70) for p in players)
        z=1.035 if close and special else 1
        self.zoom+=(z-self.zoom)*(1-math.exp(-dt*7))
    def present(self,scene,target,shake):
        if self.zoom>1.001:
            img=pygame.transform.smoothscale(scene,(int(1280*self.zoom),int(720*self.zoom)))
            pos=((1280-img.get_width())//2,(720-img.get_height())//2)
        else:img=scene;pos=(0,0)
        offset=int(shake) if self.shake_enabled else 0
        target.fill((8,14,25))
        target.blit(img,(pos[0]+random.randint(-offset,offset),pos[1]+random.randint(-offset,offset)))
