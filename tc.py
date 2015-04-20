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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Job, Employee, Clocktime


LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
DB_NAME = "timesheet.db"
LOGLEVEL = logging.INFO
logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)


date = str(datetime.date.today())
day_start = datetime.datetime.now()

engine = create_engine('sqlite:///{}'.format(DB_NAME))
DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    abbrev = raw_input("What are you working on? (ABBREV): ")
    project_name = raw_input("What is the name of this project?: ")
    # lead_name = raw_input("For whom are you working?: ")
    p_uuid = str(uuid.uuid4())
    try:
        p_rate = float(raw_input("At what rate does this job pay? (Cents): "))
    except ValueError, e:
        try:
            logging.debug(e)
            print("Check input and try again\n")
            p_rate = float(raw_input("At what rate does this job pay? (Cents): "))
        except:
            raw_input("Press enter to return to main menu.")
            main_menu()
    logging.debug("UUID is {}".format(p_uuid))
    logging.debug("abbrev is {}".format(abbrev))
    logging.debug("project_name is {}".format(project_name))
    if debug == 1:
        print "DEBUGGING: PID = {}".format(p_uuid)
        raw_input("Press enter to continue")
    status = 1
    new_task_job = [Job(abbr=abbrev, name=project_name, rate=p_rate), Clocktime(time_in=datetime.datetime.now())]
    # TODO: Get this working - doesn't yet clock in on Clocktime table.
    for i in new_task_job:
        session.add(i)
    session.commit()


# TODO: Implement these functions
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


def breaktime():
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

    sel = session.query(Job).order_by(Job.id.desc()).first()
    id = sel.id
    job_name = sel.name
    job_abbrev = sel.abbr
    rate = sel.rate

    # Check if currently in a job.
    if status == 0:
        raw_input("\nYou're not currently in job. Press enter to return to main menu.")
        main_menu()
    else:
        now = update_now()
        # Sel gets the last row printed, which should be the current job.
        for row in sel:
            print "Stopping {0}, ABBREV {1} for lunch at {2} on {3}".format(row[1], row[2], row[4], row[5])
            job_name = row[1]
            job_abbrev = row[2]
            stop_type = row[3]
            lead_name = row[6]
            start_time = row[7]
        for row in sel:
            print "Stopping {0}, ABBREV {1} for lunch at {2}".format(row[1], row[2], now)

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
            print("Variables -- Start Time {0}. Current Time: {1}. Diff: {2}. Time: {3}") \
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

    if time.split(' ')[0] in {'1', '2', '3', '4', '5', '6',
                              '7', '8', '9', '10', '11', '12'}:
        time = time.split(' ')[0] + ':' + '00' + ' ' + time.split(' ')[1]
    try:
        split_hour = time.split(':')[0]
        split_minute = time.split(':')[1]
        split_minute2 = split_minute.split(' ')[0]
        split_ap = time.split(' ')[1]
    except IndexError:
        print("\nCheck format and try again.\n")
        total_time()
    try:
        if split_ap in {'a', 'A', 'p', 'P'}:
            while split_ap in {'a', 'A'}:
                split_ap = 'AM'
            while split_ap in {'p', 'P'}:
                split_ap = 'PM'
            _time_conc = split_hour + ':' + split_minute2 + ' ' + split_ap
            time_conc = datetime.datetime.strptime(_time_conc, '%I:%M %p')
        else:
            time_conc = datetime.datetime.strptime(time, '%I:%M %p')
    except NameError:
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
    print "\n*** Your time sheet entry is {0} hours. ***".format(delta_minutes)
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


def config():
    """Configure jobs and employees"""

    global session

    # TODO: refactor these out into module-level so they're unit-testable
    def add_job(**kwargs):
        """Helper function to create Jobs

        prompt for fields if none are provided
        """
        if not kwargs:
            fields = ['name', 'abbr', 'rate']
            kwargs = {field: raw_input("{}: ".format(field)) for
                      field in fields}
            # store rate as int of cents/hour
            kwargs['rate'] = float(kwargs['rate']) * 100
        new_job = Job(**kwargs)
        session.add(new_job)
        return new_job

    def add_employee(**kwargs):
        """Helper function to create Employees

        prompt for fields if none are provided
        """
        if not kwargs:
            fields = ['firstname', 'lastname']
            kwargs = {field: raw_input("{}: ".format(field)) for
                      field in fields}
        new_employee = Employee(**kwargs)
        session.add(new_employee)
        return new_employee

    def edit_job(jobs):
        """Helper function to edit jobs

        Prompts for which job to edit, which field to change, and calls
        change_table_value to change it
        """
        show_tables(jobs)
        requested_job_abbr = raw_input("Job abbreviation? ")
        # TODO: If nothing is found, or multiple is found, handle gracefully
        job_to_edit = session.query(Job)\
                             .filter_by(abbr=requested_job_abbr)\
                             .one()
        print("1. Name\n"
              "2. Abbreviation\n"
              "3. Rate")
        answer = raw_input("What do you want to change? ")
        if answer.startswith('1'):  # Change name
            val_to_change = 'name'
        elif answer.startswith('2'):  # Change abbr
            val_to_change = 'abbr'
        elif answer.startswith('3'):  # Change rate
            val_to_change = 'rate'
        old_val = getattr(job_to_edit, val_to_change)
        new_val = raw_input("What do you want to change it to? ")
        if val_to_change == 'rate':
            new_val = int(float(new_val) * 100)
        print(job_to_edit)
        print("Changing {} to {}".format(old_val, new_val))
        confirm = raw_input("Are you sure? (y/n): ")
        if confirm == 'y':
            change_table_value(job_to_edit, val_to_change, new_val)
        else:
            print("Cancelled")

    def edit_employee(employees):
        # TODO
        """Helper function to edit employees

        Prompts for which employee to edit, which field to change, and calls
        change_table_value to change it
        """
        pass

    def show_tables(tables):
        """Prints a table of jobs/employees"""
        for table in tables:
            print(table)

    def change_table_value(table, attr, new_val):
        """Simply changes table.attr = new_val"""
        setattr(table, attr, new_val)

    while True:
        print("What do you want to configure?\n"
              "1. Jobs\n"
              "2. Employees\n"
              "3. Back\n")
        answer = raw_input(">>> ")

        if answer.startswith('1'):
            while True:
                jobs = session.query(Job).all()
                show_tables(jobs)
                print("\n"
                      "1. Add Job\n"
                      "2. Edit Job\n"
                      "3. Back\n")
                answer = raw_input(">>> ")
                if answer.startswith('1'):
                    # TODO: do something with new_job? What?
                    new_job = add_job()
                elif answer.startswith('2'):
                    edit_job(jobs)
                elif answer.startswith('3'):
                    try:
                        session.commit()
                    except Exception as e:
                        logging.error("An error occurred updating "
                                      "the jobs table {}".format(e))
                        print("There was an error committing changes. "
                              "Rolling back database to last good state.")
                        session.rollback()
                    break  # break the loop and go up a level
                else:
                    print("Invalid selection")
        if answer.startswith('2'):
            # TODO: Configure employees
            raise NotImplementedError()
        if answer.startswith('3'):
            break  # kick out of config function


# TODO: Add code from v0.1 that prints current task at bottom of main menu if status == 1.
def main_menu():
    while True:
        """Main menu for program. Prompts user for function."""
        print "PYPER Timesheet Utility\n\n" \
              "What would you like to do?\n" \
              "1. Clock In\n" \
              "2. Break Time\n" \
              "3. Clock Out\n" \
              "4. Configure\n" \
              "5. Calculate Total Time Worked\n" \
              "6. Generate Today's Timesheet\n" \
              "7. Quit\n"
        answer = raw_input(">>> ")
        if answer.startswith('1'):
            project_start()
        if answer.startswith('2'):
            breaktime()
        if answer.startswith('3'):
            raise NotImplementedError()
            # TODO: implement clock out
        if answer.startswith('4'):
            config()
        if answer.startswith('5'):
            total_time()
        if answer.startswith('6'):
            report()
        if answer.startswith('7'):
            sys.exit()


if __name__ == "__main__":
    debug = 1
    status = 0

    # Initialize logging
    LOGFILE = "timeclock.log"
    FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                       r"%(module)s | %(message)s"
    LOGLEVEL = logging.INFO
    logging.basicConfig(filename=LOGFILE,
                        format=FORMATTER_STRING,
                        level=LOGLEVEL)

    status = 0
    os.system('cls' if os.name == 'nt' else 'clear')
    main_menu()