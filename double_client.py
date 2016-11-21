#!/usr/bin/env python3

from __future__ import print_function


def main():
    import requests

    D = {'a':'a','b':'b'}

    url = 'http://localhost:8081/double'
    response = requests.post(url, json=D)
    print(response.text)

if __name__=='__main__':
    main()
