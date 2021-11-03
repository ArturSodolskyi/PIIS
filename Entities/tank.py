import pygame
from Entities.bullet import Bullet
from Entities.side import Side
from assets.path import ImagePath


class Tank(pygame.sprite.Sprite):
    score = 0
    side = ''
    speed = 1
    image_path = ''
    bullet = None
    enemies = []
    player = False
    goal = None
    movements = None

    def rotate_image(self, side):
        path = self.image_path[:(len(self.image_path) - 4)] + '_' + side + self.image_path[(len(self.image_path) - 4):]
        self.image = pygame.image.load(path)

    def __init__(self, x, y, image_path, side, walls, player):
        pygame.sprite.Sprite.__init__(self)
        self.image_path = image_path
        self.side = side
        self.rotate_image(self.side)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = 0
        self.change_y = 0
        self.walls = walls
        self.player = player

    def bullet_hit_enemy(self):
        result = self.bullet.bullet_hit_enemy(self.enemies)
        if result is not None:
            self.score += 1
        return result

    def bullet_hit_wall(self):
        return self.bullet.bullet_hit_wall(self.walls)

    def fire(self):
        self.bullet = Bullet(pygame.image.load(ImagePath.PATH + 'bullet.png'), self.side, self.walls, self.rect.x, self.rect.y)

    def change_side(self, side):
        self.side = side
        self.rotate_image(self.side)

    def change_x_coordinate(self, x):
        self.change_x += x
        self.change_y = 0
        if x > 0:
            self.change_side(Side.right)
            return
        self.change_side(Side.left)

    def change_y_coordinate(self, y):
        self.change_y += y
        self.change_x = 0
        if y > 0:
            self.change_side(Side.down)
            return
        self.change_side(Side.up)

    def update(self):
        self.rect.x += self.change_x
        objects = []
        objects += self.walls
        objects += self.enemies
        block_hit_list = pygame.sprite.spritecollide(self, objects, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            else:
                self.rect.left = block.rect.right

        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, objects, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            else:
                self.rect.top = block.rect.bottom
