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
            
    def bestBoxDetection(self, image, threshold=0.25):
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
            # Extract the most confident bounding box coordinates
            best_box = final_boxes[0]
            (cornerx, cornery) = (boxes_detected[best_box][0], boxes_detected[best_box][1])        
            (boxwidth, boxheight) = (boxes_detected[best_box][2], boxes_detected[best_box][3])
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

import json
import os
from typing import Dict, Mapping, Optional, Tuple

import pandas as pd

# Source : https://github.com/microsoft/CameraTraps/blob/main/api/batch_processing/postprocessing/load_api_results.py

def load_api_results(api_output_path: str, normalize_paths: bool = True,
                     filename_replacements: Optional[Mapping[str, str]] = None
                     ) -> Tuple[pd.DataFrame, Dict]:
    """
    Loads the json formatted results from the batch processing API to a
    Pandas DataFrame, mainly useful for various postprocessing functions.
    Args:
        api_output_path: path to the API output json file
        normalize_paths: whether to apply os.path.normpath to the 'file' field
            in each image entry in the output file
        filename_replacements: replace some path tokens to match local paths to
            the original blob structure
    Returns:
        detection_results: pd.DataFrame, contains at least the columns:
                ['file', 'max_detection_conf', 'detections','failure']            
        other_fields: a dict containing fields in the dict
    """
    #print('Loading API results from {}'.format(api_output_path))

    with open(api_output_path) as f:
        detection_results = json.load(f)

    #print('De-serializing API results')

    # Sanity-check that this is really a detector output file
    for s in ['info', 'detection_categories', 'images']:
        assert s in detection_results, 'Missing field {} in detection results'.format(s)

    # Fields in the API output json other than 'images'
    other_fields = {}
    for k, v in detection_results.items():
        if k != 'images':
            other_fields[k] = v

    # Normalize paths to simplify comparisons later
    if normalize_paths:
        for image in detection_results['images']:
            image['file'] = os.path.normpath(image['file'])
            # image['file'] = image['file'].replace('\\','/')

    # Pack the json output into a Pandas DataFrame
    detection_results = pd.DataFrame(detection_results['images'])

    # Replace some path tokens to match local paths to original blob structure
    # string_to_replace = list(filename_replacements.keys())[0]
    if filename_replacements is not None:
        for string_to_replace in filename_replacements:

            replacement_string = filename_replacements[string_to_replace]

            for i_row in range(len(detection_results)):
                row = detection_results.iloc[i_row]
                fn = row['file']
                fn = fn.replace(string_to_replace, replacement_string)
                detection_results.at[i_row, 'file'] = fn

    #print('Finished loading and de-serializing API results for {} images from {}'.format(
            #len(detection_results),api_output_path))

    return detection_results, other_fields

class DetectorJSON:
    
    def __init__(self, jsonfilename):
        # getting results in a dataframe
        self.df_json, df_notUsed = load_api_results(jsonfilename)
        self.k = 0
        
    def nextBestBoxDetection(self):
        image_path = str(self.df_json["file"][self.k])
        image = cv2.imread(image_path)
        if image is None:
            return [], False
        try: 
            bbox_norm = self.df_json['detections'][self.k][0]["bbox"]
        except:
            bbox_norm = []    
        self.k += 1
        if bbox_norm != []:
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
            return croppedimage, True
        else:
            return [], False
        
