import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
import pygame as pg
from catalog import KITS, Origin
from seu_personagem import CATALOGO, PERFIS, criar_personagem
from constants import FIXED_DT
from states import Estado as E, Fluxo as F
from match import Match
from ai import BotIA
from input_manager import InputManager
from projetil import Projetil
from game import Game
from arena import ARENAS, ArenaVisual
import settings

pg.init()
pg.display.set_mode((1280,720))

def advance(p,other,seconds):
    for _ in range(round(seconds/FIXED_DT)):
        p.atualizar(FIXED_DT,other)

class BleachTests(unittest.TestCase):
    def pair(self,a='kensei',b='akari'):
        m=Match((a,b),'PVP');m.phase=F.FIGHT
        m.players[0].x=600;m.players[1].x=690
        for p in m.players:p.sync_rect()
        m.players[1].direcao=-1
        return m,*m.players

    def test_catalog_origins_and_unique_ids(self):
        self.assertEqual(len(PERFIS),len(CATALOGO))
        self.assertEqual(set(CATALOGO),set(KITS))
        self.assertEqual(KITS['vastor'].origin,Origin.ARRANCAR)
        self.assertEqual(KITS['zephyr'].origin,KITS['kurogane'].origin)
        for key in CATALOGO:
            p=criar_personagem(key,500)
            self.assertEqual(p.identidade,key)
            self.assertEqual(set(p.moves),{'light','heavy','air','grab','special','special2','ultimate','exclusive'})

    def test_forms_cost_transition_expiry_and_reset(self):
        for key in CATALOGO:
            _,p,t=self.pair(key)
            for i,form in enumerate(p.kit.forms):
                p.reiatsu=form.cost-1
                self.assertFalse(p.ativar_liberacao())
                p.reiatsu=p.reiatsu_maximo
                before=p.reiatsu
                self.assertTrue(p.ativar_liberacao())
                self.assertEqual(p.reiatsu,before-form.cost)
                self.assertEqual(p.form_index,i)
                self.assertFalse(p.ativar_liberacao())
                advance(p,t,.75)
                self.assertEqual(p.moves['exclusive'].nome,form.technique)
            advance(p,t,p.form.duration+.1)
            self.assertIsNone(p.form)
            self.assertGreater(p.exaustao,0)
            p.resetar_round(500)
            self.assertEqual(p.form_index,-1)
            self.assertEqual(p.exaustao,0)
            self.assertEqual(p.moves,p.base_moves)

    def test_persistent_form_and_ko_cleanup(self):
        _,p,t=self.pair()
        p.kit=replace(p.kit,forms=(replace(p.kit.forms[0],duration=0),))
        p.reiatsu=100;p.ativar_liberacao();advance(p,t,12)
        self.assertTrue(p.forma_liberada)
        p.invulnerabilidade=0;p.vida=1
        p.receber_dano(t.moves['heavy'],t)
        self.assertIsNone(p.form);self.assertEqual(p.tempo_liberacao,0)
        self.assertEqual(p.estado_atual,E.DEFEAT)

    def test_passives_and_mobility(self):
        for key in CATALOGO:
            _,p,t=self.pair(key)
            before=p.stamina
            self.assertTrue(p.dash())
            self.assertEqual(p.stamina,before-p.kit.mobility.cost)
            self.assertEqual(p.invulnerabilidade,p.kit.mobility.invulnerability)
        _,p,t=self.pair('vastor')
        p.vida-=20;before=p.vida;t.receber_dano(p.moves['light'],p)
        self.assertGreater(p.vida,before)
        _,p,t=self.pair('kurogane')
        p.direcao=1;p.estado(E.BLOCK);p.reiatsu=0
        self.assertEqual(p.receber_dano(t.moves['light'],t),'block')
        self.assertGreaterEqual(p.reiatsu,p.kit.block_energy)
        _,p,t=self.pair('akari')
        p.stamina=0;advance(p,t,1)
        self.assertAlmostEqual(p.stamina,30)

    def test_charge_release_and_interruption(self):
        _,p,t=self.pair('zephyr')
        im=InputManager();key=im.maps[0]['special']
        im.event(pg.event.Event(pg.KEYDOWN,key=key));im.apply(0,p)
        advance(p,t,1)
        self.assertTrue(p.charging);self.assertIsNone(p.acao)
        im.event(pg.event.Event(pg.KEYUP,key=key));im.apply(0,p);advance(p,t,FIXED_DT)
        self.assertAlmostEqual(p.acao.dano,p.base_moves['special'].dano*2)
        p.resetar_round(600);p.set_charge(True)
        p.receber_dano(t.moves['light'],t)
        self.assertFalse(p.charging)
        p.set_charge(False);self.assertFalse(p.buffer)

    def test_multihit_schedule_and_limit(self):
        m,p,t=self.pair()
        p.reiatsu=100;p.iniciar_ataque('ultimate')
        t.vida=t.vida_maxima=999
        for _ in range(300):
            m.update(FIXED_DT)
            if not p.acao:break
        self.assertEqual(p.contador_combo,3)
        hp=t.vida
        for _ in range(20):m.resolve_attacks()
        self.assertEqual(t.vida,hp)
        m,p,t=self.pair('zephyr')
        p.reiatsu=100;p.iniciar_ataque('ultimate');t.x=1400;t.sync_rect()
        for _ in range(115):m.update(FIXED_DT)
        self.assertEqual(len(m.projectiles),3)

    def test_pause_or_disconnect_cancels_charge_without_firing(self):
        _,p,t=self.pair('zephyr')
        im=InputManager();p.set_charge(True);advance(p,t,.5)
        im.clear();im.apply(0,p)
        self.assertFalse(p.charging);self.assertFalse(p.buffer)
        p.set_charge(True);im.devices={42:(0,None)}
        im.event(pg.event.Event(pg.JOYDEVICEREMOVED,instance_id=42));im.apply(0,p)
        self.assertFalse(p.charging);self.assertFalse(p.buffer)

    def test_gamepad_guard_chord_jump(self):
        _,p,t=self.pair()
        im=InputManager();im.devices={42:(0,None)}
        for button in (4,0):im.event(pg.event.Event(pg.JOYBUTTONDOWN,instance_id=42,button=button))
        im.apply(0,p);advance(p,t,FIXED_DT)
        self.assertFalse(p.no_chao)

    def test_natural_cpu_match_completion(self):
        for a,b in [('kensei','vastor'),('zephyr','kurogane'),('akari','zephyr')]:
            m=Match((a,b),'PVE',1);driver=BotIA(m.players[0],1)
            for _ in range(120*420):
                if m.phase==F.FIGHT:driver.process(FIXED_DT,m.players[1],m.projectiles)
                m.update(FIXED_DT);m.collect_events()
                if m.phase==F.VICTORY:break
            self.assertEqual(m.phase,F.VICTORY,(a,b,m.wins))

    def test_reflection_moves_ownership_and_position(self):
        _,p,t=self.pair('zephyr','kurogane')
        t.reiatsu=100;t.ativar_liberacao();t.barreira=2
        q=Projetil(p,p.moves['special']);q.x=t.rect.centerx;q.y=t.rect.centery;q.rect.center=(q.x,q.y)
        self.assertTrue(q.checar_colisao(t))
        self.assertIs(q.dono,t)
        self.assertEqual(q.rect.center,(round(q.x),round(q.y)))
        self.assertFalse(q.checar_colisao(t))

    def test_all_pairs_finish_and_rematch(self):
        for mode in ('PVP','PVE'):
            for a in CATALOGO:
                for b in CATALOGO:
                    m=Match((a,b),mode);m.phase=F.FIGHT
                    for _ in range(180):m.update(FIXED_DT);m.collect_events()
                    for _ in range(2):
                        m.phase=F.FIGHT;m.players[1].vida=0;m.finish_round()
                        for step in range(305):m.update(FIXED_DT)
                    self.assertEqual(m.phase,F.VICTORY,(mode,a,b))
                    self.assertEqual(Match((a,b),mode).phase,F.INTRO)

    def test_ai_selects_defense_range_and_form(self):
        _,p,t=self.pair('kurogane')
        p.reiatsu=100;t.iniciar_ataque('light')
        BotIA(p).process(FIXED_DT,t)
        self.assertIn('special2',[e[0] for e in p.buffer])
        _,p,t=self.pair('zephyr');t.x=700;t.sync_rect()
        BotIA(p).process(FIXED_DT,t)
        self.assertEqual(p.movimento,-1)
        p.reiatsu=100;p.vida=30;p.buffer=[]
        BotIA(p).process(FIXED_DT,t)
        self.assertIn('release',[e[0] for e in p.buffer])

    def test_settings_roundtrip_invalid_and_ui_remapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.json'
            game=Game(path)
            def press(k):game.events([pg.event.Event(pg.KEYDOWN,key=k)])
            press(pg.K_F8);press(pg.K_F9)
            press(pg.K_F3);press(pg.K_RETURN);press(pg.K_z)
            self.assertEqual(game.inputs.maps[0]['left'],pg.K_z)
            loaded=settings.load(path)
            self.assertFalse(loaded['shake']);self.assertTrue(loaded['muted'])
            self.assertEqual(loaded['keys'][0]['left'],pg.K_z)
            press(pg.K_ESCAPE);game.start();self.assertFalse(game.camera.shake_enabled)
            path.write_text('{broken',encoding='utf-8')
            self.assertEqual(settings.load(path),settings.defaults())

    def test_gamepad_events_and_disconnect(self):
        _,p,t=self.pair()
        im=InputManager();im.devices={42:(0,None)}
        im.event(pg.event.Event(pg.JOYAXISMOTION,instance_id=42,axis=0,value=.8))
        im.event(pg.event.Event(pg.JOYBUTTONDOWN,instance_id=42,button=0))
        im.apply(0,p)
        self.assertEqual(p.movimento,1)
        self.assertEqual(p.buffer[0][0],'light')
        im.event(pg.event.Event(pg.JOYDEVICEREMOVED,instance_id=42));im.apply(0,p)
        self.assertEqual(p.movimento,0)

    def test_selection_every_fighter_arena_help_and_settings_render(self):
        with tempfile.TemporaryDirectory() as directory:
            game=Game(Path(directory)/'settings.json');game.phase=F.SELECT
            for i in range(len(PERFIS)):
                game.selected=[i,(i+1)%len(PERFIS)];game.draw()
            for arena in ARENAS:
                game.arena=ArenaVisual(arena);game.start();game.draw()
            game.help=True;game.draw();game.help=False
            game.remapping=True;game.draw()

    def test_training_has_infinite_time_and_no_round_end(self):
        m=Match(('kensei','vastor'),'TREINO');self.assertEqual(m.phase,F.FIGHT)
        self.assertEqual(m.time,float('inf'))
        target=m.players[1];target.vida=1
        target.receber_dano(m.players[0].moves['heavy'],m.players[0])
        m.update(FIXED_DT)
        self.assertEqual(target.vida,target.vida_maxima)
        self.assertEqual(m.wins,[0,0]);self.assertEqual(m.phase,F.FIGHT)

    def test_training_reset_resources_and_dummy_modes(self):
        m=Match(('zephyr','kurogane'),'TREINO');p,dummy=m.players
        p.x=900;p.reiatsu=0;p.stamina=0;m.projectiles.append(Projetil(p,p.moves['special']))
        m.update(FIXED_DT)
        self.assertEqual(p.reiatsu,p.reiatsu_maximo);self.assertEqual(p.stamina,p.stamina_maxima)
        self.assertEqual(m.cycle_training_dummy(),'DEFESA');m.update(FIXED_DT)
        self.assertTrue(dummy.guarda)
        self.assertEqual(m.cycle_training_dummy(),'CPU');m.update(FIXED_DT)
        self.assertEqual(m.cycle_training_dummy(),'PARADO')
        m.reset_training();self.assertEqual(p.x,540);self.assertFalse(m.projectiles)

    def test_training_game_shortcuts_and_render(self):
        with tempfile.TemporaryDirectory() as directory:
            game=Game(Path(directory)/'settings.json');game.mode='TREINO';game.start()
            def press(key):game.events([pg.event.Event(pg.KEYDOWN,key=key)])
            game.match.players[0].x=800
            press(pg.K_F5);self.assertEqual(game.match.players[0].x,540)
            press(pg.K_F6);self.assertEqual(game.match.training_dummy,'DEFESA')
            press(pg.K_F7);self.assertFalse(game.match.training_resources)
            game.draw()

    def test_mode_selection_cycles_through_training(self):
        with tempfile.TemporaryDirectory() as directory:
            game=Game(Path(directory)/'settings.json');game.phase=F.SELECT
            for expected in ('PVP','TREINO','PVE'):
                game.events([pg.event.Event(pg.KEYDOWN,key=pg.K_TAB)])
                self.assertEqual(game.mode,expected)

if __name__=='__main__':unittest.main()
