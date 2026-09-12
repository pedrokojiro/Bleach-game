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

    @property
    def duracao(self):
        return self.startup + self.active + self.recovery


def golpes(identidade: int, dano: float, alcance: int) -> dict[str, Golpe]:
    slow = 1.35 if identidade == 1 else (0.88 if identidade == 2 else 1)
    m = {
        'light': Golpe('Corte breve', Estado.ATTACK_LIGHT, .09*slow, .09, .19*slow, dano, alcance),
        'heavy': Golpe('Ruptura', Estado.ATTACK_HEAVY, .21*slow, .12, .30*slow, dano*1.8, alcance+28, empurrao=250, queda=True),
        'air': Golpe('Ataque descendente', Estado.ATTACK_AIR, .10, .18, .22, dano*1.3, alcance+15),
        'grab': Golpe('Arremesso', Estado.GRAB, .13, .09, .38, dano*2.1, 30, tipo='grab', empurrao=320, queda=True),
    }
    specs = [
        [('Lâmina lunar', 'projectile', 26, 95), ('Passo cortante', 'rush', 23, 115)],
        [('Investida carmesim', 'rush', 31, 115), ('Abalo sísmico', 'wave', 28, 180)],
        [('Flecha astral', 'projectile', 17, 90), ('Selo de caça', 'trap', 22, 90)],
        [('Pulso de repulsão', 'pulse', 25, 190), ('Bastião', 'barrier', 0, 100)],
    ][identidade]
    for i, (name, kind, damage, reach) in enumerate(specs):
        m['special' if i == 0 else 'special2'] = Golpe(name, Estado.SPECIAL, .19*slow, .18, .30, damage, reach, 22+i*8, kind, 300, i==1 and identidade==1, .65)
    m['ultimate'] = Golpe(['Mil luas', 'Sol devastador', 'Chuva estelar', 'Juízo de ferro'][identidade], Estado.ULTIMATE, .40, .25, .65, 58, 300, 75, 'projectile' if identidade==2 else 'pulse', 450, True, 3)
    m['exclusive'] = Golpe(['Lua infinita', 'Quebra-mundo', 'Estrela cadente', 'Muralha eterna'][identidade], Estado.ULTIMATE, .22, .23, .48, 42, 240, 15, 'projectile' if identidade in (0,2) else 'pulse', 330, True, 2)
    if identidade == 1:
        m['light'] = replace(m['light'], nome='Punho brutal')
    elif identidade == 2:
        m['light'] = replace(m['light'], nome='Fio astral')
    elif identidade == 3:
        m['light'] = replace(m['light'], nome='Golpe de guarda')
    return m
