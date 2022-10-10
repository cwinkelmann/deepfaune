import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0])) 
sys.path.append(curdir+'/../')

#######################
#######################
import cv2
import numpy as np
BATCH_SIZE=8

#######################
#######################
import numpy as np
from detectTools import Detector
detector = Detector()
from classifTools import Classifier, CROP_SIZE
classifier = Classifier()

cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)


idxnonempty = []
video = cv2.VideoCapture("/home/vmiele/Developpement/deepfaunegui-modular/devtest/video.mp4")
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fps = int(video.get(5))
duration= int(total_frames / fps)
print ("fps=" + str(fps))
print("duration=" + str(duration))
lag = fps # lag between two successice frames
k = 0
for kframe in range(0, BATCH_SIZE*lag, lag):
    video.set(cv2.CAP_PROP_POS_FRAMES, kframe)
    ret,frame = video.read()
    if not ret:
        pass # Corrupted or unavailable image, considered as empty
    else:
        original_image = frame
        croppedimage, category = detector.bestBoxDetection(original_image)
        if category>0:
            cropped_data[k,:,:,:] =  classifier.preprocessImage(croppedimage)
            idxnonempty.append(k)
    k = k+1
if len(idxnonempty):
    pred = classifier.predictOnBatch(cropped_data[[idx for idx in idxnonempty],:,:,:])

pred = np.sum(pred,axis=0)/len(idxnonempty)
(pred*100).astype("int")


#################
import pandas as pd
df_filename = pd.DataFrame({'filename':["/home/vmiele/Developpement/deepfaunegui-modular/devtest/video.mp4"]})
from predictTools import PredictorVideo
from classifTools import txt_classes
predictor = PredictorVideo(df_filename, 0.25, txt_classes["fr"]+["vide"], "indéfini")
predictor.nextBatch()
