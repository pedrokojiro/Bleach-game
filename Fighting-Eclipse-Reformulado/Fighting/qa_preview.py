"""Reproducible dummy-driver visual captures; not a hardware validation."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import tempfile
from pathlib import Path
import pygame
from game import Game
from states import Fluxo as F, Estado as E
from arena import ArenaVisual, ARENAS
from seu_personagem import PERFIS

def main():
    output=Path('qa-output');output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        game=Game(Path(directory)/'settings.json')
        def capture(name):
            game.draw();pygame.image.save(game.canvas,output/(name+'.png'))
        capture('title')
        game.phase=F.SELECT
        for i in range(len(PERFIS)):
            game.selected=[i,(i+1)%len(PERFIS)];capture('select-'+PERFIS[i].id)
        for index,arena in enumerate(ARENAS):
            game.arena=ArenaVisual(arena);game.selected=[index,(index+2)%len(PERFIS)]
            game.start();game.match.phase=F.FIGHT
            for p in game.match.players:
                p.reiatsu=p.reiatsu_maximo;p.ativar_liberacao();p.estado(E.IDLE)
            capture(arena)
        game.help=True;capture('controls');game.help=False
        game.remapping=True;capture('remapping')
        game.remapping=False;game.mode='TREINO';game.selected=[0,1];game.start()
        game.match.cycle_training_dummy();capture('training')
        pygame.quit()
    print('Capturas em',output.resolve())

if __name__=='__main__':main()
