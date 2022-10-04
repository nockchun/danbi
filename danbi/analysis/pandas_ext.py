import pandas as pd
import numpy as np
from typing import Union, List, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, window: int, func: Callable, test: int = 0, future: bool = False):
        results = []
        if test > 0:
            for idx, df in enumerate(self._obj.rolling(window)):
                if len(df) < window:
                    continue
                if idx + 1 >= window + test:
                    break
                results.append(func(df))

            return results
        else:
            for df in self._obj.rolling(window):
                if len(df) < window:
                    continue
                results.append(func(df))
            
            if len(results) > 0:
                if isinstance(results[0], tuple):
                    nan = [[np.nan for _ in range(len(results[0]))] for _ in range(window-1)]
                else:
                    nan = [np.nan for _ in range(window-1)]
            
            return results + nan if future else nan + results
    
    def tailCurrent(self, column: str):
        return self._obj.iloc[-1][column]

    def headCurrent(self, column: str):
        return self._obj.iloc[0][column]

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
    
    def _is_include(self, datas: List, criteria: str, value: Union[int, float, str]):
        result = False
        if isinstance(value, str):
            inc_array = np.char.find(datas, value)
            if len(inc_array[inc_array == 0]) > 0:
                result = True
        else:
            if criteria == "=" and len(datas[datas == value]) > 0:
                result = True
            elif criteria == ">" and len(datas[datas > value]) > 0:
                result = True
            elif criteria == "<" and len(datas[datas < value]) > 0:
                result = True
        
        return result
    
    def tailInclude(self, period: int, column: str, criteria: str = "=", value: Union[int, float, str] = 1):
        datas = self._obj[column].values[-period:]
        return self._is_include(datas, criteria, value)
    
    def headInclude(self, period: int, column: str, criteria: str = "=", value: Union[int, float, str] = 1):
        datas = self._obj[column].values[:period]
        return self._is_include(datas, criteria, value)
    
    def tailUp(self, period: int, column: str, criteria: str, value: Union[int, float, str], up_period: int, up_value: Union[int, float, str]):
        datas = self._obj[column].values[-period:]
        
        has_state = self._is_include(datas, criteria, value)
        is_up = (datas[-up_period] < datas[-1]) & (up_value < datas[-1])
        
        return has_state & is_up

    def tailDn(self, period: int, column: str, criteria: str, value: Union[int, float, str], dn_period: int, dn_value: Union[int, float, str]):
        datas = self._obj[column].values[-period:]
        
        has_state = self._is_include(datas, criteria, value)
        is_up = (datas[-dn_period] > datas[-1]) & (dn_value > datas[-1])
        
        return has_state & is_up




