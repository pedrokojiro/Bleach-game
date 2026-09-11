import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
import pygame
from constants import FIXED_DT,POSICAO_CHAO,ARENA_WIDTH
from seu_personagem import ELENCO
from match import Match
from states import Estado as E,Fluxo as F
from input_manager import InputManager,MAPS
from projetil import Projetil

pygame.init()
pygame.display.set_mode((1280,720))

class CombatTests(unittest.TestCase):
    def setUp(self):
        self.m=Match((0,1),'PVP');self.m.phase=F.FIGHT
        self.a,self.b=self.m.players
        self.a.x=600;self.b.x=690
        self.a.sync_rect();self.b.sync_rect()
        self.b.direcao=-1
    def advance(self,seconds):
        for _ in range(round(seconds/FIXED_DT)):
            self.m.update(FIXED_DT)
            self.m.collect_events()
    def test_startup_single_hit(self):
        hp=self.b.vida
        self.a.ataque_fraco();self.advance(.05)
        self.assertEqual(self.b.vida,hp)
        self.advance(.13);self.assertLess(self.b.vida,hp)
        after=self.b.vida;self.advance(.3);self.assertEqual(self.b.vida,after)
    def test_held_key_only_one_edge(self):
        im=InputManager();key=MAPS[0]['light']
        for _ in range(10):im.event(pygame.event.Event(pygame.KEYDOWN,key=key))
        self.assertEqual(im.pending[0],['light'])
        im.event(pygame.event.Event(pygame.KEYUP,key=key))
        im.event(pygame.event.Event(pygame.KEYDOWN,key=key))
        self.assertEqual(im.pending[0],['light','light'])
    def test_block_parry_grab(self):
        self.b.estado(E.BLOCK)
        hp=self.b.vida
        self.assertEqual(self.b.receber_dano(self.a.moves['light'],self.a),'block')
        chip=hp-self.b.vida
        self.assertLess(chip,3)
        self.b.estado(E.PARRY,.32)
        hp=self.b.vida
        self.assertEqual(self.b.receber_dano(self.a.moves['light'],self.a),'parry')
        self.assertEqual(hp,self.b.vida)
        self.b.estado(E.BLOCK)
        self.assertEqual(self.b.receber_dano(self.a.moves['grab'],self.a),'hit')
        self.assertEqual(self.b.estado_atual,E.KNOCKDOWN)
    def test_projectile_ownership_and_reflection(self):
        q=Projetil(self.a,self.a.moves['special']);q.rect=self.a.rect.copy()
        self.assertFalse(q.checar_colisao(self.a))
        guard=ELENCO[3](690);guard.forma_liberada=True;guard.barreira=2
        q.rect=guard.rect.copy()
        self.assertTrue(q.checar_colisao(guard));self.assertIs(q.dono,guard)
    def test_release_exhaustion_reset(self):
        self.a.reiatsu=100
        self.assertTrue(self.a.ativar_liberacao())
        self.assertFalse(self.a.ativar_liberacao())
        self.advance(10.1)
        self.assertFalse(self.a.forma_liberada);self.assertGreater(self.a.exaustao,0)
        self.a.comando('heavy');self.a.cooldowns['special']=10
        self.a.resetar_round(500)
        self.assertFalse(self.a.buffer);self.assertFalse(self.a.cooldowns)
        self.assertEqual(self.a.stamina,100);self.assertEqual(self.a.exaustao,0)
    def test_tie_and_match_victory(self):
        self.a.vida=self.b.vida=0;self.m.finish_round()
        self.assertEqual(self.m.wins,[0,0]);self.assertIn('EMPATE',self.m.result)
        self.advance(2.6);self.assertEqual(self.m.phase,F.INTRO)
        for win in range(2):
            self.m.phase=F.FIGHT;self.b.vida=0;self.m.finish_round();self.advance(2.6)
        self.assertEqual(self.m.phase,F.VICTORY);self.assertEqual(self.m.winner,0)
    def test_timeout_uses_percentage(self):
        self.a.vida=55;self.b.vida=60
        self.m.time=0;self.m.finish_round()
        self.assertEqual(self.m.wins,[1,0])
    def test_pushboxes_and_arena(self):
        self.a.x=24;self.b.x=25;self.a.sync_rect();self.b.sync_rect()
        self.m.separate()
        self.assertFalse(self.a.obter_pushbox().colliderect(self.b.obter_pushbox()))
        for p in (self.a,self.b):
            p.x=9999;p.sync_rect();self.assertLessEqual(p.rect.right,ARENA_WIDTH-24)
    def test_three_combo_sequences_all_fighters(self):
        for i in range(len(ELENCO)):
            for sequence in [('light','light','light'),('light','light','heavy'),('light','heavy','special')]:
                m=Match((i,1),'PVP');m.phase=F.FIGHT
                p,target=m.players
                p.x=600;target.x=600+p.largura+9
                p.sync_rect();target.sync_rect();p.reiatsu=130
                for key in sequence:
                    before=p.contador_combo
                    p.comando(key)
                    for _ in range(120):
                        m.update(FIXED_DT)
                        m.collect_events()
                        if p.contador_combo>before:break
                    self.assertGreater(p.contador_combo,before,(p.nome,sequence,key))
                self.assertEqual(p.contador_combo,3)
    def test_every_move_every_character(self):
        for cls in ELENCO:
            for key in ('light','heavy','air','grab','special','special2','ultimate','exclusive'):
                p=cls(600);target=ELENCO[1](700);p.reiatsu=130;p.forma_liberada=True;p.tempo_liberacao=10
                self.assertTrue(p.iniciar_ataque(key),(p.nome,key))
                for _ in range(round(p.acao.duracao/FIXED_DT)+2):p.atualizar(FIXED_DT,target)
                self.assertIsNone(p.acao)
    def test_all_matchups_and_difficulties(self):
        for difficulty in range(3):
            for i in range(len(ELENCO)):
                m=Match((i,(i+1)%len(ELENCO)),'PVE',difficulty);m.phase=F.FIGHT
                for _ in range(600):m.update(FIXED_DT);m.collect_events()
                for p in m.players:
                    self.assertGreaterEqual(p.vida,0);self.assertLessEqual(p.reiatsu,p.reiatsu_maximo)
    def test_simultaneous_double_ko(self):
        self.a.vida=self.b.vida=1
        for p in (self.a,self.b):p.ataque_fraco();p.tempo_acao=p.acao.startup+.01
        self.m.resolve_attacks()
        self.assertEqual((self.a.vida,self.b.vida),(0,0))
    def test_cancel_denied_on_whiff(self):
        self.a.ataque_fraco()
        self.assertFalse(self.a.ataque_forte())
    def test_knockdown_recovery(self):
        self.b.receber_dano(self.a.moves['heavy'],self.a)
        self.advance(.80)
        self.assertEqual(self.b.estado_atual,E.GET_UP)
        self.advance(.3)
        self.assertIn(self.b.estado_atual,(E.IDLE,E.WALK))

    def test_specials_spawn_and_barrier_expires(self):
        for i in range(len(ELENCO)):
            for key in ('special','special2','ultimate','exclusive'):
                m=Match((i,1),'PVP');m.phase=F.FIGHT
                p=m.players[0];p.reiatsu=130;p.forma_liberada=True;p.tempo_liberacao=10
                p.iniciar_ataque(key)
                for _ in range(65):m.update(FIXED_DT)
                kind=p.moves[key].tipo
                if kind in ('projectile','wave','trap'):
                    self.assertTrue(m.projectiles,(i,key))
                elif kind=='barrier':self.assertGreater(p.barreira,0)
                for _ in range(480):m.update(FIXED_DT)
                self.assertFalse(m.projectiles)
                self.assertEqual(p.barreira,0)

    def test_fixed_step_movement_across_render_rates(self):
        results=[]
        for fps in (30,60,144):
            p=ELENCO[0](400);other=ELENCO[1](1200);p.mover(1)
            accumulator=0
            for _ in range(fps*2):
                accumulator+=1/fps
                while accumulator+1e-10>=FIXED_DT:
                    p.atualizar(FIXED_DT,other);accumulator-=FIXED_DT
            results.append(p.x)
        self.assertAlmostEqual(min(results),max(results),places=6)

class ApplicationTests(unittest.TestCase):
    def test_flow_and_render(self):
        from game import Game
        game=Game()
        press=lambda key:game.events([pygame.event.Event(pygame.KEYDOWN,key=key)])
        game.draw();press(pygame.K_RETURN)
        self.assertEqual(game.phase,F.SELECT);game.draw()
        press(pygame.K_f);press(pygame.K_j);press(pygame.K_RETURN)
        self.assertEqual(game.phase,F.FIGHT);game.draw()
        for _ in range(310):game.update(FIXED_DT)
        game.draw();press(pygame.K_ESCAPE)
        self.assertTrue(game.paused);game.draw()
        press(pygame.K_ESCAPE);press(pygame.K_F1);game.draw()
        self.assertTrue(game.help)
        press(pygame.K_F1)
        game.match.phase=F.VICTORY;game.match.winner=0;game.draw()
        press(pygame.K_RETURN);self.assertEqual(game.match.phase,F.INTRO)

if __name__=='__main__':unittest.main(verbosity=2)
