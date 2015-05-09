__author__ = 'rwardrup'

import unittest

from get_weekks import get_week_days


class test_week(unittest.TestCase):
    def test_if_datetime(self):
        week = get_week_days(2015, 5)
        print(type(week))


if __name__ == '__main__':
    unittest.main()
