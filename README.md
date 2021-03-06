# DecorateIt

### DecorateIt is a web app that...
1. Lets you upload a photo or take one using the built-in photobooth (seen below):
![Photobooth](https://github.com/larissam/DecorateIt/blob/master/readmeimages/photobooth.png "Photobooth")

2. Automatically enhances your photo by enlarging your eyes and smoothing your skin, as shown in the gif below:
![Image Processing](https://github.com/larissam/DecorateIt/blob/master/readmeimages/enlargeeyes.gif "Image Processing")

3. Lets you decorate your chosen photo using markers, brushes, and stamps:
![Editor](https://github.com/larissam/DecorateIt/blob/master/readmeimages/editor.png "Editor")

4. Lets you download, email, or save your decorated photo to your gallery:
![Gallery](https://github.com/larissam/DecorateIt/blob/master/readmeimages/gallery.png "Gallery")


### To get it running locally

1. Clone this repo
<code>$ git clone https://github.com/larissam/DecorateIt.git </code>

2. Install dependencies
<code>$ pip install -r requirements.txt </code>

3. Install [OpenCV 2.4.9](http://opencv.org/downloads.html)

4. Run the app from the terminal
<code>$ python routes.py </code>


### Alternate versions
1. [DecorateIt without OpenCV](https://github.com/larissam/DecorateIt-NoOpenCV) - download this repo to run locally if OpenCV is difficult to configure.
2. DecorateIt on Heroku - In-progress version deployed on Heroku. CAVEATS: does not have photobooth or OpenCV functionality. Only supports jpgs and pngs. Needs security improvements. Only tested on Chrome version 39.0.2171.71 running OSX. 


### How it works

- Image enhancement (eye enlargement and skin smoothing) is done using OpenCV. First, OpenCV (Viola-Jones algorithm) is used to detect the face and eyes. Then, it cuts out the eyes and enlarges them 20%. To improve blending, it applies a transparency mask (created by deconstructing the image into r,g,b channels and reconstructing it with an alpha/transparency channel) to each enlarged eye before pasting it back on the face. Finally, bilateral filtering is used to smooth facial skin without sacrificing image sharpness.

![Image Processing Method](https://github.com/larissam/DecorateIt/blob/master/readmeimages/imageprocessingmethod.png "Image Processing Method")

- Image editor was built using pure HTML5 Canvas and Javascript. Javascript uses the mouse's position on the canvas to determine where to draw. No plugins used.
- Photobooth was built using pure HTML5 canvas and Javascript. No plugins used.


### Stack
- Photo editor and photobooth: HTML5 Canvas, JavaScript, Python, HTML, CSS, Bootstrap
- Image processing, email handling, and database: Python, OpenCV, SQLite, SQLAlchemy, Flask-Mail
- Framework: Flask



