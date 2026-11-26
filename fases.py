"""Cenários (fases), velocidade da campanha e resíduos de cada cenário."""

from config import VEL_QUEDA_CAMPANHA, INTERVALO_CAMPANHA, PESO_MATERIAL_NOVO
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


def velocidade_queda():
    """Velocidade de queda no INÍCIO de cada onda da campanha (85 px/s). Ao longo da onda ela
    sobe até 120 px/s (Partida._fator_aceleracao); as cartas multiplicam por cima."""
    return VEL_QUEDA_CAMPANHA


def intervalo_surgimento():
    """Intervalo médio entre resíduos na campanha: fixo. Só a carta Chuva de lixo muda."""
    return INTERVALO_CAMPANHA


def tipos_da_fase(numero):
    """Resíduos que podem cair no cenário e o peso de sorteio de cada um.

    Materiais que estreiam no cenário recebem peso maior, para que o jogador
    treine justamente o que acabou de aprender.
    """
    tipos = [t for t in CATALOGO if t.fase_minima <= numero]
    pesos = [PESO_MATERIAL_NOVO if (t.fase_minima == numero and numero > 1) else 1 for t in tipos]
    return tipos, pesos
