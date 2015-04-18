from datetime import datetime, timedelta
from mock import MagicMock
from models import Clocktime
from tests.db import TestDBBase, TESTDATA
import unittest

class TestClocktime(TestDBBase, unittest.TestCase):

    def test_clocktime(self):
        """Tests the clocktime db object"""
        clocktime = self.session.query(Clocktime).one()
        self.assertEqual(clocktime.employee, TESTDATA['employee'])
        self.assertEqual(clocktime.job, TESTDATA['job'])
        self.assertAlmostEqual(clocktime.timeworked,
                               timedelta(hours=2),
                               delta=timedelta(minutes=6))

if __name__ == "__main__":
    unittest.main()


