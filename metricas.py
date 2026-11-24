"""Grava as métricas de cada run em CSV.

É com estes dados que o grupo mostra se o jogo ajudou:
os erros de separação por minuto devem cair ao longo das ondas e entre runs.
"""

import csv
import os
import sys
from datetime import datetime

from cartas import resumo_cartas
from config import PASTA_METRICAS, ARQUIVO_METRICAS

COLUNAS = ["data_hora", "partida_id", "onda", "cenario", "evento", "custo", "acertos", "erros",
           "caidos", "duracao_s", "erros_por_minuto", "precisao_pct", "pontos_total", "venceu",
           "cartas_da_run", "itens_errados"]


def caminho_arquivo():
    # No executável (.exe) a pasta de métricas fica ao lado do .exe;
    # rodando com "python main.py", fica ao lado do código.
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    pasta = os.path.join(base, PASTA_METRICAS)
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, ARQUIVO_METRICAS)


def _preparar_arquivo(caminho, colunas):
    """Se existir um CSV de uma versão antiga do jogo (colunas diferentes), guarda com outro nome."""
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding="utf-8") as arquivo:
        cabecalho = arquivo.readline().strip().split(";")
    if cabecalho != colunas:
        antigo = caminho.replace(".csv", f"_antigo_{datetime.now():%Y%m%d%H%M%S}.csv")
        os.replace(caminho, antigo)


def salvar_partida(partida):
    """Acrescenta uma linha por onda jogada. Retorna o caminho do arquivo (ou None)."""
    agora = datetime.now()
    partida_id = agora.strftime("%Y%m%d%H%M%S")
    try:
        caminho = caminho_arquivo()
        _preparar_arquivo(caminho, COLUNAS)
        novo = not os.path.exists(caminho)
        with open(caminho, "a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS, delimiter=";")
            if novo:
                escritor.writeheader()
            for r in partida.resultados:
                escritor.writerow({
                    "data_hora": agora.strftime("%Y-%m-%d %H:%M:%S"),
                    "partida_id": partida_id,
                    "onda": r["onda"],
                    "cenario": r["cenario"],
                    "evento": r["evento"],
                    "custo": r["custo"],
                    "acertos": r["acertos"],
                    "erros": r["erros"],
                    "caidos": r["caidos"],
                    "duracao_s": r["duracao_s"],
                    "erros_por_minuto": r["erros_por_minuto"],
                    "precisao_pct": r["precisao_pct"],
                    "pontos_total": partida.pontos,
                    "venceu": "sim" if partida.venceu else "nao",
                    "cartas_da_run": resumo_cartas(partida.cartas),
                    "itens_errados": "|".join(r["itens_errados"]),
                })
        return caminho
    except OSError:
        return None


# ------------------------------------------------------------------ modo infinito
ARQUIVO_INFINITO = "infinito.csv"
COLUNAS_INFINITO = ["data_hora", "partida_id", "mapa", "dificuldade", "lixeiras", "minuto",
                    "acertos", "erros", "caidos", "duracao_s", "erros_por_minuto", "precisao_pct",
                    "pontos_total", "tempo_total_s", "cartas_da_partida", "upgrades", "itens_errados"]


def salvar_infinito(partida):
    """Uma linha por minuto jogado no modo infinito. Retorna o caminho do arquivo (ou None)."""
    agora = datetime.now()
    try:
        caminho = os.path.join(os.path.dirname(caminho_arquivo()), ARQUIVO_INFINITO)
        _preparar_arquivo(caminho, COLUNAS_INFINITO)
        novo = not os.path.exists(caminho)
        upgrades =", ".join(f"{k} {v}" for k, v in partida.upgrades_usados.items() if v)
        with open(caminho, "a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_INFINITO, delimiter=";")
            if novo:
                escritor.writeheader()
            for b in partida.blocos:
                escritor.writerow({
                    "data_hora": agora.strftime("%Y-%m-%d %H:%M:%S"),
                    "partida_id": agora.strftime("%Y%m%d%H%M%S"),
                    "mapa": partida.fase["nome"],
                    "dificuldade": partida.dificuldade,
                    "lixeiras": len(partida.categorias),
                    "minuto": b["minuto"],
                    "acertos": b["acertos"],
                    "erros": b["erros"],
                    "caidos": b["caidos"],
                    "duracao_s": b["duracao_s"],
                    "erros_por_minuto": b["erros_por_minuto"],
                    "precisao_pct": b["precisao_pct"],
                    "pontos_total": partida.pontos,
                    "tempo_total_s": round(partida.tempo, 1),
                    "cartas_da_partida": resumo_cartas(partida.cartas),
                    "upgrades": upgrades,
                    "itens_errados": "|".join(b["itens_errados"]),
                })
        return caminho
    except OSError:
        return None
