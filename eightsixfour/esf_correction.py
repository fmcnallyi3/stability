#!/usr/bin/env python

##==========================================================================## 
## Goal: find the "86400" (eight-six-four) errors present in the DST ROOT   ##
## files where the day suddenly jumps forward and correct them              ##
##==========================================================================## 

import argparse
import uproot
import numpy as np


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Extracts and stores nEvents and livetime from ' + \
            'ROOT files, organized by each run in each day')
    p.add_argument('-i', '--infiles', dest='infiles',
            nargs='+',
            #default=['/data/ana/CosmicRay/Anisotropy/IceCube/IC86-2017/2017-05-21/ic86_simpleDST_2017-05-21_run129535_part04.root'],
            default=['/data/ana/CosmicRay/Anisotropy/IceCube/IC86-2012/IC86-2012_simpleDST_2012-06-28_p09.root'],
            help='File(s) to retrieve the information from')
    p.add_argument('-o', '--out', dest='out',
            help='Name of output text file to store info')
    args = p.parse_args()


    # Data storage
    d = {}

    # Run through each input file
    for infile in args.infiles:

        print(f'Working on {infile}...')

        # Open root file
        f = uproot.open(infile)

        # Identify and fix errors in the mjd line
        mjd = f['CutDST']['ModJulDay'].array(library='np')
        dt = mjd[1:] - mjd[:-1]
        idx = np.argmax(dt)

        # Immediately quit if error not present
        if dt.max() < 0.9:
            print('  No 86400 errors found in this file!')
            f.close()
            continue

        # Error type 1: 56106.9996 --> 56107.9997 --> ... --> 56107.0001
        if (mjd[idx] % 1) > 0.9:
            print('Error type 1 found')
            start, stop = np.where(np.abs(dt) > 0.9)[0]
            display_range = np.arange(start, stop+2)
            print('Suggested correction:')
            print(mjd[display_range])
            mjd[start+1:stop+1] -= 1
            print('  -->')
            print(mjd[display_range])

        # Error type 2: 57894.9999 --> 57894.0 --> 57895.0001
        elif (mjd[idx] % 1) < 0.1:
            print('Error type 2 found')
            display_range = np.arange(idx-2, idx+3)
            print(f'Suggested correction:')
            print(mjd[display_range])
            mjd[idx] += 1
            print('  -->')
            print(mjd[display_range])

        # Catch weird cases
        else:
            print("Well, that's unexpected!")
            f.close()
            raise


        # Having identified the error, write corrected tree to a new file
        f_new = uproot.recreate('my_test.root')

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

        print('Finished!\n')
