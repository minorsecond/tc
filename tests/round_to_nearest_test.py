__author__ = 'rwardrup'

import unittest

from tc import round_to_nearest


class round_test(unittest.TestCase):
    """ Tests for project_start"""

    def test_if_rounds(self):
        # Are only six-minute intervals output?
        for i in range(6, 1000):
            self.assertTrue(round_to_nearest(i, 6) % 6 == 0)


if __name__ == '__main__':
    unittest.main()