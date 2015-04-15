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
import csv
import os.path
import logging
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

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

# Create data structures
#
# Dictionary
#
# CSV columns
# columns = ["Date", "Day Start", "Project Abbrev", "Project Name",
#            "Project Start", "Project End", "Time Out", "Time In",
#            "Day End", "ID"]
#
# SQL database.
# with conn:
#     cur = conn.cursor()
#     cur.execute('CREATE TABLE if not exists timesheet(ID TEXT, Lead_name TEXT, Job_name TEXT, Job_abbrev TEXT, Start_time DATE\
#                 , Stop_time DATE, Date DATE, Stop_type TEXT, Break_end DATE)')

os.system('cls' if os.name == 'nt' else 'clear')


def query():
    """Prompts user for a yes/no answer

    if user responds with 'yes', 'ye', or 'y', return True
    if user responds with 'no' or 'n', return False
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
    """Prompts the user for project information, creates an id for
    recalling data (will be used in the future) and returns
    project name, project abbrev and id for use in other
    functions.
    """

    logging.debug("project_start called")
    clock_in = datetime.datetime.now()
    abbrev = raw_input("What are you working on? (ABBREV): ")
    project_name = raw_input("What is the name of this project?: ")
    lead_name = raw_input("For whom are you working?: ")
    pid = str(uuid.uuid4())
    logging.debug("UUID is {}".format(pid))
    logging.debug("abbrev is {}".format(abbrev))
    logging.debug("project_name is {}".format(project_name))
    print "DEBUGGING: PID = {}".format(pid)
#    with conn:
#        cur.execute(
#            "INSERT INTO timesheet(ID, Lead_name, Job_name, Job_abbrev, Start_time, Date) VALUES(?, ?, ?, ?, ?, ?)",
#            [pid, lead_name, project_name, abbrev, clock_in, date])
    global pid
    return pid


def round_to_nearest(num, b):
    """Rounds num to the nearest base

    round_to_nearest(7, 5) -> 5
    """

    company_minutes = num + (b // 2)
    return company_minutes - (company_minutes % b)


def calc_time(t):
    """Calculate days,hours,minutes,seconds from Timer"""

    seconds = t.seconds
    days = seconds // 60 // 60 // 24
    hours = seconds // 60 // 60
    minutes = seconds // 60
    seconds %= 60
    return (days, hours, minutes, seconds)


def break_submenu():
    print "What are you doing?\n" \
          "1. Lunch\n" \
          "2. Break\n"
    answer = raw_input(">>>")
    breaktime(answer)


def breaktime(answer):
    """Prompts user to specify reason for break.

    :param answer: takes user input from timer function
    :param data: data dictionary for job variables.
    answer: takes input from timer function

    No real reason for this other than just general bookkeeping.
    Not a requirement. Would be nice to be able to pause the timer for breaks,
    rather than having to start the script all over again.
    """

    # TODO: Upon entering, check if project has been set up (see if sql entry is in memory?), otherwise
    # an error is raised because some values are undefined.

    logging.debug("Called choices with answer: {}".format(answer))
    if answer.lower() in {'1', '1.', 'lunch'}:
        now = datetime.datetime.now()
        with conn:
            cur.execute(
                "SELECT ID, Job_name, Job_abbrev, Stop_type, Stop_time, Date FROM timesheet WHERE ID = ?",
                (pid,))
            sel = cur.fetchall()
            d = from_sqlite_Row_to_dict(sel)
            for row in sel:
                print "Stopping {0}, ABBREV {1} for lunch at {2} on {3}".format(row[1], row[2], row[4], row[5])
                job_name = row[1]
                job_abbrev = row[2]
                stop_type = row[3]
                stop_time = row[4]
                date = row[5]

            # TODO: Check if the current job's PID matches all entries for same abbrev on same date. This should
            # keep everything in order as far as time calculations. It should be as simple as subtracting break
            # time from total logged hours for each PID.

            cur.execute(
                "INSERT INTO timesheet(ID, Job_name, Job_abbrev, Stop_type, Stop_time, Date) VALUES(?, ?, ?, ?, ?, ?)", [
                    pid, job_name, job_abbrev, stop_type, now, date])
        print 'Bon appetit'
        logging.info("Lunch break at {}".format(datetime.datetime.now()))
        raw_input("Press Enter to begin working again")
        print(
            "Are you still working on  '{}' ? (y/n)").format(data['project_name'])
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}\n' ".format(data['project_name'], now)
            cur.execute(
                "INSERT INTO timesheet(ID, Job_name, Job_abbrev, Stop_type, Break_end, Date) VALUES(?, ?, ?, ?, ?, ?)", [
                    pid, job_name, job_abbrev, stop_type, now, date])
            main_menu(data)
        else:
            main_menu(data)
        logging.info("Back from lunch at {}".format(datetime.datetime.now()))
    elif answer.lower() in {'2', '2.', 'break'}:
        logging.info("Taking a break at {}".format(datetime.datetime.now()))
        raw_input("Press Enter to begin working again")
        print "Are you still working on {}? (y/n)".format(data['abbrev'])
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}' " % (data['project_name'], now)
            logging.info("Back from break at {}".format(now))
        else:
            main_menu(data)
    elif answer.lower() in {'3', '3.', 'heading home', 'home'}:
        print 'Take care!'
        logging.info("Clocked out at {}".format(datetime.datetime.now()))
        return "end of day"


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
    return datetime.datetime.strptime(time, '%I:%M %p')


def total_time():
    t_in = get_time(
        raw_input(
            "Please enter your start time in 00:00 AM/PM format: "))
    t_out = get_time(
        raw_input(
            "Please enter your end time in 00:00 AM/PM format: "))
    delta = t_out - t_in
    delta_minutes = float(round_to_nearest(delta.seconds, 360)) / 3600
    print("Your time sheet entry for {0} is {1}").format(delta, delta_minutes)


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
                # TODO: what should we do with time_formatter? Time adustments??
            except ValueError as e:
                print(e)
        if answer.startswith('6'):
            total_time()
        if answer.startswith('9'):
            break


if __name__ == "__main__":
    wr_timesheet = init_csv()
    main_menu()
