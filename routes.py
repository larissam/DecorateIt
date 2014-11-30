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

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = CURRENT_FOLDER + '/static/images/purikuras/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #why do I have this again..?
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#editor = Blueprint('editor', __name__, template_folder='static')

@app.route('/', methods=['GET', 'POST'])
def index():
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
def logout():
	session.clear()
	flash("You have been successfully logged out.", 'success')
	return redirect(url_for('login'))

@app.route('/main')
def main():
	#get purikuras from the database
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

@app.route('/choose', methods=['GET', 'POST'])
def choose():
	if request.method == 'POST':
		#get the form
		#if they selected upload, save the filename in the session
		#otherwise, redirect to photobooth
		pass
	return render_template("choose.html")

# #testing some data stuff. please ignore
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadfile', methods=['POST'])
def upload_file():
	
	file = request.files['file']

	if file and allowed_file(file.filename):

		#if they want to process the image, then do it
		if request.form['imageProc'] == "yes":
			print "YESSSSSSSSSSSSS!"
			#file = enhance_image(file)


		#save to disk
		filename = secure_filename(file.filename)

		#modify the filename so every purikura is unique
		filename, extension = os.path.splitext(filename)
		filename = str(session['id']) + filename + str(datetime.utcnow()).replace(" ", "") + extension

		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		full_filename = "static/images/purikuras/" + filename
		print "full_filename: ", full_filename

		#for file dimensions
		# im = Image(str(full_filename))
		# print "image dimensions: ", im.size

        #save file path to database

        newPurikura = model.Purikura(user_id=session['id'], combined_src=full_filename, foreground_src=full_filename)
        model.session.add(newPurikura)
        model.session.commit()
	
        
        return redirect(url_for('decorate', filename=full_filename))
	# 	#return redirect(url_for('show_purikura', filename=full_filename))
 
 #only do this if image is of minimum size.
def enhance_image(raw_file):
	#do image processing stuff
	return raw_file

@app.route('/photobooth')
def photobooth():
	return render_template('photobooth.html')

#NEED A FUNCTION TO CONVERT BASE64 TO FILE.
@app.route('/uploadwebcamphoto', methods=['POST'])
def upload_webcam_photo():
	raw_file = request.form['selectedPhotos']

	storage_filename = "static/images/purikuras/" + str(session['id']) + 'webcamphoto' + str(datetime.utcnow()).replace(" ", "") + ".jpg"

	convert_datauri_to_file(raw_file, storage_filename)

	#factor this out later
	newPurikura = model.Purikura(user_id=session['id'], combined_src=storage_filename, foreground_src=storage_filename)
	model.session.add(newPurikura)
	model.session.commit()

	return redirect(url_for('decorate', filename=storage_filename))


def convert_datauri_to_file(datauri, filename):
	b64_data = datauri.replace("data:image/jpeg;base64,", "").strip()

	binary_data = a2b_base64(b64_data)

	fd = open(filename, 'wb')
	fd.write(binary_data)
	fd.close()

@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/decorate', methods=['GET'])
def decorate():
	#return render_template('decorate.html', snapshots=session['snapshots'])
	return render_template('decorate.html', filename=request.args.get('filename'))

# @app.route('/decorateold', methods=['GET'])
# def decorate_old():
# 	#return render_template('decorate.html', snapshots=session['snapshots'])
# 	return render_template('decorate_prestyle.html', filename=request.args.get('filename'))

@app.route('/deletepurikura', methods=['POST'])
def delete_purikura():
	to_be_deleted = request.form['filename']
	purikura = model.session.query(model.Purikura).filter_by(user_id=session['id'], combined_src=to_be_deleted).delete()
	model.session.commit()
	os.remove(to_be_deleted)
	return redirect(url_for('main'))


@app.route('/updatepurikura', methods=['POST'])
def update_purikura():
	#the frontend will send you the filename. you should know the user id.
	#query for the purikura
	#change some stuff
	#put the revised stuff back in the database
	#redirect to main?

	print request.form['updated_src']

	updated_image_data = request.form['updated_src']
	storage_filename = request.form['filename']

	convert_datauri_to_file(updated_image_data, storage_filename)
	
	purikura = model.session.query(model.Purikura).filter_by(user_id=session['id'], combined_src=storage_filename)
	purikura.combined_src = storage_filename #some new thing you pass in?
	model.session.commit()


	print ("HeYYYYYYYYYYYYYYYY!")
	return json.dumps({'status':'OK'})

	#return redirect(url_for('about'))

if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads" our web app
    # if we change the code.
    app.run(debug=True)
