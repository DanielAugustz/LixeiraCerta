"""Lixeira Certa - ponto de entrada e máquina de estados das telas."""

import sys

import pygame

from audio import Sons
from config import LARGURA, ALTURA, FPS, TITULO, MUSICA_MENU, DURACAO_CONTAGEM, INTERVALO_TIC
from fases import FASES
from infinito import PartidaInfinita
from loja import UPGRADES, comprar
from metricas import salvar_partida, salvar_infinito
from musica import Musica
from partida import Partida
from progresso import Progresso
import telas

(MENU, INSTRUCOES, INTRO_FASE, JOGANDO, PAUSA, CARTAS, RESULTADO,
 CONFIG_INFINITO, LOJA, RESULTADO_INFINITO) = range(10)

TECLAS_CARTA = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2}
ESQUERDA = (pygame.K_LEFT, pygame.K_a)
DIREITA = (pygame.K_RIGHT, pygame.K_d)
CIMA = (pygame.K_UP, pygame.K_w)
BAIXO = (pygame.K_DOWN, pygame.K_s)


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    # SCALED + RESIZABLE: dá para redimensionar/maximizar a janela (o jogo escala junto,
    # sem distorcer) — útil em telas menores. F11 alterna tela cheia.
    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption(TITULO)
    relogio = pygame.time.Clock()
    fontes = telas.criar_fontes()
    sons = Sons()
    musica = Musica()
    progresso = Progresso()

    estado = MENU
    opcao = 0
    selecao_carta = 0
    partida = None
    caminho_csv = None
    # Modo infinito
    selecao_config = 0
    escolhas = {"mapa": 3, "dificuldade": 1}
    selecao_loja = 0
    aviso_loja = None
    info_infinito = None
    # Tela de fim
    selecao_fim = 0
    detalhes_fim = False
    tempo_fim = 0.0       # segundos desde que a tela de fim abriu (animação da contagem)
    proximo_tic = 0.0

    while True:
        dt = min(relogio.tick(FPS) / 1000, 0.05)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type != pygame.KEYDOWN:
                continue
            tecla = evento.key
            confirmar = tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

            if tecla == pygame.K_m:        # liga/desliga a música em qualquer tela
                musica.alternar()
                continue
            if tecla == pygame.K_F11:      # tela cheia em qualquer tela
                pygame.display.toggle_fullscreen()
                continue

            if estado == MENU:
                total = len(telas.OPCOES_MENU)
                if tecla in CIMA:
                    opcao = (opcao - 1) % total
                elif tecla in BAIXO:
                    opcao = (opcao + 1) % total
                elif confirmar:
                    if opcao == 0:
                        partida = Partida(sons)
                        estado = INTRO_FASE
                    elif opcao == 1:
                        selecao_config = len(telas.ITENS_CONFIG) - 1   # já no "Começar"
                        estado = CONFIG_INFINITO
                    elif opcao == 2:
                        estado = INSTRUCOES
                    else:
                        pygame.quit()
                        return
                elif tecla == pygame.K_ESCAPE:
                    pygame.quit()
                    return

            elif estado == INSTRUCOES:
                if confirmar or tecla == pygame.K_ESCAPE:
                    estado = MENU

            elif estado == CONFIG_INFINITO:
                limites = {0: ("mapa", len(FASES)), 1: ("dificuldade", len(telas.NOMES_DIFICULDADE))}
                item = telas.ITENS_CONFIG[selecao_config]
                if tecla in CIMA:
                    selecao_config = (selecao_config - 1) % len(telas.ITENS_CONFIG)
                elif tecla in BAIXO:
                    selecao_config = (selecao_config + 1) % len(telas.ITENS_CONFIG)
                elif (tecla in ESQUERDA or tecla in DIREITA) and selecao_config in limites:
                    chave, total = limites[selecao_config]
                    passo = -1 if tecla in ESQUERDA else 1
                    escolhas[chave] = (escolhas[chave] + passo) % total
                elif confirmar and item == "Loja de upgrades":
                    aviso_loja = None
                    estado = LOJA
                elif confirmar and item == "Começar":
                    partida = PartidaInfinita(sons, progresso, escolhas["mapa"],
                                              telas.NOMES_DIFICULDADE[escolhas["dificuldade"]])
                    estado = JOGANDO
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU

            elif estado == LOJA:
                # A loja é da dificuldade escolhida; ← → troca a dificuldade.
                dificuldade = telas.NOMES_DIFICULDADE[escolhas["dificuldade"]]
                if tecla in CIMA:
                    selecao_loja = (selecao_loja - 1) % len(UPGRADES)
                elif tecla in BAIXO:
                    selecao_loja = (selecao_loja + 1) % len(UPGRADES)
                elif tecla in ESQUERDA or tecla in DIREITA:
                    passo = -1 if tecla in ESQUERDA else 1
                    escolhas["dificuldade"] = (escolhas["dificuldade"] + passo) % len(telas.NOMES_DIFICULDADE)
                    aviso_loja = None
                elif confirmar:
                    up = UPGRADES[selecao_loja]
                    if comprar(progresso, dificuldade, up):
                        sons.tocar("fase")
                        aviso_loja = (f"Comprou {up.nome} nível {progresso.nivel(dificuldade, up.id)} "
                                      f"no {dificuldade}!", telas.VERDE_OK)
                    elif progresso.nivel(dificuldade, up.id) >= up.nivel_max:
                        aviso_loja = (f"{up.nome} já está no nível máximo.", telas.AMARELO_DESTAQUE)
                    else:
                        sons.tocar("erro")
                        aviso_loja = (f"Pontos insuficientes. Jogue no {dificuldade} para juntar mais!",
                                      telas.VERMELHO_ERRO)
                elif tecla == pygame.K_ESCAPE:
                    estado = CONFIG_INFINITO

            elif estado == INTRO_FASE:
                if confirmar:
                    partida.iniciar_onda()
                    estado = JOGANDO
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU

            elif estado == JOGANDO:
                if tecla == pygame.K_p:
                    estado = PAUSA
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU
                else:
                    partida.tratar_evento(evento)

            elif estado == PAUSA:
                if tecla == pygame.K_p or confirmar:
                    estado = JOGANDO
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU

            elif estado == CARTAS:
                total = len(partida.oferta)
                if tecla in ESQUERDA:
                    selecao_carta = (selecao_carta - 1) % total
                elif tecla in DIREITA:
                    selecao_carta = (selecao_carta + 1) % total
                elif tecla in TECLAS_CARTA and TECLAS_CARTA[tecla] < total:
                    selecao_carta = TECLAS_CARTA[tecla]
                elif confirmar:
                    partida.escolher_carta(selecao_carta)
                    if partida.infinito:
                        estado = JOGANDO          # continua de onde parou
                    elif partida.inicio_de_fase:
                        estado = INTRO_FASE
                    else:
                        partida.iniciar_onda()
                        estado = JOGANDO
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU

            elif estado in (RESULTADO, RESULTADO_INFINITO):
                if detalhes_fim:
                    # tela detalhada (tabela e "para revisar"): volta para a tela simples
                    if confirmar or tecla in (pygame.K_TAB, pygame.K_ESCAPE):
                        detalhes_fim = False
                elif tecla == pygame.K_TAB:
                    detalhes_fim = True
                elif tecla in CIMA or tecla in BAIXO:
                    selecao_fim = (selecao_fim + 1) % len(telas.BOTOES_FIM)
                elif tecla == pygame.K_ESCAPE:
                    estado = MENU
                elif confirmar and tempo_fim < DURACAO_CONTAGEM:
                    tempo_fim = DURACAO_CONTAGEM      # ENTER durante a contagem: pula para o final
                elif confirmar:
                    if telas.BOTOES_FIM[selecao_fim] == "Menu":
                        estado = MENU
                    elif partida.infinito:   # jogar de novo com o mesmo mapa e dificuldade
                        partida = PartidaInfinita(sons, progresso, escolhas["mapa"],
                                                  telas.NOMES_DIFICULDADE[escolhas["dificuldade"]])
                        estado = JOGANDO
                    else:
                        partida = Partida(sons)
                        estado = INTRO_FASE

        if estado == JOGANDO:
            partida.atualizar(dt, pygame.key.get_pressed())
            if partida.terminou:
                selecao_fim = 0
                detalhes_fim = False
                tempo_fim = 0.0
                proximo_tic = 0.0
                if partida.infinito:
                    novo = progresso.registrar_partida(partida.dificuldade, partida.pontos)
                    info_infinito = {"novo_recorde": novo,
                                     "recorde": progresso.recorde(partida.dificuldade),
                                     "carteira": progresso.carteira(partida.dificuldade),
                                     "csv": salvar_infinito(partida)}
                    estado = RESULTADO_INFINITO
                else:
                    caminho_csv = salvar_partida(partida)
                    estado = RESULTADO
            elif partida.onda_concluida:
                selecao_carta = 0
                estado = CARTAS

        # Contagem dos pontos na tela de fim: "tic" enquanto conta, som de conclusão no final.
        if estado in (RESULTADO, RESULTADO_INFINITO) and not detalhes_fim:
            antes = tempo_fim
            tempo_fim += dt
            if tempo_fim < DURACAO_CONTAGEM and tempo_fim >= proximo_tic and partida.pontos > 0:
                sons.tocar("troca")
                proximo_tic = tempo_fim + INTERVALO_TIC
            if antes < DURACAO_CONTAGEM <= tempo_fim:
                sons.tocar("fase")

        # Música do cenário atual durante a partida; música do menu nas outras telas.
        if estado in (INTRO_FASE, JOGANDO, PAUSA, CARTAS, RESULTADO_INFINITO):
            musica.tocar(partida.fase["cenario"])
        elif estado == CONFIG_INFINITO:
            musica.tocar(FASES[escolhas["mapa"]]["cenario"])
        else:
            musica.tocar(MUSICA_MENU)

        if estado == MENU:
            telas.desenhar_menu(tela, fontes, opcao)
        elif estado == INSTRUCOES:
            telas.desenhar_instrucoes(tela, fontes)
        elif estado == CONFIG_INFINITO:
            telas.desenhar_config_infinito(tela, fontes, selecao_config, escolhas, progresso)
        elif estado == LOJA:
            telas.desenhar_loja(tela, fontes, selecao_loja, progresso,
                                telas.NOMES_DIFICULDADE[escolhas["dificuldade"]], aviso_loja)
        elif estado == INTRO_FASE:
            telas.desenhar_intro_fase(tela, fontes, partida)
        elif estado == JOGANDO:
            telas.desenhar_jogo(tela, fontes, partida)
        elif estado == PAUSA:
            telas.desenhar_pausa(tela, fontes, partida)
        elif estado == CARTAS:
            telas.desenhar_cartas(tela, fontes, partida, selecao_carta)
        elif estado == RESULTADO:
            if detalhes_fim:
                telas.desenhar_resultado(tela, fontes, partida, caminho_csv)
            else:
                telas.desenhar_fim(tela, fontes, partida, selecao_fim, None, tempo_fim)
        elif estado == RESULTADO_INFINITO:
            if detalhes_fim:
                telas.desenhar_resultado_infinito(tela, fontes, partida, info_infinito)
            else:
                telas.desenhar_fim(tela, fontes, partida, selecao_fim, info_infinito, tempo_fim)

        pygame.display.flip()


if __name__ == "__main__":
    main()
    sys.exit()
