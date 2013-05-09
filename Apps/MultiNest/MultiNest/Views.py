# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, request, url_for
from MultiNest import app, Server
from Forms import SubmitForm

# index view function suppressed for brevity

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/submit', methods = ['GET', 'POST'])
def submit():
    form = SubmitForm()
    if form.validate_on_submit():
        return Server.submit(form.data)
    return render_template('submit.html',
        title = 'Test Title',
        form = form)

@app.route('/progress')
def progress():
    return Server.progress()

@app.route('/monitor')
def monitor():
    return render_template("monitor.html")

@app.route('/status')
def status():
    return Server.status()

@app.route('/output')
def output():
    return Server.output()
