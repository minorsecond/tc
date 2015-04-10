# PYPER (Python Project Time Tracker)
# A timeclock program for project-based jobs
# Robert Ross Wardrup, NotTheEconomist, dschetel
# 08/31/2014

import time  # time.sleep requires this, but I'm sure there is an alternative to the sleep.
import datetime
import sys
import csv
import os.path
import select
import logging
import uuid

LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
LOGLEVEL = logging.INFO
logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)

sumtime = 0
project_time = 0
# CSV columns
columns = ["Date", "Day Start", "Project Abbrev", "Project Name",
           "Project Start", "Project End", "Time Out", "Time In",
           "Day End", "ID"]

# initialize dictionary
times = {'Date': 0, 'Day Start': 0, 'Project Abbrev': 0, 'Project Name': 0, 'Project Start': 0,
         'Project End': 0, 'Project Time': 0, 'Time Out': 0, 'Time In': 0, 'Day End': 0, 'pid': 0}

os.system('cls' if os.name == 'nt' else 'clear')


def query():
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
    abbrev = raw_input("What are you working on? (ABBREV) ")
    times['Project Abbrev'] = abbrev
    project_name = raw_input("What is the name of this project? ")
    times['Project Name'] = project_name
    pid = uuid.uuid4()
    times['pid'] = pid
    print "Entry UUID: %s" % pid
    time_start = datetime.datetime.now()
    print "----------------------------------------------"
    print "\n", 'Press enter to exit timer', '\n'

    print "The project elapsed time is: "
    timer(time_start, abbrev, project_name, pid)


def round_to_nearest(num, base=6):
    company_minutes = num + (base >> 1)
    return company_minutes - (company_minutes % base)


def timer(time_start, abbrev, project_name, pid):
    """
    Timer that ends upon user interaction. Uses round_to_nearest script to round to nearest
    six-minute interval, to comply with work requirements. Timedelta might be a better way
    of doing this. Something to look in to.
    """

    logging.debug("timer called")

    seconds = 0
    minutes = 0
    hours = 0

    while True:

        sys.stdout.write(
            "\r {hours} Hours {minutes} Minutes {seconds} Seconds".format(
                hours=hours, minutes=minutes, seconds=seconds))
        sys.stdout.flush()
        # TODO: Try print instead of stdout.
        date = datetime.datetime.now().date()
        now = datetime.datetime.now()
        seconds = 1 + (now - time_start).total_seconds()
        logging.info("seconds set to {}".format(seconds))
        hours = seconds // 60 // 60
        minutes = seconds // 60
        seconds %= 60
        logging.info("TIME SET! Hours: {}, Minutes: {}, Seconds: {}".format(
            hours, minutes, seconds))

        """
        The sys.stdin line prevents the timer from halting immediately when
        run. Without it, the key input that starts the timer is passed into
        raw_input in this if statement, causing the timer to never start.
        """

        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            # TODO: throws error in windows since sys.stdin is not a file.
            raw_input()
            print '\n', 'What are you doing? (lunch, home, break, switch task)'
            answer = raw_input()
            round_minutes = round_to_nearest(minutes)
            times['Project Time'] = round_minutes
            print"The timesheet time elapsed is: %s" % round_minutes
            # Make sure same ID is used for each abbrev code used. To help
            # check consistency.
            times_out = [date, day_start, abbrev, project_name, time_start,
                         "timeend_placeholder", "time_out_placeholder",
                         "placeholder", "time_in_placeholder", pid]
            wr_timesheet.writerow(times_out)
            choices(answer, abbrev, project_name, time_start)
        if seconds > 1:
            time.sleep(1)
            

def choices(answer, abbrev, project_name, time_start):
    """
    Prompts user to specify reason for break. No real reason for this other than
    just general bookkeeping. Not a requirement. Would be nice to be able to pause
    the timer for breaks, rather than having to start the script all over again.
    """
    logging.debug("Called choices with answer: {}".format(answer))
    if answer == 'lunch':
        print 'Bon appetit'
        ltimeout = datetime.datetime.now()
        logging.debug("ltimeout set to {}".format(ltimeout))
        quit()
    elif answer == 'home':
        print 'Take care!'
        hometime = datetime.datetime.now()
        logging.debug("hometime set to {}".format(hometime))
        quit()
    elif answer == 'break':
        breaktime = datetime.datetime.now()
        logging.debug("breaktime set to {}".format(breaktime))
        raw_input("Press Enter to begin working again")
        print "Are you still working on %s? (y/n)" % abbrev
        query()
        if True:
            time_start = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}' " % (project_name, time_start)
        else:
            quit()  # don't want to quit the program - pause it.
    else:
        quit()


def init_csv(filename="times.csv"):
    """Initializes the csv.writer based on its filename
    init_csv('file.csv') -> csv.writer(open('file.csv', 'a'))
    creates file if it doesn't exist, and writes some default columns as a
    header"""

    logging.debug("Called init_csv")
    if os.path.isfile(filename):
        logging.debug("{} already exists -- opening".format(filename))
        wr_timesheet = csv.writer(open(filename, "a"))
        logging.info("{} opened as a csv.writer".format(filename))
    else:
        logging.debug("{} does not exist -- creating".format(filename))
        wr_timesheet = csv.writer(open(filename, "w"))
        logging.info("{} created and opened as a csv.writer".format(wr_timesheet))
        wr_timesheet.writerow(columns)
        logging.debug("{} initialized with columns: {}".format(
            filename, columns))
    return wr_timesheet


wr_timesheet = init_csv("times.csv")

print "\n"
print "Hello there. I will log your project time and create a" \
      " .csv file with the results."
print "Your current logged time for this week is: ", sumtime
print "\n"
print "-----------------------------------------------------------"
raw_input("Please press <ENTER> to log current time and begin your day")
print "\n"
day_start = datetime.datetime.now()
print "The day's start time is ", day_start
project_start()





