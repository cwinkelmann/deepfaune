import PySimpleGUI as sg
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D,Activation
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import pandas as pd
from os import listdir
from os.path import join, basename
import pkgutil
from PIL import Image
import io


### SETTINGS
#sg.ChangeLookAndFeel('Reddit')
#sg.ChangeLookAndFeel('Dark2')
#sg.ChangeLookAndFeel('DarkBlue1')
sg.ChangeLookAndFeel('DarkGrey1')

backbone = "efficientnet"
batch_size = 16
workers = 1
hdf5 = "efficientnet11spVide.hdf5"
classes = ["blaireau","cerf","chamois","chevreuil","chien","ecureuil","lagomorphe","loup","mustelide","renard","sanglier","vide"]

### GUI WINDOW
prediction = [[],[]]
threshold = threshold_default = 0.99
left_col = [
     [sg.Image(filename=r'cameratrap-nb.png'),sg.Image(filename=r'logoINEE.png')],
     [sg.Text("DEEPFAUNE GUI",size=(17,1), font=("Helvetica", 35))],
     [sg.Text('Image folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
     #[sg.Spin([i for i in range(1,11)], initial_value=10, k='-SPIN-'), sg.Text('Spin')],
     [sg.Text('Threshold\t'), sg.Slider(range=(50,100), default_value=threshold_default*100, orientation='h', size=(12,10), change_submits=True, key='-THRESHOLD-')],
     [sg.Text('Progress bar'), sg.ProgressBar(1, orientation='h', size=(20, 2), border_width=4, key='-PROGBAR-',bar_color=['Blue','White'])],
     [sg.Button('Run', key='-RUN-'), sg.Button('Save in CSV', key='-SAVECSV-'), sg.Button('Save in XSLX', key='-SAVEXLSX-')]
]
right_col=[
     [sg.Multiline(size=(60, 10), write_only=True, key="-ML_KEY-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
     [sg.Table(values=prediction, headings=['filename','prediction'], justification = "c", 
               vertical_scroll_only=False, auto_size_columns=False, col_widths=[30, 17], 
               enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
               key='-TABRESULTS-')],      
     [sg.Button('Show selected image', key='-TABROW-')]
]
layout = [[sg.Column(left_col, element_justification='l' ),
           sg.Column(right_col, element_justification='l')]] 
window = sg.Window("DeepFaune predition",layout).Finalize()
window['-SAVECSV-'].Update(disabled=True)
window['-SAVEXLSX-'].Update(disabled=True)
window['-TABROW-'].Update(disabled=True)


### LOADING MODEL 
nbclasses=len(classes)
labels=["daisy","iris","tulip"]
if backbone == "resnet":
     from tensorflow.keras.applications.resnet_v2 import ResNet50V2
     from tensorflow.keras.applications.resnet_v2 import preprocess_input, decode_predictions
     base_model = ResNet50V2(include_top=False, weights=None, input_shape=(300,300,3))
elif backbone == "efficientnet":
     from tensorflow.keras.applications.efficientnet import EfficientNetB2
     from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
     base_model = EfficientNetB2(include_top=False, weights=None, input_shape=(300,300,3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
#x = Dense(512)(x) #256,1024, etc. may work as well
x = Dense(nbclasses)(x) #number of classes
preds = Activation("softmax")(x)
model = Model(inputs=base_model.input,outputs=preds)
model.load_weights(hdf5)

### PREDICTION TOOL
def prediction2class(prediction, threshold):
     class_pred = ['undefined' for i in range(len(prediction))] 
     for i in range(len(prediction)):
          pred = prediction[i]
          if(max(pred)>=threshold):
               class_pred[i] = classes[np.argmax(pred)]
     return(class_pred)

### PREDICTION & GUI ACTIONS
testdir = ""
rowidx = [-1]
while True:
     event, values = window.read()
     if event in (sg.WIN_CLOSED, 'Exit'):
          break
     elif event == '-FOLDER-':
          testdir = values['-FOLDER-']
          print(testdir)
          ### GENERATOR
          df_filename = pd.DataFrame({'filename':[join(testdir,filename) for filename in listdir(testdir)]})
          data_generator = ImageDataGenerator(preprocessing_function = preprocess_input)
          test_generator = data_generator.flow_from_dataframe(
               df_filename,
               target_size=model.input_shape[1:3],
               batch_size=batch_size,
               class_mode=None,
               shuffle=False
          )
     elif event == '-THRESHOLD-':
          threshold = values['-THRESHOLD-']/100.
     elif event == '-RUN-':
          sg.cprint('Running....', c='white on green', end='')
          sg.cprint('')
          ### CALLBACK
          class OutputCallback(tf.keras.callbacks.Callback):
               def on_predict_batch_end(self, batch, logs=None):
                    window['-PROGBAR-'].update_bar((batch+1)*batch_size/test_generator.samples)
                    print("Processing batch of images",batch+1,": done", flush=True)
                    #print(logs['outputs'])
                    window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in test_generator.filenames[slice(batch*batch_size,min(test_generator.samples,(batch+1)*batch_size))]],
                                                                       prediction2class(logs['outputs'],threshold)].tolist())
          output = OutputCallback()
          ### PREDICTING
          prediction = model.predict(test_generator, workers=workers, callbacks=[output])
          predictedclass = prediction2class(prediction,threshold)         
          window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in test_generator.filenames],predictedclass].tolist())
          window['-SAVECSV-'].Update(disabled=False)
          if pkgutil.find_loader("openpyxl"):
               window['-SAVEXLSX-'].Update(disabled=False)
     elif event == '-SAVECSV-':
          preddf  = pd.DataFrame({'filename':test_generator.filenames, 'prediction':predictedclass})
          confirm = sg.popup_yes_no("Do you want to save results in"+join(testdir,"deepfaune.csv")+"?", keep_on_top=True)
          if confirm:
               print("Saving to",join(testdir,"deepfaune.csv"))
               preddf.to_csv(join(testdir,"deepfaune.csv"), index=False)
     elif event == '-SAVEXLSX-':
          preddf  = pd.DataFrame({'filename':test_generator.filenames, 'prediction':predictedclass})
          confirm = sg.popup_yes_no("Do you want to save results in"+join(testdir,"deepfaune.xslx")+"?", keep_on_top=True)
          if confirm:
               print("Saving to",join(testdir,"deepfaune.xlsx"))
               preddf.to_excel(join(testdir,"deepfaune.xlsx"), index=False)
     elif event == '-TABRESULTS-':
          rowidx = values['-TABRESULTS-']
          window['-TABROW-'].Update(disabled=False)
     elif event == '-TABROW-':
          if rowidx[0]>=0:
               ### SHOWING IMAGE
               layout = [[sg.Image(key="-IMAGE-")],
                         [sg.Text('Prediction:', size=(15, 1)),sg.InputText(predictedclass[rowidx[0]], key="-CORRECTION-")], [sg.Submit(), sg.Cancel()]]
               windowimg = sg.Window(basename(df_filename['filename'][rowidx[0]]), layout, finalize=True)
               image = Image.open(df_filename['filename'][rowidx[0]])
               image.thumbnail((300, 300))
               bio = io.BytesIO()
               image.save(bio, format="PNG")
               windowimg["-IMAGE-"].update(data=bio.getvalue())
               ### CORRECTING PREDICTION
               while True:
                    eventimg, valuesimg = windowimg.read()
                    if eventimg in (sg.WIN_CLOSED, 'Cancel'):
                         break
                    elif eventimg == 'Submit':
                         predictedclass[rowidx[0]] = valuesimg["-CORRECTION-"]
                         window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in test_generator.filenames],predictedclass].tolist())
                         break
               windowimg.close()
          else:
               window['-TABROW-'].Update(disabled=True)
               
               
               
window.close()  



     
