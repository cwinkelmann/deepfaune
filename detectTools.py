# Copyright CNRS 2022

# simon.chamaille@cefe.cnrs.fr; vincent.miele@univ-lyon1.fr

# This software is a computer program whose purpose is to identify
# animal species in camera trap images.

#This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

####################################################################################
### LOADING YOLO
####################################################################################
import cv2
import numpy as np

YOLO_SIZE=608
model = 'deepfaune-yolov4.weights'
config = 'deepfaune-yolov4.cfg'

####################################################################################
### BEST BOX DETECTION 
####################################################################################
class Detector:
    
    def __init__(self):
        self.yolo = cv2.dnn.readNetFromDarknet(config, model)

    """
    :param image: image in BGR loaded by opencv
    :param threshold : above threshold, keep the best box given
    """
    def bestBoxDetection(self, image, threshold=0.5):
        '''
        in/out as numpy int array (0-255) in BGR
        '''
        height, width = image.shape[:2]
        # here resizing and scaling by 1./255 + swapBR since OpenCV uses BGR
        blobimage = cv2.dnn.blobFromImage(image, 1/255.0, (YOLO_SIZE, YOLO_SIZE), swapRB=True, crop=False)
        self.yolo.setInput(blobimage)
        yololayers = [self.yolo.getLayerNames()[i - 1] for i in self.yolo.getUnconnectedOutLayers()]
        layerOutputs = self.yolo.forward(yololayers)
        boxes_detected = []
        confidences_scores = []
        for output in layerOutputs:
            # Looping over each of the detections
            for detection in output:
                scores = detection[5:]
                boxclass = np.argmax(scores)
                confidence = scores[boxclass]
                if confidence > threshold:
                    # Bounding box in [0,1]x[0,1]
                    (boxcenterx, boxcentery, boxwidth, boxheight) = detection[0:4]
                    # Use the center (x, y)-coordinates to derive the top and left corner of the bounding box
                    cornerx = (boxcenterx - (boxwidth / 2))
                    cornery = (boxcentery - (boxheight / 2))
                    boxes_detected.append([cornerx, cornery, boxwidth, boxheight])
                    confidences_scores.append(float(confidence))
                    # Removing overlap and duplicates
        final_boxes = cv2.dnn.NMSBoxes(boxes_detected, confidences_scores, threshold, threshold)
        if len(final_boxes):
            # Focus on the most confident bounding box
            kbox = final_boxes[0]
            (cornerx, cornery) = (boxes_detected[kbox][0], boxes_detected[kbox][1])        
            (boxwidth, boxheight) = (boxes_detected[kbox][2], boxes_detected[kbox][3])
            # Back to image dimension in pixels
            cornerx = np.around(cornerx*width).astype("int")
            boxwidth = np.around(boxwidth*width).astype("int")
            cornery = np.around(cornery*height).astype("int")
            boxheight = np.around(boxheight*height).astype("int")
            #print((cornerx, cornery),(cornerx+boxwidth, cornery+boxheight))
            croppedimage = image[max(0,cornery):min(height,cornery+boxheight),
                                 max(0,cornerx):min(width,cornerx+boxwidth)]
            return croppedimage, True
        return [], False


####################################################################################
### BEST BOX DETECTION WITH JSON
####################################################################################

from load_api_results import load_api_results
import contextlib
import os
from pandas import concat
from numpy import argmax

class DetectorJSON:
    
    """
    We assume JSON categories are 1=animal, 2=person, 3=vehicle and the empty category 0=empty

    :param jsonfilename: JSON file containing the bondoing boxes coordinates, such as generated by megadetectorv5
    :param threshold : above threshold, keep the best box
    """
    def __init__(self, jsonfilename, threshold=0.5):
        # getting results in a dataframe
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            self.df_json, _ = load_api_results(jsonfilename)
            # removing lines with Failure event
            if 'failure' in self.df_json.keys():
                self.df_json = self.df_json[self.df_json['failure'].isnull()]
                self.df_json.reset_index(drop=True, inplace = True)
                self.df_json.drop('failure', axis=1, inplace=True)
        self.threshold = threshold
        self.k = 0 # current image index
        self.kbox = 0 # current box index

    def nextBestBoxDetection(self):
        if len(self.df_json['detections'][self.k]): # is non empty
            # Focus on the most confident bounding box coordinates
            self.kbox = argmax([box['conf'] for box in self.df_json['detections'][self.k]])
            if self.df_json['detections'][self.k][self.kbox]['conf']>self.threshold:
                category = int(self.df_json['detections'][self.k][self.kbox]['category'])
            else:
                category = 0
        else: # is empty
            category = 0
        # is an animal detected ?
        if category != 1:
            croppedimage = []
        # if yes, cropping the bounding box
        else:
            croppedimage = self.cropBox()
        # goto next image
        self.k += 1
        return croppedimage, category

    def nextBoxDetection(self):
        if self.k >= len(self.df_json):
            raise IndexError # no next box
        # is an animal detected ?
        if len(self.df_json['detections'][self.k]):
            # is box above threshold ?
            if self.df_json['detections'][self.k][self.kbox]['conf']>self.threshold:
                category = int(self.df_json['detections'][self.k][self.kbox]['category'])
                croppedimage = self.cropBox()
            else: # considered as empty
                category = 0
                croppedimage = []
            self.kbox += 1
            if self.kbox >= len(self.df_json['detections'][self.k]):
                self.k += 1
                self.kbox = 0
        else: # is empty
            category = 0
            croppedimage = []
            self.k += 1
            self.kbox = 0
        return croppedimage, category
          
    def cropBox(self):
        image_path = str(self.df_json["file"][self.k])
        image = cv2.imread(image_path)
        if image is None:
            return []
        bbox_norm = self.df_json['detections'][self.k][self.kbox]["bbox"]
        img_h, img_w = image.shape[:2]
        xmin = int(bbox_norm[0] * img_w)
        ymin = int(bbox_norm[1] * img_h)
        box_w = int(bbox_norm[2] * img_w)
        box_h = int(bbox_norm[3] * img_h)
        box_size = max(box_w, box_h)
        xmin = max(0, min(xmin - int((box_size - box_w) / 2),img_w - box_w))
        ymin = max(0, min(ymin - int((box_size - box_h) / 2),img_h - box_h))
        box_w = min(img_w, box_size)
        box_h = min(img_h, box_size)
        croppedimage = image[max(0,ymin):min(img_h,ymin + box_h),
                             max(0,xmin):min(img_w,xmin + box_w)]
        return croppedimage
        
    def getNbFiles(self):
        return self.df_json.shape[0]
    
    def getFilenames(self):
        return list(self.df_json["file"].to_numpy())
    
    def getCurrentFilename(self):
        if self.k >= len(self.df_json):
            raise IndexError
        return self.df_json['file'][self.k]
    
    def resetDetection(self):
        self.k = 0
        self.kbox = 0
    
    def merge(self, detector):
        self.df_json = concat([self.df_json, detector.df_json], ignore_index=True)
        self.resetDetection()
