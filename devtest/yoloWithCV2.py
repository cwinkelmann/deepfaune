import cv2

img = input("Path to the image : ")

model = '/home/echetouane/yolo/my-yolov4_old.weights'
config = '/home/echetouane/yolo/my-yolov4_old.cfg'
yolo_size = 608

classes = ["animal", "person", "vehicle"]
threshold = 0.25

# Load weights and construct graph
net = cv2.dnn.readNetFromDarknet(config, model)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

winName = 'Running YOLO Model'
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)

# Read input image
frame = cv2.imread(img)

# Get width and height
height,width,ch=frame.shape

# Create a 4D blob from a frame.
blob = cv2.dnn.blobFromImage(frame, 1.0/255.0, (yolo_size, yolo_size), True, crop=False)
net.setInput(blob)

# Run the preprocessed input blog through the network
predictions = net.forward()
probability_index=5

for i in range(predictions.shape[0]):
    prob_arr=predictions[i][probability_index:]
    class_index=prob_arr.argmax(axis=0)
    confidence= prob_arr[class_index]
    if confidence > threshold:
        x_center=predictions[i][0]*width
        y_center=predictions[i][1]*height
        width_box=predictions[i][2]*width
        height_box=predictions[i][3]*height
     
        x1=int(x_center-width_box * 0.5)
        y1=int(y_center-height_box * 0.5)
        x2=int(x_center+width_box * 0.5)
        y2=int(y_center+height_box * 0.5)
     
        cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),1)
        cv2.putText(frame,classes[class_index]+" "+"{0:.1f}".format(confidence),(x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
        # cv2.imwrite("out_"+args.input, frame)
        
cv2.imshow(winName, frame)

if (cv2.waitKey() >= 0):
    cv2.destroyAllWindows()
