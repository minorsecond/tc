# A timeclock program for project-based jobs
# Robert Ross Wardrup
# 08/31/2014

import time
import datetime
import sys
import csv
import os.path


def timer():
    seconds = 0
    minutes = 0
    hours = 0
    while True:
		try:
			sys.stdout.write("\r {hours} Hours {minutes} Minutes {seconds} Seconds".format(hours=hours, minutes=minutes, seconds=seconds))
			sys.stdout.flush()
			time.sleep(1)
			seconds = int(time.time() - time_start) - minutes * 60
			if seconds >= 60:
				minutes += 1
				seconds = 0
			if minutes >= 60:
				hours += 1
				minutes = 0
		except KeyboardInterrupt, e:
			break

wr = csv.writer(open("times.csv", "wb"))
if os.path.isfile("times.csv"):
    columns = ["Date", "Day Start", "Project Abbrev", "Project Start", "Time Out" "Time In", "Project End", "Day End"]
    wr.writerow(columns)

sumtime = 0

"""Hello there. I will log your project time and create a .csv file with the results."""
print "Your current logged time for this week is: ", sumtime
print "\n"
raw_input("Please press <ENTER> to log current time and begin your day")
print "\n"

Daybegin = datetime.datetime.now()
time_start = time.time()


print "----------------------------------------------"
print "The day's start time is ", Daybegin
print "\n"

print "The project elapsed time is: "
timer()
print "----------------------------------------------"