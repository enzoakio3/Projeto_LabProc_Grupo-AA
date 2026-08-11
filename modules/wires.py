import pygame
import random


class WiresModule:

    def __init__(self):

        # =====================================================
        # ESTADO DO MÓDULO
        # =====================================================

        self.concluido = False

        # playing = jogador escolhendo fio
        # error = jogador cortou fio errado
        # completed = módulo concluído
        self.state = "playing"

        # =====================================================
        # CORES DOS FIOS
        # =====================================================

        self.colors = {
            "vermelho": (220, 50, 50),
            "azul": (50, 100, 220),
            "verde": (50, 180, 80),
            "amarelo": (220, 200, 50),
            "branco": (230, 230, 230)
        }

        # =====================================================
        # SOM DE ERRO
        # =====================================================

        self.error_sound = pygame.mixer.Sound(
            "assets/sounds/error.wav"
        )

        self.error_sound.set_volume(0.7)

        self.error_duration = int(
            self.error_sound.get_length() * 1000
        )

        self.error_start_time = 0

        # =====================================================
        # FONTES
        # =====================================================

        self.title_font = pygame.font.Font(
            None,
            48
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

        self.number_font = pygame.font.Font(
            None,
            32
        )

        # =====================================================
        # GERA O PUZZLE
        # =====================================================

        self.generate_puzzle()


    # =====================================================
    # GERAR PUZZLE
    # =====================================================

    def generate_puzzle(self):

        color_names = list(
            self.colors.keys()
        )

        # Gera cinco fios aleatórios
        self.wires = [
            random.choice(color_names)
            for _ in range(5)
        ]

        # Número serial utilizado nas regras
        self.serial_number = random.randint(
            100,
            999
        )

        # Descobre qual fio é o correto
        self.correct_wire = (
            self.calculate_correct_wire()
        )

        self.state = "playing"


    # =====================================================
    # REGRA PARA DESCOBRIR O FIO CORRETO
    # =====================================================

    def calculate_correct_wire(self):

        """
        Retorna o índice do fio correto.

        Índices:
        0 = primeiro fio
        1 = segundo fio
        ...
        4 = quinto fio
        """

        # -------------------------------------------------
        # REGRA 1
        # -------------------------------------------------
        # Se não houver nenhum fio vermelho,
        # corte o segundo fio.

        if "vermelho" not in self.wires:

            return 1

        # -------------------------------------------------
        # REGRA 2
        # -------------------------------------------------
        # Se o último fio for amarelo
        # e o serial for ímpar,
        # corte o último fio.

        if (
            self.wires[-1] == "amarelo"
            and self.serial_number % 2 != 0
        ):

            return 4

        # -------------------------------------------------
        # REGRA 3
        # -------------------------------------------------
        # Se existir exatamente um fio azul,
        # corte o fio azul.

        if self.wires.count("azul") == 1:

            return self.wires.index("azul")

        # -------------------------------------------------
        # REGRA 4
        # -------------------------------------------------
        # Se houver dois ou mais fios vermelhos,
        # corte o último vermelho.

        if self.wires.count("vermelho") >= 2:

            last_red = max(
                index
                for index, color
                in enumerate(self.wires)
                if color == "vermelho"
            )

            return last_red

        # -------------------------------------------------
        # REGRA 5
        # -------------------------------------------------
        # Caso nenhuma regra anterior se aplique,
        # corte o primeiro fio.

        return 0


    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, event):

        if self.concluido:
            return

        current_time = pygame.time.get_ticks()

        # =================================================
        # JOGADOR ESCOLHENDO UM FIO
        # =================================================

        if self.state == "playing":

            # ---------------------------------------------
            # TECLADO
            # ---------------------------------------------

            if event.type == pygame.KEYDOWN:

                key_map = {
                    pygame.K_1: 0,
                    pygame.K_2: 1,
                    pygame.K_3: 2,
                    pygame.K_4: 3,
                    pygame.K_5: 4
                }

                if event.key in key_map:

                    wire_index = key_map[
                        event.key
                    ]

                    self.cut_wire(
                        wire_index
                    )

            # ---------------------------------------------
            # MOUSE
            # ---------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                for index, rect in enumerate(
                    self.wire_rects
                ):

                    # Aumentamos a área clicável
                    # ao redor do fio
                    click_area = rect.inflate(
                        0,
                        25
                    )

                    if click_area.collidepoint(
                        event.pos
                    ):

                        self.cut_wire(
                            index
                        )

                        break

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            # Espera o som de erro terminar
            if elapsed >= self.error_duration:

                pygame.mixer.stop()

                # Permite tentar novamente
                self.state = "playing"


    # =====================================================
    # CORTAR FIO
    # =====================================================

    def cut_wire(self, wire_index):

        # ---------------------------------------------
        # FIO CORRETO
        # ---------------------------------------------

        if wire_index == self.correct_wire:

            print(
                "Fio correto!"
            )

            self.concluido = True

            self.state = "completed"

        # ---------------------------------------------
        # FIO ERRADO
        # ---------------------------------------------

        else:

            print(
                "Fio errado!"
            )

            # Para qualquer som anterior
            pygame.mixer.stop()

            # Toca som de erro
            self.error_sound.play()

            self.state = "error"

            self.error_start_time = (
                pygame.time.get_ticks()
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

        title = self.title_font.render(
            "MODULO DE FIOS",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(320, 45)
        )

        screen.blit(
            title,
            title_rect
        )

        # =================================================
        # SERIAL
        # =================================================

        serial_label = self.info_font.render(
            f"SERIAL: {self.serial_number}",
            True,
            (255, 210, 80)
        )

        serial_rect = serial_label.get_rect(
            center=(320, 90)
        )

        screen.blit(
            serial_label,
            serial_rect
        )

        # =================================================
        # ERRO
        # =================================================

        if self.state == "error":

            error_text = self.title_font.render(
                "FIO ERRADO!",
                True,
                (255, 70, 70)
            )

            error_rect = error_text.get_rect(
                center=(320, 125)
            )

            screen.blit(
                error_text,
                error_rect
            )

        # =================================================
        # CONCLUÍDO
        # =================================================

        elif self.concluido:

            completed_text = (
                self.title_font.render(
                    "FIO CORRETO!",
                    True,
                    (50, 255, 100)
                )
            )

            completed_rect = (
                completed_text.get_rect(
                    center=(320, 125)
                )
            )

            screen.blit(
                completed_text,
                completed_rect
            )

        else:

            instruction = self.info_font.render(
                "Escolha o fio correto",
                True,
                (180, 180, 180)
            )

            instruction_rect = (
                instruction.get_rect(
                    center=(320, 125)
                )
            )

            screen.blit(
                instruction,
                instruction_rect
            )

        # =================================================
        # FIOS
        # =================================================

        self.wire_rects = []

        start_y = 175
        spacing = 50

        for index, color_name in enumerate(
            self.wires
        ):

            y = (
                start_y
                + index * spacing
            )

            # ---------------------------------------------
            # NÚMERO DO FIO
            # ---------------------------------------------

            number = self.number_font.render(
                str(index + 1),
                True,
                (200, 200, 200)
            )

            number_rect = number.get_rect(
                center=(90, y)
            )

            screen.blit(
                number,
                number_rect
            )

            # ---------------------------------------------
            # CONECTORES
            # ---------------------------------------------

            pygame.draw.circle(
                screen,
                (100, 100, 100),
                (130, y),
                10
            )

            pygame.draw.circle(
                screen,
                (100, 100, 100),
                (510, y),
                10
            )

            # ---------------------------------------------
            # FIO
            # ---------------------------------------------

            wire_rect = pygame.Rect(
                130,
                y - 6,
                380,
                12
            )

            self.wire_rects.append(
                wire_rect
            )

            pygame.draw.rect(
                screen,
                self.colors[color_name],
                wire_rect,
                border_radius=6
            )

        # =================================================
        # INSTRUÇÃO DE CONTROLE
        # =================================================

        if not self.concluido:

            info = self.info_font.render(
                "Teclas 1-5 ou clique no fio",
                True,
                (150, 150, 150)
            )

            info_rect = info.get_rect(
                center=(320, 445)
            )

            screen.blit(
                info,
                info_rect
            )


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        pygame.mixer.stop()

        self.concluido = False

        self.error_start_time = 0

        # Gera uma nova configuração
        self.generate_puzzle()