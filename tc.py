# A timeclock program for project-based jobs
# Robert Ross Wardrup
# 08/31/2014

import time
import datetime
import sys
import csv
import os.path
import select

os.system('cls' if os.name == 'nt' else 'clear')

wr = csv.writer(open("times.csv", "wb"))
if os.path.isfile("times.csv"):
    columns = ["Date", "Day Start", "Project Abbrev", "Project Start", "Project End", "Time Out" "Time In", "Day End", "ID"]
    wr.writerow(columns)

def timer():
    seconds = 0
    minutes = 0
    hours = 0
    while True:

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

			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				raw_input()
				print '\n','What are you doing? (lunch, home, break, switch task)'
				answer = raw_input()
				choices(answer)
				

def choices(answer):
	if answer == 'lunch':
		print 'Bon appetit'
		ltimeout = time.time()
		quit()
	elif answer == 'home':
		print 'Take care!'
		hometime = time.time()
		quit()
	elif answer == 'break':
		breaktime = time.time()
		quit()
	else:
		quit()

sumtime = 0
projTime = 0

print "\n"
print "Hello there. I will log your project time and create a .csv file with the results."
print "Your current logged time for this week is: ", sumtime
print "\n"
print "-----------------------------------------------------------"
raw_input("Please press <ENTER> to log current time and begin your day")
print "\n"
Daybegin = datetime.datetime.now()

raw_input("What are you working on? (ABBREV) ")
ABBREV = raw_input

print
time_start = time.time()


print "----------------------------------------------"
print "The day's start time is ", Daybegin
print "\n", 'Press enter to exit timer', '\n'

print "The project elapsed time is: "
timer()
