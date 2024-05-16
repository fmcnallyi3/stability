This folder contains scripts to check the stability of the detector as 
well as the processing of the root and I3 files. 

directories.py
 - Establishes a default set of paths for this project

fits_extractor.py
 - Opens all map files for a given detector configuration and stores counts
   along with good run times from i3live
 - Stores as fits_data[cfg][date][events|livetime] in a .json file

fits_merge.py
 - Merges count and livetime information from each detector configuration

grl_reader.py
 - Functions associated with reading the good run list from i3live, including
   livetime calculation and getting a list of bad runs

rate_finder.py
 - Creates summary text files and stores rate information for each detector
   configuration

rate_check.py
 - Generates rate plots for rates from root or fits files using summary output
   from rate_finder.py
 - Optionally outputs bad days using rolling average

README.md
 - this file

root_extractor.py
 - Opens a collection of root files (meant to be ~1 day) and calculates the
   number of events and livetime for each run
 - Stores as [date - run - nevents - livetime] in a .txt file

root_merge.py
 - Merges daily root summaries by detector configuration

root_submitter.py
 - Submits root files to the cluster in ~daily batches for one detector year

run2cfg.py
 - Creates a dictionary of run:config pairs using the good run list
 - Saves as a json for readability and fast loading into a python dictionary

submitter
 - Scripts for the submission of jobs (root_submitter) to the cluster


Process:
 - first time only:
    - run directories.py to create default paths
    - download good runs from i3live (https://live.icecube.wisc.edu/snapshots/)
      and save in stab.data (see directories)
    - run run2cfg.py to create dictionary relating runs to detector configs
 - produce root summary files:
    - run one year at a time using root_submitter.py
    - when all finished, run root_merge.py to create summary file
 - produce fits summary files:
    - run fits_extractor.py (one year at a time, fine on cobalt)
    - when all finished, run fits_merge.py to create summary file
 - calculate and assess rates:
    - run rate_finder.py to calculate and save the rates
    - run rate_check.py to identify days/runs of concern
 - reprocessing (fmcnally):
    - move problematic root/fits files to temporary location
      - include daily root summary files!
    - apply correction, recreating (now-missing) files
    - rerun root_submitter & fits_extractor for designated years
    - rerun root_merge & fits_merge
    - rerun rate_finder and rate_check
