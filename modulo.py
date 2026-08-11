import pygame

class Modulo():
    def __init__(self, module_id):
        self.image = pygame.image.load(module_id + ".png").convert_alpha()
        self.rect = None
        