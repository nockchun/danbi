from typing import Callable
import pandas as pd

from .TradeSingleEnv import TradeSingleEnv
from .trade import ACT


def simStockTrade(df: pd.DataFrame, policy: Callable, kwarg: dict = {}, windos: int = 26, future=26, trade_amount=10):
    env: TradeSingleEnv = TradeSingleEnv(df, windos, future, trade_amount)
    
    state = env.reset()
    state, reward, done, info = env.step(ACT.HOLD)
    while not done:
        future = info["future"]
        hold_price = info["hold_price"]
        hold_amount = info["hold_amount"]
        hold_duration = info["hold_duration"]
        invest_max = info["invest_max"]
        action = policy(state, future, hold_price, hold_amount, hold_duration, invest_max, **kwarg)
        state, reward, done, info = env.step(action)
        
    return env
