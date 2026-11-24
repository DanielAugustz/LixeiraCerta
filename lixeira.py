"""A lixeira controlada pelo jogador."""

import pygame

from config import (LARGURA, Y_CHAO, LARGURA_LIXEIRA, ALTURA_LIXEIRA, VEL_LIXEIRA,
                    DURACAO_FLASH, BRANCO, VERDE_OK, VERMELHO_ERRO)
from residuo import CATEGORIAS


class Lixeira:
    def __init__(self, categorias, mult_largura=1.0, mult_velocidade=1.0):
        self.categorias = list(categorias)   # categorias liberadas no cenário
        self.indice = 0
        self.largura = int(LARGURA_LIXEIRA * mult_largura)  # carta "Lixeira larga"
        self.velocidade = VEL_LIXEIRA * mult_velocidade     # custo "Lixeira pesada"
        self.x = LARGURA / 2 - self.largura / 2
        self.y = Y_CHAO - ALTURA_LIXEIRA
        self.tempo_flash = 0.0
        self.cor_flash = BRANCO

    @property
    def categoria(self):
        return self.categorias[self.indice]

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.largura, ALTURA_LIXEIRA)

    @property
    def boca(self):
        """Área no topo da lixeira que recebe os resíduos."""
        return pygame.Rect(int(self.x) + 6, int(self.y) - 8, self.largura - 12, 24)

    def mover(self, direcao, dt):
        self.x += direcao * self.velocidade * dt
        self.x = max(0, min(LARGURA - self.largura, self.x))

    def selecionar(self, categoria):
        """Troca para uma categoria específica (teclas Q W E R T)."""
        if categoria in self.categorias:
            self.indice = self.categorias.index(categoria)
            return True
        return False

    def receber(self, residuo):
        """Recebe um resíduo e diz se ele foi para a lixeira certa."""
        acertou = residuo.tipo.categoria == self.categoria
        self.tempo_flash = DURACAO_FLASH
        self.cor_flash = VERDE_OK if acertou else VERMELHO_ERRO
        return acertou

    def atualizar(self, dt):
        self.tempo_flash = max(0.0, self.tempo_flash - dt)

    def desenhar(self, tela, fonte):
        dados = CATEGORIAS[self.categoria]
        cor = dados["cor"]
        r = self.rect

        if self.tempo_flash > 0:
            pygame.draw.rect(tela, self.cor_flash, r.inflate(16, 16), border_radius=12)

        corpo = [(r.left + 8, r.top + 14), (r.right - 8, r.top + 14),
                 (r.right - 16, r.bottom), (r.left + 16, r.bottom)]
        pygame.draw.polygon(tela, cor, corpo)
        pygame.draw.polygon(tela, (30, 30, 30), corpo, 3)

        tampa = pygame.Rect(r.left, r.top, r.w, 16)
        escuro = tuple(max(0, c - 50) for c in cor)
        pygame.draw.rect(tela, escuro, tampa, border_radius=5)
        pygame.draw.rect(tela, (30, 30, 30), tampa, 2, border_radius=5)

        nome = fonte.render(dados["nome"], True, dados["texto"])
        tela.blit(nome, nome.get_rect(center=(r.centerx, r.centery + 10)))
