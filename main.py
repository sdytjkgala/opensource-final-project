import logging
from flask import Flask, render_template, request
from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime, timedelta
import pytz
from pytz import timezone

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
    timestamp = ndb.TimeProperty()

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

@app.route('/showowned/<string:name>')
def showowned(name):
	if users.get_current_user():
		return render_template('showowned.html', name=name)
	else:
		return "please login first"

@app.route('/reservation')
def reservation():
	if users.get_current_user():
		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container"><h2>Reservations made</h2>'
		query = Resource.query(Resource.reservedby == users.get_current_user().nickname(), Resource.flag == 1) #.order(Resource.start)
		for qry in query.fetch():
			if (reservation_pass(str(qry.end)) == 0):
				x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   , start-time:' + str(qry.start)[0:5] + '  , duration(minutes): ' + str(qry.duration) + '   , reserved-by: <a href="/showowned/' + str(qry.reservedby) + '">' + str(qry.reservedby) + '</a> , <a href="/deletereservation/' + str(qry.key.id()) + '">delete reservation </a></div>'
		x = x + "</div></body></html>"
		return x		
	else:
		return "please login first"

@app.route('/deletereservation/<string:id>')
def deletereservation(id):
	if users.get_current_user():
		query = Resource.query()
		for qry in query.fetch():
			if (str(qry.key.id()) == id):
				qry.key.delete()
		return "Deleted"
	else:
		return "please login first"

@app.route('/reservationbyuser/<string:name>')
def reservationbyuser(name):
	if users.get_current_user():
		x = '<html><head><link rel="stylesheet" type="text/css" href="/static/style.css"></head><body><div id="container"><h2>Reservations made</h2>'
		query = Resource.query(Resource.reservedby == name, Resource.flag == 1) #.order(Resource.start)
		for qry in query.fetch():
			if (reservation_pass(str(qry.end)) == 0):
				if (qry.reservedby == users.get_current_user().nickname()):
					x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   , start-time:' + str(qry.start)[0:5] + '  , duration(minutes): ' + str(qry.duration) + '   , reserved-by: <a href="/showowned/' + str(qry.reservedby) + '">' + str(qry.reservedby) + '</a> , <a href="/deletereservation/' + str(qry.key.id()) + '">delete reservation </a></div>'
				else:	
					x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>   , start-time:' + str(qry.start)[0:5] + '  , duration(minutes): ' + str(qry.duration) + '   , reserved-by: <a href="/showowned/' + str(qry.reservedby) + '">' + str(qry.reservedby) + '</a></div>'
		x = x + "</div></body></html>"
		return x
		
	else:
		return "please login first"

@app.route('/allresource')
def allresource():
	if users.get_current_user():
		query = Resource.query(Resource.flag == 0) #.order(-Resource.timestamp)
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

@app.route('/resourceownbyuser/<string:name>')
def resourceownbyuser(name):
	if users.get_current_user():
    		query = Resource.query(Resource.createdby == name)
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
			if (reservation_pass(str(qry.end)) == 0):
				if (qry.reservedby == users.get_current_user().nickname()):
					x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>  , start-time: ' + str(qry.start) + '  , duration(minutes): ' + str(qry.duration) + '  , reserved-by: <a href="/showowned/' + str(qry.reservedby) + '">' + str(qry.reservedby) + '</a> , <a href="/deletereservation/' + str(qry.key.id()) + '">delete reservation </a></div>'
				else:
					x = x + '<div><a href="/showresource/'+ qry.name +'">'+ qry.name +'</a>  , start-time: ' + str(qry.start) + '  , duration(minutes): ' + str(qry.duration) + '  , reserved-by: <a href="/showowned/' + str(qry.reservedby) + '">' + str(qry.reservedby) + '</a></div>'
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
	if (format_allowed(start)==1):
		if (can_reserve(name, start, duration) == 1):
			end = datetime.strptime(start, '%H:%M') + timedelta(minutes=int(duration))
			resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(str(end)[11:16], '%H:%M').time(), duration=int(duration), tags='', createdby='', reserved=0, reservedby=users.get_current_user().nickname(), flag=1, timestamp=datetime.strptime(str(datetime.now())[11:16], '%H:%M').time())
			resource_key = resource.put()
			query = Resource.query(Resource.name == name, Resource.flag == 0)
			for qry in query.fetch(1):
				qry.timestamp = datetime.strptime(str(datetime.now())[11:16], '%H:%M').time()
				qry.put()
			return render_template('reserved_form.html',name=name,start=start,duration=duration)
		else:
			return "Reserved Time slot not available"
	else:
		return "Time format incorrect, please fix it"	

@app.route('/editresource/<string:name>')
def editresource(name):
	if users.get_current_user():
		query = Resource.query(Resource.name == name, Resource.flag == 0)
		for qry in query.fetch(1):
			name = qry.name
			start = qry.start
			end = qry.end
			tag = qry.tags
			return render_template('editresource.html', name=str(name), start=str(start)[0:5], end=str(end)[0:5], tags=str(tag))
	else:
    		return "please login first"

@app.route('/edited', methods=['POST'])
def edited_form():
	name = request.form['name']
	start = request.form['start']
	end = request.form['end']
	tags = request.form['tags']
	if (format_allowed(end)==1 and format_allowed(start)==1):
		return "GOOD"
	else:
		return "Time format incorrect, please fix it"

@app.route('/form')
def form():
	if users.get_current_user():
    		return render_template('form.html')
	else:
		return "please login first"
		#eastern = timezone('US/Eastern')
		#current_time = str(datetime.now(eastern))[11:16]
		#return current_time

@app.route('/submitted', methods=['POST'])
def submitted_form():
	name = request.form['name']
	start = request.form['start']
	end = request.form['end']
	tags = request.form['tags']
	if (format_allowed(end)==1 and format_allowed(start)==1):
		query = Resource.query(Resource.name == name)
	    	x = 0
    		for qry in query.fetch():
        		x = x + 1
    		if (x != 0):
        		return "resource with same name already exist, please change the name"
    		else:
        		resource = Resource(name=name, start=datetime.strptime(start, '%H:%M').time(), end=datetime.strptime(end, '%H:%M').time(), duration=0, tags=tags, createdby=users.get_current_user().nickname(), reserved=0, reservedby='', flag=0, timestamp=datetime.strptime(str(datetime.now())[11:16], '%H:%M').time())
        		resource_key = resource.put()
        		return render_template('submitted_form.html',name=name,start=start,end=end,tags=tags)
	else:
		return "Time format incorrect, please fix it"
def format_allowed(a):
	b = a.split(':')
	if (len(b)!=2):
		return 0
	elif (len(b[0])!=2 or len(b[1])!=2 ):
		return 0
	else:
		return 1

def can_reserve(name, start, duration):
	query = Resource.query(Resource.name == name, Resource.flag == 0)
	start_time = ""
	end_time = ""
	for qry in query.fetch(1):
		start_time = str(qry.start)
		end_time = str(qry.end)
	if (int(start.split(':')[0]) < int(start_time.split(':')[0]) or int(start.split(':')[0]) > int(end_time.split(':')[0])):
		return 0
	else:
		return 1

def reservation_pass(end):
	eastern = timezone('US/Eastern')
	current_time = str(datetime.now(eastern))[11:16]
	end_time = end[0:5]
	if (int(current_time.split(':')[0]) > int(end_time.split(':')[0])):
		return 1
	elif (int(current_time.split(':')[0]) == int(end_time.split(':')[0])):
		if (int(current_time.split(':')[1]) >= int(end_time.split(':')[1])):
			return 1
		else:
			return 0
	else:
		return 0
		
@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
