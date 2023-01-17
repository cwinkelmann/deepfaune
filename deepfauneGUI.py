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
import os

### SETTINGS
sg.ChangeLookAndFeel('Reddit')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0

            
####################################################################################
### PARAMETERS
####################################################################################
VERSION = "0.5.2"
LANG = "fr"
DEBUG = False

####################################################################################
### GUI OPTIONS
####################################################################################
LANG = 'fr'
VIDEO = False
windowoptions = sg.Window("DeepFaune GUI options",layout=[
    [[sg.Text("Language / langue")],
     [sg.Combo(values=list(["français","english"]), default_value="français", size=(20, 1), bind_return_key=True, key='-LANG-')],
     [sg.Text("Data type / type de données")],     
     [sg.Combo(values=list(["image","video"]), default_value="image", size=(20, 1), bind_return_key=True, key='-DATATYPE-')],
     [sg.Button("OK", key='-OK-')]]
], font = ("Arial", 14)).Finalize()
while True:
    event, values = windowoptions.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-OK-':
        if values["-LANG-"] == "français":
            LANG = 'fr'
        else:
            LANG = 'gb'
        if values["-DATATYPE-"] == "video":
            VIDEO = True
        else:
            VIDEO = False
        break
windowoptions.close()

####################################################################################
### GUI TEXT
####################################################################################
from predictTools import txt_undefined, txt_empty, txt_classes
txt_other =  {'fr':"autre", 'gb':"other"}
if VIDEO:
    txt_imagefolder = {'fr':"Dossier de vidéos", 'gb':"Video folder"}
else:
    txt_imagefolder = {'fr':"Dossier d'images", 'gb':"Image folder"}
txt_browse = {'fr':"Choisir", 'gb':"Select"}
txt_confidence = {'fr':"Seuil de confiance", 'gb':"Confidence threshold"}
txt_sequencemaxlag = {'fr':"Délai max / séquence (secondes)", 'gb':"Sequence max lag (seconds)"}
txt_progressbar = {'fr':"Barre d'état", 'gb':"Progress bar"}
txt_run = {'fr':"Lancer", 'gb':"Run"}
txt_save = {'fr':"Enregistrer en ", 'gb':"Save in "}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'gb':"Create subfolders"}
txt_copy = {'fr':"Copier les fichiers", 'gb':"Copy files"}
txt_move = {'fr':"Déplacer les fichiers", 'gb':"Move files"}
txt_import = {'fr':"Import des modules externes... ", 'gb':"Importing external modules... "}
if VIDEO:
    txt_showall = {'fr':"Afficher les vidéos", 'gb':"Show all vidéos"}
    txt_showselected = {'fr':"Afficher la vidéo sélectionnée", 'gb':"Show selected video"}
else:
    txt_showall = {'fr':"Afficher les images", 'gb':"Show all images"}
    txt_showselected = {'fr':"Afficher l'image sélectionnée", 'gb':"Show selected image"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in "}
if VIDEO:
    txt_wanttocopy = {'fr':"Voulez-vous copier les vidéos vers des sous-dossiers de ", 'gb':"Do you want to copy videos in subfolders of "}
    txt_wanttomove = {'fr':"Voulez-vous déplacer les vidéos vers des sous-dossiers de ", 'gb':"Do you want to move videos in subfolders of "}
else:
    txt_wanttocopy = {'fr':"Voulez-vous copier les images vers des sous-dossiers de ", 'gb':"Do you want to copy images in subfolders of "}
    txt_wanttomove = {'fr':"Voulez-vous déplacer les images vers des sous-dossiers de ", 'gb':"Do you want to move images in subfolders of "}
txt_savepred = {'fr':"Enregistrer", 'gb':"Save"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous"}
txt_maintab = {'fr':"Accueil", 'gb':"Home"}
txt_resultstab = {'fr':"Résultats", 'gb':"Results"}
txt_selecttab = {'fr':"Sélection des classes", 'gb':"Classes selection"}
txt_creditstab = {'fr':"A propos", 'gb':"About DeepFaune"}
txt_paramframe = {'fr':"Paramètres", 'gb':"Parameters"}
txt_predframe = {'fr':"Prédictions", 'gb':"Predictions"}
txt_saveframe = {'fr':"Enregistrement", 'gb':"Save as"}
txt_close  = {'fr':"Fermer", 'gb':"Close"}

if VIDEO:
    txt_restrict = {'fr':["Toutes vidéos","Vidéos indéfinies","Vidéos vides","Vidéos non vides"], 'gb':["All videos","Undefined videos","Empty videos","Non empty videos"]}
else:
    txt_restrict = {'fr':["Toutes images","Images indéfinies","Images vides","Images non vides"], 'gb':["All images","Undefined images","Empty images","Non empty images"]}

def frgbprint(txt_fr, txt_gb, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    if LANG=="gb":
        print(txt_gb, end=end)


####################################################################################
### GUI UTILS
####################################################################################

def draw_boxes(imagecv,box):
    cv2.rectangle(imagecv, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), imagecv.shape[0]//100)
        
####################################################################################
### MAIN GUI WINDOW
####################################################################################
# Batch size for predictor
BATCH_SIZE_PRED = 8
if VIDEO:
    BATCH_SIZE = 1
else:
    BATCH_SIZE = 8
prediction = [[],[]]
threshold = threshold_default = 0.8
maxlag = maxlag_default = 20 # seconds
main_tab = [
    [sg.Image(filename=r'icons/1316-white-small.png'),sg.Text("DEEPFAUNE", font=("Helvetica", 30)), sg.Image(filename=r'icons/logoINEE.png', expand_x=True)],
    [sg.Text(txt_imagefolder[LANG]), sg.In(expand_x=True, enable_events=True, key='-FOLDER-'), sg.FolderBrowse(txt_browse[LANG], key='-FOLDERBROWSE-')],
    [sg.Frame(txt_paramframe[LANG], font='Any 13', expand_x=True, expand_y=True, layout=[
        [sg.Text(txt_confidence[LANG]+'\t', expand_x=True), sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), change_submits=True, enable_events=True, key='-THRESHOLD-')],
        [sg.Text(txt_sequencemaxlag[LANG]+'\t', expand_x=True), sg.Spin(values=[i for i in range(5, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-')]
    ])],
    [sg.Frame('Execution', font='Any 13', expand_x=True, expand_y=True, layout=[
        [sg.Multiline(size=(40, 3), default_text=txt_import[LANG], write_only=True, expand_x=True, key="-ML-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
        [sg.Text(txt_progressbar[LANG]), sg.ProgressBar(1, orientation='h', border_width=4, expand_x=True, key='-PROGBAR-',bar_color=['Blue','White'], style='vista')]
    ])],
    [sg.Button(txt_run[LANG], expand_x=True, key='-RUN-')]
]
listCB = []
lineCB = []
sorted_txt_classes_lang = sorted(txt_classes[LANG])
for k in range(0,len(sorted_txt_classes_lang)):
    lineCB = lineCB+[sg.CB(sorted_txt_classes_lang[k], key=sorted_txt_classes_lang[k], size=(12,1), default=True)]
    if k%3==2:
        listCB = listCB+[lineCB]
        lineCB = []
if lineCB:
    listCB = listCB+[lineCB]
select_tab = [
    [sg.Frame('', listCB, font='Any 13', expand_x=True, expand_y=True)]
]
results_tab = [
    [sg.Frame(txt_predframe[LANG], font='Any 13', expand_x=True, expand_y=True, layout=[
        [sg.Table(values=prediction, headings=['filename','prediction','score'], justification = "c", 
                  vertical_scroll_only=False, auto_size_columns=False, col_widths=[33, 17, 8], num_rows=BATCH_SIZE, 
                  enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
                  key='-TABRESULTS-')],  
        [sg.Button(txt_showall[LANG], key='-ALLTABROW-'),sg.Button(txt_showselected[LANG], key='-TABROW-')],
    ])],   
    [sg.Frame(txt_saveframe[LANG], font='Any 13', expand_x=True, expand_y=True, layout=[
        [sg.Button(txt_save[LANG]+'CSV', key='-SAVECSV-'), sg.Button(txt_save[LANG]+'XSLX', key='-SAVEXLSX-')],
        [sg.Button(txt_createsubfolders[LANG], key='-SUBFOLDERS-'), sg.Radio(txt_copy[LANG], 1, key='-CP-', default=True),sg.Radio(txt_move[LANG], 1, key='-MV-')]
    ])]
]
credits_tab = [
    [sg.Text("DeepFaune - version "+VERSION)],
    [sg.Text("Copyright CNRS - Licence CeCILL")],
    [sg.Text("https://www.deepfaune.cnrs.fr", font=('Any 13', 14, 'underline'), enable_events=True, key='-URL-')]
]

layout = [[sg.TabGroup(
    [[sg.Tab(txt_maintab[LANG], main_tab),
      sg.Tab(txt_selecttab[LANG], select_tab, expand_x=True),
      sg.Tab(txt_resultstab[LANG], results_tab, expand_x=True),
      sg.Tab(txt_creditstab[LANG], credits_tab, expand_x=True)]],
    expand_x=True, expand_y=True)]]


window = sg.Window("DeepFaune GUI",layout, font = ("Arial", 14), resizable=True).Finalize()
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
### GUI IN ACTION
####################################################################################
from datetime import datetime
from io import BytesIO
import numpy as np
import pandas as pd
from os import mkdir
from os.path import join, basename
from pathlib import Path
import pkgutil
import cv2

if VIDEO:
    from predictTools import PredictorVideo
else:
    from predictTools import Predictor

testdir = ""
rowidx = [-1]
hasrun = False
imgmoved  = False
frgbprint("terminé","done")
window['-FOLDERBROWSE-'].Update(disabled=False)

while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-URL-':
        import webbrowser
        webbrowser.open("https://www.deepfaune.cnrs.fr")
        continue
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
            if VIDEO:
                filenames = sorted(
                    [str(f) for f in  Path(testdir).rglob('*.[Aa][Vv][Ii]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Mm][Pp]4') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Mm][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Mm][Oo][Vv]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Mm]4[Vv]') if not f.parents[1].match('*deepfaune_*')]
                )
            else:
                filenames = sorted(
                    [str(f) for f in  Path(testdir).rglob('*.[Jj][Pp][Gg]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Jj][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Bb][Mm][Pp]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Tt][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Gg][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
                    [str(f) for f in  Path(testdir).rglob('*.[Pp][Nn][Gg]') if not f.parents[1].match('*deepfaune_*')]
                )
            nbfiles = len(filenames)
            if VIDEO:
                frgbprint("Nombre de vidéos : "+str(nbfiles), "Number of videos: "+str(nbfiles))
            else:
                frgbprint("Nombre d'images : "+str(nbfiles), "Number of images: "+str(nbfiles))
            if nbfiles>0:
                predictedclass = ['' for k in range(nbfiles)] 
                predictedscore = ['' for k in range(nbfiles)] 
                window['-RUN-'].Update(disabled=False)
                window['-THRESHOLD-'].Update(disabled=False)
                if not VIDEO:
                    window['-LAG-'].Update(disabled=False)
                window['-ALLTABROW-'].Update(disabled=False)
                window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in filenames],
                                                                   predictedclass, predictedscore].tolist())
            else:
                sg.popup_error('Incorrect image folder - no image found', keep_on_top=True)
                window['-RUN-'].Update(disabled=True)
                window['-TABROW-'].Update(disabled=True)
                window['-ALLTABROW-'].Update(disabled=True)
    elif event == '-THRESHOLD-':
        threshold = float(values['-THRESHOLD-'])
    elif event == '-LAG-':
        maxlag = float(values['-LAG-'])
    elif event == '-RUN-':
        threshold = float(values['-THRESHOLD-'])
        maxlag = float(values['-LAG-'])
        hasrun = True
        forbiddenclasses = []
        for label in sorted_txt_classes_lang:
            if not values[label]:
                forbiddenclasses += [label]
        if len(forbiddenclasses):
            frgbprint("Classes non selectionnées : ", "Unselected classes: ", end="")
            print(forbiddenclasses)
        window['-RUN-'].Update(disabled=True)
        window['-FOLDERBROWSE-'].Update(disabled=True)
        window['-TABROW-'].Update(disabled=True)
        window['-ALLTABROW-'].Update(disabled=True)
        window['-THRESHOLD-'].Update(disabled=True)
        window['-LAG-'].Update(disabled=True)
        ########################
        # Predictions using CNNs
        ########################
        frgbprint("Chargement des paramètres... ", "Loading model parameters... ", end="")
        window.refresh()
        if VIDEO:
            predictor = PredictorVideo(filenames, threshold, LANG, BATCH_SIZE_PRED)
        else:
            predictor = Predictor(filenames, threshold, LANG, BATCH_SIZE_PRED)
        predictor.setForbiddenClasses(forbiddenclasses)
        frgbprint("terminé","done")
        window.refresh()
        if LANG=="fr":
            sg.cprint('Calcul en cours', c='white on green', end='')
        if LANG=="gb":
            sg.cprint('Running', c='white on green', end='')
        sg.cprint('')
        window.refresh()
        batch = 1
        while True:
            batch, k1, k2, predictedclass_batch, predictedscore_batch = predictor.nextBatch()
            if not len(predictedclass_batch): break
            frgbprint("Traitement du batch d'images "+str(batch)+"...", "Processing batch of images "+str(batch)+"...", end="")
            frgbprint(" terminé", " done")
            window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)
            window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in filenames[k1:k2]], predictedclass_batch, predictedscore_batch].tolist())
            window.refresh()
        if VIDEO:
            predictedclass_base, predictedscore_base, bestboxes = predictor.getPredictions()
            predictedclass, predictedscore = predictedclass_base, predictedscore_base
        else:
            frgbprint("Autocorrection en utilisant les séquences...", "Autocorrecting using sequences...", end="")
            predictedclass_base, predictedscore_base, bestboxes = predictor.getPredictions()
            predictedclass, predictedscore = predictor.getPredictionsWithSequences(maxlag)
            frgbprint(" terminé", " done")
        ########################
        ########################
        # Update and next actions
        window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in filenames], predictedclass, predictedscore].tolist())
        window['-RUN-'].Update(disabled=True)
        window['-FOLDERBROWSE-'].Update(disabled=False)
        window['-SUBFOLDERS-'].Update(disabled=False)
        window['-CP-'].Update(disabled=False)
        window['-MV-'].Update(disabled=False)
        window['-SAVECSV-'].Update(disabled=False)
        if pkgutil.find_loader("openpyxl") is not None:
            window['-SAVEXLSX-'].Update(disabled=False)
        window['-ALLTABROW-'].Update(disabled=False)
    elif event == '-SAVECSV-':
        preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        csvpath = sg.popup_get_file(txt_savepredictions[LANG], no_window=True, save_as=True, default_path="deepfaune.csv", default_extension='csv', initial_folder=testdir)
        if csvpath:
            frgbprint("Enregistrement dans "+csvpath, "Saving to "+csvpath)
            preddf.to_csv(csvpath, index=False)
            window['-SAVECSV-'].Update(disabled=True)
    elif event == '-SAVEXLSX-':
        preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        xlsxpath = sg.popup_get_file(txt_savepredictions[LANG], no_window=True, save_as=True, default_path="deepfaune.xlsx", default_extension='xlsx', initial_folder=testdir)
        if xlsxpath:
            frgbprint("Enregistrement dans "+xlsxpath, "Saving to "+xlsxpath)
            preddf.to_excel(xlsxpath, index=False)
            window['-SAVEXLSX-'].Update(disabled=True)
    elif event == '-TABRESULTS-':
        rowidx = values['-TABRESULTS-']
        if len(rowidx)==0:
            window['-TABROW-'].Update(disabled=True)
        else:
            window['-TABROW-'].Update(disabled=False) 
    elif (event == '-ALLTABROW-' or event == '-TABROW-') and imgmoved == False :
        if event == '-TABROW-' and rowidx[0]>=0:
            curridx = rowidx[0]
        else:
            curridx = 0
        ## DISABLING PRINCIPAL WINDOW (but keep info about enabled buttons)
        window['-TABROW-'].Update(disabled=True)
        window['-ALLTABROW-'].Update(disabled=True)
        folderbrowsestate = window['-FOLDERBROWSE-'].Disabled
        window['-FOLDERBROWSE-'].Update(disabled=True)
        runstate = window['-RUN-'].Disabled
        window['-RUN-'].Update(disabled=True)
        savecsvstate = window['-SAVECSV-'].Disabled
        window['-SAVECSV-'].Update(disabled=True)
        savexlsxstate = window['-SAVEXLSX-'].Disabled
        window['-SAVEXLSX-'].Update(disabled=True)
        subfoldersstate = window['-SUBFOLDERS-'].Disabled
        window['-SUBFOLDERS-'].Update(disabled=True)
        ### SHOWING IMAGE
        classes = txt_classes[LANG]
        classesempty = classes + [txt_empty[LANG]]
        layout = [[sg.Image(key="-IMAGE-")],
                  [sg.Text('Prediction:', size=(10, 1)),
                   sg.Combo(values=list(classesempty+[txt_other[LANG]]), default_value=predictedclass[curridx], size=(15, 1), bind_return_key=True, key='-CORRECTION-'),
                   sg.Text("\tScore: "+str(predictedscore[curridx]), key='-CORRECTIONSCORE-')],
                  [sg.Button(txt_close[LANG], key='-CLOSE-'),
                   sg.Button(txt_prevpred[LANG], key='-PREVIOUS-'),
                   sg.Button(txt_nextpred[LANG], bind_return_key=True, key='-NEXT-'),
                   sg.Combo(values=txt_restrict[LANG], default_value=txt_restrict[LANG][0], size=(15, 1), bind_return_key=True, key="-RESTRICT-")]]
        windowimg = sg.Window(basename(filenames[curridx]), layout, size=(540, 500), font = ("Arial", 14), finalize=True) 
        if VIDEO:
            cap = cv2.VideoCapture(filenames[curridx])
            lag = int(cap.get(5) / 3)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            while ((BATCH_SIZE_PRED - 1) * lag > total_frames):
                lag = lag - 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, predictor.getKeyFrames(curridx) * lag)
            ret, imagecv = cap.read()
            if not ret:
                imagecv = np.zeros((400,500,3), np.uint8)
            else:
                if predictedclass[curridx] is not txt_empty[LANG]:
                    draw_boxes(imagecv,bestboxes[curridx])
                imagecv = cv2.resize(imagecv, (500,400))
        else:
            try:
                imagecv = cv2.imread(filenames[curridx])
            except:
                imagecv = None
            if imagecv is None:
                imagecv = np.zeros((400,500,3), np.uint8)
            else:
                if predictedclass[curridx] is not txt_empty[LANG]:
                    draw_boxes(imagecv,bestboxes[curridx])
                imagecv = cv2.resize(imagecv, (500,400))
        is_success, png_buffer = cv2.imencode(".png", imagecv)
        bio = BytesIO(png_buffer)
        windowimg["-IMAGE-"].update(data=bio.getvalue())
        ### CORRECTING PREDICTION
        while True:
            eventimg, valuesimg = windowimg.read(timeout=10)
            if valuesimg != None: # any change in the Combo list is saved
                if predictedclass[curridx] != valuesimg['-CORRECTION-']:
                    predictedclass[curridx] = valuesimg['-CORRECTION-']
                    predictedscore[curridx] = 1.0
                    windowimg.Element('-CORRECTIONSCORE-').Update("\tScore: 1.0")
                    window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in filenames],predictedclass,predictedscore].tolist())
                    window['-TABROW-'].Update(disabled=True)
                    if hasrun: savecsvstate = False
                    if pkgutil.find_loader("openpyxl") is not None:
                        if hasrun: savexlsxstate = False
            if eventimg in (sg.WIN_CLOSED, '-CLOSE-'):
                break
            elif eventimg == '-PREVIOUS-' or eventimg == '-NEXT-': # button will save and show next image, return_key as well
                #window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass,predictedscore].tolist())
                #window['-TABROW-'].Update(disabled=True)
                curridxinit = curridx
                if eventimg == '-PREVIOUS-':
                    curridx = curridx-1
                    if curridx==-1:
                        curridx = len(predictedclass)-1
                    if valuesimg['-RESTRICT-']!=txt_restrict[LANG][0]: # search for the previous image with condition, if it exists
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][1]: txt_target  = [txt_undefined[LANG]]
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][2]: txt_target  = [txt_empty[LANG]]
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][3]: txt_target  = txt_classes[LANG]
                        while (not predictedclass[curridx] in txt_target) and curridx!=curridxinit:
                            curridx = curridx-1
                            if curridx==-1:
                                curridx = len(predictedclass)-1
                else: # eventimg == '-NEXT-'
                    curridx = curridx+1
                    if curridx==len(predictedclass):
                        curridx = 0
                    if valuesimg['-RESTRICT-']!=txt_restrict[LANG][0]: # search for the next image with condition, if it exists
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][1]: txt_target  = [txt_undefined[LANG]]
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][2]: txt_target  = [txt_empty[LANG]]
                        if valuesimg['-RESTRICT-']==txt_restrict[LANG][3]: txt_target  = txt_classes[LANG]
                        while (not predictedclass[curridx] in txt_target) and curridx!=curridxinit:
                            curridx = curridx+1
                            if curridx==len(predictedclass):
                                curridx = 0
                if VIDEO:
                    cap = cv2.VideoCapture(filenames[curridx])
                    lag = int(cap.get(5) / 3)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    while ((BATCH_SIZE_PRED - 1) * lag > total_frames):
                        lag = lag - 1
                    cap.set(cv2.CAP_PROP_POS_FRAMES, predictor.getKeyFrames(curridx) * lag)
                    if not ret:
                        imagecv = np.zeros((400,500,3), np.uint8)
                    else:
                        if predictedclass[curridx] is not txt_empty[LANG]:
                            draw_boxes(imagecv, bestboxes[curridx])
                        imagecv = cv2.resize(imagecv, (500,400))
                else:
                    try:
                        imagecv = cv2.imread(filenames[curridx])
                    except:
                        imagecv = None
                    if imagecv is None:
                        imagecv = np.zeros((400,500,3), np.uint8)
                    else:
                        if predictedclass[curridx] is not txt_empty[LANG]:
                            draw_boxes(imagecv, bestboxes[curridx])
                        imagecv = cv2.resize(imagecv, (500,400))
                is_success, png_buffer = cv2.imencode(".png", imagecv)
                bio = BytesIO(png_buffer)
                windowimg["-IMAGE-"].update(data=bio.getvalue())
                windowimg.TKroot.title(basename(filenames[curridx]))
                windowimg["-CORRECTION-"].Update(predictedclass[curridx])
                windowimg["-CORRECTIONSCORE-"].Update("\tScore: "+str(predictedscore[curridx]))
        windowimg.close()
        window['-ALLTABROW-'].Update(disabled=False)
        window['-FOLDERBROWSE-'].Update(disabled=folderbrowsestate)
        window['-RUN-'].Update(disabled=runstate)
        window['-SAVECSV-'].Update(disabled=savecsvstate)
        window['-SAVEXLSX-'].Update(disabled=savexlsxstate)
        window['-SUBFOLDERS-'].Update(disabled=subfoldersstate)
    elif event == '-SUBFOLDERS-':
        def unique_new_filename(testdir, now, classname, basename):
            folder = join(join(testdir, "deepfaune_"+now, classname))
            if os.path.exists(join(folder, basename)):
                i = 2
                part1 = basename[:-4]
                part2 = basename[-4:]
                basename = f"{part1}_{i}{part2}"
                while os.path.exists(join(folder, basename)):
                    i += 1
                    basename = f"{part1}_{i}{part2}"
            return join(folder, basename)

        now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if values["-CP-"] == True:
            confirm = sg.popup_yes_no(txt_wanttocopy[LANG]+join(testdir,"deepfaune_"+now)+"?", keep_on_top=True)             
            if confirm == 'Yes':
                frgbprint("Copie vers "+join(testdir,"deepfaune_"+now), "Copying to "+join(testdir,"deepfaune_"+now))
        if values["-MV-"] == True:
            confirm = sg.popup_yes_no(txt_wanttomove[LANG]+join(testdir,"deepfaune_"+now)+"?", keep_on_top=True)             
            if confirm == 'Yes':
                frgbprint("Déplacement vers "+join(testdir,"deepfaune_"+now), "Moving to "+join(testdir,"deepfaune_"+now))
                window['-ALLTABROW-'].Update(disabled=True)
                window['-SUBFOLDERS-'].Update(disabled=True)
                window['-SUBFOLDERS-'].Update(disabled=True)
                window['-CP-'].Update(disabled=True)
                window['-MV-'].Update(disabled=True)
                imgmoved = True
        if confirm == 'Yes':
            import shutil
            mkdir(join(testdir,"deepfaune_"+now))
            for subfolder in  set(predictedclass):
                mkdir(join(testdir,"deepfaune_"+now,subfolder))
            if values["-CP-"] == True:
                for k in range(nbfiles):
                    shutil.copyfile(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
            if values["-MV-"] == True:
                for k in range(nbfiles):
                    shutil.move(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
            window['-SUBFOLDERS-'].Update(disabled=True)
            window['-CP-'].Update(disabled=True)
            window['-MV-'].Update(disabled=True)
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
    else:
        window['-TABROW-'].Update(disabled=True)
window.close()

