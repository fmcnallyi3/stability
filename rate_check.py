#!/usr/bin/env python

import argparse, json
import numpy as np
import matplotlib.pyplot as plt

import directories as stab

if __name__ == "__main__":

    # Import default project-specific paths
    stab.setup_dirs()

    p = argparse.ArgumentParser()
    #p.add_argument('-c', '--config', dest='config',
    #        nargs='+',
    #        help='Detector configuration (IC86-2011, IC86-2012, ...)')
    p.add_argument('--rate_file', dest='rate_file',
            default=f'{stab.data}/rates.json',
            help='Json file containing rate information')
    p.add_argument('--pdiff', dest='pdiff',
            type=float, default=5,
            help='percent diff marking a significant rate change (5,10,...)')
    p.add_argument('-o', '--outdir', dest='outdir',
            default=stab.rate_plots,
            help='Output directory for files')
    p.add_argument('-v', '--verbose', dest='verbose',
            default=False, action='store_true',
            help='Print bad days')
    args = p.parse_args()


    # Rate differential
    dr = args.pdiff/100

    # Load rates from summary output
    with open(args.rate_file, 'r') as f:
        rates = json.load(f)

    # Produce rate plots for root and fits data
    for ftype in rates.keys():

        all_rates = []
        configs = sorted(rates[ftype].keys())
        for cfg in configs:

            cfg_rates = [r for day, r in rates[ftype][cfg].items()]
            all_rates += cfg_rates

            if args.verbose:
                # Find and print days with bad rates
                print(f'Bad rates for {cfg}:')

                # Find comparison # from median of first 7 days
                comp = np.median(cfg_rates[:7])

                for i, (day, rate) in enumerate(rates[ftype][cfg].items()):

                    if (rate >= (1+dr)*comp) or (rate <= (1-dr)*comp):
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
            out = f'{args.outdir}/rates_{ftype}_{cfg}.png'
            plt.savefig(out)
            plt.close()

        # Plot for all years
        fig, ax = plt.subplots(figsize=(20,7))
        ax.plot(all_rates)
        ax.set_ylim(1600, 3000)
        out = f'{args.outdir}/rates_{ftype}_IC86.png'
        plt.savefig(out)
        plt.close()

    print(f'Finished. Plots saved to {args.outdir}')



