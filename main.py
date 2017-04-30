import logging
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

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