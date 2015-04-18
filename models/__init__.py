from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,\
                       ForeignKeyConstraint
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()

__all__ = ['Clocktime', 'Employee', 'Job']

class Clocktime(Base):
    """Table for clockin/clockout values

    ForeignKeys exist for Job and Employee
    """

    __tablename__ = "clocktimes"
    id = Column(Integer, primary_key=True)
    employee = ForeignKey('employee.id')
    job = ForeignKey('job.id')
    time_in = Column(DateTime)
    time_out = Column(DateTime)

class Employee(Base):
    """Table for employees"""

    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @property
    def name(self):
        return self.firstname + " " + self.lastname

class Job(Base):
    """Table for jobs"""

    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    name = Column(String(75))
    abbr = Column(String(16))
    rate = Column(Numeric(precision=2))  # $/hr
    
