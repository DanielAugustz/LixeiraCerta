"""Cartas da run: entre uma onda e outra o jogador escolhe 1 de 3.

Toda carta é uma troca:
  - VANTAGEM: vale pelo resto da run.
  - CUSTO: vale só na próxima onda.
As vantagens ajudam a PEGAR os resíduos, nunca a acertar a cor por você:
a decisão de separar continua sendo do jogador.
"""

import random
from dataclasses import dataclass

from config import BONUS_LARGURA_CARTA, LARGURA_MAX_MULT, REDUCAO_VEL_CARTA, VEL_MIN_MULT

# Custos possíveis (aplicados em Partida.iniciar_onda)
CUSTOS = {
    "vento":         "Ventania",
    "chuva":         "Chuva de lixo",
    "sem_rotulo":    "Sem rótulo",
    "lixeira_lenta": "Lixeira pesada",
    "queda_rapida":  "Queda rápida",
    "erro_duplo":    "Erro dobrado",
}


@dataclass(frozen=True)
class Carta:
    id: str
    nome: str
    vantagem: tuple    # linhas curtas para caber na carta
    custo: str         # chave de CUSTOS
    texto_custo: tuple
    unica: bool = False


CARTAS = [
    Carta("larga", "Lixeira larga",
          ("Boca da lixeira", "20% maior."),
          "vento", ("Próxima onda: os", "resíduos balançam.")),
    Carta("lenta", "Câmera lenta",
          ("Resíduos caem", "12% mais devagar."),
          "chuva", ("Próxima onda: cai", "o dobro de resíduos.")),
    Carta("escudo", "Segunda chance",
          ("O próximo erro", "não tira vida."),
          "sem_rotulo", ("Próxima onda: os", "nomes somem.")),
    Carta("combo", "Combo de mestre",
          ("O bônus por acertos", "seguidos dobra."),
          "lixeira_lenta", ("Próxima onda: lixeira", "30% mais lenta."), unica=True),
    Carta("vassoura", "Vassoura",
          ("Resíduo no chão não", "tira mais pontos."),
          "queda_rapida", ("Próxima onda: queda", "20% mais rápida."), unica=True),
    Carta("coracao", "Coração",
          ("Ganha +1 vida.", "(até o limite de vidas)"),
          "erro_duplo", ("Próxima onda: cada", "erro tira 2 vidas.")),
]

CARTAS_POR_ID = {c.id: c for c in CARTAS}


def carta_disponivel(carta, partida):
    """Tira da oferta as cartas cuja vantagem não teria efeito."""
    if carta.unica and carta.id in partida.cartas:
        return False
    if carta.id == "larga" and partida.mod_largura >= LARGURA_MAX_MULT - 1e-6:
        return False
    if carta.id == "lenta" and partida.mod_velocidade <= VEL_MIN_MULT + 1e-6:
        return False
    if carta.id == "coracao" and partida.vidas >= partida.vidas_max:
        return False
    return True


def sortear_oferta(partida):
    """Sorteia até 3 cartas diferentes entre as disponíveis."""
    disponiveis = [c for c in CARTAS if carta_disponivel(c, partida)]
    return random.sample(disponiveis, min(3, len(disponiveis)))


def aplicar_carta(partida, carta):
    partida.cartas.append(carta.id)
    if carta.id == "larga":
        partida.mod_largura = min(LARGURA_MAX_MULT, partida.mod_largura + BONUS_LARGURA_CARTA)
    elif carta.id == "lenta":
        partida.mod_velocidade = max(VEL_MIN_MULT, partida.mod_velocidade - REDUCAO_VEL_CARTA)
    elif carta.id == "escudo":
        partida.escudos += 1
    elif carta.id == "combo":
        partida.combo_duplo = True
    elif carta.id == "vassoura":
        partida.chao_sem_penalidade = True
    elif carta.id == "coracao":
        partida.vidas = min(partida.vidas_max, partida.vidas + 1)
    partida.custo = carta.custo   # campanha: próxima onda; infinito: alguns segundos


def resumo_cartas(ids):
    """'Lixeira larga x2, Vassoura' a partir da lista de ids escolhidos."""
    contagem = {}
    for i in ids:
        contagem[i] = contagem.get(i, 0) + 1
    partes = []
    for i, n in contagem.items():
        nome = CARTAS_POR_ID[i].nome
        partes.append(f"{nome} x{n}" if n > 1 else nome)
    return ", ".join(partes)
