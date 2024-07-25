#!/usr/bin/env python

##==========================================================================## 
## Goal: find all event duplicates in a file and remove them                ##
##==========================================================================## 

import argparse
import uproot
import numpy as np


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Finds and removes duplicate entries within a ' + \
            'list of ROOT files')
    p.add_argument('-i', '--infiles', dest='infiles',
            nargs='+',
            default=['/data/ana/CosmicRay/Anisotropy/IceCube/IC86-2017/2017-05-21/ic86_simpleDST_2017-05-21_run129535_part04.root'],
            help='File(s) to retrieve the information from')
    args = p.parse_args()


    # Data storage
    d = {}

    # Run through each input file
    for infile in args.infiles:

        print(f'Working on {infile}...')

        # Extract two pieces of information for every event
        try:
            f = uproot.open(infile)
            mjd = f['CutDST']['ModJulDay'].array(library='np')
            zen = f['CutDST']['LLHZenithDeg'].array(library='np')

        # Keep an eye out for corrupted root files
        except:
            print('Uh oh! Corrupted root file!')
            continue

        # Look for duplicates
        dt = mjd[1:] - mjd[:-1]
        dz = zen[1:] - zen[:-1]
        # Duplicate events will have the same MJD and zenith
        duplicate_cut = np.ones(mjd.shape, dtype=bool)
        duplicate_cut[1:] = (dt!=0) + (dz!=0)

        ##==========================================================##
        ## NOTE: the code above assumes the events are time-ordered ##
        ## (or, at a minimum, that duplicate events are adjacent to ##
        ## one another). This assumption was tested on a few files  ##
        ## and appears to be valid.                                 ##
        ##==========================================================##

        if duplicate_cut.sum() == len(duplicate_cut):
            print('No duplicates found!')
            continue

        # Write corrected tree to a new file
        outfile = infile.replace('.root', '_dupfix.root')
        f_new = uproot.recreate(outfile)

        # Break each array into 10 equal bins to avoid memory overload
        batch_idxs = np.linspace(0, len(mjd)+1, 10).astype('int')

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

            # Structure for storage
            new_dict = {}

            # Extract info as batched arrays and append to new tree
            for start, stop in zip(batch_idxs[:-1], batch_idxs[1:]):

                print(f'  Loading entries {start} to {stop}...')
                kw = {'library':'np', 'entry_start':start, 'entry_stop':stop}

                for key in keylist:
                    temp = f[tree][key].array(**kw)
                    new_dict[key] = temp[duplicate_cut[start:stop]]

                if start == 0:
                    f_new[tree] = new_dict
                else:
                    f_new[tree].extend(new_dict)

        f.close()
        f_new.close()

        print('Finished!')
        print(f'New file written to {outfile}\n')
