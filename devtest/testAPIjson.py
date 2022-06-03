import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from detectTools import DetectorJSON
from classifTools import Classifier, CROP_SIZE, txt_classes
LANG = 'fr' # or 'gb'
detector = DetectorJSON(sys.argv[1])
classifier = Classifier()

## OBJECT DETECTION
cropped_image, nonempty = detector.nextBestBoxDetection()

if(nonempty):
    ## CLASSIFICATION
    import numpy as np
    cropped_tensor = np.ones(shape=(1,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
    cropped_tensor[0,:,:,:] =  classifier.preprocessImage(cropped_image)
    scores = classifier.predictOnBatch(cropped_tensor)
    print("Prediction :", txt_classes[LANG][np.argmax(scores[0,:])])
else:
    print("Prediction : vide/empty") 
