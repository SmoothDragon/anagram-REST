#!/usr/bin/env python

from bottle import route, run, response, request
import json

@route('/double', method='POST')
def double_dict():
    '''Receive an incoming json dictionary and double all of the keys
    '''
    response.content_type = 'application/json'
    print(request.json)
    D = {key+key:request.json[key] for key in request.json}
    # incoming json request  = {letters:{}, parameters:{}}
    # outgoing json response = { #(letters): [words]}
    print(D)
    return D

@route('/')
def welcome():
    with open('hello_form.html', 'r') as infile:
        data = infile.read()
    return data
    return "<h1>Yo yo yo</h1>"

run(host='localhost', port=8081)

