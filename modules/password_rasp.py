import pygame
import random


# =====================================================
# KEYPAD DA RASPBERRY
# =====================================================

try:
    from hardware import Keypad

    RASPBERRY_AVAILABLE = True

except ImportError:
    RASPBERRY_AVAILABLE = False


class PasswordModule:

    def __init__(self):

        # =====================================================
        # ESTADO
        # =====================================================

        self.concluido = False

        # =====================================================
        # CÓDIGOS E SENHAS
        # =====================================================

        self.password_table = {
            317: "4821",
            428: "7315",
            592: "2048",
            731: "9163",
            846: "3572"
        }

        self.code = random.choice(
            list(self.password_table.keys())
        )

        self.correct_password = (
            self.password_table[self.code]
        )

        self.player_password = ""

        self.password_length = 4

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

        # =====================================================
        # ESTADO DO JOGO
        # =====================================================

        # playing
        # error
        # completed

        self.state = "playing"

        self.error_start_time = 0

        # =====================================================
        # KEYPAD
        # =====================================================

        self.keypad = None
        self.hardware_enabled = False

        self.setup_keypad()

        # =====================================================
        # FONTES
        # =====================================================

        self.title_font = pygame.font.Font(
            None,
            48
        )

        self.code_font = pygame.font.Font(
            None,
            55
        )

        self.password_font = pygame.font.Font(
            None,
            60
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

    # =====================================================
    # CONFIGURAR KEYPAD
    # =====================================================

    def setup_keypad(self):

        if not RASPBERRY_AVAILABLE:

            print(
                "Password em modo PC."
            )

            return

        try:

            rows = 4
            cols = 4

            keys = [
                '1', '2', '3', 'A',
                '4', '5', '6', 'B',
                '7', '8', '9', 'C',
                '*', '0', '#', 'D'
            ]

            # Pinagem confirmada no teste
            rows_pins = [
                16,
                20,
                21,
                26
            ]

            cols_pins = [
                19,
                13,
                6,
                5
            ]

            self.keypad = Keypad.Keypad(
                keys,
                rows_pins,
                cols_pins,
                rows,
                cols
            )

            self.keypad.setDebounceTime(
                50
            )

            self.hardware_enabled = True

            print()
            print(
                "================================"
            )
            print(
                "KEYPAD DO PASSWORD OK"
            )
            print(
                "================================"
            )
            print(
                "Linhas: 16, 20, 21, 26"
            )
            print(
                "Colunas: 19, 13, 6, 5"
            )
            print(
                "* = apagar"
            )
            print(
                "# = confirmar"
            )
            print(
                "================================"
            )
            print()

        except Exception as error:

            print(
                "Erro ao inicializar keypad:"
            )

            print(
                error
            )

            self.keypad = None
            self.hardware_enabled = False

    # =====================================================
    # PROCESSAR UMA TECLA
    # =====================================================

    def process_key(self, key):

        if self.concluido:
            return

        if self.state != "playing":
            return

        # =================================================
        # NÚMEROS
        # =================================================

        if key in "0123456789":

            if (
                len(self.player_password)
                < self.password_length
            ):

                self.player_password += key

                print(
                    "Senha:",
                    "*" * len(
                        self.player_password
                    )
                )

        # =================================================
        # APAGAR
        # =================================================

        elif key == "*":

            self.player_password = (
                self.player_password[:-1]
            )

            print(
                "Senha:",
                "*" * len(
                    self.player_password
                )
            )

        # =================================================
        # CONFIRMAR
        # =================================================

        elif key == "#":

            self.check_password()

    # =====================================================
    # LER KEYPAD
    # =====================================================

    def read_keypad(self):

        if not self.hardware_enabled:
            return

        if self.keypad is None:
            return

        try:

            key = self.keypad.getKey()

            if key != self.keypad.NULL:

                print(
                    "Keypad:",
                    key
                )

                self.process_key(
                    key
                )

        except Exception as error:

            print(
                "Erro ao ler keypad:",
                error
            )

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
        # JOGADOR DIGITANDO
        # =================================================

        if self.state == "playing":

            # =============================================
            # KEYPAD FÍSICO
            # =============================================

            self.read_keypad()

            # =============================================
            # TECLADO DO PC
            # =============================================

            if event.type == pygame.KEYDOWN:

                # Números
                if event.unicode.isdigit():

                    self.process_key(
                        event.unicode
                    )

                # Backspace
                elif (
                    event.key
                    == pygame.K_BACKSPACE
                ):

                    self.process_key(
                        "*"
                    )

                # Enter
                elif (
                    event.key
                    == pygame.K_RETURN
                ):

                    self.process_key(
                        "#"
                    )

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            # Espera o som terminar
            if elapsed >= self.error_duration:

                pygame.mixer.stop()

                self.player_password = ""

                self.state = "playing"

    # =====================================================
    # VERIFICAR SENHA
    # =====================================================

    def check_password(self):

        # Só confirma com exatamente 4 dígitos
        if (
            len(self.player_password)
            != self.password_length
        ):

            print(
                "Digite os 4 digitos."
            )

            return

        # =================================================
        # CORRETA
        # =================================================

        if (
            self.player_password
            == self.correct_password
        ):

            print(
                "Senha correta!"
            )

            self.concluido = True

            self.state = "completed"

        # =================================================
        # INCORRETA
        # =================================================

        else:

            print(
                "Senha incorreta!"
            )

            pygame.mixer.stop()

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
            "MODULO DE SENHA",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(320, 55)
        )

        screen.blit(
            title,
            title_rect
        )

        # =================================================
        # CÓDIGO
        # =================================================

        code_label = self.info_font.render(
            "CODIGO DO DISPOSITIVO",
            True,
            (180, 180, 180)
        )

        code_label_rect = (
            code_label.get_rect(
                center=(320, 115)
            )
        )

        screen.blit(
            code_label,
            code_label_rect
        )

        code_text = self.code_font.render(
            str(self.code),
            True,
            (255, 210, 80)
        )

        code_rect = code_text.get_rect(
            center=(320, 155)
        )

        screen.blit(
            code_text,
            code_rect
        )

        # =================================================
        # CONCLUÍDO
        # =================================================

        if self.concluido:

            completed_text = (
                self.title_font.render(
                    "SENHA CORRETA!",
                    True,
                    (50, 255, 100)
                )
            )

            completed_rect = (
                completed_text.get_rect(
                    center=(320, 270)
                )
            )

            screen.blit(
                completed_text,
                completed_rect
            )

            module_text = (
                self.info_font.render(
                    "MODULO CONCLUIDO",
                    True,
                    (50, 255, 100)
                )
            )

            module_rect = (
                module_text.get_rect(
                    center=(320, 320)
                )
            )

            screen.blit(
                module_text,
                module_rect
            )

            return

        # =================================================
        # ERRO
        # =================================================

        if self.state == "error":

            error_text = (
                self.title_font.render(
                    "SENHA INCORRETA!",
                    True,
                    (255, 70, 70)
                )
            )

            error_rect = (
                error_text.get_rect(
                    center=(320, 270)
                )
            )

            screen.blit(
                error_text,
                error_rect
            )

            return

        # =================================================
        # CAMPO DA SENHA
        # =================================================

        password_label = (
            self.info_font.render(
                "DIGITE A SENHA",
                True,
                (180, 180, 180)
            )
        )

        password_label_rect = (
            password_label.get_rect(
                center=(320, 215)
            )
        )

        screen.blit(
            password_label,
            password_label_rect
        )

        # =================================================
        # 4 CAMPOS
        # =================================================

        start_x = 185

        box_width = 60
        box_height = 70
        spacing = 10

        for i in range(
            self.password_length
        ):

            x = (
                start_x
                + i
                * (
                    box_width
                    + spacing
                )
            )

            box = pygame.Rect(
                x,
                250,
                box_width,
                box_height
            )

            pygame.draw.rect(
                screen,
                (70, 70, 70),
                box,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                (180, 180, 180),
                box,
                width=2,
                border_radius=8
            )

            if (
                i
                < len(
                    self.player_password
                )
            ):

                digit = (
                    self.password_font.render(
                        self.player_password[i],
                        True,
                        (255, 255, 255)
                    )
                )

                digit_rect = (
                    digit.get_rect(
                        center=box.center
                    )
                )

                screen.blit(
                    digit,
                    digit_rect
                )

            else:

                underscore = (
                    self.password_font.render(
                        "_",
                        True,
                        (130, 130, 130)
                    )
                )

                underscore_rect = (
                    underscore.get_rect(
                        center=(
                            box.centerx,
                            box.centery - 5
                        )
                    )
                )

                screen.blit(
                    underscore,
                    underscore_rect
                )

        # =================================================
        # INSTRUÇÕES
        # =================================================

        if self.hardware_enabled:

            instruction1 = (
                "KEYPAD 0-9: digitar"
            )

            instruction2 = (
                "* : apagar"
            )

            instruction3 = (
                "# : confirmar"
            )

        else:

            instruction1 = (
                "0-9: digitar"
            )

            instruction2 = (
                "BACKSPACE: apagar"
            )

            instruction3 = (
                "ENTER: confirmar"
            )

        info1 = self.info_font.render(
            instruction1,
            True,
            (160, 160, 160)
        )

        info2 = self.info_font.render(
            instruction2,
            True,
            (160, 160, 160)
        )

        info3 = self.info_font.render(
            instruction3,
            True,
            (160, 160, 160)
        )

        screen.blit(
            info1,
            (220, 355)
        )

        screen.blit(
            info2,
            (220, 385)
        )

        screen.blit(
            info3,
            (220, 415)
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        pygame.mixer.stop()

        self.concluido = False

        self.code = random.choice(
            list(
                self.password_table.keys()
            )
        )

        self.correct_password = (
            self.password_table[
                self.code
            ]
        )

        self.player_password = ""

        self.state = "playing"

        self.error_start_time = 0