# opensource-final-project

Google App Engine URL: https://opensource-final-project.appspot.com/

Github repo: https://github.com/sdytjkgala/opensource-final-project

@app.route('/') - login page

@app.route('/home') - landing page

@app.route('/showowned/<string:name>') - reservations the user currently logged in owns

@app.route('/reservation') - all reservation

@app.route('/deletereservation/<string:id>') - delete a reservation

@app.route('/reservationbyuser/<string:name>') - reservation owned by a user

@app.route('/allresource') - all resources in the system
		
@app.route('/showtagresource/<string:name>') - resources with a specific tag

@app.route('/resourceown') - resources the user currently logged in owns

@app.route('/resourceownbyuser/<string:name>') - resource owned by a user

@app.route('/showresource/<string:name>') - show resource detail
		
@app.route('/showreservation/<string:name>') - show reservation detail

@app.route('/addreservation/<string:name>') - add a new reservation

@app.route('/rss/<string:name>') - generate RSS xml page

@app.route('/editresource/<string:name>') - edit a resource

@app.route('/form') - create a resource
