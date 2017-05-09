import logging
from flask import Flask, render_template, request
from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime, timedelta

app = Flask(__name__)

class Resource(ndb.Model):
    name = ndb.StringProperty()
    start = ndb.TimeProperty()
    end = ndb.TimeProperty()
    duration = ndb.IntegerProperty()
    tags = ndb.StringProperty()
    createdby = ndb.StringProperty()
    reserved = ndb.IntegerProperty()
    reservedby = ndb.StringProperty()
    flag = ndb.IntegerProperty() # 0 = total, 1 = sub

@app.route('/')
def hello():
	user = users.get_current_user()
	if user:
		nickname = user.nickname()
		logout_url = users.create_logout_url('/')
		greeting = 'Welcome, {}! (<a href="{}">sign out</a>)<div><a href="/home">Home Page</a></div>'.format(nickname, logout_url)
		return ('<html><body>{}</body></html>'.format(greeting))
	else:
		login_url = users.create_login_url('/')
		greeting = '<a href="{}">Sign in</a>'.format(login_url)
		return ('<html><body>{}</body></html>'.format(greeting))

@app.route('/home')
def home():
	return render_template('index.html')

@app.route('/reservation')
def reservation():
	if users.get_current_user():
		return render_template('form.html')
	else:
		return "please login first"

@app.route('/allresource')
def allresource():
	if users.get_current_user():
		query = Resource.query(Resource.flag == 0)
		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
		for qry in query.fetch():
			x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   Tags:'
			for tag in str(qry.tags).split(','):
				x = x + '<a href="/showtagresource/'+ tag.strip() +'">'+ tag.strip() +'</a>  '
			x = x + '</div>'
		x = x + "</div></body></html>"
		return x
	else:
		return "please login first"
		
@app.route('/showtagresource/<string:name>')
def showtagresource(name):
	if users.get_current_user():
    		query = Resource.query(Resource.flag == 0)
    		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
    		for qry in query.fetch():
        		if (name in qry.tags):
            			x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   Tags:'
            			for tag in str(qry.tags).split(','):
                			x = x + '<a href="/showtagresource/'+ tag.strip() +'">'+ tag.strip() +'</a>  '
            			x = x + '</div>'
    		x = x + "</div></body></html>"
    		return x
	else:
		return "please login first"

@app.route('/resourceown')
def resourceown():
	if users.get_current_user():
    		query = Resource.query(Resource.createdby == users.get_current_user().nickname())
    		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container">'
    		for qry in query.fetch():
        		x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a></div>'
    		x = x + "</div></body></html>"
    		return x
	else:
    		return "please login first"

@app.route('/showresource/<string:name>')
def showresource(name):
	if users.get_current_user():
    		return render_template('resource.html', resourcename=name)
	else:
		return "please login first"
		
@app.route('/showreservation/<string:name>')
def showreservation(name):
	if users.get_current_user():
		query = Resource.query(Resource.name == name, Resource.flag == 0)
		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container"><h2>Resource Hours</h2>'
		for qry in query.fetch():
			x = x + '<div>' + qry.name + '   ' + str(qry.start) + '   ' + str(qry.end) + '</div>'
		x = x + "<h2>Reservations</h2>"
		query = Resource.query(Resource.name == name, Resource.flag == 1)
		for qry in query.fetch():
			x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   ' + str(qry.start) + '   ' + str(qry.duration) + '   ' + str(qry.reservedby) + '</div>'
		x = x + "</div></body></html>"
		return x
	else:
		return "please login first"

@app.route('/addreservation/<string:name>')
def addreservation(name):
	if users.get_current_user():
    		return render_template('addreservation.html', resourcename=name)
	else:
		return "please login first"

@app.route('/reserved', methods=['POST'])
def reserved_form():
	name = request.form['name']
	start = request.form['start']
	duration = request.form['duration']
	end = datetime.strptime(start, '%H:%M') + timedelta(minutes=int(duration))
	resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(str(end)[11:16], '%H:%M').time(), duration=int(duration), tags='', createdby='', reserved=0, reservedby=users.get_current_user().nickname(), flag=1)
	resource_key = resource.put()
	return render_template(
	'reserved_form.html',
	name=name,
	start=start,
	duration=duration)

@app.route('/editresource/<string:name>')
def editresource(name):
	if users.get_current_user():
    		return name
	else:
    		return "please login first"

@app.route('/form')
def form():
	if users.get_current_user():
    		return render_template('form.html')
	else:
		return "please login first"

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
        resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(end, '%H:%M').time(), duration=0, tags=tags, createdby=users.get_current_user().nickname(), reserved=0, reservedby='', flag=0)
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
