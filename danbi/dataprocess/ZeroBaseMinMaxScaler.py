from typing import List
import pandas as pd
import numpy as np
import danbi as bi

class ZeroBaseMinMaxScaler():
    def __init__(self, scale: List[float] = [-1.0, 1.0], zero_base: bool = False, zero_add: bool = False, same_scale: bool = False):
        # assert (zero_base or not same_scale), "Parameter same_scale can be used only when zero_base is True"
        self._scale = np.array(scale, dtype='float64')
        self._zero_base = zero_base
        self._zero_add = zero_add
        self._same_scale = same_scale
        self._df_columns = None
        self._fits = {}

    def store(self, file: str) -> dict:
        bi.storePickle({
            "range": self._range,
            "zero_base": self._zero_base,
            "zero_add": self._zero_add,
            "same_scale": self._same_scale,
            "df_columns": self._df_columns,
            "fits": self._fits
        }, file)

    def restore(self, file: str):
        stored_dict = bi.restorePickle(file)
        self._range = stored_dict["range"]
        self._zero_base = stored_dict["zero_base"]
        self._zero_add = stored_dict["zero_add"]
        self._separate_scale = stored_dict["separate_scale"]
        self._df_columns = stored_dict["df_columns"]
        self._fits = stored_dict["fits"]

    def _check_minmax(self, val: List):
        if isinstance(val, list):
            val = np.array(val).astype(np.float64)
        if self._zero_add:
            val = np.append(val, 0.0)
        neg_min = np.nanmin(val)
        pos_max = np.nanmax(val)
        pos_min = neg_max = None

        if self._zero_base:
            if len(val[val >= 0]) > 0:
                pos_min = np.nanmin(val[val >= 0])
            else:
                pos_min = 0
            if len(val[val <= 0]) > 0:
                neg_max = np.nanmax(val[val <= 0])
            else:
                neg_max = 0
            if self._same_scale:
                if np.abs(neg_min) > np.abs(pos_max):
                    pos_max = neg_min * -1
                else:
                    neg_min = pos_max * -1
                if np.abs(neg_max) > np.abs(pos_min):
                    pos_min = neg_max * -1
                else:
                    neg_max = pos_min * -1

        return neg_min, neg_max, pos_min, pos_max

    def fit(self, val: List, field: str = "base", verbos: bool = False):
        neg_min, neg_max, pos_min, pos_max = self._check_minmax(val)
        if verbos:
            print(f"'{field}' min max [neg_min:{neg_min}, neg_max:{neg_max} | pos_min:{pos_min}, pos_max:{pos_max}]")

        if self._zero_base:
            neg_b = neg_max
            neg_w = 0 if (neg_min - neg_b) == 0 else self._scale[0] / (neg_min - neg_b)
            pos_b = pos_min
            pos_w = 0 if (pos_max - pos_b) == 0 else self._scale[1] / (pos_max - pos_b)
            if verbos:
                print(f"   > zerobase is True [neg_b:{neg_b}, neg_w:{neg_w} | pos_b:{pos_b}, pos_w:{pos_w}]")
            self._fits[field] = [neg_b, neg_w, pos_b, pos_w]
        else:
            b = neg_min
            w = (self._scale[1] - self._scale[0]) / (pos_max - neg_min)
            if verbos:
                print(f"   > zerobase is False [b:{b}, w:{w}]")
            self._fits[field] = [b, w]

    def transform(self, val, field="base"):
        if isinstance(val, list):
            val = np.array(val).astype(np.float64)
        if self._zero_base:
            neg_b, neg_w, pos_b, pos_w = self._fits[field]

            val_neg = (val[np.where(val < 0)] - neg_b) * neg_w
            val_neg[val_neg == 0] = -1e-9
            val[val < 0] = val_neg

            val_pos = (val[np.where(val > 0)] - pos_b) * pos_w
            val_pos[val_pos == 0] = 1e-9
            val[val > 0] = val_pos
        else:
            b, w = self._fits[field]
            val = (val - b) * w + self._scale[0]
        return val.round(6)

    def inverse(self, val, field="base"):
        if isinstance(val, list):
            val = np.array(val).astype(np.float64)
        if self._zero_base:
            neg_b, neg_w, pos_b, pos_w = self._fits[field]
            val[val < 0] = val[np.where(val < 0)] / neg_w + neg_b 
            val[val > 0] = val[np.where(val > 0)] / pos_w + pos_b
        else:
            b, w = self._fits[field]
            val = (val - self._scale[0]) / w + b
        return val

    def fitDf(self, df: pd.DataFrame, columns: List[str] = None, groups: List[List[str]] = [[]], verbos=False):
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist()
        self._df_columns = columns

        columns = set(columns) - set(sum(groups, []))
        for column in columns:
            self.fit(df[column].astype(np.float64).values, column, verbos)

        for group in groups:
            for idx, item in enumerate(group):
                if idx == 0:
                    temp = df[group].astype(np.float64).values
                    tmp_neg = temp[temp <= 0]
                    tmp_pos = temp[temp >= 0]
                    data = np.array([tmp_neg.min(initial=0), tmp_neg.max(initial=0), tmp_pos.min(initial=0), tmp_pos.max(initial=0)])
                self.fit(data, item, verbos)

    def transformDf(self, df: pd.DataFrame, columns: List[str] = None, inplace: bool = False):
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist() if self._df_columns is None else self._df_columns

        transformed = {}
        for column in columns:
            trans = self.transform(df[column].astype(np.float64).values, column)
            if inplace:
                df[column] = trans
            else:
                transformed[column] = trans
        
        if inplace is False:
            return pd.DataFrame(transformed)

    def inverseDf(self, df: pd.DataFrame, columns: List[str] = None):
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist()

        transformed = {}
        for column in columns:
            transformed[column] = self.inverse(df[column].values, column)

        return pd.DataFrame(transformed)