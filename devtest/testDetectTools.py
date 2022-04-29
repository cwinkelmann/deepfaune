import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0])) 
sys.path.append(curdir+'/../')

#######################
#######################
import cv2
#image = cv2.imread(curdir+"/chamois.jpg")
#image = cv2.imread('/home/vmiele/Developpement/deepfaunegui-modular/testdata/sanglier.jpg')
#image = cv2.imread('/home/vmiele/Developpement/deepfaunegui-modular/img.jpg')
#image = cv2.imread('/home/vmiele/Developpement/deepfaunegui/bug2/img0.jpg')
image = cv2.imread('/home/vmiele/Developpement/deepfaunegui/outofsample_data/chevreuil_ofb_gaudry_IMG_0238.JPG')
#image = cv2.resize(image, (1200,800))
threshold = 0.25
croppedimage = image

#######################
#######################
from detectTools import Detector
detector = Detector()
croppedimage, nonempty = detector.bestBoxDetection(image, 0.25)
print(nonempty)


#######################
#######################
from cv2 import cvtColor,COLOR_BGR2RGB,resize
CROP_SIZE=300
croppedimage2classifier =  resize(cvtColor(croppedimage, COLOR_BGR2RGB), (CROP_SIZE,CROP_SIZE))

from tensorflow.keras.applications.efficientnet import preprocess_input
preprocess_input(croppedimage2classifier)
import tensorflow as tf
tf.keras.utils.save_img("img.jpg",preprocess_input(croppedimage2classifier))

#######################
#######################
from cv2 import cvtColor,COLOR_BGR2RGB,resize
CROP_SIZE=300
cv2.imshow('window', resize(croppedimage, (CROP_SIZE,CROP_SIZE)))
k = cv2.waitKey(0)
if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()

    
#######################
#######################
from classifTools import Classifier, CROP_SIZE
import numpy as np
classifier = Classifier()
cropped_data = np.ones(shape=(1,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
cropped_data[0,:,:,:] = preprocess_input(croppedimage2classifier)
pred = classifier.predictOnBatch(cropped_data)
(pred*100).astype("int")


