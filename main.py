import pygame
from sys import exit

pygame.init()

# -------------------------
# CONFIGURAÇÕES
# -------------------------

WIDTH = 640
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keep Talking - Raspberry Pi")

clock = pygame.time.Clock()

# -------------------------
# IMAGENS
# -------------------------

background = pygame.image.load("assets/images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# -------------------------
# FONTES
# -------------------------

button_font = pygame.font.Font(None, 40)
game_font = pygame.font.Font(None, 50)

# -------------------------
# CORES
# -------------------------

WHITE = (255, 255, 255)
GRAY = (70, 70, 70)
LIGHT_GRAY = (110, 110, 110)
BLACK = (20, 20, 20)

# -------------------------
# ESTADOS
# -------------------------

game_state = "menu"

# -------------------------
# BOTÕES
# -------------------------

play_button = pygame.Rect(220, 300, 200, 60)

# -------------------------
# LOOP PRINCIPAL
# -------------------------

while True:

    mouse_position = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_state == "menu":

                if play_button.collidepoint(event.pos):
                    game_state = "game"

    # -------------------------
    # MENU
    # -------------------------

    if game_state == "menu":

        screen.blit(background, (0, 0))

        if play_button.collidepoint(mouse_position):
            button_color = LIGHT_GRAY
        else:
            button_color = GRAY

        pygame.draw.rect(
            screen,
            button_color,
            play_button,
            border_radius=8
        )

        play_text = button_font.render(
            "JOGAR",
            True,
            WHITE
        )

        play_text_rect = play_text.get_rect(
            center=play_button.center
        )

        screen.blit(play_text, play_text_rect)

    # -------------------------
    # JOGO
    # -------------------------

    elif game_state == "game":

        screen.fill(BLACK)

        game_text = game_font.render(
            "JOGO INICIADO",
            True,
            WHITE
        )

        game_text_rect = game_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2)
        )

        screen.blit(game_text, game_text_rect)

    pygame.display.update()
    clock.tick(60)