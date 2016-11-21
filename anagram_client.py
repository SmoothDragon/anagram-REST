#!/usr/bin/env python3

from __future__ import print_function


def main():
    import requests

    D = {}
    letters = {'required':'EI', 'optional':'NRT', 'blanks':'0'}
    parameters = {'min':'3', 'max':'4', 'vowel_min':'0', 'vowel_max':'100'}
    D['letters'] = letters
    D['parameters'] = parameters
    url = 'http://localhost:8081/anagram'
    response = requests.post(url, json=D)
    print(response.text)

if __name__=='__main__':
    main()
