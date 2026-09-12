"""Event edges for actions; held directions/guard are applied every simulation step."""
import pygame as pg

MAPS=[
 {'left':pg.K_a,'right':pg.K_d,'jump':pg.K_w,'guard':pg.K_s,'light':pg.K_f,'heavy':pg.K_g,'special':pg.K_r,'special2':pg.K_t,'grab':pg.K_v,'dash':pg.K_LSHIFT,'parry':pg.K_c,'release':pg.K_q,'ultimate':pg.K_e,'exclusive':pg.K_x,'run':pg.K_LCTRL},
 {'left':pg.K_LEFT,'right':pg.K_RIGHT,'jump':pg.K_UP,'guard':pg.K_DOWN,'light':pg.K_j,'heavy':pg.K_k,'special':pg.K_u,'special2':pg.K_i,'grab':pg.K_n,'dash':pg.K_RSHIFT,'parry':pg.K_m,'release':pg.K_o,'ultimate':pg.K_l,'exclusive':pg.K_COMMA,'run':pg.K_RCTRL}
]

class InputManager:
    def __init__(self):self.held=set();self.pending=[[],[]]
    def clear(self):self.held.clear();self.pending=[[],[]]
    def event(self,event):
        if event.type==pg.WINDOWFOCUSLOST:self.clear()
        if event.type==pg.KEYUP:self.held.discard(event.key)
        if event.type==pg.KEYDOWN and event.key not in self.held:
            self.held.add(event.key)
            for i,m in enumerate(MAPS):
                for action,key in m.items():
                    if key==event.key and action not in ('left','right','guard','run'):
                        self.pending[i].append(action)
    def apply(self,index,p):
        m=MAPS[index]
        p.mover(int(m['right'] in self.held)-int(m['left'] in self.held))
        p.correndo=m['run'] in self.held
        p.defender(m['guard'] in self.held)
        for action in self.pending[index]:p.comando(action)
        self.pending[index].clear()
