from .info import (
    infoInstalledPackage,
    infoSubmodules
)
from .day_time import (
    MO, TU, WE, TH, FR, SA, SU,
    getDaysBetween,
    getDayPeriod,
    getWeekday, getYearAnimal
)
from .jupyter import (
    asClassMethod, setWarningOff, showAsCols
)
from .util import (
    storePickle, restorePickle
)
from .with_print import WithNumpyPrint, WithPandasPrint
from .EduPlot import EduPlotConf, EduPlot2D