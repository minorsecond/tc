from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Employee, Job, Clocktime
from datetime import datetime, timedelta

engine = create_engine('sqlite:///tc.db')
DBSession = sessionmaker(bind=engine)

session = DBSession()

new_emp = Employee(firstname="Adam", lastname="Smith")
session.add(new_emp)

new_job = Job(name="Timeclock project", abbr="PYTIME")
session.add(new_job)

new_clktime = Clocktime(employee=new_emp, job=new_job, time_in=datetime.now(), time_out=datetime.now() + timedelta(minutes=60))
session.add(new_clktime)

session.commit()
