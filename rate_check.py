#!/usr/bin/env python

import argparse, json
import numpy as np
import matplotlib.pyplot as plt

import directories as stab

if __name__ == "__main__":

    # Import default project-specific paths
    stab.setup_dirs()

    p = argparse.ArgumentParser()
    p.add_argument('-c', '--config', dest='config',
            nargs='+',
            help='Detector configuration (IC86-2011, IC86-2012, ...)')
    p.add_argument('--rate_file', dest='rate_file',
            default=f'{stab.data}/rates.json',
            help='Json file containing rate information')
    p.add_argument('--rf', dest='rf',
            default='fits', choices=['root','fits'],
            help='Look for rate spikes in [root|fits]')
    p.add_argument('--everything', dest='everything',
            default=False, action='store_true',
            help='Create plots for all detector configurations')
    p.add_argument('-o', '--outdir', dest='outdir',
            default=stab.rate_plots,
            help='Output directory for files')
    p.add_argument('-v', '--verbose', dest='verbose',
            default=False, action='store_true',
            help='Print bad days')
    args = p.parse_args()

    # Shortcut to do every year
    if args.everything:
        args.config = [f'IC86-{yy}' for yy in range(2011, 2023)]

    # Load rates from summary output
    with open(args.rate_file, 'r') as f:
        rates = json.load(f)
        rates = rates[args.rf]

    all_rates = []
    for cfg in args.config:

        cfg_rates = [r for day, r in rates[cfg].items()]
        all_rates += cfg_rates

        if args.verbose:
            # Find and print days with bad rates
            print(f'Bad rates for {cfg}:')

            # Find comparison # from median of first 7 days
            comp = np.median(cfg_rates[:7])

            for i, (day, rate) in enumerate(rates[cfg].items()):

                if (rate >= 1.05*comp) or (rate <= 0.95*comp):
                    print(f'  {day}')
                    continue

                # Include good rates into rolling average
                comp = (4*comp + rate) / 5

            print()


        # Plot rate over time
        fig, ax = plt.subplots()
        ax.plot(cfg_rates)
        ax.set_ylim(1600, 3000)

        # Save plot to png file
        out = f'{args.outdir}/rates_{cfg}_{args.rf}.png'
        plt.savefig(out)
        plt.close()

    if args.everything:
        fig, ax = plt.subplots(figsize=(20,7))
        ax.plot(all_rates)
        ax.set_ylim(1600, 3000)
        out = f'{args.outdir}/rates_IC86_{args.rf}.png'
        plt.savefig(out)
        plt.close()

    print(f'Finished. Plots saved to {args.outdir}')



