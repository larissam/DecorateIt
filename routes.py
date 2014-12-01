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
import numpy as np
import cv2
import sys

from PIL import Image, ImageFilter, ImageOps

from OverlayPNG import OverlayImage

# Module for sending users emails
from flask.ext.mail import Mail, Message

# Our database model
import model

# Our image processing file
# from imageproc import enhance_image

# Paths to local folders for image storage
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = CURRENT_FOLDER + '/static/images/purikuras/'

# Allowed extensions for image upload function
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Initialize application and set upload folder
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #Needed to have sessions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up mail app configurations so can send email
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'larissa.muramoto@gmail.com'
app.config["MAIL_PASSWORD"] = 'maminouPOOF'

# Initialize Flask Mail instance to handle sending emails
mail = Mail(app)

""" If client sends get request, then display the register template.
Otherwise, process register template information and put user in database. """
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

""" If client sends get request, then display the login template. 
Otherwise, process login template information and store login data in the app's session. """
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':

		#Get data from the user
		email = request.form['email']
		password = request.form['password']

		#Use the data to get user from database
		user = model.session.query(model.User).filter_by(email=email).first()

		#Make sure password is correct
		if not user or user.password != password:
			flash("Incorrect username or password. Please try again!", 'danger')
			return redirect(url_for("login"))


		#Log the user in and take them to their gallery
		session['id'] = user.id
		session['email'] = email
		session['logged_in'] = True
		return redirect(url_for("main"))

	return render_template("login.html")

""" Removes the session info from the app and redirects client
to the login page."""
@app.route('/logout')
def logout():
	session.clear()
	flash("You have been successfully logged out.", 'success')
	return redirect(url_for('login'))

""" Gets the decorated photos from the database and displays them
to the user. """
@app.route('/main')
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

""" Shows the template that allows the user to either upload
an image or take one with the photobooth. """
@app.route('/choose')
def choose():
	return render_template("choose.html")

""" Helper function for the upload_file handler that makes sure the
file the user chooses has a valid extension. """
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

""" Gets the file from the user, puts a copy in local storage, and 
puts a reference file in the database. """
@app.route('/uploadfile', methods=['POST'])
def upload_file():	

	#Get the file from the user
	file = request.files['file']

	#Make sure it's a valid file
	if file and allowed_file(file.filename):

		#Generates a unique storage filename to reference the image
		filename = secure_filename(file.filename)
		filename, extension = os.path.splitext(filename)
		filename = str(session['id']) + filename + str(datetime.utcnow()).replace(" ", "") + extension
		
		#Save file to disk
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		#Full filename
		full_filename = "static/images/purikuras/" + filename


		#If they want to process the image, then do so
		if request.form.getlist('imageproc'):
			enhance_image(full_filename)

		#Store filename in database
        newPurikura = model.Purikura(user_id=session['id'], combined_src=full_filename, foreground_src=full_filename)
        model.session.add(newPurikura)
        model.session.commit()
        return redirect(url_for('decorate', filename=full_filename))
 
""" Enlarges eyes and smoothes skin in the image using OpenCV. """
def enhance_image(filename):

	#Haar cascades for face and eye detection
	face_cascade = cv2.CascadeClassifier('imageproc/haarcascade.xml')
	eye_cascade = cv2.CascadeClassifier('imageproc/haarcascade_eye.xml')

	#Image mask for eye
	mask = cv2.imread('imageproc/mask2.png', 0) #0 means grayscale

	#Blending coefficients when eye with transparent mask is put back on face
	S = (0.5, 0.5, 0.5, 0.5)
	D = (0.5, 0.5, 0.5, 0.5)

	#Read in image and make a gray version for eye detection
	img = cv2.imread(filename)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


	base_img = cv2.cv.LoadImage(filename)
	#Detect faces
	faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 7, minSize = (10, 10), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

	for (x,y,w,h) in faces:
		#Select region from (x,y) to (x+w, y+h)
		roi_gray = gray[y:y+h, x:x+w]
		roi_color = img[y:y+h, x:x+w]
		eyes = eye_cascade.detectMultiScale(roi_gray)

		for (ex,ey,ew,eh) in eyes:
			#Select eye
			eye = roi_color[ey:ey+eh, ex:ex+ew]

			#Enlarge eye 20%
			big_eye = cv2.resize(eye,None,fx=1.2, fy=1.2, interpolation = cv2.INTER_CUBIC)

			#Use the big_eye's height and width to resize the eye mask
			big_eye_h, big_eye_w = big_eye.shape[:2]
			mask = cv2.resize(mask,(big_eye_w, big_eye_h), interpolation = cv2.INTER_CUBIC)

			#Mask the big eye and make a gray version
			big_eye_masked = cv2.bitwise_and(big_eye, big_eye, mask=mask)
			big_eye_gray_masked = cv2.cvtColor(big_eye_masked, cv2.COLOR_BGR2GRAY)

			#Use the gray version to generate the alpha channel for your transparent image
			big_eye_thresh, alpha = cv2.threshold(big_eye_gray_masked, 0, 255, cv2.THRESH_BINARY)

			#Split the big eye into r, g, and b channels
			big_eye_b, big_eye_g, big_eye_r = cv2.split(big_eye_masked)

			#Add the alpha channel to the rgb channels and merge into a new image
			rgba = (big_eye_b, big_eye_g, big_eye_r, alpha)
			big_eye_w_alpha = cv2.merge(rgba)

			#Write the eye with transparency mask to disk so OverlayPNG script can access
			cv2.imwrite('imageproc/bigeyewithalpha.png', big_eye_w_alpha)
			big_eye_w_alpha = cv2.cv.LoadImage('imageproc/bigeyewithalpha.png')

			#Overlay the original with the new eye
			OverlayImage(base_img, big_eye_w_alpha, x+ex-5, y+ey-5, S, D)

			#Save revised version to disk
			cv2.cv.SaveImage('imageproc/src.png', base_img)

		#Open version again as a numpy array
		img = cv2.imread('imageproc/src.png')
		roi_color = img[y:y+h, x:x+w]

		#Smooth face and replace it
		smoothed_face = cv2.bilateralFilter(roi_color, 3, 75, 75)
		roi_color[0:smoothed_face.shape[1], 0:smoothed_face.shape[0]] = smoothed_face
	cv2.imwrite(filename, img)


""" Shows the photobooth template. """
@app.route('/photobooth')
def photobooth():
	return render_template('photobooth.html')

""" Gets file from the photobooth, converts it from base64 data to a file.
Then saves it in local storage and puts a reference in the database. """
@app.route('/uploadwebcamphoto', methods=['POST'])
def upload_webcam_photo():

	#Gets the file the user selected on the photobooth page
	raw_file = request.form['selectedPhotos']

	storage_filename = "static/images/purikuras/" + str(session['id']) + 'webcamphoto' + str(datetime.utcnow()).replace(" ", "") + ".jpg"

	convert_datauri_to_file(raw_file, storage_filename)

	#Add file to database
	newPurikura = model.Purikura(user_id=session['id'], combined_src=storage_filename, foreground_src=storage_filename)
	model.session.add(newPurikura)
	model.session.commit()

	return redirect(url_for('decorate', filename=storage_filename))

""" Converts base64 image data to a file. """
def convert_datauri_to_file(datauri, filename):
	
	#Removes the header from the b64 image data
	b64_data = datauri.replace("data:image/jpeg;base64,", "").strip()
	
	#Converts it to binary
	binary_data = a2b_base64(b64_data)
	
	#Open the specified file and write in the binary data
	fd = open(filename, 'wb')
	fd.write(binary_data)
	fd.close()

""" Displays the about template. """
@app.route('/about')
def about():
	return render_template('about.html')

""" Displays the decorate template with a file specified by the upload handlers. """
@app.route('/decorate')
def decorate():
	return render_template('decorate.html', filename=request.args.get('filename'))

""" Sends mail to recipients specified by user using Flask-Mail. """
@app.route('/sendmail', methods=['POST'])
def send_mail():
	print request.form['address']
	print "filename? ", request.form['filename']

	addresses = request.form['address'].split(',')
	msg = Message(request.form['subject'],
                  sender="larissa.muramoto@gmail.com",
                  recipients=addresses)
	msg.add_recipient(session['email'])
	msg.html = request.form['body'] + "<br />" + "<br />" + "Here is your decorated image from DecorateIt! Visit us again!"
	
	with app.open_resource(request.form['filename'].strip()) as fp:
		msg.attach("image.jpg", "image/jpg", fp.read())

	print "i sent mail?"
	mail.send(msg)
	return json.dumps({'status':'OK'})

""" Deletes the decorated image from the user's gallery. """
@app.route('/deletepurikura', methods=['POST'])
def delete_purikura():
	
	#Get the filename of the image to be deleted
	to_be_deleted = request.form['filename']
	
	#Find the matching filename in the database and delete it
	purikura = model.session.query(model.Purikura).filter_by(user_id=session['id'], combined_src=to_be_deleted).delete()
	model.session.commit()
	
	#Remove the file from local storage as well
	os.remove(to_be_deleted)
	
	#Redirect user to gallery
	return redirect(url_for('main'))

""" Saves an edited image to the database. """
@app.route('/updatepurikura', methods=['POST'])
def update_purikura():

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
