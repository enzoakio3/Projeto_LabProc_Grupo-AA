import RPi.GPIO as GPIO
import time


BUZZER_PIN = 4


# =====================================================
# CONFIGURAÇÃO
# =====================================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)


# =====================================================
# PWM
# =====================================================

# Começa em 1000 Hz
pwm = GPIO.PWM(
    BUZZER_PIN,
    1000
)

# Duty cycle 50%
pwm.start(50)


try:

    # Testa várias frequências para descobrir
    # em qual faixa o buzzer responde melhor.

    frequencies = [
        200,
        400,
        700,
        1000,
        1500,
        2000,
        2500,
        3000
    ]

    for frequency in frequencies:

        print(
            f"Testando {frequency} Hz"
        )

        pwm.ChangeFrequency(
            frequency
        )

        # deixa tocar por 1 segundo
        time.sleep(1)

        # pausa
        pwm.ChangeDutyCycle(0)
        time.sleep(0.3)

        # volta a gerar onda quadrada
        pwm.ChangeDutyCycle(50)


finally:

    pwm.stop()

    GPIO.output(
        BUZZER_PIN,
        GPIO.LOW
    )

    GPIO.cleanup()