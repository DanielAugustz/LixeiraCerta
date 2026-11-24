"""Música ambiente: uma faixa em loop para cada cenário.

Os arquivos ficam em musicas/<cenario>.wav (gerados por gerar_musicas.py).
Para usar outra música, basta substituir o arquivo com o mesmo nome.
Se o arquivo não existir ou não houver saída de som, o jogo segue sem música.
"""

import os
import sys

import pygame

from config import VOLUME_MUSICA, FADE_MUSICA_MS


def pasta_recursos():
    """Pasta dos arquivos do jogo (funciona também dentro do .exe)."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


class Musica:
    def __init__(self):
        self.ativa = pygame.mixer.get_init() is not None
        self.ligada = True
        self.atual = None

    def tocar(self, nome):
        """Troca para a faixa 'nome' (não faz nada se ela já está tocando)."""
        if not self.ativa or nome == self.atual:
            return
        self.atual = nome
        if not self.ligada:
            return
        caminho = os.path.join(pasta_recursos(), "musicas", f"{nome}.wav")
        if not os.path.exists(caminho):
            pygame.mixer.music.stop()
            return
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(VOLUME_MUSICA)
            pygame.mixer.music.play(-1, fade_ms=FADE_MUSICA_MS)
        except pygame.error:
            self.ativa = False

    def alternar(self):
        """Liga/desliga a música (tecla M)."""
        self.ligada = not self.ligada
        if self.ligada:
            nome, self.atual = self.atual, None
            if nome:
                self.tocar(nome)
        elif self.ativa:
            pygame.mixer.music.stop()
