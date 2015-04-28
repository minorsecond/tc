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

from datetime import datetime
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

day_start = datetime.now()

engine = create_engine('sqlite:///{}'.format(DB_NAME))
DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    global p_rate
    global project_name
    global status
    global start_time
    global p_uuid
    global abbrev
    abbr = []

    sel = session.query(Job).order_by(Job.id.desc()).all()
    for i in sel:
        abbr.append((i.abbr))

    if status == 1:
        raw_input("\nYou're already in a task. Press enter to return to main menu.\n\n")
        os.system('cls' if os.name == 'nt' else 'clear')
        main_menu()
    else:
        logging.debug("project_start called")
        abbrev = raw_input('\nWhat are you working on? (Job ID): ')

        # Check if user has previously worked under this abbrev, and prompt to reuse information if so.
        if abbrev in abbr:
            job = session.query(Job).filter(Job.abbr == abbrev).order_by(Job.id.desc()).first()
            p_uuid = job.p_uuid
            project_name = job.name

            print("Are you working on {0}? (Y/n)").format(job.name)
            answer = query()
            if answer:
                clockin()
            else:
                raw_input("Press enter to return to main menu.")
                main_menu()
        else:
            # If new project, get new information from user.
            project_name = raw_input("What is the name of this project?: ")
            # lead_name = raw_input("For whom are you working?: ")
            try:
                p_rate = float(raw_input("At what rate does this job pay? (Cents): "))
            except ValueError, e:
                try:
                    logging.debug(e)
                    print("Check input and try again\n")
                    p_rate = float(raw_input("At what rate does this job pay? (Cents): "))
                except ValueError:
                    raw_input("Press enter to return to main menu.")
                    main_menu()
            logging.debug("job id is {}".format(abbrev))
            logging.debug("project_name is {}".format(project_name))
            p_uuid = str(uuid.uuid4())

            # Set up the table row and commit.
            new_task_job = Job(p_uuid=p_uuid, abbr=abbrev, name=project_name, rate=p_rate)
            session.add(new_task_job)
            session.commit()
            clockin()


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


def clockin():
    """
    Adds time, job, date, uuid data to tables for time tracking.

    :return: None
    """

    global start_time
    global status
    global abbrev
    global tworked

    # TODO: Add menu of past week's jobs? (May use other time frame, just an example). Must fix above issue first.

    new_task_clock = Clocktime(p_uuid=p_uuid, time_in=datetime.now())
    session.add(new_task_clock)
    session.commit()
    start_time = datetime.now()
    status = 1


def clockout():
    """
    Clocks user out of project. Prints time_out (now) to clocktimes table for whichever row contains the same
    p_uuid created in project_start().

    :rtype : object
    :return:
    """
    if status == 0:
        raw_input("You're not currently in a job. Press enter to return to main menu")
        main_menu()
    else:
        global status
        global start_time
        global tworked
        _sum_time = 0

        sel = session.query(Job).order_by(Job.id.desc()).first()
        job_name = sel.name
        job_abbrev = sel.abbr

        now = datetime.now()
        print 'Stopping {0}, project ID {1} at {2}:{3} on {4}/{5}/{6}'.format(job_name, job_abbrev, now.hour, \
                                                                              now.minute, now.day, now.month, now.year)

        # Get difference between start time and now, and then convert to tenths of an hour.
        diff = datetime.now() - start_time
        time = float(diff.seconds / 3600)

        # Short tasks (3 minutes or less) still count as .1 of an hour per my company's policy.
        if time < .1:
            time = .1
        time_worked = float(round_to_nearest(diff.seconds, 360)) / 3600
        if debug == 1:
            print("Variables -- Start Time {0}. Current Time: {1}. Diff: {2}. Time: {3}") \
                .format(start_time, datetime.now(), diff, time_worked)
        print ("Enjoy! You worked {0} hours on {1}.").format(time_worked, job_name)
        status = 0

        # Update Clocktime table with time out and time worked.
        session.query(Clocktime). \
            filter(Clocktime.p_uuid == p_uuid). \
            update({"time_out": now}, synchronize_session='fetch')

        session.query(Clocktime). \
            filter(Clocktime.p_uuid == p_uuid). \
            update({'tworked': time}, synchronize_session='fetch')

        # Get all rows in clocktime for current job, by p_uuid and then sum these tenths of an hour.
        tworked = session.query(Clocktime).filter(Clocktime.p_uuid == p_uuid).order_by(Clocktime.id.desc()).all()
        for i in tworked:
            _sum_time += i.tworked
        if debug == 1:
            print("Debugging: sum of time for {0} is {1}").format(i.job_id, _sum_time)
            raw_input()

        # Round the sum of tenths of an hour worked to the nearest tenth and then update to job table.
        sum_time = float(round_to_nearest(_sum_time, .1))
        session.query(Job). \
            filter(Job.p_uuid == p_uuid). \
            update({"worked": sum_time}, synchronize_session='fetch')

        session.commit()


def breaktime():
    """Prompts user to specify reason for break.

    No real reason for this other than just general bookkeeping.
    Not a requirement. Would be nice to be able to pause the timer for breaks,
    rather than having to start the script all over again.
    """
    global job_name
    global job_abbrev
    global lead_name
    global start_time
    global status
    global p_uuid

    # Pull most recent (top) row from jobs table.
    sel = session.query(Job).order_by(Job.id.desc()).first()
    id = sel.id
    job_name = sel.name
    job_abbrev = sel.abbr
    rate = sel.rate

    if debug == 1:
        print"DEBUGGING: JOB Database, most recent row:\n"
        print(sel)
        try:
            print("\nUUID: {0}").format(p_uuid)
            raw_input("\nPress enter to continue.\n")
        except NameError:
            print("p_uuid has not been created")

    # Check if currently in a job.
    if status == 0:
        raw_input("\nYou're not currently in job. Press enter to return to main menu.")
        os.system('cls' if os.name == 'nt' else 'clear')
        main_menu()
    else:
        # If not currently in job, prompt user for confirmation.
        print("Are you sure you want to stop working on {0} and take a break? (y/n)\n").format(job_name)
        answer = query()
        if answer:
            clockout()
            raw_input("Press Enter to begin working again")
            print("Are you still working on '{}' ? (y/n)").format(job_name)
            answer = query()
            if answer:
                # If user is returning to same job, start it back up again with same p_uuid.
                now = datetime.now().strftime('%I:%M %p')
                print "Resuming '{0}' at: '{1}\n' ".format(job_name, now)
                clockin()
            else:
                # If user is not restarting job, set status to 0 and return to menu.
                status = 0
                main_menu()
        else:
            main_menu()
            logging.info("Stopping task at {}".format(datetime.now()))


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

    # If user doesn't enter in 00:00 format, this will reformat their input into 00:00 AM so that DateTime
    # can parse it.
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
            time_conc = datetime.strptime(_time_conc, '%I:%M %p')
        else:
            time_conc = datetime.strptime(time, '%I:%M %p')
    except NameError:
        print("Check format and try again.")

    return time_conc


def total_time():
    """
    Prompts user to enter start and end time, and prints time worked in 1/10 of an hour to screen

    :rtype : str
    :return: None
    """

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


def report():
    """
    Prints a report table to screen.
    :return:
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    # TODO: Fix this so that only the current week's hours are printed.

    # Queries job table, pulling all rows.
    time_worked = session.query(Job).all()
    print("\n  Weekly Timesheet Report\n")
    print("\n{:<8} {:<15} {:<3}").format('Id', 'Job Name', 'Hours')
    print("{:<8} {:<15} {:<3}").format('========', '==============', '=====')
    for i in time_worked:
        jobs = {'job_name': i.name, 'job_id': i.abbr, 'hours': i.worked}
        print("{:<8} {:<15} {:<10}").format(i.abbr, i.name, i.worked)
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
        requested_job_abbr = raw_input("Job ID? ")
        # TODO: If nothing is found, or multiple is found, handle gracefully
        job_to_edit = session.query(Job) \
            .filter_by(abbr=requested_job_abbr) \
            .one()
        print("1. Name\n"
              "2. ID\n"
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
                    print("\nWould you like to begin working on {0}? (Y/n)").format(new_job.name)
                    answer = query()
                    if answer:
                        project_start()
                    else:
                        main_menu()
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


def main_menu():
    global project_name
    global start_time

    while True:
        """Main menu for program. Prompts user for function."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print "PYPER Timesheet Utility\n\n" \
              "What would you like to do?\n" \
              "1. Clock In\n" \
              "2. Break Time\n" \
              "3. Clock Out\n" \
              "4. Configure\n" \
              "5. Calculate Total Time Worked\n" \
              "6. Generate Today's Timesheet\n" \
              "7. Import/Export Timesheet\n" \
              "8. Quit\n"
        if status == 1:
            print ("*** Current job {0} at {1}. ***\n").format(project_name, start_time.strftime('%I:%M %p'))
        else:
            print("*** Not currently in a job. ***\n")
        answer = raw_input(">>> ")
        if answer.startswith('1'):
            project_start()
        if answer.startswith('2'):
            breaktime()
        if answer.startswith('3'):
            clockout()
            main_menu()
        if answer.startswith('4'):
            config()
        if answer.startswith('5'):
            total_time()
        if answer.startswith('6'):
            report()
        if answer.startswith('7'):
            raise NotImplementedError
        if answer.startswith('8'):
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

    os.system('cls' if os.name == 'nt' else 'clear')
    main_menu()