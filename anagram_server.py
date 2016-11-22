#!/usr/bin/env python

from __future__ import print_function

# from bottle import route, run, response, request, static_file
import bottle
import json
import collections
import string

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

def distill_query_dict(letters):
    '''Break input into {required, optional, blanks}.
    Uppercase letters are required.
    Lowercase letters are optional.
    A single numeric digit indicates the number of blanks.
    >>> distill_query_dict('aDbEdF2')
    {'required': 'DEF', 'optional': 'ABD', 'blanks': 2}
    >>> distill_query_dict('rates1')
    {'required': '', 'optional': 'AERST', 'blanks': 1}
    '''
    required = filter(lambda x: x in string.ascii_uppercase, letters)
    optional = filter(lambda x: x in string.ascii_lowercase, letters)
    # optional = optional.upper()
    numbers = filter(lambda x: x in string.digits, letters)
    blanks = int('0' + ''.join(numbers))
    return {'required':''.join(sorted(required)), 'optional':''.join(sorted(x.upper() for x in optional)), 'blanks':blanks}

def query_filter(query):
    '''Filter on words that satisfy required, optional and blank requirements.
    >>> q = query_filter({'required':'EI', 'optional':'NRST', 'blanks':'1'})
    >>> [q(w) for w in ['TINE', 'ZINE', 'TUBE', 'RETINAL', 'RETAINS', 'EAU']]
    [True, True, False, False, True, False]
    >>> q = query_filter({'required':'UW', 'blanks':'1'})
    >>> [q(w) for w in ['WUD', 'WUZ', 'WIZ']]
    [True, True, False]
    '''
    query = collections.defaultdict(lambda: '', query)
    required = query['required'].upper()
    optional = query['optional'].upper()
    blanks = int('0'+str(query['blanks'])) # Empty string becomes zero

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

def param_filter(params):
    '''Filter on words meeting parameters
    >>> q = param_filter({'min':'4', 'max':'5'})
    >>> [q(w) for w in ['TINE', 'ZINE', 'TUBE', 'RETINAL', 'RETAINS', 'EAU']]
    [True, True, True, False, False, False]

    # >>> q = param_filter({'required':'UW', 'optional':'', 'blanks':'1'})
    # >>> [q(w) for w in ['WUD', 'WUZ', 'WIZ']]
    # [True, True, False]
    '''
    params = collections.defaultdict(lambda: '', params)
    min_length = int('0'+str(params['min']))
    max_length = int('0'+str(params['max']))
    vowel_min = int('0'+str(params['vowel_min']))
    vowel_max = int('0'+str(params['vowel_max']))
    def p_filter(word):
        if len(word) < min_length:
            return False
        if len(word) > max_length:
            return False
        return True
    return p_filter

def dict_nested2flat(D):
    '''
    >>> import pprint
    >>> pprint.pprint(dict_nested2flat({'a':{'b':'c', 'd':'f'}}))
    {'a.b': 'c', 'a.d': 'f'}
    >>> pprint.pprint(dict_nested2flat({'a':{'b':{'c':{'d':'f'}, 'e':'e'}}}))
    {'a.b.c.d': 'f', 'a.b.e': 'e'}
    '''
    result = {}
    for key in D:
        if type(D[key]) is dict:
            flattened = dict_nested2flat(D[key])
            for element in flattened:
                result[str(key)+'.'+str(element)] = flattened[element]
        else:
            result[key] = D[key]
    return result

def nested_dict(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def dict_flat2nested(F):
    '''
    >>> import pprint
    >>> pprint.pprint(dict_flat2nested({'a.b': 'c', 'a.d': 'f'}))
    {'a': {'b': 'c', 'd': 'f'}}
    >>> pprint.pprint(dict_flat2nested({'a.b.c.d': 'f', 'a.b.e': 'e'}))
    {'a': {'b': {'c': {'d': 'f'}, 'e': 'e'}}}
    '''
    result = {}
    for key in F:
        keys = key.split('.')
        nested_dict(result, keys, F[key])
    return result

@bottle.route('/', method='POST')
def anagram(data=None):
    '''Receive an incoming request form or json dictionary
    For letterset:
        1) Lowercase are optional
        2) Uppercase are required
        3) Any digit is the number of blanks
    INPUT
    {
    letterset:'exaMPL1',
    parameters:{
        min,
        max,
        vowel_min,
        vowel_max,
        }
    }
    OUTPUT
    {
    #letters:[words]
    }
    '''
    bottle.response.content_type = 'application/json'
    print(dict(bottle.request.forms))
    print('json: ', bottle.request.json)

    if bottle.request.json:
        dic = bottle.request.json
    else:
        dic = dict(bottle.request.forms)
    print(dic)
    query = distill_query_dict(dic['letterset'])
    print(query)
    qfilter = query_filter(query)
    # qfilter = query_filter(dic['letters'])
    # pfilter = param_filter(dic['parameters'])

    output = collections.defaultdict(list)
    with open('OWL14.txt', 'rt') as infile:
        words = (line.strip() for line in infile)
        filters = (qfilter, )
        for f in filters:
            words = filter(f, words)
        for word in words:
            output[len(word)].append(word)
    print(output)
    return output

@bottle.route('/', method='GET')
def anagram_form():
    return bottle.static_file('anagram_form.html', root='static/')
    with open('static/anagram_form.html', 'r') as infile:
        data = infile.read()
    return data

@bottle.route('/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return bottle.static_file(filename, root='static/')

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    bottle.run(host='0.0.0.0', port=80)
