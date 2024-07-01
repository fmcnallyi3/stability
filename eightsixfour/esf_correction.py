#!/usr/bin/env python

##==========================================================================## 
## Goal: find the "86400" (eight-six-four) errors present in the DST ROOT   ##
## files where the day suddenly jumps forward (or back) and correct them    ##
##==========================================================================## 

import argparse
import uproot
import numpy as np
from glob import glob


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Extracts and stores nEvents and livetime from ' + \
            'ROOT files, organized by each run in each day')
    p.add_argument('-i', '--infiles', dest='infiles',
            nargs='+',
            help='File(s) to retrieve the information from')
    args = p.parse_args()

    if args.infiles == None:
        prefix = '/data/ana/CosmicRay/Anisotropy/IceCube/86400_errors'
        args.infiles = sorted(glob(f'{prefix}/**/*.root', recursive=True))

    # Data storage
    d = {}

    # Run through each input file
    for infile in args.infiles:

        print(f'\nWorking on {infile}...')

        # Open root file
        f = uproot.open(infile)

        # Identify and fix errors in the mjd line
        mjd = f['CutDST']['ModJulDay'].array(library='np')
        dt = mjd[1:] - mjd[:-1]
        bad_events = np.where(np.abs(dt) > 0.9)[0]

        # Immediately quit if error not present
        if len(bad_events) == 0:
            print('  No 86400 errors found in this file!')
            f.close()
            continue

        # Errors look like: 56106.9996 --> 56107.9997 --> ... --> 56107.0001
        #               OR: 56106.9999 --> 56106.0000 --> ... --> 56107.0002
        if len(bad_events) == 2:
            print('  Error found!')
            start, stop = bad_events
            correction = -1 if mjd[start+1] > mjd[start] else 1
            display_range = np.arange(start, stop+2)
            print('Suggested correction:')
            print(mjd[display_range])
            mjd[start+1:stop+1] += correction
            print('  -->')
            print(mjd[display_range])

        # Catch weird cases
        else:
            print("Well, that's unexpected...")
            f.close()
            raise

        # Having identified the error, write corrected tree to a new file
        outfile = infile.replace('.root', '_esffix.root')
        f_new = uproot.recreate(outfile)

        # Prepare batch size and keys for copying
        batchsize = int(len(mjd)/10)
        a_len = len(mjd)

        # Some weird stuff happens with semicolons in tree names
        # Ex: 'CutDST;19' and 'CutDST;20' both present in the same file
        trees = [tree.split(';')[0] for tree in f.keys()]
        trees = sorted(set(trees))

        for tree in trees:

            print(f'\nWorking on tree {tree}...')

            keylist = f[tree].keys()
            if keylist == []:
                print('  No branches found! Skipping...')
                continue

            # Check for the presence of MJD
            mjd_found = False
            if 'ModJulDay' in keylist:
                keylist.remove('ModJulDay')
                mjd_found = True

            # Structure for storage
            new_dict = {}

            # Extract info as batched arrays and append to new tree
            for i in range(0, a_len, batchsize):

                stop = i+batchsize if i+batchsize <= a_len else a_len
                print(f'  Loading entries {i} to {stop}...')
                kw = {'library':'np', 'entry_start':i, 'entry_stop':stop}

                if mjd_found:
                    new_dict['ModJulDay'] = mjd[i:stop]
                for key in keylist:
                    new_dict[key] = f[tree][key].array(**kw)

                if i == 0:
                    f_new[tree] = new_dict
                else:
                    f_new[tree].extend(new_dict)

        f.close()
        f_new.close()

        print('Finished!')
        print(f'New file written to {outfile}\n')
