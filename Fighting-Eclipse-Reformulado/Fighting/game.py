"""Application loop. Run `python game.py`; F1 shows the complete controls."""
import argparse
import pygame
from constants import *
from states import Fluxo as F, Estado as E
from arena import ArenaVisual,ARENAS
from camera import Camera
from audio import Audio
from input_manager import InputManager
from match import Match
from hud import draw_hud,draw_select,draw_title,controls,text,panel
from seu_personagem import PERFIS
import settings

class Game:
    def __init__(self,settings_path=settings.DEFAULT_PATH):
        pygame.mixer.pre_init(44100,-16,2,512)
        pygame.init()
        self.screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE)
        pygame.display.set_caption('Bleach — Spiritual Crossroads')
        self.canvas=pygame.Surface((1280,720));self.scene=pygame.Surface((1280,720))
        self.world=pygame.Surface((ARENA_WIDTH,720),pygame.SRCALPHA)
        self.overlay=pygame.Surface((1280,720),pygame.SRCALPHA)
        self.settings_path=settings_path;self.config=settings.load(settings_path)
        self.arena_index=0
        self.arena=ArenaVisual();self.camera=Camera();self.audio=Audio();self.inputs=InputManager(self.config['keys'])
        self.camera.shake_enabled=self.config['shake']
        self.audio.muted=self.config['muted'];self.audio.set_volume(self.config['volume'])
        self.remapping=False;self.remap_player=0;self.remap_action=0;self.capture=False
        self.phase=F.TITLE;self.match=None;self.selected=[0,1];self.confirmed=[False,False]
        self.mode='PVE';self.difficulty=1;self.running=True;self.help=False;self.paused=False;self.fullscreen=False
        self.audio.music('menu')
        self.status='';self.status_time=0.

    def start(self):
        self.match=Match(self.selected,self.mode,self.difficulty)
        self.phase=F.FIGHT;self.inputs.clear();self.paused=False
        self.camera=Camera();self.camera.shake_enabled=self.config['shake'];self.audio.music('arena')

    def save_settings(self):
        self.config.update(volume=self.audio.volume,muted=self.audio.muted,shake=self.camera.shake_enabled,keys=self.inputs.maps)
        try:settings.save(self.config,self.settings_path)
        except OSError:self.status='Não foi possível salvar configurações';self.status_time=4

    def remap_event(self,e):
        actions=list(self.inputs.maps[self.remap_player])
        if self.capture:
            if e.key==pygame.K_ESCAPE:self.capture=False;return
            reserved={pygame.K_F1,pygame.K_F2,pygame.K_F3,pygame.K_F4,pygame.K_F5,pygame.K_F6,pygame.K_F7,pygame.K_F8,pygame.K_F9,pygame.K_F11,pygame.K_RETURN,pygame.K_TAB,pygame.K_BACKSPACE,pygame.K_MINUS,pygame.K_EQUALS,pygame.K_PLUS}
            if e.key in reserved:return
            mapping=self.inputs.maps[self.remap_player];action=actions[self.remap_action]
            old=mapping[action]
            for other,key in mapping.items():
                if key==e.key:mapping[other]=old;break
            mapping[action]=e.key;self.capture=False;self.inputs.clear();self.save_settings()
        elif e.key in (pygame.K_ESCAPE,pygame.K_F3):self.remapping=False;self.inputs.clear()
        elif e.key==pygame.K_TAB:self.remap_player=1-self.remap_player
        elif e.key in (pygame.K_UP,pygame.K_DOWN):self.remap_action=(self.remap_action+(1 if e.key==pygame.K_DOWN else -1))%len(actions)
        elif e.key==pygame.K_RETURN:self.capture=True

    def events(self,events):
        for e in events:
            if e.type==pygame.QUIT:self.running=False
            if e.type==pygame.WINDOWFOCUSLOST:
                self.inputs.clear()
                if self.phase==F.FIGHT:self.paused=True
            if e.type in (pygame.JOYDEVICEADDED,pygame.JOYDEVICEREMOVED):self.inputs.event(e)
            if e.type==pygame.JOYBUTTONDOWN and e.button==7:
                e=pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE if self.phase==F.FIGHT else pygame.K_RETURN)
            elif self.phase==F.SELECT and e.type==pygame.JOYBUTTONDOWN:
                device=self.inputs.devices.get(e.instance_id)
                if device:
                    i=device[0]
                    if e.button==0:self.confirmed[i]=not self.confirmed[i]
                    if e.button in (4,5):self.selected[i]=(self.selected[i]+(1 if e.button==5 else -1))%len(PERFIS);self.confirmed[i]=False
                continue
            if self.remapping:
                if e.type==pygame.KEYDOWN:self.remap_event(e)
                continue
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
            elif e.key==pygame.K_F3:self.remapping=True;self.capture=False;self.inputs.clear()
            elif self.phase==F.FIGHT and self.mode=='TREINO' and e.key==pygame.K_F5:
                self.match.reset_training();self.inputs.clear();self.status='POSIÇÕES REINICIADAS';self.status_time=2
            elif self.phase==F.FIGHT and self.mode=='TREINO' and e.key==pygame.K_F6:
                value=self.match.cycle_training_dummy();self.inputs.clear();self.status='BONECO: '+value;self.status_time=2
            elif self.phase==F.FIGHT and self.mode=='TREINO' and e.key==pygame.K_F7:
                self.match.training_resources=not self.match.training_resources
                self.status='RECURSOS INFINITOS '+('LIGADOS' if self.match.training_resources else 'DESLIGADOS');self.status_time=2
            elif e.key==pygame.K_F8:
                self.camera.shake_enabled=not self.camera.shake_enabled
                self.status='TREMOR '+('LIGADO' if self.camera.shake_enabled else 'DESLIGADO');self.status_time=2
                self.save_settings()
            elif e.key==pygame.K_F9:
                self.audio.toggle();self.status='SOM '+('DESLIGADO' if self.audio.muted else 'LIGADO');self.status_time=2
                self.save_settings()
            elif e.key in (pygame.K_MINUS,pygame.K_EQUALS,pygame.K_PLUS):
                self.audio.set_volume(self.audio.volume+(-.1 if e.key==pygame.K_MINUS else .1))
                self.status=f'VOLUME {self.audio.volume:.0%}';self.status_time=2
                self.save_settings()
            elif self.help:continue
            elif self.phase==F.TITLE:
                if e.key==pygame.K_RETURN:self.phase=F.SELECT;self.audio.play('confirm')
                elif e.key==pygame.K_ESCAPE:self.running=False
            elif self.phase==F.SELECT:
                if e.key==pygame.K_ESCAPE:self.phase=F.TITLE
                if e.key==pygame.K_TAB:
                    modes=('PVE','PVP','TREINO');self.mode=modes[(modes.index(self.mode)+1)%len(modes)]
                if e.key==pygame.K_F2:self.difficulty=(self.difficulty+1)%3
                if e.key==pygame.K_F4:
                    self.arena_index=(self.arena_index+1)%len(ARENAS)
                    self.arena=ArenaVisual(list(ARENAS)[self.arena_index])
                for i,left,right,confirm in [(0,pygame.K_a,pygame.K_d,pygame.K_f),(1,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_j)]:
                    if e.key in (left,right):self.selected[i]=(self.selected[i]+(1 if e.key==right else -1))%len(PERFIS);self.confirmed[i]=False
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
        if self.paused or self.help or self.remapping:return
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
            else:draw_select(self.canvas,self.selected,self.confirmed,self.mode,self.difficulty,self.arena.name)
        if self.help:controls(self.canvas,self.inputs.maps)
        if self.remapping:
            from hud import ACTION_NAMES
            panel(self.canvas,(290,30,700,650),(10,18,31),GOLD)
            text(self.canvas,f'CONTROLES / JOGADOR {self.remap_player+1}',(640,62),25,GOLD,True)
            for j,(action,key) in enumerate(self.inputs.maps[self.remap_player].items()):
                color=GOLD if j==self.remap_action else WHITE
                text(self.canvas,ACTION_NAMES.get(action,action),(330,107+j*31),17,color)
                text(self.canvas,pygame.key.name(key).upper(),(770,107+j*31),17,color)
            text(self.canvas,'PRESSIONE NOVA TECLA / ESC CANCELA' if self.capture else '↑ ↓ ação / TAB jogador / ENTER editar / ESC sair',(640,617),16,GOLD,True)
            text(self.canvas,'Teclas de menu são reservadas. Conflitos locais trocam de lugar.',(640,650),13,WHITE,True)
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
