"""Cenários (fases) e fórmulas de dificuldade por onda."""

from config import (VEL_QUEDA_BASE, ACELERACAO_ONDA, INTERVALO_BASE,
                    REDUCAO_INTERVALO_ONDA, PESO_MATERIAL_NOVO)
from residuo import CATALOGO

FASES = [
    {
        "numero": 1,
        "nome": "Cozinha de casa",
        "cenario": "cozinha",
        "categorias": ["papel", "plastico"],
        "novidades": [
            "Comece pelo básico: PAPEL (azul, tecla Q) e PLÁSTICO (vermelho, tecla W).",
            "Leia o nome do resíduo e troque a cor da lixeira antes de pegá-lo.",
        ],
    },
    {
        "numero": 2,
        "nome": "Rua do bairro",
        "cenario": "rua",
        "categorias": ["papel", "plastico", "vidro"],
        "novidades": [
            "Nova lixeira: VIDRO (verde, tecla E).",
            "Atenção: caixa de ovo de papelão e tampinha de garrafa também caem!",
        ],
    },
    {
        "numero": 3,
        "nome": "Orla da lagoa",
        "cenario": "praia",
        "categorias": ["papel", "plastico", "vidro", "metal"],
        "novidades": [
            "Nova lixeira: METAL (amarelo, tecla R).",
            "Cuidado: a tampa do pote de vidro é metal, não vidro!",
        ],
    },
    {
        "numero": 4,
        "nome": "Feira livre",
        "cenario": "feira",
        "categorias": ["papel", "plastico", "vidro", "metal", "organico"],
        "novidades": [
            "Nova lixeira: ORGÂNICO (marrom, tecla T) para restos de comida.",
            "Filtro de café usado e casca de ovo também são orgânicos!",
        ],
    },
]


def velocidade_queda(onda_no_cenario):
    """Velocidade inicial de queda. 'onda_no_cenario' é 0 na 1ª onda de cada cenário:
    todo cenário começa devagar (introdução da lixeira nova) e acelera nas ondas seguintes."""
    return VEL_QUEDA_BASE * (1 + ACELERACAO_ONDA * onda_no_cenario)


def intervalo_surgimento(onda_no_cenario):
    """Intervalo médio entre resíduos; também reinicia a cada cenário."""
    return INTERVALO_BASE * (1 - REDUCAO_INTERVALO_ONDA) ** onda_no_cenario


def tipos_da_fase(numero):
    """Resíduos que podem cair no cenário e o peso de sorteio de cada um.

    Materiais que estreiam no cenário recebem peso maior, para que o jogador
    treine justamente o que acabou de aprender.
    """
    tipos = [t for t in CATALOGO if t.fase_minima <= numero]
    pesos = [PESO_MATERIAL_NOVO if (t.fase_minima == numero and numero > 1) else 1 for t in tipos]
    return tipos, pesos
