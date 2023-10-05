import numpy as np
import pandas as pd

class WithNumpyPrint:
    def __init__(self, precision: int = 3):
        self._precision = precision
        
    def __enter__(self):
        self.original_options = np.get_printoptions()
        np.set_printoptions(linewidth=1000, threshold=np.inf, precision=self._precision, suppress=True)
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        np.set_printoptions(**self.original_options)

class WithPandasPrint:
    def __init__(self, precision=5, width=0, rows=None, columns=None):
        self._width = width
        self._precision = precision
        self._rows = rows
        self._columns = columns
        self._origins = {}

    def __enter__(self):
        self._origins["width"] = pd.get_option("display.width")
        pd.set_option("display.width", self._width)
        
        self._origins["precision"] = pd.get_option("display.precision")
        pd.set_option("display.precision", self._precision)

        self._origins["rows"] = pd.get_option("display.max_rows")
        pd.set_option("display.max_rows", self._rows)

        self._origins["columns"] = pd.get_option("display.max_columns")
        pd.set_option("display.max_columns", self._columns)

    def __exit__(self, exc_type, exc_value, traceback):
        pd.set_option("display.width", self._origins["width"])
        pd.set_option("display.precision", self._origins["precision"])
        pd.set_option("display.max_rows", self._origins["rows"])
        pd.set_option("display.max_columns", self._origins["columns"])
