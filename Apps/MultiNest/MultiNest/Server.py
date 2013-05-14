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
    except Exception as e:
        flask.flash(u"Brak połączenia z serwerem aplikacji: %s" % e, "error")
        return flask.redirect('/')

    if r.text.startswith('MultiNest'):
        flask.flash(u"Zadanie wysłane pomyślnie", "success")
        resp = flask.make_response(flask.redirect('/monitor'))
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
                _type = 'queued'
        elif \
            r.text.startswith('Running'):
                _st = 3
                _type = 'running'
        elif \
            r.text.startswith('Done'):
                _st = 4
                _type = 'done'
        else:
            _st = 5
            _type = 'error'

        _result = {
            'state':_st, 'type':_type, 'desc':_states[_st-1], 'msg':r.text
        }
        return _result

    _result = {'state':1, 'type':'ready', 'desc':_states[0], 'msg':''}
    return _result


def progress():
    _result = {'job_output':'Waiting ...'}
    _jid = flask.request.cookies.get('CISMultiNestJobID')
    if _jid is not None:
        url = "http://localhost:5000/progress/" + _jid
        r = requests.get(url)
        if r.text.startswith('Error'):
            flask.flash(r.text, 'error')
        else:
            _result['job_output'] = r.text
    else:
        flask.flash(u"Brak zadań: nie mogę wyświetlić stanu obliczeń", "error")

    return _result


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
            _state = status()
            return flask.render_template("output.html",
                                         url=r.text,
                                         state=_state)

    flask.flash(u"Brak zakończonego zadania: nie mogę wyświetlić wyników", "error")
    return flask.redirect('/')
