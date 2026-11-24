"""Loja de upgrades permanentes. Eles só valem no MODO INFINITO e só na DIFICULDADE
em que foram comprados (cada dificuldade tem sua carteira e seus upgrades).

Como as cartas, os upgrades ajudam a pegar os resíduos, nunca a escolher a cor.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Upgrade:
    id: str
    nome: str
    descricao: str
    nivel_max: int
    custo_base: int   # preço do nível N = custo_base x N

    def preco(self, nivel_atual):
        return self.custo_base * (nivel_atual + 1)


UPGRADES = [
    Upgrade("velocidade", "Lixeira veloz", "+10% de velocidade da lixeira por nível", 5, 1000),
    Upgrade("largura", "Boca larga", "+8% de largura da lixeira por nível", 5, 1250),
    Upgrade("vida", "Vida extra", "+1 vida no começo da partida por nível", 3, 2000),
    Upgrade("escudo", "Escudo inicial", "Começa com +1 escudo por nível", 3, 1750),
    Upgrade("combo", "Combo turbinado", "+1 ponto de bônus por acerto seguido por nível", 5, 1500),
    Upgrade("pontos", "Mais pontos", "+2 pontos por resíduo na lixeira certa por nível", 5, 1500),
]

# Efeito de cada nível
BONUS_VELOCIDADE_NIVEL = 0.10
BONUS_LARGURA_NIVEL = 0.08
BONUS_PONTOS_NIVEL = 2


def comprar(progresso, dificuldade, upgrade):
    """Compra o próximo nível NA DIFICULDADE escolhida, se a carteira dela tiver pontos.
    Retorna True se comprou."""
    nivel = progresso.nivel(dificuldade, upgrade.id)
    if nivel >= upgrade.nivel_max:
        return False
    preco = upgrade.preco(nivel)
    if progresso.carteira(dificuldade) < preco:
        return False
    progresso.comprar_nivel(dificuldade, upgrade.id, preco)
    return True
