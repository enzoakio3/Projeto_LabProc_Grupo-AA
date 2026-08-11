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

pwm = GPIO.PWM(
    BUZZER_PIN,
    2000
)

# Começa com duty cycle alto
pwm.start(80)


try:

    frequencies = [
        1000,
        1500,
        1800,
        2000,
        2200,
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

        pwm.ChangeDutyCycle(
            80
        )

        time.sleep(1.2)

        # pausa
        pwm.ChangeDutyCycle(
            0
        )

        time.sleep(0.4)


finally:

    pwm.stop()

    GPIO.output(
        BUZZER_PIN,
        GPIO.LOW
    )

    GPIO.cleanup()