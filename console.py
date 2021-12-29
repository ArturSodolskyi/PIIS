import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WIDTH = 800
HEIGHT = 640
WHITE_SURFACE = pygame.Surface((WIDTH, HEIGHT))
WHITE_SURFACE.fill(WHITE)


class Console:

    def __init__(self, screen, all_sprite_list, game):
        self.console_remind = []
        self.console_text = []
        self.showAvailableCommands()
        self.screen = screen
        self.all_sprite_list = all_sprite_list
        self.game = game

    def showAvailableCommands(self):
        self.console_text.append(('Commands:', BLACK))
        self.console_text.append(('"des" - to decrease/increase enemies speed', BLACK))
        self.console_text.append(('"debs" - to to decrease/increase enemies bullet speed', BLACK))
        self.console_text.append(('"ips" - to increase player speed', BLACK))
        self.console_text.append(('"ipbs" - to increase/decrease player bullet speed', BLACK))
        self.console_text.append(('"im" - to enable/disable immortal mode', BLACK))
        self.console_text.append(('"ewb" - to enable/disable enemies without bullets mode', BLACK))
        self.console_text.append(('"x2" - to enable/disable x2 score mode', BLACK))
        self.console_text.append(('"se" - to enable/disable enemies movements', BLACK))
        self.console_text.append(('"god mode" - to enable/disable god mode', BLACK))
        self.console_text.append(('"help" - show all available commands', BLACK))

    def showConsole(self):

        def printText(text, id):
            if not text == "":
                text_surf = font.render(text, True, BLACK)
                text_rect = text_surf.get_rect()
                text_rect.left = 10
                text_rect.top = id * 20
                self.screen.blit(text_surf, text_rect)
                self.screen.blit(text_surf, text_rect)

        wheel = False
        wheel_count = 0
        el_number = self.console_remind.__len__()
        clock = pygame.time.Clock()
        font = pygame.font.Font('freesansbold.ttf', 20)
        text = ''

        while True:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        return
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:
                        wheel = True
                        if 29 - wheel_count >= 1:
                            wheel_count += 1
                    elif event.button == 5:
                        if wheel_count >= 1:
                            wheel = True
                            wheel_count -= 1
                        else:
                            wheel = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if el_number > 0:
                            el_number -= 1
                            text = ''
                            text += self.console_remind[el_number]

                    if event.key == pygame.K_DOWN:
                        if el_number < self.console_remind.__len__() - 1:
                            el_number += 1
                            text = ''
                            text += self.console_remind[el_number]
                    if event.key == pygame.K_RETURN:
                        if not text == '':
                            self.console_text.append((text, BLACK))
                            self.console_remind.append(text)
                            el_number = self.console_remind.__len__()
                        if text == 'des':
                            message = self.game.decreaseEnemiesSpeed()
                            self.console_text.append((message, GREEN))
                        elif text == 'debs':
                            message = self.game.decreaseEnemiesBulletsSpeed()
                            self.console_text.append((message, GREEN))
                        elif text == 'ips':
                            message = self.game.increasePlayerSpeed()
                            self.console_text.append((message, GREEN))
                        elif text == 'ipbs':
                            message = self.game.increasePlayerBulletsSpeed()
                            self.console_text.append((message, GREEN))
                        elif text == 'im':
                            message = self.game.immortalMode()
                            self.console_text.append((message, GREEN))
                        elif text == 'ewb':
                            message = self.game.enemiesWithoutBullets()
                            self.console_text.append((message, GREEN))
                        elif text == 'x2':
                            message = self.game.xTwoScore()
                            self.console_text.append((message, GREEN))
                        elif text == 'se':
                            message = self.game.stopAllEnemies()
                            self.console_text.append((message, GREEN))
                        elif text == 'god mode':
                            message = self.game.immortalMode()
                            self.console_text.append((message, GREEN))
                            message = self.game.increasePlayerSpeed()
                            self.console_text.append((message, GREEN))
                            message = self.game.increasePlayerBulletsSpeed()
                            self.console_text.append((message, GREEN))
                        elif text == 'help':
                            self.showAvailableCommands()
                        else:
                            self.console_text.append(('Unknown command. Try to use "help"', RED))
                        wheel = False
                        wheel_count = 0

                        text = ''

                    elif event.key == pygame.K_BACKSPACE:
                        wheel = False
                        wheel_count = 0
                        text = text[:-1]
                    else:
                        wheel = False
                        wheel_count = 0
                        if text.__len__() < 60:
                            text += event.unicode

                self.all_sprite_list.draw(self.screen)
                self.screen.blit(WHITE_SURFACE, WHITE_SURFACE.get_rect())

                counter = 0
                if self.console_text.__len__() < 30:
                    for line in self.console_text:
                        line_surf = font.render(line.__getitem__(0), True, line.__getitem__(1))
                        line_rect = line_surf.get_rect()
                        line_rect.left = 10
                        line_rect.top = counter * 20
                        self.screen.blit(line_surf, line_rect)
                        counter += 1
                    printText(text, counter)
                else:
                    i = self.console_text.__len__() - 30
                    j = self.console_text.__len__()
                    if wheel:
                        if wheel_count > 0:
                            i -= wheel_count
                            j = i + 30
                        elif wheel_count < 0:
                            i += wheel_count
                            j = i + 30
                    while (i < j):
                        obj = self.console_text[i]
                        line_surf = font.render(obj.__getitem__(0), True, obj.__getitem__(1))
                        line_rect = line_surf.get_rect()
                        line_rect.left = 10
                        line_rect.top = counter * 20
                        self.screen.blit(line_surf, line_rect)
                        counter += 1
                        i += 1
                    if not wheel:
                        printText(text, counter)

                pygame.display.flip()
