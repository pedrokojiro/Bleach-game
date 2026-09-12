"""Keyboard controller adapter retained under the original public module name."""
from input_manager import InputManager

class PersonagemHumanoTeclado:
    def __init__(self,personagem,setas=False,input_manager=None):
        self.personagem=personagem
        self.index=int(setas)
        self.input=input_manager or InputManager()
    def processar_input(self,outro_personagem=None):
        self.input.apply(self.index,self.personagem)

PersonagemHumano=PersonagemHumanoTeclado
