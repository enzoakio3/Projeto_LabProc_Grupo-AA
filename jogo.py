import pygame
from bomba import Bomba

pygame.init()

info = pygame.display.Info()

screen = pygame.display.set_mode((info.current_w * 0.9, info.current_h * 0.9))
clock = pygame.time.Clock()

running = True

selector = (0,0)
selected = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if selected == False:
                if event.key == pygame.K_UP:
                    selector = (selector[0], (selector[1] - 1) % 2)
                if event.key == pygame.K_DOWN:
                    selector = (selector[0], (selector[1] + 1) % 2)
                if event.key == pygame.K_LEFT:
                    selector = ((selector[0] - 1) % 3, selector[1])
                if event.key == pygame.K_RIGHT:
                    selector = ((selector[0] + 1) % 3, selector[1])
                if event.key == pygame.K_SPACE:
                    selected = True
            if selected == True:
                if event.key == pygame.K_ESCAPE:
                    selected = False

    screen.fill((30,30,30))

    modules = ["module_background",
               "module_background",
               "module_background",
               "module_background",
               "module_background",
               "module_background"]
    
    bomba = Bomba(modules, screen)

    bomba.draw(screen)

    selector_color = (0, 255, 0) if selected else (255, 255, 255)
    pygame.draw.rect(screen, selector_color, bomba.modules[selector[0] + selector[1] * 3].rect, 5)
    
    pygame.display.flip()
    
    clock.tick(60)
pygame.quit()
