"""Projectiles use owner filtering, fixed-step motion and a single-hit lifetime."""
import pygame
from constants import ARENA_WIDTH

class Projetil:
    def __init__(self,dono,move,tipo=None):
        self.dono,self.move = dono,move
        self.tipo = tipo or move.tipo
        self.x = float(dono.rect.centerx+dono.direcao*48)
        self.y = float(dono.rect.centery)
        self.vx = dono.direcao*dono.kit.projectile_speed
        self.vy = 240 if not dono.no_chao and dono.kit.aerial_projectile else 0
        self.vida = 1.8
        self.ativo = True
        self.direcao = dono.direcao
        self.cor = dono.cor_base
        if self.tipo=='wave':self.y=555;self.vx=dono.direcao*420
        if self.tipo=='trap':self.x+=dono.direcao*180;self.y=551;self.vx=0;self.vida=3
        self.rect=pygame.Rect(self.x-20,self.y-12,40,24)

    def atualizar(self,dt):
        self.x+=self.vx*dt;self.y+=self.vy*dt;self.vida-=dt
        self.rect.center=round(self.x),round(self.y)
        if self.vida<=0 or not -80<self.x<ARENA_WIDTH+80 or self.y>600:self.ativo=False

    def checar_colisao(self,alvo):
        if not self.ativo or alvo is self.dono or not self.rect.colliderect(alvo.obter_hurtbox()):return False
        reflected = alvo.form and alvo.form.reflect and alvo.barreira>0
        if reflected:
            self.dono=alvo;self.vx=-self.vx;self.direcao=-self.direcao
            self.x+=self.direcao*70;alvo.anunciar('REFLEXÃO')
            self.rect.center=round(self.x),round(self.y)
            self.cor=alvo.cor_base
            return True
        result=alvo.receber_dano(self.move,self.dono,True)
        if result!='miss':self.ativo=False
        return result!='miss'

    def desenhar(self,s):
        x,y=int(self.x),int(self.y)
        if self.tipo=='trap':
            pygame.draw.circle(s,self.cor,(x,y),22,2)
            pygame.draw.polygon(s,self.cor,[(x,y-30),(x+13,y),(x,y+14),(x-13,y)],2)
        else:
            if self.dono.kit.visual=='beast':
                pygame.draw.circle(s,self.cor,(x,y),19)
                pygame.draw.circle(s,(255,230,220),(x,y),9)
                return
            if self.dono.kit.visual=='human':
                pygame.draw.rect(s,self.cor,(x-9,y-17,18,34),2)
                return
            pygame.draw.line(s,self.cor,(x-self.direcao*65,y),(x,y),7)
            pygame.draw.polygon(s,(245,250,255),[(x+self.direcao*24,y),(x-self.direcao*12,y-10),(x,y),(x-self.direcao*12,y+10)])
