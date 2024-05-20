#!/usr/bin/env python

##==========================================================================##
## Establishes directory structure for file locations and output data       ##
##==========================================================================##

import os

def setup_dirs(verbose=True):

    current = os.path.dirname(os.path.realpath(__file__))
    user = os.environ['USER']

    globalVals = globals().keys()
    global home, data, root_out, fits_out, rate_plots
    home = current
    data = f'/data/user/{user}/stability'
    root_out = f'{data}/root_summaries'
    fits_out = f'{data}/fits_summaries'
    rate_plots = f'{data}/rate_plots'

    # Make sure the desired output paths exist
    # If something is broken, it's probably this (didn't test it!)
    for output_path in [data, root_out, fits_out, rate_plots]:
        os.makedirs(output_path, exist_ok=True)

if __name__ == "__main__":

    setup_dirs()
