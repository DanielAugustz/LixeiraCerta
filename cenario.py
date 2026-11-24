"""Desenho dos cenários de fundo de cada fase.

Cada cenário é desenhado numa "cena" de 960x640 (ALTURA_CENA) e colado na PARTE DE BAIXO
da janela. Se a janela for mais alta, o espaço extra em cima é preenchido com a cor do
fundo (céu ou parede). Assim os resíduos caem de mais alto sem mudar o desenho do chão.
"""

import pygame

from config import LARGURA, ALTURA, Y_CHAO

ALTURA_CENA = 640   # altura em que os cenários foram desenhados


def _cozinha(tela):
    tela.fill((245, 232, 205))
    # azulejos
    for y in range(ALTURA_CENA - 200, ALTURA_CENA, 40):
        for x in range(0, LARGURA, 40):
            pygame.draw.rect(tela, (230, 240, 240), (x, y, 40, 40))
            pygame.draw.rect(tela, (200, 215, 215), (x, y, 40, 40), 1)
    # janela
    pygame.draw.rect(tela, (150, 205, 240), (620, 110, 220, 150))
    pygame.draw.rect(tela, (120, 90, 60), (620, 110, 220, 150), 8)
    pygame.draw.line(tela, (120, 90, 60), (730, 110), (730, 260), 6)
    # armário
    pygame.draw.rect(tela, (170, 120, 80), (80, 90, 320, 110), border_radius=6)
    pygame.draw.line(tela, (130, 90, 60), (240, 90), (240, 200), 4)
    # piso
    pygame.draw.rect(tela, (160, 110, 70), (0, ALTURA_CENA - 4, LARGURA, 8))


def _rua(tela):
    tela.fill((160, 205, 240))
    predios = [(0, 160, 150, (190, 170, 150)), (160, 110, 130, (210, 190, 120)),
               (300, 190, 170, (170, 180, 200)), (480, 130, 140, (200, 150, 140)),
               (630, 170, 160, (180, 200, 170)), (800, 120, 160, (210, 200, 190))]
    for x, topo, largura, cor in predios:
        pygame.draw.rect(tela, cor, (x, topo, largura, ALTURA_CENA - topo))
        for jy in range(topo + 20, ALTURA_CENA - 80, 50):
            for jx in range(x + 15, x + largura - 25, 40):
                pygame.draw.rect(tela, (240, 240, 200), (jx, jy, 20, 26))
    pygame.draw.rect(tela, (150, 150, 150), (0, ALTURA_CENA - 40, LARGURA, 40))  # calçada
    for x in range(0, LARGURA, 60):
        pygame.draw.line(tela, (120, 120, 120), (x, ALTURA_CENA - 40), (x, ALTURA_CENA), 2)


def _praia(tela):
    tela.fill((135, 200, 245))
    pygame.draw.circle(tela, (255, 220, 90), (820, 130), 50)
    pygame.draw.rect(tela, (40, 130, 200), (0, 300, LARGURA, 110))
    for x in range(0, LARGURA, 80):
        pygame.draw.arc(tela, (220, 240, 255), (x, 300, 80, 24), 3.14, 6.28, 2)
    pygame.draw.rect(tela, (235, 212, 155), (0, 410, LARGURA, ALTURA_CENA - 410))
    # coqueiro
    pygame.draw.rect(tela, (130, 90, 50), (90, 220, 14, 200))
    for dx, dy in [(-60, 20), (60, 20), (-40, -10), (40, -10)]:
        pygame.draw.line(tela, (40, 140, 60), (97, 220), (97 + dx, 220 + dy), 10)


def _feira(tela):
    tela.fill((170, 215, 245))
    pygame.draw.rect(tela, (175, 170, 160), (0, 430, LARGURA, ALTURA_CENA - 430))   # chão da rua
    listras = [((230, 60, 60), (250, 240, 230)), ((40, 140, 200), (250, 240, 230)),
               ((60, 160, 80), (250, 240, 230)), ((240, 170, 30), (250, 240, 230))]
    frutas = [(230, 50, 40), (250, 200, 40), (110, 190, 70), (240, 130, 30), (150, 60, 140)]
    for i, (cor_a, cor_b) in enumerate(listras):
        x = 20 + i * 240
        # toldo listrado
        for k in range(8):
            cor = cor_a if k % 2 == 0 else cor_b
            pygame.draw.rect(tela, cor, (x + k * 25, 230, 25, 40))
        pygame.draw.polygon(tela, cor_a, [(x, 270), (x + 200, 270), (x + 200, 282), (x, 282)])
        # estacas
        pygame.draw.rect(tela, (110, 80, 50), (x + 4, 270, 8, 200))
        pygame.draw.rect(tela, (110, 80, 50), (x + 188, 270, 8, 200))
        # banca com caixotes de frutas
        pygame.draw.rect(tela, (150, 105, 60), (x, 380, 200, 60))
        for c in range(3):
            caixote = pygame.Rect(x + 10 + c * 63, 350, 56, 34)
            pygame.draw.rect(tela, (190, 140, 80), caixote)
            cor_fruta = frutas[(i + c) % len(frutas)]
            for f in range(4):
                pygame.draw.circle(tela, cor_fruta, (caixote.x + 9 + f * 13, caixote.y + 4), 7)


CENARIOS = {"cozinha": _cozinha, "rua": _rua, "praia": _praia, "feira": _feira}


_cenas = {}   # cache: nome -> Surface do tamanho da janela (o fundo não muda)


def _cena(nome):
    if nome not in _cenas:
        desenho = pygame.Surface((LARGURA, ALTURA_CENA))
        CENARIOS[nome](desenho)
        cena = pygame.Surface((LARGURA, ALTURA))
        cena.fill(desenho.get_at((0, 0)))              # espaço extra em cima = cor do fundo
        cena.blit(desenho, (0, ALTURA - ALTURA_CENA))   # cenário colado embaixo
        _cenas[nome] = cena
    return _cenas[nome]


def desenhar_cenario(tela, nome, sujeira=()):
    tela.blit(_cena(nome), (0, 0))
    # Resíduos que caíram no chão ficam visíveis: a cena vai ficando suja.
    for x, cor in sujeira:
        pygame.draw.ellipse(tela, cor, (x, Y_CHAO - 12, 30, 14))
        pygame.draw.ellipse(tela, (60, 60, 60), (x, Y_CHAO - 12, 30, 14), 1)


_sombras = {}   # cache: alpha -> Surface (evita criar uma tela nova a cada quadro)


def escurecer_tela(tela, alpha=150):
    if alpha not in _sombras:
        sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, alpha))
        _sombras[alpha] = sombra
    tela.blit(_sombras[alpha], (0, 0))
