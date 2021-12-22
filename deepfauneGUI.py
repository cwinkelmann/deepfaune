import PySimpleGUI as sg
### SETTINGS
sg.ChangeLookAndFeel('Reddit')
#sg.ChangeLookAndFeel('Dark2')
#sg.ChangeLookAndFeel('DarkBlue1')
#sg.ChangeLookAndFeel('DarkGrey1')


DEBUG = False
backbone = "efficientnet"
BATCH_SIZE = 8
workers = 1
hdf5 = "efficientnet_MDcheckOnlycroppedImgAug.hdf5"
classes = ["blaireau","bouquetin","cerf","chamois","chevreuil","chien","ecureuil","felinae","humain","lagomorphe","loup","micromammifere","mouflon","mouton","mustelide","oiseau","renard","sanglier","vache","vehicule"]
classesempty = classes + ["vide"]

YOLO_SIZE=608
CROP_SIZE=300
savedmodel = "checkpoints/yolov4-608/"

### GUI WINDOW
prediction = [[],[]]
threshold = threshold_default = 0.5
left_col = [
     [sg.Image(filename=r'img/cameratrap-nb.png'),sg.Image(filename=r'img/logoINEE.png')],
     [sg.Text("DEEPFAUNE GUI",size=(17,1), font=("Helvetica", 35))],[sg.Text("\n\n\n")],
     [sg.Text('Image folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
     #[sg.Spin([i for i in range(1,11)], initial_value=10, k='-SPIN-'), sg.Text('Spin')],
     [sg.Text('Confidence\t'), sg.Slider(range=(25,99), default_value=threshold_default*100, orientation='h', size=(12,10), change_submits=True, key='-THRESHOLD-')],
     [sg.Text('Progress bar'), sg.ProgressBar(1, orientation='h', size=(20, 2), border_width=4, key='-PROGBAR-',bar_color=['Blue','White'])],
     [sg.Button('Run', key='-RUN-'), sg.Button('Save in CSV', key='-SAVECSV-'), sg.Button('Save in XSLX', key='-SAVEXLSX-')],
     [sg.Button('Create separate folders', key='-SUBFOLDERS-'), sg.Radio('Copy files', 1, key='-CP-', default=True),sg.Radio('Move files', 1, key='-MV-')]
]
right_col=[
     [sg.Multiline(size=(60, 10), default_text='Loading model parameters... ', write_only=True, key="-ML_KEY-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
     [sg.Table(values=prediction, headings=['filename','prediction'], justification = "c", 
               vertical_scroll_only=False, auto_size_columns=False, col_widths=[30, 17], num_rows=BATCH_SIZE, 
               enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
               key='-TABRESULTS-')],      
     [sg.Button('Show all images', key='-ALLTABROW-'),sg.Button('Show selected image', key='-TABROW-')]
]
layout = [[sg.Column(left_col, element_justification='l' ),
           sg.Column(right_col, element_justification='l')]] 
window = sg.Window("DeepFaune GUI",layout).Finalize()
window['-SAVECSV-'].Update(disabled=True)
window['-SAVEXLSX-'].Update(disabled=True)
window['-TABROW-'].Update(disabled=True)
window['-ALLTABROW-'].Update(disabled=True)
window['-SUBFOLDERS-'].Update(disabled=True)
window['-CP-'].Update(disabled=True)
window['-MV-'].Update(disabled=True)


### LOADING CLASSIFIER
import tensorflow as tf
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D,Activation
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import numpy as np
import pandas as pd
from os import listdir
from os.path import join, basename
import pkgutil
import io
nbclasses=len(classes)
if backbone == "resnet":
     from tensorflow.keras.applications.resnet_v2 import ResNet50V2
     from tensorflow.keras.applications.resnet_v2 import preprocess_input, decode_predictions
     base_model = ResNet50V2(include_top=False, weights=None, input_shape=(300,300,3))
elif backbone == "efficientnet":
     from tensorflow.keras.applications.efficientnet import EfficientNetB2
     ##from tensorflow.keras.applications.efficientnet import EfficientNetB4
     from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
     base_model = EfficientNetB2(include_top=False, weights=None, input_shape=(300,300,3))
     ##base_model = EfficientNetB4(include_top=False, weights=None, input_shape=(380,380,3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
#x = Dense(512)(x) #256,1024, etc. may work as well
x = Dense(nbclasses)(x) #number of classes
preds = Activation("softmax")(x)
model = Model(inputs=base_model.input,outputs=preds)
model.load_weights(hdf5)

### LOADING YOLO 
saved_model_loaded = tf.saved_model.load(savedmodel)
infer = saved_model_loaded.signatures['serving_default']

### PREDICTION TOOL
def prediction2class(prediction, threshold):
     class_pred = ['undefined' for i in range(len(prediction))] 
     for i in range(len(prediction)):
          pred = prediction[i]
          if(max(pred)>=threshold):
               class_pred[i] = classesempty[np.argmax(pred)]
     return(class_pred)

### PREDICTION & GUI ACTIONS
testdir = ""
rowidx = [-1]
print("done")
while True:
     event, values = window.read(timeout=10)
     if event in (sg.WIN_CLOSED, 'Exit'):
          break
     elif event == '-FOLDER-':
          testdir = values['-FOLDER-']
          print("Selected folder:", testdir)
          print("Warning: no recursive search")
          ### GENERATOR
          df_filename = pd.DataFrame({'filename':[join(testdir,filename) for filename in sorted(listdir(testdir))
                                                  if filename.endswith(".jpg") or filename.endswith(".JPG")
                                                  or filename.endswith(".jpeg") or filename.endswith(".JPEG")
                                                  or filename.endswith(".bmp") or filename.endswith(".BMP")
                                                  or filename.endswith(".tif") or filename.endswith(".TIF")
                                                  or filename.endswith(".gif") or filename.endswith(".GIF")
                                                  or filename.endswith(".png") or filename.endswith(".PNG")]})
          nbfiles = df_filename.shape[0]
          print("Number of images:", nbfiles)
     elif event == '-THRESHOLD-':
          threshold = values['-THRESHOLD-']/100.
     elif event == '-RUN-':
          sg.cprint('Running....', c='white on green', end='')
          sg.cprint('')
          ### PREDICTING
          prediction = np.zeros(shape=(nbfiles,nbclasses+1), dtype=np.float32)
          prediction[:,nbclasses] = 1 # by default, predicted as empty
          k1 = 0
          k2 = min(k1+BATCH_SIZE,nbfiles)
          batch = 1
          images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
          while(k1<nbfiles):
               cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
               idxnonempty = []
               for k in range(k1,k2):
                    ## LOADING image and convert ton float 32 numpy array
                    image_path = df_filename["filename"][k]
                    try:
                         original_image = Image.open(image_path)
                         original_image.getdata()[0]
                    except OSError:
                         break
                    else:
                         resized_image = original_image.resize((YOLO_SIZE, YOLO_SIZE))
                         image_data = np.asarray(resized_image).astype(np.float32)
                         image_data = image_data / 255. # PIL image is int8, this array is float32 and divided by 255
                         images_data[0,:,:,:] = image_data
                         ## INFERING boxes and retain the most confident one (if it exists)
                         batch_data = tf.constant(images_data)
                         pred_bbox = infer(input_1=batch_data)
                         for key, value in pred_bbox.items():
                              boxes = value[:, :, 0:4]
                              pred_conf = value[:, :, 4:]
                         if boxes.shape[1]>0: # not empty
                              idxnonempty.append(k)
                              idxmax  = np.unravel_index(np.argmax(pred_conf.numpy()[0,:,:]), pred_conf.shape[1:])
                              bestbox = boxes[0,idxmax[0],:].numpy()
                              ## CROPPING a single box
                              NUM_BOXES = 1 # boxes.numpy().shape[1]
                              box_indices = tf.random.uniform(shape=(NUM_BOXES,), minval=0, maxval=1, dtype=tf.int32)
                              output = tf.image.crop_and_resize(batch_data, boxes[0,idxmax[0]:(idxmax[0]+1),:], box_indices, (CROP_SIZE,CROP_SIZE))
                              output.shape
                              cropped_data[k-k1,:,:,:] = preprocess_input(output[0].numpy()*255)
               if len(idxnonempty):
                    prediction[idxnonempty,0:nbclasses] = model.predict(cropped_data[[idx-k1 for idx in idxnonempty],:,:,:], workers=workers)
                    prediction[idxnonempty,nbclasses] = 0 # not empty
               ## Update
               window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)
               print("Processing batch of images",batch,": done", flush=True)
               window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"][k1:k2]],
                                                                   prediction2class(prediction[k1:k2,],threshold)].tolist())
               k1 = k2
               k2 = min(k1+BATCH_SIZE,nbfiles)
               batch = batch+1
          if DEBUG:
               pdprediction = pd.DataFrame(prediction)
               pdprediction.columns = classesempty
               pdprediction.index = df_filename["filename"]
               from tempfile import mkstemp
               tmpcsv = mkstemp(suffix=".csv",prefix="deepfauneGUI")[1]
               print("DEBUG: saving scores to",tmpcsv)
               pdprediction.to_csv(tmpcsv, float_format='%.2g')
          predictedclass = prediction2class(prediction,threshold)         
          window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass].tolist())
          window['-SAVECSV-'].Update(disabled=False)
          if pkgutil.find_loader("openpyxl") is not None:
               import openpyxl
               window['-SAVEXLSX-'].Update(disabled=False)
          window['-ALLTABROW-'].Update(disabled=False)
     elif event == '-SAVECSV-':
          preddf  = pd.DataFrame({'filename':df_filename["filename"], 'prediction':predictedclass})
          confirm = sg.popup_yes_no("Do you want to save predictions in "+join(testdir,"deepfaune.csv")+"?", keep_on_top=True)
          if confirm:
               print("Saving to",join(testdir,"deepfaune.csv"))
               preddf.to_csv(join(testdir,"deepfaune.csv"), index=False)
     elif event == '-SAVEXLSX-':
          preddf  = pd.DataFrame({'filename':df_filename["filename"], 'prediction':predictedclass})
          confirm = sg.popup_yes_no("Do you want to save predictions in "+join(testdir,"deepfaune.xslx")+"?", keep_on_top=True)
          if confirm:
               print("Saving to",join(testdir,"deepfaune.xlsx"))
               preddf.to_excel(join(testdir,"deepfaune.xlsx"), index=False)
     elif event == '-TABRESULTS-':
          rowidx = values['-TABRESULTS-']
          if len(rowidx)==0:
               window['-TABROW-'].Update(disabled=True)
          else:
               window['-TABROW-'].Update(disabled=False) 
     elif event == '-ALLTABROW-' or event == '-TABROW-':
          if event == '-TABROW-' and rowidx[0]>=0:
               curridx = rowidx[0]
          else:
               curridx = 0
               window['-TABROW-'].Update(disabled=True)
          ### SHOWING IMAGE
          window['-ALLTABROW-'].Update(disabled=True)
          window['-SAVECSV-'].Update(disabled=True)
          window['-SAVEXLSX-'].Update(disabled=True)
          layout = [[sg.Image(key="-IMAGE-")],
                    [sg.Text('Prediction:', size=(15, 1)),sg.InputText(predictedclass[curridx], key="-CORRECTION-")],
                    [sg.Button('Save', key='-SAVE-'),sg.Button('Close', key='-CLOSE-'),
                     sg.Button('Previous', key='-PREVIOUS-'),
                     sg.Button('Next', bind_return_key=True, key='-NEXT-'),
                     sg.Checkbox('Only undefined', default=False, key="-ONLYUNDEFINED-")]]
          windowimg = sg.Window(basename(df_filename['filename'][curridx]), layout, finalize=True)
          image = Image.open(df_filename['filename'][curridx])
          image = image.resize((350,300))
          bio = io.BytesIO()
          image.save(bio, format="PNG")
          windowimg["-IMAGE-"].update(data=bio.getvalue())
          ### CORRECTING PREDICTION
          while True:
               eventimg, valuesimg = windowimg.read()
               if eventimg in (sg.WIN_CLOSED, '-CLOSE-'):
                    break
               elif eventimg == '-SAVE-':
                    predictedclass[curridx] = valuesimg["-CORRECTION-"]
                    window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass].tolist())
                    window['-TABROW-'].Update(disabled=True)
               elif eventimg == '-PREVIOUS-' or eventimg == '-NEXT-': # button will save and show next image, return_key as well
                    predictedclass[curridx] = valuesimg["-CORRECTION-"]
                    window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass].tolist())
                    window['-TABROW-'].Update(disabled=True)
                    curridxinit = curridx
                    if eventimg == '-PREVIOUS-':
                         curridx = curridx-1
                         if curridx==-1:
                              curridx = len(predictedclass)-1
                         if valuesimg['-ONLYUNDEFINED-']: # search for the previous undefined image, if it exists
                              while predictedclass[curridx]!="undefined" and curridx!=curridxinit:
                                   curridx = curridx-1
                                   if curridx==-1:
                                        curridx = len(predictedclass)-1
                    else: # eventimg == '-NEXT-'
                         curridx = curridx+1
                         if curridx==len(predictedclass):
                              curridx = 0
                         if valuesimg['-ONLYUNDEFINED-']: # search for the next undefined image, if it exists
                              while predictedclass[curridx]!="undefined" and curridx!=curridxinit:
                                   curridx = curridx+1
                                   if curridx==len(predictedclass):
                                        curridx = 0
                    image = Image.open(df_filename['filename'][curridx])
                    #image.thumbnail((400, 400))
                    image = image.resize((350,300))
                    bio = io.BytesIO()
                    image.save(bio, format="PNG")
                    windowimg["-IMAGE-"].update(data=bio.getvalue())
                    windowimg.TKroot.title(basename(df_filename['filename'][curridx]))
                    windowimg["-CORRECTION-"].Update(predictedclass[curridx])
          windowimg.close()
          window['-SAVECSV-'].Update(disabled=False)
          window['-SAVEXLSX-'].Update(disabled=False)
          window['-ALLTABROW-'].Update(disabled=False)
     elif event == sg.TIMEOUT_KEY:
          window.refresh()
     else:
          window['-TABROW-'].Update(disabled=True)
               
               
               
window.close()  



     
