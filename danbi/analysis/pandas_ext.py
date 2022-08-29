import pandas as pd
import numpy as np
from typing import List, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, window: int, func: Callable):
        results = []
        for rows in self._obj.rolling(window):
            if len(rows) < window:
                continue
            results.append(func(rows))
        if len(results) > 0:
            if isinstance(results[0], tuple):
                results = [[np.nan for _ in range(len(results[0]))] for _ in range(window-1)] + results
            else:
                results = [np.nan for _ in range(window-1)] + results
        
        return results

    def tail(self, offset: int, column: str):
        if offset < self._len:
            return self._obj.iloc[-offset - 1][column]
        else:
            return np.nan
    
    def head(self, offset: int, column: str):
        if offset < self._len:
            return self._obj.iloc[offset][column]
        else:
            return np.nan
    
    def tails(self, period: int, column: str):
        if period < self._len:
            return self._obj.iloc[-period:self._len][column].values
        else:
            return np.nan
    
    def heads(self, period: int, column: str):
        if period < self._len:
            return self._obj.iloc[:period][column].values
        else:
            return np.nan
    
    def isTailInc(self, periods: List[int], column: str, is_all=True):
        values = []
        for period in periods:
            values.append(self.tails(period, column))

        is_incs = []
        for value in values:
            is_incs.append(value[0] < value[-1])

        if is_all:
            return all(is_incs)
        else:
            return any(is_incs)
    
    def isHeadInc(self, periods: List[int], column: str, is_all=True):
        values = []
        for period in periods:
            values.append(self.heads(period, column))

        is_incs = []
        for value in values:
            is_incs.append(value[0] < value[-1])

        if is_all:
            return all(is_incs)
        else:
            return any(is_incs)