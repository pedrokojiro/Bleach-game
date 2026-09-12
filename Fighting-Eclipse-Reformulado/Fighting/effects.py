from dataclasses import dataclass
import random
import pygame

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    total: float
    size: float
    color: tuple
    gravity: float = 500

class Effects:
    def __init__(self):
        self.particles=[];self.rings=[];self.ghosts=[]
        self.flash=0.;self.shake=0.;self.hitstop=0.
        self.layer=pygame.Surface((1700,720),pygame.SRCALPHA)

    def emit(self,kind,pos,color):
        heavy=kind in ('heavy','ko','release','special')
        count=48 if kind in ('ko','release') else (23 if heavy else 12)
        if kind in ('jump','land','dash'):pos=(pos[0],578);color=(135,150,164);count=8
        for _ in range(count):
            life=random.uniform(.16,.50)
            self.particles.append(Particle(*pos,random.uniform(-320,320),random.uniform(-280,90),life,life,random.uniform(2,5),color))
        self.particles=self.particles[-400:]
        if kind in ('parry','release','special','ko'):self.rings.append([*pos,5.,.5,color])
        if kind in ('hit','heavy','parry','ko'):
            self.hitstop=max(self.hitstop,.09 if heavy else .045)
            self.shake=max(self.shake,11 if heavy else 4)
            self.flash=.13 if heavy else .04
        if kind=='release':self.flash=.20;self.shake=8

    def update(self,dt):
        self.flash=max(0,self.flash-dt)
        self.shake=max(0,self.shake-dt*30)
        for p in self.particles:
            p.life-=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=p.gravity*dt
        self.particles=[p for p in self.particles if p.life>0]
        for r in self.rings:r[2]+=dt*260;r[3]-=dt
        self.rings=[r for r in self.rings if r[3]>0]
        for g in self.ghosts:g[2]-=dt
        self.ghosts=[g for g in self.ghosts if g[2]>0]

    def draw(self,s):
        self.layer.fill((0,0,0,0))
        for img,pos,life in self.ghosts:
            img.set_alpha(int(100*life/.2));self.layer.blit(img,pos)
        for p in self.particles:
            pygame.draw.circle(self.layer,(*p.color,int(255*p.life/p.total)),(int(p.x),int(p.y)),max(1,int(p.size*p.life/p.total)))
        for x,y,r,life,col in self.rings:pygame.draw.circle(self.layer,(*col,int(210*life/.5)),(int(x),int(y)),int(r),2)
        s.blit(self.layer,(0,0))
