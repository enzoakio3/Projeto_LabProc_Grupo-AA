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
        # ESTADO DO MÓDULO
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
        # Mapeamento confirmado experimentalmente
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

        # =====================================================
        # DEBOUNCE ROBUSTO
        # =====================================================
        #
        # Funcionamento:
        #
        # 1. Detecta um GPIO LOW
        # 2. Guarda como candidato
        # 3. Espera PRESS_CONFIRM_TIME
        # 4. Confirma apenas se CONTINUA LOW
        # 5. Bloqueia todas as entradas
        # 6. Espera TODOS os botões serem soltos
        # 7. Espera RELEASE_CONFIRM_TIME
        # 8. Libera próxima entrada
        #
        # =====================================================

        # Possível botão sendo pressionado
        self.button_candidate = None

        # Momento em que detectamos o candidato
        self.button_candidate_time = 0

        # 40 ms para confirmar o pressionamento
        self.press_confirm_time = 40

        # Depois de registrar um botão,
        # bloqueamos novas leituras
        self.waiting_release = False

        # Momento em que todos ficaram soltos
        self.release_start_time = None

        # Todos precisam continuar soltos por 70 ms
        self.release_confirm_time = 70

        # O hardware e ativado somente ao entrar neste modulo.
        # Isso evita conflito com o keypad, que compartilha
        # GPIO16, GPIO20, GPIO21 e GPIO26.

        # =====================================================
        # TABELA DE SEQUÊNCIAS
        # =====================================================
        #
        # ESQUERDA = sequência tocada
        # DIREITA  = sequência resposta
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
        # APRESENTAÇÃO DA SEQUÊNCIA
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
    # CONFIGURA HARDWARE
    # =====================================================

    def setup_hardware(self):

        if not RASPBERRY_AVAILABLE:

            print("Modo PC.")

            return

        try:

            GPIO.setwarnings(False)

            GPIO.setmode(
                GPIO.BCM
            )

            # =================================================
            # BOTÕES
            # =================================================

            for color, pin in self.button_pins.items():

                GPIO.setup(
                    pin,
                    GPIO.IN,
                    pull_up_down=GPIO.PUD_UP
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

            print()
            print("Hardware inicializado:")
            print("Vermelho -> GPIO21")
            print("Azul     -> GPIO20")
            print("Verde    -> GPIO16")
            print("Amarelo  -> GPIO26")
            print("Buzzer   -> GPIO4")
            print()

        except Exception as error:

            print(
                "Erro ao configurar GPIO:"
            )

            print(error)

            self.hardware_enabled = False


    # =====================================================
    # ATIVAR / DESATIVAR HARDWARE
    # =====================================================

    def activate(self):
        """Configura botoes e buzzer somente ao entrar no modulo."""
        if self.hardware_enabled:
            return

        self.setup_hardware()
        self.reset_button_reader()

    def deactivate(self):
        """Para o buzzer e libera logicamente o hardware compartilhado."""
        self.stop_sound()

        if RASPBERRY_AVAILABLE:
            try:
                # Libera apenas os GPIOs compartilhados com o keypad.
                for pin in self.button_pins.values():
                    GPIO.cleanup(pin)

                # O buzzer nao e compartilhado, mas encerramos o PWM
                # para que uma futura ativacao possa cria-lo novamente.
                if self.buzzer_pwm is not None:
                    try:
                        self.buzzer_pwm.stop()
                    except Exception:
                        pass

                GPIO.cleanup(self.buzzer_pin)

            except Exception as error:
                print("Erro ao liberar hardware da sequencia:", error)

        self.buzzer_pwm = None
        self.hardware_enabled = False
        self.reset_button_reader()

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

        # =================================================
        # DEBUG
        # =================================================

        print()
        print(
            "========================================"
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
            "========================================"
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
    # TODOS OS BOTÕES ESTÃO SOLTOS?
    # =====================================================

    def all_buttons_released(self):

        if not self.hardware_enabled:

            return True

        for pin in self.button_pins.values():

            if GPIO.input(pin) == GPIO.LOW:

                return False

        return True


    # =====================================================
    # DESCOBRIR QUAL BOTÃO ESTÁ PRESSIONADO
    # =====================================================

    def get_pressed_button(self):

        if not self.hardware_enabled:

            return None

        pressed = []

        for color, pin in self.button_pins.items():

            if GPIO.input(pin) == GPIO.LOW:

                pressed.append(
                    color
                )

        # =================================================
        # SÓ ACEITA EXATAMENTE UM
        # =================================================
        #
        # Se houver dois GPIOs LOW ao mesmo tempo,
        # não escolhemos arbitrariamente o primeiro.
        #
        # Isso é muito importante para o problema
        # azul -> vermelho que você encontrou.
        # =================================================

        if len(pressed) == 1:

            return pressed[0]

        if len(pressed) > 1:

            print(
                "Leitura simultanea ignorada:",
                pressed
            )

        return None


    # =====================================================
    # LER BOTÕES COM DEBOUNCE
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
        # ESTAMOS ESPERANDO O BOTÃO SER SOLTO
        # =================================================

        if self.waiting_release:

            # Todos parecem soltos
            if self.all_buttons_released():

                # Começou período de confirmação
                if self.release_start_time is None:

                    self.release_start_time = (
                        current_time
                    )

                # Continuam soltos por tempo suficiente
                elif (
                    current_time
                    - self.release_start_time
                    >= self.release_confirm_time
                ):

                    self.waiting_release = False

                    self.release_start_time = None

                    self.button_candidate = None

            else:

                # Algum ainda está pressionado
                self.release_start_time = None

            return None

        # =================================================
        # NÃO TEMOS CANDIDATO AINDA
        # =================================================

        if self.button_candidate is None:

            pressed_color = (
                self.get_pressed_button()
            )

            if pressed_color is not None:

                # Encontramos possível botão
                self.button_candidate = (
                    pressed_color
                )

                self.button_candidate_time = (
                    current_time
                )

            return None

        # =================================================
        # TEMOS UM CANDIDATO
        # =================================================

        candidate_pin = (
            self.button_pins[
                self.button_candidate
            ]
        )

        # Se deixou de estar pressionado antes
        # do tempo mínimo, era ruído/bounce

        if GPIO.input(candidate_pin) == GPIO.HIGH:

            self.button_candidate = None

            return None

        # =================================================
        # CONFIRMA APÓS 40 ms
        # =================================================

        if (
            current_time
            - self.button_candidate_time
            >= self.press_confirm_time
        ):

            # Verifica novamente todos os GPIOs
            # no instante da confirmação.

            confirmed_color = (
                self.get_pressed_button()
            )

            # Precisa ser exatamente o mesmo botão
            if (
                confirmed_color
                == self.button_candidate
            ):

                selected_color = (
                    self.button_candidate
                )

                pin = self.button_pins[
                    selected_color
                ]

                # Bloqueia até liberar os botões
                self.waiting_release = True

                self.release_start_time = None

                self.button_candidate = None

                print(
                    f"BOTAO CONFIRMADO: "
                    f"{selected_color} "
                    f"(GPIO{pin})"
                )

                return selected_color

            # Algo mudou durante debounce
            self.button_candidate = None

        return None


    # =====================================================
    # RESET DO LEITOR DOS BOTÕES
    # =====================================================

    def reset_button_reader(self):

        self.button_candidate = None

        self.button_candidate_time = 0

        # Quando começamos uma nova fase,
        # exigimos que todos estejam soltos.

        self.waiting_release = True

        self.release_start_time = None


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

        self.reset_button_reader()

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
        # TOCA SOM
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

        if selected_color != expected_color:

            print(
                "RESULTADO: ERRADO"
            )

            self.trigger_error()

            return

        # =================================================
        # ACERTO
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
            == len(self.answer_sequence)
        ):

            self.stop_sound()

            self.highlighted_color = None

            self.input_tone_active = False

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

        self.reset_button_reader()

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

            if self.pc_error_sound is not None:

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

            # 2200 -> 1700 -> 1100 -> 700

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
        # TERMINOU ERRO
        # =================================================

        if elapsed_total >= self.error_duration:

            self.stop_sound()

            # Mesma sequência novamente
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

                if self.start_button.collidepoint(
                    event.pos
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
            # ACENDER COR
            # ---------------------------------------------

            if not self.showing_light:

                if elapsed >= self.pause_duration:

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

                        # Sequência acabou

                        self.stop_sound()

                        self.highlighted_color = None

                        self.player_input = []

                        # Obriga todos os botões a estarem
                        # soltos antes de começar resposta.

                        self.reset_button_reader()

                        self.state = "input"

            # ---------------------------------------------
            # APAGAR COR
            # ---------------------------------------------

            else:

                if elapsed >= self.light_duration:

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
                and event.type == pygame.KEYDOWN
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
                        key_map[event.key]
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

                        selected_color = color

                        break

            # =================================================
            # PROCESSAR
            # =================================================

            if selected_color is not None:

                self.process_color_input(
                    selected_color
                )

            # =================================================
            # PARA SOM CURTO
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

        self.reset_button_reader()


    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(self):

        self.stop_sound()

        if self.hardware_enabled:

            try:

                if self.buzzer_pwm is not None:

                    self.buzzer_pwm.stop()

                GPIO.output(
                    self.buzzer_pin,
                    GPIO.LOW
                )

                GPIO.cleanup()

            except Exception:

                pass