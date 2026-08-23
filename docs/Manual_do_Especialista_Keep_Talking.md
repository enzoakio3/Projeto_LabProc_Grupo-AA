# Manual de Desativação --- Keep Talking (Raspberry Pi)

**Manual do Especialista --- versão 1.0**

## Como jogar

Um jogador é o **Desarmador**: ele vê a interface do jogo e opera a
Raspberry Pi. O outro é o **Especialista**: ele consulta este manual e
orienta o Desarmador.

-   **Objetivo:** concluir os cinco módulos antes que o cronômetro
    chegue a `00:00`.
-   **Tempo de partida:** 5 minutos.
-   **Módulos:** Sequência, Senha, Fios, Labirinto e Relógios.
-   O Especialista não deve ver a interface do jogo.

------------------------------------------------------------------------

## 1. Módulo de Sequência

O Desarmador inicia o módulo, observa a sequência de quatro cores
apresentada e informa as quatro cores ao Especialista, na ordem. O
Especialista procura a sequência na tabela e informa quais botões devem
ser pressionados.

  -----------------------------------------------------------------------
  Sequência mostrada                  Resposta a pressionar
  ----------------------------------- -----------------------------------
  Vermelho → Azul → Verde → Amarelo   Amarelo → Verde → Vermelho → Azul

  Azul → Azul → Vermelho → Verde      Verde → Amarelo → Azul → Vermelho

  Verde → Amarelo → Vermelho → Azul   Azul → Vermelho → Amarelo → Verde

  Amarelo → Vermelho → Azul → Verde   Vermelho → Verde → Azul → Amarelo

  Vermelho → Verde → Vermelho → Azul  Azul → Amarelo → Verde → Vermelho

  Azul → Verde → Amarelo → Vermelho   Verde → Vermelho → Azul → Amarelo

  Verde → Vermelho → Amarelo →        Vermelho → Azul → Verde → Azul
  Amarelo                             

  Amarelo → Azul → Verde → Vermelho   Azul → Verde → Vermelho → Amarelo
  -----------------------------------------------------------------------

Se a resposta estiver errada, o módulo sinaliza erro e a sequência deve
ser tentada novamente.

------------------------------------------------------------------------

## 2. Módulo de Senha

O Desarmador informa ao Especialista o **código do dispositivo**
mostrado na tela. O Especialista procura o código e informa a senha
correspondente.

    Código   Senha
  -------- -------
       317    4821
       428    7315
       592    2048
       731    9163
       846    3572

### Controles do keypad

-   `0–9`: digitar a senha
-   `*`: apagar
-   `#`: confirmar

------------------------------------------------------------------------

## 3. Módulo de Fios

O Desarmador informa ao Especialista as cores dos **cinco fios, da
esquerda para a direita**, e o **número serial** exibido.

O Especialista deve verificar as regras **na ordem abaixo** e parar na
primeira regra verdadeira.

1.  Se **não existe nenhum fio vermelho**, corte o **2º fio**.
2.  Se o **último fio é amarelo** e o **número serial é ímpar**, corte o
    **5º fio (último)**.
3.  Se existe **exatamente um fio azul**, corte o **fio azul**.
4.  Se existem **dois ou mais fios vermelhos**, corte o **último fio
    vermelho**.
5.  Se nenhuma regra anterior se aplica, corte o **1º fio**.

> **Importante:** a ordem das regras faz parte do puzzle. Não pule
> diretamente para uma regra posterior.

------------------------------------------------------------------------

## 4. Módulo de Labirinto

O Desarmador informa os **dois símbolos** exibidos. O jogador controla a
posição com o joystick. O início é `A1` e o destino é `H8`.

O Especialista escolhe o mapa pelo par de símbolos e orienta o
Desarmador célula por célula.

**Legenda:** `S` = início, `G` = destino, `█` = parede, `·` = caminho.

### Círculo + Triângulo

``` text
    1 2 3 4 5 6 7 8
A   S · · █ · · · ·
B   █ █ · █ · █ █ ·
C   · · · █ · · · ·
D   · █ █ █ █ █ █ ·
E   · · · · · · · ·
F   █ █ █ · █ █ █ ·
G   · · · · · · █ ·
H   · █ █ █ █ · · G
```

### Quadrado + Círculo

``` text
    1 2 3 4 5 6 7 8
A   S · · · · █ · ·
B   █ █ █ █ · █ · █
C   · · · · · █ · ·
D   · █ █ █ █ █ █ ·
E   · · · · · · · ·
F   █ █ · █ █ █ █ ·
G   · · · · · · · ·
H   · █ █ █ █ █ █ G
```

### Triângulo + Quadrado

``` text
    1 2 3 4 5 6 7 8
A   S █ · · · · · ·
B   · █ · █ █ █ █ ·
C   · · · · · · █ ·
D   █ █ █ █ █ · █ ·
E   · · · · · · █ ·
F   · █ █ █ █ █ █ ·
G   · · · · · · · ·
H   █ █ █ █ █ █ █ G
```

### Círculo + Losango

``` text
    1 2 3 4 5 6 7 8
A   S · · · █ · · ·
B   █ █ █ · █ · █ ·
C   · · · · █ · █ ·
D   · █ █ █ █ · █ ·
E   · · · · · · █ ·
F   █ █ █ █ █ · █ ·
G   · · · · · · █ ·
H   · █ █ █ █ █ █ G
```

Bater em uma parede ou tentar sair do mapa gera erro.

------------------------------------------------------------------------

## 5. Módulo dos Relógios

Existem três relógios, cada um associado a um símbolo. O Desarmador
informa ao Especialista os três símbolos, da esquerda para a direita. O
Especialista informa a posição correta de cada ponteiro.

  Símbolo     Posição do ponteiro
  ----------- ---------------------
  Círculo     9 horas
  Triângulo   11 horas
  Quadrado    1 hora
  Losango     3 horas
  Estrela     12 horas
  Cruz        2 horas

O Desarmador ajusta os três potenciômetros. Os três ponteiros precisam
permanecer simultaneamente nas posições corretas por aproximadamente **1
segundo** para concluir o módulo.

------------------------------------------------------------------------

## Resumo rápido do Especialista

  -----------------------------------------------------------------------
  Módulo                  Pergunte ao Desarmador  Responda com
  ----------------------- ----------------------- -----------------------
  Sequência               Quais foram as 4 cores? A sequência de 4 botões
                                                  da tabela

  Senha                   Qual é o código do      A senha de 4 dígitos
                          dispositivo?            

  Fios                    Quais são os 5 fios e   Qual fio cortar
                          qual o serial?          

  Labirinto               Quais são os 2          Direções até H8 sem
                          símbolos? Onde você     tocar nas paredes
                          está?                   

  Relógios                Quais são os 3 simbolos?        A hora de cada ponteiro            

  -----------------------------------------------------------------------


**Boa sorte.**
