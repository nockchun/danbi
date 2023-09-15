import numpy as np

class WithNumpyPrint:
    def __init__(self, precision: int = 3):
        self._precision = precision
        
    def __enter__(self):
        self.original_options = np.get_printoptions()
        np.set_printoptions(linewidth=1000, threshold=np.inf, precision=self._precision, suppress=True)
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        np.set_printoptions(**self.original_options)