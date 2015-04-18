from tests.db import TestDBBase
from models import Employee
import unittest

class TestEmployee(TestDBBase, unittest.TestCase):

    def test_employee(self):
        """Tests the employee db object"""
        employee = self.session.query(Employee).one()
        self.assertEqual(employee.firstname, "Adam")
        self.assertEqual(employee.lastname, "Smith")
        self.assertEqual(employee.name, "Adam Smith")
        self.assertTrue(hasattr(employee, 'id'))

if __name__ == "__main__":
    unittest.main()
