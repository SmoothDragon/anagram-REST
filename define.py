#!/usr/bin/env python3

from __future__ import print_function

info = r'''Print word definition

Dictionary options are:
    SSWL15 - School Scrabble 2015
    TWL06  - Tournament word list 2006
    OWL14  - Tournament word list 2014
    CSW12  - Collins word list 2012
    OSPD4  - Official Scrabble Players Dictionary 4th edition
'''

DICT = ['SSWL15', 'TWL06', 'OWL14', 'CSW12', 'OSPD4']

def main():
    import sys
    import argparse
    import os

    parser = argparse.ArgumentParser(description=info,
                formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-d', '--dict', action='store', dest='dict',
                default='OWL14', help='Choose dictionary')
    parser.add_argument('words', nargs=argparse.REMAINDER)
    results = parser.parse_args()

    if results.dict not in DICT:
        print('Error: Invalid dictionary', file=sys.stderr)
        exit(-1)

    words = [word.upper() for word in sys.argv[1:]]
    # Find dictionary location based on script location
    head, tail = os.path.split(__file__)
    # def_file = os.path.join(head, '..', 'share', results.dict+'.def')
    def_file = os.path.join('OWL14.def')
    # def_file = os.path.join(__file__, 'data', 'OWL14.def')

    # def_file = '/usr/share/dict/'+results.dict+'.def'
    with open(def_file) as infile:
        for line in infile:
            if line.split()[0] in words:
                print(line, end='')

if __name__=='__main__':
    main()
