"""Original four public character classes, now driven by distinct profiles."""
from dataclasses import dataclass
from personagem_base import PersonagemBase

@dataclass(frozen=True)
class Perfil:
    nome: str
    titulo: str
    descricao: str
    cor: tuple
    vida: int
    velocidade: int
    dano: int
    defesa: float
    peso: float
    alcance: int
    reiatsu: int
    regen: float
    largura: int
    altura: int
    dificuldade: str
    passiva: str
    id: str = ''

PERFIS = [
    Perfil('Kensei', 'SHINIGAMI ERRANTE', 'Equilíbrio, alcance e cancelamentos rápidos.', (99,205,247), 110,330,10,.05,1,95,110,7,58,142,'Fácil','Disciplina: mais reiatsu ao acertar.', 'kensei'),
    Perfil('Vastor', 'ARRANCAR DO VAZIO', 'Força devastadora; recuperações vulneráveis.', (245,104,87), 145,245,14,.10,1.6,82,90,5,88,166,'Normal','Predação: cura ao acertar; armadura no forte.', 'vastor'),
    Perfil('Zephyr', 'ARQUEIRO QUINCY', 'Controle de espaço, mobilidade e pouca vida.', (110,190,255), 90,390,8,.02,.8,78,130,9,48,138,'Difícil','Reishi: flecha carregável; regeneração na forma.', 'zephyr'),
    Perfil('Kurogane', 'FULLBRINGER DO ESCUDO', 'Objeto de afinidade: escudo herdado da família.', (187,155,244), 130,265,10,.18,1.35,85,110,6,78,151,'Normal','Guarda: parry longo e reiatsu ao bloquear.', 'kurogane'),
    Perfil('Akari', 'VIGILANTE DE KARAKURA', 'Talismãs, esquiva econômica e contraofensiva.', (255,197,102), 105,350,9,.04,.95,85,100,6,54,140,'Normal','Disciplina humana: stamina regenera mais rápido.', 'akari'),
]

CATALOGO = {p.id: p for p in PERFIS}

def criar_personagem(identifier, x, y=None):
    profile = CATALOGO[identifier] if isinstance(identifier,str) else PERFIS[identifier]
    return PersonagemBase(x,y,profile,profile.id)

from functools import partial
ELENCO = [partial(criar_personagem, identifier) for identifier in CATALOGO]

# Compatibility aliases for the original public API.
EspadachimKensei = partial(criar_personagem, 'kensei')
HollowVastor = partial(criar_personagem, 'vastor')
AtiradorZephyr = partial(criar_personagem, 'zephyr')
GuardiaoKurogane = partial(criar_personagem, 'kurogane')
HumanaAkari = partial(criar_personagem, 'akari')
