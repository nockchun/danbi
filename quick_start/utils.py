from matplotlib import offsetbox
from danbi.utils import *

print(infoInstalledPackage("danbi.*"))
print(getDaysBetween("2000-01-01", "2010-12-31", [2, 7], [0]))

print(getDayPeriod())
print(getDayPeriod("2022-06-01"))
print(getDayPeriod("2022-06-01", off_year=1, delta_year=10))
print(getDayPeriod("2022-06-01", off_year=1, delta_year=-10))
