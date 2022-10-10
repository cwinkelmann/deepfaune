import sys
import os

import torch

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

#######################
#######################
import cv2
image = cv2.imread('testdata/cerf_neige.jpg')
#image = cv2.resize(image, (1200,800))
threshold = 0.25
croppedimage = image

#######################
#######################
from detectTools import Detector
detector = Detector()
croppedimage, nonempty = detector.bestBoxDetection(image, 0.25)
croppedimage = np.asarray(croppedimage) # from PIL to cv2
print(category)

#######################
#######################
from cv2 import resize
CROP_SIZE=300
cv2.imshow('window', resize(croppedimage, (CROP_SIZE,CROP_SIZE)))
k = cv2.waitKey(0)
if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()

    
#######################
#######################
from classifTools import Classifier, CROP_SIZE
classifier = Classifier()
cropped_data = torch.ones((1,3,CROP_SIZE,CROP_SIZE), dtype=torch.float32)
cropped_data[0,:,:,:] = classifier.preprocessImage(croppedimage)
pred = classifier.predictOnBatch(cropped_data)
(pred*100).astype("int")


