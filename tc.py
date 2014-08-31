# A timeclock program for project-based jobs
# Robert Ross Wardrup
# 08/31/2014

import time
import datetime
import sys
import csv

with open('times.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='    ', quotechar='|')

sumtime = 0

"""Hello there. I will log your project time and create a .csv file with the results."""
print "Your current logged time for this week is: ", sumtime
print "\n"
raw_input("Please press <ENTER> to log current time and begin your day")
print "\n"

Daybegin = datetime.datetime.now()
time_start = time.time()
seconds = 0
minutes = 0
hours = 0

print "The day's start time is ", Daybegin

def timer():
    while True:
		try:
			sys.stdout.write("\r{hours} Hours {minutes} Minutes {seconds} Seconds".format(minutes=minutes, seconds=seconds))
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