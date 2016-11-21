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
    import requests

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
    for word in words:
        url = 'http://localhost:8081/define/'+word
        response = requests.get(url)
        print(response.text, end='')

if __name__=='__main__':
    main()
