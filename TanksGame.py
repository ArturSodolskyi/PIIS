import pygame
import random
from Entities.tank import Tank
from Entities.brick_wall import BrickWall
from Entities.side import Side
from Entities.wall import Wall
from assets.path import ImagePath
from queue import Queue
from console import Console


TILE = 32
COLS, ROWS = 25, 20

SCREEN_HEIGHT = TILE * ROWS
SCREEN_WIDTH = TILE * COLS

ENEMIES_COUNT = 2
DELAY_TICKS = 50
PLAYER_IMAGE = 'player.png'
ENEMY_IMAGE = 'enemy.png'
MAX_BULLET_DELAY = 200
BULLET_DELAY = 0

screen = None
all_sprite_list = pygame.sprite.Group()
walls_and_players = pygame.sprite.Group()
walls = pygame.sprite.Group()
players = pygame.sprite.Group()
enemies = pygame.sprite.Group()
wallImage = pygame.image.load(ImagePath.PATH + BrickWall.name)
clock = pygame.time.Clock()
grid = None
graph = {}
player = None
tanks = []
FONT = ''

increasePLayerSpeed = False
increasePlayerBulletSpeed = False
decreaseEnemiesSpeed = False
decreaseEnemiesBulletSpeed = False
playerIsImmortal = False
xTwoScore = False
enemiesWithoutBullets = False
stopAllEnemies = False

def get_rect(x, y):
    return x * TILE + 1, y * TILE + 1, TILE, TILE


def get_next_nodes(x, y):
    check_next_node = lambda x, y: True if 0 <= x < COLS and 0 <= y < ROWS and not grid[y][x] else False
    ways = [-1, 0], [0, -1], [1, 0], [0, 1]
    return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]


def create_tank(image_path, player):
    while True:
        x = random.randint(0, SCREEN_WIDTH - BrickWall.width)
        y = random.randint(0, SCREEN_HEIGHT - BrickWall.height)
        tank = Tank(x, y, image_path, Side.up, walls, player)
        collisions = pygame.sprite.spritecollide(tank, all_sprite_list, False)
        if not any(collisions):
            return tank


def resetGlobals():
    global grid, walls, wallImage, TILE, graph, all_sprite_list, walls_and_players, player, players, tanks, enemies, \
        clock, playerIsImmortal, xTwoScore, enemiesWithoutBullets, stopAllEnemies
    all_sprite_list = pygame.sprite.Group()
    walls_and_players = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    wallImage = pygame.image.load(ImagePath.PATH + BrickWall.name)
    clock = pygame.time.Clock()
    grid = None
    graph = {}
    player = None
    tanks = []
    playerIsImmortal = False
    xTwoScore = False
    enemiesWithoutBullets = False
    stopAllEnemies = False
    onInit()


def onInit():
    global grid, walls, wallImage, TILE, graph, all_sprite_list, walls_and_players, player, players, tanks, enemies, \
        FONT, screen

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    FONT = pygame.font.Font('freesansbold.ttf', 108)
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

    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            if not col:
                graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(x, y)

    all_sprite_list.add(walls)
    walls_and_players.add(walls)

    player = create_tank(ImagePath.PATH + PLAYER_IMAGE, True)
    players.add(player)
    all_sprite_list.add(players)
    walls_and_players.add(players)

    for i in range(ENEMIES_COUNT):
        enemy = create_tank(ImagePath.PATH + ENEMY_IMAGE, False)
        enemy.enemies = players
        enemies.add(enemy)
        all_sprite_list.add(enemy)

    player.enemies = enemies

    tanks += players
    tanks += enemies


def tank_fire(tank):
    tank.fire()
    all_sprite_list.add(tank.bullet)


def remove_bullet(tank):
    all_sprite_list.remove(player.bullet)
    tank.bullet = None


def check_enemy_kill(tank, game):
    if tank.bullet:
        enemy = tank.bullet_hit_enemy()
        if enemy is not None:
            if enemy.player is False or enemy.player is True and playerIsImmortal is False:
                enemies.remove(enemy)
                players.remove(enemy)
                all_sprite_list.remove(enemy)
                remove_bullet(tank)
                if tank.player is True:
                    value = 2 if xTwoScore is True else 1
                    game.score += value
                return
        result = tank.bullet_hit_wall()
        if result:
            remove_bullet(tank)


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


def opponentsMove(enemies):
    for tank in enemies:
        if not tank.bullet and enemiesWithoutBullets is False:
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
                path = a_start(graph, tank_start_point, tank.goal)
                path.pop(0)
                tank.movements = get_movements_by_path((tank.rect.x, tank.rect.y), path)
            if tank.movements.queue:
                move_tank_by_movements(tank)


def handleTanksBullets(game):
    for tank in game.tanks:
        if tank.bullet and not tank.bullet.fired:
            game.all_sprite_list.remove(tank.bullet)
            tank.bullet = None
        check_enemy_kill(tank, game)


def checkWinOrLoss(game):
    if not any(game.enemies):
        game.win = True
    if not any(players):
        game.win = False


def readPlayerMovementsEvents(events, player, console):
    for event in events:
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

            if event.key == pygame.K_k and pygame.KMOD_LCTRL:
                console.showConsole()


def updateDisplay(all_sprite_list):
    all_sprite_list.update()
    screen.fill(pygame.Color('white'))
    all_sprite_list.draw(screen)
    pygame.display.flip()
    clock.tick(DELAY_TICKS)


def showResult(game):
    end = False
    while not end:
        score = FONT.render("Score : " + str(game.score), True, pygame.Color('white'))
        screen.fill(pygame.Color('black'))
        screen.blit(score, (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                end = True


class Game:
    def __init__(self):
        pygame.init()
        onInit()
        self.score = 0
        self.time = 0
        self.win = None
        self.all_sprite_list = all_sprite_list
        self.player = player
        self.players = players
        self.enemies = enemies
        self.tanks = tanks
        self.console = Console(screen, self.all_sprite_list, self)

    def InitialDisplay(self):
        all_sprite_list.update()
        screen.fill(pygame.Color('white'))
        all_sprite_list.draw(screen)
        pygame.display.flip()
        clock.tick(DELAY_TICKS)

    def PlayNextMove(self):
        readPlayerMovementsEvents(pygame.event.get(), self.player, self.console)
        if stopAllEnemies is False:
            opponentsMove(self.enemies)
        updateDisplay(self.all_sprite_list)
        handleTanksBullets(self)
        checkWinOrLoss(self)

    def Start(self):
        self.InitialDisplay()

        running = True
        while running:
            self.PlayNextMove()
            if self.win is not None:
                showResult(self)
                self.Restart()

    def Restart(self):
        resetGlobals()
        self.score = 0
        self.time = 0
        self.win = None
        self.all_sprite_list = all_sprite_list
        self.player = player
        self.players = players
        self.enemies = enemies
        self.tanks = tanks
        self.console = Console(screen, self.all_sprite_list, self)

    def decreaseEnemiesBulletsSpeed(self):
        global decreaseEnemiesBulletSpeed
        decreaseEnemiesBulletSpeed = not decreaseEnemiesBulletSpeed
        value = 2 if decreaseEnemiesBulletSpeed is True \
            else 3
        for enemy in enemies:
            enemy.bullet_speed = value

        return 'Enemies speed was reduced' if decreaseEnemiesBulletSpeed is True      \
            else 'Enemies speed was set to default'

    def decreaseEnemiesSpeed(self):
        global decreaseEnemiesSpeed
        decreaseEnemiesSpeed = not decreaseEnemiesSpeed
        value = 1 if decreaseEnemiesSpeed is True \
            else 2
        for enemy in enemies:
            print(enemy.speed)
            enemy.speed = value
            print(enemy.speed)

        return 'Enemies bullet speed was reduced' if decreaseEnemiesSpeed is True \
            else 'Enemies bullet speed was set to default'

    def increasePlayerSpeed(self):
        global increasePLayerSpeed
        increasePLayerSpeed = not increasePLayerSpeed
        value = 3 if increasePLayerSpeed is True else 2
        player.speed = value
        return 'Player speed was increased' if increasePLayerSpeed is True \
            else 'Player speed was set to default'

    def increasePlayerBulletsSpeed(self):
        global increasePlayerBulletSpeed
        increasePlayerBulletSpeed = not increasePlayerBulletSpeed
        value = 5 if increasePlayerBulletSpeed is True else 3
        player.bullet_speed = value
        return 'Player bullet speed was increased' if increasePlayerBulletSpeed is True \
            else 'Player bullet speed was set to default'

    def xTwoScore(self):
        global xTwoScore
        xTwoScore = not xTwoScore
        return 'X2 Score: ON' if xTwoScore is True \
            else 'X2 Score: OFF'

    def immortalMode(self):
        global playerIsImmortal
        playerIsImmortal = not playerIsImmortal
        return 'Immortal Mode: ON' if playerIsImmortal is True \
            else 'Immortal Mode: OFF'

    def enemiesWithoutBullets(self):
        global enemiesWithoutBullets
        enemiesWithoutBullets = not enemiesWithoutBullets
        return 'Enemies without bullets: ON' if enemiesWithoutBullets is True \
            else 'Enemies without bullets: OFF'

    def stopAllEnemies(self):
        global stopAllEnemies
        stopAllEnemies = not stopAllEnemies
        if stopAllEnemies is True:
            for enemy in enemies:
                enemy.change_x = 0
                enemy.change_y = 0
        return 'All enemies were stopped' if stopAllEnemies is True \
            else 'Enemies can move'


game = Game()
while True:
    game.Start()
