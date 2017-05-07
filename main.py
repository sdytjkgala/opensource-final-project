import logging
from flask import Flask, render_template, request
from google.appengine.ext import ndb
from datetime import datetime

app = Flask(__name__)

class Resource(ndb.Model):
    name = ndb.StringProperty()
    start = ndb.TimeProperty()
    end = ndb.TimeProperty()
    tags = ndb.StringProperty()
    createdby = ndb.StringProperty()
    reserved = ndb.IntegerProperty()
    reservedby = ndb.StringProperty()

@app.route('/')
def hello():
    return render_template('index.html')
@app.route('/reservation')
def reservation():
    return render_template('form.html')

@app.route('/allresource')
def allresource():
    return render_template('form.html')

@app.route('/resourceown')
def resourceown():
    return render_template('form.html')
@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    start = request.form['start']
    end = request.form['end']
    tags = request.form['tags']
    resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(end, '%H:%M').time(), tags=tags, createdby='Kun', reserved=0, reservedby='')
    resource_key = resource.put()
    return render_template(
    'submitted_form.html',
    name=name,
    start=start,
    end=end,
    tags=tags)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500