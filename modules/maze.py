import pygame
import random


class MazeModule:

    def __init__(self):

        # =====================================================
        # ESTADO
        # =====================================================

        self.concluido = False

        # playing = jogando
        # error = bateu em parede
        # completed = chegou ao destino
        self.state = "playing"

        # =====================================================
        # LABIRINTOS
        # =====================================================
        #
        # 0 = caminho
        # 1 = parede
        #
        # Cada mapa possui exatamente 8x8 posições.
        #
        # Os símbolos servem para o colega identificar
        # qual mapa deve consultar no manual.
        # =====================================================

        self.mazes = [

            # -------------------------------------------------
            # MAPA 1 - CÍRCULO + TRIÂNGULO
            # -------------------------------------------------

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

            # -------------------------------------------------
            # MAPA 2 - QUADRADO + CÍRCULO
            # -------------------------------------------------

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

            # -------------------------------------------------
            # MAPA 3 - TRIÂNGULO + QUADRADO
            # -------------------------------------------------

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

            # -------------------------------------------------
            # MAPA 4 - CÍRCULO + LOSANGO
            # -------------------------------------------------

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

        # =====================================================
        # SORTEIA UM LABIRINTO
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

        self.player_row = self.start_row
        self.player_col = self.start_col

        # =====================================================
        # DESTINO
        # =====================================================

        self.goal_row = 7
        self.goal_col = 7

        # =====================================================
        # CAMINHO PERCORRIDO
        # =====================================================
        #
        # Essa matriz poderá ser usada futuramente
        # para controlar a matriz de LEDs 8x8.
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
        # CONFIGURAÇÃO VISUAL
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
        # SOM DE ERRO
        # =====================================================

        self.error_sound = pygame.mixer.Sound(
            "assets/sounds/error.wav"
        )

        self.error_sound.set_volume(
            0.7
        )

        self.error_duration = int(
            self.error_sound.get_length()
            * 1000
        )

        self.error_start_time = 0

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
    # UPDATE
    # =====================================================

    def update(self, event):

        if self.concluido:
            return

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # JOGANDO
        # =================================================

        if self.state == "playing":

            if event.type == pygame.KEYDOWN:

                # CIMA
                if (
                    event.key == pygame.K_w
                    or event.key == pygame.K_UP
                ):

                    self.try_move(
                        -1,
                        0
                    )

                # BAIXO
                elif (
                    event.key == pygame.K_s
                    or event.key == pygame.K_DOWN
                ):

                    self.try_move(
                        1,
                        0
                    )

                # ESQUERDA
                elif (
                    event.key == pygame.K_a
                    or event.key == pygame.K_LEFT
                ):

                    self.try_move(
                        0,
                        -1
                    )

                # DIREITA
                elif (
                    event.key == pygame.K_d
                    or event.key == pygame.K_RIGHT
                ):

                    self.try_move(
                        0,
                        1
                    )

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            # Espera o error.wav terminar
            if elapsed >= self.error_duration:

                pygame.mixer.stop()

                self.state = "playing"


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

        self.player_row = new_row
        self.player_col = new_col

        # Marca como visitado
        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        # =================================================
        # CHEGOU AO DESTINO
        # =================================================

        if (
            self.player_row == self.goal_row
            and
            self.player_col == self.goal_col
        ):

            print(
                "Labirinto concluído!"
            )

            self.concluido = True

            self.state = "completed"


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        print(
            "Você bateu em uma parede!"
        )

        pygame.mixer.stop()

        self.error_sound.play()

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )


    # =====================================================
    # COORDENADA
    # =====================================================

    def get_coordinate(
        self,
        row,
        col
    ):

        # Linhas:
        # A B C D E F G H
        #
        # Colunas:
        # 1 2 3 4 5 6 7 8

        letter = chr(
            ord("A")
            + row
        )

        number = col + 1

        return f"{letter}{number}"


    # =====================================================
    # DESENHAR SÍMBOLOS
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

            points = [
                (x, y - 14),
                (x - 14, y + 12),
                (x + 14, y + 12)
            ]

            pygame.draw.polygon(
                screen,
                color,
                points,
                width=3
            )

        # QUADRADO
        elif symbol == "square":

            rect = pygame.Rect(
                x - 12,
                y - 12,
                24,
                24
            )

            pygame.draw.rect(
                screen,
                color,
                rect,
                width=3
            )

        # LOSANGO
        elif symbol == "diamond":

            points = [
                (x, y - 14),
                (x + 14, y),
                (x, y + 14),
                (x - 14, y)
            ]

            pygame.draw.polygon(
                screen,
                color,
                points,
                width=3
            )


    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, screen):

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

        title_rect = title.get_rect(
            center=(320, 30)
        )

        screen.blit(
            title,
            title_rect
        )

        # =================================================
        # IDENTIFICADORES DO MAPA
        # =================================================

        identifier = self.info_font.render(
            "MAPA:",
            True,
            (180, 180, 180)
        )

        identifier_rect = (
            identifier.get_rect(
                center=(260, 70)
            )
        )

        screen.blit(
            identifier,
            identifier_rect
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
        # NÚMEROS 1-8
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

            rect = number.get_rect(
                center=(
                    x,
                    self.offset_y - 12
                )
            )

            screen.blit(
                number,
                rect
            )

        # =================================================
        # LETRAS A-H
        # =================================================

        for row in range(8):

            letter = self.coord_font.render(
                chr(
                    ord("A")
                    + row
                ),
                True,
                (150, 150, 150)
            )

            y = (
                self.offset_y
                + row * self.cell_size
                + self.cell_size // 2
            )

            rect = letter.get_rect(
                center=(
                    self.offset_x - 15,
                    y
                )
            )

            screen.blit(
                letter,
                rect
            )

        # =================================================
        # GRADE 8x8
        # =================================================
        #
        # ATENÇÃO:
        #
        # NÃO usamos self.maze aqui para mostrar as paredes.
        #
        # As paredes continuam escondidas do jogador.
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

                # Fundo
                pygame.draw.rect(
                    screen,
                    (35, 35, 35),
                    cell
                )

                # Borda
                pygame.draw.rect(
                    screen,
                    (80, 80, 80),
                    cell,
                    width=1
                )

                # -----------------------------------------
                # CAMINHO PERCORRIDO
                # -----------------------------------------

                if self.visited[row][col]:

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

        goal_rect = pygame.Rect(
            goal_x + 8,
            goal_y + 8,
            self.cell_size - 16,
            self.cell_size - 16
        )

        pygame.draw.rect(
            screen,
            (50, 220, 80),
            goal_rect,
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
        # INSTRUÇÕES
        # =================================================

        instruction = self.info_font.render(
            "WASD / setas | Consulte o especialista",
            True,
            (150, 150, 150)
        )

        instruction_rect = (
            instruction.get_rect(
                center=(320, 455)
            )
        )

        screen.blit(
            instruction,
            instruction_rect
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        pygame.mixer.stop()

        self.concluido = False

        self.state = "playing"

        # Sorteia outro labirinto
        self.maze_index = random.randint(
            0,
            len(self.mazes) - 1
        )

        self.load_maze()

        # Volta ao início
        self.player_row = (
            self.start_row
        )

        self.player_col = (
            self.start_col
        )

        # Limpa caminho
        self.visited = [
            [False for _ in range(8)]
            for _ in range(8)
        ]

        self.visited[
            self.player_row
        ][
            self.player_col
        ] = True

        self.error_start_time = 0