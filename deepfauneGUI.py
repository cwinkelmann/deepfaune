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
### SETTINGS
sg.ChangeLookAndFeel('Reddit')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0

from classifTools import txt_classes
txt_undefined = {'fr':"indéfini", 'gb':"undefined"}
txt_empty = {'fr':"vide", 'gb':"empty"}
txt_other =  {'fr':"autre", 'gb':"other"}
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
txt_loading = {'fr':"Chargement des paramètres... ", 'gb':"Loading model parameters... "}
txt_showall = {'fr':"Afficher les images", 'gb':"Show all images"}
txt_showselected = {'fr':"Afficher l'image sélectionnée", 'gb':"Show selected image"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in "}
txt_wanttocopy = {'fr':"Voulez-vous copier les images vers des sous-dossiers de ", 'gb':"Do you want to copy images in subfolders of "}
txt_wanttomove = {'fr':"Voulez-vous déplacer les images vers des sous-dossiers de ", 'gb':"Do you want to move images in subfolders of "}
txt_savepred = {'fr':"Enregistrer", 'gb':"Save"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous"}
txt_restrict = {'fr':["Toutes images","Images indéfinies","Images vides","Images non vides"], 'gb':["All images","Undefined images","Empty images","Non empty images"]}

def frgbprint(txt_fr, txt_gb, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    if LANG=="gb":
        print(txt_gb, end=end)
            
####################################################################################
### PARAMETERS
####################################################################################
VERSION = "0.3.0"
LANG = "fr"
DEBUG = False

####################################################################################
### GUI WINDOW
####################################################################################
BATCH_SIZE = 8

## LANGUAGE SELECTION AT FIRST
windowlang = sg.Window("DeepFaune GUI",layout=[[sg.Text("Please select your language / choisissez votre langue")], 
                                            [sg.Radio("français", 1, key='-FR-', default=True), sg.Radio("english", 1, key='-GB-'), sg.Button("OK", key='-OK-')]], font = ("Arial", 14)).Finalize()
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
    [sg.Image(filename=r'icons/cameratrap-nb.png'),sg.Image(filename=r'icons/logoINEE.png')],
    [sg.Text("DEEPFAUNE",size=(12,1), font=("Helvetica", 35)), sg.Text("version "+VERSION)],[sg.Text("\n\n\n")],
    [sg.Text(txt_imagefolder[LANG]), sg.In(size=(25,1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse(txt_browse[LANG], key='-FOLDERBROWSE-')],
    [sg.Text(txt_confidence[LANG]+'\t'), sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), change_submits=True, enable_events=True, key='-THRESHOLD-')],
    [sg.Text(txt_sequencemaxlag[LANG]+'\t'), sg.Spin(values=[i for i in range(5, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-')],
    [sg.Text(txt_progressbar[LANG]), sg.ProgressBar(1, orientation='h', size=(20, 2), border_width=4, key='-PROGBAR-',bar_color=['Blue','White'])],
    [sg.Button(txt_run[LANG], key='-RUN-'), sg.Button(txt_save[LANG]+'CSV', key='-SAVECSV-'), sg.Button(txt_save[LANG]+'XSLX', key='-SAVEXLSX-')],
    [sg.Button(txt_createsubfolders[LANG], key='-SUBFOLDERS-'), sg.Radio(txt_copy[LANG], 1, key='-CP-', default=True),sg.Radio(txt_move[LANG], 1, key='-MV-')]
]
right_col=[
    [sg.Multiline(size=(69, 10), default_text=txt_loading[LANG], write_only=True, key="-ML-", reroute_stdout=True, echo_stdout_stderr=True, reroute_cprint=True)],
    [sg.Table(values=prediction, headings=['filename','prediction','score'], justification = "c", 
              vertical_scroll_only=False, auto_size_columns=False, col_widths=[33, 17, 8], num_rows=BATCH_SIZE, 
              enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
              key='-TABRESULTS-')],      
    [sg.Button(txt_showall[LANG], key='-ALLTABROW-'),sg.Button(txt_showselected[LANG], key='-TABROW-')]
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

from predictTools import Predictor
from sequenceTools import reorderAndCorrectPredictionWithSequence

testdir = ""
rowidx = [-1]
hasrun = False
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
                window['-ALLTABROW-'].Update(disabled=False)
                window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],
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
        window.refresh()
        ########################
        # Predictions using CNNs
        ########################
        predictor = Predictor(df_filename, threshold, txt_classes[LANG]+[txt_empty[LANG]], txt_undefined[LANG])
        batch = 1
        while True:
            batch, k1, k2, predictedclass_batch, predictedscore_batch = predictor.nextBatch()
            if not len(predictedclass_batch): break
            frgbprint("Traitement du batch d'images "+str(batch)+"...", "Processing batch of images "+str(batch)+"...", end="")
            frgbprint(" terminé", " done")
            window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)
            window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"][k1:k2]], predictedclass_batch, predictedscore_batch].tolist())                    
            window.refresh()
        predictedclass_base, predictedscore_base = predictor.getPredictions()
        frgbprint("Autocorrection en utilisant les séquences...", "Autocorrecting using sequences...", end="")                 
        df_filename, predictedclass_base, predictedscore_base, predictedclass, predictedscore, seqnum = reorderAndCorrectPredictionWithSequence(df_filename, predictedclass_base, predictedscore_base, maxlag, LANG)
        frgbprint(" terminé", " done")
        ########################
        ########################
        # Update and next actions
        window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]], predictedclass, predictedscore].tolist())
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
        preddf  = pd.DataFrame({'filename':df_filename["filename"], 'seqnum':seqnum,
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        confirm = sg.popup_yes_no(txt_savepredictions[LANG]+join(testdir,"deepfaune.csv")+"?", keep_on_top=True)
        if confirm == 'Yes':
            frgbprint("Enregistrement dans "+join(testdir,"deepfaune.csv"), "Saving to "+join(testdir,"deepfaune.csv"))
            preddf.to_csv(join(testdir,"deepfaune.csv"), index=False)
            window['-SAVECSV-'].Update(disabled=True)
    elif event == '-SAVEXLSX-':
        preddf  = pd.DataFrame({'filename':df_filename["filename"], 'seqnum':seqnum,
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore})
        preddf.sort_values(['seqnum','filename'], inplace=True)
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
                  [sg.Button('Close', key='-CLOSE-'),
                   sg.Button(txt_prevpred[LANG], key='-PREVIOUS-'),
                   sg.Button(txt_nextpred[LANG], bind_return_key=True, key='-NEXT-'),
                   sg.Combo(values=txt_restrict[LANG], default_value=txt_restrict[LANG][0], size=(15, 1), bind_return_key=True, key="-RESTRICT-")]]
        windowimg = sg.Window(basename(df_filename['filename'][curridx]), layout, size=(650, 600), font = ("Arial", 14), finalize=True)            
        image = cv2.imread(str(df_filename['filename'][curridx]))
        if image is None:
            image = np.zeros((600,500,3), np.uint8)
        else:
            image = cv2.resize(image, (600,500))
        is_success, png_buffer = cv2.imencode(".png", image)
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
                    window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"]],predictedclass,predictedscore].tolist())
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
                image = cv2.imread(str(df_filename['filename'][curridx]))
                if image is None:
                    image = np.zeros((600,500,3), np.uint8)
                else:
                    image = cv2.resize(image, (600,500))
                is_success, png_buffer = cv2.imencode(".png", image)
                bio = BytesIO(png_buffer)
                windowimg["-IMAGE-"].update(data=bio.getvalue())
                windowimg.TKroot.title(basename(df_filename['filename'][curridx]))
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



     
