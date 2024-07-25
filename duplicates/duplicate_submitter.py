#!/usr/bin/env python

import re, sys, argparse
from pathlib import Path

# Cluster submission from submitter folder
path_to_file = Path(__file__).resolve()
parent_dir = str(path_to_file.parents[1])
sys.path.append(parent_dir)

from submitter.pysubmit import pysubmit


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Submits daily jobs for removing duplicate events')

    # General parameters
    p.add_argument('-c', '--config', dest='config',
            help='Detector configuration [IC86-2011,IC86-2012,IC86-2013...]')
    p.add_argument('-d', '--dates', dest='dates', type=str,
            default=None, nargs='*',
            help='Dates to process [yyyy-mm-dd]')
    p.add_argument('-o', '--overwrite', dest='overwrite',
            default=False, action='store_true',
            help='Overwrite existing "dupfix" files')

    args = p.parse_args()


    # Collect input files
    root_path = Path(f'/data/ana/CosmicRay/Anisotropy/IceCube/{args.config}')
    file_list = sorted(root_path.rglob('*.root'))

    # Skip already-processed files by default
    if not args.overwrite:
        file_list = [str(f) for f in file_list 
                if not Path.is_file(f.with_name(f.stem+'_dupfix.root'))]

    # Processes all dates if none given
    if args.dates == None:
        date_list = [re.findall('\d{4}-\d{2}-\d{2}', f)[-1] 
                for f in file_list]

    # Environment for script
    npx_out = f'{parent_dir}/submitter'
    sublines = ["getenv = True"]
    # Require extra memory for earlier years where the files are larger
    if int(args.config[-4:]) < 2016:
        sublines += ["request_memory = 4000"]

    # Split into days for submission
    date_list = sorted(set(date_list))      # Limit to unique values
    for day in date_list:
        day_files = [f for f in file_list if day in f]
        day_str = ' '.join(day_files)

        cmd = f'./duplicate_correction.py -i {day_str}'

        pysubmit(cmd, npx_out, sublines=sublines)


