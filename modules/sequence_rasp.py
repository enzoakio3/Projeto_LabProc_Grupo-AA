import pygame
import random


# =====================================================
# TENTA IMPORTAR O GPIO DA RASPBERRY
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
        # GPIO DOS BOTÕES
        # =====================================================
        #
        # Placa:
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

        self.buzzer_pin = 4

        # Frequências usadas para diferenciar as cores.
        # Mantemos todas relativamente próximas de 2 kHz,
        # onde o buzzer da placa respondeu melhor.

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

        # Guarda estado anterior dos botões para detectar
        # apenas o momento em que foram pressionados.

        self.previous_button_state = {
            "vermelho": GPIO.HIGH if RASPBERRY_AVAILABLE else 1,
            "azul": GPIO.HIGH if RASPBERRY_AVAILABLE else 1,
            "verde": GPIO.HIGH if RASPBERRY_AVAILABLE else 1,
            "amarelo": GPIO.HIGH if RASPBERRY_AVAILABLE else 1
        }

        self.setup_hardware()

        # =====================================================
        # TABELA DE SEQUÊNCIAS
        # =====================================================
        #
        # ESQUERDA:
        # sequência que o jogador vê/ouve.
        #
        # DIREITA:
        # sequência que o especialista encontra no manual
        # e manda o jogador apertar.
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
        # ENTRADA DO JOGADOR
        # =====================================================

        self.player_input = []

        # =====================================================
        # CONTROLE DA EXIBIÇÃO
        # =====================================================

        self.show_index = 0

        self.highlighted_color = None

        self.last_change_time = 0

        # Tempo que a cor fica acesa/tocando
        self.light_duration = 550

        # Pausa entre as cores
        self.pause_duration = 300

        self.showing_light = False

        # =====================================================
        # SOM DE BOTÃO
        # =====================================================

        # Quando o jogador aperta um botão físico,
        # tocamos a nota por um pequeno período.

        self.input_tone_active = False

        self.input_tone_start = 0

        self.input_tone_duration = 180

        # =====================================================
        # SOM DE ERRO
        # =====================================================

        self.error_start_time = 0

        # O erro dura cerca de 1 segundo
        self.error_duration = 1000

        self.error_stage = 0

        self.error_last_change = 0

        # =====================================================
        # ÁUDIO PARA PC
        # =====================================================

        # Se não estivermos na Raspberry,
        # continuamos usando os WAVs.

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
                    "Não foi possível carregar os sons do PC."
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
        # BOTÕES NA TELA
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
                "RPi.GPIO não disponível."
            )

            print(
                "Executando sequência em modo PC."
            )

            return

        try:

            # ---------------------------------------------
            # MODO BCM
            # ---------------------------------------------

            GPIO.setmode(
                GPIO.BCM
            )

            GPIO.setwarnings(
                False
            )

            # ---------------------------------------------
            # BOTÕES
            # ---------------------------------------------

            for color, pin in (
                self.button_pins.items()
            ):

                GPIO.setup(
                    pin,
                    GPIO.IN,
                    pull_up_down=GPIO.PUD_UP
                )

            # ---------------------------------------------
            # BUZZER
            # ---------------------------------------------

            GPIO.setup(
                self.buzzer_pin,
                GPIO.OUT
            )

            # Cria PWM inicialmente em 2000 Hz
            self.buzzer_pwm = GPIO.PWM(
                self.buzzer_pin,
                2000
            )

            # Começa desligado
            self.buzzer_pwm.start(
                0
            )

            self.hardware_enabled = True

            print(
                "Hardware da sequência inicializado!"
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
                "Buzzer passivo -> GPIO4"
            )

        except Exception as error:

            print(
                "Erro ao inicializar hardware:"
            )

            print(
                error
            )

            self.hardware_enabled = False


    # =====================================================
    # GERAR DESAFIO
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

        # DEBUG PARA DESENVOLVIMENTO

        print(
            "Sequência tocada:",
            self.sequence
        )

        print(
            "Resposta correta:",
            self.answer_sequence
        )


    # =====================================================
    # TOCAR COR
    # =====================================================

    def play_color_sound(
        self,
        color
    ):

        # =================================================
        # RASPBERRY
        # =================================================

        if self.hardware_enabled:

            frequency = self.frequencies[
                color
            ]

            try:

                self.buzzer_pwm.ChangeFrequency(
                    frequency
                )

                # 50% = onda quadrada
                self.buzzer_pwm.ChangeDutyCycle(
                    50
                )

            except Exception as error:

                print(
                    "Erro ao tocar buzzer:",
                    error
                )

        # =================================================
        # PC
        # =================================================

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

        # Só aceita botão durante a resposta
        if self.state != "input":

            # Mesmo quando não aceitamos entrada,
            # atualizamos o estado anterior para evitar
            # detectar um botão que ficou segurado.

            for color, pin in (
                self.button_pins.items()
            ):

                self.previous_button_state[
                    color
                ] = GPIO.input(
                    pin
                )

            return None

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

            # Botões são active LOW.
            #
            # HIGH -> LOW significa que acabou
            # de ser pressionado.

            if (
                previous_state == GPIO.HIGH
                and current_state == GPIO.LOW
            ):

                self.previous_button_state[
                    color
                ] = current_state

                return color

            self.previous_button_state[
                color
            ] = current_state

        return None


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

        self.last_change_time = (
            pygame.time.get_ticks()
        )

        self.state = "showing"


    # =====================================================
    # PROCESSAR BOTÃO
    # =====================================================

    def process_color_input(
        self,
        selected_color
    ):

        if self.state != "input":

            return

        # ---------------------------------------------
        # TOCA O TOM DO BOTÃO
        # ---------------------------------------------

        self.stop_sound()

        self.play_color_sound(
            selected_color
        )

        self.input_tone_active = True

        self.input_tone_start = (
            pygame.time.get_ticks()
        )

        # Também acende botão na tela
        self.highlighted_color = (
            selected_color
        )

        # ---------------------------------------------
        # GUARDA RESPOSTA
        # ---------------------------------------------

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

            self.stop_sound()

            self.highlighted_color = None

            self.concluido = True

            self.state = "completed"

            print(
                "Sequência concluída!"
            )


    # =====================================================
    # ERRO
    # =====================================================

    def trigger_error(self):

        self.stop_sound()

        self.highlighted_color = None

        self.state = "error"

        self.error_start_time = (
            pygame.time.get_ticks()
        )

        self.error_last_change = (
            self.error_start_time
        )

        self.error_stage = 0

        # ---------------------------------------------
        # RASPBERRY
        # ---------------------------------------------

        if self.hardware_enabled:

            self.buzzer_pwm.ChangeFrequency(
                2200
            )

            self.buzzer_pwm.ChangeDutyCycle(
                50
            )

        # ---------------------------------------------
        # PC
        # ---------------------------------------------

        else:

            if self.pc_error_sound is not None:

                pygame.mixer.stop()

                self.pc_error_sound.play()

        print(
            "Sequência incorreta!"
        )


    # =====================================================
    # ATUALIZAR SOM DE ERRO
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

        # Na Raspberry fazemos uma sequência descendente
        # para diferenciar bem o erro das notas normais.

        if self.hardware_enabled:

            # -----------------------------------------
            # ETAPA 1
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
            # ETAPA 2
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
            # ETAPA 3
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

        if elapsed_total >= self.error_duration:

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
            # COMEÇA PRÓXIMA COR
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

                        self.stop_sound()

                        self.play_color_sound(
                            color
                        )

                        self.showing_light = True

                        self.last_change_time = (
                            current_time
                        )

                    else:

                        # Sequência terminou
                        self.stop_sound()

                        self.highlighted_color = None

                        self.player_input = []

                        self.state = "input"

            # ---------------------------------------------
            # TERMINA COR ATUAL
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
        # RECEBENDO RESPOSTA
        # =================================================

        elif self.state == "input":

            selected_color = None

            # ---------------------------------------------
            # PRIMEIRO: BOTÕES FÍSICOS
            # ---------------------------------------------

            selected_color = (
                self.read_hardware_buttons()
            )

            # ---------------------------------------------
            # TECLADO
            # ---------------------------------------------

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
                        key_map[
                            event.key
                        ]
                    )

            # ---------------------------------------------
            # MOUSE
            # ---------------------------------------------

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

            # ---------------------------------------------
            # PROCESSA
            # ---------------------------------------------

            if selected_color is not None:

                self.process_color_input(
                    selected_color
                )

            # ---------------------------------------------
            # PARA SOM DO BOTÃO
            # ---------------------------------------------

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
        # ERRO
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
        # BOTÕES
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
                    "Use 1, 2, 3, 4 ou o mouse"
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

        # Sorteia novo desafio
        self.generate_sequence()

        self.player_input = []

        self.show_index = 0

        self.highlighted_color = None

        self.showing_light = False

        self.input_tone_active = False

        self.error_start_time = 0


    # =====================================================
    # LIMPAR GPIO
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