import TanksGame
import MyAgent
import numpy as np
import random
import matplotlib.pyplot as plt
import pygame
import logging

ACTIONS = 5
STATECOUNT = 10
TOTAL_GAMETIME = 150
logging.basicConfig(filename="sample.log", level=logging.INFO)

def CaptureNormalisedState(PlayerXPos, PlayerYPos, EnemiesPos):
    gstate = np.zeros([STATECOUNT])
    gstate[0] = PlayerXPos
    gstate[1] = PlayerYPos

    i = 2
    for pos in EnemiesPos:
        gstate[i] = pos[0]
        gstate[i + 1] = pos[1]
        i += 2
    return gstate


def loop(game, agent, game_state, game_history, gamesCount):
    game.InitialDisplay()

    iteration = 0
    while True:
        BestAction = agent.Act(game_state)
        score, player_x, player_y, enemies_pos = game.PlayNextMove(BestAction)
        NextState = CaptureNormalisedState(player_x, player_y, enemies_pos)
        agent.CaptureSample((game_state, BestAction, score, NextState))
        agent.Process()
        game_state = NextState

        if game.win is not None or iteration == 150:
            logging.info(f'{gamesCount}, {score}')
            game_history.append((gamesCount, score))
            break
        iteration += 1

    return game_history


def PlayExperiment(TheGame, GameHistory, TheAgent, gamesCount):

    GameState = CaptureNormalisedState(TheGame.player.rect.x, TheGame.player.rect.y, TheGame.getEmeniesPos())

    history = loop(TheGame, TheAgent, GameState, GameHistory, gamesCount)

    x_val = [x[0] for x in history]
    y_val = [x[1] for x in history]

    plt.plot(x_val, y_val)
    plt.xlabel("Games")
    plt.ylabel("Score")
    plt.show()


def main():
    TheGame = TanksGame.Game()
    TheAgent = MyAgent.Agent(STATECOUNT, ACTIONS)
    GameHistory = []
    gamesCount = 0
    count = 0
    while True:
        PlayExperiment(TheGame, GameHistory, TheAgent, gamesCount)
        TheGame.Restart()
        gamesCount += 1
        count += 1
        if count == 10:
            TheAgent.Save()
            count = 0



if __name__ == "__main__":
    main()
