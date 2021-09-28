import pygame
import random
from Entities.tank import Tank
from Entities.brick_wall import BrickWall
from Entities.side import Side
from Entities.wall import Wall
from assets.path import ImagePath

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800

ENEMIES_COUNT = 7
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
DELAY_TICKS = 240
PLAYER_IMAGE = 'player.png'
ENEMY_IMAGE = 'enemy.png'
MAX_BULLET_DELAY = 200
bullet_delay = 0

pygame.init()

FONT = pygame.font.Font('freesansbold.ttf', 108)

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

all_sprite_list = pygame.sprite.Group()
walls_and_players = pygame.sprite.Group()

walls = pygame.sprite.Group()
wallImage = pygame.image.load(ImagePath.PATH + BrickWall.name)


def create_borders():
    for i in range(int(SCREEN_WIDTH / BrickWall.width) + 1):
        walls.add(Wall(i * BrickWall.height, 0, wallImage))
        walls.add(Wall(i * BrickWall.height, SCREEN_HEIGHT - BrickWall.height, wallImage))
    for i in range(int(SCREEN_HEIGHT / BrickWall.height) + 1):
        walls.add(Wall(0, i * BrickWall.width, wallImage))
        walls.add(Wall(SCREEN_WIDTH - BrickWall.width, i * BrickWall.width, wallImage))


def create_obstacles():
    for i in range(3):
        walls.add(Wall(SCREEN_HEIGHT / 4 - i * BrickWall.width, SCREEN_HEIGHT / 2, wallImage))
    for i in range(3):
        walls.add(Wall(SCREEN_HEIGHT + i * BrickWall.width, SCREEN_HEIGHT / 2, wallImage))
    for i in range(9):
        walls.add(Wall(SCREEN_HEIGHT / 4, SCREEN_HEIGHT / 4 + i * BrickWall.width, wallImage))
    for i in range(9):
        walls.add(Wall(SCREEN_HEIGHT, SCREEN_HEIGHT / 4 + i * BrickWall.width, wallImage))
    for i in range(2):
        walls.add(Wall(SCREEN_HEIGHT / 2 + 2.5 * BrickWall.width, BrickWall.width + i * BrickWall.height, wallImage))
    for i in range(2):
        walls.add(Wall(SCREEN_HEIGHT / 2 + 2.5 * BrickWall.width, SCREEN_HEIGHT - 2 * BrickWall.height - i * BrickWall.height, wallImage))
    for i in range(7):
        walls.add(Wall(SCREEN_HEIGHT / 2 + 2.5 * BrickWall.width, SCREEN_HEIGHT / 3 + i * BrickWall.width, wallImage))
    for i in range(9):
        walls.add(Wall(250 + i * BrickWall.width, SCREEN_HEIGHT / 2, wallImage))
    walls.add(Wall(70, 70, wallImage))
    walls.add(Wall(70, SCREEN_HEIGHT - BrickWall.height * 3, wallImage))
    walls.add(Wall(SCREEN_WIDTH - BrickWall.width * 3, 70, wallImage))
    walls.add(Wall(SCREEN_WIDTH - BrickWall.width * 3, SCREEN_HEIGHT - BrickWall.height * 3, wallImage))


def create_walls():
    create_borders()
    create_obstacles()


create_walls()
all_sprite_list.add(walls)
walls_and_players.add(walls)


def create_tank(image_path):
    while True:
        x = random.randint(0, SCREEN_WIDTH - BrickWall.width)
        y = random.randint(0, SCREEN_HEIGHT - BrickWall.height)
        tank = Tank(x, y, image_path, Side.up, walls)
        collisions = pygame.sprite.spritecollide(tank, all_sprite_list, False)
        if not any(collisions):
            return tank


players = pygame.sprite.Group()
player = create_tank(ImagePath.PATH + PLAYER_IMAGE)
players.add(player)
all_sprite_list.add(players)
walls_and_players.add(players)

enemies = pygame.sprite.Group()
for i in range(ENEMIES_COUNT):
    enemy = create_tank(ImagePath.PATH + ENEMY_IMAGE)
    enemy.enemies = players
    enemies.add(enemy)
    all_sprite_list.add(enemy)

player.enemies = enemies

tanks = []
tanks += players
tanks += enemies

clock = pygame.time.Clock()


def restore_coordinates_and_change_side(x_stash, y_stash, side):
    tank.rect.x = x_stash
    tank.rect.y = y_stash
    tank.change_side(side)


def tank_fire(tank):
    tank.fire()
    all_sprite_list.add(tank.bullet)


def enemies_intellect(tank):
    global bullet_delay
    if tank.bullet is None and bullet_delay == MAX_BULLET_DELAY:
        tank_fire(tank)
    old_x = tank.rect.x
    olx_y = tank.rect.y
    if tank.side == Side.up:
        tank.rect.y += -tank.speed
    elif tank.side == Side.down:
        tank.rect.y += tank.speed
    elif tank.side == Side.left:
        tank.rect.x += -tank.speed
    elif tank.side == Side.right:
        tank.rect.x += tank.speed
    collisions = pygame.sprite.spritecollide(tank, walls_and_players, False)
    if any(collisions):
        loop_count = 0
        while True:
            if tank.side == Side.up:
                restore_coordinates_and_change_side(old_x, olx_y, Side.right)
                tank.rect.x += tank.speed
            elif tank.side == Side.right:
                restore_coordinates_and_change_side(old_x, olx_y, Side.down)
                tank.rect.y += tank.speed
            elif tank.side == Side.down:
                restore_coordinates_and_change_side(old_x, olx_y, Side.left)
                tank.rect.x += -tank.speed
            else:
                restore_coordinates_and_change_side(old_x, olx_y, Side.up)
                tank.rect.y += -tank.speed
            if loop_count < 2:
                loop_count += 1
            else:
                return
            collisions = pygame.sprite.spritecollide(tank, walls_and_players, False)
            if not any(collisions):
                return


def remove_bullet(tank):
    all_sprite_list.remove(player.bullet)
    tank.bullet = None


def check_enemy_kill(tank):
    if tank.bullet:
        enemy = tank.bullet_hit_enemy()
        if enemy is not None:
            enemies.remove(enemy)
            players.remove(enemy)
            all_sprite_list.remove(enemy)
            remove_bullet(tank)
        else:
            result = tank.bullet_hit_wall()
            if result:
                remove_bullet(tank)


running = True
end = False


def end_game():
    global running, end
    while not end:
        score = FONT.render("Score : " + str(player.score), True, WHITE_COLOR)
        screen.fill(BLACK_COLOR)
        screen.blit(score, (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5))
        pygame.display.update()
        running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                end = True


while running:
    for tank in tanks:
        if tank.bullet and not tank.bullet.fired:
            all_sprite_list.remove(tank.bullet)
            tank.bullet = None
        check_enemy_kill(tank)

    if not any(enemies) or not any(players):
        end_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.change_x = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player.change_y = 0

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.change_x_coordinate(player.speed)
                elif event.key == pygame.K_LEFT:
                    player.change_x_coordinate(-player.speed)
                elif event.key == pygame.K_UP:
                    player.change_y_coordinate(-player.speed)
                elif event.key == pygame.K_DOWN:
                    player.change_y_coordinate(player.speed)

                if event.key == pygame.K_SPACE and player.bullet is None:
                    tank_fire(player)
    if not end:
        bullet_delay += 1
        for tank in enemies:
            enemies_intellect(tank)
        if bullet_delay == MAX_BULLET_DELAY:
            bullet_delay = 0

        all_sprite_list.update()

        screen.fill(WHITE_COLOR)

        all_sprite_list.draw(screen)

        pygame.display.flip()

        clock.tick(DELAY_TICKS)

pygame.quit()
