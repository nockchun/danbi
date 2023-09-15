import pandas as pd
import numpy as np
from typing import List, Tuple, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, win: int, func: Callable, test: int = 0, future: bool = False):
        results = []
        if test > 0:
            for idx, df in enumerate(self._obj.rolling(win)):
                if len(df) < win:
                    continue
                if idx + 1 >= win + test:
                    break
                results.append(func(df))

            return results
        else:
            for df in self._obj.rolling(win):
                if len(df) < win:
                    continue
                results.append(func(df))
            
            if len(results) > 0:
                if len(results[0]) > 1:
                    nan = [[np.nan for _ in range(len(results[0]))] for _ in range(win-1)]
                else:
                    nan = [np.nan for _ in range(win-1)]
            
            return results + nan if future else nan + results

    def getSigmaSimilarity(self, sigma: int = 3, method: str = "sigma") -> pd.DataFrame:
        """
        method: sigma, distance
        """
        columns = self._obj.select_dtypes(include='number').columns.tolist()
        df = pd.DataFrame(1, index=columns, columns=columns)
        for idx1 in range(len(columns)):
            col1 = columns[idx1]
            min1, max1 = self._obj[col1].aot.getSigma(sigma)
            for idx2 in range(idx1+1, len(columns)):
                col2 = columns[idx2]
                min2, max2 = self._obj[col2].aot.getSigma(sigma)
                similarity = 0.0
                if method == "sigma":
                    if max1 >= min2 and max2 >= min1:
                        intersection = min(max1, max2) - max(min1, min2)
                        union = max(max1, max2) - min(min1, min2)
                        similarity = (intersection / union) * 100
                elif method == "distance":
                    amplitude1 = abs(max1 - min1)
                    amplitude2 = abs(max2 - min2)
                    similarity = min(amplitude1, amplitude2) / max(amplitude1, amplitude2) * 100
                df.iloc[idx1, idx2] = similarity
                df.iloc[idx2, idx1] = similarity
                
        return df

    def split(self, rate: float, suffle=False, seed=None) -> Tuple[pd.DataFrame, pd.DataFrame]: 
        if suffle:
            self._obj = self._obj.sample(frac=1, random_state=seed).reset_index(drop=True)
        idx = int(len(self._obj) * rate)
        return self._obj[:idx].reset_index(drop=True), self._obj[idx:].reset_index(drop=True)
    
    def getTimeseries(self, win: int, col_data: List[str], col_label: List[str] = None, next_label: List[int] = [1], step: int = 1) -> Tuple[np.array, np.array]:
        win_data = []
        win_label = []
        next_label = np.array(next_label)
        
        datas = self._obj[col_data].values
        if col_label is not None:
            labels = self._obj[col_label].values
        for idx in range(win, len(datas) - next_label[-1] + 1):
            if idx % step != 0:
                continue
            win_data.append(datas[idx-win:idx])
            if col_label is not None:
                win_label.append(labels[next_label + idx - 1].flatten())
        
        if col_label is None:
            return np.array(win_data), None
        else:
            return np.array(win_data), np.array(win_label)
