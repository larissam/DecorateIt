# DecorateIt

DecorateIt is a web application that:
1. Lets you upload a photo or take one using the built-in photobooth
2. Automatically enhances your photo by enlarging your eyes and smoothing your skin
3. Lets you decorate your chosen photo using markers, brushes, and stamps
4. Lets you download, email, or save your decorated photo to your gallery


### How it works

- Photobooth built using HTML5 getUserMedia(), HTML5 canvas, and Javascript. No plugins used.
- Image enhancement (eye enlargement and skin smoothing) done using OpenCV. First, OpenCV is used to detect the face and eyes. Then, it enlarges the eyes. To improve blending, it applies a transparency mask (created by deconstructing the image into r,g,b channels and reconstructing it with an alpha/transparency channel) to each enlarged eye before pasting it back on the face. Finally, bilateral filtering is used to smooth facial skin without sacrificing image sharpness.
- Image editor built using HTML5 Canvas and Javascript. Javascript uses the mouse's position on the canvas to determine where to draw. No plugins used.

