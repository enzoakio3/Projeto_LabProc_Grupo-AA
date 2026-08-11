#!/usr/bin/env python3

import math
import pygame

from hardware.ADCDevice import (
    ADCDevice,
    ADS7830
)


# =====================================================
# CONFIGURAÇÕES
# =====================================================

WIDTH = 640
HEIGHT = 480

ADC_ADDRESS = 0x48

POT_CHANNELS = [
    2,
    3,
    4
]

# Valores observados
ADC_MIN = 0
ADC_MAX = 250


# =====================================================
# PYGAME
# =====================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Teste dos Relogios"
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    28
)

small_font = pygame.font.Font(
    None,
    22
)


# =====================================================
# ADC
# =====================================================

adc = ADCDevice(
    ADC_ADDRESS
)


def setup_adc():

    global adc

    if adc.detectI2C(
        ADC_ADDRESS
    ):

        adc = ADS7830(
            ADC_ADDRESS
        )

        print(
            "ADS7830 encontrado!"
        )

    else:

        print(
            "ADS7830 nao encontrado."
        )

        exit(-1)


# =====================================================
# LIMITAR VALOR
# =====================================================

def clamp(
    value,
    minimum,
    maximum
):

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )


# =====================================================
# ADC -> ÂNGULO
# =====================================================

def adc_to_angle(
    value
):

    # =================================================
    # FAIXA DO ADC
    # =================================================

    value = clamp(
        value,
        ADC_MIN,
        ADC_MAX
    )

    # Normaliza:
    #
    # 250 -> 0.0
    # 0   -> 1.0
    #
    # Está invertido porque você observou
    # que o valor diminui ao girar.

    normalized = (
        ADC_MAX - value
    ) / (
        ADC_MAX - ADC_MIN
    )

    # =================================================
    # ARCO DO PONTEIRO
    # =================================================
    #
    # Começa aproximadamente em 7h30
    # e termina aproximadamente em 4h30.
    #
    # Em coordenadas matemáticas:
    #
    # 7h30  ≈ 225 graus
    # percorre 270 graus
    #
    # =================================================

    start_angle = 225

    sweep_angle = 270

    angle = (
        start_angle
        + normalized
        * sweep_angle
    )

    return angle


# =====================================================
# DESENHAR RELÓGIO
# =====================================================

def draw_clock(
    surface,
    center,
    radius,
    angle,
    value,
    number
):

    center_x, center_y = center

    # =================================================
    # CÍRCULO
    # =================================================

    pygame.draw.circle(
        surface,
        (220, 220, 220),
        center,
        radius,
        width=3
    )

    # =================================================
    # MARCAS
    # =================================================

    for hour in range(12):

        hour_angle = (
            hour * 30
            - 90
        )

        radians = math.radians(
            hour_angle
        )

        outer_x = (
            center_x
            + math.cos(
                radians
            )
            * (
                radius - 5
            )
        )

        outer_y = (
            center_y
            + math.sin(
                radians
            )
            * (
                radius - 5
            )
        )

        inner_x = (
            center_x
            + math.cos(
                radians
            )
            * (
                radius - 12
            )
        )

        inner_y = (
            center_y
            + math.sin(
                radians
            )
            * (
                radius - 12
            )
        )

        pygame.draw.line(
            surface,
            (150, 150, 150),
            (
                inner_x,
                inner_y
            ),
            (
                outer_x,
                outer_y
            ),
            2
        )

    # =================================================
    # PONTEIRO
    # =================================================

    radians = math.radians(
        angle
    )

    pointer_length = (
        radius - 18
    )

    end_x = (
        center_x
        + math.cos(
            radians
        )
        * pointer_length
    )

    end_y = (
        center_y
        + math.sin(
            radians
        )
        * pointer_length
    )

    pygame.draw.line(
        surface,
        (255, 210, 70),
        center,
        (
            end_x,
            end_y
        ),
        5
    )

    pygame.draw.circle(
        surface,
        (255, 210, 70),
        center,
        6
    )

    # =================================================
    # TEXTO
    # =================================================

    title = font.render(
        f"POT {number}",
        True,
        (255, 255, 255)
    )

    title_rect = title.get_rect(
        center=(
            center_x,
            center_y
            + radius
            + 30
        )
    )

    surface.blit(
        title,
        title_rect
    )

    adc_text = small_font.render(
        f"ADC: {value}",
        True,
        (170, 170, 170)
    )

    adc_rect = adc_text.get_rect(
        center=(
            center_x,
            center_y
            + radius
            + 55
        )
    )

    surface.blit(
        adc_text,
        adc_rect
    )


# =====================================================
# MAIN
# =====================================================

def main():

    setup_adc()

    running = True

    while running:

        # =================================================
        # EVENTOS
        # =================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif (
                event.type
                == pygame.KEYDOWN
                and
                event.key
                == pygame.K_ESCAPE
            ):

                running = False

        # =================================================
        # LÊ POTENCIÔMETROS
        # =================================================

        values = []

        angles = []

        for channel in POT_CHANNELS:

            value = adc.analogRead(
                channel
            )

            angle = adc_to_angle(
                value
            )

            values.append(
                value
            )

            angles.append(
                angle
            )

        # =================================================
        # FUNDO
        # =================================================

        screen.fill(
            (20, 20, 20)
        )

        # =================================================
        # TÍTULO
        # =================================================

        title = font.render(
            "TESTE DOS TRES RELOGIOS",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    WIDTH // 2,
                    45
                )
            )
        )

        # =================================================
        # RELÓGIO 1
        # =================================================

        draw_clock(
            screen,
            (
                120,
                210
            ),
            75,
            angles[0],
            values[0],
            1
        )

        # =================================================
        # RELÓGIO 2
        # =================================================

        draw_clock(
            screen,
            (
                320,
                210
            ),
            75,
            angles[1],
            values[1],
            2
        )

        # =================================================
        # RELÓGIO 3
        # =================================================

        draw_clock(
            screen,
            (
                520,
                210
            ),
            75,
            angles[2],
            values[2],
            3
        )

        # =================================================
        # INSTRUÇÃO
        # =================================================

        instruction = small_font.render(
            "Gire os tres potenciometros | ESC para sair",
            True,
            (160, 160, 160)
        )

        screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    WIDTH // 2,
                    440
                )
            )
        )

        pygame.display.update()

        clock.tick(
            60
        )


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    try:

        main()

    finally:

        try:

            adc.close()

        except Exception:

            pass

        pygame.quit()