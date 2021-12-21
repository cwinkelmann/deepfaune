import tensorflow as tf
saved_model_loaded = tf.saved_model.load("checkpoints/yolov4-608/")
infer = saved_model_loaded.signatures['serving_default']
YOLO_SIZE=608
CROP_SIZE=300
BATCH_SIZE=16

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
     
import numpy as np
from PIL import Image
cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
#for k in range(df_filename.shape[0]):
idxnonempty = []
for k in range(BATCH_SIZE):
     ## LOADING image and convert ton float 32 numpy array
     image_path = df_filename["filename"][k]
     original_image = Image.open(image_path)
     resized_image = original_image.resize((YOLO_SIZE, YOLO_SIZE))
     image_data = np.asarray(resized_image).astype(np.float32)
     image_data = image_data / 255. # PIL image is int8, this array is float32 and divided by 255
     images_data[0,:,:,:] = image_data 
     #img = Image.fromarray((255*images_data[0,:,:,:]).astype(np.int8), 'RGB')
     #img.show()
     ## INFERING boxes and retain the most confident one (if it exists)
     batch_data = tf.constant(images_data)
     pred_bbox = infer(input_1=batch_data)
     for key, value in pred_bbox.items():
          boxes = value[:, :, 0:4]
          pred_conf = value[:, :, 4:]
     if boxes.shape[1]==0:
          pass # EMPTY
     else:
          idxnonempty.append(k)
          idxmax  = np.unravel_index(np.argmax(pred_conf.numpy()[0,:,:]), pred_conf.shape[1:])
          bestbox = boxes[0,idxmax[0],:].numpy()
          ## CROPPING a single box
          NUM_BOXES = 1 # boxes.numpy().shape[1]
          box_indices = tf.random.uniform(shape=(NUM_BOXES,), minval=0, maxval=1, dtype=tf.int32)
          output = tf.image.crop_and_resize(batch_data, boxes[0,idxmax[0]:(idxmax[0]+1),:], box_indices, (CROP_SIZE,CROP_SIZE))
          output.shape
          #img = Image.fromarray((255*output[0].numpy()).astype(np.int8), 'RGB')
          #img.show()
          cropped_data[k,:,:,:] = output[0].numpy()

if len(idxnonempty):
      cropped_data[idxnonempty,:,:,:]




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
