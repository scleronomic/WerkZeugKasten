import numpy as np
import calendar
import datetime


def get_iso_weeks(year):
    dates = get_days_in_year(year=year)
    iso_weeks = np.array([d.isocalendar()[1] for d in dates])

    weeks = []
    for i in range(1, iso_weeks[-1]+1):
        weeks.append(dates[iso_weeks == i])
    return weeks


def get_num_days(year, month):
    return calendar.monthrange(year, month)[1]


def get_days_in_year(year):
    return np.concatenate([get_days_in_month(year=year, month=m) for m in range(1, 13)], axis=0)


def get_days_in_month(year, month):
    return np.array([datetime.date(year, month, d) for d in range(1, get_num_days(year, month) + 1)])

