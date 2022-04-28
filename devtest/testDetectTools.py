import sys
import os
curdir = os.path.abspath(os.path.dirname(sys.argv[0])) 
sys.path.append(curdir+'/../')

from detectTools import bestBoxDetection

import cv2
image = cv2.imread(curdir+"/chamois.jpg")
image = cv2.resize(image, (1200,800))
threshold = 0.25

croppedimage, nonempty = bestBoxDetection(image, threshold = 0.25)
print(nonempty)

CROP_SIZE=300
croppedimage2classifier = cv2.dnn.blobFromImage(croppedimage, 1/1.0, (CROP_SIZE, CROP_SIZE), swapRB=True, crop=False)
from tensorflow.keras.applications.efficientnet import preprocess_input
preprocess_input(croppedimage2classifier)

cv2.imshow('window', croppedimage)
cv2.waitKey(5000)
cv2.destroyAllWindows()
