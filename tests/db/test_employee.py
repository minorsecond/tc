from models import Employee
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os # to clean up afterwards

TEST_DB_NAME = "test_db.db"

class TestEmployee(unittest.TestCase):
    def setUp(self):
        try:
            os.remove(TEST_DB_NAME)
        except Exception:
            try:
                with open(TEST_DB_NAME, 'wb'):
                    # opening it in 'wb' mode should blank db
                    pass
            except Exception:
                # if we can't guarantee state, we need to fail!
                self.fail("Can't initialize test DB")
        engine = create_engine('sqlite:///{}'.format(TEST_DB_NAME))
        Employee.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        test_employee = Employee(firstname="Adam",
                                 lastname="Smith")
        self.session.add(test_employee)
        self.session.commit()

    def tearDown(self):
        try:
            os.remove(TEST_DB_NAME)
        except Exception as e:
            print(e)
            pass # if it doesn't remove here, it's not the end of the world

    def test_employee(self):
        """Tests the employee db object"""
        employee = self.session.query(Employee).one()
        self.assertEqual(employee.firstname, "Adam")
        self.assertEqual(employee.lastname, "Smith")
        self.assertEqual(employee.name, "Adam Smith")
        self.assertTrue(hasattr(employee, 'id'))

if __name__ == "__main__":
    unittest.main()
