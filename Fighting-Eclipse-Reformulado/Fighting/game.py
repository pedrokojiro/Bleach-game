"""Application loop. Run `python game.py`; F1 shows the complete controls."""
import argparse
import pygame
from constants import *
from states import Fluxo as F, Estado as E
from arena import ArenaVisual
from camera import Camera
from audio import Audio
from input_manager import InputManager
from match import Match
from hud import draw_hud,draw_select,draw_title,controls,text,panel

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100,-16,2,512)
        pygame.init()
        self.screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE)
        pygame.display.set_caption('Fighting — Eclipse: Spirit Clash')
        self.canvas=pygame.Surface((1280,720));self.scene=pygame.Surface((1280,720))
        self.world=pygame.Surface((ARENA_WIDTH,720),pygame.SRCALPHA)
        self.overlay=pygame.Surface((1280,720),pygame.SRCALPHA)
        self.arena=ArenaVisual();self.camera=Camera();self.audio=Audio();self.inputs=InputManager()
        self.phase=F.TITLE;self.match=None;self.selected=[0,1];self.confirmed=[False,False]
        self.mode='PVE';self.difficulty=1;self.running=True;self.help=False;self.paused=False;self.fullscreen=False
        self.audio.music('menu')
        self.status='';self.status_time=0.

    def start(self):
        self.match=Match(self.selected,self.mode,self.difficulty)
        self.phase=F.FIGHT;self.inputs.clear();self.paused=False
        self.camera=Camera();self.audio.music('arena')

    def events(self,events):
        for e in events:
            if e.type==pygame.QUIT:self.running=False
            # Only combat receives action edges. Menu keys cannot leak into a round.
            if self.phase==F.FIGHT and self.match.phase==F.FIGHT and not self.paused and not self.help:self.inputs.event(e)
            if e.type==pygame.WINDOWFOCUSLOST:
                self.inputs.clear()
                if self.phase==F.FIGHT:self.paused=True
            if e.type!=pygame.KEYDOWN or getattr(e,'repeat',False):continue
            if e.key==pygame.K_F11:
                self.fullscreen=not self.fullscreen
                self.screen=pygame.display.set_mode((0,0) if self.fullscreen else (1280,720),pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)
            elif e.key==pygame.K_F1:self.help=not self.help;self.inputs.clear()
            elif e.key==pygame.K_F8:
                self.camera.shake_enabled=not self.camera.shake_enabled
                self.status='TREMOR '+('LIGADO' if self.camera.shake_enabled else 'DESLIGADO');self.status_time=2
            elif e.key==pygame.K_F9:
                self.audio.toggle();self.status='SOM '+('DESLIGADO' if self.audio.muted else 'LIGADO');self.status_time=2
            elif e.key in (pygame.K_MINUS,pygame.K_EQUALS,pygame.K_PLUS):
                self.audio.set_volume(self.audio.volume+(-.1 if e.key==pygame.K_MINUS else .1))
                self.status=f'VOLUME {self.audio.volume:.0%}';self.status_time=2
            elif self.help:continue
            elif self.phase==F.TITLE:
                if e.key==pygame.K_RETURN:self.phase=F.SELECT;self.audio.play('confirm')
                elif e.key==pygame.K_ESCAPE:self.running=False
            elif self.phase==F.SELECT:
                if e.key==pygame.K_ESCAPE:self.phase=F.TITLE
                if e.key==pygame.K_TAB:self.mode='PVP' if self.mode=='PVE' else 'PVE'
                if e.key==pygame.K_F2:self.difficulty=(self.difficulty+1)%3
                for i,left,right,confirm in [(0,pygame.K_a,pygame.K_d,pygame.K_f),(1,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_j)]:
                    if e.key in (left,right):self.selected[i]=(self.selected[i]+(1 if e.key==right else -1))%4;self.confirmed[i]=False
                    if e.key==confirm:self.confirmed[i]=not self.confirmed[i];self.audio.play('confirm')
                if e.key==pygame.K_RETURN and all(self.confirmed):self.start()
            elif self.phase==F.FIGHT:
                if self.match.phase==F.VICTORY:
                    if e.key==pygame.K_RETURN:self.start()
                    if e.key==pygame.K_ESCAPE:self.phase=F.SELECT;self.audio.music('menu');self.inputs.clear()
                elif e.key==pygame.K_ESCAPE:self.paused=not self.paused;self.inputs.clear()
                elif self.paused and e.key==pygame.K_BACKSPACE:self.phase=F.SELECT;self.paused=False;self.audio.music('menu');self.inputs.clear()

    def update(self,dt):
        self.status_time=max(0,self.status_time-dt)
        if self.paused or self.help:return
        self.arena.atualizar(dt)
        if self.phase==F.FIGHT:
            prev=self.match.phase
            self.match.update(dt,self.inputs)
            if self.match.phase!=prev:
                self.inputs.clear()
                if self.match.phase==F.VICTORY:self.audio.play('victory')
            for kind,_,_ in self.match.collect_events():self.audio.play(kind)
            self.camera.update(dt,self.match.players)

    def draw(self):
        if self.phase==F.FIGHT:
            m=self.match
            self.arena.desenhar(self.scene,self.camera.x)
            self.world.fill((0,0,0,0))
            for p in m.players:p.desenhar(self.world)
            for q in m.projectiles:q.desenhar(self.world)
            m.effects.draw(self.world)
            self.scene.blit(self.world,(-int(self.camera.x),0))
            self.scene.blit(self.arena.vignette,(0,0))
            self.camera.present(self.scene,self.canvas,m.effects.shake)
            if m.effects.flash>0:
                self.overlay.fill((190,225,245,int(min(.3,m.effects.flash)*200)))
                self.canvas.blit(self.overlay,(0,0))
            draw_hud(self.canvas,m)
            if any(p.estado_atual==E.RELEASE for p in m.players):
                pygame.draw.rect(self.canvas,(5,9,18),(0,0,1280,20))
                pygame.draw.rect(self.canvas,(5,9,18),(0,620,1280,100))
                text(self.canvas,'DESPERTAR ESPIRITUAL',(640,659),25,GOLD,True)
            if self.paused:
                panel(self.canvas,(340,255,600,220),(10,18,31),GOLD)
                text(self.canvas,'PAUSA',(640,315),46,GOLD,True)
                text(self.canvas,'ESC CONTINUAR  /  BACKSPACE SELEÇÃO',(640,395),18,WHITE,True)
        else:
            self.arena.desenhar(self.canvas,210)
            self.overlay.fill((4,10,23,125));self.canvas.blit(self.overlay,(0,0))
            if self.phase==F.TITLE:draw_title(self.canvas,self.arena.time)
            else:draw_select(self.canvas,self.selected,self.confirmed,self.mode,self.difficulty)
        if self.help:controls(self.canvas)
        if self.status_time:text(self.canvas,self.status,(640,660),19,GOLD,True)
        w,h=self.screen.get_size();scale=min(w/1280,h/720)
        size=(max(1,int(1280*scale)),max(1,int(720*scale)))
        self.screen.fill((0,0,0))
        self.screen.blit(pygame.transform.smoothscale(self.canvas,size),((w-size[0])//2,(h-size[1])//2))
        pygame.display.flip()

    def run(self,frames=0):
        clock=pygame.time.Clock();accumulator=0.;n=0
        while self.running:
            dt=min(.1,clock.tick(FPS)/1000)
            self.events(pygame.event.get());accumulator+=dt
            while accumulator>=FIXED_DT:self.update(FIXED_DT);accumulator-=FIXED_DT
            self.draw();n+=1
            if frames and n>=frames:break
        pygame.quit()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke',type=int,default=0,help='Exit after N rendered frames')
    args=parser.parse_args()
    Game().run(args.smoke)
