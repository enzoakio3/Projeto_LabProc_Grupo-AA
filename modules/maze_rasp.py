import pygame
import random


# =====================================================
# HARDWARE
# =====================================================

try:
    import RPi.GPIO as GPIO
    from hardware.ADCDevice import ADCDevice, ADS7830

    RASPBERRY_AVAILABLE = True

except ImportError:
    RASPBERRY_AVAILABLE = False


class MazeModule:

    def __init__(self):

        # =====================================================
        # ESTADO
        # =====================================================

        self.concluido = False
        self.state = "playing"

        # =====================================================
        # LABIRINTOS
        # =====================================================
        #
        # 0 = caminho
        # 1 = parede
        #
        # =====================================================

        self.mazes = [

            {
                "symbols": ("circle", "triangle"),
                "map": [
                    [0, 0, 0, 1, 0, 0, 0, 0],
                    [1, 1, 0, 1, 0, 1, 1, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0],
                    [0, 1, 1, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 1, 1, 1, 1, 0, 0, 0]
                ]
            },

            {
                "symbols": ("square", "circle"),
                "map": [
                    [0, 0, 0, 0, 0, 1, 0, 0],
                    [1, 1, 1, 1, 0, 1, 0, 1],
                    [0, 0, 0, 0, 0, 1, 0, 0],
                    [0, 1, 1, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 1, 1, 1, 0]
                ]
            },

            {
                "symbols": ("triangle", "square"),
                "map": [
                    [0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 1, 0, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [1, 1, 1, 1, 1, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 1, 1, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 0]
                ]
            },

            {
                "symbols": ("circle", "diamond"),
                "map": [
                    [0, 0, 0, 0, 1, 0, 0, 0],
                    [1, 1, 1, 0, 1, 0, 1, 0],
                    [0, 0, 0, 0, 1, 0, 1, 0],
                    [0, 1, 1, 1, 1, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [1, 1, 1, 1, 1, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 1, 1, 1, 1, 1, 1, 0]
                ]
            }
        ]

        self.maze_index = random.randint(
            0,
            len(self.mazes) - 1
        )

        self.load_maze()

        # =====================================================
        # POSIÇÕES
        # =====================================================

        self.start_row = 0
        self.start_col = 0

        self.player_row = self.start_row
        self.player_col = self.start_col

        self.goal_row = 7
        self.goal_col = 7

        # =====================================================
        # CAMINHO PERCORRIDO
        # =====================================================

        self.visited = [
            [False for _ in range(8)]
            for _ in range(8)
        ]

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        # =====================================================
        # JOYSTICK
        # =====================================================

        self.adc = None

        self.joystick_x_channel = 5
        self.joystick_y_channel = 6

        # ADS7830 -> 0 a 255
        self.joystick_low = 70
        self.joystick_high = 185

        # Só permite um movimento por inclinação
        self.joystick_ready = True

        # =====================================================
        # LED MATRIX
        # =====================================================
        #
        # Freenove:
        # DATA  = GPIO22
        # LATCH = GPIO27
        # CLOCK = GPIO17
        #
        # =====================================================

        self.matrix_data_pin = 22
        self.matrix_latch_pin = 27
        self.matrix_clock_pin = 17

        self.matrix_scan_column = 0

        # =====================================================
        # BUZZER
        # =====================================================

        self.buzzer_pin = 4
        self.buzzer_pwm = None

        self.error_start_time = 0
        self.error_duration = 700

        # =====================================================
        # HARDWARE
        # =====================================================

        self.hardware_enabled = False

        self.setup_hardware()

        # =====================================================
        # VISUAL PYGAME
        # =====================================================

        self.cell_size = 36

        self.grid_size = (
            8 * self.cell_size
        )

        self.offset_x = (
            640 - self.grid_size
        ) // 2

        self.offset_y = 145

        self.title_font = pygame.font.Font(
            None,
            40
        )

        self.info_font = pygame.font.Font(
            None,
            24
        )

        self.coord_font = pygame.font.Font(
            None,
            22
        )

    # =====================================================
    # CARREGAR LABIRINTO
    # =====================================================

    def load_maze(self):

        maze_data = self.mazes[
            self.maze_index
        ]

        self.maze = maze_data[
            "map"
        ]

        self.symbols = maze_data[
            "symbols"
        ]

    # =====================================================
    # HARDWARE
    # =====================================================

    def setup_hardware(self):

        if not RASPBERRY_AVAILABLE:

            print(
                "Maze em modo PC."
            )

            return

        try:

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            # ---------------------------------------------
            # MATRIZ
            # ---------------------------------------------

            GPIO.setup(
                self.matrix_data_pin,
                GPIO.OUT
            )

            GPIO.setup(
                self.matrix_latch_pin,
                GPIO.OUT
            )

            GPIO.setup(
                self.matrix_clock_pin,
                GPIO.OUT
            )

            # ---------------------------------------------
            # BUZZER
            # ---------------------------------------------

            GPIO.setup(
                self.buzzer_pin,
                GPIO.OUT
            )

            self.buzzer_pwm = GPIO.PWM(
                self.buzzer_pin,
                1500
            )

            self.buzzer_pwm.start(
                0
            )

            # ---------------------------------------------
            # ADC / JOYSTICK
            # ---------------------------------------------

            test_adc = ADCDevice(
                0x48
            )

            if test_adc.detectI2C(
                0x48
            ):

                self.adc = ADS7830(
                    0x48
                )

                print(
                    "ADS7830 encontrado em 0x48."
                )

            else:

                print(
                    "ADS7830 nao encontrado."
                )

                return

            self.hardware_enabled = True

            print()
            print(
                "Hardware do labirinto OK!"
            )

            print(
                "Joystick X -> canal 5"
            )

            print(
                "Joystick Y -> canal 6"
            )

            print(
                "Matrix DATA -> GPIO22"
            )

            print(
                "Matrix LATCH -> GPIO27"
            )

            print(
                "Matrix CLOCK -> GPIO17"
            )

            print()

        except Exception as error:

            print(
                "Erro no hardware do maze:"
            )

            print(
                error
            )

            self.hardware_enabled = False

    # =====================================================
    # SHIFT OUT
    # =====================================================

    def shift_out(
        self,
        value
    ):

        for bit in range(8):

            GPIO.output(
                self.matrix_clock_pin,
                GPIO.LOW
            )

            mask = (
                0x80 >> bit
            )

            GPIO.output(
                self.matrix_data_pin,
                GPIO.HIGH
                if value & mask
                else GPIO.LOW
            )

            GPIO.output(
                self.matrix_clock_pin,
                GPIO.HIGH
            )

    # =====================================================
    # MATRIZ LED
    # =====================================================

    def update_led_matrix(self):

        if not self.hardware_enabled:

            return

        col = self.matrix_scan_column

        row_data = 0

        # Monta os bits da coluna atual
        for row in range(8):

            if self.visited[
                row
            ][
                col
            ]:

                row_data |= (
                    1 << row
                )

        column_mask = (
            0x80 >> col
        )

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.LOW
        )

        self.shift_out(
            row_data
        )

        # seleção de coluna ativa em LOW
        self.shift_out(
            (~column_mask) & 0xFF
        )

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.HIGH
        )

        self.matrix_scan_column += 1

        if (
            self.matrix_scan_column
            >= 8
        ):

            self.matrix_scan_column = 0

    # =====================================================
    # JOYSTICK
    # =====================================================

    def read_joystick(self):

        if not self.hardware_enabled:

            return None

        try:

            x = self.adc.analogRead(
                self.joystick_x_channel
            )

            y = self.adc.analogRead(
                self.joystick_y_channel
            )

        except Exception as error:

            print(
                "Erro joystick:",
                error
            )

            return None

        # DEBUG
        # pode remover depois
        # print("X:", x, "Y:", y)

        # ---------------------------------------------
        # CENTRO
        # ---------------------------------------------

        centered = (
            self.joystick_low <= x <= self.joystick_high
            and
            self.joystick_low <= y <= self.joystick_high
        )

        if centered:

            self.joystick_ready = True

            return None

        # Já moveu nessa inclinação
        if not self.joystick_ready:

            return None

        # ---------------------------------------------
        # HORIZONTAL
        # ---------------------------------------------

        if (
            x < self.joystick_low
        ):

            self.joystick_ready = False

            return "LEFT"

        if (
            x > self.joystick_high
        ):

            self.joystick_ready = False

            return "RIGHT"

        # ---------------------------------------------
        # VERTICAL
        # ---------------------------------------------

        if (
            y < self.joystick_low
        ):

            self.joystick_ready = False

            return "UP"

        if (
            y > self.joystick_high
        ):

            self.joystick_ready = False

            return "DOWN"

        return None

    # =====================================================
    # DIREÇÃO
    # =====================================================

    def process_direction(
        self,
        direction
    ):

        print(
            "Direcao:",
            direction
        )

        if direction == "UP":

            self.try_move(
                -1,
                0
            )

        elif direction == "DOWN":

            self.try_move(
                1,
                0
            )

        elif direction == "LEFT":

            self.try_move(
                0,
                -1
            )

        elif direction == "RIGHT":

            self.try_move(
                0,
                1
            )

    # =====================================================
    # MOVIMENTO
    # =====================================================

    def try_move(
        self,
        row_change,
        col_change
    ):

        new_row = (
            self.player_row
            + row_change
        )

        new_col = (
            self.player_col
            + col_change
        )

        # ---------------------------------------------
        # FORA DO MAPA
        # ---------------------------------------------

        if (
            new_row < 0
            or new_row >= 8
            or new_col < 0
            or new_col >= 8
        ):

            self.trigger_error()

            return

        # ---------------------------------------------
        # PAREDE
        # ---------------------------------------------

        if self.maze[
            new_row
        ][
            new_col
        ] == 1:

            self.trigger_error()

            return

        # ---------------------------------------------
        # MOVIMENTO VÁLIDO
        # ---------------------------------------------

        self.player_row = new_row
        self.player_col = new_col

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        print(
            "Posicao:",
            self.get_coordinate(
                self.player_row,
                self.player_col
            )
        )

        # ---------------------------------------------
        # OBJETIVO
        # ---------------------------------------------

        if (
            self.player_row
            == self.goal_row
            and
            self.player_col
            == self.goal_col
        ):

            self.concluido = True
            self.state = "completed"

            print(
                "Labirinto concluido!"
            )

    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        if self.state == "error":

            return

        print(
            "Parede!"
        )

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        if (
            self.hardware_enabled
            and self.buzzer_pwm
            is not None
        ):

            self.buzzer_pwm.ChangeFrequency(
                700
            )

            self.buzzer_pwm.ChangeDutyCycle(
                50
            )

    # =====================================================
    # BUZZER
    # =====================================================

    def stop_buzzer(self):

        if (
            self.hardware_enabled
            and self.buzzer_pwm
            is not None
        ):

            try:

                self.buzzer_pwm.ChangeDutyCycle(
                    0
                )

            except Exception:

                pass

    # =====================================================
    # COORDENADA
    # =====================================================

    def get_coordinate(
        self,
        row,
        col
    ):

        letter = chr(
            ord("A") + row
        )

        return (
            f"{letter}{col + 1}"
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        event
    ):

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # REFRESH MATRIZ
        # =================================================

        if self.hardware_enabled:

            # várias varreduras por frame
            for _ in range(16):

                self.update_led_matrix()

        # =================================================
        # COMPLETOU
        # =================================================

        if self.concluido:

            return

        # =================================================
        # ERRO
        # =================================================

        if self.state == "error":

            if (
                current_time
                - self.error_start_time
                >= self.error_duration
            ):

                self.stop_buzzer()

                self.state = "playing"

                # precisa voltar ao centro
                self.joystick_ready = False

            return

        # =================================================
        # JOYSTICK
        # =================================================

        direction = (
            self.read_joystick()
        )

        if direction is not None:

            self.process_direction(
                direction
            )

            return

        # =================================================
        # TECLADO
        # =================================================

        if event.type == pygame.KEYDOWN:

            if (
                event.key == pygame.K_w
                or event.key == pygame.K_UP
            ):

                self.process_direction(
                    "UP"
                )

            elif (
                event.key == pygame.K_s
                or event.key == pygame.K_DOWN
            ):

                self.process_direction(
                    "DOWN"
                )

            elif (
                event.key == pygame.K_a
                or event.key == pygame.K_LEFT
            ):

                self.process_direction(
                    "LEFT"
                )

            elif (
                event.key == pygame.K_d
                or event.key == pygame.K_RIGHT
            ):

                self.process_direction(
                    "RIGHT"
                )

    # =====================================================
    # DESENHAR SÍMBOLO
    # =====================================================

    def draw_symbol(
        self,
        screen,
        symbol,
        center
    ):

        x, y = center

        color = (
            255,
            210,
            80
        )

        if symbol == "circle":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                12,
                width=3
            )

        elif symbol == "triangle":

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y - 14),
                    (x - 14, y + 12),
                    (x + 14, y + 12)
                ],
                width=3
            )

        elif symbol == "square":

            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    x - 12,
                    y - 12,
                    24,
                    24
                ),
                width=3
            )

        elif symbol == "diamond":

            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y - 14),
                    (x + 14, y),
                    (x, y + 14),
                    (x - 14, y)
                ],
                width=3
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
        # TÍTULO
        # =================================================

        if self.concluido:

            title_text = (
                "LABIRINTO CONCLUIDO!"
            )

            title_color = (
                50,
                255,
                100
            )

        elif self.state == "error":

            title_text = (
                "PAREDE!"
            )

            title_color = (
                255,
                70,
                70
            )

        else:

            title_text = (
                "MODULO LABIRINTO"
            )

            title_color = (
                255,
                255,
                255
            )

        title = self.title_font.render(
            title_text,
            True,
            title_color
        )

        screen.blit(
            title,
            title.get_rect(
                center=(320, 30)
            )
        )

        # =================================================
        # MAPA
        # =================================================

        map_text = self.info_font.render(
            "MAPA:",
            True,
            (180, 180, 180)
        )

        screen.blit(
            map_text,
            (235, 62)
        )

        self.draw_symbol(
            screen,
            self.symbols[0],
            (320, 70)
        )

        self.draw_symbol(
            screen,
            self.symbols[1],
            (370, 70)
        )

        # =================================================
        # POSIÇÃO / DESTINO
        # =================================================

        position = self.get_coordinate(
            self.player_row,
            self.player_col
        )

        destination = self.get_coordinate(
            self.goal_row,
            self.goal_col
        )

        position_text = self.info_font.render(
            f"POSICAO: {position}",
            True,
            (255, 210, 80)
        )

        destination_text = self.info_font.render(
            f"DESTINO: {destination}",
            True,
            (80, 220, 100)
        )

        screen.blit(
            position_text,
            (145, 105)
        )

        screen.blit(
            destination_text,
            (355, 105)
        )

        # =================================================
        # COORDENADAS
        # =================================================

        for col in range(8):

            text = self.coord_font.render(
                str(col + 1),
                True,
                (150, 150, 150)
            )

            x = (
                self.offset_x
                + col * self.cell_size
                + self.cell_size // 2
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        x,
                        self.offset_y - 12
                    )
                )
            )

        for row in range(8):

            text = self.coord_font.render(
                chr(
                    ord("A") + row
                ),
                True,
                (150, 150, 150)
            )

            y = (
                self.offset_y
                + row * self.cell_size
                + self.cell_size // 2
            )

            screen.blit(
                text,
                text.get_rect(
                    center=(
                        self.offset_x - 15,
                        y
                    )
                )
            )

        # =================================================
        # GRADE
        # =================================================

        for row in range(8):

            for col in range(8):

                x = (
                    self.offset_x
                    + col * self.cell_size
                )

                y = (
                    self.offset_y
                    + row * self.cell_size
                )

                cell = pygame.Rect(
                    x,
                    y,
                    self.cell_size,
                    self.cell_size
                )

                pygame.draw.rect(
                    screen,
                    (35, 35, 35),
                    cell
                )

                pygame.draw.rect(
                    screen,
                    (80, 80, 80),
                    cell,
                    width=1
                )

                if self.visited[
                    row
                ][
                    col
                ]:

                    pygame.draw.circle(
                        screen,
                        (80, 120, 170),
                        cell.center,
                        5
                    )

        # =================================================
        # DESTINO
        # =================================================

        goal_x = (
            self.offset_x
            + self.goal_col
            * self.cell_size
        )

        goal_y = (
            self.offset_y
            + self.goal_row
            * self.cell_size
        )

        pygame.draw.rect(
            screen,
            (50, 220, 80),
            pygame.Rect(
                goal_x + 8,
                goal_y + 8,
                self.cell_size - 16,
                self.cell_size - 16
            ),
            border_radius=5
        )

        # =================================================
        # JOGADOR
        # =================================================

        player_x = (
            self.offset_x
            + self.player_col
            * self.cell_size
            + self.cell_size // 2
        )

        player_y = (
            self.offset_y
            + self.player_row
            * self.cell_size
            + self.cell_size // 2
        )

        pygame.draw.circle(
            screen,
            (255, 210, 60),
            (
                player_x,
                player_y
            ),
            10
        )

        # =================================================
        # INSTRUÇÃO
        # =================================================

        if self.hardware_enabled:

            info = (
                "Joystick para mover | Matriz = caminho"
            )

        else:

            info = (
                "WASD / setas para mover"
            )

        text = self.info_font.render(
            info,
            True,
            (150, 150, 150)
        )

        screen.blit(
            text,
            text.get_rect(
                center=(320, 455)
            )
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.stop_buzzer()

        self.concluido = False
        self.state = "playing"

        self.maze_index = random.randint(
            0,
            len(self.mazes) - 1
        )

        self.load_maze()

        self.player_row = self.start_row
        self.player_col = self.start_col

        self.visited = [
            [False for _ in range(8)]
            for _ in range(8)
        ]

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        self.joystick_ready = False

    # =====================================================
    # LIMPAR MATRIZ
    # =====================================================

    def clear_led_matrix(self):

        if not self.hardware_enabled:

            return

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.LOW
        )

        self.shift_out(
            0x00
        )

        self.shift_out(
            0xFF
        )

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.HIGH
        )

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        self.stop_buzzer()

        if not self.hardware_enabled:

            return

        try:

            self.clear_led_matrix()

            if self.adc is not None:

                self.adc.close()

            if self.buzzer_pwm is not None:

                self.buzzer_pwm.stop()

            GPIO.cleanup()

        except Exception:

            pass