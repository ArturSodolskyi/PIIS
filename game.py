import pygame
import random
from Entities.tank import Tank
from Entities.brick_wall import BrickWall
from Entities.side import Side
from Entities.wall import Wall
from assets.path import ImagePath
from queue import Queue

TILE = 32
COLS, ROWS = 25, 20

SCREEN_HEIGHT = TILE * ROWS
SCREEN_WIDTH = TILE * COLS

ENEMIES_COUNT = 1
DELAY_TICKS = 1000000
PLAYER_IMAGE = 'player.png'
ENEMY_IMAGE = 'enemy.png'
MAX_BULLET_DELAY = 200
BULLET_DELAY = 0

pygame.init()

FONT = pygame.font.Font('freesansbold.ttf', 108)

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

all_sprite_list = pygame.sprite.Group()
walls_and_players = pygame.sprite.Group()

walls = pygame.sprite.Group()
wallImage = pygame.image.load(ImagePath.PATH + BrickWall.name)


def get_rect(x, y):
    return x * TILE + 1, y * TILE + 1, TILE, TILE


def get_next_nodes(x, y):
    check_next_node = lambda x, y: True if 0 <= x < COLS and 0 <= y < ROWS and not grid[y][x] else False
    ways = [-1, 0], [0, -1], [1, 0], [0, 1]
    return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]


grid = list(map(lambda line: list(
    map(lambda x: int(x), line[:-1])), open('defaultMap.txt', 'r')))

x_index = 0
for x in grid:
    y_index = 0
    for y in x:
        if y == 1:
            walls.add(Wall(y_index * TILE, x_index * TILE, wallImage))
        y_index += 1
    x_index += 1

graph = {}
for y, row in enumerate(grid):
    for x, col in enumerate(row):
        if not col:
            graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(x, y)

all_sprite_list.add(walls)
walls_and_players.add(walls)


def create_tank(image_path, player):
    while True:
        x = random.randint(0, SCREEN_WIDTH - BrickWall.width)
        y = random.randint(0, SCREEN_HEIGHT - BrickWall.height)
        tank = Tank(x, y, image_path, Side.up, walls, player)
        collisions = pygame.sprite.spritecollide(tank, all_sprite_list, False)
        if not any(collisions):
            return tank


players = pygame.sprite.Group()
player = create_tank(ImagePath.PATH + PLAYER_IMAGE, True)
players.add(player)
all_sprite_list.add(players)
walls_and_players.add(players)

enemies = pygame.sprite.Group()
for i in range(ENEMIES_COUNT):
    enemy = create_tank(ImagePath.PATH + ENEMY_IMAGE, False)
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
        score = FONT.render("Score : " + str(player.score), True, pygame.Color('white'))
        screen.fill(pygame.Color('black'))
        screen.blit(score, (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5))
        pygame.display.update()
        running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                end = True


def get_element_pos(x, y):
    grid_x, grid_y = x // TILE, y // TILE
    return grid_x, grid_y


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_a_star_path(visited, goal):
    path = []
    path_head, path_segment = goal, goal
    while path_segment and path_segment in visited:
        path.append(path_segment)
        path_segment = visited[path_segment]
    return path[::-1]


def a_start(graph, start, goal):
    queue = Queue()
    queue.put((0, start))
    cost_visited = {start: 0}
    visited = {start: None}

    while queue:
        cur_cost, cur_node = queue.get()
        if cur_node == goal:
            break

        next_nodes = graph[cur_node]
        for next_node in next_nodes:
            new_cost = cost_visited[cur_node] + 1

            if next_node not in cost_visited or new_cost < cost_visited[next_node]:
                priority = new_cost + heuristic(next_node, goal)
                queue.put((priority, next_node))
                cost_visited[next_node] = new_cost
                visited[next_node] = cur_node
    return get_a_star_path(visited, goal)


def get_movements_by_path(tank_pos, path):
    queue = Queue()
    for node in path:
        x = node[0] * TILE
        y = node[1] * TILE
        x_diff = x - tank_pos[0]
        y_diff = y - tank_pos[1]
        if x_diff > 0:
            for i in range(abs(x_diff)):
                queue.put(Side.right)
        else:
            for i in range(abs(x_diff)):
                queue.put(Side.left)

        if y_diff < 0:
            for i in range(abs(y_diff)):
                queue.put(Side.up)
        else:
            for i in range(abs(y_diff)):
                queue.put(Side.down)
        tank_pos = (x, y)
    return queue


def move_tank_by_movements(tank):
    movement = tank.movements.get()
    if movement == Side.right:
        tank.change_x_coordinate(tank.speed)
    elif movement == Side.left:
        tank.change_x_coordinate(-tank.speed)
    elif movement == Side.up:
        tank.change_y_coordinate(-tank.speed)
    elif movement == Side.down:
        tank.change_y_coordinate(tank.speed)


def get_forward_nodes_by_side(tank):
    forward_nodes = []
    tank_pos = get_element_pos(tank.rect.x, tank.rect.y)
    if tank.side == Side.right:
        for i in range(COLS - tank_pos[0]):
            if grid[tank_pos[1]][tank_pos[0] + i] == 1:
                break
            else:
                forward_nodes.append((tank_pos[0] + i, tank_pos[1]))
    elif tank.side == Side.left:
        for i in range(tank_pos[0]):
            if grid[tank_pos[1]][tank_pos[0] - i] == 1:
                break
            else:
                forward_nodes.append((tank_pos[0] - i, tank_pos[1]))
    elif tank.side == Side.up:
        for i in range(tank_pos[1]):
            if grid[tank_pos[1] - i][tank_pos[0]] == 1:
                break
            else:
                forward_nodes.append((tank_pos[0], tank_pos[1] - i))
    elif tank.side == Side.down:
        for i in range(ROWS - tank_pos[1]):
            if grid[tank_pos[1] + i][tank_pos[0]] == 1:
                break
            else:
                forward_nodes.append((tank_pos[0], tank_pos[1] + i))
    return forward_nodes


def check_enemy_in_forward_nodes(forward_nodes, enemies):
    for enemy in enemies:
        tank_pos = get_element_pos(enemy.rect.x, enemy.rect.y)
        for node in forward_nodes:
            if node == tank_pos:
                return True
    return False


def moveBySide(side):
    if side == Side.right:
        player.change_x_coordinate(player.speed)
    elif side == Side.left:
        player.change_x_coordinate(-player.speed)
    elif side == Side.up:
        player.change_y_coordinate(-player.speed)
    elif side == Side.down:
        player.change_y_coordinate(player.speed)


def OpponentsMove():
    for tank in enemies:
        if not tank.bullet:
            forward_nodes = get_forward_nodes_by_side(tank)
            if check_enemy_in_forward_nodes(forward_nodes, tank.enemies):
                tank_fire(tank)

        if tank.movements:
            tank.change_x = 0
            tank.change_y = 0

        if tank.movements and not tank.movements.queue:
            tank.goal = None
            tank.movements = None

        if tank.goal != get_element_pos(player.rect.x, player.rect.y):
            tank.goal = get_element_pos(player.rect.x, player.rect.y)
            tank.movements = None

        if tank.goal is not None:
            if tank.movements is None:
                tank_start_point = get_element_pos(tank.rect.x, tank.rect.y)
                path = None
                path = a_start(graph, tank_start_point, tank.goal)
                path.pop(0)
                tank.movements = get_movements_by_path((tank.rect.x, tank.rect.y), path)
            if tank.movements.queue:
                move_tank_by_movements(tank)


def handleTanksBullets():
    for tank in tanks:
        if tank.bullet and not tank.bullet.fired:
            all_sprite_list.remove(tank.bullet)
            tank.bullet = None
        check_enemy_kill(tank)


def checkWinOrLoss():
    if not any(enemies) or not any(players):
        end_game()


def readPlayerMovementsEvents():
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


def executeAction(action):
    if action == 0:
        player.change_x_coordinate(player.speed)
    elif action == 1:
        player.change_x_coordinate(-player.speed)
    elif action == 2:
        player.change_y_coordinate(-player.speed)
    elif action == 3:
        player.change_y_coordinate(player.speed)
    else:
        tank_fire(player)


def updateDisplay():
    all_sprite_list.update()
    screen.fill(pygame.Color('white'))
    all_sprite_list.draw(screen)
    pygame.display.flip()
    clock.tick(DELAY_TICKS)


while running:
    checkWinOrLoss()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            readPlayerMovementsEvents()

    handleTanksBullets()
    # OpponentsMove()

    if not end:
        updateDisplay()

pygame.quit()
