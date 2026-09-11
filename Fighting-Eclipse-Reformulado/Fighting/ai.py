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
        ranged=p.kit.archetype=='distância'
        ideal=330 if ranged else 88
        incoming=any(q.dono is not p and abs(q.x-p.rect.centerx)<220 and (p.rect.centerx-q.x)*q.vx>0 for q in projeteis)
        threat=adversario.acao and distance<adversario.acao.alcance+100
        if incoming:
            p.mover(0)
            if self.dificuldade>0:p.comando('jump')
            else:p.defender(True)
            return
        if threat and not p.acao:
            defensive=p.moves['special2']
            if defensive.tipo=='barrier' and not p.barreira and p.reiatsu>=defensive.custo and not p.cooldowns.get('special2',0):
                p.defender(False);p.comando('special2');return
            p.mover(0);p.defender(True)
            if self.dificuldade==2 and p.stamina>35 and self.sequence%3==0:p.comando('parry')
            self.sequence+=1
            return
        next_form=p.form_index+1
        if next_form<len(p.kit.forms) and p.reiatsu>=p.kit.forms[next_form].cost and p.vida<p.vida_maxima*.65:
            p.comando('release');return
        if p.forma_liberada and p.reiatsu>=15 and distance<280 and not p.cooldowns.get('exclusive',0):
            p.comando('exclusive');return
        if p.acao and p.acertou and p.contador_combo<self.dificuldade+2:
            p.comando('heavy' if p.contador_combo>=2 else 'light');return
        if distance>ideal+35:p.mover(direction)
        elif ranged and distance<ideal-75:p.mover(-direction)
        else:p.mover(0)
        if distance>420 and not ranged and p.stamina>50:p.comando('dash')
        if p.reiatsu>=p.moves['special'].custo and distance<650 and not p.cooldowns.get('special',0):
            if p.moves['special'].tipo=='projectile' and distance>160:p.comando('special');return
            if p.moves['special'].tipo!='projectile' and distance<190:p.comando('special');return
        secondary=p.moves['special2']
        if p.reiatsu>=secondary.custo and not p.cooldowns.get('special2',0):
            if (secondary.tipo=='barrier' and threat) or (secondary.tipo=='trap' and 160<distance<380) or (secondary.tipo=='wave' and distance<350):
                p.comando('special2');return
        if p.reiatsu>=75 and distance<280 and adversario.acao:
            p.comando('ultimate');return
        if distance<130:
            self.sequence+=1
            if adversario.estado_atual==E.BLOCK and distance<65:p.comando('grab')
            elif not adversario.no_chao:p.comando('heavy')
            elif adversario.acao and adversario.tempo_acao>adversario.acao.startup+adversario.acao.active:p.comando('heavy')
            else:p.comando('heavy' if self.sequence%4==0 else 'light')
