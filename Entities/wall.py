import pygame


class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, image):

        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
