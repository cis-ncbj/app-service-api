import requests
import flask

try:
    import json
except:
    import simplejson as json

def submit(payload):
    payload['service'] = "MultiNest"
    url = "http://localhost:5000/submit"
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.text.startswith('MultiNest'):
        flask.flash('Job submitted successfuly')
        resp = flask.make_response(flask.redirect('/'))
        resp.set_cookie('CISMultiNestJobID', r.text)
        return resp

    flask.flash(r.text)
    return flask.redirect('/')

def status():
    _jid = flask.request.cookies.get('CISMultiNestJobID')
    if _jid is not None:
        url = "http://localhost:5000/status/" + _jid
        r = requests.get(url)
        flask.flash(r.text)
        return flask.redirect('/')

    flask.flash('No job submitted yet ...')
    return flask.redirect('/')

def output():
    _jid = flask.request.cookies.get('CISMultiNestJobID')
    if _jid is not None:
        url = "http://localhost:5000/output/" + _jid
        r = requests.get(url)
        if r.text.startswith('Error'):
            flask.flash(r.text)
            return flask.redirect('/')
        else:
            return flask.redirect('file://' + r.text)

    flask.flash('No job submitted yet ...')
    return flask.redirect('/')

