"""Optional WAV/OGG assets; synthesized original feedback if files are absent."""
from pathlib import Path
from array import array
import math
import pygame

class Audio:
    def __init__(self):
        self.volume=.35;self.muted=False;self.sounds={};self.music_name=None
        self.root=Path(__file__).parent/'assets'/'audio'
        try:
            if not pygame.mixer.get_init():pygame.mixer.init(44100,-16,1)
        except pygame.error:
            self.enabled=False;return
        self.enabled=True
        for name,freq in [('hit',125),('heavy',70),('block',280),('parry',880),('special',480),('release',160),('ko',60),('jump',350),('land',95),('dash',220),('confirm',660),('victory',780)]:
            path=self.root/(name+'.wav')
            if path.exists():self.sounds[name]=pygame.mixer.Sound(str(path))
            else:
                rate,_,channels=pygame.mixer.get_init()
                duration=.23 if name in ('release','ko','victory') else .075
                samples=array('h')
                for i in range(int(rate*duration)):
                    t=i/rate;envelope=(1-t/duration)**2
                    value=int(10000*envelope*math.sin(2*math.pi*(freq*t-freq*.35*t*t/duration)))
                    samples.extend([value]*channels)
                self.sounds[name]=pygame.mixer.Sound(buffer=samples)
    def play(self,name):
        if self.enabled and name in self.sounds and not self.muted:
            self.sounds[name].set_volume(self.volume);self.sounds[name].play()
    def music(self,name):
        if not self.enabled or self.music_name==name:return
        self.music_name=name;pygame.mixer.music.stop()
        path=self.root/(name+'.ogg')
        if path.exists():pygame.mixer.music.load(str(path));pygame.mixer.music.play(-1)
        self.set_volume(self.volume)
    def set_volume(self,value):
        self.volume=max(0,min(1,value))
        if self.enabled:pygame.mixer.music.set_volume(0 if self.muted else self.volume)
    def toggle(self):self.muted=not self.muted;self.set_volume(self.volume)
