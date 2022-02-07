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


import PySimpleGUI as sg
import re
### SETTINGS
sg.ChangeLookAndFeel('Reddit')
#sg.ChangeLookAndFeel('Dark2')
#sg.ChangeLookAndFeel('DarkBlue1')
#sg.ChangeLookAndFeel('DarkGrey1')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0



####################################################################################
### ROUNDED BUTTON
####################################################################################



txt_classes = {'fr':["blaireau","bouquetin","cerf","chamois","chevreuil","chien","ecureuil","felinae","humain","lagomorphe","loup","micromammifere","mouflon","mouton","mustelide","oiseau","renard","sanglier","vache","vehicule"],
              'gb':["badger","ibex","red deer","chamois","roe deer","dog","squirrel","felinae","human","lagomorph","wolf","micromammal","mouflon","sheep","mustelide","bird","fox","wild boar","cow","vehicule"]}
txt_empty = {'fr':"vide", 'gb':"empty"}
txt_undefined = {'fr':"indéfini", 'gb':"undefined"}
txt_imagefolder = {'fr':"Dossier d'images", 'gb':"Image folder"}
txt_browse = {'fr':"Choisir", 'gb':"Select"}
txt_confidence = {'fr':"Seuil de confiance", 'gb':"Confidence threshold"}
txt_sequencemaxlag = {'fr':"Délai max / sequence (secondes)", 'gb':"Sequence max lag (seconds)"}
txt_progressbar = {'fr':"Barre d'état", 'gb':"Progress bar"}
txt_run = {'fr':"Lancer", 'gb':"Run"}
txt_save = {'fr':"Enregistrer en ", 'gb':"Save in "}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'gb':"Create subfolders"}
txt_copy = {'fr':"Copier les fichiers", 'gb':"Copy files"}
txt_move = {'fr':"Déplacer les fichiers", 'gb':"Move files"}
txt_loading = {'fr':"Chargement des paramètres... ", 'gb':"Loading model parameters... "}
txt_showall = {'fr':"Afficher les images", 'gb':"Show all images"}
txt_showselected = {'fr':"Afficher l'image sélectionnée", 'gb':"Show selected image"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in "}
txt_wanttocopy = {'fr':"Voulez-vous copier les images vers des sous-dossiers de ", 'gb':"Do you want to copy images in subfolders of "}
txt_wanttomove = {'fr':"Voulez-vous déplacer les images vers des sous-dossiers de ", 'gb':"Do you want to move images in subfolders of "}
txt_savepred = {'fr':"Enregistrer", 'gb':"Save"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous"}
txt_restrict = {'fr':["Undéfini seulement"], 'gb':["Only undefined"]}

def frgbprint(txt_fr, txt_gb, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    if LANG=="gb":
        print(txt_gb, end=end)
            

####################################################################################
### PARAMETERS
####################################################################################
VERSION = "0.1"
LANG = "fr"
DEBUG = False
backbone = "efficientnet"
hdf5 = "efficientnet_MDcheckOnlycroppedImgAugB3.hdf5"
BATCH_SIZE = 8
workers = 1
classes = txt_classes[LANG]
classesempty = classes + [txt_empty[LANG]]
YOLO_SIZE=608
CROP_SIZE=300
savedmodel = "checkpoints/yolov4-608/"


####################################################################################
### ROUNDED BUTTON
####################################################################################
from base64 import b64encode
from PIL import Image, ImageDraw
from PySimpleGUI import Button, BUTTON_TYPE_READ_FORM, FILE_TYPES_ALL_FILES, theme_background_color, theme_button_color
import io
from base64 import b64encode

def RButton(button_text=' ', corner_radius=0.5, button_type=BUTTON_TYPE_READ_FORM, target=(None, None),
            tooltip=None, file_types=FILE_TYPES_ALL_FILES, initial_folder=None, default_extension='',
            disabled=False, change_submits=False, enable_events=False,
            image_size=(None, None), image_subsample=None, border_width=0, size=(None, None),
            auto_size_button=None, button_color=None, disabled_button_color=("white","white"), highlight_colors=None, 
            mouseover_colors=(None, None), use_ttk_buttons=None, font=None, bind_return_key=False, focus=False, 
            pad=None, key=None, right_click_menu=None, expand_x=False, expand_y=False, visible=True, 
            metadata=None):
    if None in size:
        multi = 5
        size = (((len(button_text) if size[0] is None else size[0]) * 5 + 20) * multi,
                20 * multi if size[1] is None else size[1])
    if button_color is None:
        button_color = theme_button_color()
    btn_img = Image.new('RGBA', size, (0, 0, 0, 0))
    corner_radius = int(corner_radius/2*min(size))
    poly_coords = (
        (corner_radius, 0),
        (size[0] - corner_radius, 0),
        (size[0], corner_radius),
        (size[0], size[1] - corner_radius),
        (size[0] - corner_radius, size[1]),
        (corner_radius, size[1]),
        (0, size[1] - corner_radius),
        (0, corner_radius),
    )
    pie_coords = [
        [(size[0] - corner_radius * 2, size[1] - corner_radius * 2, size[0], size[1]),
         [0, 90]],
        [(0, size[1] - corner_radius * 2, corner_radius * 2, size[1]), [90, 180]],
        [(0, 0, corner_radius * 2, corner_radius * 2), [180, 270]],
        [(size[0] - corner_radius * 2, 0, size[0], corner_radius * 2), [270, 360]],
    ]
    brush = ImageDraw.Draw(btn_img)
    brush.polygon(poly_coords, button_color[1])
    for coord in pie_coords:
        brush.pieslice(coord[0], coord[1][0], coord[1][1], button_color[1])
    data = io.BytesIO()
    btn_img.thumbnail((size[0] // 3, size[1] // 3), resample=Image.LANCZOS)
    btn_img.save(data, format='png', quality=95)
    btn_img = b64encode(data.getvalue())
    return Button(button_text=button_text, button_type=button_type, target=target, tooltip=tooltip,
                  file_types=file_types, initial_folder=initial_folder, default_extension=default_extension,
                  disabled=disabled, change_submits=change_submits, enable_events=enable_events,
                  image_data=btn_img, image_size=image_size,
                  image_subsample=image_subsample, border_width=border_width, size=size,
                  auto_size_button=auto_size_button, button_color=(button_color[0], theme_background_color()),
                  disabled_button_color=disabled_button_color, highlight_colors=highlight_colors,
                  mouseover_colors=mouseover_colors, use_ttk_buttons=use_ttk_buttons, font=font,
                  bind_return_key=bind_return_key, focus=focus, pad=pad, key=key, right_click_menu=right_click_menu,
                  expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata)


####################################################################################
### GUI WINDOW
####################################################################################

## LANGUAGE SELECTION AT FIRST
windowlang = sg.Window("DeepFaune GUI",layout=[[sg.Text("Please select your language / choisissez votre langue")], 
                                            [sg.Radio("français", 1, key='-FR-', default=True), sg.Radio("english", 1, key='-GB-'), Button("OK", key='-OK-')]], font = ("Arial", 14)).Finalize()
while True:
    event, values = windowlang.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-OK-':
        if values["-FR-"] == True:
            LANG = 'fr'
        else:
            LANG = 'gb'
        break                          
windowlang.close()  

## GUI
prediction = [[],[]]
threshold = threshold_default = 0.5
maxlag = maxlag_default = 20 # seconds
left_col = [
    [sg.Image(filename=r'img/cameratrap-nb.png'),sg.Image(filename=r'img/logoINEE.png')],
    [sg.Text("DEEPFAUNE",size=(12,1), font=("Helvetica", 35)), sg.Text("version "+VERSION)],[sg.Text("\n\n\n")],
    [sg.Text(txt_imagefolder[LANG]), sg.In(size=(25,1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse(txt_browse[LANG], key='-FOLDERBROWSE-')],
    [sg.Text(txt_confidence[LANG]+'\t'), sg.Spin(values=[i for i in range(25, 99)], initial_value=int(threshold_default*100), size=(4, 1), change_submits=True, enable_events=True, key='-THRESHOLD-')],
    [sg.Text(txt_sequencemaxlag[LANG]+'\t'), sg.Spin(values=[i for i in range(5, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-')],
    [sg.Text(txt_progressbar[LANG]), sg.ProgressBar(1, orientation='h', size=(20, 2), border_width=4, key='-PROGBAR-',bar_color=['Blue','White'])],
    [RButton(txt_run[LANG], key='-RUN-'), RButton(txt_save[LANG]+'CSV', key='-SAVECSV-'), RButton(txt_save[LANG]+'XSLX', key='-SAVEXLSX-')],
    [RButton(txt_createsubfolders[LANG], key='-SUBFOLDERS-'), sg.Radio(txt_copy[LANG], 1, key='-CP-', default=True),sg.Radio(txt_move[LANG], 1, key='-MV-')]
]
right_col=[
    [sg.Multiline(size=(69, 10), default_text=txt_loading[LANG], write_only=True, key="-ML-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
    [sg.Table(values=prediction, headings=['filename','prediction','score'], justification = "c", 
              vertical_scroll_only=False, auto_size_columns=False, col_widths=[33, 17, 8], num_rows=BATCH_SIZE, 
              enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
              key='-TABRESULTS-')],      
    [RButton(txt_showall[LANG], key='-ALLTABROW-'),RButton(txt_showselected[LANG], key='-TABROW-')]
]
layout = [[sg.Column(left_col, element_justification='l' ),
           sg.Column(right_col, element_justification='l')]] 
window = sg.Window("DeepFaune GUI",layout, font = ("Arial", 14)).Finalize()
window['-FOLDERBROWSE-'].Update(disabled=True)
window['-RUN-'].Update(disabled=True)
window['-THRESHOLD-'].Update(disabled=True)
window['-LAG-'].Update(disabled=True)
window['-SAVECSV-'].Update(disabled=True)
window['-SAVEXLSX-'].Update(disabled=True)
window['-TABROW-'].Update(disabled=True)
window['-ALLTABROW-'].Update(disabled=True)
window['-SUBFOLDERS-'].Update(disabled=True)
window['-CP-'].Update(disabled=True)
window['-MV-'].Update(disabled=True)
window.read(timeout=0) # trick to make the button disabled at first


####################################################################################
### LOADING CLASSIFIER
####################################################################################
import tensorflow as tf
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D,Activation
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import numpy as np
import pandas as pd
from os import listdir, mkdir
from os.path import join, basename
from pathlib import Path
import pkgutil
import io
nbclasses=len(classes)
if backbone == "resnet":
    from keras.applications.resnet_v2 import ResNet50V2
    from keras.applications.resnet_v2 import preprocess_input, decode_predictions
    base_model = ResNet50V2(include_top=False, weights=None, input_shape=(300,300,3))
elif backbone == "efficientnet":
    from tensorflow.keras.applications.efficientnet import EfficientNetB3
    from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
    base_model = EfficientNetB3(include_top=False, weights=None, input_shape=(300,300,3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
#x = Dense(512)(x) #256,1024, etc. may work as well
x = Dense(nbclasses)(x) #number of classes
preds = Activation("softmax")(x)
model = Model(inputs=base_model.input,outputs=preds)
model.load_weights(hdf5)

####################################################################################
### LOADING YOLO 
####################################################################################
saved_model_loaded = tf.saved_model.load(savedmodel)
infer = saved_model_loaded.signatures['serving_default']

####################################################################################
### PREDICTION TOOL
####################################################################################
def prediction2class(prediction, threshold):
    class_pred = [txt_undefined[LANG] for i in range(len(prediction))] 
    score_pred = [0. for i in range(len(prediction))] 
    for i in range(len(prediction)):
        pred = prediction[i]
        if(max(pred)>=threshold):
            class_pred[i] = classesempty[np.argmax(pred)]
        score_pred[i] = int(max(pred)*100)/100.
    return class_pred, score_pred

####################################################################################
### PREDICTION TOOL USING EXIF INFO & SEQUENCES, TIME DELTA = 20s
####################################################################################
import random
from time import time
from datetime import datetime
def randomDate(seed):
    random.seed(seed)
    d = random.randint(1, int(time()))
    return datetime.fromtimestamp(d).strftime("%Y:%m:%d %H:%M:%S")

def get_date_taken(path):
    try:
        date = Image.open(path)._getexif()[36867]
    except:
        date = None
    return date
    
def correctPredictionWithSequence(df_filename, predictedclass_base, predictedscore_base):
    seqnum = np.repeat(0, df_filename.shape[0])
    ## Getting date from exif, or draw random fake date
    dates = np.array([get_date_taken(file) for file in df_filename["filename"]])
    withoutdate = np.where(dates == None)[0]
    dates[withoutdate] = [randomDate(int(i)) for i in withoutdate]
    
    ## Sorting dates and computing lag
    from datetime import timedelta
    datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
    datesorder = np.argsort(datesstrip)
    datesstripSorted = np.sort(datesstrip)
    
    def majorityVotingInSequence(i1, i2):
        df = pd.DataFrame({'prediction':[predictedclass_base[k] for k in datesorder[i1:(i2+1)]], 'score':[predictedscore_base[k] for k in datesorder[i1:(i2+1)]]})
        majority = df.groupby(['prediction']).sum()
        if list(majority.index) == [txt_empty[LANG]]:
            for k in datesorder[i1:(i2+1)]:
                predictedclass[k] = txt_empty[LANG]
                predictedscore[k] = predictedscore_base[k]
        else:
            majority = majority[majority.index != txt_empty[LANG]] # skipping empty images in sequence
            best = np.argmax(majority['score']) # selecting class with best total score
            majorityclass = majority.index[best]
            majorityscore = df.groupby(['prediction']).mean()['score'][best] # overall score as the mean for this class
            for k in datesorder[i1:(i2+1)]:
                if predictedclass_base[k]!= txt_empty[LANG]:
                    predictedclass[k] = majorityclass 
                    predictedscore[k] = int(majorityscore*100)/100.
                else:
                    predictedclass[k] = txt_empty[LANG]
                    predictedscore[k] = predictedscore_base[k]
            
    ## Treating sequences
    curseqnum = 1
    i1 = i2 = 0 # sequences boundaries
    for i in range(1,len(datesstripSorted)):
        lag = datesstripSorted[i]-datesstripSorted[i-1]
        if lag<timedelta(seconds=20): # subsequent images in sequence
            pass
        else: # sequence change
            majorityVotingInSequence(i1, i2)
            seqnum[datesorder[i1:(i2+1)]] = curseqnum
            curseqnum += 1
            i1 = i
        i2 = i
    majorityVotingInSequence(i1, i2)
    seqnum[datesorder[i1:(i2+1)]] = curseqnum
    return predictedclass, predictedscore, seqnum


####################################################################################
### GUI IN ACTION
####################################################################################
testdir = ""
rowidx = [-1]
frgbprint("terminé","done")
window['-FOLDERBROWSE-'].Update(disabled=False)
while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-FOLDER-':
        window['-SAVECSV-'].Update(disabled=True)
        window['-SAVEXLSX-'].Update(disabled=True)
        window['-SUBFOLDERS-'].Update(disabled=True)
        window['-CP-'].Update(disabled=True)
        window['-MV-'].Update(disabled=True)
        testdir = values['-FOLDER-']
        
        if testdir != "":
            frgbprint("Dossier sélectionné : "+testdir, "Selected folder: "+testdir)
            ### GENERATOR
            
            df_filename = pd.DataFrame({'filename':sorted(
                [f for f in  Path(testdir).rglob('*.[Jj][Pp][Gg]') if not f.parents[1].match('*deepfaune_*')] +
                [f for f in  Path(testdir).rglob('*.[Jj][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
                [f for f in  Path(testdir).rglob('*.[Bb][Mm][Pp]') if not f.parents[1].match('*deepfaune_*')] +
                [f for f in  Path(testdir).rglob('*.[Tt][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
                [f for f in  Path(testdir).rglob('*.[Gg][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
                [f for f in  Path(testdir).rglob('*.[Pp][Nn][Gg]') if not f.parents[1].match('*deepfaune_*')]
            )})
            nbfiles = df_filename.shape[0]
            frgbprint("Nombre d'images : "+str(nbfiles), "Number of images: "+str(nbfiles))
            if nbfiles>0:
                predictedclass_base = ['' for k in range(nbfiles)] # before autocorrect with sequences
                predictedscore_base = ['' for k in range(nbfiles)] # idem
                predictedclass = ['' for k in range(nbfiles)] 
                predictedscore = ['' for k in range(nbfiles)] 
                seqnum = np.repeat(0, df_filename.shape[0])
                window['-RUN-'].Update(disabled=False)
                window['-THRESHOLD-'].Update(disabled=False)
                window['-LAG-'].Update(disabled=False)
                window['-TABROW-'].Update(disabled=False)
                window['-ALLTABROW-'].Update(disabled=False)
                window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],
                                                                   predictedclass, predictedscore].tolist())
            else:
                sg.popup_error('Incorrect image folder - no image found')
                window['-RUN-'].Update(disabled=True)
                window['-TABROW-'].Update(disabled=True)
                window['-ALLTABROW-'].Update(disabled=True)
    elif event == '-THRESHOLD-':
        threshold = float(values['-THRESHOLD-'])/100.
    elif event == '-LAG-':
        maxlag = float(values['-LAG-'])
    elif event == '-RUN-':
        window['-RUN-'].Update(disabled=True)
        window['-FOLDERBROWSE-'].Update(disabled=True)
        window['-TABROW-'].Update(disabled=True)
        window['-ALLTABROW-'].Update(disabled=True)
        window['-THRESHOLD-'].Update(disabled=True)
        window['-LAG-'].Update(disabled=True)
        if LANG=="fr":
            sg.cprint('Calcul en cours', c='white on green', end='')
        if LANG=="gb":
            sg.cprint('Running', c='white on green', end='')
        sg.cprint('')
        ### PREDICTING
        prediction = np.zeros(shape=(nbfiles,nbclasses+1), dtype=np.float32)
        prediction[:,nbclasses] = 1 # by default, predicted as empty
        k1 = 0
        k2 = min(k1+BATCH_SIZE,nbfiles)
        batch = 1
        images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
        while(k1<nbfiles):
            frgbprint("Traitement du batch d'images "+str(batch)+"...", "Processing batch of images "+str(batch)+"...", end="")
            cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
            idxnonempty = []
            for k in range(k1,k2):
                ## LOADING image and convert ton float 32 numpy array
                image_path = df_filename["filename"][k]
                try:
                    original_image = Image.open(image_path)
                    original_image.getdata()[0]
                except OSError:
                    pass # Corrupted image, considered as empty
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
                        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                            scores=tf.reshape(
                                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                            max_output_size_per_class=5,
                            max_total_size=5,
                            iou_threshold=0.45,
                            score_threshold=0.25
                        )
                        idxnonempty.append(k)
                        idxmax  = np.unravel_index(np.argmax(scores.numpy()[0,:]), scores.shape[1])
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
            frgbprint(" terminé", " done")
            predictedclass_batch, predictedscore_batch = prediction2class(prediction[k1:k2,],threshold)
            window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"][k1:k2]], predictedclass_batch, predictedscore_batch].tolist())
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
        frgbprint("Autocorrection en utilisant les exif...", "Autocorrecting using exif information...", end="")
        predictedclass_base, predictedscore_base = prediction2class(prediction, threshold)
        predictedclass, predictedscore, seqnum = correctPredictionWithSequence(df_filename, predictedclass_base, predictedscore_base)
        frgbprint(" terminé", " done")
        window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]], predictedclass, predictedscore].tolist())
        window['-RUN-'].Update(disabled=True)
        window['-FOLDERBROWSE-'].Update(disabled=False)
        window['-SUBFOLDERS-'].Update(disabled=False)
        window['-CP-'].Update(disabled=False)
        window['-MV-'].Update(disabled=False)
        window['-SAVECSV-'].Update(disabled=False)
        if pkgutil.find_loader("openpyxl") is not None:
            import openpyxl
            window['-SAVEXLSX-'].Update(disabled=False)
        window['-ALLTABROW-'].Update(disabled=False)
    elif event == '-SAVECSV-':
        preddf  = pd.DataFrame({'filename':df_filename["filename"], 'seqnum':seqnum,
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        confirm = sg.popup_yes_no(txt_savepredictions[LANG]+join(testdir,"deepfaune.csv")+"?", keep_on_top=True)
        if confirm == 'Yes':
            frgbprint("Enregistrement dans "+join(testdir,"deepfaune.csv"), "Saving to "+join(testdir,"deepfaune.csv"))
            preddf.to_csv(join(testdir,"deepfaune.csv"), index=False)
            window['-SAVECSV-'].Update(disabled=True)
    elif event == '-SAVEXLSX-':
        preddf  = pd.DataFrame({'filename':df_filename["filename"], 'seqnum':seqnum,
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        confirm = sg.popup_yes_no(txt_savepredictions[LANG]+join(testdir,"deepfaune.xslx")+"?", keep_on_top=True)
        if confirm == 'Yes':
            frgbprint("Enregistrement dans "+join(testdir,"deepfaune.xlsx"), "Saving to "+join(testdir,"deepfaune.xlsx"))
            preddf.to_excel(join(testdir,"deepfaune.xlsx"), index=False)
            window['-SAVEXLSX-'].Update(disabled=True)
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
        layout = [[sg.Image(key="-IMAGE-")],
                  [sg.Text('Prediction:', size=(15, 1)),
                   sg.Combo(values=list(classesempty+['autre']), default_value=predictedclass[curridx], size=(15, 1), bind_return_key=True, key="-CORRECTION-")],
                  [RButton(txt_savepred[LANG], key='-SAVE-'),RButton('Close', key='-CLOSE-'),
                   RButton(txt_prevpred[LANG], key='-PREVIOUS-'),
                   RButton(txt_nextpred[LANG], bind_return_key=True, key='-NEXT-'),
                   #sg.Combo(values=txt_restrict[LANG], default_value=txt_restrict[LANG][0], size=(15, 1), bind_return_key=True, key="-RESTRICT-"),
                   sg.Checkbox('Only\nundefined', default=False, key="-ONLYUNDEFINED-")]]
        windowimg = sg.Window(basename(df_filename['filename'][curridx]), layout, size=(650, 600), font = ("Arial", 14), finalize=True)
        try:
            image = Image.open(df_filename['filename'][curridx])
            image.getdata()[0]
        except OSError:
            image = Image.new('RGB', (600, 500))
        else:
            image = image.resize((600,500))
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
                predictedscore[curridx] = 1.0
                window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass,predictedscore].tolist())
                window['-TABROW-'].Update(disabled=True)
                window['-SAVECSV-'].Update(disabled=False)
                if pkgutil.find_loader("openpyxl") is not None:
                    window['-SAVEXLSX-'].Update(disabled=False)
            elif eventimg == '-PREVIOUS-' or eventimg == '-NEXT-': # button will save and show next image, return_key as well
                window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass,predictedscore].tolist())
                window['-TABROW-'].Update(disabled=True)
                curridxinit = curridx
                if eventimg == '-PREVIOUS-':
                    curridx = curridx-1
                    if curridx==-1:
                        curridx = len(predictedclass)-1
                    if valuesimg['-ONLYUNDEFINED-']: # search for the previous undefined image, if it exists
                        while predictedclass[curridx]!=txt_undefined[LANG] and curridx!=curridxinit:
                            curridx = curridx-1
                            if curridx==-1:
                                curridx = len(predictedclass)-1
                else: # eventimg == '-NEXT-'
                    curridx = curridx+1
                    if curridx==len(predictedclass):
                        curridx = 0
                    if valuesimg['-ONLYUNDEFINED-']: # search for the next undefined image, if it exists
                        while predictedclass[curridx]!=txt_undefined[LANG] and curridx!=curridxinit:
                            curridx = curridx+1
                            if curridx==len(predictedclass):
                                curridx = 0
                try:
                    image = Image.open(df_filename['filename'][curridx])
                    image.getdata()[0]
                except OSError:
                    image = Image.new('RGB', (600, 500))
                else:
                    image = image.resize((600,500))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                windowimg["-IMAGE-"].update(data=bio.getvalue())
                windowimg.TKroot.title(basename(df_filename['filename'][curridx]))
                windowimg["-CORRECTION-"].Update(predictedclass[curridx])
        windowimg.close()
        window['-ALLTABROW-'].Update(disabled=False)
    elif event == '-SUBFOLDERS-':
        now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if values["-CP-"] == True:
            confirm = sg.popup_yes_no(txt_wanttocopy[LANG]+join(testdir,"deepfaune_"+now)+"?", keep_on_top=True)             
            if confirm == 'Yes':
                frgbprint("Copie vers "+join(testdir,"deepfaune_"+now), "Copying to "+join(testdir,"deepfaune_"+now))
        if values["-MV-"] == True:
            confirm = sg.popup_yes_no(txt_wanttomove[LANG]+join(testdir,"deepfaune_"+now)+"?", keep_on_top=True)             
            if confirm == 'Yes':
                frgbprint("Déplacement vers "+join(testdir,"deepfaune_"+now), "Moving to "+join(testdir,"deepfaune_"+now))
        if confirm == 'Yes':
            import shutil
            mkdir(join(testdir,"deepfaune_"+now))
            for subfolder in  set(predictedclass):
                mkdir(join(testdir,"deepfaune_"+now,subfolder))
            if values["-CP-"] == True:
                for k in range(nbfiles):
                    shutil.copyfile(df_filename["filename"][k],
                                    join(testdir,"deepfaune_"+now,predictedclass[k],basename(df_filename['filename'][k])))
            if values["-MV-"] == True:
                for k in range(nbfiles):
                    shutil.move(df_filename["filename"][k],
                                join(testdir,"deepfaune_"+now,predictedclass[k],basename(df_filename['filename'][k])))
            window['-SUBFOLDERS-'].Update(disabled=True)
            window['-CP-'].Update(disabled=True)
            window['-MV-'].Update(disabled=True)
                            
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
    else:
        window['-TABROW-'].Update(disabled=True)
        
window.close()  



     
