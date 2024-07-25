#!/usr/bin/env python

import argparse
import uproot
from glob import glob
import numpy as np
import json
import os

if __name__ == "__main__":

    user = os.environ['USER']

    p = argparse.ArgumentParser(
            description='Counts duplicate events in DST root files')
    p.add_argument('-c', '--config', dest='config',
            help='Detector configuration (IC86-2011 - IC86-2022')
    p.add_argument('-o', '--outdir', dest='outdir',
            default=f'/data/user/{user}/stability/duplicates',
            help='Name of output directory to store info')
    args = p.parse_args()

    root_dir = '/data/ana/CosmicRay/Anisotropy/IceCube'
    files = sorted(glob(f'{root_dir}/{args.config}/**/*.root', recursive=True))

    info = {}

    for i, root_file in enumerate(files):

        f_name = root_file.split('/')[-1]
        print(f'Working on {f_name} ({i/len(files)*100:.03f}%)...')

        try:
            with uproot.open(root_file) as f:
                mjd = f['CutDST']['ModJulDay'].array(library='np')
                zen = f['CutDST']['LLHZenithDeg'].array(library='np')
        except:
            print('Uh oh! Error found!')
            continue

        dt = mjd[1:] - mjd[:-1]
        dz = zen[1:] - zen[:-1]

        n_dup = np.sum((dt==0) * (dz==0))
        p_dup = n_dup / len(mjd) * 100

        info[f_name] = p_dup

    with open(f'{args.outdir}/duplicates_{args.config}.json', 'w') as f:
        json.dump(info, f)



