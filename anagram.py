#!/usr/bin/env python

from __future__ import print_function

try:
    # Python2
    from itertools import izip_longest as zip_longest
    from itertools import ifilter as filter
except ImportError:
    # Python3
    from itertools import zip_longest

info = r'''Find anagrams of letters

By default, 'anagram' uses /usr/share/dict/linux.words as the dictionary.

To use a custom dictionary, change the symlink at
    ~/.config/anagram/dict.txt'
to point to the desired dictionary.

This utility is useful in conjuction with grep. Some examples:

    1) Find anagrams of "aeionrst" containing the sequence "nor".
        anagram aeionrst | grep nor
    Result: senorita

    2) Find anagrams of "raze_" starting with "z".
        anagram raze_ | grep "^z"
    Result: zaire zebra zerda
'''

import string

freq = 'QJXZWKVFYBHGMPUDCLOTNRAISE' # Frequency order obtained from counting word.lst
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101]
prime_dict = {freq[i]:primes[i] for i in range(26)} # Match common letters with small primes

def freq_sort(letters):
    '''Sort letters according to frequency.
    >>> freq_sort('QUINZHEE')
    ['Q', 'Z', 'H', 'U', 'N', 'I', 'E', 'E']
    '''
    return sorted(letters, key=lambda c: freq.find(c))

def least_common_letter_included(letters):
    '''Filter on the least common letter in letters.
    str -> str -> Bool
    >>> least_common_letter_included('QADI')('QJX')
    True
    '''
    for ch in freq:
        if ch in letters:
            break
    else:
        raise TypeError
    return lambda word: ch in word

def least_common_letter(letters):
    '''Find the least common letter in letters.
    str -> str
    >>> least_common_letter('QADI')
    'Q'
    '''
    for ch in freq:
        if ch in letters:
            return ch
    else:
        raise TypeError

def most_common_letter_excluded(letters):
    '''Filter on the least common letter in letters.
    str -> str -> Bool
    >>> most_common_letter_excluded('QADI')('QJX')
    True
    '''
    freq = 'QJXZWKVFYBHGMPUDCLOTNRAISE' # Frequency order obtained from counting word.lst
    for ch in freq[::-1]:
        if ch not in letters:
            break
    else:
        raise TypeError
    return lambda word: ch not in word

def most_common_letter_missing(letters):
    '''Return the most common letter missing from <letters>.
    >>> most_common_letter_missing('QADI')
    'E'
    '''
    for ch in freq[::-1]:
        if ch not in letters:
            return ch
    else:
        raise TypeError

def prime_value(letters):
    result = 1
    for ch in letters:
        result *= prime_dict[ch]
    return result

def contains_filter(letters, stream):
    '''Filters out words in stream that contain all the letters.
    More general than anagram filter. Useful for anagrams with blanks.
    '''
    def product(L):
        result = 1
        for i in L:
            result *= i
        return result
    p = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101]
    freq = 'QJXZWKVFYBHGMPUDCLOTNRAISE' # Frequency order obtained from counting word.lst
    D = {freq[i]:p[i] for i in range(26)} # Match common letters with small primes
    n = product((D[ch] for ch in letters))
    for line in stream:
        if product((D[ch] for ch in line[:-1]))%n == 0:
            yield line

def distill_query(letters):
    '''Break input into (required, optional, blanks).
    Uppercase letters are required.
    Lowercase letters are optional.
    A single numeric digit indicates the number of blanks.
    >>> distill_query('aDbEdF2')
    ('DEF', 'ABD', 2)
    >>> distill_query('rates1')
    ('', 'AERST', 1)
    '''
    required = filter(lambda x: x in string.ascii_uppercase, letters)
    optional = filter(lambda x: x in string.ascii_lowercase, letters)
    # optional = optional.upper()
    numbers = filter(lambda x: x in string.digits, letters)
    blanks = int('0' + ''.join(numbers))
    return (''.join(sorted(required)), ''.join(sorted(x.upper() for x in optional)), blanks)

def query_filter(query):
    '''Filter on words that satisfy required, optional and blank requirements.
    >>> q = query_filter(('EI', 'NRST', 1))
    >>> [q(w) for w in ['TINE', 'ZINE', 'TUBE', 'RETINAL', 'RETAINS', 'EAU']]
    [True, True, False, False, True, False]
    >>> q = query_filter(('UW', '', 1))
    >>> [q(w) for w in ['WUD', 'WUZ', 'WIZ']]
    [True, True, False]
    '''
    required, optional, blanks = query
    req_dict = {ch:required.count(ch) for ch in set(required)}
    opt_dict = {ch:optional.count(ch) for ch in set(optional)}
    def q_filter(word):
        target = len(word)
        for ch in req_dict:
            if word.count(ch) < req_dict[ch]:
                return False
            target -= req_dict[ch]
            word = word.replace(ch, '', req_dict[ch])
        for ch in opt_dict:
            target -= min(opt_dict[ch], word.count(ch))
        return target <= blanks
    return q_filter


def len_range(start, stop):
    '''Returns a function that recognizes words with length in [start, stop).
    (int, int) -> str -> Bool
    >>> len_range(4,5)('HELP')
    True
    '''
    # If words are not ordered in increasing word length, use the following.
    # return lambda word: len(word) < stop and len(word) >= start
    def len_filter(word):
        n = len(word)
        if n < start:
            return False
        if n >= stop:
            raise StopIteration
        return True
    return len_filter

DICT = ['SSWL15', 'TWL06', 'OWL14', 'CSW12', 'OSPD4']

def all_func(F):
    '''Return a function that is the logical and of input functions.
    Equivalent, but faster than lambda x: all(f(x) for f in F
    F must be repeatably iterable.
    '''
    F = tuple(F)
    def multi_filter(x):
        for f in F:
            if not f(x):
                return False
        return True
    return multi_filter

# if __name__ == "__main__":
def main():
    import sys
    import argparse
    import os
    import os.path
    import errno

    parser = argparse.ArgumentParser(description=info,
                formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-d', '--dict', action='store', dest='dict',
                default='OWL14', help='Choose dictionary.')
    parser.add_argument('--min', type=int, action='store', dest='min', default=None)
    parser.add_argument('--max', type=int, action='store', dest='max', default=None)
    parser.add_argument('-a', '--all', action='store_true', dest='all', 
                default=False, help='Return all anagrams of length 3 or more.')
    parser.add_argument('letters', nargs='?', type=str, 
            help='Letters to anagram. Use _ for blanks.')
    results = parser.parse_args()

    # Abort if dictionary is not valid
    if results.dict not in DICT:
        print('Error: Invalid dictionary', file=sys.stderr)
        exit(-1)

    # Abort if no letters were provided
    if results.letters is None:
        parser.print_help()
        exit(-1)

    query = distill_query(results.letters)
    f = query_filter(query)

    # Find dictionary location based on script location
    head, tail = os.path.split(__file__)
    dictfile = os.path.join(head, '..', 'share', 'OWL14.txt')
    dictfile = os.path.join(head, '..', 'anagram', 'data', 'OWL14.txt')
    # dictfile = os.path.join(__file__, 'data', 'OWL14.txt')

    with open(dictfile, 'rt') as infile:
        words = (line.strip() for line in infile)
        for word in filter(f, words):
            print(word)
    exit(0)

    L = {letter:letters.count(letter) for letter in letters}
    if results.min is None:
        results.min = len(letters) + blanks
    if results.max is None:
        results.max = len(letters) + blanks
    if results.max < results.min:
        parser.print_help()
        exit(-1)
    if results.all:
        results.min = 3
