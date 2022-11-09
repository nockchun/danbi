from danbi.utils import *

print(infoInstalledPackage("danbi.*"))
print(getDaysBetween("2000-01-01", "2010-12-31", [2, 7], [0]))

print(getDayPeriod())
print(getDayPeriod("2022-06-01"))
print(getDayPeriod("2022-06-01", off_year=1, delta_year=10))
print(getDayPeriod("2022-06-01", off_year=1, delta_year=-10))
print(getDayPeriod("2022/06/01 13:36:47", off_hour=-2, format="%Y/%m/%d %H:%M:%S"))
print(getDayPeriod("2022/06/01 13:36:47", delta_hour=-2, delta_minute=10, delta_second=70, format="%Y/%m/%d %H:%M:%S"))
# print(getDayPeriod("2022-06-01", off_year=1, delta_year=10))
# print(getDayPeriod("2022-06-01", off_year=1, delta_year=-10))

print(infoSubmodules("danbi", True, True))
