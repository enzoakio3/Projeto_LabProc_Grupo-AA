import pygame
import random


# =====================================================
# TENTA IMPORTAR GPIO
# =====================================================

try:
    import RPi.GPIO as GPIO
    RASPBERRY_AVAILABLE = True

except ImportError:
    RASPBERRY_AVAILABLE = False


class SequenceModule:

    def __init__(self):

        # =====================================================
        # ESTADO
        # =====================================================

        self.concluido = False

        # waiting
        # showing
        # input
        # error
        # completed

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
        # GPIO DOS BOTÕES
        # =====================================================
        #
        # MAPEAMENTO CONFIRMADO NA PLACA
        #
        # Vermelho -> GPIO21
        # Azul     -> GPIO20
        # Verde    -> GPIO16
        # Amarelo  -> GPIO26
        #
        # =====================================================

        self.button_pins = {
            "vermelho": 21,
            "azul": 20,
            "verde": 16,
            "amarelo": 26
        }

        # =====================================================
        # BUZZER PASSIVO
        # =====================================================

        self.buzzer_pin = 4

        self.frequencies = {
            "vermelho": 1700,
            "azul": 1900,
            "verde": 2100,
            "amarelo": 2300
        }

        # =====================================================
        # HARDWARE
        # =====================================================

        self.hardware_enabled = False

        self.buzzer_pwm = None

        # Guarda o último estado dos botões
        self.previous_button_state = {
            "vermelho": 1,
            "azul": 1,
            "verde": 1,
            "amarelo": 1
        }

        # Debounce
        self.last_button_time = 0
        self.debounce_time = 150

        self.setup_hardware()

        # =====================================================
        # TABELA DE SEQUÊNCIAS
        # =====================================================
        #
        # ESQUERDA = sequência tocada
        # DIREITA  = resposta correta
        #
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
        # RESPOSTA DO JOGADOR
        # =====================================================

        self.player_input = []

        # =====================================================
        # EXIBIÇÃO
        # =====================================================

        self.show_index = 0

        self.highlighted_color = None

        self.last_change_time = 0

        self.light_duration = 550

        self.pause_duration = 300

        self.showing_light = False

        # =====================================================
        # SOM DO BOTÃO
        # =====================================================

        self.input_tone_active = False

        self.input_tone_start = 0

        self.input_tone_duration = 180

        # =====================================================
        # ERRO
        # =====================================================

        self.error_start_time = 0

        self.error_duration = 1000

        self.error_stage = 0

        self.error_last_change = 0

        # =====================================================
        # SOM NO PC
        # =====================================================

        self.pc_sounds = {}

        self.pc_error_sound = None

        if not self.hardware_enabled:

            try:

                self.pc_sounds = {
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

                self.pc_error_sound = pygame.mixer.Sound(
                    "assets/sounds/error.wav"
                )

            except pygame.error:

                print(
                    "Nao foi possivel carregar os sons do PC."
                )

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
                "Modo PC."
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
            # BOTÕES
            # =================================================

            for color, pin in (
                self.button_pins.items()
            ):

                GPIO.setup(
                    pin,
                    GPIO.IN,
                    pull_up_down=GPIO.PUD_UP
                )

                self.previous_button_state[
                    color
                ] = GPIO.input(
                    pin
                )

            # =================================================
            # BUZZER
            # =================================================

            GPIO.setup(
                self.buzzer_pin,
                GPIO.OUT
            )

            self.buzzer_pwm = GPIO.PWM(
                self.buzzer_pin,
                2000
            )

            self.buzzer_pwm.start(
                0
            )

            self.hardware_enabled = True

            print(
                "Hardware inicializado!"
            )

            print(
                "Vermelho -> GPIO21"
            )

            print(
                "Azul -> GPIO20"
            )

            print(
                "Verde -> GPIO16"
            )

            print(
                "Amarelo -> GPIO26"
            )

            print(
                "Buzzer -> GPIO4"
            )

        except Exception as error:

            print(
                "Erro ao configurar GPIO:"
            )

            print(
                error
            )

            self.hardware_enabled = False


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

        print()

        print(
            "=================================="
        )

        print(
            "SEQUENCIA MOSTRADA:"
        )

        print(
            self.sequence
        )

        print(
            "RESPOSTA CORRETA:"
        )

        print(
            self.answer_sequence
        )

        print(
            "=================================="
        )

        print()


    # =====================================================
    # TOCAR COR
    # =====================================================

    def play_color_sound(
        self,
        color
    ):

        if self.hardware_enabled:

            try:

                self.buzzer_pwm.ChangeFrequency(
                    self.frequencies[
                        color
                    ]
                )

                self.buzzer_pwm.ChangeDutyCycle(
                    50
                )

            except Exception as error:

                print(
                    "Erro no buzzer:",
                    error
                )

        else:

            if color in self.pc_sounds:

                pygame.mixer.stop()

                self.pc_sounds[
                    color
                ].play()


    # =====================================================
    # PARAR SOM
    # =====================================================

    def stop_sound(self):

        if self.hardware_enabled:

            try:

                self.buzzer_pwm.ChangeDutyCycle(
                    0
                )

            except Exception:

                pass

        else:

            pygame.mixer.stop()


    # =====================================================
    # LER BOTÕES FÍSICOS
    # =====================================================

    def read_hardware_buttons(self):

        if not self.hardware_enabled:

            return None

        if self.state != "input":

            return None

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # DEBOUNCE
        # =================================================

        if (
            current_time
            - self.last_button_time
            < self.debounce_time
        ):

            return None

        # =================================================
        # LÊ TODOS OS BOTÕES
        # =================================================

        for color, pin in (
            self.button_pins.items()
        ):

            current_state = GPIO.input(
                pin
            )

            previous_state = (
                self.previous_button_state[
                    color
                ]
            )

            # Atualiza o estado
            self.previous_button_state[
                color
            ] = current_state

            # =================================================
            # HIGH -> LOW
            #
            # botão acabou de ser pressionado
            # =================================================

            if (
                previous_state == GPIO.HIGH
                and current_state == GPIO.LOW
            ):

                self.last_button_time = (
                    current_time
                )

                print(
                    f"BOTAO FISICO: "
                    f"{color} "
                    f"(GPIO{pin})"
                )

                return color

        return None


    # =====================================================
    # ATUALIZAR ESTADO DOS BOTÕES
    # =====================================================

    def update_button_states(self):

        if not self.hardware_enabled:

            return

        for color, pin in (
            self.button_pins.items()
        ):

            self.previous_button_state[
                color
            ] = GPIO.input(
                pin
            )


    # =====================================================
    # INICIAR SEQUÊNCIA
    # =====================================================

    def start_sequence(self):

        self.stop_sound()

        self.player_input = []

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.input_tone_active = False

        # Atualiza os estados para evitar leitura
        # de botão pressionado anteriormente
        self.update_button_states()

        self.last_change_time = (
            pygame.time.get_ticks()
        )

        self.state = "showing"


    # =====================================================
    # PROCESSAR COR
    # =====================================================

    def process_color_input(
        self,
        selected_color
    ):

        if self.state != "input":

            return

        input_index = len(
            self.player_input
        )

        if input_index >= len(
            self.answer_sequence
        ):

            return

        expected_color = (
            self.answer_sequence[
                input_index
            ]
        )

        # =================================================
        # DEBUG
        # =================================================

        print()

        print(
            f"POSICAO {input_index + 1}"
        )

        print(
            f"Apertado: {selected_color}"
        )

        print(
            f"Esperado: {expected_color}"
        )

        # =================================================
        # SOM DO BOTÃO
        # =================================================

        self.stop_sound()

        self.play_color_sound(
            selected_color
        )

        self.input_tone_active = True

        self.input_tone_start = (
            pygame.time.get_ticks()
        )

        self.highlighted_color = (
            selected_color
        )

        # =================================================
        # ERRO
        # =================================================

        if (
            selected_color
            != expected_color
        ):

            print(
                "RESULTADO: ERRADO"
            )

            self.trigger_error()

            return

        # =================================================
        # CORRETO
        # =================================================

        print(
            "RESULTADO: CORRETO"
        )

        self.player_input.append(
            selected_color
        )

        print(
            "Progresso:",
            len(self.player_input),
            "/",
            len(self.answer_sequence)
        )

        # =================================================
        # COMPLETOU
        # =================================================

        if (
            len(self.player_input)
            == len(
                self.answer_sequence
            )
        ):

            self.stop_sound()

            self.highlighted_color = None

            self.concluido = True

            self.state = "completed"

            print()

            print(
                "SEQUENCIA COMPLETA!"
            )


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        self.stop_sound()

        self.highlighted_color = None

        self.input_tone_active = False

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        self.error_last_change = (
            self.error_start_time
        )

        self.error_stage = 0

        # =================================================
        # RASPBERRY
        # =================================================

        if self.hardware_enabled:

            self.buzzer_pwm.ChangeFrequency(
                2200
            )

            self.buzzer_pwm.ChangeDutyCycle(
                50
            )

        # =================================================
        # PC
        # =================================================

        else:

            if (
                self.pc_error_sound
                is not None
            ):

                pygame.mixer.stop()

                self.pc_error_sound.play()

        print(
            "Sequencia incorreta!"
        )


    # =====================================================
    # SOM DE ERRO
    # =====================================================

    def update_error_sound(
        self,
        current_time
    ):

        elapsed_total = (
            current_time
            - self.error_start_time
        )

        elapsed_stage = (
            current_time
            - self.error_last_change
        )

        if self.hardware_enabled:

            # -----------------------------------------
            # PRIMEIRO TOM
            # -----------------------------------------

            if (
                self.error_stage == 0
                and elapsed_stage >= 250
            ):

                self.buzzer_pwm.ChangeFrequency(
                    1700
                )

                self.error_stage = 1

                self.error_last_change = (
                    current_time
                )

            # -----------------------------------------
            # SEGUNDO TOM
            # -----------------------------------------

            elif (
                self.error_stage == 1
                and elapsed_stage >= 250
            ):

                self.buzzer_pwm.ChangeFrequency(
                    1100
                )

                self.error_stage = 2

                self.error_last_change = (
                    current_time
                )

            # -----------------------------------------
            # TERCEIRO TOM
            # -----------------------------------------

            elif (
                self.error_stage == 2
                and elapsed_stage >= 250
            ):

                self.buzzer_pwm.ChangeFrequency(
                    700
                )

                self.error_stage = 3

                self.error_last_change = (
                    current_time
                )

        # =================================================
        # TERMINOU O ERRO
        # =================================================

        if (
            elapsed_total
            >= self.error_duration
        ):

            self.stop_sound()

            # Repete a MESMA sequência
            self.start_sequence()


    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, event):

        current_time = (
            pygame.time.get_ticks()
        )

        # =================================================
        # WAITING
        # =================================================

        if self.state == "waiting":

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if (
                    self.start_button.collidepoint(
                        event.pos
                    )
                ):

                    self.start_sequence()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    self.start_sequence()

        # =================================================
        # SHOWING
        # =================================================

        elif self.state == "showing":

            elapsed = (
                current_time
                - self.last_change_time
            )

            # ---------------------------------------------
            # ACENDER
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

                        color = (
                            self.sequence[
                                self.show_index
                            ]
                        )

                        self.highlighted_color = (
                            color
                        )

                        self.stop_sound()

                        self.play_color_sound(
                            color
                        )

                        self.showing_light = True

                        self.last_change_time = (
                            current_time
                        )

                    else:

                        self.stop_sound()

                        self.highlighted_color = None

                        self.player_input = []

                        # Atualiza estado antes de começar
                        # a ler os botões
                        self.update_button_states()

                        self.state = "input"

            # ---------------------------------------------
            # APAGAR
            # ---------------------------------------------

            else:

                if (
                    elapsed
                    >= self.light_duration
                ):

                    self.stop_sound()

                    self.highlighted_color = None

                    self.showing_light = False

                    self.show_index += 1

                    self.last_change_time = (
                        current_time
                    )

        # =================================================
        # INPUT
        # =================================================

        elif self.state == "input":

            selected_color = (
                self.read_hardware_buttons()
            )

            # =================================================
            # TECLADO
            # =================================================

            if (
                selected_color is None
                and event.type
                == pygame.KEYDOWN
            ):

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

            # =================================================
            # MOUSE
            # =================================================

            if (
                selected_color is None
                and event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                for color, button in (
                    self.color_buttons.items()
                ):

                    if button.collidepoint(
                        event.pos
                    ):

                        selected_color = (
                            color
                        )

                        break

            # =================================================
            # PROCESSAR
            # =================================================

            if selected_color is not None:

                self.process_color_input(
                    selected_color
                )

            # =================================================
            # PARAR SOM DO BOTÃO
            # =================================================

            if self.input_tone_active:

                elapsed = (
                    current_time
                    - self.input_tone_start
                )

                if (
                    elapsed
                    >= self.input_tone_duration
                ):

                    self.stop_sound()

                    self.highlighted_color = None

                    self.input_tone_active = False

        # =================================================
        # ERROR
        # =================================================

        elif self.state == "error":

            self.update_error_sound(
                current_time
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

            start_text = (
                self.info_font.render(
                    "INICIAR",
                    True,
                    (255, 255, 255)
                )
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
        # TEXTO DE ESTADO
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
                    "Use 1, 2, 3, 4 ou mouse"
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

        self.stop_sound()

        self.concluido = False

        self.state = "waiting"

        self.generate_sequence()

        self.player_input = []

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.input_tone_active = False

        self.error_start_time = 0

        self.update_button_states()


    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        self.stop_sound()

        if self.hardware_enabled:

            try:

                if (
                    self.buzzer_pwm
                    is not None
                ):

                    self.buzzer_pwm.stop()

                GPIO.output(
                    self.buzzer_pin,
                    GPIO.LOW
                )

                GPIO.cleanup()

            except Exception:

                pass