"""Regras do jogo: uma run roguelike de ondas em vários cenários (ver config e fases)."""

import random

import pygame

from cartas import aplicar_carta, sortear_oferta, CUSTOS
from config import (LARGURA, Y_CHAO, TAMANHO_RESIDUO, DURACAO_ONDA, ONDAS_POR_FASE,
                    VIDAS_INICIAIS, VIDAS_MAX, VIDA_BONUS_FASE, PONTOS_ACERTO, BONUS_COMBO,
                    COMBO_MAX, PENALIDADE_CHAO, RAMPA_DENTRO_ONDA, REDUCAO_INTERVALO_DENTRO_ONDA,
                    BALANCO_VENTO, FATOR_INTERVALO_CHUVA, FATOR_LIXEIRA_LENTA, FATOR_QUEDA_RAPIDA,
                    DANO_ERRO_DOBRADO, DURACAO_MENSAGEM, DURACAO_TEXTO_FLUTUANTE, VERDE_OK, VERMELHO_ERRO,
                    AMARELO_DESTAQUE, AZUL_INFO)
from eventos import EVENTOS, sortear_evento, aplicar_evento
from fases import FASES, velocidade_queda, intervalo_surgimento, tipos_da_fase
from lixeira import Lixeira
from residuo import Residuo, CATEGORIAS

TOTAL_ONDAS = ONDAS_POR_FASE * len(FASES)

# Q W E R T escolhem a cor da lixeira
TECLAS_CATEGORIA = {
    pygame.K_q: "papel",
    pygame.K_w: "plastico",
    pygame.K_e: "vidro",
    pygame.K_r: "metal",
    pygame.K_t: "organico",
}


class Partida:
    """Modo campanha. As regras comuns (pegar, errar, chão) são reaproveitadas pelo
    modo infinito em infinito.py, que herda desta classe."""

    infinito = False

    def __init__(self, sons):
        self.sons = sons
        self.vidas = VIDAS_INICIAIS
        self.vidas_max = VIDAS_MAX
        self.bonus_combo = BONUS_COMBO
        self.pontos_acerto = PONTOS_ACERTO
        self.pontos = 0
        self.onda = 0                 # índice da onda atual (0 a TOTAL_ONDAS-1)
        self.resultados = []          # métricas de cada onda jogada
        self.revisar = {}             # resíduos errados -> categoria correta
        self.terminou = False
        self.venceu = False
        self.onda_concluida = False

        # Efeitos acumulados das cartas (duram a run inteira)
        self.cartas = []
        self.mod_largura = 1.0
        self.mod_velocidade = 1.0
        self.escudos = 0
        self.combo_duplo = False
        self.chao_sem_penalidade = False

        # Valem só para a próxima onda
        self.custo = None
        self.evento = None
        self.proximo_evento = None
        self.oferta = []

    # ------------------------------------------------------------ estrutura
    @property
    def indice_fase(self):
        return self.onda // ONDAS_POR_FASE

    @property
    def fase(self):
        return FASES[self.indice_fase]

    @property
    def inicio_de_fase(self):
        return self.onda % ONDAS_POR_FASE == 0

    @property
    def ultima_onda(self):
        return self.onda == TOTAL_ONDAS - 1

    @property
    def tempo_restante(self):
        return max(0.0, DURACAO_ONDA - self.tempo)

    def iniciar_onda(self):
        lenta = self.custo == "lixeira_lenta"
        self.lixeira = Lixeira(self.fase["categorias"], self.mod_largura,
                               FATOR_LIXEIRA_LENTA if lenta else 1.0)
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
        self.textos = []          # textos flutuantes: [texto, cor, x, y, tempo]
        self.onda_concluida = False

        tipos, pesos = tipos_da_fase(self.fase["numero"])
        self.tipos, self.pesos = aplicar_evento(tipos, pesos, self.evento)
        # Reinicia a cada cenário: a 1ª onda de um cenário novo é sempre devagar.
        onda_no_cenario = self.onda % ONDAS_POR_FASE
        self.vel_base = velocidade_queda(onda_no_cenario) * self.mod_velocidade
        self.intervalo_base = intervalo_surgimento(onda_no_cenario)

        # Custo da carta escolhida antes desta onda (vale só nesta onda)
        self.mostrar_nomes = self.custo != "sem_rotulo"
        self.balanco = BALANCO_VENTO if self.custo == "vento" else 0.0
        self.dano_erro = DANO_ERRO_DOBRADO if self.custo == "erro_duplo" else 1
        if self.custo == "chuva":
            self.intervalo_base *= FATOR_INTERVALO_CHUVA
        elif self.custo == "queda_rapida":
            self.vel_base *= FATOR_QUEDA_RAPIDA

        if self.evento:
            e = EVENTOS[self.evento]
            self._mensagem("Evento: " + e["nome"], e["descricao"], AZUL_INFO)

    def escolher_carta(self, indice):
        """Aplica a carta escolhida e prepara a próxima onda."""
        aplicar_carta(self, self.oferta[indice])
        self.oferta = []
        self.onda += 1
        self.evento = self.proximo_evento
        self.proximo_evento = None
        if self.inicio_de_fase:
            self.vidas = min(self.vidas_max, self.vidas + VIDA_BONUS_FASE)

    # ------------------------------------------------------------ entrada
    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in TECLAS_CATEGORIA:
            if self.lixeira.selecionar(TECLAS_CATEGORIA[evento.key]):
                self.sons.tocar("troca")

    # ------------------------------------------------------------ lógica
    def _progresso(self):
        return min(self.tempo / DURACAO_ONDA, 1.0)

    # Os três métodos abaixo são sobrescritos pelo modo infinito.
    def _velocidade_atual(self):
        return self.vel_base * (1 + RAMPA_DENTRO_ONDA * self._progresso())

    def _intervalo_atual(self):
        return self.intervalo_base * (1 - REDUCAO_INTERVALO_DENTRO_ONDA * self._progresso())

    def _pode_surgir(self):
        """Novos resíduos só surgem enquanto o tempo da onda não acabou."""
        return self.tempo < DURACAO_ONDA

    def _criar_residuo(self):
        tipo = random.choices(self.tipos, weights=self.pesos, k=1)[0]
        x = random.randint(20, LARGURA - TAMANHO_RESIDUO - 20)
        self.residuos.append(Residuo(tipo, x, self._velocidade_atual(), self.balanco))

    def _texto(self, texto, cor, x, y):
        self.textos.append([texto, cor, x, y, DURACAO_TEXTO_FLUTUANTE])

    def _mensagem(self, titulo, explicacao, cor):
        self.mensagem = (titulo, explicacao, cor)
        self.tempo_mensagem = DURACAO_MENSAGEM

    def _acertou(self, residuo):
        bonus = self.bonus_combo * (2 if self.combo_duplo else 1) * min(self.combo, COMBO_MAX)
        ganho = self.pontos_acerto + bonus
        self.pontos += ganho
        self.combo += 1
        self.acertos += 1
        self._texto(f"+{ganho}", VERDE_OK, residuo.x, residuo.y)
        self.sons.tocar("acerto")
        if residuo.tipo.pegadinha:
            # Reforço positivo nos itens que costumam confundir.
            self._mensagem("Boa! " + residuo.tipo.nome, residuo.tipo.explicacao, VERDE_OK)

    def _errou(self, residuo):
        self.combo = 0
        self.erros += 1
        tipo = residuo.tipo
        certo = CATEGORIAS[tipo.categoria]["nome"]
        self.itens_errados.append(tipo.nome)
        self.revisar[tipo.nome] = certo
        self._mensagem(f"Ops! {tipo.nome} vai no {certo.upper()}", tipo.explicacao, VERMELHO_ERRO)
        if self.escudos > 0:
            self.escudos -= 1          # carta "Segunda chance": o erro conta, a vida não
            self._texto("Escudo!", AZUL_INFO, residuo.x, residuo.y)
        else:
            self.vidas -= self.dano_erro
            rotulo = "-1 vida" if self.dano_erro == 1 else f"-{self.dano_erro} vidas"
            self._texto(rotulo, VERMELHO_ERRO, residuo.x, residuo.y)
        self.sons.tocar("erro")

    def _caiu_no_chao(self, residuo):
        self.caidos += 1
        self.combo = 0
        self.sujeira.append((residuo.x, residuo.tipo.cor))
        if not self.chao_sem_penalidade:
            self.pontos = max(0, self.pontos - PENALIDADE_CHAO)
            self._texto(f"-{PENALIDADE_CHAO}", AMARELO_DESTAQUE, residuo.x, Y_CHAO - 40)
        self.sons.tocar("chao")

    def atualizar(self, dt, teclas):
        self._atualizar_jogo(dt, teclas)
        self._verificar_fim()

    def _atualizar_jogo(self, dt, teclas):
        """Regras comuns aos dois modos: mover, fazer cair, pegar, errar, chão."""
        direcao = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            direcao -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            direcao += 1
        self.lixeira.mover(direcao, dt)
        self.lixeira.atualizar(dt)

        self.tempo += dt

        self.proximo_surgimento -= dt
        if self.proximo_surgimento <= 0 and self._pode_surgir():
            self._criar_residuo()
            self.proximo_surgimento = self._intervalo_atual() * random.uniform(0.8, 1.2)

        boca = self.lixeira.boca
        for residuo in list(self.residuos):
            residuo.atualizar(dt)
            if residuo.rect.colliderect(boca):
                self.residuos.remove(residuo)
                if self.lixeira.receber(residuo):
                    self._acertou(residuo)
                else:
                    self._errou(residuo)
            elif residuo.rect.bottom >= Y_CHAO:
                self.residuos.remove(residuo)
                self._caiu_no_chao(residuo)

        self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)
        for texto in self.textos:
            texto[3] -= 40 * dt
            texto[4] -= dt
        self.textos = [t for t in self.textos if t[4] > 0]

    def _verificar_fim(self):
        """Campanha: fim da onda (cartas) ou fim da run."""
        if self.vidas <= 0:
            self._finalizar_onda()
            self.terminou = True
            self.venceu = False
        elif self.tempo >= DURACAO_ONDA and not self.residuos:
            self._finalizar_onda()
            self.sons.tocar("fase")
            if self.ultima_onda:
                self.terminou = True
                self.venceu = True
            else:
                self.onda_concluida = True
                self.oferta = sortear_oferta(self)
                proxima = self.onda + 1
                self.proximo_evento = sortear_evento(proxima, FASES[proxima // ONDAS_POR_FASE]["numero"])

    def _finalizar_onda(self):
        minutos = max(self.tempo, 1.0) / 60
        tentativas = self.acertos + self.erros
        self.resultados.append({
            "onda": self.onda + 1,
            "cenario": self.fase["nome"],
            "evento": EVENTOS[self.evento]["nome"] if self.evento else "",
            "custo": CUSTOS[self.custo] if self.custo else "",
            "acertos": self.acertos,
            "erros": self.erros,
            "caidos": self.caidos,
            "duracao_s": round(self.tempo, 1),
            "erros_por_minuto": round(self.erros / minutos, 2),
            "precisao_pct": round(100 * self.acertos / tentativas, 1) if tentativas else 0.0,
            "itens_errados": list(self.itens_errados),
        })
        self.custo = None   # o custo valia só para esta onda
