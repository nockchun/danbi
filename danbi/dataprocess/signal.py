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


def genFourierInverseData(freq_sin: Union[int, List[int]], freq_cos: Union[int, List[int]], x_range: int = 1000, y_range: [int, int] = [0, 1], sample: int = 1, phase_shift: float = 0, sin_weight: float = 1, cos_weight: float = 1, figsize: tuple = None):
    """
    example : x, y = genFourierInverseData(freq_sin=2, freq_cos=2, x_range=2000, y_range=[0, 65536], sample=1, phase_shift=math.pi/4, sin_weight=1, cos_weight=0.5, figsize=(10, 4))
    """
    y_scale = y_range[1] - y_range[0]
    x_value = np.array(range(x_range * sample))
    y_value = np.zeros(len(x_value))

    if isinstance(freq_sin, int):
        freq_sin = [freq_sin]
    if isinstance(freq_cos, int):
        freq_cos = [freq_cos]

    for f in freq_sin:
        y_sin = sin_weight * np.array([(math.sin(2 * math.pi * f * x / x_range) * (y_scale / 2) + ((y_range[1] + y_range[0]) / 2)) for x in x_value])
        y_value += y_sin
    
    for f in freq_cos:
        y_cos = cos_weight * np.array([(math.cos(2 * math.pi * f * x / x_range + phase_shift) * (y_scale / 2) + ((y_range[1] + y_range[0]) / 2)) for x in x_value])
        y_value += y_cos
    
    min_val = np.min(y_value)
    max_val = np.max(y_value)
    y_scaled = y_range[0] + (y_value - min_val) * (y_range[1] - y_range[0]) / (max_val - min_val)

    if figsize is not None:
        plt.figure(figsize=figsize)
        plt.plot(x_value, y_scaled)
        plt.title(f'Fourier Series with Sin Frequencies {freq_sin} and Cos Frequencies {freq_cos}, Phase Shift {phase_shift}, and Y Range {y_range[0]} to {y_range[1]}')
        plt.xlabel('x')
        plt.ylabel(f'Value ({y_range[0]} to {y_range[1]})')
        plt.grid(True)
        plt.show()
    
    return x_value, y_scaled
