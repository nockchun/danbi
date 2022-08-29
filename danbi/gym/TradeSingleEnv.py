from gym import Env
from gym.spaces import Discrete, Box
import pandas as pd
import numpy as np
from typing import Tuple

from .trade import ACT


class TradeSingleEnv(Env):
    def __init__(self, df: pd.DataFrame, window: int, future: int = 0):
        # class variables
        self._df = df.reset_index()
        self._size = len(df)
        self._window = window
        self._future = future

        # spaces
        self.action_space = Discrete(len(ACT))
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(window, df.shape[1]), dtype=np.float64)

        # call init function
        self._init(df, window, future)

    def _getWindow(self):
        return self._df.iloc[self._index-self._window:self._index].reset_index()

    def _getFuture(self):
        if self._future <= 0:
            return None
        return self._df.iloc[self._index - 1:self._index+self._future - 1].reset_index()

    def step(self, action: ACT) -> Tuple[pd.DataFrame, float, bool, dict]:
        reward = self._reward(ACT(action), self._getWindow(), self._getFuture())

        self._index += 1
        self._state = self._getWindow()

        if self._size == self._future + self._index - 1:
            done = True
        else:
            done = False

        info = {}

        return (self._state, reward, done, info)

    def render(self, mode='human'):
        ...

    def reset(self):
        self._index = self._window
        self._state = self._getWindow()
        self._init(self._df, self._window, self._future)

        return self._state

    def _init(self, df: pd.DataFrame, window: int, future: int):
        ...

    def _reward(self, action: ACT, df_window: pd.DataFrame, df_future: pd.DataFrame) -> float:
        return 0
