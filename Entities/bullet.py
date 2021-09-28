import pygame
from Entities.side import Side


class Bullet(pygame.sprite.Sprite):
    side = ''
    speed = 5
    fired = True

    def bullet_init(self, x, y):
        if self.side == Side.up:
            self.rect.x = x + 12
            self.rect.y = y - 7
        elif self.side == Side.down:
            self.rect.x = x + 12
            self.rect.y = y + 32
        elif self.side == Side.left:
            self.rect.x = x - 7
            self.rect.y = y + 13
        elif self.side == Side.right:
            self.rect.x = x + 32
            self.rect.y = y + 13

    def __init__(self, image, side, walls, tank_x, tank_y):
        pygame.sprite.Sprite.__init__(self)
        self.side = side
        self.image = image
        self.rect = self.image.get_rect()
        self.bullet_init(tank_x, tank_y)
        self.change_x = 0
        self.change_y = 0
        self.walls = walls

    def move(self):
        if self.side == Side.up:
            self.change_y -= self.speed
        elif self.side == Side.down:
            self.change_y += self.speed
        elif self.side == Side.left:
            self.change_x -= self.speed
        elif self.side == Side.right:
            self.change_x += self.speed

    def bullet_hit_enemy(self, enemies):
        enemies_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        if any(enemies_hit_list):
            return enemies_hit_list[0]
        else:
            return None

    def bullet_hit_wall(self, walls):
        return any(pygame.sprite.spritecollide(self, walls, False))

    def check_collision_update(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
        for block in block_hit_list:
            self.fired = False

    def update(self):
        if self.fired:
            self.move()
            self.rect.x += self.change_x
            self.check_collision_update()
            self.rect.y += self.change_y
            self.check_collision_update()

        self.change_x = 0
        self.change_y = 0
