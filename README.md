# DecorateIt

### DecorateIt is a web application that:
1. Lets you upload a photo or take one using the built-in photobooth

2. Automatically enhances your photo by enlarging your eyes and smoothing your skin

3. Lets you decorate your chosen photo using markers, brushes, and stamps

4. Lets you download, email, or save your decorated photo to your gallery


### How it works

- Image enhancement (eye enlargement and skin smoothing) done using OpenCV. First, OpenCV is used to detect the face and eyes. Then, it enlarges the eyes. To improve blending, it applies a transparency mask (created by deconstructing the image into r,g,b channels and reconstructing it with an alpha/transparency channel) to each enlarged eye before pasting it back on the face. Finally, bilateral filtering is used to smooth facial skin without sacrificing image sharpness.
- Image editor built using pure HTML5 Canvas and Javascript. Javascript uses the mouse's position on the canvas to determine where to draw. No plugins used.
- Photobooth built using pure HTML5 canvas and Javascript. No plugins used.

### To get it running locally

1. Clone this repo
<code>$ git clone https://github.com/larissam/DecorateIt-NoOpenCV.git </code>

2. Install dependencies
<code>$ pip install -r requirements.txt </code>

3. Install [OpenCV 2.4.9](http://opencv.org/downloads.html)

4. Run the app from the terminal
<code>$ python routes.py </code>

### Notes

OpenCV can be difficult to install and configure. For your convenience, is a [version without the OpenCV image processing](https://github.com/larissam/DecorateIt-NoOpenCV). Additionally, here is a [version deployed on Heroku](https://github.com/larissam/DecorateIt-Heroku).

