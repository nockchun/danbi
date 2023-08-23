import abc
import pandas as pd

class ITimeseriesToImage(abc.ABC):
    def __init__(self, df: pd.DataFrame, win: int, height: int = None, width: int = None, backcolor: str = "black", line: float = 1, pad: float = 0.5, dpi: int = 96,
                 data_type = np.float16, label_type = np.float16, tfrec_file: str = "time2image.tfrec", tfrec_zip: bool = True,
                 method: str = "summation", n_bins: int = 10, strategy: str = 'quantile', overlapping: bool = False, flatten: bool = False):
        self._df = df
        self._win = win
        self._height = height
        self._width = width
        if width is None or height is None:
            figsize = win // 5
            self._figsize = (win // figsize, win // figsize)
        else:
            figsize = height // 5
            self._figsize = (width // figsize, height // figsize)

        self._winidx = list(range(win))
        self._backcolor = backcolor
        self._line = line
        self._pad = pad
        self._dpi = dpi
        
        self._tfrec_data_type = data_type
        self._tfrec_label_type = label_type
        self._tfrec_zip = tfrec_zip
        self._tfrec_file = tfrec_file

        self._gaf = GramianAngularField(image_size=self._win, sample_range=None, method=method, overlapping=overlapping, flatten=flatten)
        self._mtf = MarkovTransitionField(image_size=self._win, n_bins=n_bins, strategy=strategy, overlapping=overlapping, flatten=flatten)

    @abc.abstractclassmethod
    def connect(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def isConnect(self) -> bool:
        ...

    @abc.abstractclassmethod
    def close(self, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def getConnection(self, auto_commit=True, **kwargs):
        ...
    
    @abc.abstractclassmethod
    def releaseConnection(self, conn):
        ...
