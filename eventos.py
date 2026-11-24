"""Eventos sorteados que mudam quais resíduos caem em uma onda."""

import random

from config import CHANCE_EVENTO, ONDAS_POR_FASE, PESO_EVENTO

EVENTOS = {
    "feira": {
        "nome": "Dia de feira",
        "descricao": "Muito resto de comida: orgânico aparece mais.",
        "favorece": ["organico"],
        "fase_minima": 4,
    },
    "mudanca": {
        "nome": "Dia de mudança",
        "descricao": "Caixas e papéis por todo lado.",
        "favorece": ["papel"],
        "fase_minima": 1,
    },
    "festa": {
        "nome": "Depois da festa",
        "descricao": "Garrafas e latas: vidro e metal aparecem mais.",
        "favorece": ["vidro", "metal"],
        "fase_minima": 3,
    },
    "pegadinha": {
        "nome": "Onda das pegadinhas",
        "descricao": "Só caem os itens que mais confundem!",
        "so_pegadinhas": True,
        "fase_minima": 3,
    },
}


def sortear_evento(indice_onda, numero_fase):
    """A 1ª onda de cada cenário nunca tem evento: é a hora de aprender o material novo."""
    if indice_onda % ONDAS_POR_FASE == 0 or random.random() >= CHANCE_EVENTO:
        return None
    possiveis = [chave for chave, e in EVENTOS.items() if e["fase_minima"] <= numero_fase]
    return random.choice(possiveis)


def aplicar_evento(tipos, pesos, evento):
    """Ajusta a lista de resíduos e os pesos de sorteio conforme o evento."""
    if evento is None:
        return tipos, pesos
    dados = EVENTOS[evento]
    if dados.get("so_pegadinhas"):
        filtrados = [(t, p) for t, p in zip(tipos, pesos) if t.pegadinha]
        return [t for t, _ in filtrados], [1] * len(filtrados)
    novos_pesos = [p * PESO_EVENTO if t.categoria in dados["favorece"] else p
                   for t, p in zip(tipos, pesos)]
    return tipos, novos_pesos
