#!/usr/bin/env python3

import time

from hardware.ADCDevice import (
    ADCDevice,
    ADS7830
)


# =====================================================
# CONFIGURAÇÃO
# =====================================================

ADC_ADDRESS = 0x48


# =====================================================
# ADC
# =====================================================

adc = ADCDevice(
    ADC_ADDRESS
)


# =====================================================
# SETUP
# =====================================================

def setup():

    global adc

    print(
        "Procurando ADS7830 em 0x48..."
    )

    if adc.detectI2C(
        ADC_ADDRESS
    ):

        print(
            "ADS7830 encontrado!"
        )

        adc = ADS7830(
            ADC_ADDRESS
        )

    else:

        print()
        print(
            "ADS7830 nao encontrado."
        )

        print(
            "Verifique com:"
        )

        print(
            "sudo i2cdetect -y 1"
        )

        exit(-1)


# =====================================================
# LOOP
# =====================================================

def loop():

    print()
    print(
        "Teste dos potenciometros"
    )

    print()
    print(
        "Gire um potenciometro por vez."
    )

    print(
        "Observe quais canais mudam."
    )

    print()
    print(
        "CTRL+C para sair."
    )

    print()

    while True:

        values = []

        # =================================================
        # LÊ TODOS OS 8 CANAIS
        # =================================================

        for channel in range(8):

            value = adc.analogRead(
                channel
            )

            values.append(
                value
            )

        # =================================================
        # MOSTRA
        # =================================================

        print(
            " | ".join(
                [
                    f"CH{channel}: {values[channel]:3d}"
                    for channel in range(8)
                ]
            )
        )

        time.sleep(
            0.15
        )


# =====================================================
# FINALIZAR
# =====================================================

def destroy():

    print()
    print(
        "Finalizando..."
    )

    try:

        adc.close()

    except Exception:

        pass


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    try:

        setup()
        loop()

    except KeyboardInterrupt:

        print()
        print(
            "Teste interrompido."
        )

    finally:

        destroy()