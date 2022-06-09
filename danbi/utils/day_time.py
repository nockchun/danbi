from dateutil.parser import parse
from dateutil.rrule import rrule, YEARLY, MONTHLY, WEEKLY, DAILY, MO, TU, WE, TH, FR, SA, SU

def getDaysBetween(start, end, month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], weekday=[0, 1, 2, 3, 4, 5, 6], weekno=[], strftime="%Y-%m-%d"):
    result = rrule(
        MONTHLY,
        bymonth=month,
        byweekday=weekday,
        bysetpos=sum([list(range(1+len(weekday)*(no-1), 1+len(weekday)*no)) for no in weekno], []),
        dtstart=parse(start) if isinstance(start, str) else start,
        until=parse(end) if isinstance(start, str) else end
    )
    
    return [x.strftime(strftime) if strftime else x for x in result]