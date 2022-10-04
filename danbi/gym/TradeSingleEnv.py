from gym import Env
from gym.spaces import Discrete, Box
import pandas as pd
import numpy as np
from typing import Tuple
from danbi import analysis as dana

from .trade import ACT


class TradeSingleEnv(Env):
    def __init__(self, df: pd.DataFrame, window: int, future: int = 0, trade_amount: int = 10, trade_fee: float = 0.01):
        # class variables
        self._df = df.reset_index()
        self._size = len(df)
        self._window = window
        self._future = future
        self._trade_amount = trade_amount
        self._trade_fee = trade_fee
        self._buy_price = 0
        self._buy_amount = 0
        self._buy_duration = 0
        self._invest_max = 0
        self._invest_accum = 0
        self._score = 0

        # spaces
        self.action_space = Discrete(len(ACT))
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(window, df.shape[1]), dtype=np.float64)

        # call init function
        self._init(df, window, future)
    
    def getScore(self):
        return self._score

    def getDf(self):
        return self._df
    
    def hasTrade(self):
        return True if self._buy_amount > 0 else False
    
    def getInvestMax(self):
        return self._investment_max
    
    def getBuyDuration(self):
        return self._buy_duration
    
    def getCurrentProfitRate(self):
        if self._buy_amount > 0:
            price_current = self._df.iloc[self._index].close
            earn = round((self._buy_amount * price_current - self._buy_price) / self._buy_price, 2)
            return earn
        
        return 0
    
    def _getCurrent(self):
        return self._df.iloc[self._index]
    
    def _getWindow(self):
        return self._df.iloc[self._index-self._window:self._index].reset_index()

    def _getFuture(self):
        if self._future <= 0:
            return None
        return self._df.iloc[self._index - 1:self._index+self._future - 1].reset_index()

    def step(self, action: ACT) -> Tuple[pd.DataFrame, float, bool, dict]:
        fixed_income = self._trade(action)
        if self.hasTrade():
            self._buy_duration += 1
        self._df.at[self._index, "env_invest"] = self._invest_accum + (self._buy_amount * self._df.iloc[self._index].close - self._buy_price)
        
        reward = self._reward(ACT(action), self._getWindow(), self._getFuture(),  self._buy_duration, self.getCurrentProfitRate(), fixed_income)

        self._index += 1
        self._state = self._getWindow()

        if self._size == self._future + self._index - 1:
            done = True
        else:
            done = False

        info = {
            "future": self._getFuture(),
            "hold_price": self._buy_price,
            "hold_amount": self._buy_amount,
            "hold_duration": self._buy_duration,
            "invest_max": self._investment_max
        }
        self._score += reward

        return (self._state, reward, done, info)
    
    def render(self, mode="human", width: int = 1000, height: int = 500, candle: bool = True, ma: bool = False, vol_ma: bool = False, ichimoku: bool = False):
        if mode == "plot":
            height_up = int(height * 0.15)
            height_dn = int(height * 0.2)
            ds = dana.getBokehDataSource(self._df)
            dana.showAsRows([
                dana.plotTimeseriesLines(ds, width, height_up, ylist=["env_hold"], title="Holding Period"),
                dana.plotCandleBollingerIchimoku(ds, width, height - height_up - height_dn, candle=candle, ma=ma, vol_ma=vol_ma, ichimoku=ichimoku, title=f"Trading History"),
                dana.plotTimeseriesLines(ds, width, height_dn, ylist=["env_invest"], title="Cumulated Profit"),
            ], "x")

    def _trade(self, action: ACT):
        price_current = self._df.iloc[self._index].close
        fixed_income = 0
        if action == ACT.BUY:
            self._buy_amount += self._trade_amount
            self._buy_price += self._trade_amount * price_current
            if self._buy_price > self._invest_max:
                self._invest_max = self._buy_price
            self._df.at[self._index, "env_buy"] = price_current * 0.95
        if action == ACT.SELL:
            if self.hasTrade():
                fixed_income = (self._buy_amount * price_current) - self._buy_price
                self._df.at[self._index, "env_sell"] = price_current * 1.05
                self._df.at[self._index, "env_earn"] = fixed_income
                self._df.at[self._index, "env_hold"] = self._buy_duration
                self._invest_accum += fixed_income
                self._buy_price = 0
                self._buy_amount = 0
                self._buy_duration = 0
            
        return fixed_income

    def reset(self):
        self._df[["env_buy", "env_sell", "env_earn", "env_hold", "env_invest"]] = np.nan, np.nan, np.nan, 0, 0
        self._index = self._window
        self._state = self._getWindow()
        self._buy_price = 0
        self._buy_amount = 0
        self._buy_duration = 0
        self._investment_max = 0
        self._invest_accum = 0
        self._score = 0
        self._init(self._df, self._window, self._future)

        return self._state

    def _init(self, df: pd.DataFrame, window: int, future: int):
        ...

    def _reward(self, action: ACT, df_window: pd.DataFrame, df_future: pd.DataFrame, buy_duration: int, profit_rate: float, fixed_income: int = 0) -> float:
        return fixed_income
