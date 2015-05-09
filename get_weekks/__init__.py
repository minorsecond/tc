from datetime import date, timedelta


def get_week_days():
    """
    Calculates week start and end date for given year and week number.
    :param year:
    :param week:
    :return: Timedelta, looks like: "2003-12-29 , 2004-01-04"
    """
    d = date(2015, 1, 1)
    if (d.weekday() > 3):
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(6 - 1) * 7)
    print(d + dlt + timedelta(days=4))
    return d + dlt, d + dlt + timedelta(days=4)


get_week_days()
