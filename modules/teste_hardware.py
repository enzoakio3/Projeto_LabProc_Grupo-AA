import RPi.GPIO as GPIO
import time


# =====================================================
# PINOS - BCM
# =====================================================

BUZZER_PIN = 4

RED_BUTTON = 16
BLUE_BUTTON = 20
GREEN_BUTTON = 21
YELLOW_BUTTON = 26


# =====================================================
# CONFIGURAÇÃO
# =====================================================

GPIO.setmode(GPIO.BCM)

GPIO.setup(
    BUZZER_PIN,
    GPIO.OUT
)

GPIO.setup(
    RED_BUTTON,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)

GPIO.setup(
    BLUE_BUTTON,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)

GPIO.setup(
    GREEN_BUTTON,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)

GPIO.setup(
    YELLOW_BUTTON,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)


# =====================================================
# PWM DO BUZZER
# =====================================================

buzzer = GPIO.PWM(
    BUZZER_PIN,
    1000
)

buzzer.start(0)


# =====================================================
# TOCAR TOM
# =====================================================

def play_tone(
    frequency,
    duration=0.2
):

    buzzer.ChangeFrequency(
        frequency
    )

    buzzer.ChangeDutyCycle(
        50
    )

    time.sleep(
        duration
    )

    buzzer.ChangeDutyCycle(
        0
    )


# =====================================================
# LOOP
# =====================================================

print(
    "Teste iniciado."
)

print(
    "Pressione os botoes coloridos."
)

try:

    while True:

        # -------------------------
        # VERMELHO
        # -------------------------

        if GPIO.input(
            RED_BUTTON
        ) == GPIO.LOW:

            print(
                "VERMELHO - GPIO16"
            )

            play_tone(
                1000
            )

            while GPIO.input(
                RED_BUTTON
            ) == GPIO.LOW:

                time.sleep(
                    0.01
                )

        # -------------------------
        # AZUL
        # -------------------------

        if GPIO.input(
            BLUE_BUTTON
        ) == GPIO.LOW:

            print(
                "AZUL - GPIO20"
            )

            play_tone(
                1300
            )

            while GPIO.input(
                BLUE_BUTTON
            ) == GPIO.LOW:

                time.sleep(
                    0.01
                )

        # -------------------------
        # VERDE
        # -------------------------

        if GPIO.input(
            GREEN_BUTTON
        ) == GPIO.LOW:

            print(
                "VERDE - GPIO21"
            )

            play_tone(
                1600
            )

            while GPIO.input(
                GREEN_BUTTON
            ) == GPIO.LOW:

                time.sleep(
                    0.01
                )

        # -------------------------
        # AMARELO
        # -------------------------

        if GPIO.input(
            YELLOW_BUTTON
        ) == GPIO.LOW:

            print(
                "AMARELO - GPIO26"
            )

            play_tone(
                2000
            )

            while GPIO.input(
                YELLOW_BUTTON
            ) == GPIO.LOW:

                time.sleep(
                    0.01
                )

        time.sleep(
            0.01
        )


except KeyboardInterrupt:

    print(
        "Encerrando..."
    )


finally:

    buzzer.stop()

    GPIO.cleanup()