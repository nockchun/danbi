import abc
import cv2
import numpy as np
import pandas as pd
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


class ITimeImage(abc.ABC):
    def __init__(self, height: int = None, width: int = None):
        self._height = height
        self._width = width
    
    @abc.abstractclassmethod
    def setParams(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def getImageChannels(self, data: np.array) -> List[np.array]:
        ...

class TimeDfToImageBuilder():
    def __init__(self, generators: List[Callable]):
        self._generators = generators
    
    def getImage(self, data: np.array, is_img: bool = True):
        channels = []
        for generator in self._generators:
            channels += generator.getImageChannels(data)
        
        return np.stack(channels, axis=-1) if is_img else channels