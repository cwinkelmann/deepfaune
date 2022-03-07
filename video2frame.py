import cv2
import os

folder = input("Nom du dossier : ")
video_name = input("Nom du fichier : ")
vidcap = cv2.VideoCapture(video_name)
frames = []

while True:
    success,image = vidcap.read()
    if not success:
        break
    frames.append(image)

size = len(frames)
step = int(size/10)

if step == 0:
	step == 1

for i in range(0, size, step):    
    cv2.imwrite(os.path.join(folder,"{}_frame{:d}.jpg".format(video_name.split(".")[-2],i)), frames[i])

print("{} images are extracted from {}, {} are saved.".format(i,folder, int(size/step)))
