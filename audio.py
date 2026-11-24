"""Efeitos sonoros gerados por código (não dependem de arquivos de áudio).

Se o computador não tiver saída de som, o jogo continua funcionando em silêncio.
"""

import array
import math

import pygame


class Sons:
    def __init__(self):
        self.ativo = False
        self._sons = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._sons = {
                "acerto": self._tom([660, 990], 0.07),
                "erro": self._tom([220, 160], 0.14),
                "chao": self._tom([300], 0.08, volume=0.25),
                "troca": self._tom([520], 0.03, volume=0.15),
                "fase": self._tom([523, 659, 784], 0.11),
            }
            self.ativo = True
        except pygame.error:
            self.ativo = False

    @staticmethod
    def _tom(frequencias, duracao, volume=0.35):
        taxa, _, canais = pygame.mixer.get_init()
        amostras = array.array("h")
        for freq in frequencias:
            n = int(taxa * duracao)
            for i in range(n):
                envelope = 1 - i / n
                valor = int(32767 * volume * envelope * math.sin(2 * math.pi * freq * i / taxa))
                for _ in range(canais):
                    amostras.append(valor)
        return pygame.mixer.Sound(buffer=amostras.tobytes())

    def tocar(self, nome):
        if self.ativo and nome in self._sons:
            self._sons[nome].play()
