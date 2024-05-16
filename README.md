This folder contains scripts to check the stability of the detector as 
well as the processing of the root and I3 files. 

root_extractor.py
 - Opens a collection of root files (meant to be ~1 day) and calculates the
   number of events and livetime for each run
 - Stores as [date - run - nevents - livetime] in a .txt file

root_submitter.py
 - Submits root files to the cluster in ~daily batches for one detector year

root_merge.py
 - Merges daily root summaries by detector configuration

run2cfg.py
 - Creates a dictionary of run:config pairs using the good run list
 - Saves as a json for readability and fast loading into a python dictionary

rate_finder.py
 - Creates summary text files and stores rate information for each detector
   configuration
 - Requires:
    - Location of good run list output from i3live
    - Location of fits summary text files
       - Will generate automatically if maps have been updated
    - Location of root summary text files from root_extractor.py
       - To be submitted by root_submitter.py, merged by root_merge.py

rate_check.py
 - Generates rate plots for rates from root or fits files using summary output
   from rate_finder.py
 - Optionally outputs bad days using rolling average (from eschmidt)


Process:
 - first time only:
    - run directories.py to create default paths
    - download good runs from i3live: https://live.icecube.wisc.edu/snapshots/
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
