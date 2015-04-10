# A timeclock program for project-based jobs
# Robert Ross Wardrup
# 08/31/2014

import time # why are we using both time and datetime?
import datetime
import sys
import csv
import os.path
import select
import logging

LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
LOGLEVEL = logging.INFO

logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)

sumtime = 0
project_time = 0

os.system('cls' if os.name == 'nt' else 'clear')

def timer():
    # TODO: Docstring
    logging.debug("timer called")
    while True:

        sys.stdout.write(
            "\r {hours} Hours {minutes} Minutes {seconds} Seconds".format(
                hours=hours, minutes=minutes, seconds=seconds))
        sys.stdout.flush()
        # why not just print? Is there some cross-platform reason I'm missing?
        now = datetime.datetime.now()
        seconds = (now - time_start).total_seconds
        logging.info("seconds set to {}".format(seconds))
        hours = seconds // 60 // 60
        minutes = seconds // 60
        seconds %= 60
        logging.info("TIME SET! Hours: {}, Minutes: {}, Seconds: {}".format(
                hours, minutes, seconds))

        # TODO: more comments here please! No idea what this does
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            # TODO: throws error in windows since sys.stdin is not a file
            raw_input()
            print '\n', 'What are you doing? (lunch, home, break, switch task)'
            answer = raw_input()
            times_out = ["holder", day_start, abbrev, project_name, time_start,
                         "placeholder", "placeholder", "placeholder",
                         "placeholder", " placeholder"]
            wr.writerow(times_out)
            choices(answer)
	time.sleep(1)


def choices(answer):
    # TODO: Docstring
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
        quit()
    else:
        quit()

def init_csv(filename="times.csv"):
    """Initializes the csv.writer based on its filename

    init_csv('file.csv') -> csv.writer(open('file.csv', 'a'))
    creates file if it doesn't exist, and writes some default columns as a
    header"""

    columns = ["Date", "Day Start", "Project Abbrev", "Project Name",
               "Project Start", "Project End", "Time Out", "Time In",
               "Day End", "ID"]
    # isn't this used when writing each time in/out, too? Possibly factor
    # into a global

    logging.debug("Called init_csv")
    if os.path.isfile(filename):
        logging.debug("{} already exists -- opening".format(filename))
        wr = csv.writer(open(filename, "a"))
        logging.info("{} opened as a csv.writer".format(filename))
    else:
        logging.debug("{} does not exist -- creating".format(filename))
        wr = csv.writer(open(filename, "w"))
        logging.info("{} created and opened as a csv.writer".format(wr))
        wr.writerow(columns)
        logging.debug("{} initialized with columns: {}".format(
            filename, columns))
    return wr

wr = init_csv("times.csv")

print "\n"
print "Hello there. I will log your project time and create a" \
      " .csv file with the results."
print "Your current logged time for this week is: ", sumtime
print "\n"
print "-----------------------------------------------------------"
raw_input("Please press <ENTER> to log current time and begin your day")
print "\n"

day_start = datetime.datetime.now()

abbrev = raw_input("What are you working on? (ABBREV) ")
project_name = raw_input("What is the name of this project? ")

print
time_start = datetime.datetime.now()

print "----------------------------------------------"
print "The day's start time is ", day_start
print "\n", 'Press enter to exit timer', '\n'

print "The project elapsed time is: "
timer()

