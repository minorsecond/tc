from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine('sqlite:///tc.db')
DBSession = sessionmaker(bind=engine)

session = DBSession()

print("EMPLOYEE:")
print(session.query(models.Employee).all())
print(session.query(models.Employee).first().name)

print("JOB:")
print(session.query(models.Job).all())
print(session.query(models.Job).first().abbr)

print("Clocktime")
print(session.query(models.Clocktime).all())
print(session.query(models.Clocktime).first().time_in)

