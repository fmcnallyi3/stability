#!/usr/bin/env python

from glob import glob
import numpy as np
import json
import re
import os
import matplotlib.pyplot as plt

if __name__ == "__main__":

    user = os.environ['USER']
    prefix = f'/data/user/{user}/stability/duplicates'
    infiles = sorted(glob(f'{prefix}/duplicates_IC86-????.json'))
    d = {}

    for i, infile in enumerate(infiles):

        with open(infile, 'r') as f:
            d_i = json.load(f)

        cfg = re.findall('IC86-\d{4}',infile)[0]
        for key in d_i.keys():
            d[f'{cfg}_{key}'] = d_i[key]

        fig, ax = plt.subplots()
        ax.plot([d_i[key] for key in d_i.keys()])
        ax.set_title(f'{cfg}')
        ax.set_xlabel('Root File')
        ax.set_ylabel('Percentage of Duplicate Events')
        plt.savefig(f'{prefix}/duplicate_plot_{cfg}.png')

    keys = sorted(d.keys())
    values = np.array([d[key] for key in keys])

    fig, ax = plt.subplots()
    ax.plot(values)
    ax.set_title('All Data')
    ax.set_xlabel('Root File')
    ax.set_ylabel('Percentage of Duplicate Events')
    plt.savefig(f'{prefix}/duplicate_plot.png')

    print(values.min(), values.max())
    print(keys[values.argmax()])

    
