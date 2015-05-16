"""
This script creates a timestamped database backup,
and cleans backups older than a set number of dates

"""

from __future__ import print_function
from __future__ import unicode_literals

import shutil
import time
import os

DESCRIPTION = """
              Create a timestamped SQLite database backup, and
              clean backups older than a defined number of days
              """

# How old a file needs to be in order
# to be considered for being removed
NO_OF_DAYS = 14


def sqlite3_backup(dbfile, backupdir):
    """Create timestamped database copy"""

    if not os.path.isdir(backupdir):
        raise Exception("Backup directory does not exist: {}".format(backupdir))

    backup_file = os.path.join(backupdir, os.path.basename(dbfile) +
                               time.strftime("-%Y%m%d-%H%M%S"))

    # Make new backup file
    shutil.copyfile(dbfile, backup_file)
    print("\nCreating {}...".format(backup_file))


def clean_data(backup_dir):
    """Delete files older than 14 days"""

    print("\n------------------------------")
    print("Cleaning up old backups")

    for filename in os.listdir(backup_dir):
        backup_file = os.path.join(backup_dir, filename)
        if os.stat(backup_file).st_ctime < (time.time() - NO_OF_DAYS * 86400):
            if os.path.isfile(backup_file):
                os.remove(backup_file)
                print("Deleting {}...".format(backup_file))


if __name__ == "__main__":
    sqlite3_backup(args.db_file, args.backup_dir)
    clean_data(args.backup_dir)

    print("\nBackup update has been successful.")