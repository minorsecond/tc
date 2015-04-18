from models import Job
from tests.db import TestDBBase
import unittest

class TestJob(TestDBBase, unittest.TestCase):

    def test_job(self):
        """Tests the clocktime db object"""
        job = self.session.query(Job).one()
        self.assertEqual(job.name, "Python Time")
        self.assertEqual(job.abbr, "PYTIME")
        self.assertEqual(job.rate, 20000)

if __name__ == "__main__":
    unittest.main()

