#!/usr/bin/env python

import os, re, argparse
from glob import glob
import datetime as dt


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Makes daily healpix maps using time-scrambling code')

    # General parameters
    p.add_argument('-c', '--config', dest='config',
            help='Detector configuration [IC86-2011,IC86-2012,IC86-2013...]')
    p.add_argument('-d', '--dates', dest='dates', type=str,
            default=None, nargs='*',
            help='Dates to process [yyyy-mm-dd]')
    p.add_argument('--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Option to overwrite existing map files')

    args = p.parse_args()


    # Collect input files
    fileList = []
    root_dir = '/data/ana/CosmicRay/Anisotropy/IceCube'
    root_path = f'{root_dir}/{args.config}'
    masterList = glob(f'{root_path}/*.root')
    # Newer configurations use directories for each day
    if masterList == []:
        masterList = glob(f'{root_path}/*/*.root')
    masterList.sort()

    for rootFile in masterList:

        # Filter by desired dates
        date = re.findall('\d{4}-\d{2}-\d{2}', rootFile)[-1]
        if date not in args.dates:
            continue

        # Apply naming conventions to find existing files
        # ...
        # Overwrite or omit existing files
        #if all([os.path.isfile(f) for f in testFiles]) and not args.overwrite:
        #    continue
        #for testFile in testFiles:
        #    if os.path.isfile(testFile):
        #        os.remove(testFile)

        fileList.append(rootFile)

    # Split into days for submission
    dateList = [re.findall('\d{4}-\d{2}-\d{2}', f)[-1] for f in fileList]
    dateList = sorted(list(set(dateList)))  # Limit to unique values

    # "Day" files are not actually 24 hours
    # Include previous and next runs (or full days when necessary)
    prev_dates, next_dates = [], []
    for date_str in dateList:
        yyyy, mm, dd = [int(i) for i in date_str.split('-')]
        date = dt.datetime(yyyy, mm, dd)
        prev_dates += [(date + dt.timedelta(days=-1)).strftime('%Y-%m-%d')]
        next_dates += [(date + dt.timedelta(days=1)).strftime('%Y-%m-%d')]

    # Collect surrounding files to allow runs from midnight to midnight
    # ("Daily" files grouped by run, not actually 24 hours)
    dayFiles = []
    for day, prev, post in zip(dateList, prev_dates, next_dates):

        prev_files = [f for f in masterList if prev in f]
        # Reduce list of previous files to only the run right before
        if any(['run' in f for f in prev_files]):
            runlist = [re.findall('run\d{6}',f)[-1] for f in prev_files]
            runlist = sorted(set(runlist))
            prev_files = [f for f in prev_files if runlist[-1] in f]

        post_files = [f for f in masterList if post in f]
        # Reduce list of next day files to only the run right after
        if any(['run' in f for f in post_files]):
            runlist = [re.findall('run\d{6}',f)[-1] for f in post_files]
            runlist = sorted(set(runlist))
            post_files = [f for f in post_files if runlist[0] in f]

        one_day = [f for f in masterList if day in f]

        dayFiles += [prev_files + one_day + post_files]

    dayFiles = [' '.join(oneDay)+'\n' for oneDay in dayFiles]

    for day in dayFiles:
        os.system(f'./esf_correction.py -i {day}')
