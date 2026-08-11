import math
import random
import pygame


# =====================================================
# HARDWARE
# =====================================================

try:
    from hardware.ADCDevice import ADCDevice, ADS7830

    RASPBERRY_AVAILABLE = True

except ImportError:
    RASPBERRY_AVAILABLE = False


class ClocksModule:

    def __init__(self):

        # =================================================
        # ESTADO
        # =================================================

        self.concluido = False
        self.state = "playing"

        # =================================================
        # ADC / POTENCIOMETROS
        # =================================================

        self.adc = None
        self.hardware_enabled = False

        self.adc_address = 0x48

        # Confirmado nos testes
        self.pot_channels = [
            2,
            3,
            4
        ]

        # Valores observados
        self.adc_min = 0
        self.adc_center = 130
        self.adc_max = 250

        # =================================================
        # SIMBOLOS -> HORARIOS
        # =================================================
        #
        # ESTA É A TABELA QUE O PARCEIRO CONSULTA.
        #
        # Como o potenciometro não gira 360 graus,
        # usamos somente posições alcançáveis.
        #
        # =================================================

        self.symbol_hours = {

            "circle": 9,
            "triangle": 11,
            "square": 1,
            "diamond": 3,
            "star": 12,
            "cross": 2

        }

        # =================================================
        # SORTEIA 3 SIMBOLOS DIFERENTES
        # =================================================

        self.symbols = random.sample(
            list(self.symbol_hours.keys()),
            3
        )

        self.target_hours = [

            self.symbol_hours[symbol]

            for symbol in self.symbols
        ]

        # =================================================
        # VALORES DOS POTENCIOMETROS
        # =================================================

        self.pot_values = [
            self.adc_center,
            self.adc_center,
            self.adc_center
        ]

        self.angles = [
            -90,
            -90,
            -90
        ]

        # =================================================
        # VERIFICACAO DA RESPOSTA
        # =================================================

        # O jogador precisa manter os três corretos
        # durante 1 segundo.

        self.correct_start_time = None

        self.correct_hold_time = 1000

        # Tolerância angular em graus.
        #
        # 12 posições do relógio são separadas por 30 graus.
        # Com 10 graus de tolerância ainda há boa separação.

        self.angle_tolerance = 10

        # =================================================
        # VISUAL
        # =================================================

        self.title_font = pygame.font.Font(
            None,
            42
        )

        self.info_font = pygame.font.Font(
            None,
            25
        )

        self.small_font = pygame.font.Font(
            None,
            20
        )

        self.symbol_font = pygame.font.Font(
            None,
            30
        )

        # =================================================
        # HARDWARE
        # =================================================

        self.setup_hardware()

    # =====================================================
    # HARDWARE
    # =====================================================

    def setup_hardware(self):

        if not RASPBERRY_AVAILABLE:

            print(
                "Modulo dos relogios em modo PC."
            )

            return

        try:

            test_adc = ADCDevice(
                self.adc_address
            )

            if not test_adc.detectI2C(
                self.adc_address
            ):

                print(
                    "ADS7830 nao encontrado!"
                )

                return

            self.adc = ADS7830(
                self.adc_address
            )

            self.hardware_enabled = True

            print()
            print(
                "================================"
            )
            print(
                "RELOGIOS - HARDWARE OK"
            )
            print(
                "================================"
            )
            print(
                "POT 1 -> CH2"
            )
            print(
                "POT 2 -> CH3"
            )
            print(
                "POT 3 -> CH4"
            )
            print(
                "Centro ADC -> aproximadamente 130"
            )
            print(
                "================================"
            )
            print()

        except Exception as error:

            print(
                "Erro ao inicializar ADC:"
            )

            print(
                error
            )

            self.hardware_enabled = False

    # =====================================================
    # CLAMP
    # =====================================================

    def clamp(
        self,
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
    # ADC -> ANGULO
    # =====================================================

    def adc_to_angle(
        self,
        value
    ):

        value = self.clamp(
            value,
            self.adc_min,
            self.adc_max
        )

        # 270 graus totais
        # 135 para cada lado do 12h

        half_sweep = 135

        # =================================================
        # ADC 130 -> 250
        # =================================================

        if value >= self.adc_center:

            normalized = (
                value
                - self.adc_center
            ) / (
                self.adc_max
                - self.adc_center
            )

            angle = (
                -90
                - normalized
                * half_sweep
            )

        # =================================================
        # ADC 130 -> 0
        # =================================================

        else:

            normalized = (
                self.adc_center
                - value
            ) / (
                self.adc_center
                - self.adc_min
            )

            angle = (
                -90
                + normalized
                * half_sweep
            )

        return angle

    # =====================================================
    # HORA -> ANGULO
    # =====================================================

    def hour_to_angle(
        self,
        hour
    ):

        # 12h -> -90
        # 1h  -> -60
        # 2h  -> -30
        # 3h  ->   0
        # etc.

        if hour == 12:

            return -90

        return (
            -90
            + hour * 30
        )

    # =====================================================
    # DIFERENCA ENTRE ANGULOS
    # =====================================================

    def angle_difference(
        self,
        angle1,
        angle2
    ):

        difference = (
            angle1
            - angle2
            + 180
        ) % 360 - 180

        return abs(
            difference
        )

    # =====================================================
    # LER POTENCIOMETROS
    # =====================================================

    def read_potentiometers(self):

        if not self.hardware_enabled:
            return

        try:

            for i, channel in enumerate(
                self.pot_channels
            ):

                value = self.adc.analogRead(
                    channel
                )

                self.pot_values[i] = (
                    value
                )

                self.angles[i] = (
                    self.adc_to_angle(
                        value
                    )
                )

        except Exception as error:

            print(
                "Erro ao ler potenciometros:",
                error
            )

    # =====================================================
    # VERIFICAR UM RELOGIO
    # =====================================================

    def clock_is_correct(
        self,
        index
    ):

        target_angle = (
            self.hour_to_angle(
                self.target_hours[index]
            )
        )

        difference = (
            self.angle_difference(
                self.angles[index],
                target_angle
            )
        )

        return (
            difference
            <= self.angle_tolerance
        )

    # =====================================================
    # VERIFICAR TODOS
    # =====================================================

    def check_solution(self):

        if self.concluido:
            return

        all_correct = all(

            self.clock_is_correct(i)

            for i in range(3)
        )

        # =================================================
        # TODOS CORRETOS
        # =================================================

        if all_correct:

            current_time = (
                pygame.time.get_ticks()
            )

            # Começou agora
            if (
                self.correct_start_time
                is None
            ):

                self.correct_start_time = (
                    current_time
                )

            # Já está correto há tempo suficiente
            elif (
                current_time
                - self.correct_start_time
                >= self.correct_hold_time
            ):

                self.concluido = True

                self.state = "completed"

                print()
                print(
                    "MODULO DOS RELOGIOS CONCLUIDO!"
                )
                print()

        # =================================================
        # ALGUM ESTÁ ERRADO
        # =================================================

        else:

            self.correct_start_time = None

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self):

        if self.concluido:
            return

        self.read_potentiometers()

        self.check_solution()

    # =====================================================
    # EVENTOS
    # =====================================================

    def handle_event(
        self,
        event
    ):

        # Por enquanto o módulo não precisa
        # de teclado.
        #
        # Mantemos esta função para ficar
        # compatível com a arquitetura do Maze.

        pass

    # =====================================================
    # DESENHAR SIMBOLO
    # =====================================================

    def draw_symbol(
        self,
        surface,
        symbol,
        center
    ):

        x, y = center

        color = (
            255,
            210,
            80
        )

        # =================================================
        # CIRCULO
        # =================================================

        if symbol == "circle":

            pygame.draw.circle(
                surface,
                color,
                center,
                12,
                width=3
            )

        # =================================================
        # TRIANGULO
        # =================================================

        elif symbol == "triangle":

            pygame.draw.polygon(
                surface,
                color,
                [
                    (x, y - 14),
                    (x - 14, y + 12),
                    (x + 14, y + 12)
                ],
                width=3
            )

        # =================================================
        # QUADRADO
        # =================================================

        elif symbol == "square":

            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(
                    x - 12,
                    y - 12,
                    24,
                    24
                ),
                width=3
            )

        # =================================================
        # LOSANGO
        # =================================================

        elif symbol == "diamond":

            pygame.draw.polygon(
                surface,
                color,
                [
                    (x, y - 15),
                    (x + 13, y),
                    (x, y + 15),
                    (x - 13, y)
                ],
                width=3
            )

        # =================================================
        # CRUZ
        # =================================================

        elif symbol == "cross":

            pygame.draw.line(
                surface,
                color,
                (
                    x - 11,
                    y - 11
                ),
                (
                    x + 11,
                    y + 11
                ),
                4
            )

            pygame.draw.line(
                surface,
                color,
                (
                    x + 11,
                    y - 11
                ),
                (
                    x - 11,
                    y + 11
                ),
                4
            )

        # =================================================
        # ESTRELA
        # =================================================

        elif symbol == "star":

            points = []

            for i in range(10):

                angle = (
                    math.radians(
                        -90
                        + i * 36
                    )
                )

                if i % 2 == 0:
                    radius = 15
                else:
                    radius = 7

                px = (
                    x
                    + math.cos(angle)
                    * radius
                )

                py = (
                    y
                    + math.sin(angle)
                    * radius
                )

                points.append(
                    (
                        px,
                        py
                    )
                )

            pygame.draw.polygon(
                surface,
                color,
                points,
                width=3
            )

    # =====================================================
    # DESENHAR RELOGIO
    # =====================================================

    def draw_clock(
        self,
        surface,
        center,
        radius,
        angle,
        index
    ):

        center_x, center_y = (
            center
        )

        # =================================================
        # CIRCULO
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
                + math.cos(radians)
                * (
                    radius - 5
                )
            )

            outer_y = (
                center_y
                + math.sin(radians)
                * (
                    radius - 5
                )
            )

            inner_x = (
                center_x
                + math.cos(radians)
                * (
                    radius - 12
                )
            )

            inner_y = (
                center_y
                + math.sin(radians)
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
        # NUMEROS
        # =================================================

        for hour in range(
            1,
            13
        ):

            hour_angle = (
                hour * 30
                - 90
            )

            radians = math.radians(
                hour_angle
            )

            number_radius = (
                radius - 25
            )

            number_x = (
                center_x
                + math.cos(radians)
                * number_radius
            )

            number_y = (
                center_y
                + math.sin(radians)
                * number_radius
            )

            text = (
                self.small_font.render(
                    str(hour),
                    True,
                    (175, 175, 175)
                )
            )

            surface.blit(
                text,
                text.get_rect(
                    center=(
                        number_x,
                        number_y
                    )
                )
            )

        # =================================================
        # PONTEIRO
        # =================================================

        radians = math.radians(
            angle
        )

        pointer_length = (
            radius - 32
        )

        end_x = (
            center_x
            + math.cos(radians)
            * pointer_length
        )

        end_y = (
            center_y
            + math.sin(radians)
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
        # SIMBOLO
        # =================================================

        self.draw_symbol(
            surface,
            self.symbols[index],
            (
                center_x,
                center_y
                + radius
                + 28
            )
        )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        screen
    ):

        screen.fill(
            (20, 20, 20)
        )

        # =================================================
        # TITULO
        # =================================================

        if self.concluido:

            title_text = (
                "RELOGIOS CORRETOS!"
            )

            title_color = (
                50,
                255,
                100
            )

        else:

            title_text = (
                "MODULO DOS RELOGIOS"
            )

            title_color = (
                255,
                255,
                255
            )

        title = (
            self.title_font.render(
                title_text,
                True,
                title_color
            )
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    320,
                    40
                )
            )
        )

        # =================================================
        # INSTRUCAO
        # =================================================

        instruction = (
            self.info_font.render(
                "Informe os simbolos ao seu parceiro",
                True,
                (170, 170, 170)
            )
        )

        screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    320,
                    75
                )
            )
        )

        # =================================================
        # RELOGIOS
        # =================================================

        centers = [
            (120, 215),
            (320, 215),
            (520, 215)
        ]

        for i in range(3):

            self.draw_clock(
                screen,
                centers[i],
                75,
                self.angles[i],
                i
            )

        # =================================================
        # NUMERO DO RELOGIO
        # =================================================

        for i, center in enumerate(
            centers
        ):

            text = (
                self.small_font.render(
                    f"RELOGIO {i + 1}",
                    True,
                    (160, 160, 160)
                )
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        center[0],
                        345
                    )
                )
            )

        # =================================================
        # PROGRESSO
        # =================================================

        if (
            self.correct_start_time
            is not None
            and not self.concluido
        ):

            elapsed = (
                pygame.time.get_ticks()
                - self.correct_start_time
            )

            progress = min(
                elapsed
                / self.correct_hold_time,
                1
            )

            # Fundo
            pygame.draw.rect(
                screen,
                (60, 60, 60),
                pygame.Rect(
                    170,
                    385,
                    300,
                    15
                ),
                border_radius=7
            )

            # Progresso
            pygame.draw.rect(
                screen,
                (80, 220, 100),
                pygame.Rect(
                    170,
                    385,
                    int(
                        300 * progress
                    ),
                    15
                ),
                border_radius=7
            )

            checking = (
                self.small_font.render(
                    "Mantenha os ponteiros...",
                    True,
                    (100, 220, 120)
                )
            )

            screen.blit(
                checking,
                checking.get_rect(
                    center=(
                        320,
                        420
                    )
                )
            )

        elif not self.concluido:

            instruction2 = (
                self.small_font.render(
                    "Ajuste os tres potenciometros",
                    True,
                    (150, 150, 150)
                )
            )

            screen.blit(
                instruction2,
                instruction2.get_rect(
                    center=(
                        320,
                        405
                    )
                )
            )

        # =================================================
        # CONCLUIDO
        # =================================================

        if self.concluido:

            completed = (
                self.info_font.render(
                    "MODULO CONCLUIDO",
                    True,
                    (50, 255, 100)
                )
            )

            screen.blit(
                completed,
                completed.get_rect(
                    center=(
                        320,
                        405
                    )
                )
            )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.concluido = False
        self.state = "playing"

        # Sorteia novos símbolos

        self.symbols = random.sample(
            list(
                self.symbol_hours.keys()
            ),
            3
        )

        self.target_hours = [

            self.symbol_hours[symbol]

            for symbol in self.symbols
        ]

        self.correct_start_time = None

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        try:

            if self.adc is not None:

                self.adc.close()

        except Exception:

            pass