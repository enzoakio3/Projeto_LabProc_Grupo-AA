import pygame

def draw_bomb(screen):
    width, height = screen.get_size()
    
    module = pygame.image.load("module_background.png")
    module_size = 200
    module = pygame.transform.scale(module, (module_size,module_size))
    
    side_margin = (width - 3 * module_size) / 2
    top_margin = (height - 2 * module_size) / 2
    
    for i in range(3):
        for j in range(2):
            screen.blit(module, (side_margin + i * module_size, top_margin + j * module_size))
    
    return

pygame.init()

screen = pygame.display.set_mode((1000,600))
clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    screen.fill((30,30,30))
    
    #pygame.draw.rect(screen, (200, 50, 50), (100, 100, 200, 100))
    draw_bomb(screen)
    
    pygame.display.flip()
    
    clock.tick(60)
pygame.quit()

