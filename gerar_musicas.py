"""Gera as músicas ambiente de cada cenário por síntese sonora (sem assets de terceiros).

Rode uma vez (ou sempre que mudar algo aqui):
    python gerar_musicas.py
Cria a pasta musicas/ com cozinha.wav, rua.wav e praia.wav.
As músicas são loops: o fim emenda no começo sem corte.
"""

import array
import math
import os
import random
import wave

TAXA = 22050
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musicas")
DOIS_PI = 2 * math.pi

SEMITONS = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
            "G": -2, "G#": -1, "A": 0, "A#": 1, "Bb": 1, "B": 2}


def freq(nome):
    """'A4' -> 440 Hz."""
    return 440.0 * 2 ** ((SEMITONS[nome[:-1]] + 12 * (int(nome[-1]) - 4)) / 12)


class Faixa:
    """Buffer circular: o que passa do fim volta para o começo (loop perfeito)."""

    def __init__(self, segundos):
        self.n = int(TAXA * segundos)
        self.buf = [0.0] * self.n

    def somar(self, inicio_s, amostras):
        i0 = int(inicio_s * TAXA)
        n = self.n
        buf = self.buf
        for k, v in enumerate(amostras):
            buf[(i0 + k) % n] += v

    def salvar(self, nome, volume=0.6):
        pico = max(abs(v) for v in self.buf) or 1.0
        dados = array.array("h", (int(32767 * volume * v / pico) for v in self.buf))
        os.makedirs(PASTA, exist_ok=True)
        with wave.open(os.path.join(PASTA, nome), "wb") as arquivo:
            arquivo.setnchannels(1)
            arquivo.setsampwidth(2)
            arquivo.setframerate(TAXA)
            arquivo.writeframes(dados.tobytes())


# ---------------------------------------------------------------- instrumentos
def dedilhado(f, dur=1.2, amp=1.0, decaimento=4.0):
    out = []
    for i in range(int(dur * TAXA)):
        t = i / TAXA
        env = math.exp(-decaimento * t) * min(1.0, t * 300)
        out.append(amp * env * (math.sin(DOIS_PI * f * t) + 0.3 * math.sin(2 * DOIS_PI * f * t)))
    return out


def colchao(f, dur, amp=1.0, ataque=0.8):
    out = []
    for i in range(int(dur * TAXA)):
        t = i / TAXA
        env = min(1.0, t / ataque, (dur - t) / ataque)
        v = (math.sin(DOIS_PI * f * t) + math.sin(DOIS_PI * f * 1.004 * t)
             + 0.4 * math.sin(2 * DOIS_PI * f * t))
        out.append(amp * env * v / 2.4)
    return out


def baixo(f, dur, amp=1.0, decaimento=3.0):
    out = []
    for i in range(int(dur * TAXA)):
        t = i / TAXA
        env = math.exp(-decaimento * t) * min(1.0, t * 150)
        out.append(amp * env * (math.sin(DOIS_PI * f * t) + 0.25 * math.sin(3 * DOIS_PI * f * t)))
    return out


def sino(f, dur=2.5, amp=1.0):
    out = []
    for i in range(int(dur * TAXA)):
        t = i / TAXA
        env = math.exp(-2.2 * t) * min(1.0, t * 400)
        out.append(amp * env * (math.sin(DOIS_PI * f * t) + 0.35 * math.sin(2.76 * DOIS_PI * f * t)))
    return out


def chimbal(rng, amp=1.0, dur=0.07):
    return [amp * rng.uniform(-1, 1) * math.exp(-70 * i / TAXA) for i in range(int(dur * TAXA))]


def ondas_do_mar(faixa, rng, amp=1.0, periodo=6.0):
    """Ruído filtrado subindo e descendo devagar, como ondas quebrando."""
    filtrado = 0.0
    out = []
    ciclos = max(1, round(faixa.n / TAXA / periodo))   # número inteiro de ondas = loop sem emenda
    for i in range(faixa.n):
        filtrado += 0.04 * (rng.uniform(-1, 1) - filtrado)
        onda = math.sin(math.pi * ciclos * i / faixa.n) ** 2
        out.append(amp * 4 * filtrado * (0.25 + onda))
    faixa.somar(0, out)


# ---------------------------------------------------------------- músicas
ACORDES = {
    "C": ["C", "E", "G"], "Am": ["A", "C", "E"], "F": ["F", "A", "C"], "G": ["G", "B", "D"],
    "Dm": ["D", "F", "A"], "Bb": ["Bb", "D", "F"], "Fmaj7": ["F", "A", "C", "E"],
}


def notas(acorde, oitava):
    return [freq(f"{n}{oitava}") for n in ACORDES[acorde]]


def musica_cozinha():
    """Alegre e tranquila: tom maior, arpejo dedilhado. 100 bpm."""
    batida = 60 / 100
    progressao = ["C", "Am", "F", "G"] * 2
    faixa = Faixa(len(progressao) * 4 * batida)
    for c, acorde in enumerate(progressao):
        t0 = c * 4 * batida
        for f in notas(acorde, 3):
            faixa.somar(t0, colchao(f, 4 * batida + 0.3, amp=0.22))
        raiz = notas(acorde, 2)[0]
        faixa.somar(t0, baixo(raiz, 1.2, amp=0.55))
        faixa.somar(t0 + 2 * batida, baixo(raiz, 1.2, amp=0.45))
        arpejo = notas(acorde, 4) + [notas(acorde, 5)[0]]
        padrao = [0, 1, 2, 3, 2, 1, 2, 1] if c < 4 else [0, 2, 1, 3, 2, 3, 1, 2]
        for k, idx in enumerate(padrao):
            faixa.somar(t0 + k * batida / 2, dedilhado(arpejo[idx], amp=0.32))
    faixa.salvar("cozinha.wav")


def musica_rua():
    """Urbana e animada: baixo sincopado, chimbal e acordes curtos. 112 bpm."""
    rng = random.Random(7)
    batida = 60 / 112
    progressao = ["Am", "F", "C", "G"] * 2
    faixa = Faixa(len(progressao) * 4 * batida)
    for c, acorde in enumerate(progressao):
        t0 = c * 4 * batida
        for f in notas(acorde, 3):
            faixa.somar(t0, colchao(f, 4 * batida + 0.2, amp=0.12))
        raiz = notas(acorde, 2)[0]
        for tempo in (0, 1.5, 2, 3.5):        # 1, "e" do 2, 3, "e" do 4
            faixa.somar(t0 + tempo * batida, baixo(raiz, 0.5, amp=0.6, decaimento=6))
        for tempo in (1, 3):                   # acordes curtos nos tempos 2 e 4
            for f in notas(acorde, 4):
                faixa.somar(t0 + tempo * batida, dedilhado(f, dur=0.4, amp=0.18, decaimento=9))
        for k in range(8):                     # chimbal em colcheias, mais forte no contratempo
            faixa.somar(t0 + k * batida / 2, chimbal(rng, amp=0.16 if k % 2 else 0.08))
    faixa.salvar("rua.wav")


def musica_praia():
    """Relaxante: colchão longo, sininhos espaçados e ondas do mar. 76 bpm."""
    rng = random.Random(3)
    batida = 60 / 76
    progressao = ["Fmaj7", "C", "Dm", "Bb"] * 2
    faixa = Faixa(len(progressao) * 4 * batida)
    for c, acorde in enumerate(progressao):
        t0 = c * 4 * batida
        for f in notas(acorde, 3):
            faixa.somar(t0, colchao(f, 4 * batida + 0.6, amp=0.3, ataque=1.2))
        faixa.somar(t0, baixo(notas(acorde, 2)[0], 3.0, amp=0.3, decaimento=1.2))
        for tempo in (0, 2.5):
            faixa.somar(t0 + tempo * batida, sino(rng.choice(notas(acorde, 5)), amp=0.22))
    ondas_do_mar(faixa, rng, amp=0.5)
    faixa.salvar("praia.wav")


def musica_feira():
    """Feira animada: baixo alternando tônica e quinta, acordes no contratempo. 120 bpm."""
    rng = random.Random(11)
    batida = 60 / 120
    progressao = ["F", "Dm", "Bb", "C"] * 2
    faixa = Faixa(len(progressao) * 4 * batida)
    for c, acorde in enumerate(progressao):
        t0 = c * 4 * batida
        for f in notas(acorde, 3):
            faixa.somar(t0, colchao(f, 4 * batida + 0.2, amp=0.1))
        graves = notas(acorde, 2)
        for tempo in range(4):                 # tônica e quinta alternadas
            nota_baixo = graves[0] if tempo % 2 == 0 else graves[2]
            faixa.somar(t0 + tempo * batida, baixo(nota_baixo, 0.45, amp=0.55, decaimento=6))
        for tempo in (0.5, 1.5, 2.5, 3.5):     # acordes curtos no contratempo
            for f in notas(acorde, 4):
                faixa.somar(t0 + tempo * batida, dedilhado(f, dur=0.35, amp=0.16, decaimento=10))
        melodia = notas(acorde, 5)
        for tempo in (0, 1, 3):
            faixa.somar(t0 + tempo * batida, dedilhado(rng.choice(melodia), dur=0.6, amp=0.14, decaimento=6))
        for k in range(8):
            faixa.somar(t0 + k * batida / 2, chimbal(rng, amp=0.07))
    faixa.salvar("feira.wav")


if __name__ == "__main__":
    for gerar in (musica_cozinha, musica_rua, musica_praia, musica_feira):
        print("Gerando", gerar.__name__, "...")
        gerar()
    print("Pronto! Arquivos em", PASTA)
