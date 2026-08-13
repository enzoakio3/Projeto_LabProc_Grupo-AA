import pygame
from sys import exit

# from modules.sequence import SequenceModule
from modules.sequence_rasp import SequenceModule
# from modules.password import PasswordModule
from modules.password_rasp import PasswordModule
from modules.wires import WiresModule
#from modules.maze import MazeModule
from modules.maze_rasp import MazeModule
from modules.clocks_rasp import ClocksModule
from modules.game_timer import GameTimer


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

RED = (
    220,
    60,
    60
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


retry_button = pygame.Rect(
    190,
    290,
    260,
    60
)

sequence_button = pygame.Rect(
    170,
    100,
    300,
    50
)

password_button = pygame.Rect(
    170,
    160,
    300,
    50
)

wires_button = pygame.Rect(
    170,
    220,
    300,
    50
)

maze_button = pygame.Rect(
    170,
    280,
    300,
    50
)

clocks_button = pygame.Rect(
    170,
    340,
    300,
    50
)


# =====================================================
# MÓDULOS
# =====================================================

sequence_module = SequenceModule()

password_module = PasswordModule()

wires_module = WiresModule()

maze_module = MazeModule()

clocks_module = ClocksModule()

game_timer = GameTimer(
    duration_seconds=5 * 60
)


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
# CONTROLE GLOBAL DO JOGO
# =====================================================

def activate_sequence_hardware():
    # O keypad e os botoes da sequencia compartilham GPIOs.
    password_module.deactivate()
    sequence_module.activate()


def activate_password_hardware():
    # Libera os botoes da sequencia antes de configurar o keypad.
    sequence_module.deactivate()
    password_module.activate()


def all_modules_completed():

    return (
        sequence_module.concluido
        and password_module.concluido
        and wires_module.concluido
        and maze_module.concluido
        and clocks_module.concluido
    )


def reset_game():

    sequence_module.deactivate()
    password_module.deactivate()

    sequence_module.reset()
    password_module.reset()
    wires_module.reset()
    maze_module.reset()
    clocks_module.reset()

    game_timer.reset()
    game_timer.start()


def cleanup_game():

    try:
        game_timer.cleanup()
    except Exception:
        pass

    for module in [
        sequence_module,
        password_module,
        wires_module,
        maze_module,
        clocks_module
    ]:

        try:

            if hasattr(
                module,
                "cleanup"
            ):

                module.cleanup()

        except Exception:
            pass


def draw_center_message(
    title_text,
    subtitle_text,
    title_color
):

    screen.fill(
        (20, 20, 20)
    )

    title = title_font.render(
        title_text,
        True,
        title_color
    )

    screen.blit(
        title,
        title.get_rect(
            center=(320, 180)
        )
    )

    subtitle = module_font.render(
        subtitle_text,
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(
            center=(320, 240)
        )
    )

    instruction = module_font.render(
        "ESC para voltar ao menu",
        True,
        (150, 150, 150)
    )

    screen.blit(
        instruction,
        instruction.get_rect(
            center=(320, 390)
        )
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

            cleanup_game()

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

                    reset_game()

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

                    activate_sequence_hardware()
                    game_state = "sequence"

                elif password_button.collidepoint(
                    event.pos
                ):

                    activate_password_hardware()
                    game_state = "password"

                elif wires_button.collidepoint(
                    event.pos
                ):

                    game_state = "wires"

                elif maze_button.collidepoint(
                    event.pos
                ):

                    game_state = "maze"

                elif clocks_button.collidepoint(
                    event.pos
                ):

                    game_state = "clocks"

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

                sequence_module.deactivate()

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

                password_module.deactivate()

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

            maze_module.handle_event(
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
        # RELOGIOS
        # ---------------------------------------------

        elif game_state == "clocks":

            clocks_module.handle_event(
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
        # VITORIA / DERROTA
        # ---------------------------------------------

        elif (
            game_state == "victory"
            or game_state == "game_over"
        ):

            # TENTAR NOVAMENTE
            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and retry_button.collidepoint(
                    event.pos
                )
            ):

                reset_game()

                game_state = "module_select"

            # VOLTAR AO MENU
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                game_timer.reset()

                game_state = "menu"



    # =================================================
    # CRONOMETRO GLOBAL
    # =================================================

    if game_state not in [
        "menu",
        "victory",
        "game_over"
    ]:

        game_timer.update()

        # Primeiro verifica se o jogador terminou tudo.
        if all_modules_completed():

            game_timer.stop()

            game_state = "victory"

        # Se o tempo acabou antes de concluir os 5 modulos.
        elif game_timer.is_expired():

            game_state = "game_over"

    # =================================================
    # DISPLAY FISICO DO CRONOMETRO
    # =================================================
    #
    # A matriz do labirinto e o display de 7 segmentos
    # usam GPIO22, GPIO27 e GPIO17.
    #
    # Durante o Maze, a matriz recebe prioridade e o
    # cronometro continua contando internamente.
    #
    # =================================================

    if game_state not in [
        "menu",
        "maze"
    ]:

        game_timer.refresh_display()


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


        draw_button(
            clocks_button,
            "RELOGIOS",
            module_font,
            clocks_module.concluido
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
                center=(320, 455)
            )
        )

        screen.blit(
            instruction,
            instruction_rect
        )

        timer_text = module_font.render(
            f"TEMPO: {game_timer.get_text()}",
            True,
            WHITE
        )

        screen.blit(
            timer_text,
            timer_text.get_rect(
                center=(320, 420)
            )
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

        # O joystick e a matriz precisam ser atualizados
        # continuamente, mesmo quando nao existe evento Pygame.
        maze_module.update()

        maze_module.draw(
            screen
        )


    # =================================================
    # RELOGIOS
    # =================================================

    elif game_state == "clocks":

        # Os potenciometros precisam ser lidos continuamente.
        clocks_module.update()

        clocks_module.draw(
            screen
        )



    # =================================================
    # VITORIA
    # =================================================

    elif game_state == "victory":

        draw_center_message(
            "VOCES VENCERAM!",
            (
                "Todos os 5 modulos foram concluidos "
                f"com {game_timer.get_text()} restantes"
            ),
            GREEN
        )

        draw_button(
            retry_button,
            "TENTAR NOVAMENTE",
            module_font
        )


    # =================================================
    # DERROTA
    # =================================================

    elif game_state == "game_over":

        draw_center_message(
            "VOCE PERDEU!",
            "O tempo de 5 minutos acabou",
            RED
        )

        draw_button(
            retry_button,
            "TENTAR NOVAMENTE",
            module_font
        )


    # =================================================
    # ATUALIZAÇÃO
    # =================================================

    pygame.display.update()

    clock.tick(60)