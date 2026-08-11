import RPi.GPIO as GPIO
import time

BUZZER_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    while True:
        print("GPIO4 HIGH")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(1)

        print("GPIO4 LOW")
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(1)

finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()