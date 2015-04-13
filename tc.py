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
import sqlite3

LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
conn = sqlite3.connect('timesheet.db')
LOGLEVEL = logging.INFO
logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)

date = str(datetime.date.today())
day_start = datetime.datetime.now()


# Create data structures

# CSV columns
columns = ["Date", "Day Start", "Project Abbrev", "Project Name",
           "Project Start", "Project End", "Time Out", "Time In",
           "Day End", "ID"]

# SQL database.
with conn:
    cur = conn.cursor()
    cur.execute('CREATE TABLE if not exists timesheet(ID TEXT, Lead_name TEXT, Job_name TEXT, Job_abbrev TEXT, Start_time DATE\
                , Stop_time DATE, Date DATE, Stop_type TEXT, Break_end DATE)')

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
    """
    Prompts the user for project information, creates an id for
    recalling data (will be used in the future) and returns
    project name, project abbrev and id for use in other
    functions.
    """
    global pid
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
    with conn:
        cur.execute(
            "INSERT INTO timesheet(ID, Lead_name, Job_name, Job_abbrev, Start_time, Date) VALUES(?, ?, ?, ?, ?, ?)",
            [pid, lead_name, project_name, abbrev, clock_in, date])
    return pid


def round_to_nearest(num, b):
    """Rounds num to the nearest base

    round_to_nearest(7, 5) -> 5
    """

    company_minutes = num + (b // 2)
    return company_minutes - (company_minutes % b)


def break_submenu():
    print "What are you doing?\n" \
          "1. Lunch\n" \
          "2. Break\n"
    answer = raw_input(">>>")
    breaktime(answer)


def from_sqlite_Row_to_dict(list_with_rows):
    """

    :param list_with_rows: give list from sqlite db
    :param keys: names of sqlite db columns. This MUST be provided in the same order as your SELECT query.
    :return: a dictionary containing the keys and values from sqlite db
    """
    d = {}  # the dictionary to be filled with the row data and to be returned

    for i, row in enumerate(list_with_rows):  # iterate throw the sqlite3.Row objects
        l = []  # for each Row use a separate list
        for col in range(0, len(row)):  # copy over the row date (ie. column data) to a list
            l.append(row[col])
        d[i] = l  # add the list to the dictionary
    return d


def breaktime(answer):
    """Prompts user to specify reason for break.

    :param answer: takes user input from timer function
    :param data: data dictionary for job variables.
    answer: takes input from timer function

    No real reason for this other than just general bookkeeping.
    Not a requirement. Would be nice to be able to pause the timer for breaks,
    rather than having to start the script all over again.
    """

    with conn:
        cur.execute(
            "SELECT ID, Job_name, Job_abbrev, Stop_type, Stop_time, Date FROM timesheet WHERE ID = ?", (pid,))
        sel = cur.fetchall()

        for row in sel:
            job_name = row[1]
            job_abbrev = row[2]
            stop_type = row[3]
            stop_time = row[4]
            date = row[5]

    # TODO: Upon entering, check if project has been set up (see if sql entry is in memory?), otherwise
    # an error is raised because some values are undefined.

    logging.debug("Called choices with answer: {}".format(answer))
    if answer.lower() in {'1', '1.', 'lunch'}:
        now = datetime.datetime.now()
        for row in sel:
            print "Stopping {0}, ABBREV {1} for lunch at {2} on {3}".format(row[1], row[2], row[4], row[5])

            # TODO: Check if the current job's PID matches all entries for same abbrev on same date. This should
            # keep everything in order as far as time calculations. It should be as simple as subtracting break
            # time from total logged hours for each PID.

            cur.execute(
                "INSERT INTO timesheet(ID, Job_name, Job_abbrev, Stop_type, Stop_time, Date) VALUES(?, ?, ?, ?, ?, ?)",
                [pid, job_name, job_abbrev, stop_type, now, date])
        print 'Bon appetit'
        logging.info("Lunch break at {}".format(datetime.datetime.now()))
        raw_input("Press Enter to begin working again")
        print("Are you still working on  '{}' ? (y/n)").format(job_name)
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}\n' ".format(job_name, now)
            cur.execute(
                "INSERT INTO timesheet(ID, Job_name, Job_abbrev, Stop_type, Break_end, Date) VALUES(?, ?, ?, ?, ?, ?)",
                [pid, job_name, job_abbrev, stop_type, now, date])
            main_menu(data)
        else:
            main_menu(data)
        logging.info("Back from lunch at {}".format(datetime.datetime.now()))
    elif answer.lower() in {'2', '2.', 'break'}:
        logging.info("Taking a break at {}".format(datetime.datetime.now()))
        raw_input("Press Enter to begin working again")
        print "Are you still working on {}? (y/n)".format(job_name)
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}' " % (job_name, now)
            logging.info("Back from break at {}".format(now))
        else:
            main_menu()
    elif answer.lower() in {'3', '3.', 'heading home', 'home'}:
        print 'Take care!'
        logging.info("Clocked out at {}".format(datetime.datetime.now()))
        return "end of day"


def init_csv(filename="times.csv"):
    """Initializes the csv.writer based on its filename

    init_csv('file.csv') -> csv.writer(open('file.csv', 'a'))
    creates file if it doesn't exist, and writes some default columns as a
    header
    """

    logging.debug("Called init_csv")
    if os.path.isfile(filename):
        logging.debug("{} already exists -- opening".format(filename))
        wr_timesheet = csv.writer(open(filename, "a"))
        logging.info("{} opened as a csv.writer".format(filename))
    else:
        logging.debug("{} does not exist -- creating".format(filename))
        wr_timesheet = csv.writer(open(filename, "w"))
        logging.info("{} created and opened as a csv.writer".format(
            wr_timesheet))
        wr_timesheet.writerow(columns)
        logging.debug("{} initialized with columns: {}".format(
            filename, columns))
    return wr_timesheet


def time_formatter():
    """
    Takes user input as 00:00, splits those using : as seperator,
    and prints the time formatted for timesheet in tenths of an
    hour
    """
    time_input = raw_input("\nTime Formatter\n" \
                           "Please enter hours and minutes worked today" \
                           "in 00:00 format: ")
    if len(time_input.split(':')) == 2:
        split_hours = time_input.split(':')[0]
        split_minutes = time_input.split(':')[1]
        round_minutes = round_to_nearest(int(split_minutes))
        print "Your timesheet entry is {0}:{1}".format(split_hours, round_minutes)
        main_menu()
    else:
        print "Please check input format and try again. (00:00)"
        time_formatter()


def get_time(time):
    return datetime.datetime.strptime(time, '%I:%M %p')


def total_time():
    t_in = get_time(raw_input("Please enter your start time in 00:00 AM/PM format: "))
    t_out = get_time(raw_input("Please enter your end time in 00:00 AM/PM format: "))
    delta = t_out - t_in
    delta_minutes = float(round_to_nearest(delta.seconds, 360)) / 3600
    print("Your time sheet entry for {0} is {1}").format(delta, delta_minutes)


def main_menu():
    """
    Main menu for program. Prompts user for function.
    Currently, options one and two are unused but
    can't be commented out.
    """
    print "PYPER Timesheet Utility\n\n" \
          "What would you like to do?\n" \
          "1. Clock In\n" \
          "2. Break Time\n" \
          "3. Clock Out\n" \
          "4. Set up obs/break types\n" \
          "5. Timesheet Minute Formatter\n" \
          "6. Calculate Total Time Worked\n"
    answer = raw_input(">>> ")
    if answer.lower() in {'1', '1.'}:
        project_start()
        main_menu()
    if answer.lower() in {'2', '2.'}:
        break_submenu()
    # if answer.lower() in {'3', '3.'}:
    if answer.lower() in {'5', '5.'}:
        time_formatter()
    if answer.lower() in {'6', '6.'}:
        total_time()


if __name__ == "__main__":
    wr_timesheet = init_csv()
    main_menu()