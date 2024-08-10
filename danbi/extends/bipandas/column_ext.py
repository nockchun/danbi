import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from typing import Union, List, Tuple, Callable

@pd.api.extensions.register_series_accessor("bi")
class DanbiExtendSeries:
    def __init__(self, column):
        self._col = column
        self._len = len(column)

    def rollapply(self, window: int, func: Callable, test: int = 0, future: bool = False, val_nan=np.nan):
        results = []
        if test > 0:
            for idx, df in enumerate(self._col.rolling(window)):
                if len(df) < window:
                    continue
                if idx + 1 >= window + test:
                    break
                results.append(func(df))

            return results
        else:
            for df in self._col.rolling(window):
                if len(df) < window:
                    continue
                results.append(func(df))
            
            if len(results) > 0:
                if isinstance(results[0], tuple):
                    nan = [[val_nan for _ in range(len(results[0]))] for _ in range(window-1)]
                else:
                    nan = [val_nan for _ in range(window-1)]
            
            return results + nan if future else nan + results

    def sigma(self, sigma: int = 3, quantile=0.1, as_int: bool = False) -> Tuple[float, float, float, float, float, float]:
        data = self._col.values
        val_max = max(data)
        val_min = min(data)
        mean = np.nanmean(data)
        std = np.nanstd(data)
        threshold = sigma * std

        sigma_lower = mean - threshold
        sigma_upper = mean + threshold
        sigma_percent = np.sum((data >= sigma_lower) & (data <= sigma_upper)) / data.size * 100

        quantile_lower = self._col.quantile(quantile)
        quantile_upper = self._col.quantile(1 - quantile)
        quantile_percent = np.sum((data >= quantile_lower) & (data <= quantile_upper)) / data.size * 100

        if as_int:
            lower = int(lower)
            mean = int(mean)
            upper = int(upper)
            std = int(std)
            threshold = int(threshold)
            sigma_percent = int(sigma_percent)
            quantile_percent = int(quantile_percent)

        return {
            "max": val_max,
            "min": val_min,
            "mean": mean,
            "std": std,
            "threshold": threshold,
            "sigma_lower": sigma_lower,
            "sigma_upper": sigma_upper,
            "sigma_percent": sigma_percent,
            "quantile_lower": quantile_lower,
            "quantile_upper": quantile_upper,
            "quantile_percent": quantile_percent
        }
    
    def lpf(self, cutoff: float = 0.1, fs: float = 1.0, order=5):
        data = self._col.values

        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)

        return y
    
    def forceDirection(self, period: int = 1, sigma: Union[int, float, dict] = 1, zero_rate: float = 0.0):
        diff = self._col.diff(period)
        if isinstance(sigma, (int, float)):
            sigma = diff.bi.sigma(sigma)
        direction = (diff / sigma["threshold"]).clip(-1, 1).fillna(0)

        zero_bound = zero_rate / 100
        direction = direction.mask((direction >= -zero_bound) & (direction <= zero_bound), 0.0)

        return direction

    def stateUpDn(self, window: int, up_rate: float = 1, dn_rate: float = 1, future: bool = False) -> List:
        if future:
            ups = self._col == self._col.rolling(window).min().shift(-window+1)
            dns = self._col == self._col.rolling(window).max().shift(-window+1)
        else:
            ups = self._col == self._col.rolling(window).min()
            dns = self._col == self._col.rolling(window).max()
        updn, term, is_up, is_change, s_val, e_val = [], [], False, False, 0, 0

        for up, dn, val in zip(ups, dns, self._col):
            if not np.isnan(val):
                e_val = val
            if is_change:
                updn += term
                term, is_change = [], False
                s_val = val
            term.append(is_up)

            if not is_up and up: # dn -> up 으로 변환
                is_up, is_change = True, True
                if s_val != 0 and s_val * dn_rate < val: # dn상태가 rate_dn 조건을 만족하지 않음.
                    term = list(np.logical_not(term))
            elif is_up and dn: # up -> dn 으로 변환
                is_up, is_change = False, True
                if s_val != 0 and s_val * up_rate > val: # up상태가 rate_up 조건을 만족하지 않음.
                    term = list(np.logical_not(term))

        if (is_up and s_val * up_rate > e_val) or (not is_up and s_val * dn_rate < e_val):
            term = list(np.logical_not(term))
        updn += term
        
        return np.array(updn)

    def updnFuture(self, window: int, rate_up: float = 0.1, rate_dn: float = 0.1, valid_change: int = 3) -> List:
        ups = self._col == self._col.rolling(window).min().shift(-window+1)
        dns = self._col == self._col.rolling(window).max().shift(-window+1)
        updn, term, is_up, is_change, s_val, e_val = [], [], False, False, 0, 0
        change_period = 1

        for up, dn, val in zip(ups, dns, self._col):
            if not np.isnan(val):
                e_val = val
            if is_change:
                updn += term
                term, is_change = [], False
                s_val = val
                change_period = 1
            else:
                change_period += 1
            if change_period >= valid_change:
                term.append(None)
            else:
                term.append(is_up)

            if not is_up and up: # dn -> up 으로 변환
                is_up, is_change = True, True
                if s_val != 0 and s_val * (1-rate_dn) < val: # dn상태가 rate_dn 조건을 만족하지 않음.
                    term = list(np.logical_not(term))
            elif is_up and dn: # up -> dn 으로 변환
                is_up, is_change = False, True
                if s_val != 0 and s_val * (1+rate_up) > val: # up상태가 rate_up 조건을 만족하지 않음.
                    term = list(np.logical_not(term))

        if (is_up and s_val * (1+rate_up) > e_val) or (not is_up and s_val * (1-rate_dn) < e_val):
            term = list(np.logical_not(term))
        updn += term
        
        return updn

    def updnCurrent(self, window: int, rate_up: float = 0.1, rate_dn: float = 0.1, fillna: bool = True) -> List:
        updn = self._col.pct_change(window)
        updn.mask(updn > rate_up , 1, inplace=True)
        updn.mask(updn < -rate_dn, -1, inplace=True)
        updn.mask((updn <= rate_up) & (updn >= -rate_dn) & (updn < 0), -0.5, inplace=True)
        updn.mask((updn <= rate_up) & (updn >= -rate_dn) & (updn >= 0), 0.5, inplace=True)
        
        return updn.fillna(0) if fillna else updn


