from sqlalchemy import create_engine
from models import Employee, Job, Clocktime, Base
from tc import DB_NAME

engine = create_engine('sqlite:///{}'.format(DB_NAME))

Base.metadata.create_all(engine)
