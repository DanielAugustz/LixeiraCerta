"""Desenho das telas (menu, instruções, HUD, cartas, resultado...)."""

import pygame

from cartas import resumo_cartas, CUSTOS
from cenario import desenhar_cenario, escurecer_tela
from config import (DIFICULDADES, DURACAO_CUSTO_INFINITO, ESCURECER_FUNDO_JOGO, SEGUNDOS_POR_ETAPA,
                    DURACAO_CONTAGEM, DURACAO_PULO)
from loja import UPGRADES
from config import (LARGURA, ALTURA, ALTURA_HUD, RAIO_BOLINHA, ESPACO_BOLINHA, DURACAO_ONDA,
                    ONDAS_POR_FASE, BRANCO, CINZA_ESCURO, VERDE_OK, VERMELHO_ERRO,
                    AMARELO_DESTAQUE, AZUL_INFO)
from eventos import EVENTOS
from fases import FASES
from partida import TOTAL_ONDAS
from residuo import CATEGORIAS, ORDEM_CATEGORIAS


def criar_fontes():
    def f(tamanho, negrito=False):
        return pygame.font.SysFont("segoeui,arial,dejavusans", tamanho, bold=negrito)
    return {"titulo": f(60, True), "grande": f(34, True), "media": f(24),
            "media_n": f(24, True), "pequena": f(18), "pequena_n": f(18, True), "mini": f(15, True)}


def texto(tela, fonte, conteudo, cor=BRANCO, **posicao):
    superficie = fonte.render(conteudo, True, cor)
    tela.blit(superficie, superficie.get_rect(**posicao))


def painel(tela, rect, cor=CINZA_ESCURO, borda=None, alpha=235):
    fundo = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(fundo, (*cor, alpha), fundo.get_rect(), border_radius=14)
    tela.blit(fundo, rect.topleft)
    if borda:
        pygame.draw.rect(tela, borda, rect, 3, border_radius=14)


def bolinhas_categorias(tela, categorias, selecionada):
    """Durante o jogo: bolinhas com a cor de cada lixeira no canto inferior esquerdo.
    A cor selecionada ganha um círculo amarelo em volta."""
    y = ALTURA - 24
    x = 28
    for chave in ORDEM_CATEGORIAS:
        if chave not in categorias:
            continue
        pygame.draw.circle(tela, (25, 25, 25), (x, y), RAIO_BOLINHA + 2)
        pygame.draw.circle(tela, CATEGORIAS[chave]["cor"], (x, y), RAIO_BOLINHA)
        if chave == selecionada:
            pygame.draw.circle(tela, AMARELO_DESTAQUE, (x, y), RAIO_BOLINHA + 6, 3)
        x += ESPACO_BOLINHA


ALTURA_UI = 640   # as telas de menu foram desenhadas para 640 px de altura


def area_central(tela):
    """Área de 640 px de altura no meio da janela: o conteúdo das telas de menu é desenhado
    aqui, para ficar centralizado mesmo com a janela mais alta (o fundo usa a janela toda)."""
    dy = max(0, (tela.get_height() - ALTURA_UI) // 2)
    return tela.subsurface((0, dy, tela.get_width(), ALTURA_UI))


def legenda_categorias(tela, fontes, categorias, y):
    """Caixinhas coloridas com o nome de cada lixeira (telas de instrução e de cenário)."""
    largura = 140
    espaco = 10
    total = len(categorias) * largura + (len(categorias) - 1) * espaco
    x = (LARGURA - total) // 2
    for chave in ORDEM_CATEGORIAS:
        if chave not in categorias:
            continue
        dados = CATEGORIAS[chave]
        caixa = pygame.Rect(x, y, largura, 52)
        pygame.draw.rect(tela, dados["cor"], caixa, border_radius=10)
        texto(tela, fontes["pequena_n"], dados["nome"], dados["texto"], center=caixa.center)
        x += largura + espaco


# ------------------------------------------------------------------ menu
def desenhar_menu(tela, fontes, opcao):
    desenhar_cenario(tela, "praia")
    escurecer_tela(tela, 120)
    tela = area_central(tela)   # conteúdo centralizado na altura
    texto(tela, fontes["titulo"], "Lixeira Certa", AMARELO_DESTAQUE, center=(LARGURA // 2, 140))
    texto(tela, fontes["media"], "Separe o lixo certo antes que ele caia no chão!", BRANCO,
          center=(LARGURA // 2, 205))
    for i, (nome, descricao) in enumerate(OPCOES_MENU):
        caixa = pygame.Rect(0, 0, 320, 52)
        caixa.center = (LARGURA // 2, 280 + i * 66)
        selecionada = i == opcao
        painel(tela, caixa, (60, 120, 70) if selecionada else CINZA_ESCURO,
               AMARELO_DESTAQUE if selecionada else None)
        texto(tela, fontes["media_n"], nome, BRANCO, center=caixa.center)
    texto(tela, fontes["pequena"], OPCOES_MENU[opcao][1], AMARELO_DESTAQUE,
          center=(LARGURA // 2, ALTURA_UI - 70))
    texto(tela, fontes["pequena"], "Setas para escolher  •  ENTER para confirmar", BRANCO,
          center=(LARGURA // 2, ALTURA_UI - 36))


OPCOES_MENU = [
    ("Modo campanha", "4 cenários e 8 ondas: uma lixeira nova a cada cenário."),
    ("Modo infinito", "Sem fim, num mapa só. Escolha a dificuldade e compre upgrades na loja."),
    ("Como jogar", "Controles, regras e cores das lixeiras."),
    ("Sair", "Fechar o jogo."),
]


def desenhar_instrucoes(tela, fontes):
    desenhar_cenario(tela, "rua")
    escurecer_tela(tela, 170)
    tela = area_central(tela)   # conteúdo centralizado na altura
    texto(tela, fontes["grande"], "Como jogar", AMARELO_DESTAQUE, center=(LARGURA // 2, 45))
    linhas = [
        "Objetivo: pegar cada resíduo com a lixeira da COR CERTA.",
        "←  →  (ou A  D): mover    •    Q Papel  W Plástico  E Vidro  R Metal  T Orgânico",
        "Lixeira certa: ganha pontos. Acertos seguidos dão bônus de combo.",
        "Lixeira errada: perde 1 vida e o jogo explica onde o item deveria ir.",
        "Deixou cair no chão: perde 5 pontos e a cena fica suja.",
        f"{TOTAL_ONDAS} ondas de {DURACAO_ONDA} s em {len(FASES)} cenários: a cada cenário entra uma lixeira nova.",
        "Entre as ondas, escolha 1 de 3 cartas. Toda carta é uma troca:",
        "a vantagem vale a run toda, o custo vale só na próxima onda.",
        "Perdeu todas as vidas? A run acaba e você recomeça do zero.",
        "P: pausar   •   M: música   •   F11: tela cheia   •   ESC: voltar ao menu",
    ]
    for i, linha in enumerate(linhas):
        texto(tela, fontes["media"], linha, BRANCO, midleft=(50, 100 + i * 37))
    texto(tela, fontes["pequena_n"], "As cores seguem o padrão da coleta seletiva:", BRANCO,
          center=(LARGURA // 2, 488))
    legenda_categorias(tela, fontes, ORDEM_CATEGORIAS, y=508)
    texto(tela, fontes["pequena"], "ENTER ou ESC para voltar", BRANCO, center=(LARGURA // 2, ALTURA_UI - 30))


# ------------------------------------------------------------------ cenário novo
def desenhar_intro_fase(tela, fontes, partida):
    fase = partida.fase
    desenhar_cenario(tela, fase["cenario"])
    escurecer_tela(tela, 150)
    tela = area_central(tela)   # conteúdo centralizado na altura
    caixa = pygame.Rect(20, 60, LARGURA - 40, 440)
    painel(tela, caixa, borda=AMARELO_DESTAQUE)
    primeira = partida.onda + 1
    texto(tela, fontes["mini"], f"CENÁRIO {fase['numero']} DE {len(FASES)}  •  ONDAS {primeira} A "
          f"{primeira + ONDAS_POR_FASE - 1}", AMARELO_DESTAQUE, center=(LARGURA // 2, 95))
    texto(tela, fontes["grande"], fase["nome"], BRANCO, center=(LARGURA // 2, 135))
    for i, linha in enumerate(fase["novidades"]):
        texto(tela, fontes["media"], linha, BRANCO, center=(LARGURA // 2, 195 + i * 36))
    texto(tela, fontes["pequena_n"], f"{ONDAS_POR_FASE} ondas de {DURACAO_ONDA} s. Os resíduos só caem mais rápido "
          "se você escolher a carta com o custo \"Queda rápida\".", AZUL_INFO, center=(LARGURA // 2, 292))
    texto(tela, fontes["pequena"], f"Vidas: {partida.vidas}   •   Pontos: {partida.pontos}", BRANCO,
          center=(LARGURA // 2, 325))
    if partida.cartas:
        texto(tela, fontes["pequena"], "Suas cartas: " + resumo_cartas(partida.cartas), VERDE_OK,
              center=(LARGURA // 2, 355))
    legenda_categorias(tela, fontes, fase["categorias"], y=400)
    texto(tela, fontes["media_n"], "ENTER para começar", AMARELO_DESTAQUE, center=(LARGURA // 2, 560))


# ------------------------------------------------------------------ cartas
def desenhar_cartas(tela, fontes, partida, selecao):
    desenhar_cenario(tela, partida.fase["cenario"], partida.sujeira)
    escurecer_tela(tela, 170)
    tela = area_central(tela)   # conteúdo centralizado na altura
    if partida.infinito:
        texto(tela, fontes["grande"], "Carta desbloqueada!", VERDE_OK, center=(LARGURA // 2, 45))
        texto(tela, fontes["pequena"], f"{partida.pontos} pontos  •  {_relogio(partida.tempo)} de jogo  •  "
              f"{partida.acertos} acertos  •  {partida.erros} erros", BRANCO, center=(LARGURA // 2, 85))
        texto(tela, fontes["pequena_n"], f"No modo infinito o custo dura {DURACAO_CUSTO_INFINITO} segundos  •  "
              f"Próxima carta em {partida.proxima_carta} pontos", AZUL_INFO, center=(LARGURA // 2, 118))
    else:
        r = partida.resultados[-1]
        texto(tela, fontes["grande"], f"Onda {r['onda']} concluída!", VERDE_OK, center=(LARGURA // 2, 45))
        texto(tela, fontes["pequena"], f"{r['acertos']} acertos  •  {r['erros']} erros  •  "
              f"{r['caidos']} no chão  •  {r['erros_por_minuto']} erros/min  •  {partida.pontos} pontos",
              BRANCO, center=(LARGURA // 2, 85))

        proxima = partida.onda + 2
        if partida.proximo_evento:
            evento = EVENTOS[partida.proximo_evento]
            aviso = f"Próxima: onda {proxima}  •  Evento: {evento['nome']}"
            cor_aviso = AZUL_INFO
        else:
            aviso = f"Próxima: onda {proxima}"
            cor_aviso = BRANCO
        if (proxima - 1) % ONDAS_POR_FASE == 0:
            aviso += "  •  Cenário novo (+1 vida)"
        texto(tela, fontes["pequena_n"], aviso, cor_aviso, center=(LARGURA // 2, 118))

    texto(tela, fontes["media_n"], "Escolha uma carta", AMARELO_DESTAQUE, center=(LARGURA // 2, 160))
    largura, altura, espaco = 270, 280, 30
    x0 = (LARGURA - (3 * largura + 2 * espaco)) // 2
    for i, carta in enumerate(partida.oferta):
        caixa = pygame.Rect(x0 + i * (largura + espaco), 190, largura, altura)
        escolhida = i == selecao
        if escolhida:
            caixa.y -= 10
        painel(tela, caixa, borda=AMARELO_DESTAQUE if escolhida else (110, 110, 120))
        texto(tela, fontes["media_n"], carta.nome, BRANCO, center=(caixa.centerx, caixa.top + 56))
        texto(tela, fontes["mini"], "VANTAGEM (a partida toda)" if partida.infinito else "VANTAGEM (a run toda)",
              VERDE_OK, center=(caixa.centerx, caixa.top + 96))
        for j, linha in enumerate(carta.vantagem):
            texto(tela, fontes["pequena"], linha, BRANCO, center=(caixa.centerx, caixa.top + 122 + j * 24))
        texto(tela, fontes["mini"], f"CUSTO: {CUSTOS[carta.custo].upper()}", VERMELHO_ERRO,
              center=(caixa.centerx, caixa.top + 182))
        linhas_custo = carta.texto_custo
        if partida.infinito:   # no infinito o custo não é "na próxima onda", e sim por 30 s
            linhas_custo = (f"Por {DURACAO_CUSTO_INFINITO} s: " + linhas_custo[0].replace("Próxima onda: ", ""),
                            *linhas_custo[1:])
        for j, linha in enumerate(linhas_custo):
            texto(tela, fontes["pequena"], linha, BRANCO, center=(caixa.centerx, caixa.top + 208 + j * 24))
        quantas = partida.cartas.count(carta.id)
        if quantas:
            texto(tela, fontes["mini"], f"Já tem {quantas}", AMARELO_DESTAQUE,
                  midright=(caixa.right - 14, caixa.top + 24))

    if partida.cartas:
        texto(tela, fontes["pequena"], "Suas cartas: " + resumo_cartas(partida.cartas), VERDE_OK,
              center=(LARGURA // 2, 515))
    texto(tela, fontes["pequena"], f"Vidas: {partida.vidas}" +
          (f"   •   Escudos: {partida.escudos}" if partida.escudos else ""), BRANCO,
          center=(LARGURA // 2, 545))
    texto(tela, fontes["media_n"], "←  →  para escolher  •  ENTER para confirmar",
          AMARELO_DESTAQUE, center=(LARGURA // 2, 595))


# ------------------------------------------------------------------ jogo
def _relogio(segundos):
    return f"{int(segundos) // 60:02d}:{int(segundos) % 60:02d}"


def _desenhar_hud(tela, fontes, partida):
    pygame.draw.rect(tela, CINZA_ESCURO, (0, 0, LARGURA, ALTURA_HUD))
    if partida.infinito:
        texto(tela, fontes["pequena_n"], f"Infinito  •  {partida.dificuldade}  •  {partida.fase['nome']}",
              BRANCO, midleft=(16, 20))
        texto(tela, fontes["pequena"], f"{_relogio(partida.tempo)}  •  Nível {partida.etapa + 1}  •  "
              f"Carta em {partida.proxima_carta}",
              BRANCO, midleft=(16, 42))
    else:
        texto(tela, fontes["pequena_n"], f"Onda {partida.onda + 1}/{TOTAL_ONDAS}  •  {partida.fase['nome']}",
              BRANCO, midleft=(16, 20))
        texto(tela, fontes["pequena"], f"Tempo: {int(partida.tempo_restante):02d}s", BRANCO, midleft=(16, 42))
    texto(tela, fontes["media_n"], f"{partida.pontos} pts", AMARELO_DESTAQUE, center=(LARGURA // 2, 18))
    detalhes = []
    if partida.combo >= 2:
        detalhes.append((f"Combo x{partida.combo}", VERDE_OK))
    if partida.custo:
        resto = f" ({int(partida.tempo_custo) + 1}s)" if partida.infinito else ""
        detalhes.append((f"Custo: {CUSTOS[partida.custo]}{resto}", VERMELHO_ERRO))
    if detalhes:
        linha = "   ".join(d[0] for d in detalhes)
        texto(tela, fontes["pequena"], linha, detalhes[-1][1] if len(detalhes) == 1 else AMARELO_DESTAQUE,
              center=(LARGURA // 2, 43))
    texto(tela, fontes["pequena_n"], "Vidas:", BRANCO, midright=(LARGURA - 185, 20))
    passo = min(22, 160 // max(1, partida.vidas))
    for i in range(partida.vidas):
        pygame.draw.circle(tela, VERMELHO_ERRO, (LARGURA - 170 + i * passo, 20), min(8, passo // 2))
    if partida.escudos:
        texto(tela, fontes["pequena"], f"Escudos: {partida.escudos}", AZUL_INFO, midright=(LARGURA - 16, 42))
    if partida.infinito:   # barra = quanto falta para a próxima carta
        inicio = partida.proxima_carta - partida.passo_carta
        fracao = (partida.pontos - inicio) / max(1, partida.passo_carta)
    else:                  # barra = tempo restante da onda
        fracao = partida.tempo_restante / DURACAO_ONDA
    largura_barra = int(LARGURA * max(0.0, min(1.0, fracao)))
    pygame.draw.rect(tela, AMARELO_DESTAQUE, (0, ALTURA_HUD - 4, largura_barra, 4))


def _desenhar_mensagem(tela, fontes, partida):
    if not partida.mensagem or partida.tempo_mensagem <= 0:
        return
    titulo, explicacao, cor = partida.mensagem
    caixa = pygame.Rect(0, 0, 720, 70)
    caixa.midtop = (LARGURA // 2, ALTURA_HUD + 10)
    painel(tela, caixa, borda=cor)
    texto(tela, fontes["media_n"], titulo, cor, center=(caixa.centerx, caixa.top + 22))
    texto(tela, fontes["pequena"], explicacao, BRANCO, center=(caixa.centerx, caixa.top + 50))


def desenhar_jogo(tela, fontes, partida):
    desenhar_cenario(tela, partida.fase["cenario"], partida.sujeira)
    escurecer_tela(tela, ESCURECER_FUNDO_JOGO)   # fundo um pouco mais escuro: itens se destacam
    for residuo in partida.residuos:
        residuo.desenhar(tela, fontes["mini"], partida.mostrar_nomes)
    partida.lixeira.desenhar(tela, fontes["pequena_n"])
    for conteudo, cor, x, y, _ in partida.textos:
        texto(tela, fontes["media_n"], conteudo, cor, center=(x + 22, y))
    bolinhas_categorias(tela, partida.lixeira.categorias, partida.lixeira.categoria)
    _desenhar_hud(tela, fontes, partida)
    _desenhar_mensagem(tela, fontes, partida)


def desenhar_pausa(tela, fontes, partida):
    desenhar_jogo(tela, fontes, partida)
    escurecer_tela(tela, 160)
    texto(tela, fontes["titulo"], "Pausado", AMARELO_DESTAQUE, center=(LARGURA // 2, ALTURA // 2 - 30))
    texto(tela, fontes["media"], "P ou ENTER para continuar  •  ESC para o menu", BRANCO,
          center=(LARGURA // 2, ALTURA // 2 + 40))


# ------------------------------------------------------------------ resultado
def desenhar_resultado(tela, fontes, partida, caminho_csv):
    desenhar_cenario(tela, "praia" if partida.venceu else "rua")
    escurecer_tela(tela, 185)
    tela = area_central(tela)   # conteúdo centralizado na altura
    if partida.venceu:
        texto(tela, fontes["grande"], "Você limpou a cidade!", VERDE_OK, center=(LARGURA // 2, 35))
    else:
        texto(tela, fontes["grande"], f"Fim da run na onda {partida.onda + 1}", VERMELHO_ERRO,
              center=(LARGURA // 2, 35))
    texto(tela, fontes["media_n"], f"{partida.pontos} pontos", AMARELO_DESTAQUE, center=(LARGURA // 2, 78))
    if partida.cartas:
        texto(tela, fontes["mini"], "Cartas: " + resumo_cartas(partida.cartas), BRANCO,
              center=(LARGURA // 2, 108))

    colunas = [("Onda", 70), ("Cenário", 200), ("Acertos", 370), ("Erros", 470), ("No chão", 570),
               ("Erros/min", 690), ("Precisão", 830)]
    y = 140
    for nome, x in colunas:
        texto(tela, fontes["pequena_n"], nome, AMARELO_DESTAQUE, center=(x, y))
    for r in partida.resultados:
        y += 22
        valores = [r["onda"], r["cenario"], r["acertos"], r["erros"], r["caidos"],
                   r["erros_por_minuto"], f"{r['precisao_pct']}%"]
        for (_, x), valor in zip(colunas, valores):
            texto(tela, fontes["pequena"], str(valor), BRANCO, center=(x, y))

    y = 140 + 22 * TOTAL_ONDAS + 30
    if len(partida.resultados) >= 2:
        primeira = partida.resultados[0]["erros_por_minuto"]
        ultima = partida.resultados[-1]["erros_por_minuto"]
        if ultima < primeira:
            frase, cor = f"Seus erros por minuto caíram de {primeira} para {ultima}!", VERDE_OK
        elif ultima == primeira:
            frase, cor = f"Erros por minuto: {primeira} na 1ª onda e {ultima} na última.", BRANCO
        else:
            frase, cor = f"Erros por minuto subiram de {primeira} para {ultima}. Treine de novo!", AMARELO_DESTAQUE
        texto(tela, fontes["pequena_n"], frase, cor, center=(LARGURA // 2, y))

    y += 34
    if partida.revisar:
        itens = list(partida.revisar.items())[:6]
        texto(tela, fontes["pequena_n"], "Para revisar:", AMARELO_DESTAQUE, center=(LARGURA // 2, y))
        for i, (nome, categoria) in enumerate(itens):
            texto(tela, fontes["pequena"], f"{nome}  →  {categoria}", BRANCO,
                  center=(LARGURA // 2 - 230 + (i % 2) * 460, y + 26 + (i // 2) * 24))
    else:
        texto(tela, fontes["pequena_n"], "Nenhum erro de separação. Excelente!", VERDE_OK,
              center=(LARGURA // 2, y))

    if caminho_csv:
        texto(tela, fontes["mini"], "Métricas salvas em metricas/partidas.csv", BRANCO,
              center=(LARGURA // 2, ALTURA_UI - 52))
    texto(tela, fontes["media_n"], "TAB ou ENTER para voltar", AMARELO_DESTAQUE,
          center=(LARGURA // 2, ALTURA_UI - 24))


# ------------------------------------------------------------------ modo infinito
NOMES_DIFICULDADE = list(DIFICULDADES)
ITENS_CONFIG = ["Mapa", "Dificuldade", "Loja de upgrades", "Começar"]
OPCOES_COM_SETAS = 2   # as 2 primeiras linhas mudam com ← →


def desenhar_config_infinito(tela, fontes, selecao, escolhas, progresso):
    """escolhas = {"mapa": i, "dificuldade": i}"""
    mapa = FASES[escolhas["mapa"]]
    desenhar_cenario(tela, mapa["cenario"])
    escurecer_tela(tela, 160)
    tela = area_central(tela)   # conteúdo centralizado na altura
    texto(tela, fontes["grande"], "Modo infinito", AMARELO_DESTAQUE, center=(LARGURA // 2, 50))
    texto(tela, fontes["pequena"], "Sem fim: jogue até as vidas acabarem. A dificuldade define lixeiras, "
          "vidas e velocidade.", BRANCO, center=(LARGURA // 2, 90))

    dificuldade = NOMES_DIFICULDADE[escolhas["dificuldade"]]
    dados = DIFICULDADES[dificuldade]
    valores = [mapa["nome"], dificuldade, f"Carteira do {dificuldade}: {progresso.carteira(dificuldade)} pts", ""]
    dicas = ["", f"{dados['lixeiras']} lixeiras  •  {dados['vidas']} vidas  •  itens x{dados['velocidade']:g}  •  "
             f"+{int(dados['acel_etapa'] * 100)}% a cada {SEGUNDOS_POR_ETAPA}s", f"upgrades só do {dificuldade}", ""]
    for i, nome in enumerate(ITENS_CONFIG):
        caixa = pygame.Rect(0, 0, 680, 58)
        caixa.center = (LARGURA // 2, 160 + i * 74)
        selecionada = i == selecao
        cor = (60, 120, 70) if (selecionada and i == len(ITENS_CONFIG) - 1) else CINZA_ESCURO
        painel(tela, caixa, cor, AMARELO_DESTAQUE if selecionada else None)
        if i < OPCOES_COM_SETAS:
            texto(tela, fontes["pequena_n"], nome, AMARELO_DESTAQUE, midleft=(caixa.left + 20, caixa.top + 18))
            texto(tela, fontes["media_n"], f"◄  {valores[i]}  ►", BRANCO, center=(caixa.right - 140, caixa.centery))
            if dicas[i]:
                texto(tela, fontes["mini"], dicas[i], BRANCO, midleft=(caixa.left + 20, caixa.top + 42))
        else:
            texto(tela, fontes["media_n"], nome, BRANCO, center=(caixa.centerx, caixa.centery - (8 if dicas[i] else 0)))
            if dicas[i] or valores[i]:
                texto(tela, fontes["mini"], f"{valores[i]}  •  {dicas[i]}", AMARELO_DESTAQUE,
                      center=(caixa.centerx, caixa.top + 44))

    texto(tela, fontes["pequena_n"], f"Lixeiras no {dificuldade}:", BRANCO, center=(LARGURA // 2, 452))
    legenda_categorias(tela, fontes, ORDEM_CATEGORIAS[:dados["lixeiras"]], y=468)
    recorde = progresso.recorde(dificuldade)
    texto(tela, fontes["pequena_n"], f"Recorde no {dificuldade}: {recorde} pts", VERDE_OK,
          center=(LARGURA // 2, 555))
    texto(tela, fontes["pequena"], "↑ ↓ escolher  •  ← → mudar  •  ENTER confirmar  •  ESC voltar", BRANCO,
          center=(LARGURA // 2, 600))


def desenhar_loja(tela, fontes, selecao, progresso, dificuldade, aviso):
    """Loja da dificuldade escolhida: cada dificuldade tem sua carteira e seus upgrades."""
    desenhar_cenario(tela, "feira")
    escurecer_tela(tela, 170)
    tela = area_central(tela)   # conteúdo centralizado na altura
    carteira = progresso.carteira(dificuldade)
    texto(tela, fontes["grande"], "Loja de upgrades", AMARELO_DESTAQUE, center=(LARGURA // 2, 40))
    texto(tela, fontes["media_n"], f"◄  {dificuldade}  ►     Carteira: {carteira} pts", VERDE_OK,
          center=(LARGURA // 2, 84))
    texto(tela, fontes["mini"], f"Upgrades comprados aqui valem só no modo infinito, na dificuldade {dificuldade}. "
          f"Pontos feitos no {dificuldade} vão para esta carteira.", BRANCO, center=(LARGURA // 2, 116))
    for i, up in enumerate(UPGRADES):
        nivel = progresso.nivel(dificuldade, up.id)
        caixa = pygame.Rect(0, 0, 760, 60)
        caixa.center = (LARGURA // 2, 168 + i * 68)
        selecionada = i == selecao
        painel(tela, caixa, borda=AMARELO_DESTAQUE if selecionada else None)
        texto(tela, fontes["media_n"], up.nome, BRANCO, midleft=(caixa.left + 20, caixa.top + 20))
        texto(tela, fontes["pequena"], up.descricao, BRANCO, midleft=(caixa.left + 20, caixa.top + 44))
        # nível em bolinhas
        for n in range(up.nivel_max):
            cor = AMARELO_DESTAQUE if n < nivel else (90, 90, 100)
            pygame.draw.circle(tela, cor, (caixa.right - 250 + n * 20, caixa.top + 20), 7)
        if nivel >= up.nivel_max:
            preco, cor_preco = "MÁXIMO", VERDE_OK
        else:
            valor = up.preco(nivel)
            preco = f"{valor} pts"
            cor_preco = AMARELO_DESTAQUE if carteira >= valor else VERMELHO_ERRO
        texto(tela, fontes["media_n"], preco, cor_preco, midright=(caixa.right - 20, caixa.top + 42))
    if aviso:
        texto(tela, fontes["pequena_n"], aviso[0], aviso[1], center=(LARGURA // 2, 570))
    texto(tela, fontes["pequena"], "↑ ↓ escolher  •  ← → trocar dificuldade  •  ENTER comprar  •  ESC voltar",
          BRANCO, center=(LARGURA // 2, 610))


def desenhar_resultado_infinito(tela, fontes, partida, info):
    """info = {"novo_recorde": bool, "recorde": int, "carteira": int, "csv": caminho}"""
    desenhar_cenario(tela, partida.fase["cenario"], partida.sujeira)
    escurecer_tela(tela, 185)
    tela = area_central(tela)   # conteúdo centralizado na altura
    texto(tela, fontes["grande"], "Fim da partida infinita", VERMELHO_ERRO, center=(LARGURA // 2, 35))
    texto(tela, fontes["media_n"], f"{partida.pontos} pontos  •  {_relogio(partida.tempo)} de jogo",
          AMARELO_DESTAQUE, center=(LARGURA // 2, 75))
    if info["novo_recorde"]:
        texto(tela, fontes["pequena_n"], f"NOVO RECORDE no {partida.dificuldade}!", VERDE_OK, center=(LARGURA // 2, 105))
    else:
        texto(tela, fontes["pequena"], f"Recorde no {partida.dificuldade}: {info['recorde']} pts", BRANCO,
              center=(LARGURA // 2, 105))
    texto(tela, fontes["pequena"], f"+{partida.pontos} na carteira do {partida.dificuldade}  •  "
          f"Carteira: {info['carteira']} pts",
          VERDE_OK, center=(LARGURA // 2, 130))

    colunas = [("Minuto", 160), ("Acertos", 300), ("Erros", 420), ("No chão", 540), ("Erros/min", 670),
               ("Precisão", 800)]
    y = 165
    for nome, x in colunas:
        texto(tela, fontes["pequena_n"], nome, AMARELO_DESTAQUE, center=(x, y))
    blocos = partida.blocos[-10:]   # os últimos 10 minutos
    for b in blocos:
        y += 22
        valores = [b["minuto"], b["acertos"], b["erros"], b["caidos"], b["erros_por_minuto"], f"{b['precisao_pct']}%"]
        for (_, x), valor in zip(colunas, valores):
            texto(tela, fontes["pequena"], str(valor), BRANCO, center=(x, y))

    y = 165 + 22 * 10 + 30
    if len(partida.blocos) >= 2:
        primeiro = partida.blocos[0]["erros_por_minuto"]
        ultimo = partida.blocos[-1]["erros_por_minuto"]
        if ultimo < primeiro:
            frase, cor = f"Seus erros por minuto caíram de {primeiro} para {ultimo}!", VERDE_OK
        else:
            frase, cor = f"Erros por minuto: {primeiro} no 1º minuto e {ultimo} no último.", BRANCO
        texto(tela, fontes["pequena_n"], frase, cor, center=(LARGURA // 2, y))
    y += 32
    if partida.revisar:
        itens = list(partida.revisar.items())[:6]
        texto(tela, fontes["pequena_n"], "Para revisar:", AMARELO_DESTAQUE, center=(LARGURA // 2, y))
        for i, (nome, categoria) in enumerate(itens):
            texto(tela, fontes["pequena"], f"{nome}  →  {categoria}", BRANCO,
                  center=(LARGURA // 2 - 230 + (i % 2) * 460, y + 24 + (i // 2) * 22))
    texto(tela, fontes["media_n"], "TAB ou ENTER para voltar", AMARELO_DESTAQUE, center=(LARGURA // 2, ALTURA_UI - 24))


# ------------------------------------------------------------------ tela de fim (simples)
BOTOES_FIM = ["Jogar novamente", "Menu"]


def pontos_na_contagem(total, tempo):
    """Valor mostrado durante a contagem: começa rápido e desacelera no fim (ease-out)."""
    t = min(1.0, tempo / DURACAO_CONTAGEM)
    return round(total * (1 - (1 - t) ** 3))


def desenhar_fim(tela, fontes, partida, selecao, info=None, tempo=DURACAO_CONTAGEM + DURACAO_PULO):
    """Tela de fim: PONTOS, o número (em contagem) e dois botões. TAB mostra os detalhes.
    'tempo' = segundos desde que a tela abriu (controla a animação da contagem)."""
    desenhar_cenario(tela, partida.fase["cenario"], partida.sujeira)
    escurecer_tela(tela, 170)
    caixa = pygame.Rect(0, 0, 640, 420)
    caixa.center = (LARGURA // 2, ALTURA // 2 - 10)
    painel(tela, caixa, borda=BRANCO)

    texto(tela, fontes["grande"], "PONTOS", BRANCO, center=(LARGURA // 2, caixa.top + 85))

    # Número contando de 0 até o total; ao terminar, dá um "pulo" (cresce e volta).
    valor = pontos_na_contagem(partida.pontos, tempo)
    numero = fontes["titulo"].render(str(valor), True, AMARELO_DESTAQUE)
    depois = tempo - DURACAO_CONTAGEM
    if 0 <= depois < DURACAO_PULO:
        escala = 1 + 0.35 * (1 - depois / DURACAO_PULO)
        numero = pygame.transform.smoothscale(
            numero, (int(numero.get_width() * escala), int(numero.get_height() * escala)))
    tela.blit(numero, numero.get_rect(center=(LARGURA // 2, caixa.top + 150)))
    contando = tempo < DURACAO_CONTAGEM

    # uma linha curta abaixo do número (vitória ou recorde), só depois da contagem
    if contando:
        pass
    elif getattr(partida, "venceu", False):
        texto(tela, fontes["pequena_n"], "Você limpou a cidade!", VERDE_OK, center=(LARGURA // 2, caixa.top + 200))
    elif info and info.get("novo_recorde"):
        texto(tela, fontes["pequena_n"], f"NOVO RECORDE no {partida.dificuldade}!", VERDE_OK,
              center=(LARGURA // 2, caixa.top + 200))

    for i, nome in enumerate(BOTOES_FIM):
        botao = pygame.Rect(0, 0, 360, 50)
        botao.center = (LARGURA // 2, caixa.top + 260 + i * 66)
        selecionado = i == selecao
        painel(tela, botao, (60, 120, 70) if selecionado else CINZA_ESCURO,
               AMARELO_DESTAQUE if selecionado else (150, 150, 160))
        texto(tela, fontes["media_n"], nome, BRANCO, center=botao.center)

    texto(tela, fontes["pequena"], "↑ ↓ escolher  •  ENTER confirmar  •  TAB ver detalhes", BRANCO,
          center=(LARGURA // 2, ALTURA - 30))
