import RPi.GPIO as GPIO
import time


BUZZER_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

pwm = GPIO.PWM(BUZZER_PIN, 2000)

try:
    print("Tocando buzzer em 2000 Hz...")
    
    pwm.start(50)

    time.sleep(5)

finally:
    pwm.stop()
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()