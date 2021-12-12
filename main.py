from typing import Any

import pygame
import random
from Entities.tank import Tank
from Entities.brick_wall import BrickWall
from Entities.side import Side
from Entities.wall import Wall
from assets.path import ImagePath
from collections import deque
from queue import Queue
import math
import timeit
import csv

TILE = 32
COLS: Any
COLS, ROWS = 25, 20

SCREEN_HEIGHT = TILE * ROWS
SCREEN_WIDTH = TILE * COLS

ENEMIES_COUNT = 2
DELAY_TICKS = 1000000
PLAYER_IMAGE = 'player.png'
ENEMY_IMAGE = 'enemy.png'
MAX_BULLET_DELAY = 200
BULLET_DELAY = 0
Z_KEY = 122

playerAlgorithm = 'minimax'
algNumber = 5

INFINITY = 1000000000

for i in range(50):
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


    def enemies_intellect(tank):
        global BULLET_DELAY
        if tank.bullet is None and BULLET_DELAY == MAX_BULLET_DELAY:
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

    alg = True


    def saveStatistic(score, time):
        winOrLoss = int(ENEMIES_COUNT == score)
        file = open('Statistics/statistics.csv', 'a', newline='')
        writer = csv.writer(file)
        writer.writerow([str(winOrLoss), str(time), str(score), algNumber])
        file.close()


    def end_game():
        global running, end, start

        stop = timeit.default_timer()
        gameTime = stop - start

        saveStatistic(player.score, gameTime)

        while not end:
            score = FONT.render("Score : " + str(player.score), True, pygame.Color('white'))
            screen.fill(pygame.Color('black'))
            screen.blit(score, (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2.5))
            pygame.display.update()
            running = False
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            end = True


    def get_element_pos(x, y):
        grid_x, grid_y = x // TILE, y // TILE
        return grid_x, grid_y


    def bfs(graph, start, goal):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break

            next_nodes = graph[cur_node]
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited


    def ucs(graph, start, goal):
        visited = set()
        queue = Queue()
        queue.put((start, [start]))

        while queue:
            (cur_node, path) = queue.get()
            if cur_node not in visited:
                visited.add(cur_node)

                if cur_node == goal:
                    return path
                next_nodes = graph[cur_node]
                for next_node in next_nodes:
                    if next_node not in visited:
                        queue.put((next_node, path + [next_node]))


    def dfs(graph, start, goal):
        stack = [(start, [start])]
        visited = set()
        while stack:
            (cur_node, path) = stack.pop()
            if cur_node not in visited:
                if cur_node == goal:
                    return path
                visited.add(cur_node)
                for next_node in graph[cur_node]:
                    stack.append((next_node, path + [next_node]))


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


    def get_and_draw_path(enemy, alg):
        start = get_element_pos(enemy.rect.x, enemy.rect.y)
        goal = get_element_pos(player.rect.x, player.rect.y)
        if alg == 1:
            bfs_visited = bfs(graph, start, goal)
            draw_path_bfs(goal, start, bfs_visited)
        elif alg == 2:
            dfs_path = dfs(graph, start, goal)
            draw_path_dfs_or_ucs(goal, start, dfs_path, 'red')
        else:
            ucs_path = ucs(graph, start, goal)
            draw_path_dfs_or_ucs(goal, start, ucs_path, 'orange')


    def draw_path_bfs(goal, start, visited):
        path_head, path_segment = goal, goal
        while path_segment and path_segment in visited:
            pygame.draw.rect(screen, pygame.Color('green'), get_rect(*path_segment), TILE, border_radius=TILE // 3)
            path_segment = visited[path_segment]
        pygame.draw.rect(screen, pygame.Color('blue'), get_rect(*start), border_radius=TILE // 3)
        pygame.draw.rect(screen, pygame.Color('magenta'), get_rect(*path_head), border_radius=TILE // 3)


    def draw_path_dfs_or_ucs(goal, start, path, color):
        for step in path:
            pygame.draw.rect(screen, pygame.Color(color), get_rect(*step), TILE, border_radius=TILE // 3)
        pygame.draw.rect(screen, pygame.Color('blue'), get_rect(*start), border_radius=TILE // 3)
        pygame.draw.rect(screen, pygame.Color('magenta'), get_rect(*goal), border_radius=TILE // 3)


    def change_alg():
        global alg
        if alg == 3:
            alg = 1
            return
        alg += 1


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


    def get_click_mouse_pos():
        x, y = pygame.mouse.get_pos()
        grid_x, grid_y = x // TILE, y // TILE
        pygame.draw.rect(screen, pygame.Color('red'), get_rect(grid_x, grid_y))
        click = pygame.mouse.get_pressed()
        return (grid_x, grid_y) if click[0] else False


    def getDistance(node1: object, node2: object) -> object:
        y1 = ROWS - node1[1]
        y2 = ROWS - node2[1]
        return math.sqrt(math.pow((node1[0] - node2[0]), 2) + math.pow((y1 - y2), 2))


    def getClosestEnemyCoordsAndDistance(node):
        shortestDistance = INFINITY
        coords = (0, 0)

        for enemy in enemies:
            enemyNode = get_element_pos(enemy.rect.x, enemy.rect.y)
            distance = getDistance(node, enemyNode)
            if distance < shortestDistance:
                shortestDistance = distance
                coords = (enemy.rect.x, enemy.rect.y)
        return coords, shortestDistance


    def getDistanceToClosestEnemy(node):
        if node == player.goal:
            return -INFINITY

        distance = (getClosestEnemyCoordsAndDistance(node))[1]
        return distance
        #  return getDistance(node, player.goal)  # for testing


    def evaluationFunction(node):
        return getDistanceToClosestEnemy(node) * -1


    def minimax(maximizingPlayer, depth, node, alpha, beta):
        if depth == 2:
            return evaluationFunction(node)
        if maximizingPlayer:
            value = -INFINITY
            for child in graph[node]:
                value = max(value, minimax(False, depth, child, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = INFINITY
            for child in graph[node]:
                value = min(value, minimax(True, depth + 1, child, alpha, beta))
                alpha = min(alpha, value)
                if beta <= alpha:
                    break
            return value


    def expectimax(maximizingPlayer, depth, node):
        if depth == 3:
            return evaluationFunction(node)
        if maximizingPlayer:
            return max(expectimax(False, depth, child) for child in graph[node])
        else:
            return sum(expectimax(True, depth + 1, child) for child in graph[node]) / float(len(graph[node]))


    def getOptimalMovements(x, y):
        alpha = -INFINITY
        beta = INFINITY

        node = get_element_pos(x, y)
        scores = []
        if playerAlgorithm == 'minimax':
            scores = [minimax(True, 0, child, alpha, beta) for child in graph[node]]
        else:
            scores = [expectimax(True, 0, child) for child in graph[node]]

        index = scores.index(max(scores))
        optimalNode = (graph[node])[index]

        tankPos = (x, y)
        return get_movements_by_path(tankPos, [optimalNode])


    def get_side_and_move_tank(tank, tank_pos, goal):
        if tank_pos[0] != goal[0] and tank_pos[0] < goal[0]:
            tank.change_x_coordinate(tank.speed)
        elif tank_pos[0] != goal[0] and tank_pos[0] > goal[0]:
            tank.change_x_coordinate(-tank.speed)
        elif tank_pos[1] != goal[1] and tank_pos[1] > goal[1]:
            tank.change_y_coordinate(-tank.speed)
        elif tank_pos[1] != goal[1] and tank_pos[1] < goal[1]:
            tank.change_y_coordinate(tank.speed)


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


    def move_tank_by_path(tank, path):
        global goal, player_path
        tank_pos = get_element_pos(tank.rect.x, tank.rect.y)
        if tank_pos == goal:
            goal = None
            player_path = None
            player.change_x = 0
            player.change_y = 0
            return

        index = 0
        for node in path:
            if node == tank_pos:
                get_side_and_move_tank(tank, tank_pos, path[index + 1])
                return
            index += 1


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


    def random_point():
        rand_y = random.randint(0, COLS - 1)
        rand_x = random.randint(0, ROWS - 1)
        if grid[rand_x][rand_y] == 0:
            return (rand_x, rand_y)
        else:
            random_point()


    start = timeit.default_timer()

    while running:
        for tank in tanks:
            if tank.bullet and not tank.bullet.fired:
                all_sprite_list.remove(tank.bullet)
                tank.bullet = None
            check_enemy_kill(tank)

            if not tank.bullet:
                forward_nodes = get_forward_nodes_by_side(tank)
                if check_enemy_in_forward_nodes(forward_nodes, tank.enemies):
                    tank_fire(tank)

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

                    if event.key == Z_KEY:
                        change_alg()

                    if event.key == pygame.K_SPACE and player.bullet is None:
                        tank_fire(player)
        if not end:
            BULLET_DELAY += 1
            # for tank in enemies:
            #     enemies_intellect(tank)
            if BULLET_DELAY == MAX_BULLET_DELAY:
                BULLET_DELAY = 0

            all_sprite_list.update()

            screen.fill(pygame.Color('white'))

            mouse_pos = get_click_mouse_pos()
            if mouse_pos:
                player.goal = mouse_pos

            for tank in players:
                if tank.movements:
                    tank.change_x = 0
                    tank.change_y = 0

                if tank.movements and not tank.movements.queue:
                    tank.goal = None
                    tank.movements = None

                tankPos = (tank.rect.x, tank.rect.y)
                tankPosInGrid = get_element_pos(tankPos[0], tankPos[1])

                if playerAlgorithm != 'minimax' and playerAlgorithm != 'expectimax':
                    coords = (getClosestEnemyCoordsAndDistance(tankPosInGrid))[0]
                    enemyPos = get_element_pos(coords[0], coords[1])
                    if enemyPos != tank.goal:
                        tank.goal = enemyPos
                        tank.movements = None

                if tank.movements is None:
                    if playerAlgorithm == 'minimax' or playerAlgorithm == 'expectimax':
                        tank.movements = getOptimalMovements(tankPos[0], tankPos[1])
                    elif playerAlgorithm == 'bfs':
                        path = bfs(graph, tankPosInGrid, tank.goal)
                        del path[tankPosInGrid]
                        tank.movements = get_movements_by_path(tankPos, path)
                    elif playerAlgorithm == 'dfs':
                        path = dfs(graph, tankPosInGrid, tank.goal)
                        tank.movements = get_movements_by_path(tankPos, path)
                    elif playerAlgorithm == 'ucs':
                        path = ucs(graph, tankPosInGrid, tank.goal)
                        path.pop(0)
                        tank.movements = get_movements_by_path(tankPos, path)
                    else:
                        path = a_start(graph, tankPosInGrid, tank.goal)
                        tank.movements = get_movements_by_path(tankPos, path)
                if tank.movements.queue:
                    move_tank_by_movements(tank)

            for tank in enemies:
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
                        path = ucs(graph, tank_start_point, tank.goal)
                        path.pop(0)
                        tank.movements = get_movements_by_path((tank.rect.x, tank.rect.y), path)
                    if tank.movements.queue:
                        move_tank_by_movements(tank)

            all_sprite_list.draw(screen)

            pygame.display.flip()

            clock.tick(DELAY_TICKS)

pygame.quit()