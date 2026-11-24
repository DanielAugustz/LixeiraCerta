"""Modo infinito: um mapa só, sem fim.

- A dificuldade define quantas lixeiras (Fácil 3, Normal 4, Difícil 5), vidas e velocidade.

- A dificuldade sobe com o tempo (queda mais rápida, resíduos mais seguidos).
- A cada X pontos aparece uma escolha de cartas; o custo da carta dura alguns segundos.
- Upgrades comprados na loja (loja.py) valem só aqui.
- Acaba quando as vidas acabam; os pontos vão para a carteira (progresso.py).
"""

from cartas import aplicar_carta, sortear_oferta, CUSTOS
from config import (VEL_QUEDA_BASE, VEL_LIXEIRA, LARGURA, LARGURA_LIXEIRA, BONUS_COMBO, PONTOS_ACERTO,
                    DIFICULDADES, ACEL_MAX_INFINITO, REDUCAO_INTERVALO_ETAPA, SEGUNDOS_POR_ETAPA,
                    INTERVALO_MIN_MULT, VIDAS_MAX_INFINITO, PONTOS_PRIMEIRA_CARTA, CRESCIMENTO_CARTA,
                    DURACAO_CUSTO_INFINITO, LIMITE_SUJEIRA, BALANCO_VENTO, FATOR_INTERVALO_CHUVA,
                    FATOR_LIXEIRA_LENTA, FATOR_QUEDA_RAPIDA, DANO_ERRO_DOBRADO, VERMELHO_ERRO,
                    AZUL_INFO)
from fases import FASES
from lixeira import Lixeira
from loja import BONUS_VELOCIDADE_NIVEL, BONUS_LARGURA_NIVEL, BONUS_PONTOS_NIVEL
from partida import Partida
from residuo import CATALOGO, ORDEM_CATEGORIAS


class PartidaInfinita(Partida):
    infinito = True

    def __init__(self, sons, progresso, indice_mapa, dificuldade):
        super().__init__(sons)
        self.mapa = FASES[indice_mapa]
        self.dificuldade = dificuldade
        dados = DIFICULDADES[dificuldade]
        self.categorias = ORDEM_CATEGORIAS[:dados["lixeiras"]]   # Fácil 3, Normal 4, Difícil 5
        self.acel_etapa = dados["acel_etapa"]
        self.etapa = 0          # sobe 1 a cada SEGUNDOS_POR_ETAPA (velocidade em degraus)
        self.intervalo_inicial = dados["intervalo"]
        self.mult_vel_itens = dados["velocidade"]

        # Upgrades comprados na loja DESTA dificuldade (só valem neste modo e nesta dificuldade)
        def nivel(upgrade_id):
            return progresso.nivel(dificuldade, upgrade_id)

        self.upgrades_usados = progresso.upgrades(dificuldade)
        self.vidas_max = VIDAS_MAX_INFINITO
        self.vidas = min(self.vidas_max, dados["vidas"] + nivel("vida"))
        self.escudos = nivel("escudo")
        self.mod_largura = 1 + BONUS_LARGURA_NIVEL * nivel("largura")
        self.mult_lixeira = 1 + BONUS_VELOCIDADE_NIVEL * nivel("velocidade")
        self.bonus_combo = BONUS_COMBO + nivel("combo")
        self.pontos_acerto = PONTOS_ACERTO + BONUS_PONTOS_NIVEL * nivel("pontos")

        # Cartas por pontos
        self.passo_carta = PONTOS_PRIMEIRA_CARTA
        self.proxima_carta = PONTOS_PRIMEIRA_CARTA
        self.tempo_custo = 0.0

        # Métricas por minuto
        self.blocos = []
        self._inicio_bloco = 0.0
        self._base = (0, 0, 0)
        self._itens_bloco = []

        self._iniciar()

    @property
    def fase(self):
        return self.mapa

    @property
    def minutos(self):
        return self.tempo / 60

    def _iniciar(self):
        self.lixeira = Lixeira(self.categorias, self.mod_largura, self.mult_lixeira)
        self.residuos = []
        self.tempo = 0.0
        self.proximo_surgimento = 1.0
        self.acertos = 0
        self.erros = 0
        self.caidos = 0
        self.combo = 0
        self.itens_errados = []
        self.sujeira = []
        self.mensagem = None
        self.tempo_mensagem = 0.0
        self.textos = []
        self.onda_concluida = False
        self.tipos = [t for t in CATALOGO if t.categoria in self.categorias]
        self.pesos = [1] * len(self.tipos)
        self._aplicar_custo()

    # ------------------------------------------------------------ dificuldade
    def _aplicar_custo(self):
        """Liga/desliga os efeitos do custo da carta atual."""
        self.mostrar_nomes = self.custo != "sem_rotulo"
        self.balanco = BALANCO_VENTO if self.custo == "vento" else 0.0
        self.dano_erro = DANO_ERRO_DOBRADO if self.custo == "erro_duplo" else 1
        lenta = FATOR_LIXEIRA_LENTA if self.custo == "lixeira_lenta" else 1.0
        self.lixeira.velocidade = VEL_LIXEIRA * self.mult_lixeira * lenta

    def _velocidade_atual(self):
        aceleracao = min(ACEL_MAX_INFINITO, 1 + self.acel_etapa * self.etapa)
        rapida = FATOR_QUEDA_RAPIDA if self.custo == "queda_rapida" else 1.0
        return VEL_QUEDA_BASE * self.mult_vel_itens * self.mod_velocidade * aceleracao * rapida

    def _intervalo_atual(self):
        reducao = max(INTERVALO_MIN_MULT, 1 - REDUCAO_INTERVALO_ETAPA * self.etapa)
        chuva = FATOR_INTERVALO_CHUVA if self.custo == "chuva" else 1.0
        return self.intervalo_inicial * reducao * chuva

    def _pode_surgir(self):
        return True   # nunca acaba

    # ------------------------------------------------------------ cartas
    def escolher_carta(self, indice):
        carta = self.oferta[indice]
        aplicar_carta(self, carta)
        self.oferta = []
        self.onda_concluida = False
        self.tempo_custo = DURACAO_CUSTO_INFINITO
        self.lixeira.largura = int(LARGURA_LIXEIRA * self.mod_largura)
        self.lixeira.x = min(self.lixeira.x, LARGURA - self.lixeira.largura)
        self._aplicar_custo()
        self._mensagem(f"Custo: {CUSTOS[self.custo]}", f"Dura {DURACAO_CUSTO_INFINITO} segundos.",
                       VERMELHO_ERRO)

    # ------------------------------------------------------------ laço
    def atualizar(self, dt, teclas):
        self._atualizar_jogo(dt, teclas)
        if len(self.sujeira) > LIMITE_SUJEIRA:
            del self.sujeira[:-LIMITE_SUJEIRA]

        # Velocidade sobe em degraus a cada SEGUNDOS_POR_ETAPA
        etapa = int(self.tempo // SEGUNDOS_POR_ETAPA)
        if etapa > self.etapa:
            self.etapa = etapa
            self._mensagem(f"Mais rápido! Nível {self.etapa + 1}",
                           f"A cada {SEGUNDOS_POR_ETAPA} segundos os resíduos caem mais rápido.", AZUL_INFO)
            self.sons.tocar("troca")

        if self.custo:
            self.tempo_custo -= dt
            if self.tempo_custo <= 0:
                self.custo = None
                self._aplicar_custo()
                self._mensagem("O custo acabou!", "Tudo voltou ao normal.", AZUL_INFO)

        if self.tempo - self._inicio_bloco >= 60:
            self._fechar_bloco()

        if self.vidas <= 0:
            self._fechar_bloco()
            self.terminou = True
        elif self.pontos >= self.proxima_carta:
            self.passo_carta = int(self.passo_carta * CRESCIMENTO_CARTA)
            self.proxima_carta += self.passo_carta
            self.oferta = sortear_oferta(self)
            if self.oferta:
                self.onda_concluida = True     # main.py abre a tela de cartas
                self.sons.tocar("fase")

    def _fechar_bloco(self):
        """Guarda as métricas do último minuto jogado."""
        duracao = self.tempo - self._inicio_bloco
        if duracao < 1:
            return
        acertos = self.acertos - self._base[0]
        erros = self.erros - self._base[1]
        caidos = self.caidos - self._base[2]
        tentativas = acertos + erros
        self.blocos.append({
            "minuto": len(self.blocos) + 1,
            "acertos": acertos,
            "erros": erros,
            "caidos": caidos,
            "duracao_s": round(duracao, 1),
            "erros_por_minuto": round(erros / (duracao / 60), 2),
            "precisao_pct": round(100 * acertos / tentativas, 1) if tentativas else 0.0,
            "itens_errados": self.itens_errados[len(self._itens_bloco):],
        })
        self._inicio_bloco = self.tempo
        self._base = (self.acertos, self.erros, self.caidos)
        self._itens_bloco = list(self.itens_errados)
