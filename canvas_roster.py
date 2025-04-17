#!/usr/bin/env python3

import sys, os, csv
from argparse import ArgumentParser

if __name__ == '__main__':
    SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

    parser = ArgumentParser(description='Create Gradescope roster from Canvas roster')
    parser.add_argument("--input", type=str,
        dest='input', required=True,
        help="Path to CSV roster from canvas")
    parser.add_argument("--output", type=str,
        dest='output', required=True,
        help="Path to CSV roster for gradescope")
    OPT = vars(parser.parse_args())

    with open(OPT['output'], 'w', newline='') as out_csv:
        writer = csv.writer(out_csv, quoting=csv.QUOTE_MINIMAL)
    
        with open(OPT['input'], 'r') as in_csv:

            # write header
            header = ['Student', 'ID', 'Email']
            writer.writerow(header)

            cavas_roster = csv.DictReader(in_csv)
            for row in cavas_roster:
                if row['ID'] == '':
                    continue
                student = [row['Student'], row['ID'], row['SIS User ID']+'@sonoma.edu']
                writer.writerow(student)
                print(student)
