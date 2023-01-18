import cv2
import os
import sys



YOLO_SIZE=608
CROP_SIZE=300
BATCH_SIZE = 4


import numpy as np
images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)


video_path = sys.argv[1]
video = cv2.VideoCapture(video_path)

total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
#get fps and video duration in s
fps = int(video.get(5))
#get duration of video in s
duration= int(total_frames / fps)

#messages to verif video param
print ("fps=" + str(fps))
print("duration=" + str(duration))
  
#for frame_nb in range(0,4):#range(0, BATCH_SIZE*fps, fps):
for frame_nb in range(0, BATCH_SIZE*int(fps/3), int(fps/3)):
    #get frame corresponding to frame_nb
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_nb)
    #read frame
    ret,frame = video.read()
    #if frame was read correctly, save frame to name path
    if ret:
        name = video_path[:-4]+"_F" + str(frame_nb) + '.jpg'
        # save extracted frame to name path
        cv2.imwrite(name, frame)
        #else break out
        resized_image = frame.resize((YOLO_SIZE, YOLO_SIZE))
        image_data = np.asarray(resized_image).astype(np.float32)
        image_data = image_data / 255. # PIL image is int8, this array is float32 and divided by 255
        images_data[0,:,:,:] = image_data
        print("Yolo sur images_data")
    else:
        #print duration, fps, total frames and last frame nb before breaking for verif
        print("Can't read frame number " + str(frame_nb) + " out of " + str(total_frames) + ". Expect " + str(int(frame_nb / fps)) + " images.")
        break

# Release all space and windows once done
video.release()
cv2.destroyAllWindows()
