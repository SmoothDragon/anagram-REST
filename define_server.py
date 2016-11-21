#!/usr/bin/env python

from bottle import route, run, template

def define_word(word):
    word = word.upper()
    def_file = 'OWL14.def'
    with open(def_file) as infile:
        for line in infile:
            if line.split()[0] == word:
                return line
                break
        else:
            return('***UNACCEPTABLE***\n')

@route('/define/:word')
def index(word):
    response = define_word(word)
    return template(response)

@route('/')
def welcome():
    return "<h1>Yo yo yo</h1>"

run(host='localhost', port=8081)

