"""Event edges for actions; held directions/guard are applied every simulation step."""
import pygame as pg

MAPS=[
 {'left':pg.K_a,'right':pg.K_d,'jump':pg.K_w,'guard':pg.K_s,'light':pg.K_f,'heavy':pg.K_g,'special':pg.K_r,'special2':pg.K_t,'grab':pg.K_v,'dash':pg.K_LSHIFT,'parry':pg.K_c,'release':pg.K_q,'ultimate':pg.K_e,'exclusive':pg.K_x,'run':pg.K_LCTRL},
 {'left':pg.K_LEFT,'right':pg.K_RIGHT,'jump':pg.K_UP,'guard':pg.K_DOWN,'light':pg.K_j,'heavy':pg.K_k,'special':pg.K_u,'special2':pg.K_i,'grab':pg.K_n,'dash':pg.K_RSHIFT,'parry':pg.K_m,'release':pg.K_o,'ultimate':pg.K_l,'exclusive':pg.K_COMMA,'run':pg.K_RCTRL}
]

class InputManager:
    def __init__(self,maps=None):
        self.maps=[dict(m) for m in (maps or MAPS)]
        self.held=set();self.pending=[[],[]]
        self.charge_edges=[None,None]
        self.cancel_charge=[False,False]
        self.devices={};self.pad_held=[set(),set()];self.axes=[0,0]
        self.pad_actions={}
        pg.joystick.init()
        for i in range(pg.joystick.get_count()):self.add_device(i)
    def add_device(self,index):
        if len(self.devices)>=2:return
        joystick=pg.joystick.Joystick(index)
        joystick.init()
        slot=next(i for i in range(2) if i not in [v[0] for v in self.devices.values()])
        self.devices[joystick.get_instance_id()]=(slot,joystick)
    def clear(self):
        self.held.clear();self.pending=[[],[]];self.charge_edges=[None,None];self.cancel_charge=[True,True]
        self.pad_held=[set(),set()];self.axes=[0,0]
        self.pad_actions.clear()
    def event(self,event):
        if event.type==pg.JOYDEVICEADDED:self.add_device(event.device_index)
        if event.type==pg.JOYDEVICEREMOVED:
            removed=self.devices.pop(event.instance_id,None)
            if removed:
                i=removed[0];self.pad_held[i].clear();self.axes[i]=0;self.pending[i].clear();self.charge_edges[i]=None;self.cancel_charge[i]=True
        if event.type in (pg.JOYBUTTONDOWN,pg.JOYBUTTONUP,pg.JOYAXISMOTION,pg.JOYHATMOTION):
            device=self.devices.get(event.instance_id)
            if device:
                i=device[0]
                if event.type==pg.JOYAXISMOTION and event.axis==0:self.axes[i]=0 if abs(event.value)<.25 else (1 if event.value>0 else -1)
                if event.type==pg.JOYHATMOTION:
                    self.axes[i]=event.value[0]
                    if event.value[1]>0:self.pending[i].append('jump')
                if event.type in (pg.JOYBUTTONDOWN,pg.JOYBUTTONUP):
                    action=PAD_BUTTONS.get(event.button)
                    token=(event.instance_id,event.button)
                    if event.type==pg.JOYBUTTONDOWN:
                        if 'guard' in self.pad_held[i]:action={0:'jump',1:'grab',2:'exclusive',3:'ultimate'}.get(event.button,action)
                        self.pad_actions[token]=action
                    else:action=self.pad_actions.pop(token,action)
                    if action:
                        down=event.type==pg.JOYBUTTONDOWN
                        if down and action not in self.pad_held[i]:
                            self.pad_held[i].add(action)
                            if action=='special':self.charge_edges[i]=True
                            if action not in ('guard','run'):self.pending[i].append(action)
                        elif not down:
                            self.pad_held[i].discard(action)
                            if action=='special':self.charge_edges[i]=False
        if event.type==pg.WINDOWFOCUSLOST:self.clear()
        if event.type==pg.KEYUP:
            self.held.discard(event.key)
            for i,m in enumerate(self.maps):
                if event.key==m['special']:self.charge_edges[i]=False
        if event.type==pg.KEYDOWN and event.key not in self.held:
            self.held.add(event.key)
            for i,m in enumerate(self.maps):
                for action,key in m.items():
                    if key==event.key and action not in ('left','right','guard','run'):
                        self.pending[i].append(action)
                        if action=='special':self.charge_edges[i]=True
    def apply(self,index,p):
        if self.cancel_charge[index]:
            p.charging=False;p.charge_ready=0;p.buffer.clear();self.cancel_charge[index]=False
        m=self.maps[index];pad=self.pad_held[index]
        p.mover(self.axes[index] or int(m['right'] in self.held)-int(m['left'] in self.held))
        p.correndo=m['run'] in self.held or 'run' in pad
        p.defender(m['guard'] in self.held or 'guard' in pad)
        if any(action in ('jump','grab','exclusive','ultimate') for action in self.pending[index]):p.defender(False)
        for action in self.pending[index]:
            if action=='special' and p.kit.charge:
                p.set_charge(True)
            else:p.comando(action)
        if self.charge_edges[index] is False:p.set_charge(False)
        self.charge_edges[index]=None
        self.pending[index].clear()

# Conventional SDL joystick layout. Start pauses; Back shows help (handled by Game).
PAD_BUTTONS={0:'light',1:'heavy',2:'special',3:'special2',4:'guard',5:'dash',6:'parry',8:'grab',9:'release',10:'ultimate',11:'exclusive',12:'jump',13:'run'}
