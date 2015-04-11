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
import threading

LOGFILE = "timeclock.log"
FORMATTER_STRING = r"%(levelname)s :: %(asctime)s :: in " \
                   r"%(module)s | %(message)s"
LOGLEVEL = logging.INFO
logging.basicConfig(filename=LOGFILE, format=FORMATTER_STRING, level=LOGLEVEL)

sumtime = 0
project_time = 0


class Timer(threading.Thread):
    """Timer thread to track job timing

    initialized with `project_name` and `abbr` fields, the timer will keep running
    until you you call `the_timer.stop()`

    Timer.seconds -> int
        how many seconds have passed since timer start
        this respects time paused!
    Timer.time_paused -> int
        how much time has been spend paused, in seconds
    Timer.pause(reason) -> None
        pauses the timer
    Timer.unpause -> None
        unpauses the timer
    """

    def __init__(self, project_name, abbrev, pid, *args, **kwargs):
        super(Timer, self).__init__(*args, **kwargs)
        self._running = True
        self.start_time = datetime.datetime.now()
        self.pause_times = []
        self.project_name = project_name
        self.abbrev = abbrev
        self.pid = pid
        self.paused = False
        # TODO: should probably make a clockline object that can store some
        # of this information rather than keeping it all in Timer.

    @property
    def time_paused(self):
        if self.pause_times:
            return sum((pause.get('stop', datetime.datetime.now()) - \
                        pause['start']).total_seconds() for \
                       pause in self.pause_times)
        else:
            return 0

    @property
    def seconds(self):
        now = datetime.datetime.now()
        return (now - self.start_time).total_seconds() - self.time_paused

    def pause(self, reason):
        if self.paused:
            msg = "Can't pause {!r} since it's already paused!".format(self)
            logging.error(msg)
            raise ValueError(msg)
        p = {'start': datetime.datetime.now(),
             'reason': reason}
        self.pause_times.append(p)
        self.paused = True

    def unpause(self):
        if not self.paused:
            msg = "Can't unpause {!r} since it's not paused!".format(self)
            logging.error(msg)
            raise ValueError(msg)
        p = self.pause_times[-1]
        p['stop'] = datetime.datetime.now()
        self.paused = False

    def stop(self):
        logging.info("{!r} stopped".format(self))
        self._running = False

    def run(self):
        while self._running:
            pass
        return self.seconds

# CSV columns
columns = ["Date", "Day Start", "Project Abbrev", "Project Name",
           "Project Start", "Project End", "Time Out", "Time In",
           "Day End", "ID"]

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
    logging.debug("project_start called")
    abbrev = raw_input("What are you working on? (ABBREV) ")
    project_name = raw_input("What is the name of this project? ")
    pid = uuid.uuid4()
    logging.debug("UUID is {}".format(pid))
    logging.debug("abbrev is {}".format(abbrev))
    logging.debug("project_name is {}".format(project_name))
    return {'project_name': project_name,
            'abbrev': abbrev,
            'pid': pid}


def round_to_nearest(num, base=6):
    """Rounds num to the nearest base

    round_to_nearest(7, 5) -> 5
    """

    company_minutes = num + (base // 2)
    return company_minutes - (company_minutes % base)


def calc_time(t):
    """Calculate days,hours,minutes,seconds from Timer"""

    seconds = t.seconds
    days = seconds // 60 // 60 // 24
    hours = seconds // 60 // 60
    minutes = seconds // 60
    seconds %= 60
    return (days, hours, minutes, seconds)


def timer(t):
    """Timer that ends upon user interaction. Uses round_to_nearest script
    to round to nearest six-minute interval,
    to comply with work requirements.
    """

    logging.debug("timer called")

    days, hours, minutes, seconds = calc_time(t)
    print "{days} Days {hours} Hours {minutes} Minutes {seconds} Seconds".format(
        days=days, hours=hours, minutes=minutes, seconds=seconds)

    while True:

        date = t.start_time.date()  # day the timer started
        seconds = t.seconds
        logging.info("seconds set to {}".format(seconds))
        hours = seconds // 60 // 60
        minutes = seconds // 60
        seconds %= 60
        logging.debug("TIME SET! Hours: {}, Minutes: {}, Seconds: {}".format(
            hours, minutes, seconds))

        print "What are you doing?\n" \
              "1. Lunch\n" \
              "2. Break\n" \
              "3. Heading home\n" \
              "4. Switching tasks\n"
        answer = raw_input(">>>")
        response = choices(answer, t)

        # Recalculate so we have accurate end times
        days, hours, minutes, seconds = calc_time(t)
        print "{days} Days {hours} Hours {minutes} Minutes {seconds} Seconds".format(
            days=days, hours=hours, minutes=minutes, seconds=seconds)

        round_minutes = round_to_nearest(minutes, 6)

        # times['Project Time'] = round_minutes  # TODO: factor out since I removed times dict
        print"The timesheet time elapsed is: {:.0f}m".format(round_minutes)
        # Make sure same ID is used for each abbrev code used. To help
        # check consistency.

        # let's refactor this into a clocktime object that knows how to write itself
        # especially since we REALLY only need to write to this when we clock out
        times_out = [date, day_start, t.abbrev, t.project_name, t.start_time,
                     "timeend_placeholder", "time_out_placeholder",
                     "placeholder", "time_in_placeholder", t.pid]
        wr_timesheet.writerow(times_out)

        if response == "end of day":
            quit()

            # time.sleep(1)
            # since we're waiting for user input, we really don't need this


def begin(t):
    """
    Asks user for proect abbrev and name, and kicks off the timer.
    This is probably going to be reused several times so I thought
    it prudent to just make it a function.
    """

    project = project_start()
    t = Timer(project['project_name'], project['abbrev'], project['pid'])
    t.daemon = True
    t.start()
    timer(t)


def choices(answer, t):
    """Prompts user to specify reason for break.

    No real reason for this other than just general bookkeeping.
    Not a requirement. Would be nice to be able to pause the timer for breaks,
    rather than having to start the script all over again.
    """

    logging.debug("Called choices with answer: {} on Timer {!r}".format(answer, t))
    if answer.lower() in {'1', '1.', 'lunch'}:
        print 'Bon appetit'
        t.pause("lunch")
        logging.info("Lunch break at {}".format(datetime.datetime.now()))
        raw_input("Press Enter to begin working again")
        print("Are you still working on  '{}' ? (y/n)").format(t.project_name)
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}' ".format(t.project_name, now)
            t.unpause()
        else:
            begin(t)

        logging.info("Back from lunch at {}".format(datetime.datetime.now()))
    elif answer.lower() in {'2', '2.', 'break'}:
        logging.info("Taking a break at {}".format(datetime.datetime.now()))
        t.pause("break")
        raw_input("Press Enter to begin working again")
        print "Are you still working on {}? (y/n)".format(t.abbrev)
        answer = query()
        if answer:
            now = datetime.datetime.now()
            print "Resuming '{0}' at: '{1}' " % (t.project_name, now)
            t.unpause()
            logging.info("Back from break at {}".format(now))
        else:
            # If they're back from break, but NO LONGER working on that job,
            # I think we should prompt to change jobs somehow
            project_start()
    elif answer.lower() in {'3', '3.', 'heading home', 'home'}:
        print 'Take care!'
        logging.info("Clocked out at {}".format(datetime.datetime.now()))
        t.stop()
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


if __name__ == "__main__":
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
    begin(t)
