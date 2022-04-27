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
import tensorflow as tf
import numpy as np

savedmodel = "checkpoints/yolov4-608/"
saved_model_loaded = tf.saved_model.load(savedmodel)
infer = saved_model_loaded.signatures['serving_default']


def detecting(batch_data, CROP_SIZE):
    ## INFERING boxes and retain the most confident one (if it exists)
    pred_bbox = infer(input_1=batch_data) # dans yolo
    for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]
    if boxes.shape[1]>0: # not empty
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=5,
            max_total_size=5,
            iou_threshold=0.45,
            score_threshold=0.25
        )
        idxmax  = np.unravel_index(np.argmax(scores.numpy()[0,:]), scores.shape[1])
        ## CROPPING a single box
        NUM_BOXES = 1 # boxes.numpy().shape[1]
        box_indices = tf.random.uniform(shape=(NUM_BOXES,), minval=0, maxval=1, dtype=tf.int32)
        output = tf.image.crop_and_resize(batch_data, boxes[0,idxmax[0]:(idxmax[0]+1),:], box_indices, (CROP_SIZE, CROP_SIZE))
        output.shape
        return output, True
    return [], False


import cv2
model = '/home/vmiele/Developpement/deepfaunegui-modular/my-yolov4_last.weights'
config = '/home/vmiele/Developpement/deepfaunegui-modular/my-yolov4.cfg'
yolo = cv2.dnn.readNetFromDarknet(config, model)
yololayers = [yolo.getLayerNames()[i - 1] for i in yolo.getUnconnectedOutLayers()]
#classes = ["animal", "person", "vehicle"]


def detecting2(blobimage, threshold = 0.25):
    yolo.setInput(blobimage)
    layerOutputs = yolo.forward(yololayers)
    boxes_detected = []
    confidences_scores = []
    #labels_detected = []
    probability_index=5
    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
     
            # Take only predictions with confidence more than CONFIDENCE_MIN thresold
            threshold = 0.25
            if confidence > threshold:
                # Bounding box
                box = detection[0:4] # * np.array([w, h, w, h]) ## UTILE ???? ENSUITE ON A BESOIN D'ENTRE 0 et 1 ???
                (centerX, centerY, width, height) = box#.astype("int")
                # Use the center (x, y)-coordinates to derive the top and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our result list (detection)
                boxes_detected.append([x, y, int(width), int(height)])
                confidences_scores.append(float(confidence))
                #labels_detected.append(classID)
    final_boxes = cv2.dnn.NMSBoxes(boxes_detected, confidences_scores, 0.25, 0.25)
    if final_boxes.size>0:
        # extract the most confident bounding box coordinates
        max_class_id = final_boxes[0]
        (x, y) = (boxes_detected[max_class_id][0], boxes_detected[max_class_id][1])
        (w, h) = (boxes_detected[max_class_id][2], boxes_detected[max_class_id][3])
        ## CROPPING a single box
        NUM_BOXES = 1 # boxes.numpy().shape[1]
        box_indices = tf.random.uniform(shape=(NUM_BOXES,), minval=0, maxval=1, dtype=tf.int32)
        output = tf.image.crop_and_resize(batch_data, XXXXXX, box_indices, (CROP_SIZE, CROP_SIZE))
        return output, True
    return [], False
