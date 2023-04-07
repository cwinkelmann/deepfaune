# Copyright CNRS 2023

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
import threading

####################################################################################
### SETTINGS
####################################################################################
sg.ChangeLookAndFeel('Reddit')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0
os.environ["PYTORCH_JIT"] = "0"

####################################################################################
### PARAMETERS
####################################################################################
VERSION = "0.6.0"
LANG = "fr"

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
txt_browse = {'fr':"Choisir", 'gb':"Select"}
txt_incorrect = {'fr':"Dossier incorrect - aucun media trouvé", 'gb':"Incorrect folder - no media found"}
txt_confidence = {'fr':"Seuil de confiance", 'gb':"Confidence threshold"}
txt_sequencemaxlag = {'fr':"Délai max / séquence (secondes)", 'gb':"Sequence max lag (seconds)"}
txt_progressbar = {'fr':"Barre d'état", 'gb':"Progress bar"}
txt_run = {'fr':"Lancer", 'gb':"Run"}
txt_save = {'fr':"Enregistrer en ", 'gb':"Save in "}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'gb':"Create subfolders"}
txt_copy = {'fr':"Copier les fichiers", 'gb':"Copy files"}
txt_move = {'fr':"Déplacer les fichiers", 'gb':"Move files"}
txt_import = {'fr':"Import des modules externes... ", 'gb':"Importing external modules... "}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in "}
txt_wanttocopy = {'fr':"Voulez-vous copier les médias vers des sous-dossiers de ", 'gb':"Do you want to copy medias in subfolders of "}
txt_wanttomove = {'fr':"Voulez-vous déplacer les déplacer vers des sous-dossiers de ", 'gb':"Do you want to move medias in subfolders of "}
txt_savepred = {'fr':"Enregistrer", 'gb':"Save"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous"}
txt_maintab = {'fr':"Accueil", 'gb':"Home"}
txt_resultstab = {'fr':"Résultats", 'gb':"Results"}
txt_selectclasses = {'fr':"Sélection des classes", 'gb':"Classes selection"}
txt_credits = {'fr':"A propos", 'gb':"About DeepFaune"}
txt_paramframe = {'fr':"Paramètres", 'gb':"Parameters"}
txt_close  = {'fr':"Fermer", 'gb':"Close"}
txt_all = {'fr':"Toutes", 'gb':"All"}
txt_count = {'fr':"Comptage", 'gb':"Count"}
txt_import = {'fr':"Importer des médias", 'gb':"Import medias"}

def frgbprint(txt_fr, txt_gb, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    if LANG=="gb":
        print(txt_gb, end=end)


####################################################################################
### GUI UTILS
####################################################################################
def draw_boxes(imagecv, box=None):
    if box is not None:
        cv2.rectangle(imagecv, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), imagecv.shape[0]//100)
    
####################################################################################
### MAIN GUI WINDOW
####################################################################################
# Batch size for predictor, in number of images
if VIDEO:
    BATCH_SIZE = 12
else:
    BATCH_SIZE = 8

# Default parameters
threshold = threshold_default = 0.8
maxlag = maxlag_default = 20 # seconds

# Default selected classes
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
select_frame = sg.Frame(txt_selectclasses[LANG], listCB, font='Any 13', expand_x=True, expand_y=True)

# Credits
credits_layout = [
    [sg.Text("DeepFaune - version "+VERSION)],
    [sg.Text("Copyright CNRS - Licence CeCILL")],
    [sg.Text("https://www.deepfaune.cnrs.fr", font=('Any 13', 14, 'underline'), enable_events=True, key='-URL-')]
]

# Main window
menu_def = [['&File', ['&'+txt_import[LANG], '&Export results',['as csv', 'as xslx'],  '&Create subfolders', ['copy images', 'move images'],'E&xit']],
            ['&Edit', ['Edit Me', 'Special', 'Preferences',['Language', 'Data type'] , 'Undo']],
            ['&Help', ['&Version'], ['&'+txt_credits[LANG]]], ]

layout = [
    [sg.MenubarCustom(menu_def, pad=(0,0), k='-CUST MENUBAR-', bar_background_color='black', bar_text_color='white')],
    [
        [sg.Frame('',[
            [
                sg.Column([
                    [sg.Table(values=[],
                              headings=['filename'], justification = "l", 
                              vertical_scroll_only=False, auto_size_columns=False, col_widths=[20], num_rows=32, 
                              enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
                              key='-TAB-')],
                    [sg.Combo(values=[txt_all[LANG]]+sorted_txt_classes_lang+[txt_undefined[LANG],txt_empty[LANG]],
                              default_value=txt_all[LANG], size=(12, 1), bind_return_key=True, key="-RESTRICT-"),
                     sg.RealtimeButton(sg.SYMBOL_LEFT, key='-PREVIOUS-'),
                     sg.RealtimeButton(sg.SYMBOL_RIGHT, key='-NEXT-')]
                ]),
                sg.Column([ 
                    [sg.Frame('',
                              [[sg.Image(filename=r'icons/1316-white-small.png', key='-IMAGE-', size=(933, 700))]]
                              )
                     ],
                    [sg.Text('Prediction:', size=(10, 1)),
                     sg.Combo(values=list(sorted_txt_classes_lang+[txt_empty[LANG]]+[txt_other[LANG]]), default_value="", size=(15, 1), bind_return_key=True, key='-PREDICTION-'),
                     sg.Text("\tScore: 0.0", key='-SCORE-'), sg.Text("\t"+txt_count[LANG]+": 0", key='-COUNT-')]
                ])
            ]
        ])]
    ],
    [
        sg.Frame('',[
            [sg.Button("Configure & Run", expand_x=False, key='-CONFIG-'),
             sg.ProgressBar(1, orientation='h', border_width=4, expand_x=True, key='-PROGBAR-',bar_color=['Blue','White'], style='vista')],
        ], expand_x=True)
    ]
]

window = sg.Window("DeepFaune - CNRS",layout, margins=(0,0), font = ("Arial", 14), resizable=True).Finalize()
window.read(timeout=0)


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

curridx = -1
testdir = ""
hasrun = False
imgmoved  = False
frgbprint("terminé","done")

while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == txt_credits[LANG]:
        import webbrowser
        webbrowser.open("https://www.deepfaune.cnrs.fr")
        continue
    elif event == txt_import[LANG]:
        window['-PROGBAR-'].update_bar(0)
        window['-IMAGE-'].update(filename=r'icons/1316-white-small.png', size=(933, 700))
        hasrun = False
        testdir = sg.popup_get_folder(txt_browse[LANG], no_window=True)
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
            if nbfiles==0:
                sg.popup_error(txt_incorrect[LANG], keep_on_top=True)
        window.Element('-TAB-').Update(values=[basename(f) for f in filenames])
    elif event == '-CONFIG-':
        import copy
        layoutconfig = [
            #[sg.Text('', size=(10, 1))],
            [select_frame],
            [sg.Frame(txt_paramframe[LANG], font='Any 13', expand_x=True, expand_y=True, layout=[
                [sg.Text(txt_confidence[LANG]+'\t', expand_x=True),
                 sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), change_submits=True, enable_events=True, key='-THRESHOLD-')],
                [sg.Text(txt_sequencemaxlag[LANG]+'\t', expand_x=True), sg.Spin(values=[i for i in range(0, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-')]
            ])],
            [sg.Button("Run", expand_x=False, key='-RUN-')]
        ]
        windowconfig = sg.Window("Configure & run XXXX", copy.deepcopy(layoutconfig), size=(540, 500), font = ("Arial", 14), finalize=True)
        while True:
            eventconfig, valuesconfig = windowconfig.read(timeout=10)
            if eventconfig == '-RUN-':
                break
            elif eventconfig in (sg.WIN_CLOSED, 'Exit'):
                print("XXXXXXX PAS PRIS EN COMPTE XXXXX")
                break
        threshold = float(valuesconfig['-THRESHOLD-'])
        maxlag = float(valuesconfig['-LAG-'])
        forbiddenclasses = []
        for label in sorted_txt_classes_lang:
            if not valuesconfig[label]:
                forbiddenclasses += [label]
        if len(forbiddenclasses):
            frgbprint("Classes non selectionnées : ", "Unselected classes: ", end="")
            print(forbiddenclasses)
        windowconfig.close()
        ########################
        # Predictions using CNNs
        ########################
        frgbprint("Chargement des paramètres... ", "Loading model parameters... ", end="")
        window.refresh()
        if VIDEO:
            predictor = PredictorVideo(filenames, threshold, LANG, BATCH_SIZE)
        else:
            predictor = Predictor(filenames, threshold, maxlag, LANG, BATCH_SIZE)
            filenames = predictor.getFilenames()
            window.Element('-TAB-').Update(values=[basename(f) for f in filenames])
        predictor.setForbiddenClasses(forbiddenclasses)
        def runPredictor():
            global window, nbfiles, BATCH_SIZE, VIDEO
            if VIDEO:
                while True:
                    batch, k1, k2 = predictor.nextBatch()
                    if k1==nbfiles: break
                    window['-PROGBAR-'].update_bar(batch/nbfiles)
                    window.refresh()
            else:
                while True:
                    batch, k1, k2 = predictor.nextBatch()
                    if k1==nbfiles: break
                    window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)
        thread = threading.Thread(target=runPredictor)
        thread.setDaemon(True)
        thread.start() 
        hasrun = True       
        frgbprint(" terminé", " done")
    elif event == '-SAVECSV-' or event == '-SAVEXLSX-':
        predictedclass_base, predictedscore_base, _, count = predictor.getPredictions()
        if VIDEO:
            predictedclass, predictedscore = predictedclass_base, predictedscore_base
        else:
            predictedclass, predictedscore, _, count = predictor.getPredictionsWithSequences()
        preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore,
                                'count':count})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        if event == '-SAVECSV-':
            csvpath = sg.popup_get_file(txt_savepredictions[LANG], no_window=True, save_as=True, default_path="deepfaune.csv", default_extension='csv', initial_folder=testdir)
            if csvpath:
                frgbprint("Enregistrement dans "+csvpath, "Saving to "+csvpath)
                preddf.to_csv(csvpath, index=False)
            xlsxpath = sg.popup_get_file(txt_savepredictions[LANG], no_window=True, save_as=True, default_path="deepfaune.xlsx", default_extension='xlsx', initial_folder=testdir)
            if xlsxpath:
                frgbprint("Enregistrement dans "+xlsxpath, "Saving to "+xlsxpath)
                preddf.to_excel(xlsxpath, index=False)
    elif (event == '-TAB-' and len(values['-TAB-'])>0) or  event == '-PREVIOUS-' or event == '-NEXT-' :
        if event == '-TAB-':
            rowidx = values['-TAB-'][0]
            curridx = rowidx
        else:
            if event == '-NEXT-':
                curridx = curridx+1
                if curridx==len(filenames):
                    curridx = 0
            if event == '-PREVIOUS-':
                curridx = curridx-1
                if curridx==-1:
                    curridx = len(filenames)-1
            window['-TAB-'].update(select_rows=[curridx])
            window['-TAB-'].Widget.see(curridx+1)
        if not imgmoved: 
            if VIDEO:
                cap = cv2.VideoCapture(filenames[curridx])
                lag = int(cap.get(5) / 3)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                while ((BATCH_SIZE - 1) * lag > total_frames):
                    lag = lag - 1
                if hasrun:                    
                    cap.set(cv2.CAP_PROP_POS_FRAMES, predictor.getKeyFrames(curridx) * lag)
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, imagecv = cap.read()
                if not ret:
                    imagecv = None
            else:
                try:
                    imagecv = cv2.imread(filenames[curridx])
                except:
                    imagecv = None
            if imagecv is None:
                imagecv = np.zeros((700,933,3), np.uint8)
            else:
                if hasrun:                    
                    if VIDEO:
                        predictedclass_curridx, predictedscore_curridx, predictedbox_curridx, count_curridx = predictor.getPredictions(curridx)
                    else:
                        predictedclass_curridx, predictedscore_curridx, predictedbox_curridx, count_curridx = predictor.getPredictionsWithSequences(curridx)
                    if predictedclass_curridx is not txt_empty[LANG]:
                        draw_boxes(imagecv,predictedbox_curridx)
                    window['-PREDICTION-'].update(value=predictedclass_curridx)
                    window['-SCORE-'].Update("\tScore: "+str(predictedscore_curridx))
                    window['-COUNT-'].Update("\t"+txt_count[LANG]+": "+str(count_curridx))
            imagecv = cv2.resize(imagecv, (933,700))
            is_success, png_buffer = cv2.imencode(".png", imagecv)
            bio = BytesIO(png_buffer)
            window['-IMAGE-'].update(data=bio.getvalue())
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
                imgmoved = True
        if confirm == 'Yes':
            import shutil
            if VIDEO:
                predictedclass, predictedscore, _, _ = predictor.getPredictionsWithSequences()
            else:
                predictedclass, predictedscore, _, _ = predictor.getPredictionsWithSequences()
            mkdir(join(testdir,"deepfaune_"+now))
            for subfolder in set(predictedclass):
                mkdir(join(testdir,"deepfaune_"+now,subfolder))
            if values["-CP-"] == True:
                for k in range(nbfiles):
                    shutil.copyfile(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
            if values["-MV-"] == True:
                for k in range(nbfiles):
                    shutil.move(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
window.close()

