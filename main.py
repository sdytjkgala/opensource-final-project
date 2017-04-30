import logging
from flask import Flask, render_template, request
from google.appengine.ext import ndb

app = Flask(__name__)

class Resources(ndb.Model):
    name = ndb.StringProperty()
    start = ndb.StringProperty()

@app.route('/')
def hello():
    test1 = Resources(name='hotel', start='12:00')
    test1_key = test1.put()
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')
    
@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    start = request.form['start']
    end = request.form['end']
    tags = request.form['tags']
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