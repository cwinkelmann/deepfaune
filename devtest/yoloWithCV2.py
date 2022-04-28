# Source: https://www.datacorner.fr/yolo-nms/ 

import cv2
import numpy as np

imgpath = input("Path to the image : ")
image = cv2.imread(imgpath)

model = '/home/echetouane/yolo/my-yolov4_old.weights'
config = '/home/echetouane/yolo/my-yolov4_old.cfg'
yolo_size = 608

classes = ["animal", "person", "vehicle"]
threshold = 0.25

# Little function to resize in keeping the format ratio
# Source: https://stackoverflow.com/questions/35180764/opencv-python-image-too-big-to-display
def ResizeWithAspectRatio(_image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    image = _image.copy()
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(image, dim, interpolation=inter)

np.random.seed(45)
BOX_COLORS = np.random.randint(0, 255, size=(len(classes), 3), dtype="uint8")

(h, w) = image.shape[:2]

# Load weights and construct graph
yolo = cv2.dnn.readNetFromDarknet(config, model)
yololayers = [yolo.getLayerNames()[i - 1] for i in yolo.getUnconnectedOutLayers()]
blobimage = cv2.dnn.blobFromImage(image, 1 / 255.0, (yolo_size, yolo_size), swapRB=True, crop=False)
yolo.setInput(blobimage)
layerOutputs = yolo.forward(yololayers)

boxes_detected = []
confidences_scores = []
labels_detected = []
 
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
    if confidence > threshold:
      # Bounding box
      box = detection[0:4] * np.array([w, h, w, h])
      (centerX, centerY, width, height) = box.astype("int")
 
      # Use the center (x, y)-coordinates to derive the top and left corner of the bounding box
      x = int(centerX - (width / 2))
      y = int(centerY - (height / 2))
 
      # update our result list (detection)
      boxes_detected.append([x, y, int(width), int(height)])
      confidences_scores.append(float(confidence))
      labels_detected.append(classID)

final_boxes = cv2.dnn.NMSBoxes(boxes_detected, confidences_scores, 0.25, 0.25)

image2 = image.copy()
# loop through the final set of detections remaining after NMS and draw bounding box and write text
for max_valueid in final_boxes:
    max_class_id = max_valueid
 
    # extract the bounding box coordinates
    (x, y) = (boxes_detected[max_class_id][0], boxes_detected[max_class_id][1])
    (w, h) = (boxes_detected[max_class_id][2], boxes_detected[max_class_id][3])
 
    # draw a bounding box rectangle and label on the image
    color = [int(c) for c in BOX_COLORS[labels_detected[max_class_id]]]
    cv2.rectangle(image2, (x, y), (x + w, y + h), color, 1)
     
    score = str(round(float(confidences_scores[max_class_id]) * 100, 1)) + "%"
    text = "{}: {}".format(classes[labels_detected[max_class_id]], score)
    cv2.putText(image2, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

cv2.imshow("Results", ResizeWithAspectRatio(image2, width=1024))
#cv2.imshow("Results", image2)

if (cv2.waitKey() >= 0):
    cv2.destroyAllWindows()
    
