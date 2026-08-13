import math
import time

try:
    import RPi.GPIO as GPIO
    RASPBERRY_AVAILABLE = True
except ImportError:
    RASPBERRY_AVAILABLE = False


class GameTimer:

    def __init__(self, duration_seconds=300):

        # =====================================================
        # TEMPORIZADOR
        # =====================================================

        self.duration_seconds = duration_seconds

        self.start_time = None
        self.running = False
        self.finished = False

        self.remaining = duration_seconds

        # =====================================================
        # DISPLAY 4 DIGITOS / 74HC595
        # =====================================================
        #
        # Freenove:
        # DATA  -> GPIO22
        # LATCH -> GPIO27
        # CLOCK -> GPIO17
        #
        # Estes GPIOs sao compartilhados com a matriz 8x8.
        # Por isso, o main NAO atualiza o display durante o Maze.
        #
        # =====================================================

        self.data_pin = 22
        self.latch_pin = 27
        self.clock_pin = 17

        # Codificacao 0-9 para display common anode
        self.num = [
            0xC0,  # 0
            0xF9,  # 1
            0xA4,  # 2
            0xB0,  # 3
            0x99,  # 4
            0x92,  # 5
            0x82,  # 6
            0xF8,  # 7
            0x80,  # 8
            0x90   # 9
        ]

        # Selecao dos quatro digitos
        self.digit_bits = [
            0x01,
            0x02,
            0x04,
            0x08
        ]

        self.hardware_enabled = False

        self.setup_display()

    # =====================================================
    # DISPLAY
    # =====================================================

    def setup_display(self):

        if not RASPBERRY_AVAILABLE:
            print("GameTimer em modo PC.")
            return

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            GPIO.setup(
                self.data_pin,
                GPIO.OUT
            )

            GPIO.setup(
                self.latch_pin,
                GPIO.OUT
            )

            GPIO.setup(
                self.clock_pin,
                GPIO.OUT
            )

            GPIO.output(
                self.data_pin,
                GPIO.LOW
            )

            GPIO.output(
                self.latch_pin,
                GPIO.HIGH
            )

            GPIO.output(
                self.clock_pin,
                GPIO.LOW
            )

            self.hardware_enabled = True

            print()
            print("==============================")
            print("CRONOMETRO - DISPLAY OK")
            print("==============================")
            print("DATA  -> GPIO22")
            print("LATCH -> GPIO27")
            print("CLOCK -> GPIO17")
            print("Tempo -> 05.00")
            print("==============================")
            print()

        except Exception as error:
            print(
                "Erro ao configurar display do cronometro:",
                error
            )

            self.hardware_enabled = False

    # =====================================================
    # CONTROLE DO TEMPO
    # =====================================================

    def start(self):

        self.start_time = time.monotonic()

        self.remaining = self.duration_seconds

        self.running = True
        self.finished = False

    def reset(self):

        self.start_time = None

        self.remaining = self.duration_seconds

        self.running = False
        self.finished = False

    def stop(self):

        self.update()

        self.running = False

    def update(self):

        if not self.running:
            return

        elapsed = (
            time.monotonic()
            - self.start_time
        )

        self.remaining = max(
            0,
            int(
                math.ceil(
                    self.duration_seconds
                    - elapsed
                )
            )
        )

        if self.remaining <= 0:
            self.remaining = 0
            self.running = False
            self.finished = True

    def is_expired(self):

        return self.finished

    # =====================================================
    # TEXTO DO TEMPO
    # =====================================================

    def get_minutes_seconds(self):

        minutes = (
            self.remaining // 60
        )

        seconds = (
            self.remaining % 60
        )

        return (
            minutes,
            seconds
        )

    def get_text(self):

        minutes, seconds = (
            self.get_minutes_seconds()
        )

        return (
            f"{minutes:02d}:{seconds:02d}"
        )

    # =====================================================
    # 74HC595
    # =====================================================

    def shift_out(self, value):

        for i in range(8):

            GPIO.output(
                self.clock_pin,
                GPIO.LOW
            )

            bit = (
                0x80
                & (value << i)
            )

            GPIO.output(
                self.data_pin,
                GPIO.HIGH
                if bit
                else GPIO.LOW
            )

            GPIO.output(
                self.clock_pin,
                GPIO.HIGH
            )

    def write_digit(
        self,
        digit_index,
        number,
        decimal_point=False
    ):

        segment_value = (
            self.num[number]
        )

        # No display common-anode o ponto decimal
        # acende quando o bit mais alto fica em 0.
        if decimal_point:
            segment_value &= 0x7F

        GPIO.output(
            self.latch_pin,
            GPIO.LOW
        )

        self.shift_out(
            self.digit_bits[
                digit_index
            ]
        )

        self.shift_out(
            segment_value
        )

        GPIO.output(
            self.latch_pin,
            GPIO.HIGH
        )

        # Pequeno tempo para multiplexacao
        time.sleep(
            0.00035
        )

        # Apaga o digito antes de passar para o proximo
        GPIO.output(
            self.latch_pin,
            GPIO.LOW
        )

        self.shift_out(
            self.digit_bits[
                digit_index
            ]
        )

        self.shift_out(
            0xFF
        )

        GPIO.output(
            self.latch_pin,
            GPIO.HIGH
        )

    # =====================================================
    # MOSTRAR MM.SS
    # =====================================================

    def refresh_display(self):

        if not self.hardware_enabled:
            return

        minutes, seconds = (
            self.get_minutes_seconds()
        )

        # Como sao apenas 5 minutos,
        # quatro digitos sao suficientes:
        #
        # 05.00
        # 04.59
        # ...
        # 00.00

        digits = [
            (minutes // 10) % 10,
            minutes % 10,
            (seconds // 10) % 10,
            seconds % 10
        ]

        # Repete algumas varreduras por frame
        # para aumentar o brilho.
        for _ in range(3):

            for index in range(4):

                self.write_digit(
                    index,
                    digits[index],
                    decimal_point=(
                        index == 1
                    )
                )

    # =====================================================
    # APAGAR DISPLAY
    # =====================================================

    def clear_display(self):

        if not self.hardware_enabled:
            return

        try:
            GPIO.output(
                self.latch_pin,
                GPIO.LOW
            )

            self.shift_out(
                0x00
            )

            self.shift_out(
                0xFF
            )

            GPIO.output(
                self.latch_pin,
                GPIO.HIGH
            )

        except Exception:
            pass

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        # Nao fazemos GPIO.cleanup() aqui porque os mesmos
        # GPIOs tambem sao usados por outros modulos.
        self.clear_display()