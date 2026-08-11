import pygame
from bomba import Bomba

pygame.init()

info = pygame.display.Info()

screen = pygame.display.set_mode((info.current_w * 0.9, info.current_h * 0.9))
clock = pygame.time.Clock()

running = True

selected = (1,1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.UP:
                selected = ((selected[0] - 1) % 2, selected[1])
            if event.key == pygame.DOWN:
                selected = ((selected[0] + 1) % 2, selected[1])
            if event.key == pygame.LEFT:
                selected = (selected[0], (selected[1] - 1) % 3)
            if event.key == pygame.RIGHT:
                selected = (selected[0], (selected[1] + 1) % 3)
                
            
    screen.fill((30,30,30))
    #pygame.draw.rect(screen, (200, 50, 50), (100, 100, 200, 100))

    modules = ["module_background","module_background","module_background","module_background","module_background","module_background"]
    bomba = Bomba(modules, screen)

    bomba.draw(screen)

    #pygame.draw.rect(screen, ())
    
    pygame.display.flip()
    
    clock.tick(60)
pygame.quit()

