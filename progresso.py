"""Progresso salvo do modo infinito, SEPARADO POR DIFICULDADE.

Cada dificuldade (Fácil, Normal, Difícil) tem a sua carteira de pontos, os seus upgrades
e o seu recorde. Upgrade comprado no Fácil só vale no Fácil (o mapa não importa).

Fica em save/progresso.json (ao lado do código, ou ao lado do .exe).
Se o arquivo estiver faltando ou corrompido, começa do zero sem travar o jogo.
"""

import json
import os
import sys

PASTA_SAVE = "save"
ARQUIVO_SAVE = "progresso.json"
DIFICULDADE_PADRAO = "Normal"   # para onde vai o progresso salvo por versões antigas


def _caminho():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, PASTA_SAVE, ARQUIVO_SAVE)


class Progresso:
    def __init__(self):
        self.dados = {}   # dificuldade -> {"carteira": int, "upgrades": {id: nivel}, "recorde": int}
        self.carregar()

    def _da(self, dificuldade):
        return self.dados.setdefault(dificuldade, {"carteira": 0, "upgrades": {}, "recorde": 0})

    # ------------------------------------------------------------ leitura
    def carteira(self, dificuldade):
        return self._da(dificuldade)["carteira"]

    def upgrades(self, dificuldade):
        return dict(self._da(dificuldade)["upgrades"])

    def nivel(self, dificuldade, upgrade_id):
        return self._da(dificuldade)["upgrades"].get(upgrade_id, 0)

    def recorde(self, dificuldade):
        return self._da(dificuldade)["recorde"]

    # ------------------------------------------------------------ escrita
    def comprar_nivel(self, dificuldade, upgrade_id, preco):
        dados = self._da(dificuldade)
        dados["carteira"] -= preco
        dados["upgrades"][upgrade_id] = dados["upgrades"].get(upgrade_id, 0) + 1
        self.salvar()

    def registrar_partida(self, dificuldade, pontos):
        """Soma os pontos na carteira DESTA dificuldade e atualiza o recorde.
        Retorna True se for recorde novo."""
        dados = self._da(dificuldade)
        dados["carteira"] += pontos
        novo_recorde = pontos > dados["recorde"]
        if novo_recorde:
            dados["recorde"] = pontos
        self.salvar()
        return novo_recorde

    # ------------------------------------------------------------ arquivo
    def carregar(self):
        try:
            with open(_caminho(), encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
            if "dificuldades" in bruto:
                for dif, d in bruto["dificuldades"].items():
                    self.dados[dif] = {
                        "carteira": int(d.get("carteira", 0)),
                        "upgrades": {k: int(v) for k, v in d.get("upgrades", {}).items()},
                        "recorde": int(d.get("recorde", 0)),
                    }
            else:
                # Formato antigo (uma carteira só): vai para a dificuldade Normal.
                padrao = self._da(DIFICULDADE_PADRAO)
                padrao["carteira"] = int(bruto.get("carteira", 0))
                padrao["upgrades"] = {k: int(v) for k, v in bruto.get("upgrades", {}).items()}
                for dif, valor in bruto.get("recordes", {}).items():
                    self._da(dif)["recorde"] = int(valor)
        except (OSError, ValueError, TypeError, AttributeError):
            pass

    def salvar(self):
        try:
            os.makedirs(os.path.dirname(_caminho()), exist_ok=True)
            with open(_caminho(), "w", encoding="utf-8") as arquivo:
                json.dump({"dificuldades": self.dados}, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            pass
