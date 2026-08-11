import pygame
import random


class SequenceModule:

    def __init__(self):

        # =====================================================
        # ESTADO
        # =====================================================

        self.concluido = False

        # waiting   = esperando iniciar
        # showing   = mostrando a sequência
        # input     = esperando resposta
        # error     = resposta errada
        # completed = módulo concluído

        self.state = "waiting"

        # =====================================================
        # CORES
        # =====================================================

        self.color_names = [
            "vermelho",
            "azul",
            "verde",
            "amarelo"
        ]

        self.colors = {
            "vermelho": (220, 60, 60),
            "azul": (60, 100, 220),
            "verde": (60, 190, 80),
            "amarelo": (230, 210, 60)
        }

        self.dark_colors = {
            "vermelho": (110, 30, 30),
            "azul": (30, 50, 110),
            "verde": (30, 95, 40),
            "amarelo": (115, 105, 30)
        }

        # =====================================================
        # TABELA DE SEQUÊNCIAS
        # =====================================================
        #
        # AQUI ESTÃO AS RESPOSTAS DO JOGO.
        #
        # ESQUERDA  = sequência que será tocada
        # DIREITA   = sequência que deve ser apertada
        #
        # Essa mesma tabela depois vai para o manual
        # do segundo jogador.
        # =====================================================

        self.sequence_table = {

            (
                "vermelho",
                "azul",
                "verde",
                "amarelo"
            ):
            (
                "amarelo",
                "verde",
                "vermelho",
                "azul"
            ),

            (
                "azul",
                "azul",
                "vermelho",
                "verde"
            ):
            (
                "verde",
                "amarelo",
                "azul",
                "vermelho"
            ),

            (
                "verde",
                "amarelo",
                "vermelho",
                "azul"
            ):
            (
                "azul",
                "vermelho",
                "amarelo",
                "verde"
            ),

            (
                "amarelo",
                "vermelho",
                "azul",
                "verde"
            ):
            (
                "vermelho",
                "verde",
                "azul",
                "amarelo"
            ),

            (
                "vermelho",
                "verde",
                "vermelho",
                "azul"
            ):
            (
                "azul",
                "amarelo",
                "verde",
                "vermelho"
            ),

            (
                "azul",
                "verde",
                "amarelo",
                "vermelho"
            ):
            (
                "verde",
                "vermelho",
                "azul",
                "amarelo"
            ),

            (
                "verde",
                "vermelho",
                "amarelo",
                "amarelo"
            ):
            (
                "vermelho",
                "azul",
                "verde",
                "azul"
            ),

            (
                "amarelo",
                "azul",
                "verde",
                "vermelho"
            ):
            (
                "azul",
                "verde",
                "vermelho",
                "amarelo"
            )
        }

        # =====================================================
        # SEQUÊNCIA ATUAL
        # =====================================================

        self.sequence = []

        self.answer_sequence = []

        self.generate_sequence()

        # =====================================================
        # ENTRADA DO JOGADOR
        # =====================================================

        self.player_input = []

        # =====================================================
        # CONTROLE DA EXIBIÇÃO
        # =====================================================

        self.show_index = 0

        self.highlighted_color = None

        self.last_change_time = 0

        # Tempo que cada cor fica acesa
        self.light_duration = 500

        # Pausa entre as cores
        self.pause_duration = 250

        self.showing_light = False

        # =====================================================
        # SONS DAS CORES
        # =====================================================

        self.sounds = {

            "vermelho": pygame.mixer.Sound(
                "assets/sounds/red.wav"
            ),

            "azul": pygame.mixer.Sound(
                "assets/sounds/blue.wav"
            ),

            "verde": pygame.mixer.Sound(
                "assets/sounds/green.wav"
            ),

            "amarelo": pygame.mixer.Sound(
                "assets/sounds/yellow.wav"
            )
        }

        for sound in self.sounds.values():

            sound.set_volume(
                0.5
            )

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
            42
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

        self.button_font = pygame.font.Font(
            None,
            25
        )

        # =====================================================
        # BOTÃO INICIAR
        # =====================================================

        self.start_button = pygame.Rect(
            220,
            360,
            200,
            55
        )

        # =====================================================
        # BOTÕES DAS CORES
        # =====================================================

        self.color_buttons = {

            "vermelho": pygame.Rect(
                120,
                150,
                180,
                80
            ),

            "azul": pygame.Rect(
                340,
                150,
                180,
                80
            ),

            "verde": pygame.Rect(
                120,
                250,
                180,
                80
            ),

            "amarelo": pygame.Rect(
                340,
                250,
                180,
                80
            )
        }


    # =====================================================
    # GERAR DESAFIO
    # =====================================================

    def generate_sequence(self):

        # Pega todas as sequências existentes
        sequences = list(
            self.sequence_table.keys()
        )

        # Sorteia UMA das sequências
        self.sequence = random.choice(
            sequences
        )

        # Busca diretamente a resposta correspondente
        self.answer_sequence = (
            self.sequence_table[
                self.sequence
            ]
        )

        # =================================================
        # DEBUG
        # =================================================
        #
        # Esses prints são úteis durante o desenvolvimento.
        #
        # Depois retiramos a resposta correta.
        # =================================================

        print(
            "Sequência tocada:",
            self.sequence
        )

        print(
            "Resposta correta:",
            self.answer_sequence
        )


    # =====================================================
    # INICIAR SEQUÊNCIA
    # =====================================================

    def start_sequence(self):

        pygame.mixer.stop()

        self.player_input = []

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.last_change_time = (
            pygame.time.get_ticks()
        )

        self.state = "showing"


    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, event):

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # ESPERANDO INICIAR
        # =================================================

        if self.state == "waiting":

            # Mouse
            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if self.start_button.collidepoint(
                    event.pos
                ):

                    self.start_sequence()

            # Espaço
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    self.start_sequence()

        # =================================================
        # MOSTRANDO A SEQUÊNCIA
        # =================================================

        elif self.state == "showing":

            elapsed = (
                current_time
                - self.last_change_time
            )

            # ---------------------------------------------
            # ACENDER PRÓXIMA COR
            # ---------------------------------------------

            if not self.showing_light:

                if (
                    elapsed
                    >= self.pause_duration
                ):

                    if (
                        self.show_index
                        < len(self.sequence)
                    ):

                        color = self.sequence[
                            self.show_index
                        ]

                        self.highlighted_color = (
                            color
                        )

                        pygame.mixer.stop()

                        self.sounds[
                            color
                        ].play()

                        self.showing_light = True

                        self.last_change_time = (
                            current_time
                        )

                    else:

                        # Terminou de mostrar
                        self.highlighted_color = None

                        self.player_input = []

                        self.state = "input"

            # ---------------------------------------------
            # APAGAR COR
            # ---------------------------------------------

            else:

                if (
                    elapsed
                    >= self.light_duration
                ):

                    self.highlighted_color = None

                    self.showing_light = False

                    self.show_index += 1

                    self.last_change_time = (
                        current_time
                    )

        # =================================================
        # RECEBENDO A RESPOSTA
        # =================================================

        elif self.state == "input":

            selected_color = None

            # ---------------------------------------------
            # TECLADO
            # ---------------------------------------------

            if event.type == pygame.KEYDOWN:

                key_map = {

                    pygame.K_1:
                        "vermelho",

                    pygame.K_2:
                        "azul",

                    pygame.K_3:
                        "verde",

                    pygame.K_4:
                        "amarelo"
                }

                if event.key in key_map:

                    selected_color = (
                        key_map[
                            event.key
                        ]
                    )

            # ---------------------------------------------
            # MOUSE
            # ---------------------------------------------

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                for color, button in (
                    self.color_buttons.items()
                ):

                    if button.collidepoint(
                        event.pos
                    ):

                        selected_color = color

                        break

            # ---------------------------------------------
            # PROCESSAR COR
            # ---------------------------------------------

            if selected_color is not None:

                # Toca som da cor apertada
                pygame.mixer.stop()

                self.sounds[
                    selected_color
                ].play()

                self.player_input.append(
                    selected_color
                )

                input_index = (
                    len(self.player_input)
                    - 1
                )

                # =========================================
                # VERIFICAR ERRO
                # =========================================

                if (
                    selected_color
                    != self.answer_sequence[
                        input_index
                    ]
                ):

                    self.trigger_error()

                    return

                # =========================================
                # COMPLETOU
                # =========================================

                if (
                    len(self.player_input)
                    == len(
                        self.answer_sequence
                    )
                ):

                    self.concluido = True

                    self.state = "completed"

                    print(
                        "Sequência concluída!"
                    )

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            if elapsed >= self.error_duration:

                pygame.mixer.stop()

                # Mostra novamente a MESMA sequência
                self.start_sequence()


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        pygame.mixer.stop()

        self.error_sound.play()

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        print(
            "Sequência incorreta!"
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
                "SEQUENCIA CONCLUIDA!"
            )

            title_color = (
                50,
                255,
                100
            )

        elif self.state == "error":

            title_text = (
                "SEQUENCIA ERRADA!"
            )

            title_color = (
                255,
                70,
                70
            )

        else:

            title_text = (
                "MODULO DE SEQUENCIA"
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
            center=(320, 50)
        )

        screen.blit(
            title,
            title_rect
        )

        # =================================================
        # INSTRUÇÃO
        # =================================================

        instruction = self.info_font.render(
            "Observe e informe a sequencia ao especialista",
            True,
            (170, 170, 170)
        )

        instruction_rect = (
            instruction.get_rect(
                center=(320, 100)
            )
        )

        screen.blit(
            instruction,
            instruction_rect
        )

        # =================================================
        # BOTÕES DE CORES
        # =================================================

        for color_name in self.color_names:

            button = self.color_buttons[
                color_name
            ]

            if (
                self.highlighted_color
                == color_name
            ):

                color = self.colors[
                    color_name
                ]

            else:

                color = self.dark_colors[
                    color_name
                ]

            pygame.draw.rect(
                screen,
                color,
                button,
                border_radius=10
            )

            text = self.button_font.render(
                color_name.upper(),
                True,
                (255, 255, 255)
            )

            text_rect = text.get_rect(
                center=button.center
            )

            screen.blit(
                text,
                text_rect
            )

        # =================================================
        # BOTÃO INICIAR
        # =================================================

        if self.state == "waiting":

            pygame.draw.rect(
                screen,
                (70, 70, 70),
                self.start_button,
                border_radius=8
            )

            start_text = self.info_font.render(
                "INICIAR",
                True,
                (255, 255, 255)
            )

            start_rect = (
                start_text.get_rect(
                    center=self.start_button.center
                )
            )

            screen.blit(
                start_text,
                start_rect
            )

        # =================================================
        # ESTADO
        # =================================================

        if self.state == "showing":

            info = "Observe a sequencia"

        elif self.state == "input":

            info = "Aguarde a resposta do especialista"

        elif self.state == "error":

            info = "Resposta incorreta - aguarde"

        elif self.state == "completed":

            info = "Modulo concluido!"

        else:

            info = "SPACE ou clique em INICIAR"

        info_text = self.info_font.render(
            info,
            True,
            (170, 170, 170)
        )

        info_rect = info_text.get_rect(
            center=(320, 450)
        )

        screen.blit(
            info_text,
            info_rect
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        pygame.mixer.stop()

        self.concluido = False

        self.state = "waiting"

        # Sorteia outro desafio
        self.generate_sequence()

        self.player_input = []

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.error_start_time = 0