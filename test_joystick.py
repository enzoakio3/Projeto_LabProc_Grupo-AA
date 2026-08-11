#!/usr/bin/env python3

import time
from hardware.ADCDevice import ADCDevice, ADS7830


# =====================================================
# CONFIGURAÇÕES DO ADC / JOYSTICK
# =====================================================

ADC_ADDRESS = 0x48

X_CHANNEL = 5
Y_CHANNEL = 6


# =====================================================
# CRIA OBJETO ADC
# =====================================================

adc = ADCDevice(ADC_ADDRESS)


# =====================================================
# SETUP
# =====================================================

def setup():

    global adc

    print("Procurando ADS7830 no endereco 0x48...")

    if adc.detectI2C(ADC_ADDRESS):

        print("ADS7830 encontrado!")

        adc = ADS7830(
            ADC_ADDRESS
        )

    else:

        print()
        print("ERRO: ADS7830 nao encontrado.")
        print()
        print("Rode:")
        print("sudo i2cdetect -y 1")
        print()
        print("e verifique se aparece 48.")

        exit(-1)


# =====================================================
# INTERPRETAR DIREÇÃO
# =====================================================

def get_direction(x, y):

    # Valores provisórios.
    #
    # Normalmente o centro fica perto de 128.
    # Depois podemos ajustar usando os valores reais
    # que aparecerem na sua placa.

    LOW = 70
    HIGH = 185

    if x < LOW:
        return "ESQUERDA"

    if x > HIGH:
        return "DIREITA"

    if y < LOW:
        return "CIMA"

    if y > HIGH:
        return "BAIXO"

    return "CENTRO"


# =====================================================
# LOOP
# =====================================================

def loop():

    print()
    print("Teste do joystick iniciado.")
    print()
    print("Mova o joystick para:")
    print("- cima")
    print("- baixo")
    print("- esquerda")
    print("- direita")
    print()
    print("CTRL+C para sair.")
    print()

    while True:

        # =================================================
        # LER EIXOS
        # =================================================

        value_x = adc.analogRead(
            X_CHANNEL
        )

        value_y = adc.analogRead(
            Y_CHANNEL
        )

        # =================================================
        # DESCOBRIR DIREÇÃO
        # =================================================

        direction = get_direction(
            value_x,
            value_y
        )

        # =================================================
        # MOSTRAR RESULTADO
        # =================================================

        print(
            f"X = {value_x:3d} | "
            f"Y = {value_y:3d} | "
            f"{direction}"
        )

        time.sleep(
            0.1
        )


# =====================================================
# FINALIZAR
# =====================================================

def destroy():

    print()
    print("Finalizando joystick...")

    try:

        adc.close()

    except Exception:

        pass


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print(
        "Programa iniciado."
    )

    try:

        setup()
        loop()

    except KeyboardInterrupt:

        print()
        print("Teste interrompido.")

    finally:

        destroy()