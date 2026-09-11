"""Move data: startup/active/recovery in seconds, resolved by the simulation."""
from dataclasses import dataclass, replace
from states import Estado

@dataclass(frozen=True)
class Golpe:
    nome: str
    estado: Estado
    startup: float
    active: float
    recovery: float
    dano: float
    alcance: int
    custo: float = 0
    tipo: str = 'melee'
    empurrao: float = 160
    queda: bool = False
    cooldown: float = 0
    hits: tuple = (0.,)

    @property
    def duracao(self):
        return self.startup + self.active + self.recovery


def golpes(kit, dano: float, alcance: int) -> dict[str, Golpe]:
    slow = kit.tempo
    m = {
        'light': Golpe('Corte breve', Estado.ATTACK_LIGHT, .09*slow, .09, .19*slow, dano, alcance),
        'heavy': Golpe('Ruptura', Estado.ATTACK_HEAVY, .21*slow, .12, .30*slow, dano*1.8, alcance+28, empurrao=250, queda=True),
        'air': Golpe('Ataque descendente', Estado.ATTACK_AIR, .10, .18, .22, dano*1.3, alcance+15),
        'grab': Golpe('Arremesso', Estado.GRAB, .13, .09, .38, dano*2.1, 30, tipo='grab', empurrao=320, queda=True),
    }
    specs = kit.specials
    for i, (name, kind, damage, reach) in enumerate(specs):
        m['special' if i == 0 else 'special2'] = Golpe(name, Estado.SPECIAL, .19*slow, .18, .30, damage, reach, 22+i*8, kind, 300, kind=='wave', .65)
    m['ultimate'] = Golpe(kit.ultimate, Estado.ULTIMATE, .40, .55, .65, 22, 300, 75, 'projectile' if kit.archetype=='distância' else 'pulse', 80, False, 3, (0., .18, .36))
    m['exclusive'] = Golpe(kit.exclusive, Estado.ULTIMATE, .22, .23, .48, 42, 240, 15, 'projectile' if kit.projectile_speed>700 else 'pulse', 330, True, 2)
    return m
