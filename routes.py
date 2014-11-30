from flask import Flask, render_template, request, redirect, session, url_for, flash, escape, Blueprint
import jinja2

# Modules for converting and saving photobooth images to disk.
import io
import os
import json
from base64 import decodestring
from binascii import a2b_base64
from werkzeug import secure_filename
from datetime import datetime

# Modules for image processing
import cv2
import numpy as np
from PIL import Image

# Our database model
import model

# Paths to local folders for image storage
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = CURRENT_FOLDER + '/static/images/purikuras/'

# Allowed extensions for image upload function
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Initialize application and set upload folder
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
""" If client sends get request, then display the register template.
Otherwise, process register template information and put user in database. """
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		passwordcheck = request.form['passwordcheck']

		# Prevent users from having the same usernames; usernames should be unique.
		isExisting = model.session.query(model.User).filter_by(email=email).first()
		if isExisting:
			flash('This email already exists. Please use another one!', 'danger')
			return redirect(url_for("index"))

		if password != passwordcheck:
			flash('Your passwords do not match. Please try again!', 'danger')
			return redirect(url_for("index"))

		# Creates a new user account as long as the username is unique.
		newuser = model.User(email=email, password=password)
		model.session.add(newuser)
		model.session.commit()
		flash('Your account has been created!', 'success')
		return redirect(url_for("login"))

	return render_template("register.html", title = "Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
""" If client sends get request, then display the login template.
Otherwise, process login template information and store login data
in the app's session. """
	if request.method == 'POST':

		email = request.form['email'] #for WTForms: form.email.data
		print "email: ", email
		password = request.form['password'] #for WTForms: form.password.data
		print "password: ", password

		user = model.session.query(model.User).filter_by(email=email).first() #look for existing flask function

		if not user or user.password != password:
			flash("Incorrect username or password. Please try again!", 'danger')
			return redirect(url_for("login"))


		#DOES THIS WORK?!?!
		session['id'] = user.id
		print "user id is: ", session['id']


		session['email'] = email
		session['logged_in'] = True
		return redirect(url_for("main"))
	return render_template("login.html")

@app.route('/logout')
""" Removes the session info from the app and redirects client
to the login page."""
def logout():
	session.clear()
	flash("You have been successfully logged out.", 'success')
	return redirect(url_for('login'))

@app.route('/main')
""" Gets the decorated photos from the database and displays them
to the user. """
def main():
	purikuras = model.session.query(model.Purikura).filter_by(user_id=session['id'])
	
	return render_template('main.html', purikura_list = purikuras)

#just for testing. getting image from server.
@app.route('/purikuradetails')
def show_purikura():
	filename = request.args.get('filename')
	return render_template('purikura_details.html', filename=filename)

# @app.route('/purikura/<int:id>')
# def show_purikura(id):
# 	#get purikura from the database based on id
# 	#placeholders for now because we can't insert purikuras into database :(
# 	purikura = []
# 	return render_template('purikura_details.html', display_purikura = purikura)

@app.route('/choose')
def choose():
""" Shows the template that allows the user to either upload
an image or take one with the photobooth. """
	return render_template("choose.html")

# #testing some data stuff. please ignore
def allowed_file(filename):
""" Helper function for the upload_file handler that makes sure the
file the user chooses has a valid extension. """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadfile', methods=['POST'])
def upload_file():
""" Gets the file from the user, puts a copy in local storage, and 
puts a reference file in the database. """
	
	file = request.files['file']

	if file and allowed_file(file.filename):

		#if they want to process the image, then do it
		if request.form['imageProc'] == "yes":
			print "YESSSSSSSSSSSSS!"
			#file = enhance_image(file)


		#save to disk
		
		
		#Generates a unique storage filename to reference the image
		filename = secure_filename(file.filename)
		filename, extension = os.path.splitext(filename)
		filename = str(session['id']) + filename + str(datetime.utcnow()).replace(" ", "") + extension
		
		#Saves file to disk
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		
		full_filename = "static/images/purikuras/" + filename
		print "full_filename: ", full_filename

        newPurikura = model.Purikura(user_id=session['id'], combined_src=full_filename, foreground_src=full_filename)
        model.session.add(newPurikura)
        model.session.commit()
	
        
        return redirect(url_for('decorate', filename=full_filename))
 
 #only do this if image is of minimum size.
def enhance_image(raw_file):
""" Enlarges eyes and smoothes skin in the image using OpenCV. """
	#do image processing stuff
	return raw_file

@app.route('/photobooth')
def photobooth():
""" Shows the photobooth template. """
	return render_template('photobooth.html')

#NEED A FUNCTION TO CONVERT BASE64 TO FILE.
@app.route('/uploadwebcamphoto', methods=['POST'])
def upload_webcam_photo():
""" Gets file from the photobooth, converts it from base64 data to a file.
Then saves it in local storage and puts a reference in the database. """
	
	#Gets the file the user selected on the photobooth page
	raw_file = request.form['selectedPhotos']

	storage_filename = "static/images/purikuras/" + str(session['id']) + 'webcamphoto' + str(datetime.utcnow()).replace(" ", "") + ".jpg"

	convert_datauri_to_file(raw_file, storage_filename)

	#Add file to database
	newPurikura = model.Purikura(user_id=session['id'], combined_src=storage_filename, foreground_src=storage_filename)
	model.session.add(newPurikura)
	model.session.commit()

	return redirect(url_for('decorate', filename=storage_filename))


def convert_datauri_to_file(datauri, filename):
""" Converts base64 image data to a file. """
	
	#Removes the header from the b64 image data
	b64_data = datauri.replace("data:image/jpeg;base64,", "").strip()
	
	#Converts it to binary
	binary_data = a2b_base64(b64_data)
	
	#Open the specified file and write in the binary data
	fd = open(filename, 'wb')
	fd.write(binary_data)
	fd.close()

@app.route('/about')
def about():
""" Displays the about template. """
	return render_template('about.html')


@app.route('/decorate')
def decorate():
""" Displays the decorate template with a file specified by the upload handlers. """
	return render_template('decorate.html', filename=request.args.get('filename'))


@app.route('/deletepurikura', methods=['POST'])
def delete_purikura():
""" Deletes the decorated image from the user's gallery. """
	
	#Get the filename of the image to be deleted
	to_be_deleted = request.form['filename']
	
	#Find the matching filename in the database and delete it
	purikura = model.session.query(model.Purikura).filter_by(user_id=session['id'], combined_src=to_be_deleted).delete()
	model.session.commit()
	
	#Remove the file from local storage as well
	os.remove(to_be_deleted)
	
	#Redirect user to gallery
	return redirect(url_for('main'))


@app.route('/updatepurikura', methods=['POST'])
def update_purikura():
""" Saves an edited image to the database. """

	#Get the revised data and the old filename from the user
	updated_image_data = request.form['updated_src']
	storage_filename = request.form['filename']
	
	#Convert it to an image
	convert_datauri_to_file(updated_image_data, storage_filename)
	
	#Put the revised image in the database
	purikura = model.session.query(model.Purikura).filter_by(user_id=session['id'], combined_src=storage_filename)
	purikura.combined_src = storage_filename
	model.session.commit()
	
	#Tell the frontend it worked
	return json.dumps({'status':'OK'})

if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads" our web app
    # if we change the code.
    app.run(debug=True)
