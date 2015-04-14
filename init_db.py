from sqlalchemy import create_engine
from models import Employee, Job, Clocktime, Base

engine = create_engine('sqlite:///tc.db')

Base.metadata.create_all(engine)
