#!/usr/bin/python
# -*- coding: ascii -*-

"""
This script is a timesheet utility designed to assist
in keeping track of projects in a project-based
job using project codes and names. It has the ability
to create CSV files, convert standard time to tenths
of an hour, and to generate reports.
"""

# PYPER (Python Project Time Tracker)
# A timeclock program for project-based jobs
# Robert Ross Wardrup, NotTheEconomist, dschetel
# 08/31/2014

import datetime
import sys
import os
import os.path
import logging
import uuid

from sqlalchemy import create_engine, Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


__all__ = ['Clocktime', 'Employee', 'Job']
LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
# TODO: Figure out what to do with jobdb. This DB kept the total daily time for each task.
DB_NAME = "timesheet.db"
LOGLEVEL = logging.INFO
logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)

# Status variable - 0 = not in task. 1 = in task
status = 0
# Enable this flag (1) if debugging. Else leave at 0.
debug = 1


date = str(datetime.date.today())
day_start = datetime.datetime.now()


engine = create_engine('sqlite:///{}'.format(DB_NAME))

"""
A DBSession() instance establishes all conversations with the database
and represents a "staging zone" for all the objects loaded into the
database session object. Any change made against the objects in the
session won't be persisted into the database until you call
session.commit(). If you're not happy about the changes, you can
revert all of them back to the last commit by calling
session.rollback()
http://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
"""
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()


class Clocktime(Base):
    """Table for clockin/clockout values

    ForeignKeys exist for Job and Employee
    many to one -> employee
    many to one -> job
    """

    __tablename__ = "clocktimes"
    id = Column(Integer, primary_key=True)
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))

    @property
    def timeworked(self):
        return self.time_out - self.time_in


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


class Job(Base):
    """Table for jobs

    one to many -> clocktimes
    note that rate is cents/hr"""

    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    name = Column(String(75))
    abbr = Column(String(16))
    rate = Column(Integer)  # cents/hr
    clocktimes = relationship('Clocktime', backref='job')


def update_now():
    """
    Updates the "now" variable, which is a datetime object with
    Year, month, day, hour, minute. e.g. 2015-2-5 13:00
    :return: datetime object with above parameters.
    """
    now = datetime.datetime.now().strftime('%I:%M %p')
    return now


def query():
    """Prompts user for a yes/no answer

    if user responds with 'yes', 'ye', or 'y', return True
    if user responds with 'no' or 'n', return False.
    else: return None
    """

    # raw_input returns the empty string for "enter"
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = raw_input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def project_start():
    """
    Prompts the user for project information, creates an id for
    recalling data (will be used in the future) and returns
    project name, project abbrev and id for use in other
    functions.
    """
    global p_uuid
    global project_name
    global clock_in
    global status

    logging.debug("project_start called")
    time_in = datetime.datetime.now()
    abbrev = raw_input("What are you working on? (ABBREV): ")
    project_name = raw_input("What is the name of this project?: ")
    # lead_name = raw_input("For whom are you working?: ")
    p_uuid = str(uuid.uuid4())
    p_rate = raw_input("At what rate does this job pay? (Cents): ")
    logging.debug("UUID is {}".format(p_uuid))
    logging.debug("abbrev is {}".format(abbrev))
    logging.debug("project_name is {}".format(project_name))
    if debug == 1:
        print "DEBUGGING: PID = {}".format(p_uuid)
        raw_input("Press enter to continue")
    status = 1
    new_task = jobs(id=p_uuid, abbr=abbrev, name=project_name, rate=p_rate)

    session.add(new_task)
    session.commit()
    return p_uuid, project_name, time_in, status


# Experimental functions - https://github.com/NotTheEconomist/Timeclock/commit/74a8de1b66b4aeef51feaaf447d5cacacfdf2b5c
"""
def get_job_by_abbr(abbr):
    jobs = session.query(models.Job).filter_by(abbr=abbr).all()
    if len(jobs) > 1:
        # two jobs with the same abbr in here -- should this be unique? If not:
        for idx, job in enumerate(jobs, start=1):
            print("{idx}. {job.name}".format(idx=idx, job=job))
        selection = input("Which job? ")
        job = jobs[int(selection) - 1]
    elif len(jobs) == 1:
        job = jobs[0]
    else:
        return None
        # TODO: no jobs found with that info -- what do we do?
    return job


def clock_in():
    now = datetime.datetime.now()
    me = models.Employee(firstname="My", lastname="Name")  # or load from config or etc
    job = get_job_by_abbr(input("Job abbreviation? "))  # set up jobs somewhere else?
    c = Clocktime(time_in=now, employee=me, job=job)
    session.add(c)
    session.commit()


def get_open_clktime(job, employee):
    cq = session.query(Clocktime)
    clktime = cq.filter_by(time_out=None, job=job, employee=employee).one()
    # the `one` method will throw an error if there are more than one open
    # clock times with that job and employee!
    return clktime


def clock_out():
    job = get_job_by_abbr(input("Job abbr ?"))
    now = datetime.now()
    clktime = get_open_clktime(job, me)
    clktime.time_out = now
    session.commit()
"""

def round_to_nearest(num, b):
    """Rounds num to the nearest base

    round_to_nearest(7, 5) -> 5
    """

    company_minutes = num + (b // 2)
    return company_minutes - (company_minutes % b)


def sel_timesheet_row():
    """
    Returns the current job's row, using the PID generated by project_start.
    :return: the current job's row.
    """

    # Probably be better to use cur.lastrowid to select the last row, because currently it will fetch all activities
    # per PID and update them.

    with conn:
        lid = cur.lastrowid
        cur.execute(
            "SELECT UUID, Job_name, Job_abbrev, Stop_type, Stop_time, Date, Lead_name, Start_time FROM timesheet WHERE Id = ?",
            (lid,))
        sel = cur.fetchall()
        return sel


def breaktime(answer):
    """Prompts user to specify reason for break.

    :param answer: takes user input from timer function

    No real reason for this other than just general bookkeeping.
    Not a requirement. Would be nice to be able to pause the timer for breaks,
    rather than having to start the script all over again.
    """
    global job_name
    global job_abbrev
    global lead_name
    global stop_type
    global start_time
    global diff
    global status

    sel = sel_timesheet_row()
    if debug == 1:
        print("\nDEBUGGING MODE\n")
        print("Timesheet Rows:")
        print(sel)

    for row in sel:
        job_name = row[1]
        job_abbrev = row[2]
        stop_type = row[3]
        lead_name = row[6]
        start_time = row[7]

    logging.debug("Called choices with answer: {}".format(answer))
    if answer.lower() in {'1', '1.', 'lunch'}:
        if status == 1:
            now = update_now()
            # Sel gets the last row printed, which should be the current job.
            sel = sel_timesheet_row()
            for row in sel:
                print "Stopping {0}, ABBREV {1} for lunch at {2} on {3}".format(row[1], row[2], row[4], row[5])
                job_name = row[1]
                job_abbrev = row[2]
                stop_type = row[3]
                lead_name = row[6]
                start_time = row[7]
            for row in sel:
                print "Stopping {0}, ABBREV {1} for lunch at {2}".format(row[1], row[2], now)

                # TODO: Check if the current job's PID matches all entries for same abbrev on same date. This should
                # keep everything in order as far as time calculations. It should be as simple as subtracting break
                # time from total logged hours for each PID.
            stop_type = "lunch"
            with conn:
                cur.execute(
                    "INSERT INTO timesheet(UUID, Job_name, Job_abbrev, Stop_type, Stop_time) VALUES(?, ?, ?, ?, ?)",
                    [p_uuid, job_name, job_abbrev, stop_type, now])

            # Get time passed since beginning of task.
            curr_time = datetime.datetime.now().strftime('%I:%M %p')
            # diff is returning incorrect time
            diff = datetime.datetime.strptime(curr_time, '%I:%M %p') - datetime.datetime.strptime(start_time, '%I:%M %p')
            time = float(round_to_nearest(diff.seconds, 360)) / 3600
            if debug == 1:
                print("Variables -- Start Time {0}. Current Time: {1}. Diff: {2}. Time: {3}")\
                    .format(start_time, curr_time, diff, time)
            with jobdb:
                if debug == 1:
                    print("Connected to DB: jobdb.\n")
                cur.execute(
                    "INSERT INTO jobdb(UUID, Lead_name, Job_name, Job_abbrev, Time_worked, "
                    "Date) VALUES(?, ?, ?, ?, ?, ?)", [p_uuid, lead_name, job_name, job_abbrev, time, date]
                )

            print ("Enjoy! You worked {0} hours on {1}.").format(time, job_name)
            logging.info("Lunch break at {}".format(datetime.datetime.now()))
            status = 0
            raw_input("Press Enter to begin working again")
            print("Are you still working on '{}' ? (y/n)").format(job_name)
            answer = query()
            if answer:
                now = datetime.datetime.now().strftime('%I:%M %p')
                print "Resuming '{0}' at: '{1}\n' ".format(job_name, now)
                status = 1
                cur.execute(
                    "INSERT INTO timesheet(UUID, Job_name, Job_abbrev, Stop_type, Start_time) VALUES(?, ?, ?, ?, ?)",
                    [p_uuid, job_name, job_abbrev, stop_type, now])
                main_menu()
            else:
                status = 0
                main_menu()
            logging.info("Back from lunch at {}".format(now))
        else:
            raw_input("\nYou're not currently in job. Press enter to return to main menu.")
            main_menu()
    elif answer.lower() in {'2', '2.', 'break'}:
        if status == 1:
            now = update_now()
            status = 0
            logging.info("Taking a break at {}".format(now))
            raw_input("Press Enter to begin working again")
            print ("Are you still working on {}? (y/n)").format(job_name)
            answer = query()
            if answer:
                cur.execute(
                    "INSERT INTO timesheet(UUID, Job_name, Job_abbrev, Stop_type, Start_time) VALUES(?, ?, ?, ?, ?)",
                    [p_uuid, job_name, job_abbrev, stop_type, now])
                print "Resuming '{0}' at: '{1}' ".format(job_name, now)
                logging.info("Back from break at {}".format(now))
                status = 1
                main_menu()
            else:
                status = 0
                main_menu()
        else:
            raw_input("\nYou're not currently in job. Press enter to return to main menu.")
            main_menu()
    elif answer.lower() in {'3', '3.', 'heading home', 'home'}:
        if status == 1:
            print 'Take care!'
            status = 0
            now = update_now()
            logging.info("Clocked out at {}".format(now))
            return "end of day"
        else:
            raw_input("\nYou're not currently in job. Press enter to return to main menu.")
            main_menu()


def time_formatter(time_input):
    """Prompts the user for hh:mm and returns a timedelta

    Takes user input as 00:00, splits those using : as seperator, and returns
    the resulting timedelta object.
    """
    FAIL_MSG = "Please check input format and try again. (00:00)"
    split = time_input.split(":")
    if len(split) != 2:
        raise ValueError(FAIL_MSG)
    try:
        hours, minutes = map(int, split)
    except ValueError as e:
        raise ValueError(FAIL_MSG)
    minutes = round_to_nearest(minutes, 6)
    d = datetime.timedelta(hours=hours, minutes=minutes)
    return d


def get_time(time):
    """
    Format user input time so that datetime can process it correctly.
    """

    global time_conc

    if time.split(' ')[0] in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'}:
        time = time.split(' ')[0] + ':' + '00' + ' ' + time.split(' ')[1]
        print(time)
    try:
        split_hour = time.split(':')[0]
        split_minute = time.split(':')[1]
        split_minute2 = split_minute.split(' ')[0]
        split_ap = time.split(' ')[1]
        if split_ap in {'a', 'A', 'p', 'P'}:
            while split_ap in {'a', 'A'}:
                split_ap = 'AM'
            while split_ap in {'p', 'P'}:
                split_ap = 'PM'
            global _time_conc
            _time_conc = split_hour + ':' + split_minute2 + ' ' + split_ap
            time_conc = datetime.datetime.strptime(_time_conc, '%I:%M %p')
        else:
            time_conc = datetime.datetime.strptime(time, '%I:%M %p')
    except SyntaxError:
        print("Check format and try again.")

    return time_conc


def total_time():
    t_in = get_time(
        raw_input(
            "Please enter your start time in 00:00 AM/PM format: "))
    t_out = get_time(
        raw_input(
            "Please enter your end time in 00:00 AM/PM format: "))
    delta = t_out - t_in
    delta_minutes = float(round_to_nearest(delta.seconds, 360)) / 3600
    print "Your time sheet entry for {0} is {1} hours.".format(delta, delta_minutes)
    raw_input("\nPress enter to return to main menu.")
    main_menu()


def switch_task():
    global job_name
    global job_abbrev
    now = update_now()
    sel = sel_timesheet_row()
    stop_type = "switch task"
    for row in sel:
        job_name = row[1]
        job_abbrev = row[2]
        stop_type = row[3]
    with conn:
        cur.execute(
            "INSERT INTO timesheet(UUID, Job_name, Job_abbrev, Stop_type, Stop_time) VALUES(?, ?, ?, ?, ?)",
            [p_uuid, job_name, job_abbrev, stop_type, now])
    project_start()
    main_menu()


def report():
    print("\nGenerating report for {0}\n").format(date)
    with jobdb:
        cur.execute(
            "SELECT Job_name, Job_abbrev, Time_worked, Lead_name, Date FROM jobdb WHERE Date = ?", (date, ))
        while True:
            sel = cur.fetchall()
            print("Job Name | Job Abbrev | Time Worked | Lead Name  | Date")
            print("=======================================================")
            for row in sel:
                print("\n{0}    | {1}      | {2}        | {3}       | {4}") \
                    .format(row[0], row[1], row[2], row[3], row[4])
            raw_input("\nPress enter to return to main menu.")
            main_menu()


# TODO: Add code from v0.1 that prints current task at bottom of main menu if status == 1.
def main_menu():
    while True:
        """Main menu for program. Prompts user for function."""
        print "PYPER Timesheet Utility\n\n" \
              "What would you like to do?\n" \
              "1. Clock In\n" \
              "2. Break Time\n" \
              "3. Clock Out\n" \
              "4. Set up obs/break types\n" \
              "5. Timesheet Minute Formatter\n" \
              "6. Calculate Total Time Worked\n" \
              "7. Generate Today's Timesheet\n" \
              "9. Quit\n"
        answer = raw_input(">>> ")
        if answer.startswith('1'):
            project_start()
        if answer.startswith('2'):
            break_submenu()
        if answer.startswith('3'):
            raise NotImplementedError()
            # TODO: implement clock out
        if answer.startswith('4'):
            raise NotImplementedError()
            # TODO: implement set up break types
        if answer.startswith('5'):
            time_input = raw_input("\nTime Formatter\n"
                                   "Please enter hours and minutes worked today"
                                   "in 00:00 format: ")
            try:
                d = time_formatter(time_input)
                # TODO: what should we do with time_formatter? Time adustments?
            except ValueError as e:
                print(e)
        if answer.startswith('6'):
            total_time()
        if answer.startswith('7'):
            report()
        if answer.startswith('9'):
            break


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main_menu()
