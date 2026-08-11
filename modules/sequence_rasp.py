import pygame
import random
import time

# =====================================================
# TENTA CARREGAR O HARDWARE DA RASPBERRY
# =====================================================

try:
    from gpiozero import Button, TonalBuzzer
    from gpiozero.tones import Tone

    RASPBERRY_AVAILABLE = True

except ImportError:
    RASPBERRY_AVAILABLE = False


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
        # GPIO DOS BOTÕES DA PLACA
        # =====================================================
        #
        # De acordo com a placa:
        #
        # Vermelho -> GPIO16
        # Azul     -> GPIO20
        # Verde    -> GPIO21
        # Amarelo  -> GPIO26
        #
        # =====================================================

        self.button_pins = {
            "vermelho": 16,
            "azul": 20,
            "verde": 21,
            "amarelo": 26
        }

        # =====================================================
        # BUZZER PASSIVO
        # =====================================================
        #
        # Freenove Projects Board:
        #
        # Passive Buzzer -> GPIO4
        #
        # =====================================================

        self.buzzer_pin = 4

        # Frequência de cada cor.
        #
        # O buzzer passivo da placa tem melhor resposta
        # próximo de 2 kHz, então usamos frequências
        # relativamente altas.

        self.frequencies = {
            "vermelho": 1000,
            "azul": 1300,
            "verde": 1600,
            "amarelo": 2000
        }

        # =====================================================
        # HARDWARE
        # =====================================================

        self.hardware_enabled = False

        self.buttons_gpio = {}

        self.buzzer = None

        self.setup_hardware()

        # =====================================================
        # TABELA DE SEQUÊNCIAS
        # =====================================================
        #
        # ESQUERDA = sequência mostrada/tocada
        #
        # DIREITA = sequência que o especialista
        #           manda o jogador apertar
        #
        # Essa mesma tabela irá para o manual.
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

        self.sequence = ()
        self.answer_sequence = ()

        self.generate_sequence()

        # =====================================================
        # ENTRADA DO JOGADOR
        # =====================================================

        self.player_input = []

        # Fila utilizada pelos botões físicos.
        #
        # O gpiozero detecta o botão em outra thread.
        # Colocamos a cor nessa fila e o update()
        # processa normalmente.

        self.hardware_input_queue = []

        # Evita aceitar entrada enquanto não é hora
        self.accept_hardware_input = False

        # =====================================================
        # EXIBIÇÃO DA SEQUÊNCIA
        # =====================================================

        self.show_index = 0

        self.highlighted_color = None

        self.last_change_time = 0

        # Tempo que cada cor fica ligada
        self.light_duration = 550

        # Intervalo entre cores
        self.pause_duration = 300

        self.showing_light = False

        # =====================================================
        # ERRO
        # =====================================================

        # Não usaremos mais error.wav neste módulo.
        # O erro também será produzido pelo buzzer passivo.

        self.error_start_time = 0

        # Duração total do aviso
        self.error_duration = 900

        # Controle das etapas do som de erro
        self.error_tone_stage = 0
        self.error_last_change = 0

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
        # BOTÕES VISUAIS
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
    # CONFIGURAR HARDWARE
    # =====================================================

    def setup_hardware(self):

        if not RASPBERRY_AVAILABLE:

            print(
                "GPIOZero não encontrado."
            )

            print(
                "Executando módulo em modo PC."
            )

            return

        try:

            # ---------------------------------------------
            # BUZZER PASSIVO
            # ---------------------------------------------

            self.buzzer = TonalBuzzer(
                self.buzzer_pin
            )

            # ---------------------------------------------
            # BOTÕES
            # ---------------------------------------------

            for color, pin in (
                self.button_pins.items()
            ):

                button = Button(
                    pin,
                    pull_up=True,
                    bounce_time=0.08
                )

                # Precisamos capturar a cor correta
                # dentro da função lambda.

                button.when_pressed = (
                    lambda color=color:
                    self.hardware_button_pressed(
                        color
                    )
                )

                self.buttons_gpio[
                    color
                ] = button

            self.hardware_enabled = True

            print(
                "Hardware da Raspberry inicializado."
            )

            print(
                "Botões:"
            )

            print(
                "Vermelho -> GPIO16"
            )

            print(
                "Azul -> GPIO20"
            )

            print(
                "Verde -> GPIO21"
            )

            print(
                "Amarelo -> GPIO26"
            )

            print(
                "Passive Buzzer -> GPIO4"
            )

        except Exception as error:

            print(
                "Não foi possível inicializar GPIO:"
            )

            print(
                error
            )

            self.hardware_enabled = False


    # =====================================================
    # BOTÃO FÍSICO PRESSIONADO
    # =====================================================

    def hardware_button_pressed(
        self,
        color
    ):

        # Só aceita os botões quando estamos
        # esperando a resposta.

        if (
            self.state == "input"
            and self.accept_hardware_input
        ):

            self.hardware_input_queue.append(
                color
            )


    # =====================================================
    # GERAR SEQUÊNCIA
    # =====================================================

    def generate_sequence(self):

        sequences = list(
            self.sequence_table.keys()
        )

        self.sequence = random.choice(
            sequences
        )

        self.answer_sequence = (
            self.sequence_table[
                self.sequence
            ]
        )

        # DEBUG
        #
        # Deixar por enquanto para testar.

        print(
            "Sequência tocada:",
            self.sequence
        )

        print(
            "Resposta correta:",
            self.answer_sequence
        )


    # =====================================================
    # TOCAR COR NO BUZZER
    # =====================================================

    def play_color_tone(
        self,
        color
    ):

        if not self.hardware_enabled:

            return

        frequency = self.frequencies[
            color
        ]

        try:

            self.buzzer.play(
                Tone(
                    frequency
                )
            )

        except Exception as error:

            print(
                "Erro ao tocar buzzer:",
                error
            )


    # =====================================================
    # PARAR BUZZER
    # =====================================================

    def stop_buzzer(self):

        if (
            self.hardware_enabled
            and self.buzzer is not None
        ):

            try:

                self.buzzer.stop()

            except Exception:

                pass


    # =====================================================
    # INICIAR SEQUÊNCIA
    # =====================================================

    def start_sequence(self):

        self.stop_buzzer()

        self.player_input = []

        self.hardware_input_queue = []

        self.accept_hardware_input = False

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.last_change_time = (
            pygame.time.get_ticks()
        )

        self.state = "showing"


    # =====================================================
    # PROCESSAR UMA COR DIGITADA
    # =====================================================

    def process_color_input(
        self,
        selected_color
    ):

        if self.state != "input":

            return

        # ---------------------------------------------
        # TOCA O SOM DO BOTÃO PRESSIONADO
        # ---------------------------------------------

        self.stop_buzzer()

        self.play_color_tone(
            selected_color
        )

        # O som é interrompido no próximo update
        # depois de um pequeno período.

        self.button_tone_start = (
            pygame.time.get_ticks()
        )

        self.player_input.append(
            selected_color
        )

        input_index = (
            len(self.player_input)
            - 1
        )

        # =================================================
        # ERRO
        # =================================================

        if (
            selected_color
            != self.answer_sequence[
                input_index
            ]
        ):

            self.trigger_error()

            return

        # =================================================
        # COMPLETOU
        # =================================================

        if (
            len(self.player_input)
            == len(
                self.answer_sequence
            )
        ):

            self.stop_buzzer()

            self.concluido = True

            self.state = "completed"

            self.accept_hardware_input = False

            print(
                "Sequência concluída!"
            )


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

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if self.start_button.collidepoint(
                    event.pos
                ):

                    self.start_sequence()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    self.start_sequence()

        # =================================================
        # MOSTRANDO SEQUÊNCIA
        # =================================================

        elif self.state == "showing":

            elapsed = (
                current_time
                - self.last_change_time
            )

            # ---------------------------------------------
            # ACENDER / TOCAR PRÓXIMA COR
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

                        self.stop_buzzer()

                        self.play_color_tone(
                            color
                        )

                        self.showing_light = True

                        self.last_change_time = (
                            current_time
                        )

                    else:

                        self.stop_buzzer()

                        self.highlighted_color = None

                        self.player_input = []

                        self.hardware_input_queue = []

                        self.accept_hardware_input = True

                        self.state = "input"

            # ---------------------------------------------
            # APAGAR / PARAR COR
            # ---------------------------------------------

            else:

                if (
                    elapsed
                    >= self.light_duration
                ):

                    self.stop_buzzer()

                    self.highlighted_color = None

                    self.showing_light = False

                    self.show_index += 1

                    self.last_change_time = (
                        current_time
                    )

        # =================================================
        # RECEBENDO RESPOSTA
        # =================================================

        elif self.state == "input":

            selected_color = None

            # ---------------------------------------------
            # BOTÃO FÍSICO
            # ---------------------------------------------

            if self.hardware_input_queue:

                selected_color = (
                    self.hardware_input_queue.pop(
                        0
                    )
                )

            # ---------------------------------------------
            # TECLADO DO PC
            # ---------------------------------------------

            elif event.type == pygame.KEYDOWN:

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

            if selected_color is not None:

                self.process_color_input(
                    selected_color
                )

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            self.update_error_sound(
                current_time
            )


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        self.accept_hardware_input = False

        self.hardware_input_queue = []

        self.stop_buzzer()

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        self.error_last_change = (
            self.error_start_time
        )

        self.error_tone_stage = 0

        # Primeiro tom de erro
        if self.hardware_enabled:

            self.buzzer.play(
                Tone(700)
            )

        print(
            "Sequência incorreta!"
        )


    # =====================================================
    # SOM DE ERRO
    # =====================================================

    def update_error_sound(
        self,
        current_time
    ):

        total_elapsed = (
            current_time
            - self.error_start_time
        )

        stage_elapsed = (
            current_time
            - self.error_last_change
        )

        # Som de erro:
        #
        # 700 Hz
        # 400 Hz
        # 200 Hz

        if (
            self.error_tone_stage == 0
            and stage_elapsed >= 250
        ):

            if self.hardware_enabled:

                self.buzzer.play(
                    Tone(400)
                )

            self.error_tone_stage = 1

            self.error_last_change = (
                current_time
            )

        elif (
            self.error_tone_stage == 1
            and stage_elapsed >= 250
        ):

            if self.hardware_enabled:

                self.buzzer.play(
                    Tone(200)
                )

            self.error_tone_stage = 2

            self.error_last_change = (
                current_time
            )

        if total_elapsed >= self.error_duration:

            self.stop_buzzer()

            # Repete a MESMA sequência
            self.start_sequence()


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
            "Informe a sequencia ao especialista",
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
        # BOTÕES VISUAIS
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

            start_rect = start_text.get_rect(
                center=self.start_button.center
            )

            screen.blit(
                start_text,
                start_rect
            )

        # =================================================
        # ESTADO
        # =================================================

        if self.state == "showing":

            info = (
                "Observe e escute a sequencia"
            )

        elif self.state == "input":

            if self.hardware_enabled:

                info = (
                    "Use os botoes coloridos da placa"
                )

            else:

                info = (
                    "PC: teclas 1, 2, 3 e 4"
                )

        elif self.state == "error":

            info = (
                "Resposta incorreta - aguarde"
            )

        elif self.state == "completed":

            info = (
                "Modulo concluido!"
            )

        else:

            info = (
                "SPACE ou clique em INICIAR"
            )

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

        self.stop_buzzer()

        self.concluido = False

        self.state = "waiting"

        self.generate_sequence()

        self.player_input = []

        self.hardware_input_queue = []

        self.accept_hardware_input = False

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.error_start_time = 0


    # =====================================================
    # FECHAR GPIO
    # =====================================================

    def cleanup(self):

        self.stop_buzzer()

        if self.buzzer is not None:

            self.buzzer.close()

        for button in (
            self.buttons_gpio.values()
        ):

            button.close()