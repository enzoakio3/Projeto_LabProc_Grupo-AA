#!/usr/bin/env python3

import time
from hardware.ADCDevice import ADCDevice, ADS7830


# =====================================================
# CONFIGURAÇÃO
# =====================================================

ADC_ADDRESS = 0x48

X_CHANNEL = 5
Y_CHANNEL = 6

adc = ADCDevice(ADC_ADDRESS)


# =====================================================
# SETUP
# =====================================================

def setup():

    global adc

    print("Procurando ADS7830 no endereco 0x48...")

    if adc.detectI2C(ADC_ADDRESS):

        print("ADS7830 encontrado!")

        adc = ADS7830(ADC_ADDRESS)

    else:

        print()
        print("ERRO: ADS7830 nao encontrado.")
        print()
        print("Execute no terminal:")
        print()
        print("    sudo i2cdetect -y 1")
        print()
        print("e verifique se aparece o endereco 48.")

        exit(-1)


# =====================================================
# LOOP
# =====================================================

def loop():

    print()
    print("Teste do joystick iniciado.")
    print("Mova o joystick nas quatro direcoes.")
    print("Pressione CTRL+C para sair.")
    print()

    while True:

        # Mesmo mapeamento usado pelo exemplo da Freenove
        value_x = adc.analogRead(X_CHANNEL)
        value_y = adc.analogRead(Y_CHANNEL)

        print(
            f"X: {value_x:3d} | "
            f"Y: {value_y:3d}"
        )

        time.sleep(0.1)


# =====================================================
# FINALIZAR
# =====================================================

def destroy():

    print()
    print("Finalizando teste...")

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
        print("Teste interrompido.")

    finally:

        destroy()