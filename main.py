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
    flag = ndb.IntegerProperty() # 0 = total, 1 = sub

@app.route('/')
def hello():
    return render_template('index.html')
@app.route('/reservation')
def reservation():
    return render_template('form.html')

@app.route('/allresource')
def allresource():
	query = Resource.query()
	x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
	for qry in query.fetch():
		x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a></div>'
	x = x + "</div></body></html>"
	return x

@app.route('/resourceown')
def resourceown():
    query = Resource.query(Resource.createdby == 'Kun')
    x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
    for qry in query.fetch():
        x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a></div>'
    x = x + "</div></body></html>"
    return x

@app.route('/showresource/<string:name>')
def showresource(name):
    return render_template('resource.html', resourcename=name)

@app.route('/showreservation/<string:name>')
def showreservation(name):
	query = Resource.query(Resource.name == name)
	x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
	for qry in query.fetch():
		x = x + '<div>' + qry.name + '___' + str(qry.start) + '___' + str(qry.end) + '___' + str(qry.createdby) + '</div>'
	x = x + "</div></body></html>"
	return x

@app.route('/addreservation/<string:name>')
def addreservation(name):
    return render_template('addreservation.html', resourcename=name)

@app.route('/reserved', methods=['POST'])
def reserved_form():
	name = request.form['name']
	start = request.form['start']
	duration = request.form['duration']
	return render_template(
    'reserved_form.html',
    name=name,
    start=start,
    duration=duration)

@app.route('/editresource/<string:name>')
def editresource(name):
    return name

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    start = request.form['start']
    end = request.form['end']
    tags = request.form['tags']
    query = Resource.query(Resource.name == name)
    x = 0
    for qry in query.fetch():
        x = x + 1
    if (x != 0):
        return "resource with same name already exist, please change the name"
    else:
        resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(end, '%H:%M').time(), tags=tags, createdby='Sonia', reserved=0, reservedby='', flag=0)
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