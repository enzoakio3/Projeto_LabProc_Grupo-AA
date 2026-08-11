#!/usr/bin/env python3

import time

from hardware import Keypad


# =====================================================
# CONFIGURAÇÃO DO TECLADO 4x4
# =====================================================

ROWS = 4
COLS = 4

KEYS = [
    '1', '2', '3', 'A',
    '4', '5', '6', 'B',
    '7', '8', '9', 'C',
    '*', '0', '#', 'D'
]

# Pinos usados pelo exemplo MatrixKeypad.py da Freenove
ROWS_PINS = [
    16,
    20,
    21,
    26
]

COLS_PINS = [
    19,
    13,
    6,
    5
]


# =====================================================
# CRIAR KEYPAD
# =====================================================

keypad = Keypad.Keypad(
    KEYS,
    ROWS_PINS,
    COLS_PINS,
    ROWS,
    COLS
)

# Mesmo debounce usado no exemplo oficial
keypad.setDebounceTime(
    50
)


# =====================================================
# MAIN
# =====================================================

print()
print("Teste do teclado matricial iniciado.")
print()
print("Pressione as teclas do keypad.")
print("CTRL+C para sair.")
print()


try:

    while True:

        key = keypad.getKey()

        if key != keypad.NULL:

            print(
                f"Tecla pressionada: {key}"
            )

        # Pequena pausa para não ocupar 100% da CPU
        time.sleep(
            0.01
        )


except KeyboardInterrupt:

    print()
    print("Teste encerrado.")