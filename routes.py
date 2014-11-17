from flask import Flask, render_template, request, redirect, session, url_for, flash, escape, Blueprint

#import re
#import Image
import cv2
import numpy as np
import jinja2
import model
import io

import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

UPLOAD_FOLDER = '/Users/Larissa/Desktop/testupload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #why do I have this again..?
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#editor = Blueprint('editor', __name__, template_folder='static')

#testing some data stuff. please ignore
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('displaytest.html', filename=filename)
            #return redirect(url_for('displaytest',
            #                        filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

# @app.route('/displaytest')
# def displaytest():
# 	return """
# 	<p>%s</p>

# 	""" % filename


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		# Prevent users from having the same usernames; usernames should be unique.
		isExisting = model.session.query(model.User).filter_by(email=email).first()
		if isExisting:
			flash('This username already exists. Please select another one!')
			return redirect(url_for("index"))

		# Creates a new user account as long as the username is unique.
		newuser = model.User(email=email, password=password)
		model.session.add(newuser)
		model.session.commit()
		flash('Your account has been created!')
		return redirect(url_for("login"))

	return render_template("register.html", title = "Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# if 'email' in session:
		# 	redirect(url_for("main"))
		print "I am here!"

		email = request.form['email'] #for WTForms: form.email.data
		print "email: ", email
		password = request.form['password'] #for WTForms: form.password.data
		print "password: ", password

		user = model.session.query(model.User).filter_by(email=email).first() #look for existing flask function

		if not user or user.password != password:
			flash("Incorrect username or password. Please try again!")
			return redirect(url_for("login"))

		session['email'] = email
		session['logged_in'] = True
		return redirect(url_for("main"))

	return render_template("login.html")

@app.route('/logout')
def logout():
	session.clear()
	flash("Logged out!")
	return redirect(url_for('login'))

@app.route('/main')
def main():
	#get purikuras from the database
	purikuras = []

	return render_template('main.html', purikura_list = purikuras)

#just for testing. not getting purikura info from server. just displaying hardcoded image
@app.route('/purikuradetailstest')
def show_purikura():
	return render_template('purikura_details.html')

# @app.route('/purikura/<int:id>')
# def show_purikura(id):
# 	#get purikura from the database based on id
# 	#placeholders for now because we can't insert purikuras into database :(
# 	purikura = []
# 	return render_template('purikura_details.html', display_purikura = purikura)

@app.route('/choose', methods=['GET', 'POST'])
def choose():
	if request.method == 'POST':
		#get the form
		#if they selected upload, save the filename in the session
		#otherwise, redirect to photobooth
		pass
	return render_template("choose.html")


@app.route('/photobooth')
def photobooth():
	return render_template('photobooth.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/processimage', methods=['POST'])
def process_image():
	if request.method == 'POST':
		snapshots = request.form.getlist("selectedPhotos")
		# session['snapshots'] = snapshots
		print "snapshots:", snapshots

		#return HttpResponse(pic, content_type='image/jpeg')

		#convert to openCV
		"""
		openCVimage = numpy.array(im)
		openCVimage = openCVimage[:, :, ::-1].copy()


		#process image using openCV
		"""

		return redirect("/decorate")
		
	# elif request.method == 'GET':
	# 	return render_template('decorate.html')

@app.route('/decorate', methods=['GET'])
def decorate():
	#return render_template('decorate.html', snapshots=session['snapshots'])
	return render_template('decorate.html')

if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads" our web app
    # if we change the code.
    app.run(debug=True)