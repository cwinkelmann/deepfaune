############
############ OPECNV LOADING VERSION
images_data = []
import os
#image_path='/home/vmiele/Projects/deepfaune/code/gui/testdata/humain2.jpg'
for image_path in os.listdir("/home/vmiele/Projects/deepfaune/code/gui/testdata/"):
     original_image = cv2.imread(image_path)
     original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
     #When the image file is read with the OpenCV function imread(), the order of colors is BGR (blue, green, red). On the other hand, in Pillow, the order of colors is assumed to be RGB (red, green, blue).
     input_size=416
     image_data = cv2.resize(original_image, (input_size, input_size))
     image_data = image_data / 255.
     images_data.append(image_data)
     
images_data = np.asarray(images_data).astype(np.float32)


############
############ 
import numpy as np
import tensorflow as tf
saved_model_loaded = tf.saved_model.load("checkpoints/yolov4-tiny-416/")
infer = saved_model_loaded.signatures['serving_default']

import pandas as pd
from os import listdir
from os.path import join
testdir = "/home/vmiele/Projects/deepfaune/code/gui/orchamp/"
df_filename = pd.DataFrame({'filename':[join(testdir,filename) for filename in sorted(listdir(testdir))
                                        if filename.endswith(".jpg") or filename.endswith(".JPG")
                                        or filename.endswith(".jpeg") or filename.endswith(".JPEG")
                                        or filename.endswith(".bmp") or filename.endswith(".BMP")
                                        or filename.endswith(".tif") or filename.endswith(".TIF")
                                        or filename.endswith(".gif") or filename.endswith(".GIF")
                                        or filename.endswith(".png") or filename.endswith(".PNG")]})
     
import os
from os.path import join
import numpy as np
from PIL import Image
YOLO_SIZE=416
CROP_SIZE = (300, 300)
#images_data = np.empty(shape=(df_filename.shape[0],YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
#for k in range(df_filename.shape[0]):
images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
for k in [6]:
     #image_path = "/home/vmiele/Projects/deepfaune/code/gui/testdata/humain2.jpg"
     image_path = df_filename["filename"][k]
     original_image = Image.open(image_path)
     resized_image = original_image.resize((YOLO_SIZE, YOLO_SIZE))
     image_data = np.asarray(resized_image).astype(np.float32)
     image_data = image_data / 255. # PIL image is int8, this array is float32 and divided by 255
     images_data[0,:,:,:] = image_data 
     img = Image.fromarray((255*images_data[0,:,:,:]).astype(np.int8), 'RGB')
     img.show()


batch_data = tf.constant(images_data)
pred_bbox = infer(input_1=batch_data)

for key, value in pred_bbox.items():
     boxes = value[:, :, 0:4]
     pred_conf = value[:, :, 4:]

pconf = pred_conf.numpy()[0,:,:]
idxmax  = np.unravel_index(np.argmax(pconf), pconf.shape)
bestbox = boxes[0,idxmax[0],:].numpy()

import tf.image
BATCH_SIZE = 1
NUM_BOXES = 1 # boxes.numpy().shape[1]
box_indices = tf.random.uniform(shape=(NUM_BOXES,), minval=0, maxval=BATCH_SIZE, dtype=tf.int32)
output = tf.image.crop_and_resize(batch_data, boxes[0,idxmax[0]:(idxmax[0]+1),:], box_indices, CROP_SIZE)
output.shape

img = Image.fromarray((255*output[0].numpy()).astype(np.int8), 'RGB')
img.show()






#########################################################################
import cv2
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import pandas as pd
from os import listdir
from os.path import join
saved_model_loaded = tf.saved_model.load("checkpoints/yolov4-tiny-416/")

data_generator = ImageDataGenerator(preprocessing_function = preprocess_input)
testdir="//home/vmiele/Projects/deepfaune/code/gui/testdata/"
df_filename = pd.DataFrame({'filename':[join(testdir,filename) for filename in sorted(listdir(testdir))
                                        if filename.endswith(".jpg") or filename.endswith(".JPG")
                                        or filename.endswith(".jpeg") or filename.endswith(".JPEG")
                                        or filename.endswith(".bmp") or filename.endswith(".BMP")
                                        or filename.endswith(".tif") or filename.endswith(".TIF")
                                        or filename.endswith(".gif") or filename.endswith(".GIF")
                                        or filename.endswith(".png") or filename.endswith(".PNG")]})

test_generator = data_generator.flow_from_dataframe(
    df_filename,
    target_size=(416,416),
    batch_size=16,
    class_mode=None,
    shuffle=False
)
infer = saved_model_loaded.signatures['serving_default']
batch_data = tf.constant(next(iter(test_generator)))
pred_bbox = infer(batch_data[0,:,:,:].numpy())


for key, value in pred_bbox.items():
     boxes = value[:, :, 0:4]
     pred_conf = value[:, :, 4:]

from PIL import Image
df_filename.loc[1,"filename"]
img = Image.fromarray((255*images_data[0,:,:,:]).astype(np.int8), 'RGB')
img.show()
