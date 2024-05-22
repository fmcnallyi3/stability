#!/usr/bin/env python

import numpy as np
import json
from datetime import datetime as dt


""" Extract bad runs from good run file """
def get_bad_runs(goodrunfile):

    badruns = []

    # Load I3 good run list from json file
    with open(goodrunfile, 'r') as f:
        i3_data = json.load(f)
        i3_data = i3_data['runs']

    for run_info in i3_data:
        if run_info['good_i3'] == False:
            badruns.append(str(run_info['run']))

    return sorted(set(badruns))



""" Extract livetimes from good run file """
def get_livetime(goodrunfile, run2cfgfile):

    i3_livetime = {}

    # Load I3 good run list from json file
    with open(goodrunfile, 'r') as f:
        i3_data = json.load(f)
        i3_data = i3_data['runs']

    # Load run2cfg dictionary from json file
    with open(run2cfgfile, 'r') as f:
        run2cfg = json.load(f)

    for run_info in i3_data:

        # Instate each day as a key for the dictionary
        day = run_info['good_tstart'].split(' ')[0]
        run = str(run_info['run'])

        # Ignore runs that are before/after the dates of the run dictionary
        try: cfg = run2cfg[run]
        except KeyError:
            continue

        if cfg not in i3_livetime.keys():
            i3_livetime[cfg] = {}
        if day not in i3_livetime[cfg].keys():
            i3_livetime[cfg][day] = {}

        # Deal with null livetimes
        if run_info['good_tstop'] == None:
            #i3_livetime[cfg][day][run] = 'null'
            i3_livetime[cfg][day][run] = np.nan
            continue

        # Obtain start/stop times from list, removing fractions of seconds
        t_i = run_info['good_tstart'].split('.')[0]
        start_t = dt.strptime(t_i, '%Y-%m-%d %H:%M:%S')
        t_f = run_info['good_tstop'].split('.')[0]
        stop_t = dt.strptime(t_f, '%Y-%m-%d %H:%M:%S')

        # Check if run crosses over a day and adjust start/stop times
        if start_t.day != stop_t.day:
            day_aft = stop_t.strftime('%Y-%m-%d')
            if day_aft not in i3_livetime[cfg].keys():
                i3_livetime[cfg][day_aft] = {}
            midnight = dt.combine(stop_t, dt.min.time())
            i3_livetime[cfg][day][run] = (midnight - start_t).seconds
            i3_livetime[cfg][day_aft][run] = (stop_t - midnight).seconds

        # If no crossover, the run is fully contained in a day
        else:
            i3_livetime[cfg][day][run] = (stop_t - start_t).seconds

    return i3_livetime

