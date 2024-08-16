import pandas as pd
import numpy as np
from typing import Union, List, Tuple, Callable

@pd.api.extensions.register_dataframe_accessor("bi")
class DanbiExtendFrame:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._len = len(pandas_obj)

    def rollapply(self, win: int, func: Callable, test: int = 0, future: bool = False, val_nan=np.nan):
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
                if type(results[0]) in (list, tuple) and len(results[0]) > 1:
                    nan = [[val_nan for _ in range(len(results[0]))] for _ in range(win-1)]
                else:
                    nan = [val_nan for _ in range(win-1)]
                
            
            return results + nan if future else nan + results

    def sigmaSimilarity(self, sigma: int = 3, method: str = "sigma") -> pd.DataFrame:
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
    
    def timeseries(self, win: int, col_data: List[str], col_label: List[str] = None, next_label: List[int] = [1], step: int = 1) -> Tuple[np.array, np.array]:
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
        
    def timeseries_multi(self, win: int, col_datas: List[List[str]], col_labels: List[List[str]] = None, next_label: List[int] = [1], step: int = 1) -> Tuple[np.array, np.array]:
        win_data = [[] for _ in range(len(col_datas))]
        win_label = [[] for _ in range(len(col_labels))]
        next_label = np.array(next_label)
 
        datas = []
        labels = []
        for col_data in col_datas:
            datas.append(self._obj[col_data].values)
        if col_labels is not None:
            for col_label in col_labels:
                labels.append(self._obj[col_label].values)
        for idx in range(win, len(datas[0]) - next_label[-1] + 1):
            if idx % step != 0:
                continue
            for idx_array in range(len(col_datas)):
                win_data[idx_array].append(datas[idx_array][idx-win:idx])
            if col_label is not None:
                for idx_array in range(len(col_labels)):
                    win_label[idx_array].append(labels[idx_array][next_label + idx - 1].flatten())
        if col_label is None:
            return np.array(win_data), None
        else:
            return np.array(win_data), np.array(win_label)

    def dtype(self, src: Union[str, List[str]], dst: str, inplace: bool = True) -> pd.DataFrame:
        """Change all columns of a specific type to the target type. support numpy like notation.
    
        Args:
            src (List[str]): list of types to change.
                > optional : you can use the numpy like type notation.
                > example: i : int, int16, int32 ...
                           f : float, float16, float32 ...
            dst (str): target type.
            inplace (bool): apply the changed data directly to the original data.

        Examples:
           > df.bi.dtype(["i", "f"], "int8")
           > df.bi.dtype("f", "int8", True)
           > df_changed = df.bi.dtype("float8", "int8", False)
    
        Returns:
            When the inplace option is set to False, the method returns a pandas DataFrame that has been changed.
        """
        if isinstance(src, str):
            src = [src]
        
        cols = []
        for item in src:
            if len(item) == 1:
                cols += self._obj.columns[[dtype.kind in src for dtype in self._obj.dtypes]].tolist()
            else:
                cols += self._obj.columns[self._obj.dtypes.isin([np.dtype(ty) for ty in src])].tolist()
        cols = set(cols)
        
        if inplace:
            for col in cols:
                self._obj[col] = self._obj[col].astype(dst)
        else:
            return self._obj.astype({col: dst for col in cols})