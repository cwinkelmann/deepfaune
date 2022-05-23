import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from detectTools import Detector, YOLO_SIZE
from classifTools import Classifier, CROP_SIZE, NBCLASSES, txt_classes
LANG = 'fr' # or 'gb'
detector = Detector()
classifier = Classifier()

## LOADING IMAGE
import cv2
image_path = sys.argv[1]
image = cv2.imread(image_path)

## OBJECT DETECTION
cropped_image, nonempty = detector.bestBoxDetection(image)

if(nonempty):
    ## CLASSIFICATION
    import numpy as np
    cropped_tensor = np.ones(shape=(1,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
    cropped_tensor[0,:,:,:] =  classifier.preprocessImage(cropped_image)
    scores = classifier.predictOnBatch(cropped_tensor)
    print("Prediction :", txt_classes[LANG][np.argmax(scores[0,:])])
else:
    print("Prediction : vide/empty") 
        
