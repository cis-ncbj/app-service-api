# -*- coding: UTF-8 -*-

import requests
import flask
import logging

try:
    import json
except:
    import simplejson as json

from logging import debug, error, warning

logging.basicConfig(level=logging.DEBUG)


def submit(payload):
    payload['service'] = "MultiNest"
    url = "http://localhost:5000/submit"
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
    except:
        flask.flash(u"Brak połączenia z serwerem aplikacji", "error")
        return flask.redirect('/')

    if r.text.startswith('MultiNest'):
        flask.flash(u"Zadanie wysłane pomyślnie", "success")
        resp = flask.make_response(flask.redirect('/'))
        resp.set_cookie('CISMultiNestJobID', r.text)
        return resp

    flask.flash(r.text, "error")
    return flask.redirect('/')

def status():
    _states = (
            u'Oczekuję na zadania',
            u'Zadanie oczekuje w kolejce',
            u'Obliczenia w toku',
            u'Obliczenia zakończone',
            u'Błąd',
            )
    _jid = flask.request.cookies.get('CISMultiNestJobID')
    if _jid is not None:
        url = "http://localhost:5000/status/" + _jid
        r = requests.get(url)
        if \
            r.text.startswith('Waiting') or \
            r.text.startswith('Queued'):
                _st = 2
        elif \
            r.text.startswith('Running'):
                _st = 3
        elif \
            r.text.startswith('Done'):
                _st = 4
        else:
            _st = 5

        _result = {'state':_st, 'desc':_states[_st-1], 'msg':r.text}
        return flask.jsonify(_result)

    _result = {'state':1, 'desc':_states[0], 'msg':''}
    return flask.jsonify(_result)

def output():
    _jid = flask.request.cookies.get('CISMultiNestJobID')
    if _jid is not None:
        url = "http://localhost:5000/output/" + _jid
        r = requests.get(url)
        if r.text.startswith('Error'):
            flask.flash(r.text)
            return flask.redirect('/')
        else:
            debug(r.text)
            return flask.redirect(r.text)

    flask.flash(u"Brak zakończonego zadania: nie mogę wyświetlić wyników", "error")
    return flask.redirect('/')
