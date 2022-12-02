import numpy as np
import pandas as pd
from typing import List

def getStateUpDn(df: pd.DataFrame, window: int, col: str, rate_dn: float = 1, rate_up: float = 1.1) -> List:
    ups = df[col] == df[col].rolling(window).min().shift(-window+1)
    dns = df[col] == df[col].rolling(window).max().shift(-window+1)
    updn, term, is_up, is_change, s_val, e_val = [], [], False, False, 0, 0
    
    for up, dn, val in zip(ups, dns, df[col]):
        if not np.isnan(val):
            e_val = val
        if is_change:
            updn += term
            term, is_change = [], False
            s_val = val
        term.append(is_up)
        
        if not is_up and up: # change state: dn -> up
            is_up, is_change = True, True
            if s_val != 0 and s_val * rate_dn < val: # dn state does not satisfy rate_dn condition.
                term = list(np.logical_not(term))
        elif is_up and dn: # change state: up -> dn
            is_up, is_change = False, True
            if s_val != 0 and s_val * rate_up > val: # up state does not satisfy rate_up condition.
                term = list(np.logical_not(term))
    
    if (is_up and s_val * rate_up > e_val) or (not is_up and s_val * rate_dn < e_val):
        term = list(np.logical_not(term))
    updn += term

    return updn