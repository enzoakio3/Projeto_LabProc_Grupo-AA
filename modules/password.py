import pygame
import random


class PasswordModule:

    def __init__(self):

        # Indica se o módulo foi concluído
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

        # Sorteia um código
        self.code = random.choice(
            list(self.password_table.keys())
        )

        # Senha correta correspondente
        self.correct_password = (
            self.password_table[self.code]
        )

        # Senha digitada pelo jogador
        self.player_password = ""

        # Quantidade máxima de dígitos
        self.password_length = 4

        # =====================================================
        # SOM DE ERRO
        # =====================================================

        self.error_sound = pygame.mixer.Sound(
            "assets/sounds/error.wav"
        )

        self.error_sound.set_volume(0.7)

        # Duração do som em milissegundos
        self.error_duration = int(
            self.error_sound.get_length() * 1000
        )

        # =====================================================
        # ESTADO
        # =====================================================

        # playing = jogador digitando
        # error = tocando som de erro
        # completed = módulo concluído

        self.state = "playing"

        # Momento em que o som de erro começou
        self.error_start_time = 0

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
    # UPDATE
    # =====================================================

    def update(self, event):

        if self.concluido:
            return

        current_time = pygame.time.get_ticks()

        # =================================================
        # JOGADOR DIGITANDO
        # =================================================

        if self.state == "playing":

            if event.type == pygame.KEYDOWN:

                # -----------------------------------------
                # NÚMEROS
                # -----------------------------------------

                if event.unicode.isdigit():

                    if (
                        len(self.player_password)
                        < self.password_length
                    ):

                        self.player_password += (
                            event.unicode
                        )

                # -----------------------------------------
                # BACKSPACE
                # -----------------------------------------

                elif event.key == pygame.K_BACKSPACE:

                    self.player_password = (
                        self.player_password[:-1]
                    )

                # -----------------------------------------
                # ENTER
                # -----------------------------------------

                elif event.key == pygame.K_RETURN:

                    self.check_password()

        # =================================================
        # ERRO
        # =================================================

        elif self.state == "error":

            elapsed = (
                current_time
                - self.error_start_time
            )

            # Só volta ao jogo depois
            # que o som terminar
            if elapsed >= self.error_duration:

                pygame.mixer.stop()

                self.player_password = ""

                self.state = "playing"


    # =====================================================
    # VERIFICAR SENHA
    # =====================================================

    def check_password(self):

        # Só confirma se os 4 dígitos
        # tiverem sido preenchidos
        if (
            len(self.player_password)
            != self.password_length
        ):

            return

        # =================================================
        # SENHA CORRETA
        # =================================================

        if (
            self.player_password
            == self.correct_password
        ):

            print("Senha correta!")

            self.concluido = True

            self.state = "completed"

        # =================================================
        # SENHA INCORRETA
        # =================================================

        else:

            print("Senha incorreta!")

            # Para qualquer outro som
            pygame.mixer.stop()

            # Toca som de erro
            self.error_sound.play()

            # Entra no estado de erro
            self.state = "error"

            # Guarda quando o som começou
            self.error_start_time = (
                pygame.time.get_ticks()
            )


    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, screen):

        # Fundo
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
        # MÓDULO CONCLUÍDO
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
        # MOSTRA OS 4 CAMPOS
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
                + i * (
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

            # Se já existe um dígito
            if i < len(
                self.player_password
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

        info1 = self.info_font.render(
            "0-9: digitar",
            True,
            (160, 160, 160)
        )

        info2 = self.info_font.render(
            "BACKSPACE: apagar",
            True,
            (160, 160, 160)
        )

        info3 = self.info_font.render(
            "ENTER: confirmar",
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
            list(self.password_table.keys())
        )

        self.correct_password = (
            self.password_table[self.code]
        )

        self.player_password = ""

        self.state = "playing"

        self.error_start_time = 0