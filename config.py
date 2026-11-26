"""Todos os números do jogo ficam aqui.

Concentrar os parâmetros em um único arquivo facilita o balanceamento
e a rastreabilidade com o GDD (seção 13).
"""

# ---------------- Janela ----------------
LARGURA = 960
ALTURA = 760   # mais alta = os resíduos caem de mais alto (mais tempo para mover a lixeira)
FPS = 60
TITULO = "Lixeira Certa"

# ---------------- Layout ----------------
ALTURA_HUD = 56          # barra superior (onda, tempo, pontos, vidas)
Y_CHAO = ALTURA          # linha em que o resíduo "cai no chão" (base da tela)
RAIO_BOLINHA = 13        # bolinhas de cor das lixeiras no canto inferior esquerdo
ESPACO_BOLINHA = 36

# ---------------- Lixeira ----------------
LARGURA_LIXEIRA = 110
ALTURA_LIXEIRA = 100
VEL_LIXEIRA = 480        # pixels por segundo

# ---------------- Estrutura da run (roguelike) ----------------
DURACAO_ONDA = 30        # segundos por onda
ONDAS_POR_FASE = 2       # ondas em cada cenário
# total de ondas = ONDAS_POR_FASE x número de cenários (4) = 8

# ---------------- Resíduos e dificuldade ----------------
TAMANHO_RESIDUO = 44
# Campanha: em CADA onda a queda começa em 85 px/s e acelera aos poucos até 120 px/s
# no fim dos 30 s; a lixeira acelera na mesma proporção, para sempre dar tempo de
# alcançar. A onda seguinte recomeça em 85. As cartas agem por cima disso: o custo
# "Queda rápida" (x1,2) e "Chuva de lixo" valem na onda seguinte; "Câmera lenta" freia.
VEL_QUEDA_CAMPANHA = 85              # px/s no início de cada onda
VEL_QUEDA_CAMPANHA_FIM = 120         # px/s no fim de cada onda
INTERVALO_CAMPANHA = 1.7             # segundos entre resíduos (fixo)
VEL_QUEDA_INFINITO = 110             # px/s no início do modo infinito (antes da dificuldade)
PESO_MATERIAL_NOVO = 3               # material novo do cenário aparece 3x mais

# ---------------- Regras ----------------
VIDAS_INICIAIS = 5
VIDAS_MAX = 7            # limite de vidas (cartas não passam disso)
VIDA_BONUS_FASE = 1      # vida recuperada ao chegar num cenário novo
PONTOS_ACERTO = 10
BONUS_COMBO = 2          # pontos extras por acerto seguido
COMBO_MAX = 10           # limite do bônus de combo
PENALIDADE_CHAO = 5      # pontos perdidos quando o resíduo cai no chão

# ---------------- Cartas: vantagens (valem a run inteira) ----------------
BONUS_LARGURA_CARTA = 0.20   # "Lixeira larga": +20% de largura por carta
LARGURA_MAX_MULT = 1.60      # limite da largura (3 cartas)
REDUCAO_VEL_CARTA = 0.12     # "Câmera lenta": -12% de velocidade por carta
VEL_MIN_MULT = 0.64          # limite da redução (3 cartas)

# ---------------- Cartas: custos (valem só na próxima onda) ----------------
BALANCO_VENTO = 110          # "Ventania": px/s de balanço lateral dos resíduos
FATOR_INTERVALO_CHUVA = 0.5  # "Chuva de lixo": metade do intervalo = o dobro de resíduos
FATOR_LIXEIRA_LENTA = 0.70   # "Lixeira pesada": lixeira 30% mais lenta
FATOR_QUEDA_RAPIDA = 1.20    # "Queda rápida": resíduos 20% mais rápidos
DANO_ERRO_DOBRADO = 2        # "Erro dobrado": vidas perdidas por erro

# ---------------- Eventos ----------------
CHANCE_EVENTO = 0.40     # chance de uma onda ter evento (exceto a 1ª de cada cenário)
PESO_EVENTO = 4          # peso extra das categorias favorecidas pelo evento

# ---------------- Tela de fim ----------------
DURACAO_CONTAGEM = 1.6      # segundos que os pontos levam contando de 0 até o total
DURACAO_PULO = 0.25         # "pulo" do número quando a contagem termina
INTERVALO_TIC = 0.06        # som de "tic" a cada 0,06 s durante a contagem

# ---------------- Visual ----------------
ESCURECER_FUNDO_JOGO = 45   # 0 a 255: quanto o cenário escurece durante o jogo (itens se destacam)

# ---------------- Retorno ao jogador ----------------
DURACAO_MENSAGEM = 3.5   # segundos que a explicação fica na tela
DURACAO_FLASH = 0.35     # segundos do brilho verde/vermelho na lixeira
DURACAO_TEXTO_FLUTUANTE = 0.9

# ---------------- Modo infinito ----------------
# A dificuldade define tudo junto:
#   lixeiras    = quantas lixeiras (na ordem Papel, Plástico, Vidro, Metal, Orgânico)
#   vidas       = vidas iniciais
#   velocidade  = velocidade de queda dos itens (multiplica VEL_QUEDA_INFINITO)
#   intervalo   = segundos entre resíduos no começo
#   acel_etapa  = quanto a queda acelera a cada etapa (a cada SEGUNDOS_POR_ETAPA)
DIFICULDADES = {
    "Fácil":   {"lixeiras": 3, "vidas": 7, "velocidade": 0.8, "intervalo": 2.0, "acel_etapa": 0.05},
    "Normal":  {"lixeiras": 4, "vidas": 5, "velocidade": 1.0, "intervalo": 1.6, "acel_etapa": 0.08},
    "Difícil": {"lixeiras": 5, "vidas": 3, "velocidade": 1.3, "intervalo": 1.2, "acel_etapa": 0.12},
}
SEGUNDOS_POR_ETAPA = 45          # a velocidade sobe em degraus, a cada 45 segundos
ACEL_MAX_INFINITO = 2.0          # a queda acelera no máximo até 2x
REDUCAO_INTERVALO_ETAPA = 0.06   # -6% no intervalo entre resíduos a cada etapa
INTERVALO_MIN_MULT = 0.45        # limite da redução do intervalo
VIDAS_MAX_INFINITO = 10
PONTOS_PRIMEIRA_CARTA = 300      # primeira carta ao chegar em 300 pontos
CRESCIMENTO_CARTA = 1.3          # cada carta seguinte pede 30% mais pontos
DURACAO_CUSTO_INFINITO = 30      # segundos que o custo da carta dura no infinito
LIMITE_SUJEIRA = 40              # quantas manchas de sujeira ficam no chão

# ---------------- Música ambiente ----------------
VOLUME_MUSICA = 0.12     # 0 a 1 (bem baixo: só ambiente, sem abafar os efeitos)
FADE_MUSICA_MS = 800     # entrada suave ao trocar de música
MUSICA_MENU = "praia"    # faixa das telas de menu, instruções e resultado

# ---------------- Métricas ----------------
PASTA_METRICAS = "metricas"
ARQUIVO_METRICAS = "partidas.csv"

# ---------------- Cores da interface ----------------
BRANCO = (255, 255, 255)
PRETO = (20, 20, 20)
CINZA_ESCURO = (40, 44, 52)
VERDE_OK = (60, 200, 90)
VERMELHO_ERRO = (230, 60, 60)
AMARELO_DESTAQUE = (255, 210, 60)
AZUL_INFO = (90, 170, 255)
