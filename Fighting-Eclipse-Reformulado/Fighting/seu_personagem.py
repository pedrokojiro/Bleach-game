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

PERFIS = [
    Perfil('Kensei', 'A LÂMINA DO ECLIPSE', 'Equilíbrio, alcance e cancelamentos rápidos.', (99,205,247), 110,330,10,.05,1,95,110,7,58,142,'Fácil','Disciplina: mais reiatsu ao acertar.'),
    Perfil('Vastor', 'O REI SEM COROA', 'Força devastadora; recuperações vulneráveis.', (245,104,87), 145,245,14,.10,1.6,82,90,5,88,166,'Normal','Tenacidade: armadura no ataque forte.'),
    Perfil('Zephyr', 'A VOZ DAS ESTRELAS', 'Controle de espaço, mobilidade e pouca vida.', (117,236,195), 90,390,8,.02,.8,78,130,9,48,138,'Difícil','Fluidez: dash com mais invulnerabilidade.'),
    Perfil('Kurogane', 'O ÚLTIMO BASTIÃO', 'Resiste à pressão e pune a imprudência.', (187,155,244), 130,265,10,.18,1.35,85,110,6,78,151,'Normal','Guarda: parry longo e reiatsu ao bloquear.'),
]

class EspadachimKensei(PersonagemBase):
    def __init__(self,x,y=None):
        super().__init__(x,y,PERFIS[0],0)

class HollowVastor(PersonagemBase):
    def __init__(self,x,y=None):
        super().__init__(x,y,PERFIS[1],1)

class AtiradorZephyr(PersonagemBase):
    def __init__(self,x,y=None):
        super().__init__(x,y,PERFIS[2],2)

class GuardiaoKurogane(PersonagemBase):
    def __init__(self,x,y=None):
        super().__init__(x,y,PERFIS[3],3)

ELENCO = [EspadachimKensei,HollowVastor,AtiradorZephyr,GuardiaoKurogane]
