import abc
import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Callable


def genFigureImageArray(fig: plt.figure, width: int = None, height: int = None, channels: str = "r"):
    fig.canvas.draw()
    fig_data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image = fig_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    if width is not None or height is not None:
        image = cv2.resize(image, (width, height))

    imgarrays = []
    imgarray = np.array(image)
    for channel in channels:
        imgarrays.append(imgarray[:, :, "rgb".index(channel)])
    imgarray = np.max(imgarrays, axis=0)

    return imgarray * (255 // imgarray.max())


class ITimeEncoder(abc.ABC):
    def __init__(self, slice_start: int = None, slice_end: int = None):
        self._slice_start = slice_start
        self._slice_end = slice_end
    
    @abc.abstractclassmethod
    def setParams(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def getEncoded(self, data: np.array) -> List[np.array]:
        ...


class TimeEncodingBuilder():
    def __init__(self, encoders: List[ITimeEncoder]):
        self._encoders = encoders
    
    def getImage(self, data: np.array, tolist: bool = False):
        encoded = []
        for encoder in self._encoders:
            encoded += encoder.getEncoded(data)
        
        return encoded if tolist else np.stack(encoded, axis=-1)
    
    def getTimeseries(self, data: np.array, tolist: bool = False):
        encoded = []
        for encoder in self._encoders:
            encoded += encoder.getEncoded(data)

        return encoded if tolist else np.concatenate(encoded)

