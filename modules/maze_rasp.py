import pygame
import random
import time


# =====================================================
# HARDWARE DA RASPBERRY
# =====================================================

try:
    import RPi.GPIO as GPIO

    from hardware.ADCDevice import (
        ADCDevice,
        ADS7830
    )

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

            # =================================================
            # MAPA 1
            # CIRCULO + TRIANGULO
            # =================================================

            {
                "symbols": (
                    "circle",
                    "triangle"
                ),

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

            # =================================================
            # MAPA 2
            # QUADRADO + CIRCULO
            # =================================================

            {
                "symbols": (
                    "square",
                    "circle"
                ),

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

            # =================================================
            # MAPA 3
            # TRIANGULO + QUADRADO
            # =================================================

            {
                "symbols": (
                    "triangle",
                    "square"
                ),

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

            # =================================================
            # MAPA 4
            # CIRCULO + LOSANGO
            # =================================================

            {
                "symbols": (
                    "circle",
                    "diamond"
                ),

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

        # =====================================================
        # ESCOLHE MAPA
        # =====================================================

        self.maze_index = random.randint(
            0,
            len(self.mazes) - 1
        )

        self.load_maze()

        # =====================================================
        # POSIÇÃO INICIAL
        # =====================================================

        self.start_row = 0
        self.start_col = 0

        self.player_row = (
            self.start_row
        )

        self.player_col = (
            self.start_col
        )

        # =====================================================
        # DESTINO
        # =====================================================

        self.goal_row = 7
        self.goal_col = 7

        # =====================================================
        # CAMINHO PERCORRIDO
        # =====================================================

        self.visited = [
            [
                False
                for _ in range(8)
            ]
            for _ in range(8)
        ]

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        # =====================================================
        # HARDWARE
        # =====================================================

        self.hardware_enabled = False

        # =====================================================
        # JOYSTICK
        # =====================================================

        self.adc = None

        self.joystick_x_channel = 5
        self.joystick_y_channel = 6

        # Valores encontrados no teste
        self.joystick_low = 70
        self.joystick_high = 185

        # Impede vários movimentos enquanto
        # o joystick continua inclinado
        self.joystick_ready = False

        # =====================================================
        # MATRIZ LED
        # =====================================================

        self.matrix_data_pin = 22
        self.matrix_latch_pin = 27
        self.matrix_clock_pin = 17

        # =====================================================
        # ERRO
        # =====================================================

        self.error_start_time = 0

        self.error_duration = 600

        # =====================================================
        # CONFIGURA HARDWARE
        # =====================================================

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

        # =====================================================
        # FONTES
        # =====================================================

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
    # CONFIGURAR HARDWARE
    # =====================================================

    def setup_hardware(self):

        if not RASPBERRY_AVAILABLE:

            print(
                "Labirinto em modo PC."
            )

            return

        try:

            GPIO.setwarnings(
                False
            )

            GPIO.setmode(
                GPIO.BCM
            )

            # =================================================
            # MATRIZ
            # =================================================

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

            GPIO.output(
                self.matrix_data_pin,
                GPIO.LOW
            )

            GPIO.output(
                self.matrix_latch_pin,
                GPIO.LOW
            )

            GPIO.output(
                self.matrix_clock_pin,
                GPIO.LOW
            )

            # =================================================
            # JOYSTICK
            # =================================================

            test_adc = ADCDevice(
                0x48
            )

            if not test_adc.detectI2C(
                0x48
            ):

                print(
                    "ADS7830 nao encontrado."
                )

                return

            self.adc = ADS7830(
                0x48
            )

            # =================================================
            # SUCESSO
            # =================================================

            self.hardware_enabled = True

            print()
            print(
                "=============================="
            )
            print(
                "HARDWARE DO LABIRINTO OK"
            )
            print(
                "=============================="
            )

            print(
                "Joystick X -> canal 5"
            )

            print(
                "Joystick Y -> canal 6"
            )

            print(
                "Matrix DATA  -> GPIO22"
            )

            print(
                "Matrix LATCH -> GPIO27"
            )

            print(
                "Matrix CLOCK -> GPIO17"
            )

            print(
                "=============================="
            )
            print()

        except Exception as error:

            print(
                "Erro no hardware do labirinto:"
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

            if value & mask:

                GPIO.output(
                    self.matrix_data_pin,
                    GPIO.HIGH
                )

            else:

                GPIO.output(
                    self.matrix_data_pin,
                    GPIO.LOW
                )

            GPIO.output(
                self.matrix_clock_pin,
                GPIO.HIGH
            )


    # =====================================================
    # MOSTRAR UMA COLUNA DA MATRIZ
    # =====================================================

    def display_matrix_column(
        self,
        column,
        row_data
    ):

        column_mask = (
            0x80 >> column
        )

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.LOW
        )

        # Linhas
        self.shift_out(
            row_data
        )

        # Coluna ativa LOW
        self.shift_out(
            (~column_mask) & 0xFF
        )

        GPIO.output(
            self.matrix_latch_pin,
            GPIO.HIGH
        )


    # =====================================================
    # REFRESH DA MATRIZ
    # =====================================================

    def refresh_led_matrix(self):

        if not self.hardware_enabled:

            return

        # Faz uma varredura completa das 8 colunas

        for column in range(8):

            row_data = 0

            for row in range(8):

                if self.visited[
                    row
                ][
                    column
                ]:

                    row_data |= (
                        1 << row
                    )

            self.display_matrix_column(
                column,
                row_data
            )

            # Pequeno tempo para LED ficar visível
            time.sleep(
                0.001
            )


    # =====================================================
    # APAGAR MATRIZ
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
    # LER JOYSTICK
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
                "Erro ao ler joystick:",
                error
            )

            return None

        # =================================================
        # JOYSTICK CENTRALIZADO
        # =================================================

        centered = (
            self.joystick_low
            <= x
            <= self.joystick_high
            and
            self.joystick_low
            <= y
            <= self.joystick_high
        )

        if centered:

            self.joystick_ready = True

            return None

        # Já realizou movimento nessa inclinada
        if not self.joystick_ready:

            return None

        # =================================================
        # DIREÇÕES
        # =================================================
        #
        # ORIENTAÇÃO CONFIRMADA NO TESTE:
        #
        # X baixo -> DIREITA
        # X alto  -> ESQUERDA
        #
        # Y baixo -> BAIXO
        # Y alto  -> CIMA
        #
        # =================================================

        if x < self.joystick_low:

            self.joystick_ready = False

            return "RIGHT"

        if x > self.joystick_high:

            self.joystick_ready = False

            return "LEFT"

        if y < self.joystick_low:

            self.joystick_ready = False

            return "DOWN"

        if y > self.joystick_high:

            self.joystick_ready = False

            return "UP"

        return None


    # =====================================================
    # PROCESSAR DIREÇÃO
    # =====================================================

    def process_direction(
        self,
        direction
    ):

        print(
            "Joystick:",
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
    # TENTAR MOVIMENTO
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

        # =================================================
        # FORA DO MAPA
        # =================================================

        if (
            new_row < 0
            or new_row >= 8
            or new_col < 0
            or new_col >= 8
        ):

            self.trigger_error()

            return

        # =================================================
        # PAREDE
        # =================================================

        if self.maze[
            new_row
        ][
            new_col
        ] == 1:

            self.trigger_error()

            return

        # =================================================
        # MOVIMENTO VÁLIDO
        # =================================================

        self.player_row = (
            new_row
        )

        self.player_col = (
            new_col
        )

        # =================================================
        # MARCA MATRIZ
        # =================================================

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

        # =================================================
        # DESTINO
        # =================================================

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
                "LABIRINTO CONCLUIDO!"
            )


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        if self.state == "error":

            return

        print(
            "PAREDE!"
        )

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        # Exige que o joystick seja centralizado
        # antes de aceitar outro movimento

        self.joystick_ready = False


    # =====================================================
    # HANDLE EVENT
    # =====================================================
    #
    # SOMENTE eventos do Pygame:
    # teclado.
    #
    # =====================================================

    def handle_event(
        self,
        event
    ):

        if self.concluido:

            return

        if self.state != "playing":

            return

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
    # UPDATE
    # =====================================================
    #
    # IMPORTANTE:
    #
    # ESTA FUNÇÃO PRECISA SER CHAMADA TODO FRAME.
    #
    # =====================================================

    def update(self):

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # MATRIZ
        # =================================================

        self.refresh_led_matrix()

        # =================================================
        # CONCLUÍDO
        # =================================================

        if self.concluido:

            return

        # =================================================
        # ERRO
        # =================================================

        if self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            if elapsed >= self.error_duration:

                self.state = "playing"

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

        number = (
            col + 1
        )

        return (
            f"{letter}{number}"
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

        # CÍRCULO
        if symbol == "circle":

            pygame.draw.circle(
                screen,
                color,
                (x, y),
                12,
                width=3
            )

        # TRIÂNGULO
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

        # QUADRADO
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

        # LOSANGO
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
                center=(
                    320,
                    30
                )
            )
        )

        # =================================================
        # IDENTIFICADORES
        # =================================================

        identifier = (
            self.info_font.render(
                "MAPA:",
                True,
                (180, 180, 180)
            )
        )

        screen.blit(
            identifier,
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

        position = (
            self.get_coordinate(
                self.player_row,
                self.player_col
            )
        )

        destination = (
            self.get_coordinate(
                self.goal_row,
                self.goal_col
            )
        )

        position_text = (
            self.info_font.render(
                f"POSICAO: {position}",
                True,
                (255, 210, 80)
            )
        )

        destination_text = (
            self.info_font.render(
                f"DESTINO: {destination}",
                True,
                (80, 220, 100)
            )
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
        # NÚMEROS
        # =================================================

        for col in range(8):

            number = self.coord_font.render(
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
                number,
                number.get_rect(
                    center=(
                        x,
                        self.offset_y - 12
                    )
                )
            )

        # =================================================
        # LETRAS
        # =================================================

        for row in range(8):

            letter = self.coord_font.render(
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
                letter,
                letter.get_rect(
                    center=(
                        self.offset_x - 15,
                        y
                    )
                )
            )

        # =================================================
        # GRADE
        # =================================================
        #
        # As paredes NÃO aparecem na tela.
        #
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

                # =========================================
                # CAMINHO PERCORRIDO
                # =========================================

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
                "JOYSTICK: mover | MATRIZ: caminho"
            )

        else:

            info = (
                "WASD / setas para mover"
            )

        info_text = (
            self.info_font.render(
                info,
                True,
                (150, 150, 150)
            )
        )

        screen.blit(
            info_text,
            info_text.get_rect(
                center=(
                    320,
                    455
                )
            )
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.concluido = False

        self.state = "playing"

        # =================================================
        # NOVO MAPA
        # =================================================

        self.maze_index = random.randint(
            0,
            len(self.mazes) - 1
        )

        self.load_maze()

        # =================================================
        # VOLTA AO INÍCIO
        # =================================================

        self.player_row = (
            self.start_row
        )

        self.player_col = (
            self.start_col
        )

        # =================================================
        # LIMPA CAMINHO
        # =================================================

        self.visited = [
            [
                False
                for _ in range(8)
            ]
            for _ in range(8)
        ]

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        self.joystick_ready = False


    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        try:

            self.clear_led_matrix()

            if self.adc is not None:

                self.adc.close()

        except Exception:

            pass