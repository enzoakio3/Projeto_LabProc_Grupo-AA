import time
from ADCDevice import *


adc = ADCDevice(0x48)


def setup():

    global adc

    if adc.detectI2C(0x48):

        adc = ADS7830(0x48)

        print("ADS7830 encontrado!")

    else:

        print("ADS7830 nao encontrado!")
        print("Execute: i2cdetect -y 1")

        exit()


def loop():

    while True:

        x = adc.analogRead(5)
        y = adc.analogRead(6)

        print(
            f"X = {x:3d} | Y = {y:3d}"
        )

        time.sleep(0.1)


def destroy():

    adc.close()


if __name__ == "__main__":

    try:

        setup()
        loop()

    except KeyboardInterrupt:

        destroy()