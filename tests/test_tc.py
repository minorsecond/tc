import unittest
import tc
from datetime import timedelta  # test against time_formatter output

class Test_TC(unittest.TestCase):
    
    def test_time_formatter(self):
        """Tests tc.time_formatter
        
        time_formatter should take a hh:mm string and format it into
        a timedelta, rounded to the nearest 6 minutes"""
        self.assertEqual(tc.time_formatter("00:10"), timedelta(minutes=12))
        self.assertEqual(tc.time_formatter("01:00"), timedelta(hours=1))
        self.assertEqual(tc.time_formatter("12:12"),
                         timedelta(hours=12, minutes=12))
        self.assertEqual(tc.time_formatter("13:05"),
                         timedelta(hours=13, minutes=6))
        self.assertEqual(tc.time_formatter("00:67"),
                         timedelta(hours=1, minutes=6))
        self.assertRaises(ValueError, tc.time_formatter, "wrong input")

if __name__ == "__main__":
    unittest.main()
