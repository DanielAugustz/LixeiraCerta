"""Categorias de coleta seletiva, catálogo de resíduos e a classe Residuo."""

import math
import random
from dataclasses import dataclass

import pygame

from config import LARGURA, TAMANHO_RESIDUO, BRANCO, PRETO

# Cores da coleta seletiva (padrão CONAMA 275/2001).
# A tecla de cada categoria é fixa em todas as fases (Q W E R T).
CATEGORIAS = {
    "papel":    {"nome": "Papel",    "cor": (30, 100, 210), "texto": BRANCO, "tecla": "Q"},
    "plastico": {"nome": "Plástico", "cor": (210, 40, 40),  "texto": BRANCO, "tecla": "W"},
    "vidro":    {"nome": "Vidro",    "cor": (30, 150, 70),  "texto": BRANCO, "tecla": "E"},
    "metal":    {"nome": "Metal",    "cor": (235, 190, 0),  "texto": PRETO,  "tecla": "R"},
    "organico": {"nome": "Orgânico", "cor": (120, 70, 30),  "texto": BRANCO, "tecla": "T"},
}
ORDEM_CATEGORIAS = ["papel", "plastico", "vidro", "metal", "organico"]


@dataclass(frozen=True)
class TipoResiduo:
    nome: str
    categoria: str
    forma: str
    cor: tuple
    fase_minima: int
    pegadinha: bool
    explicacao: str


# Catálogo de resíduos. "fase_minima" é a primeira fase em que o item aparece.
# "pegadinha" marca itens que costumam ser descartados errado.
CATALOGO = [
    # ---- Fase 1: papel e plástico ----
    TipoResiduo("Jornal", "papel", "folha", (225, 225, 215), 1, False,
                "Papel seco e limpo vai no azul."),
    TipoResiduo("Caixa de papelão", "papel", "caixa", (190, 140, 80), 1, False,
                "Papelão é papel: desmonte e coloque no azul."),
    TipoResiduo("Folha de caderno", "papel", "folha", (250, 250, 250), 1, False,
                "Papel limpo vai no azul."),
    TipoResiduo("Garrafa PET", "plastico", "garrafa", (150, 210, 230), 1, False,
                "PET é plástico: vai no vermelho."),
    TipoResiduo("Sacola plástica", "plastico", "sacola", (240, 240, 240), 1, False,
                "Sacola é plástico: vai no vermelho."),
    TipoResiduo("Pote de margarina", "plastico", "pote", (250, 230, 120), 1, False,
                "Pote plástico vazio vai no vermelho."),

    # ---- Fase 2: entra o vidro ----
    TipoResiduo("Garrafa de vidro", "vidro", "garrafa", (60, 140, 80), 2, False,
                "Garrafa de vidro vai no verde."),
    TipoResiduo("Pote de geleia", "vidro", "pote", (180, 220, 200), 2, False,
                "Pote de vidro vazio vai no verde."),
    TipoResiduo("Garrafa de azeite", "vidro", "garrafa", (130, 150, 50), 2, False,
                "Garrafa de vidro vazia vai no verde."),
    TipoResiduo("Caixa de ovo de papelão", "papel", "caixa", (170, 150, 120), 2, True,
                "Caixa de ovo de papelão é papel: azul."),
    TipoResiduo("Tampinha de garrafa", "plastico", "tampa", (40, 120, 220), 2, True,
                "Tampinha de garrafa PET é plástico: vermelho."),

    # ---- Fase 3: entra o metal ----
    TipoResiduo("Lata de refrigerante", "metal", "lata", (200, 30, 30), 3, False,
                "Lata de alumínio é metal: amarelo."),
    TipoResiduo("Lata de sardinha", "metal", "lata", (170, 170, 180), 3, False,
                "Lata de aço é metal: amarelo."),
    TipoResiduo("Lata de milho", "metal", "lata", (220, 200, 60), 3, False,
                "Lata de aço é metal: amarelo."),
    TipoResiduo("Papel alumínio limpo", "metal", "bola", (200, 200, 210), 3, True,
                "Alumínio limpo é metal reciclável: amarelo."),
    TipoResiduo("Tampa de metal do pote", "metal", "tampa", (160, 160, 170), 3, True,
                "A tampa do pote de vidro é metal: amarelo, não verde."),

    # ---- Fase 4: entra o orgânico ----
    TipoResiduo("Casca de banana", "organico", "fruta", (240, 210, 50), 4, False,
                "Restos de comida são orgânicos: marrom."),
    TipoResiduo("Maçã mordida", "organico", "fruta", (200, 40, 40), 4, False,
                "Restos de comida são orgânicos: marrom."),
    TipoResiduo("Folha de alface", "organico", "fruta", (90, 180, 70), 4, False,
                "Restos de verdura são orgânicos: marrom."),
    TipoResiduo("Borra de café", "organico", "bola", (90, 60, 40), 4, False,
                "Borra de café é orgânica e pode virar adubo."),
    TipoResiduo("Casca de ovo", "organico", "bola", (245, 235, 210), 4, True,
                "Casca de ovo é orgânica: marrom."),
    TipoResiduo("Filtro de café usado", "organico", "folha_suja", (235, 220, 190), 4, True,
                "Filtro de papel com borra vai no orgânico, não no papel."),
]


def _escurecer(cor, qtd=60):
    return tuple(max(0, c - qtd) for c in cor)


def desenhar_forma(tela, forma, cor, r):
    """Desenha um ícone simples para o resíduo dentro do retângulo r."""
    borda = _escurecer(cor)
    w, h = r.w, r.h
    if forma.endswith("_suja"):
        # Mesma forma, com manchas: ajuda a reconhecer o item sem o nome (custo "Sem rótulo").
        desenhar_forma(tela, forma[:-5], cor, r)
        mancha = (150, 110, 40)
        for dx, dy, raio in ((-8, 2, 5), (7, 6, 4), (2, -4, 3)):
            pygame.draw.circle(tela, mancha, (r.centerx + dx, r.centery + dy), raio)
        return
    if forma == "caixa":
        corpo = pygame.Rect(r.x, r.y + h // 5, w, h * 3 // 5)
        pygame.draw.rect(tela, cor, corpo, border_radius=3)
        pygame.draw.rect(tela, borda, corpo, 2, border_radius=3)
        pygame.draw.line(tela, borda, (corpo.centerx, corpo.top), (corpo.centerx, corpo.top + 10), 2)
    elif forma == "folha":
        folha = pygame.Rect(0, 0, w * 7 // 10, h)
        folha.center = r.center
        pygame.draw.rect(tela, cor, folha)
        pygame.draw.rect(tela, borda, folha, 1)
        for i in range(1, 5):
            y = folha.top + i * h // 5
            pygame.draw.line(tela, (150, 150, 160), (folha.left + 4, y), (folha.right - 4, y), 1)
    elif forma == "garrafa":
        corpo = pygame.Rect(0, 0, w * 45 // 100, h * 62 // 100)
        corpo.midbottom = r.midbottom
        gargalo = pygame.Rect(0, 0, w * 22 // 100, h * 28 // 100)
        gargalo.midbottom = corpo.midtop
        tampa = pygame.Rect(0, 0, w * 26 // 100, h // 10)
        tampa.midbottom = gargalo.midtop
        pygame.draw.rect(tela, cor, corpo, border_radius=5)
        pygame.draw.rect(tela, cor, gargalo)
        pygame.draw.rect(tela, borda, corpo, 2, border_radius=5)
        pygame.draw.rect(tela, borda, tampa)
    elif forma == "lata":
        corpo = pygame.Rect(0, 0, w * 55 // 100, h * 85 // 100)
        corpo.center = r.center
        pygame.draw.rect(tela, cor, corpo, border_radius=4)
        topo = pygame.Rect(corpo.x, corpo.y - 3, corpo.w, 8)
        pygame.draw.ellipse(tela, (210, 210, 215), topo)
        pygame.draw.rect(tela, borda, corpo, 2, border_radius=4)
    elif forma == "pote":
        corpo = pygame.Rect(0, 0, w * 8 // 10, h * 55 // 100)
        corpo.midbottom = r.midbottom
        tampa = pygame.Rect(0, 0, w * 88 // 100, h * 15 // 100)
        tampa.midbottom = corpo.midtop
        pygame.draw.rect(tela, cor, corpo, border_radius=6)
        pygame.draw.rect(tela, borda, corpo, 2, border_radius=6)
        pygame.draw.rect(tela, borda, tampa, border_radius=3)
    elif forma == "fruta":
        raio = w * 38 // 100
        centro = (r.centerx, r.centery + 3)
        pygame.draw.circle(tela, cor, centro, raio)
        pygame.draw.circle(tela, borda, centro, raio, 2)
        pygame.draw.line(tela, (90, 60, 20), (centro[0], centro[1] - raio), (centro[0] + 4, centro[1] - raio - 8), 3)
    elif forma == "sacola":
        pontos = [(r.left + 6, r.top + 12), (r.right - 6, r.top + 12), (r.right - 2, r.bottom), (r.left + 2, r.bottom)]
        pygame.draw.polygon(tela, cor, pontos)
        pygame.draw.polygon(tela, borda, pontos, 2)
        pygame.draw.arc(tela, borda, pygame.Rect(r.left + 10, r.top, 12, 24), 0, 3.14, 2)
        pygame.draw.arc(tela, borda, pygame.Rect(r.right - 22, r.top, 12, 24), 0, 3.14, 2)
    elif forma == "bola":
        raio = w * 4 // 10
        pygame.draw.circle(tela, cor, r.center, raio)
        pygame.draw.circle(tela, borda, r.center, raio, 2)
        pygame.draw.line(tela, borda, (r.centerx - 8, r.centery - 6), (r.centerx + 6, r.centery + 2), 1)
        pygame.draw.line(tela, borda, (r.centerx - 4, r.centery + 8), (r.centerx + 9, r.centery - 5), 1)
    elif forma == "caco":
        pontos = [(r.left + 4, r.top + 10), (r.centerx, r.top), (r.right - 3, r.top + 16),
                  (r.right - 10, r.bottom - 2), (r.left + 8, r.bottom - 8)]
        pygame.draw.polygon(tela, cor, pontos)
        pygame.draw.polygon(tela, (120, 140, 150), pontos, 2)
        pygame.draw.line(tela, BRANCO, (r.centerx - 6, r.top + 10), (r.centerx + 4, r.bottom - 12), 2)
    elif forma == "tampa":
        tampa = pygame.Rect(0, 0, w * 6 // 10, h * 35 // 100)
        tampa.center = r.center
        pygame.draw.ellipse(tela, cor, tampa)
        pygame.draw.ellipse(tela, borda, tampa, 2)
    else:
        pygame.draw.rect(tela, cor, r)


# ---------------------------------------------------------------- relevo
MARGEM_RELEVO = 6                  # espaço em volta do ícone para contorno e sombra
COR_CONTORNO = (25, 25, 25, 255)
COR_SOMBRA = (0, 0, 0, 110)
COR_BRILHO = (255, 255, 255, 170)
ESPESSURA_CONTORNO = 2
DESLOCAMENTO_SOMBRA = 4
_sprites = {}                      # cache: (forma, cor) -> Surface pronta


def sprite_residuo(forma, cor):
    """Ícone do resíduo com relevo: sombra, contorno escuro e brilho no canto de cima.

    O contorno garante que o item se destaque em qualquer fundo (ex.: papel branco na
    parede clara da cozinha). Cada combinação forma+cor é montada uma vez e guardada.
    """
    chave = (forma, cor)
    if chave in _sprites:
        return _sprites[chave]
    m = MARGEM_RELEVO
    tamanho = (TAMANHO_RESIDUO + 2 * m, TAMANHO_RESIDUO + 2 * m)
    base = pygame.Surface(tamanho, pygame.SRCALPHA)
    desenhar_forma(base, forma, cor, pygame.Rect(m, m, TAMANHO_RESIDUO, TAMANHO_RESIDUO))

    silhueta = pygame.mask.from_surface(base)
    sombra = silhueta.to_surface(setcolor=COR_SOMBRA, unsetcolor=(0, 0, 0, 0))
    contorno = silhueta.to_surface(setcolor=COR_CONTORNO, unsetcolor=(0, 0, 0, 0))
    brilho = silhueta.to_surface(setcolor=COR_BRILHO, unsetcolor=(0, 0, 0, 0))

    final = pygame.Surface(tamanho, pygame.SRCALPHA)
    final.blit(sombra, (DESLOCAMENTO_SOMBRA, DESLOCAMENTO_SOMBRA))
    e = ESPESSURA_CONTORNO
    for dx in (-e, 0, e):
        for dy in (-e, 0, e):
            if dx or dy:
                final.blit(contorno, (dx, dy))
    final.blit(brilho, (-1, -1))   # borda clara em cima/esquerda = efeito de relevo
    final.blit(base, (0, 0))
    _sprites[chave] = final
    return final


class Residuo:
    """Um resíduo caindo na tela."""

    def __init__(self, tipo, x, velocidade, balanco=0.0):
        self.tipo = tipo
        self.x = float(x)
        self.y = float(-TAMANHO_RESIDUO)
        self.velocidade = velocidade
        self.balanco = balanco          # px/s de oscilação lateral (risco "Ventania")
        self.tempo = 0.0
        self.fase_balanco = random.uniform(0, 2 * math.pi)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), TAMANHO_RESIDUO, TAMANHO_RESIDUO)

    def atualizar(self, dt):
        self.tempo += dt
        self.y += self.velocidade * dt
        if self.balanco:
            self.x += math.cos(self.tempo * 2.5 + self.fase_balanco) * self.balanco * dt
            self.x = max(0.0, min(LARGURA - TAMANHO_RESIDUO, self.x))

    def desenhar(self, tela, fonte, mostrar_nome=True):
        r = self.rect
        tela.blit(sprite_residuo(self.tipo.forma, self.tipo.cor), (r.x - MARGEM_RELEVO, r.y - MARGEM_RELEVO))
        if not mostrar_nome:
            return
        # Nome do resíduo acima do ícone: o jogador precisa reconhecer o material.
        rotulo = fonte.render(self.tipo.nome, True, BRANCO)
        fundo = rotulo.get_rect(midbottom=(r.centerx, r.top - 3)).inflate(10, 4)
        pygame.draw.rect(tela, PRETO, fundo, border_radius=6)
        tela.blit(rotulo, rotulo.get_rect(center=fundo.center))
