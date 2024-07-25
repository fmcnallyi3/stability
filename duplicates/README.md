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

`duplicate_submitter.py`
 - Runs duplicate_correction.py over an entire year of data, submitting to the
   cluster

`README.md`
 - this file


## Process

 - Requires uproot python package
    - using pzilberman's venv: 
      source /home/pzilberman/venvs/custom_py3-v4.3.0_cobalt/bin/activate

 - Run duplicate_finder.py to collect information on duplicates present in root
   files
 - Run duplicate_check.py to visualize the results
 - Run duplicate_submitter.py to find and remove duplicates
 - Run mover.py to move original files with duplicates to a new directory and
   rename _dupfix output files to be the new defaults
