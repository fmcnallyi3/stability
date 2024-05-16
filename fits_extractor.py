#!/usr/bin/env python

import argparse
import re
import json
import healpy as hp
from glob import glob
from collections import defaultdict

from grl_reader import get_livetime, get_bad_runs
import directories as stab


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Extract and store events and livetime for fits files')
    p.add_argument('-c', '--config', dest='config',
            help='Detector configuration to process [IC86-2011 - IC86-2022]')
    args = p.parse_args()

    # Establish default project-specific paths
    stab.setup_dirs()

    # Storage structure: fits_data[cfg][day][events|livetime]
    fits_data = defaultdict(lambda: defaultdict(
                            lambda: defaultdict(int)))

    # Extract detector livetime and bad runs from good run list
    print('Loading livetimes from i3live...')
    goodrunfile = f'{stab.data}/goodrunlist.txt'
    run2cfg = f'{stab.data}/run2cfg.json'
    i3live = get_livetime(goodrunfile, run2cfg)
    badruns = get_bad_runs(goodrunfile)

    # Find events for each day
    #map_dir = '/data/ana/CosmicRay/Anisotropy/IceCube/twelve_year/maps'
    map_dir = f'/data/user/fmcnally/anisotropy/maps/{args.config}'
    fits_files = sorted(glob(f'{map_dir}/*sid_????-??-??.fits'))

    print(f'Working on {args.config} ({len(fits_files)} files found)...')
    # Run through each fits file
    for map_file in fits_files:

        # Read fits file
        map_i = hp.read_map(map_file, verbose=0)
        date = re.split('_|\.', map_file)[-2]

        # Calculate runtime
        try: t_i3 = sum([t_run for r, t_run in i3live[args.config][date].items()
                if r not in badruns])
        except KeyError:
            print(f'Date {date} not found in i3live for {args.config}!')
            t_i3 = 0

        # Save information in dictionary
        fits_data[args.config][date]['events'] = int(map_i.sum())
        fits_data[args.config][date]['livetime'] = int(t_i3)

    with open(f'{stab.fits_out}/sum_{args.config}.json', 'w') as f:
        json.dump(fits_data, f)





