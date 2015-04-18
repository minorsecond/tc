from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Employee, Job, Clocktime
from datetime import datetime, timedelta

TESTDATA = {
        'employee': Employee(firstname="Adam", lastname="Smith"),
        'job': Job(name="Python Time", abbr="PYTIME", rate=20000),
        'clocktime': Clocktime(time_in=datetime.today(),
                               time_out=datetime.today() + timedelta(hours=2))}
TESTDATA['clocktime'].employee = TESTDATA['employee']
TESTDATA['clocktime'].job = TESTDATA['job']

class TestDBBase(object):
    """ABC for DB test classes in the timeclock package

    REQUIRED to be implemented:
    instance method: `add_test_data` should add any test data to the session
        that's passed into it, returning None
    """
    
    def setUp(self):
        """Create a new blank sqlite database and add test data"""
        engine = create_engine('sqlite:///')
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        for datum in TESTDATA.values():
            self.session.add(datum)

    def tearDown(self):
        self.session.rollback()
        self.session.close()
