# -*- coding: utf-8 -*-

import json
from flask import render_template, flash, redirect, request, url_for, jsonify,\
        Response
from MultiNest import app, Server
from Forms import SubmitForm

# index view function suppressed for brevity

@app.route('/')
def hello():
    _state = Server.status()
    return render_template('index.html', state=_state)

@app.route('/submit', methods = ['GET', 'POST'])
def submit():
    _state = Server.status()
    form = SubmitForm()
    if form.validate_on_submit():
        return Server.submit(form.data)
    return render_template('submit.html',
        title = 'Test Title',
        form = form,
        state = _state)

@app.route('/progress')
def progress():
    _result = Server.progress()
    return Response(json.dumps(_result), mimetype='application/json')

@app.route('/monitor')
def monitor():
    _state = Server.status()
    _progress = Server.progress()
    _progress['job_output'] = _progress['job_output'].replace('\n', '<br/>')
    return render_template("monitor.html", state=_state, progress=_progress)

@app.route('/status')
def status():
    return jsonify(Server.status())

@app.route('/output')
def output():
    return Server.output()
