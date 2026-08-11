import pygame
from modulo import Modulo

class Bomba():
    def __init__(self, modules, screen):
        # Definição do tamanho da bomba a partir da tela
        width, height = screen.get_size()
        module_size = min((width - 2 * 100)/3,(height - 2 * 100)/2)
        side_margin = (width - 3 * module_size) / 2
        top_margin = (height - 2 * module_size) / 2

        self.modules = []
        for module in modules:
            self.modules.append(Modulo(module))
            
        self.size = (3 * module_size, 2 * module_size)
        self.pos = (side_margin, top_margin)

        # Ajuste do tamanho e posição dos módulos
        for i, module in enumerate(self.modules):
            module.image = pygame.transform.scale(module.image, (module_size,module_size))

            module_pos  = (self.pos[0] + ((i % 3) * module_size), self.pos[1] + ((i // 3) * module_size))
            module_rect = pygame.Rect(module_pos[0], module_pos[1], module_size, module_size)

            module.rect = module_rect

    def draw(self, screen):
        for module in self.modules:
            screen.blit(module.image, module.rect)
