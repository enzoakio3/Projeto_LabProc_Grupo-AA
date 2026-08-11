import pygame
from sys import exit

from modules.sequence import SequenceModule
from modules.password import PasswordModule
from modules.wires import WiresModule
from modules.maze import MazeModule


# =====================================================
# INICIALIZAÇÃO
# =====================================================

pygame.init()


# =====================================================
# CONFIGURAÇÕES
# =====================================================

WIDTH = 640
HEIGHT = 480

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Keep Talking - Raspberry Pi"
)

clock = pygame.time.Clock()


# =====================================================
# IMAGENS
# =====================================================

background = pygame.image.load(
    "assets/images/background.png"
)

background = pygame.transform.scale(
    background,
    (WIDTH, HEIGHT)
)


# =====================================================
# FONTES
# =====================================================

button_font = pygame.font.Font(
    None,
    40
)

module_font = pygame.font.Font(
    None,
    32
)

title_font = pygame.font.Font(
    None,
    48
)


# =====================================================
# CORES
# =====================================================

WHITE = (
    255,
    255,
    255
)

GRAY = (
    70,
    70,
    70
)

LIGHT_GRAY = (
    110,
    110,
    110
)

GREEN = (
    50,
    180,
    80
)


# =====================================================
# ESTADO
# =====================================================

game_state = "menu"


# =====================================================
# BOTÕES
# =====================================================

play_button = pygame.Rect(
    220,
    300,
    200,
    60
)

sequence_button = pygame.Rect(
    170,
    120,
    300,
    55
)

password_button = pygame.Rect(
    170,
    190,
    300,
    55
)

wires_button = pygame.Rect(
    170,
    260,
    300,
    55
)

maze_button = pygame.Rect(
    170,
    330,
    300,
    55
)


# =====================================================
# MÓDULOS
# =====================================================

sequence_module = SequenceModule()

password_module = PasswordModule()

wires_module = WiresModule()

maze_module = MazeModule()


# =====================================================
# DESENHAR BOTÃO
# =====================================================

def draw_button(
    button,
    text,
    font,
    completed=False
):

    mouse_position = (
        pygame.mouse.get_pos()
    )

    if completed:

        color = GREEN

    elif button.collidepoint(
        mouse_position
    ):

        color = LIGHT_GRAY

    else:

        color = GRAY

    pygame.draw.rect(
        screen,
        color,
        button,
        border_radius=8
    )

    button_text = font.render(
        text,
        True,
        WHITE
    )

    text_rect = (
        button_text.get_rect(
            center=button.center
        )
    )

    screen.blit(
        button_text,
        text_rect
    )


# =====================================================
# LOOP PRINCIPAL
# =====================================================

while True:

    # =================================================
    # EVENTOS
    # =================================================

    for event in pygame.event.get():

        # ---------------------------------------------
        # FECHAR
        # ---------------------------------------------

        if event.type == pygame.QUIT:

            pygame.quit()

            exit()

        # ---------------------------------------------
        # MENU
        # ---------------------------------------------

        if game_state == "menu":

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if play_button.collidepoint(
                    event.pos
                ):

                    game_state = (
                        "module_select"
                    )

        # ---------------------------------------------
        # SELEÇÃO DE MÓDULO
        # ---------------------------------------------

        elif game_state == "module_select":

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if sequence_button.collidepoint(
                    event.pos
                ):

                    game_state = "sequence"

                elif password_button.collidepoint(
                    event.pos
                ):

                    game_state = "password"

                elif wires_button.collidepoint(
                    event.pos
                ):

                    game_state = "wires"

                elif maze_button.collidepoint(
                    event.pos
                ):

                    game_state = "maze"

        # ---------------------------------------------
        # SEQUÊNCIA
        # ---------------------------------------------

        elif game_state == "sequence":

            sequence_module.update(
                event
            )

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                game_state = (
                    "module_select"
                )

        # ---------------------------------------------
        # SENHA
        # ---------------------------------------------

        elif game_state == "password":

            password_module.update(
                event
            )

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                game_state = (
                    "module_select"
                )

        # ---------------------------------------------
        # FIOS
        # ---------------------------------------------

        elif game_state == "wires":

            wires_module.update(
                event
            )

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                game_state = (
                    "module_select"
                )

        # ---------------------------------------------
        # LABIRINTO
        # ---------------------------------------------

        elif game_state == "maze":

            maze_module.update(
                event
            )

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                game_state = (
                    "module_select"
                )


    # =================================================
    # MENU
    # =================================================

    if game_state == "menu":

        screen.blit(
            background,
            (0, 0)
        )

        draw_button(
            play_button,
            "JOGAR",
            button_font
        )


    # =================================================
    # SELEÇÃO DOS MÓDULOS
    # =================================================

    elif game_state == "module_select":

        screen.fill(
            (20, 20, 20)
        )

        title = title_font.render(
            "MODULOS",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(320, 60)
        )

        screen.blit(
            title,
            title_rect
        )

        draw_button(
            sequence_button,
            "SEQUENCIA",
            module_font,
            sequence_module.concluido
        )

        draw_button(
            password_button,
            "SENHA",
            module_font,
            password_module.concluido
        )

        draw_button(
            wires_button,
            "FIOS",
            module_font,
            wires_module.concluido
        )

        draw_button(
            maze_button,
            "LABIRINTO",
            module_font,
            maze_module.concluido
        )

        instruction = (
            module_font.render(
                "Verde = concluido",
                True,
                (150, 150, 150)
            )
        )

        instruction_rect = (
            instruction.get_rect(
                center=(320, 430)
            )
        )

        screen.blit(
            instruction,
            instruction_rect
        )


    # =================================================
    # SEQUÊNCIA
    # =================================================

    elif game_state == "sequence":

        sequence_module.update(
            pygame.event.Event(
                pygame.NOEVENT
            )
        )

        sequence_module.draw(
            screen
        )


    # =================================================
    # SENHA
    # =================================================

    elif game_state == "password":

        password_module.update(
            pygame.event.Event(
                pygame.NOEVENT
            )
        )

        password_module.draw(
            screen
        )


    # =================================================
    # FIOS
    # =================================================

    elif game_state == "wires":

        wires_module.update(
            pygame.event.Event(
                pygame.NOEVENT
            )
        )

        wires_module.draw(
            screen
        )


    # =================================================
    # LABIRINTO
    # =================================================

    elif game_state == "maze":

        maze_module.update(
            pygame.event.Event(
                pygame.NOEVENT
            )
        )

        maze_module.draw(
            screen
        )


    # =================================================
    # ATUALIZAÇÃO
    # =================================================

    pygame.display.update()

    clock.tick(60)