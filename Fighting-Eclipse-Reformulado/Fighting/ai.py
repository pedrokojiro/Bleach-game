"""Reaction-limited tactical controller; difficulty never modifies damage."""
from states import Estado as E

class BotIA:
    def __init__(self,personagem,dificuldade=1):
        self.personagem=personagem;self.dificuldade=dificuldade
        self.timer=0.;self.sequence=0
    def process(self,dt,adversario,projeteis=()):
        self.timer-=dt
        if self.timer>0:return
        self.timer=[.32,.19,.105][self.dificuldade]
        p=self.personagem
        distance=abs(p.rect.centerx-adversario.rect.centerx)
        direction=1 if adversario.rect.centerx>p.rect.centerx else -1
        p.defender(False);p.correndo=False
        ideal=330 if p.identidade==2 else 88
        incoming=any(q.dono is not p and abs(q.x-p.rect.centerx)<220 and (p.rect.centerx-q.x)*q.vx>0 for q in projeteis)
        threat=adversario.acao and distance<adversario.acao.alcance+100
        if incoming:
            p.mover(0)
            if self.dificuldade>0:p.comando('jump')
            else:p.defender(True)
            return
        if threat and not p.acao:
            p.mover(0);p.defender(True)
            if self.dificuldade==2 and p.stamina>35 and self.sequence%3==0:p.comando('parry')
            self.sequence+=1
            return
        if p.reiatsu>=75 and p.vida<p.vida_maxima*.55 and not p.forma_liberada:
            p.comando('release');return
        if p.forma_liberada and p.reiatsu>=15 and distance<280 and not p.cooldowns.get('exclusive',0):
            p.comando('exclusive');return
        if p.acao and p.acertou and p.contador_combo<self.dificuldade+2:
            p.comando('heavy' if p.contador_combo>=2 else 'light');return
        if distance>ideal+35:p.mover(direction)
        elif p.identidade==2 and distance<ideal-75:p.mover(-direction)
        else:p.mover(0)
        if distance>420 and p.identidade!=2 and p.stamina>50:p.comando('dash')
        if p.reiatsu>=p.moves['special'].custo and distance<650 and not p.cooldowns.get('special',0):
            if p.identidade in (0,2) and distance>160:p.comando('special');return
            if p.identidade in (1,3) and distance<190:p.comando('special');return
        if distance<130:
            self.sequence+=1
            if adversario.estado_atual==E.BLOCK and distance<65:p.comando('grab')
            elif not adversario.no_chao:p.comando('heavy')
            elif adversario.acao and adversario.tempo_acao>adversario.acao.startup+adversario.acao.active:p.comando('heavy')
            else:p.comando('heavy' if self.sequence%4==0 else 'light')
