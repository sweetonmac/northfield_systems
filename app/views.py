from sqlite3 import dbapi2 as sqlite3
from flask import render_template, Flask, request, flash, url_for, redirect,abort, g, Response, session, Request
from werkzeug.utils import secure_filename
from app import app
import json
import os


# Load default config or override config from an environment variable, if it exists
app.config.update(dict(
    DATABASE='M2M.db',
    DEBUG=True,
    SECRET_KEY='someRandomKey',
    USERNAME='m2m',
    PASSWORD='challenge'
))

UPLOAD_FOLDER = '/home/drew/350'
ALLOWED_EXTENSIONS = set(['txt'])
userDB = {'Drew':'fubar', 'admin':'admin'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def check_user(username, password):
	if username in userDB and userDB[username] == password:
		session['username'] = username
		session['key'] = password #change to key later
		flash("login sucsessful")
		return 1
	else:
		flash("login failed")
		session.clear()
		return -1


@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
def index():
	if request.method =='POST':
		username = request.form['username']
		password = request.form['password'] 
		if check_user(username, password) == 1:
			return 'Logged in as %s' % session['username']
		else:
			return 'failed to log in'
	
	return render_template("index.html")

@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/vsms')
def vsms():
	return render_template('vsms.html')


@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/extra')
def extra():
	return render_template('extra.html')


@app.route('/plot')
def plot():
	try:	
		username = session['username']
	except KeyError:
		return redirect('/index')
	try:	
		key = session['key']	
	except KeyError:
		return redirect('/index')
	
	if check_user(username, key) == 1:
		return render_template("plot.html")
	else:
		return redirect('/index')



@app.route('/upl', methods=['GET','POST'])
def upl():
	if request.method =='POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			lines = file.readlines()
			#filename = secure_filename(file.filename)
			#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return lines[0]
	return render_template("upl.html")



@app.route('/piup', methods=['GET', 'POST'])
def piup():	
	if request.method =='POST':
		init_db()		
		db = get_db()
		file = request.files['file']
		if file and allowed_file(file.filename):
			lines = file.readlines()
			y = 0
			x = 0
			tmp = lines[0].split('*')
			tmp2 = tmp[0].split('&')
			memi = tmp2[0]
			imsi = tmp2[1]
			thedate = tmp2[2]
			time = tmp2[3]
			cpuid = tmp2[4]
			lat = tmp2[5]
			lon = tmp2[6]
			alt = tmp2[7]
			speed = tmp2[8]
			Rcount = tmp2[9]
			temp = tmp2[10]
			lev = tmp2[11]
			spare2 = tmp2[12]
			db.execute('insert into records (imei, imsi, thedate, time , cpuid, lat, lon , alt , speed ,Rcount,temp,lev,spare2) values (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)',[memi,imsi,thedate,time,cpuid,lat,lon,alt,speed,Rcount,temp,lev,spare2])
			db.commit()

			for x in range(1,len(tmp)-1):
			    tmp2 = tmp[x].split('&')
			    thedate = str(float(thedate) - float(tmp2[0]))
			    time = ("%13.6F" %(float(time) - float(tmp2[1]))).replace(' ','0')
			    lat = str(float(lat) - float(tmp2[2]))
			    lon = str(float(lon) - float(tmp2[3]))
			    alt = str(float(alt) - float(tmp2[4]))
			    speed = str(float(speed) - float(tmp2[5]))
			    Rcount = str(float(Rcount) - float(tmp2[6]))
			    temp = str(float(temp) - float(tmp2[7]))
			    lev = str(int(float(lev) - float(tmp2[8])))
			    spare2 = str(int(float(spare2)-float(tmp2[9])))
			    db.execute('insert into records (imei, imsi, thedate, time , cpuid, lat, lon , alt , speed ,Rcount,temp,lev,spare2) values (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)',[memi,imsi,thedate,time,cpuid,lat,lon,alt,speed,Rcount,temp,lev,spare2])
			db.commit()
			return "all data worked- will output settings for pi"

	else:
		return render_template("piup.html")

#################################
#       Database methods        #
#################################


def connect_db():
    """Connects to the database defined in config."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

