from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, \
    create_engine
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

from sqa_uuid import UUID


engine = create_engine('sqlite:///timesheet.db')
Base = declarative_base()

__all__ = ['Clocktime', 'Employee', 'Job']

class Clocktime(Base):
    """Table for clockin/clockout values

    ForeignKeys exist for Job and Employee
    many to one -> employee
    many to one -> job
    """

    __tablename__ = "clocktimes"
    id = Column(Integer, primary_key=True)
    p_uuid = Column(UUID)
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))
    # employee = many to one relationship with Employee
    # job = many to one relationship with Job

    # Should be able to query this, run it through the time_formatter function and output the results.
    # May have to perform some math on it first (add all timeworked per job, per day) and output to a table.
    @property
    def timeworked(self):
        return self.time_out - self.time_in

    @property
    def __str__(self):
        formatter="Employee: {employee.name}, "\
                  "Job: {job.abbr}, "\
                  "Start: {self.time_in}, "\
                  "End: {self.time_out}, "\
                  "Hours Worked: {self.timeworked}, "\
                  "ID# {self.id}"
        return formatter.format(employee=self.employee, job=self.job, self=self)

class Employee(Base):
    """Table for employees
    
    one to many -> clocktimes
    """

    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    clocktimes = relationship('Clocktime', backref='employee')
    
    @property
    def name(self):
        return self.firstname + " " + self.lastname

    def __str__(self):
        return "{name:<70}{id:>10}".format(name=self.name,
                                           id="ID# " + str(self.id))

class Job(Base):
    """Table for jobs
    
    one to many -> clocktimes
    note that rate is cents/hr"""

    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    p_uuid = Column(String)
    name = Column(String(50))
    abbr = Column(String(16))
    rate = Column(Integer)  # cents/hr
    clocktimes = relationship('Clocktime', backref='job')

    def __str__(self):
        formatter = "Name: {name:<50} {abbr:>23}\n" \
                    "Rate: ${rate:<7.2f}/hr {id:>62}"
        return formatter.format(name=self.name,
                                abbr="Abbr: " + str(self.abbr),
                                rate=self.rate/100.0,
                                id="ID# " + str(self.id))


Base.metadata.create_all(engine)