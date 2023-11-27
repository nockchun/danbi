import matplotlib.pyplot as plt
import math
import numpy as np
from typing import List, Union


def genSignData(freq: Union[int, List[int]], x_range: int = 1000, y_min: int = 0, y_max: int = 65536, sample: int = 1, figsize: tuple = None):
    y_range = y_max - y_min
    x_value = np.array(range(x_range * sample))
    y_value = None

    if isinstance(freq, int):
        freq = [freq]
    for f in freq:
        y_temp = np.array([(math.sin(2 * math.pi * f * x / x_range) * (y_range / 2) + ((y_max + y_min) / 2)) for x in x_value])
        y_value = y_temp if y_value is None else y_value + np.array(y_temp)
    
    min_val = np.min(y_value)
    max_val = np.max(y_value)
    y_scaled = y_min + (y_value - min_val) * (y_max - y_min) / (max_val - min_val)

    if figsize is not None:
        plt.figure(figsize=figsize)
        plt.plot(x_value, y_scaled)
        plt.title(f'Sign Wave with Frequency {freq} and Y Range {y_min} to {y_max}')
        plt.xlabel('x')
        plt.ylabel(f'Value ({y_min} to {y_max})')
        plt.grid(True)
        plt.show()
    
    return x_value, y_scaled

