This folder contains scripts to correct duplicate errors -- events in
ROOT files that share the same exact values (MJD, zenith, etc.) except subevent

## Files

`duplicate_check.py`
 - Plots duplicate rates as a function of detector year using .json files
   output by duplicate_finder.py

`duplicate_correction.py`
 - Removes all duplicates from a given root file, saving a new, reduced tree as
   a _dupfix in the same location

`duplicate_finder.py`
 - Counts and stores the number of duplicates in all root files for a given
   detector configuration

`README.md`
 - this file


## Process

 - Requires uproot python package
    - using pzilberman's venv: 
      source /home/pzilberman/venvs/custom_py3-v4.3.0_cobalt/bin/activate

 - Identify 864 errors using rate_check.py in parent directory
 - Run esf_submitter.py with the bad dates
