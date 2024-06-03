#!/usr/bin/env python

import argparse, json
import numpy as np
import matplotlib.pyplot as plt

import directories as stab

def save_info(day, cfg, f):
    f.write(f'{cfg},')
    f.write(f'{day}\n')

    with open(f'{stab.data}/{cfg}_summary.txt', 'r') as summary:
        lines = summary.readlines()
        recording = False

        # Go through all lines in the appropriate summary file
        for line in lines:
            if recording:
                f.write(',,')
                items = line.split('-')

                for item in items:
                    f.write(item.strip() + ',')     

                f.write('\n')

            # Start recording data when the line has the target day
            if day in line:
                recording = True
                
            # Stop recording data if the line has the word fits in it
            if 'fits' in line:
                recording = False

if __name__ == "__main__":

    # Import default project-specific paths
    stab.setup_dirs()

    p = argparse.ArgumentParser()
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

    with open('bad_rates.csv', 'w') as f:
        f.write('Configuration, Day, Runs\n')
        # Produce rate plots for root and fits data
        for ftype in rates.keys():

            all_rates = []
            all_dates = []
            configs = sorted(rates[ftype].keys())

            for cfg in configs:

                cfg_rates = [r for day, r in rates[ftype][cfg].items()]
                cfg_dates = [day for day, r in rates[ftype][cfg].items()]
                all_rates += cfg_rates
                all_dates += cfg_dates

                if args.verbose:
                    # Find and print days with bad rates
                    print(f'Bad rates for {cfg}:')

                    # Find comparison # from median of first 7 days
                    comp = np.median(cfg_rates[:7])

                    for i, (day, rate) in enumerate(rates[ftype][cfg].items()):

                        if (rate >= (1+dr)*comp) or (rate <= (1-dr)*comp):
                            print(f'  {day}')
                            save_info(day, cfg, f)
                            continue

                        # Include good rates into rolling average
                        comp = (4*comp + rate) / 5

                    print()


                # Plot rate over time
                fig, ax = plt.subplots()
                ax.plot(cfg_rates)
                ax.set_ylim(1600, 3000)

                # Adjust x-axis labels to show dates
                fig.canvas.draw()
                labels = [item.get_text() for item in ax.get_xticklabels()]
                for i in range(1, len(labels)):
                    try: labels[i] = cfg_dates[int(labels[i])]
                    except IndexError:
                        labels[i] = ''
                ax.set_xticklabels(labels, rotation=45, ha='right')

                # Save plot to png file
                out = f'{args.outdir}/rates_{ftype}_{cfg}.png'
                plt.savefig(out, bbox_inches="tight")
                plt.close()

            # Plot for all years
            fig, ax = plt.subplots(figsize=(20,7))
            ax.plot(all_rates)
            ax.set_ylim(1600, 3000)

            # Adjust x-axis labels to show dates
            fig.canvas.draw()
            labels = [item.get_text() for item in ax.get_xticklabels()]
            for i in range(1, len(labels)):
                try: labels[i] = all_dates[int(labels[i])]
                except IndexError:
                    labels[i] = ''
            ax.set_xticklabels(labels, rotation=45, ha='right')


            out = f'{args.outdir}/rates_{ftype}_IC86.png'
            plt.savefig(out, bbox_inches="tight")
            plt.close()

    print(f'Finished. Plots saved to {args.outdir}')



