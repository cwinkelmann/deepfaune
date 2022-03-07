import cv2
import os

folder = input("Nom du dossier : ") # the folder where the frames will be extracted into
video_name = input("Nom du fichier : ") # the video we want to extract frames from
vidcap = cv2.VideoCapture(video_name)
frames = [] # array of all extracted frames (not optimal to do so, but easier to understand for testing)

while True:
    success,image = vidcap.read() # extracts a frame (1 by 1)
    if not success: # if not success, there is no more frames to extract
        break
    frames.append(image) # adding the frame into the array (not optimal)

size = len(frames)
step = int(size/10) # to keep 1 frame every 10 frames
if step == 0:
	step == 1

for i in range(0, size, step):    
    cv2.imwrite(os.path.join(folder,"{}_frame{:d}.jpg".format(video_name.split(".")[-2],i)), frames[i]) # creates a jpg file for the frame we extracted

print("{} images are extracted from {}, {} are saved.".format(i,folder, int(size/step)))
