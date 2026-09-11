"""Fighter simulation independent of presentation and human/AI controllers."""
import pygame
from constants import POSICAO_CHAO, ARENA_WIDTH
from states import Estado as E
from combat import golpes
from catalog import KITS
from dataclasses import replace

FREE = {E.IDLE,E.WALK,E.RUN,E.JUMP,E.FALL,E.EXHAUSTED}
LOCKED = {E.HITSTUN,E.BLOCKSTUN,E.KNOCKDOWN,E.GET_UP,E.RELEASE,E.LAND,E.PARRY,E.DASH}

class PersonagemBase:
    def __init__(self, x, y, perfil, identidade):
        self.perfil, self.identidade = perfil, perfil.id
        self.kit = KITS[perfil.id]
        self.nome, self.titulo, self.descricao = perfil.nome, perfil.titulo, perfil.descricao
        self.vida_maxima, self.reiatsu_maximo = perfil.vida, perfil.reiatsu
        self.stamina_maxima = 100
        self.largura, self.altura, self.cor_base = perfil.largura, perfil.altura, perfil.cor
        self.velocidade_movimento, self.peso, self.defesa = perfil.velocidade, perfil.peso, perfil.defesa
        self.aceleracao, self.gravidade, self.forca_pulo = 2300, 1900, -740
        self.base_moves = golpes(self.kit,perfil.dano,perfil.alcance)
        self.moves = dict(self.base_moves)
        self.vitorias = self.derrotas = 0
        self.resetar_round(x, True)
        if y is not None:
            self.y = min(float(y),POSICAO_CHAO-self.altura)
            self.no_chao = self.y >= POSICAO_CHAO-self.altura
            self.sync_rect()

    def resetar_round(self, x, olhando_direita=True):
        self.x, self.y = float(x), float(POSICAO_CHAO-self.altura)
        self.rect = pygame.Rect(self.x,self.y,self.largura,self.altura)
        self.vida, self.vida_atrasada = float(self.vida_maxima),float(self.vida_maxima)
        self.reiatsu, self.stamina = 45.,100.
        self.velocidade_x = self.velocidade_y = 0.
        self.direcao = 1 if olhando_direita else -1
        self.no_chao = True
        self.estado_atual = self.estado_anterior = E.IDLE
        self.tempo_estado = self.tempo_acao = 0.
        self.acao = None
        self.acertou = self.emitiu = False
        self.forma_liberada = False
        self.form_index = -1
        self.moves = dict(self.base_moves)
        self.hit_slots = set()
        self.charge_time = 0.
        self.charging = False
        self.charge_ready = 0.
        self.tempo_liberacao = self.exaustao = self.invulnerabilidade = self.barreira = 0.
        self.contador_combo = 0
        self.dano_combo = self.janela_combo = 0.
        self.cooldowns = {}
        self.buffer = []
        self.projeteis_pendentes = []
        self.eventos = []
        self.movimento = 0
        self.correndo = self.guarda = False
        self.mensagem, self.tempo_mensagem = '',0.
        self.anim_time = 0.

    def resetar_para_round(self,x,y=None,olhando_direita=True):
        self.resetar_round(x,olhando_direita)

    def sync_rect(self):
        self.x = max(24., min(ARENA_WIDTH-self.largura-24.,self.x))
        self.rect.topleft = round(self.x),round(self.y)

    def estado(self, state, duration=0.):
        self.estado_anterior,self.estado_atual = self.estado_atual,state
        self.tempo_estado = duration
        self.anim_time = 0

    def pode_agir(self):
        return self.vida>0 and self.estado_atual in FREE

    def mover(self, direcao):
        self.movimento = max(-1,min(1,direcao))

    def parar(self):
        self.mover(0)

    def correr(self, direcao):
        self.mover(direcao)
        self.correndo = True

    def defender(self, ativo):
        self.guarda = ativo

    def comando(self, nome):
        """150 ms input buffer; each press is consumed at most once."""
        self.buffer.append([nome,.15])
        self.buffer = self.buffer[-4:]

    def consumir_reiatsu(self, custo):
        if self.reiatsu<custo:return False
        self.reiatsu -= custo
        return True

    def ganhar_reiatsu(self, qtd):
        self.reiatsu = min(self.reiatsu_maximo,self.reiatsu+qtd)

    def consumir_stamina(self,custo):
        if self.stamina<custo:return False
        self.stamina -= custo
        return True

    def pular(self):
        if not self.pode_agir() or not self.no_chao:return False
        self.velocidade_y,self.no_chao = self.forca_pulo,False
        self.estado(E.JUMP)
        self.criar_efeito('jump')
        return True

    def dash(self):
        mobility = self.kit.mobility
        if not self.pode_agir() or not self.consumir_stamina(mobility.cost):return False
        self.estado(E.DASH,mobility.duration)
        self.velocidade_x = (self.movimento or self.direcao)*mobility.speed
        self.invulnerabilidade = mobility.invulnerability
        self.criar_efeito('dash')
        return True

    def aparar(self):
        if not (self.pode_agir() or self.estado_atual==E.BLOCK) or not self.consumir_stamina(18):return False
        self.estado(E.PARRY,.32)
        return True

    def ativar_liberacao(self):
        next_index = self.form_index+1
        if not self.pode_agir() or self.exaustao or next_index>=len(self.kit.forms):return False
        form = self.kit.forms[next_index]
        if not self.consumir_reiatsu(form.cost):return False
        self.form_index = next_index
        self.forma_liberada,self.tempo_liberacao = True,form.duration
        self.charging=False
        self.moves = dict(self.base_moves)
        self.moves['exclusive'] = replace(self.moves['exclusive'], nome=form.technique or self.kit.exclusive,
            hits=(0., .10) if next_index>0 else (0.,), dano=27 if next_index>0 else 42)
        self.invulnerabilidade = .7
        self.estado(E.RELEASE,.7)
        self.anunciar(form.name.upper())
        self.criar_efeito('release')
        return True

    def desativar_liberacao(self):
        exhaustion = self.form.exhaustion if self.form else 0
        self.forma_liberada = False
        self.form_index = -1
        self.moves = dict(self.base_moves)
        self.tempo_liberacao,self.exaustao = 0,exhaustion
        self.anunciar('EXAUSTÃO')

    @property
    def form(self):
        # The boolean remains a compatibility view for legacy integrations.
        return self.kit.forms[max(0,self.form_index)] if self.forma_liberada else None

    def set_charge(self, held):
        if not self.kit.charge:return
        if held and self.pode_agir() and not self.charging:
            self.charging=True;self.charge_time=0
        elif not held and self.charging:
            self.charge_ready=min(1.,self.charge_time)
            self.charging=False
            self.comando('special')

    def iniciar_ataque(self,nome):
        if nome=='light' and not self.no_chao:nome='air'
        if nome=='exclusive' and not self.forma_liberada:return False
        # Confirmed normals cancel after startup, into normals/specials; no whiff cancels.
        cancel = self.acao and self.acertou and self.acao.estado in (E.ATTACK_LIGHT,E.ATTACK_HEAVY,E.ATTACK_AIR) and self.tempo_acao>=self.acao.startup
        if not (self.pode_agir() or cancel):return False
        move = self.moves[nome]
        if nome=='special' and self.charge_ready:
            move=replace(move,dano=move.dano*(1+self.charge_ready),custo=move.custo+10*self.charge_ready)
        if self.cooldowns.get(nome,0)>0 or self.reiatsu<move.custo:return False
        self.consumir_reiatsu(move.custo)
        self.cooldowns[nome] = move.cooldown
        self.acao,self.tempo_acao = move,0.
        self.hit_slots.clear()
        self.charging=False
        self.charge_ready=0
        self.acertou = self.emitiu = False
        self.estado(move.estado)
        self.velocidade_x *= .2
        if move.custo:
            self.anunciar(move.nome.upper())
            self.criar_efeito('special')
        return True

    def ataque_fraco(self):return self.iniciar_ataque('light')
    def ataque_forte(self):return self.iniciar_ataque('heavy')
    def ataque_aereo(self):return self.iniciar_ataque('air')
    def agarrar(self):return self.iniciar_ataque('grab')
    def usar_especial(self,outro=None):return self.iniciar_ataque('special')
    def usar_supremo(self):return self.iniciar_ataque('ultimate')

    def executar(self, nome):
        if nome in self.moves:return self.iniciar_ataque(nome)
        return {'jump':self.pular,'dash':self.dash,'parry':self.aparar,'release':self.ativar_liberacao}[nome]()

    def cancelar_acao(self):
        self.acao = None
        self.charging=False;self.charge_ready=0
        self.buffer.clear()

    def anunciar(self,text):
        self.mensagem,self.tempo_mensagem = text,1.25

    def criar_efeito(self,kind):
        self.eventos.append((kind,self.rect.center,self.cor_base))

    def obter_hurtbox(self):
        return self.rect.inflate(-8,-8)

    def obter_pushbox(self):
        return self.rect.inflate(-10,-8)

    def obter_hitbox(self):
        if not self.acao:return pygame.Rect(0,0,0,0)
        reach = self.acao.alcance * (self.form.reach if self.form else 1)
        if self.acao.tipo=='pulse':return self.rect.inflate(reach*2,80)
        return pygame.Rect(self.rect.centerx if self.direcao>0 else self.rect.centerx-reach-self.largura/2,
                           self.rect.y+20,reach+self.largura/2,self.altura-30)

    def continuar_combo(self, dano):
        if self.janela_combo<=0:
            self.contador_combo,self.dano_combo = 0,0.
        self.contador_combo += 1
        self.dano_combo += dano
        self.janela_combo = 1.05

    def receber_cura(self,qtd):
        self.vida = min(self.vida_maxima,self.vida+max(0,qtd))

    def receber_dano(self, move, atacante, projetil=False):
        if self.vida<=0 or self.invulnerabilidade>0:return 'miss'
        frontal = (atacante.rect.centerx-self.rect.centerx)*self.direcao>=0
        if self.estado_atual==E.PARRY and self.tempo_estado>.32-self.kit.parry_window and move.tipo!='grab' and frontal:
            self.ganhar_reiatsu(15)
            self.anunciar('PARRY')
            self.criar_efeito('parry')
            if not projetil:
                atacante.cancelar_acao(); atacante.estado(E.HITSTUN,.42)
            return 'parry'
        blocked = self.estado_atual in (E.BLOCK,E.BLOCKSTUN) and frontal and move.tipo!='grab'
        counter = self.acao is not None and self.tempo_acao<self.acao.startup
        scale = max(.35,1-atacante.contador_combo*.12) if atacante.janela_combo>0 else 1
        damage = move.dano*scale*(1-self.defesa)*(atacante.form.damage if atacante.form else 1)
        if blocked:
            self.stamina = max(0,self.stamina-move.dano*.8)
            damage *= .15
            self.estado(E.BLOCKSTUN,.16)
            self.ganhar_reiatsu(self.kit.block_energy)
            if self.stamina<=0:
                self.estado(E.HITSTUN,.7); self.anunciar('GUARDA QUEBRADA')
            self.criar_efeito('block')
        else:
            armor = self.kit.armor and self.acao and self.acao.estado==E.ATTACK_HEAVY and self.tempo_acao<self.acao.startup+self.acao.active
            if self.barreira>0:damage *= .55
            if self.form:damage *= self.form.absorption
            if counter:damage *= 1.15; atacante.anunciar('COUNTER')
            if not armor:
                self.cancelar_acao()
                self.estado(E.KNOCKDOWN if move.queda else E.HITSTUN,.65 if move.queda else .34)
            self.criar_efeito('heavy' if move.queda else 'hit')
            atacante.continuar_combo(damage)
            atacante.ganhar_reiatsu(atacante.kit.hit_energy)
            if atacante.vida>0:atacante.receber_cura(atacante.kit.heal_on_hit)
        self.vida = max(0,self.vida-damage)
        self.velocidade_x = atacante.direcao*move.empurrao/self.peso*(.4 if blocked else 1)
        self.ganhar_reiatsu(damage*.2)
        if self.vida<=0:
            self.forma_liberada=False;self.form_index=-1;self.tempo_liberacao=0
            self.moves=dict(self.base_moves)
            self.cancelar_acao(); self.estado(E.DEFEAT); self.criar_efeito('ko')
        return 'block' if blocked else 'hit'

    def atualizar(self, dt, outro):
        if self.charging:
            if self.pode_agir():self.charge_time=min(1.,self.charge_time+dt)
            else:self.charging=False
        self.anim_time += dt
        self.tempo_mensagem = max(0,self.tempo_mensagem-dt)
        self.vida_atrasada = max(self.vida,self.vida_atrasada-dt*16)
        self.invulnerabilidade = max(0,self.invulnerabilidade-dt)
        self.barreira = max(0,self.barreira-dt)
        self.exaustao = max(0,self.exaustao-dt)
        self.janela_combo = max(0,self.janela_combo-dt)
        if not self.janela_combo:self.contador_combo,self.dano_combo = 0,0
        for key in self.cooldowns:self.cooldowns[key] = max(0,self.cooldowns[key]-dt)
        if self.forma_liberada:
            self.ganhar_reiatsu(self.form.regen*dt)
            if self.form.duration>0:
                self.tempo_liberacao -= dt
                if self.tempo_liberacao<=0:self.desativar_liberacao()
        elif not self.exaustao:self.ganhar_reiatsu(self.perfil.regen*dt)
        self.stamina = min(100,self.stamina+dt*(7 if self.guarda else self.kit.stamina_regen))
        if self.vida<=0:return
        if self.estado_atual in LOCKED:
            self.tempo_estado -= dt
            if self.tempo_estado<=0:
                if self.estado_atual==E.KNOCKDOWN:
                    self.estado(E.GET_UP,.25); self.invulnerabilidade=.25
                else:self.estado(E.IDLE)
        if self.estado_atual in FREE or self.estado_atual==E.BLOCK:
            self.direcao = 1 if outro.rect.centerx>=self.rect.centerx else -1
            if self.guarda and self.no_chao and self.stamina>0:
                self.estado_atual=E.BLOCK
                self.stamina=max(0,self.stamina-dt*12)
            elif self.estado_atual==E.BLOCK:self.estado(E.IDLE)
        for entry in list(self.buffer):
            entry[1] -= dt
            if entry not in self.buffer:continue
            if self.executar(entry[0]):
                if entry in self.buffer:self.buffer.remove(entry)
                break
            if entry[1]<=0:self.buffer.remove(entry)
        if self.acao:
            self.tempo_acao += dt
            if self.tempo_acao>=self.acao.duracao:
                self.acao=None;self.estado(E.IDLE)
        self.atualizar_fisica(dt)

    def atualizar_fisica(self,dt):
        if self.pode_agir():
            speed = self.velocidade_movimento*(1.3 if self.correndo else 1)*(self.form.speed if self.form else 1)*(.72 if self.exaustao else 1)*(.45 if self.charging else 1)
            target = self.movimento*speed
            delta = max(-self.aceleracao*dt,min(self.aceleracao*dt,target-self.velocidade_x))
            self.velocidade_x += delta
            if self.no_chao:self.estado_atual = (E.RUN if self.correndo else E.WALK) if self.movimento else (E.EXHAUSTED if self.exaustao else E.IDLE)
        elif self.estado_atual!=E.DASH:self.velocidade_x *= max(0,1-dt*8)
        if self.acao and self.acao.tipo=='rush' and self.tempo_acao<self.acao.startup+self.acao.active:
            self.velocidade_x = self.direcao*650
        self.x += self.velocidade_x*dt
        if not self.no_chao:
            self.velocidade_y += self.gravidade*dt
            self.y += self.velocidade_y*dt
            if self.pode_agir():self.estado_atual = E.JUMP if self.velocidade_y<0 else E.FALL
            if self.y+self.altura>=POSICAO_CHAO:
                self.y=POSICAO_CHAO-self.altura; self.velocidade_y=0;self.no_chao=True
                self.criar_efeito('land')
                if self.pode_agir():self.estado(E.LAND,.065)
        self.sync_rect()

    def desenhar(self,superficie):
        from animation import draw_fighter
        draw_fighter(superficie,self)
