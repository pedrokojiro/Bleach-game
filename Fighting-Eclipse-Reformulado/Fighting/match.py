"""Match, round lifecycle and simultaneous melee resolution."""
from seu_personagem import ELENCO
from states import Fluxo as F, Estado as E
from constants import ROUND_SECONDS
from projetil import Projetil
from effects import Effects
from ai import BotIA
from animation import sprite,ANIMATION

class Match:
    def __init__(self,selections=(0,1),mode='PVE',difficulty=1):
        self.players=[ELENCO[selections[0]](540),ELENCO[selections[1]](1040)]
        self.mode=mode;self.difficulty=difficulty
        self.bot=BotIA(self.players[1],difficulty)
        self.wins=[0,0];self.round=1;self.winner=None
        self.reset_round()

    def reset_round(self):
        self.players[0].resetar_round(540,True);self.players[1].resetar_round(1040,False)
        self.projectiles=[];self.effects=Effects()
        self.time=float(ROUND_SECONDS);self.phase=F.INTRO;self.phase_time=2.4
        self.result='';self.trail_time=0.
        self.bot.timer=0;self.bot.sequence=0

    def resolve_attacks(self):
        hits=[]
        for p,other in ((self.players[0],self.players[1]),(self.players[1],self.players[0])):
            move=p.acao
            if not move or not move.startup<=p.tempo_acao<move.startup+move.active:continue
            if move.tipo in ('projectile','wave','trap'):
                if not p.emitiu:
                    self.projectiles.append(Projetil(p,move));p.emitiu=True
            elif move.tipo=='barrier':
                if not p.emitiu:p.barreira=2.5;p.emitiu=True;p.criar_efeito('parry')
            elif not p.acertou and p.obter_hitbox().colliderect(other.obter_hurtbox()):
                if move.tipo!='grab' or (p.no_chao and other.no_chao):hits.append((p,other,move))
        for p,other,move in hits:
            result=other.receber_dano(move,p)
            if result!='miss':p.acertou=True
        for q in self.projectiles:
            for p in self.players:q.checar_colisao(p)
        self.projectiles=[q for q in self.projectiles if q.ativo]

    def separate(self):
        a,b=self.players
        if not a.obter_pushbox().colliderect(b.obter_pushbox()):return
        left,right=(a,b) if a.rect.centerx<b.rect.centerx else (b,a)
        overlap=left.obter_pushbox().right-right.obter_pushbox().left
        left.x-=overlap/2;right.x+=overlap/2
        left.sync_rect();right.sync_rect()
        # Transfer blocked displacement to the other body at walls.
        overlap=left.obter_pushbox().right-right.obter_pushbox().left
        if overlap>0:
            if left.x<=24:right.x+=overlap
            else:left.x-=overlap
            left.sync_rect();right.sync_rect()

    def finish_round(self):
        a,b=self.players
        ratio=[a.vida/a.vida_maxima,b.vida/b.vida_maxima]
        if abs(ratio[0]-ratio[1])<1e-8:
            self.result='EMPATE — ROUND REPETIDO'
        else:
            winner=int(ratio[1]>ratio[0]);self.wins[winner]+=1
            self.players[winner].vitorias+=1;self.players[1-winner].derrotas+=1
            self.players[winner].estado(E.VICTORY)
            self.result='K.O.' if min(a.vida,b.vida)<=0 else 'TEMPO ESGOTADO'
            if self.wins[winner]>=2:self.winner=winner
        self.phase=F.KO;self.phase_time=2.5
        for p in self.players:p.buffer.clear();p.movimento=0

    def update(self,dt,inputs=None):
        self.effects.update(dt)
        if self.phase==F.INTRO:
            self.phase_time-=dt
            if self.phase_time<=0:self.phase=F.FIGHT
            return
        if self.phase==F.KO:
            self.phase_time-=dt
            if self.phase_time<=0:
                if self.winner is not None:self.phase=F.VICTORY
                else:
                    if not self.result.startswith('EMPATE'):self.round+=1
                    self.reset_round()
            return
        if self.phase!=F.FIGHT:return
        if self.effects.hitstop>0:self.effects.hitstop=max(0,self.effects.hitstop-dt);return
        if inputs:
            inputs.apply(0,self.players[0])
            if self.mode=='PVP':inputs.apply(1,self.players[1])
        if self.mode=='PVE':self.bot.process(dt,self.players[0],self.projectiles)
        a,b=self.players
        a.atualizar(dt,b);b.atualizar(dt,a)
        self.separate()
        for q in self.projectiles:q.atualizar(dt)
        self.resolve_attacks()
        self.trail_time-=dt
        if self.trail_time<=0:
            self.trail_time=.045
            for p in self.players:
                if p.estado_atual==E.DASH or (p.acao and p.acao.tipo=='rush'):
                    img=sprite(p.identidade,p.estado_atual,ANIMATION.frame(p.anim_time),p.forma_liberada,p.direcao).copy()
                    self.effects.ghosts.append([img,(p.rect.centerx-140-(20 if p.direcao<0 else 0),p.rect.bottom-211),.2])
                elif p.estado_atual==E.RUN:p.criar_efeito('dash')
        self.time=max(0,self.time-dt)
        if min(a.vida,b.vida)<=0 or self.time<=0:self.finish_round()

    def collect_events(self):
        events=[]
        for p in self.players:
            events.extend(p.eventos);p.eventos.clear()
        for kind,pos,color in events:self.effects.emit(kind,pos,color)
        return events
