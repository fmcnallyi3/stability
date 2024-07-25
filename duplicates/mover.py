#!/usr/bin/env python

from glob import glob
import os

if __name__ == "__main__":

    # Collect all DST root files
    prefix = '/data/ana/CosmicRay/Anisotropy/IceCube'
    configs = [f'IC86-{yy}' for yy in range(2011,2023)]

    for cfg in configs:
        root_files = glob(f'{prefix}/{cfg}/**/*.root', recursive=True)
        root_files.sort()

        # Separate into lists of duplicate-fixed files and others
        dup_files = [f for f in root_files if 'dupfix' in f]
        root_files = [f for f in root_files if f not in dup_files]

        for dup_file in dup_files:

            # Identify and move old (unfixed) files
            orig = dup_file.replace('_dupfix', '')
            print(f'Moving files associated with {orig.split("/")[-1]}')
            if os.path.isfile(orig):
                out = orig.replace(f'/{cfg}/', f'/duplicate_errors/{cfg}/')
                out_dir = os.path.dirname(out)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                os.rename(orig, out)

            # Rename dupfix to take its place
            os.rename(dup_file, orig)
