from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
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
