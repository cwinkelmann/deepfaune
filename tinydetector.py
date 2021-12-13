import tensorflow as tf
saved_model_loaded = tf.saved_model.load("checkpoints/yolov4-tiny-416/")

image_path='/home/vmiele/Projects/deepfaune/code/gui/testdata/humain2.jpg'
original_image = cv2.imread(image_path)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
input_size=416
image_data = cv2.resize(original_image, (input_size, input_size))
image_data = image_data / 255.
images_data = []
for i in range(1):
     images_data.append(image_data)
import numpy as np
images_data = np.asarray(images_data).astype(np.float32)
infer = saved_model_loaded.signatures['serving_default']
batch_data = tf.constant(images_data)
pred_bbox = infer(batch_data)

for key, value in pred_bbox.items():
     boxes = value[:, :, 0:4]
     pred_conf = value[:, :, 4:] # con


     
import tensorflow as tf
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
pred_bbox = infer(batch_data[1:1,:,:,:])

saved_model_loaded = tf.keras.models.load_model("checkpoints/yolov4-tiny-416/")
saved_model_loaded.predict(batch_data)
