import pandas as pd
import numpy as np

class ZeroBaseMinMaxScaler():
    def __init__(self, base_range=(-1, 1)):
        self._range = base_range
        self._fits = {}
        self._globals = []
        self._globals_fit = []
    
    def __repr__(self):
        return str(self._fits)
    
    def fit(self, data, field="base", cleave=False):
        p_idx = np.where(data > 0)
        n_idx = np.where(data < 0)
        if cleave:
            p_max = max(data[p_idx]) if p_idx[0].size > 0 else 1e-9
            p_min = min(data[p_idx])-1e-10 if p_idx[0].size > 0 else 1e-10
            n_min = min(data[n_idx]) if n_idx[0].size > 0 else -1e-10
            n_max = max(data[n_idx])+1e-10 if n_idx[0].size > 0 else -1e-9
        else:
            data_all = np.abs(data[~np.isnan(data)])
            p_max = max(data_all)
            p_min = min(data_all)-1e-10
            n_max = -p_min+1e-10
            n_min = -p_max
        
        self._fits[field] = [
            self._range[1] / (p_max-p_min),
            self._range[0] / (n_min-n_max),
            p_min, n_max
        ]
    
    def fit_frame(self, data, cleave=False, combine_fields=[[]], except_fields=[], include_fields=[]):
        for column in data.columns:
            if column in except_fields:
                continue
            if (len(include_fields) > 0) and (column not in include_fields):
                continue
            if data[column].dtype in [int, float]:
                for fields in combine_fields:
                    if column in fields:
                        self.fit(np.concatenate([data[field].values for field in fields]), column, cleave)
                    else:
                        self.fit(data[column].values, column, cleave)
        
    def transform(self, data, field="base"):
        data = data.astype("float64")
        p_idx = np.where(data > 0)
        n_idx = np.where(data < 0)
        p_scale = (data[p_idx] - self._fits[field][2]) * self._fits[field][0]
        n_scale = (data[n_idx] - self._fits[field][3]) * self._fits[field][1]
        data[p_idx] = p_scale
        data[n_idx] = n_scale
        
        return data
    
    def transform_frame(self, data, postfix=None):
        for column in self._fits.keys():
            if column in data.columns:
                column_new = column if postfix == None else f"{column}_{postfix}"
                data[column_new] = self.transform(data[column].values, column)
    
    def inverse(self, data, field="base"):
        data = data.astype("float64")
        p_idx = np.where(data > 0)
        n_idx = np.where(data < 0)
        p_scale = data[p_idx] / self._fits[field][0] + self._fits[field][2]
        n_scale = data[n_idx] / self._fits[field][1] + self._fits[field][3]
        data[p_idx] = p_scale
        data[n_idx] = n_scale
        
        return data
    
    def inverse_frame(self, data, postfix=None):
        if isinstance(data, pd.DataFrame):
            for column in self._fits.keys():
                if column in data.columns:
                    column_transform = column if postfix == None else f"{column}_{postfix}"
                    data[column_transform] = self.inverse(data[column_transform].values, column)