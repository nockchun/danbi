from typing import Union
from datetime import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.relativedelta import relativedelta


def getDaysBetween(start: Union[str, datetime], end: Union[str, datetime],
                   month: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   weekday: list[int] = [MO, TU, WE, TH, FR, SA, SU],
                   weekno: list[int] = [], strftime: str = "%Y-%m-%d") -> list[Union[str, datetime]]:
    """Find a filtered date that exists within a period.

    Args:
        start (Union[str, datetime]): start day of a period
        end (Union[str, datetime]): end day of a period
        month (list[int], optional): month filter. Defaults to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].
        weekday (list[int], optional): week filter. An int type is also possible(0:monday ... 6:sunday). Defaults to [MO, TU, WE, TH, FR, SA, SU].
        weekno (list[int], optional): It means the sequence of weeks in which month. Defaults to [].
        strftime (str, optional): if set to None, returns datetime type. Defaults to "%Y-%m-%d".

    Returns:
        list[Union[str, datetime]]: Returns all dates in the period as a list in 'str' or 'datetime' format.
    """
    len_weekday = 1+len(weekday)
    result = rrule(
        MONTHLY,
        bymonth=month,
        byweekday=weekday,
        bysetpos=sum([list(range(len_weekday*(no-1), len_weekday*no)) for no in weekno], []),
        dtstart=parse(start) if isinstance(start, str) else start,
        until=parse(end) if isinstance(start, str) else end
    )
    
    return [x.strftime(strftime) if strftime else x for x in result]


def getDayPeriod(base: Union[str, datetime] = None,
                 off_year: int = 0, off_month: int = 0, off_day: int = 0, off_week: int = 0,
                 delta_year: int = 0, delta_month: int = 0, delta_day: int = 0, delta_week: int = 0,
                 weekday: int = None, strftime: str = "%Y-%m-%d") -> tuple[Union[str, datetime]]:
    """Find the start date and end date that satisfy the condition.

    Args:
        base (Union[str, datetime], optional): The base date. if it is Null then means today. Defaults to None.
        off_year (int, optional): Change the base date by year. A negative number means before year. Defaults to 0.
        off_month (int, optional): Change the base date by month. A negative number means before month. Defaults to 0.
        off_day (int, optional): Change the base date by day. A negative number means before day. Defaults to 0.
        off_week (int, optional): Change the base date by week. A negative number means before week. Defaults to 0.
        delta_year (int, optional): The period in years based on the base date. Defaults to 0.
        delta_month (int, optional): The period in months based on the base date.. Defaults to 0.
        delta_day (int, optional): The period in days based on the base date.. Defaults to 0.
        delta_week (int, optional): The period in weeks based on the base date.. Defaults to 0.
        weekday (int, optional): Change the base date by a day of the week. Defaults to None.
        strftime (str, optional): if set to None, returns datetime type. Defaults to "%Y-%m-%d".

    Returns:
        tuple[Union[str, datetime]]: Returns a tuple of period day in 'str' or 'datetime' format. (start day, end day)
    """
    if base is None:
        base_day = datetime.now()
    else:
        base_day = datetime.strptime(base, "%Y-%m-%d") if isinstance(base, str) else base
    
    if weekday != None:
        weeks = [MO, TU, WE, TH, FR, SA, SU]
        if weekday in weeks:
            base_day = base_day + relativedelta(days=weeks.index(weekday)-base_day.weekday())
        else:
            base_day = base_day + relativedelta(days=weekday-base_day.weekday())

    start_day = base_day + relativedelta(years=off_year, months=off_month, days=off_day, weeks=off_week)
    end_day = start_day + relativedelta(years=delta_year, months=delta_month, days=delta_day, weeks=delta_week)
    
    if start_day > end_day:
        temp = start_day
        start_day = end_day
        end_day = temp
    
    if strftime is not None:
        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
    
    return start_day, end_day
