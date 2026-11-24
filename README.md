# Lixeira Certa

Serious game 2D em Pygame com camada roguelike · Desafio P2 · Tema 03: Meio ambiente e cidade limpa.

**Problema:** moradores descartam recicláveis na lixeira errada porque não reconhecem o
material, principalmente os itens que confundem (tampa de metal do pote de vidro, caixa de
ovo de papelão, filtro de café usado). O jogo treina esse reconhecimento sob pressão de tempo: para jogar bem,
é preciso separar certo.

## Como executar

1. Instale o Python 3.10 ou mais novo (https://www.python.org). No Windows, marque
   "Add Python to PATH" durante a instalação.
2. Abra um terminal **dentro desta pasta** e instale o Pygame:
   ```
   pip install -r requirements.txt
   ```
3. Rode o jogo:
   ```
   python main.py
   ```

O jogo não usa nenhum asset de terceiros: imagens, efeitos sonoros e músicas são gerados
por código.

### Música ambiente

Cada cenário tem sua música em loop: `musicas/cozinha.wav`, `musicas/rua.wav`,
`musicas/praia.wav` e `musicas/feira.wav` (a da praia também toca no menu). O volume é
baixo de propósito (`VOLUME_MUSICA` em `config.py`), só para ambientar. Elas são geradas pelo script:
```
python gerar_musicas.py
```
Para usar outra música, basta substituir o `.wav` mantendo o nome (declarar a origem nos
créditos). Tecla **M** liga/desliga a música.

### Executável para Windows (sem precisar de Python)

Para gerar o `LixeiraCerta.exe` (um único arquivo que abre com dois cliques, com as músicas
embutidas):
```
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name LixeiraCerta --add-data "musicas;musicas" main.py
```
O executável fica na pasta `dist`. As métricas da versão .exe são salvas em uma pasta
`metricas` ao lado do executável. Gere o .exe de novo sempre que mudar o código.

## Controles

| Tecla | Ação |
|---|---|
| ← → ou A D | Mover a lixeira |
| Q W E R T | Escolher a cor da lixeira: Q Papel, W Plástico, E Vidro, R Metal, T Orgânico |
| ← → + ENTER | Escolher carta entre as ondas |
| P | Pausar |
| M | Liga/desliga a música |
| F11 | Tela cheia (a janela também pode ser redimensionada) |
| ESC | Voltar ao menu |
| TAB | Na tela de fim: mostrar/esconder os detalhes (tabela por onda/minuto e itens para revisar) |
| ENTER | Confirmar nos menus |

## Modos de jogo

- **Modo campanha:** 4 cenários e 12 ondas, com uma lixeira nova a cada cenário. Tem fim (vitória
  na onda 12).
- **Modo infinito:** sem fim, num mapa só. Você escolhe a dificuldade (que define quantas
  lixeiras, vidas e velocidade), ganha cartas por pontos e compra upgrades na loja.

## Modo campanha

**Estrutura da run**
- Uma run tem **12 ondas de 30 segundos** em 4 cenários (3 ondas cada). A cada cenário
  entra **uma lixeira nova**:

  | Cenário | Lixeiras | Novidade |
  |---|---|---|
  | 1. Cozinha de casa | 2 | Papel (Q) e Plástico (W) |
  | 2. Rua do bairro | 3 | + Vidro (E) |
  | 3. Orla da lagoa | 4 | + Metal (R) |
  | 4. Feira livre | 5 | + Orgânico (T) |

- **Cada cenário começa devagar:** a 1ª onda é a introdução da lixeira nova. Nas ondas seguintes do mesmo cenário os resíduos caem 15% mais rápido e surgem 10% mais seguido a cada onda. Ao trocar de cenário, a velocidade volta ao início.
- Começa com 5 vidas e ganha +1 ao chegar num cenário novo (máximo 7).
- Perdeu todas as vidas: a run acaba e começa do zero. Venceu a onda 12: vitória.

**Separação**
- Resíduo na lixeira certa: +10 pontos, mais 2 por acerto seguido (combo, limite +20).
- Resíduo na lixeira errada: −1 vida, e uma mensagem explica onde o item deveria ir.
- Resíduo no chão: −5 pontos, e a sujeira fica visível no cenário.

**Cartas (entre as ondas, escolha 1 de 3)**

Toda carta é uma troca: a **vantagem vale pelo resto da run** e o **custo vale só na
próxima onda**.

| Carta | Vantagem (run toda) | Custo (próxima onda) |
|---|---|---|
| Lixeira larga | Boca da lixeira +20% (até 3x) | Ventania: os resíduos balançam ao cair |
| Câmera lenta | Queda −12% (até 3x) | Chuva de lixo: cai o dobro de resíduos |
| Segunda chance | O próximo erro não tira vida (o erro conta e a explicação aparece) | Sem rótulo: os nomes dos resíduos somem |
| Combo de mestre | Bônus de combo dobra (única) | Lixeira pesada: lixeira 30% mais lenta |
| Vassoura | Resíduo no chão não tira pontos (única) | Queda rápida: resíduos 20% mais rápidos |
| Coração | +1 vida (máximo 7) | Erro dobrado: cada erro tira 2 vidas |

As vantagens ajudam a **pegar** os resíduos, nunca a escolher a cor: a decisão de separar
continua sendo do jogador. O custo "Sem rótulo" obriga a reconhecer o material pelo
desenho (o filtro de café usado tem manchas de borra).

**Eventos** (40% de chance por onda, exceto a 1ª de cada cenário)
- Dia de mudança: papel aparece mais.
- Depois da festa: vidro e metal aparecem mais (a partir da Orla).
- Onda das pegadinhas: só caem itens que confundem (a partir da Orla).
- Dia de feira: orgânico aparece mais (na Feira).

## Modo infinito

**Antes de começar** (setas ↑ ↓ para escolher, ← → para mudar):

- **Mapa:** Cozinha de casa, Rua do bairro, Orla da lagoa ou Feira livre.
- **Dificuldade** (define tudo junto):

| Dificuldade | Lixeiras | Vidas | Velocidade dos itens | Acelera a cada 45 s |
|---|---|---|---|---|
| Fácil | 3: Papel, Plástico, Vidro | 7 | x0,8 | +5% |
| Normal | 4: + Metal | 5 | x1 | +8% |
| Difícil | 5: + Orgânico | 3 | x1,3 | +12% (itens mais seguidos) |

**Regras**
- Só caem resíduos das lixeiras liberadas pela dificuldade.
- Não tem fim: **a cada 45 segundos** sobe um nível (aviso "Mais rápido!" na tela e nível no HUD): a queda acelera (até 2x) e os resíduos surgem 6% mais seguido.
- **Cartas por pontos:** a primeira aos 300 pontos; cada carta seguinte pede 30% mais pontos.
  As mesmas cartas da campanha, mas o **custo dura 30 segundos**.
- Acaba quando as vidas acabam (limite de 10 vidas neste modo).
- Os pontos da partida vão para a **carteira da dificuldade jogada**, e o recorde de cada
  dificuldade fica salvo.

**Loja de upgrades:** só vale no modo infinito, e **cada dificuldade tem a sua loja**: carteira,
upgrades e recorde separados. Upgrade comprado no Fácil só vale no Fácil, em qualquer mapa.
Na loja, ← → troca a dificuldade. Preço do nível N = preço base × N.

| Upgrade | Efeito por nível | Níveis | Preço base |
|---|---|---|---|
| Lixeira veloz | +10% de velocidade da lixeira | 5 | 1000 |
| Boca larga | +8% de largura da lixeira | 5 | 1250 |
| Vida extra | +1 vida no começo | 3 | 2000 |
| Escudo inicial | +1 escudo no começo | 3 | 1750 |
| Combo turbinado | +1 ponto de bônus por acerto seguido | 5 | 1500 |
| Mais pontos | +2 pontos por resíduo na lixeira certa (base 10) | 5 | 1500 |

Carteira, upgrades e recordes de cada dificuldade ficam em `save/progresso.json` (ao lado do
.exe na versão executável). Apagar esse arquivo zera o progresso. Saves de versões antigas
(com uma carteira só) são convertidos automaticamente para a dificuldade Normal.

## Métricas (como saber que o jogo ajudou)

Cada run grava uma linha por onda em `metricas/partidas.csv` (separador `;`, abre no
Excel): cenário, evento, custo da carta, acertos, erros, caídos, **erros por minuto**, precisão,
cartas da run e quais itens o jogador errou. A tela final compara os erros por minuto
da 1ª e da última onda. Comparar várias runs da mesma pessoa mostra se os erros caíram.

O modo infinito grava em `metricas/infinito.csv` **uma linha por minuto jogado** (mapa,
dificuldade, número de lixeiras, acertos, erros, erros por minuto, precisão, cartas, upgrades e
itens errados). Como o número de lixeiras não muda durante a partida, é o melhor lugar para
comparar os erros por minuto ao longo do tempo.

## Estrutura do código

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada e máquina de estados das telas |
| `config.py` | Todos os números do jogo (velocidades, vidas, pontos, cartas, eventos) |
| `partida.py` | Modo campanha e regras comuns: acerto, erro, chão, vidas, pontos, custos das cartas |
| `infinito.py` | Modo infinito (herda de `Partida`): dificuldade crescente, cartas por pontos |
| `loja.py` | Upgrades do modo infinito: preços, níveis e compra |
| `progresso.py` | Carteira, upgrades e recorde de cada dificuldade, salvos em `save/progresso.json` |
| `cartas.py` | Cartas (vantagem + custo): sorteio e aplicação |
| `eventos.py` | Eventos sorteados que mudam os resíduos de uma onda |
| `fases.py` | Os 4 cenários e as fórmulas de dificuldade por onda |
| `residuo.py` | Categorias da coleta seletiva, catálogo de resíduos e classe `Residuo` |
| `lixeira.py` | Classe `Lixeira` (mover, trocar cor, receber) |
| `telas.py` | Menu, instruções, HUD, cenário novo, cartas, pausa, resultado |
| `cenario.py` | Fundos de cada cenário e sujeira no chão |
| `audio.py` | Efeitos sonoros gerados por código |
| `musica.py` | Música ambiente de cada cenário (troca e liga/desliga) |
| `gerar_musicas.py` | Script que sintetiza as músicas e grava em `musicas/` |
| `metricas.py` | Gravação do CSV de métricas |

## Rastreabilidade (seção 13 do GDD)

| Regra no GDD | Onde está no código | Situação |
|---|---|---|
| Lixeira muda de cor com Q W E R T | `partida.py` · `TECLAS_CATEGORIA`, `Partida.tratar_evento()`, `lixeira.py` · `Lixeira.selecionar()` | Implementado |
| Resíduo na lixeira certa soma 10 pts + combo | `partida.py` · `Partida._acertou()`, `config.py` · `PONTOS_ACERTO`, `BONUS_COMBO` | Implementado |
| Resíduo na lixeira errada tira 1 vida e explica o motivo | `lixeira.py` · `Lixeira.receber()`, `partida.py` · `Partida._errou()` | Implementado |
| Resíduo no chão tira 5 pts e suja o cenário | `partida.py` · `Partida._caiu_no_chao()`, `config.py` · `PENALIDADE_CHAO` | Implementado |
| Run de 12 ondas de 30 s em 4 cenários | `config.py` · `DURACAO_ONDA`, `ONDAS_POR_FASE`, `partida.py` · `TOTAL_ONDAS` | Implementado |
| Campanha: cada cenário começa devagar e acelera 15% por onda dentro dele | `config.py` · `ACELERACAO_ONDA`, `fases.py` · `velocidade_queda()`, `partida.py` · `Partida.iniciar_onda()` (`onda_no_cenario`) | Implementado |
| Uma lixeira nova por cenário (2 → 3 → 4 → 5) | `fases.py` · `FASES[...]["categorias"]` | Implementado |
| Material novo aparece com mais frequência | `config.py` · `PESO_MATERIAL_NOVO`, `fases.py` · `tipos_da_fase()` | Implementado |
| Escolha de 1 entre 3 cartas; vantagem vale a run toda | `cartas.py` · `sortear_oferta()`, `aplicar_carta()`, `partida.py` · `Partida.escolher_carta()` | Implementado |
| Custo da carta vale só na próxima onda | `partida.py` · `Partida.iniciar_onda()`, `_finalizar_onda()`, `config.py` · `BALANCO_VENTO`, `FATOR_INTERVALO_CHUVA`, `FATOR_LIXEIRA_LENTA`, `FATOR_QUEDA_RAPIDA`, `DANO_ERRO_DOBRADO` | Implementado |
| Eventos sorteados por onda | `eventos.py` · `sortear_evento()`, `aplicar_evento()`, `config.py` · `CHANCE_EVENTO` | Implementado |
| Run reinicia do zero ao perder todas as vidas | `main.py` (nova `Partida` a cada "Jogar"), `partida.py` · `Partida.atualizar()` | Implementado |
| +1 vida ao chegar num cenário novo | `config.py` · `VIDA_BONUS_FASE`, `partida.py` · `Partida.escolher_carta()` | Implementado |
| Métricas por onda salvas em CSV | `partida.py` · `Partida._finalizar_onda()`, `metricas.py` · `salvar_partida()` | Implementado |
| Tela de fim simples (PONTOS + botões Jogar novamente / Menu); TAB mostra os detalhes | `telas.py` · `desenhar_fim()`, `main.py` (estados `RESULTADO`, `RESULTADO_INFINITO`) | Implementado |
| Música ambiente diferente em cada cenário | `main.py` (chamada `musica.tocar(...)`), `musica.py` · `Musica.tocar()`, `gerar_musicas.py` | Implementado |
| Modo infinito sem fim num mapa só | `infinito.py` · `PartidaInfinita`, `_pode_surgir()`, `atualizar()` | Implementado |
| Escolha de mapa e dificuldade; a dificuldade define lixeiras (3/4/5), vidas e velocidade | `main.py` (estado `CONFIG_INFINITO`), `config.py` · `DIFICULDADES`, `infinito.py` · `PartidaInfinita.__init__()` | Implementado |
| Infinito: velocidade sobe em degraus a cada 45 s | `infinito.py` · `atualizar()` (`etapa`), `_velocidade_atual()`, `_intervalo_atual()`, `config.py` · `SEGUNDOS_POR_ETAPA`, `ACEL_MAX_INFINITO`, `REDUCAO_INTERVALO_ETAPA` | Implementado |
| Carta a cada X pontos no infinito; custo dura 30 s | `infinito.py` · `atualizar()`, `escolher_carta()`, `config.py` · `PONTOS_PRIMEIRA_CARTA`, `CRESCIMENTO_CARTA`, `DURACAO_CUSTO_INFINITO` | Implementado |
| Loja de upgrades que só vale no infinito; preço sobe a cada nível | `loja.py` · `UPGRADES`, `Upgrade.preco()`, `comprar()`, `infinito.py` · `PartidaInfinita.__init__()` | Implementado |
| Upgrade "Mais pontos": +2 pontos por acerto por nível | `loja.py` · `BONUS_PONTOS_NIVEL`, `infinito.py` (`pontos_acerto`), `partida.py` · `Partida._acertou()` | Implementado |
| Carteira, upgrades e recorde separados por dificuldade e salvos entre partidas | `progresso.py` · `Progresso` (`carteira()`, `nivel()`, `registrar_partida()`, `salvar()`), `loja.py` · `comprar()` | Implementado |
| Métricas por minuto do infinito em CSV | `infinito.py` · `_fechar_bloco()`, `metricas.py` · `salvar_infinito()` | Implementado |
| Lixeira de rejeito (não reciclável) | — | Removida por decisão de escopo (limitação) |
| Pilhas, lâmpadas e eletrônicos (descarte especial) | — | Não implementado (limitação) |

## Créditos

- Código: equipe. Desenvolvido com apoio de IA generativa (Claude, da Anthropic). Declarar
  na seção 16 do GDD.
- Biblioteca: [pygame-ce](https://pyga.me) (licença LGPL).
- Arte, efeitos sonoros e músicas: gerados por código (`cenario.py`, `audio.py`,
  `gerar_musicas.py`), sem assets de terceiros.
- Cores das lixeiras: Resolução CONAMA nº 275/2001.
