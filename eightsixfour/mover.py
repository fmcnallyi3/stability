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

        # Separate into lists of fixed 86400 files and others
        esf_files = [f for f in root_files if 'esffix' in f]
        root_files = [f for f in root_files if f not in esf_files]

        for esf_file in esf_files:

            # Identify and move old (unfixed) files
            orig = esf_file.replace('_esffix', '')
            print(f'Moving files associated with {orig.split("/")[-1]}')
            if os.path.isfile(orig):
                out = orig.replace(f'/{cfg}/', f'/86400_errors/{cfg}/')
                out_dir = os.path.dirname(out)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                os.rename(orig, out)

            # Rename esffix to take its place
            os.rename(esf_file, orig)
