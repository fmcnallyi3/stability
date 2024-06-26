This folder contains scripts to correct "864" errors -- locations
in ROOT files where the MJD suddenly jumps by a full day, resulting in a
runtime of ~86400 seconds.

## Files

`esf_correction.py`
 - Identifies the offending file and entries within the file, then creates a
   duplicate, corrected file.

`esf_submitter.py`
 - Executes esf_correction.py over all offending days

`README.md`
 - this file


## Process

 - Requires uproot python package
    - using pzilberman's venv: 
      source /home/pzilberman/venvs/custom_py3-v4.3.0_cobalt/bin/activate

 - Identify 864 errors using rate_check.py in parent directory
 - Run esf_submitter.py with the bad dates
