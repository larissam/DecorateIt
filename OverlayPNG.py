# Adapted from http://www.aishack.in/2010/07/transparent-image-overlays-in-opencv/
# Note: This code assumes a PNG with a Color->Transparency, with black as the alpha color

from cv2 import *

S = (0.5, 0.5, 0.5, 0.5)			# Define blending coefficients S and D
D = (0.5, 0.5, 0.5, 0.5)

def OverlayImage(src, overlay, posx, posy, S, D):

	for x in range(overlay.width):

		if x+posx < src.width:

			for y in range(overlay.height):

				if y+posy < src.width:

					source = cv.Get2D(src, y+posy, x+posx)
					over   = cv.Get2D(overlay, y, x)
					merger = [0, 0, 0, 0]

					for i in range(3):
						if over[i] == 0:
							merger[i] = source[i]
						else:
							merger[i] = (S[i]*source[i]+D[i]*over[i])

					merged = tuple(merger)

					cv.Set2D(src, y+posy, x+posx, merged)