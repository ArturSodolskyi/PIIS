import random, numpy, math
from keras.models import Sequential, load_model
from keras.layers import *


class Brain:
    def __init__(self, NbrStates, NbrActions):
        self.NbrStates = NbrStates
        self.NbrActions = NbrActions

        self.model = load_model('dqn10')

    def _createModel(self):
        model = Sequential()

        model.add(Dense(units=64, activation='relu', input_dim=self.NbrStates))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dense(units=self.NbrActions,
                        activation='linear'))

        model.compile(loss='mse', optimizer='adam')

        return model

    def train(self, x, y, epoch=1, verbose=0):
        self.model.fit(x, y, batch_size=64, epochs=epoch, verbose=verbose)

    def predict(self, s):
        return self.model.predict(s)

    def predictOne(self, s):
        return self.predict(s.reshape(1, self.NbrStates)).flatten()

    def save(self):
        self.model.save('dqn10')


class ExpReplay:
    samples = []

    def __init__(self, capacity):
        self.capacity = capacity

    def add(self, sample):
        self.samples.append(sample)

        if len(self.samples) > self.capacity:
            self.samples.pop(0)

    def sample(self, n):
        n = min(n, len(self.samples))
        return random.sample(self.samples, n)


ExpReplay_CAPACITY = 2000
OBSERVEPERIOD = 750
BATCH_SIZE = 128
GAMMA = 0.95
MAX_EPSILON = 1
MIN_EPSILON = 0.05
LAMBDA = 0.0005


# ============================================================================================
class Agent:
    def __init__(self, NbrStates, NbrActions):
        self.NbrStates = NbrStates
        self.NbrActions = NbrActions

        self.brain = Brain(NbrStates, NbrActions)
        self.ExpReplay = ExpReplay(ExpReplay_CAPACITY)
        self.steps = 0
        self.epsilon = MAX_EPSILON

    def Save(self):
        self.brain.save()

    def Act(self, s):
        if (random.random() < self.epsilon or self.steps < OBSERVEPERIOD):
            return random.randint(0, self.NbrActions - 1)
        else:
            return numpy.argmax(self.brain.predictOne(s))

    def CaptureSample(self, sample):
        self.ExpReplay.add(sample)

        self.steps += 1
        if (self.steps > OBSERVEPERIOD):
            self.epsilon = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * math.exp(-LAMBDA * (self.steps - OBSERVEPERIOD))

    def Process(self):
        batch = self.ExpReplay.sample(BATCH_SIZE)
        batchLen = len(batch)

        no_state = numpy.zeros(self.NbrStates)

        states = numpy.array([batchitem[0] for batchitem in batch])
        states_ = numpy.array([(no_state if batchitem[3] is None else batchitem[3]) for batchitem in batch])

        predictedQ = self.brain.predict(states)
        predictedNextQ = self.brain.predict(states_)

        x = numpy.zeros((batchLen, self.NbrStates))
        y = numpy.zeros((batchLen, self.NbrActions))

        for i in range(batchLen):
            batchitem = batch[i]
            state = batchitem[0];
            a = batchitem[1];
            reward = batchitem[2];
            nextstate = batchitem[3]

            targetQ = predictedQ[i]
            if nextstate is None:
                targetQ[a] = reward
            else:
                targetQ[a] = reward + GAMMA * numpy.amax(predictedNextQ[i])

            x[i] = state
            y[i] = targetQ

        self.brain.train(x, y)