"""Stable combat definitions: origin, affiliation, style and appearance are independent."""
from dataclasses import dataclass
from enum import Enum

class Origin(str, Enum):
    SOUL = 'Alma / Shinigami'
    HOLLOW = 'Hollow'
    ARRANCAR = 'Hollow / Arrancar'
    HUMAN = 'Humano'

@dataclass(frozen=True)
class Mobility:
    name: str
    speed: float = 850
    duration: float = .17
    cost: float = 23
    invulnerability: float = .045

@dataclass(frozen=True)
class Form:
    name: str
    cost: float = 70
    duration: float = 10
    exhaustion: float = 3
    damage: float = 1.14
    speed: float = 1.18
    reach: float = 1.25
    absorption: float = 1
    reflect: bool = False
    regen: float = 0
    technique: str = ''

@dataclass(frozen=True)
class Kit:
    id: str
    origin: Origin
    affiliation: str
    archetype: str
    visual: str
    mobility: Mobility
    forms: tuple
    specials: tuple
    ultimate: str
    exclusive: str
    tempo: float = 1
    hit_energy: float = 6
    block_energy: float = 0
    parry_window: float = .11
    armor: bool = False
    projectile_speed: float = 620
    aerial_projectile: bool = False
    charge: bool = False
    stamina_regen: float = 20
    heal_on_hit: float = 0

KITS = {
 'kensei': Kit('kensei', Origin.SOUL, 'Shinigami independente', 'equilibrado', 'swordsman', Mobility('Shunpo'),
    (Form('Shikai: Tsukikage', technique='Getsurin', regen=2), Form('Bankai: Mugen Tsukikage', 55, 8, 4, 1.28, 1.28, 1.45, technique='Sengetsu')),
    (('Getsurin', 'projectile', 26, 95), ('Corte Shunpo', 'rush', 23, 115)), 'Mil cortes', 'Lua infinita', hit_energy=9),
 'vastor': Kit('vastor', Origin.ARRANCAR, 'Hueco Mundo', 'pressão', 'beast', Mobility('Sonído', 950, .16, 26, .065),
    (Form('Resurrección: Devorador', damage=1.25, speed=1.1, absorption=.85, technique='Cero devastador'),),
    (('Cero', 'projectile', 31, 115), ('Ruptura bestial', 'wave', 28, 180)), 'Mandíbula do vazio', 'Cero devastador', tempo=1.35, armor=True, heal_on_hit=1.2),
 'zephyr': Kit('zephyr', Origin.HUMAN, 'Quincy independente', 'distância', 'archer', Mobility('Hirenkyaku', 1000, .18, 25, .12),
    (Form('Vollständig: Sternflug', speed=1.3, regen=6, technique='Lichtregen'),),
    (('Heilig Pfeil', 'projectile', 17, 90), ('Selo de reishi', 'trap', 22, 90)), 'Chuva de reishi', 'Lichtregen', tempo=.88, projectile_speed=780, aerial_projectile=True, charge=True),
 'kurogane': Kit('kurogane', Origin.HUMAN, 'Fullbringer independente', 'contra-ataque', 'guardian', Mobility('Bringer Light', 760, .20, 20, .08),
    (Form('Fullbring: Iron Oath', absorption=.72, reflect=True, technique='Juramento de ferro'),),
    (('Repulsão do escudo', 'pulse', 25, 190), ('Bastião', 'barrier', 0, 100)), 'Juízo de ferro', 'Juramento de ferro', block_energy=7, parry_window=.18),
 'akari': Kit('akari', Origin.HUMAN, 'Vigilantes de Karakura', 'técnico', 'human', Mobility('Esquiva treinada', 680, .19, 16, .025),
    (Form('Foco absoluto', 55, 9, 2, 1.1, 1.35, 1.05, technique='Sequência decisiva'),),
    (('Palma concentrada', 'rush', 24, 110), ('Talismã de contenção', 'trap', 18, 100)), 'Sequência decisiva', 'Contraofensiva', stamina_regen=30),
}
