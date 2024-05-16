#!/usr/bin/env python

import json
from glob import glob
import directories as stab

if __name__ == "__main__":

    # Establish default project-specific paths
    stab.setup_dirs()

    # Storage structure: fits_data[cfg][day][events|livetime]
    fits_data = {}

    summary_files = sorted(glob(f'{stab.fits_out}/*.json'))

    for summary_file in summary_files:

        with open(summary_file, 'r') as f:
            cfg_data = json.load(f)

        fits_data.update(cfg_data)

    with open(f'{stab.data}/fits_summary.json', 'w') as f:
        json.dump(fits_data, f)

