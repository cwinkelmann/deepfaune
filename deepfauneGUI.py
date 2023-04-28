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
import threading
import io
import os
os.environ["PYTORCH_JIT"] = "0"

####################################################################################
### PARAMETERS
####################################################################################
VERSION = "1.0.0"
LANG = 'fr'
VIDEO = False 
threshold = threshold_default = 0.8
maxlag = maxlag_default = 10 # seconds

####################################################################################
### GUI TEXT
####################################################################################
from predictTools import txt_undefined, txt_empty, txt_classes
txt_other =  {'fr':"autre", 'gb':"other"}
txt_browse = {'fr':"Choisir", 'gb':"Select"}
txt_incorrect = {'fr':"Dossier incorrect - aucun media trouvé", 'gb':"Incorrect folder - no media found"}
txt_confidence = {'fr':"Seuil de confiance", 'gb':"Confidence threshold"}
txt_sequencemaxlag = {'fr':"Délai max / séquence (secondes)", 'gb':"Sequence max lag (seconds)"}
txt_configrun = {'fr':"Configurer et lancer", 'gb':"Configure & Run"}
txt_run = {'fr':"Lancer", 'gb':"Run"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous"}
txt_paramframe = {'fr':"Paramètres", 'gb':"Parameters"}
txt_selectclasses = {'fr':"Sélection des classes", 'gb':"Classes selection"}
txt_close  = {'fr':"Fermer", 'gb':"Close"}
txt_all = {'fr':"toutes", 'gb':"all"}
txt_classnotfound = {'fr':"Aucun média pour cette classe", 'gb':"No media found for this class"}
txt_count = {'fr':"Comptage", 'gb':"Count"}
txt_error = {'fr':"Erreur", 'gb':"Error"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in "}
txt_wanttocopy = {'fr':"Voulez-vous copier les médias vers des sous-dossiers de ", 'gb':"Do you want to copy medias in subfolders of "}
txt_wanttomove = {'fr':"Voulez-vous déplacer les déplacer vers des sous-dossiers de ", 'gb':"Do you want to move medias in subfolders of "}


####################################################################################
### THEME SETTINGS
####################################################################################
from b64_images import *

DEFAULT_THEME = {'accent': '#00bfff', 'background': '#121212', 'text': '#d7d7d7', 'alternate_background': '#222222'}
settings: dict = {'theme': DEFAULT_THEME.copy()}
accent_color, text_color, background_color = settings['theme']['accent'], settings['theme']['text'], settings['theme']['background']

SUN_VALLEY_TCL = 'theme/sun-valley.tcl'
FONT_NORMAL = 'Segoe UI', 11
FONT_SMALL = 'Segoe UI', 10
FONT_LINK = 'Segoe UI', 11, 'underline'
FONT_TITLE = 'Segoe UI', 14
FONT_MED = 'Segoe UI', 12
FONT_TAB = 'Meiryo UI', 10
LINK_COLOR = '#3ea6ff'


####################################################################################
### GUI UTILS
####################################################################################
def frgbprint(txt_fr, txt_gb, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    if LANG=="gb":
        print(txt_gb, end=end)
        
def draw_boxes(imagecv, box=None):
    if box is not None:
        cv2.rectangle(imagecv, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), imagecv.shape[0]//100)

import tkinter
from tkinter import filedialog
def dialog_get_dir(title):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    selectdir = filedialog.askdirectory(title=title, parent=_root)
    if len(selectdir) == 0:
        selectdir = None
    _root.destroy()
    return selectdir

def dialog_get_file(title, initialdir, initialfile, defaultextension):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    selectfile = filedialog.asksaveasfilename(initialdir=initialdir, initialfile=initialfile, defaultextension=defaultextension, parent=_root)
    if len(selectfile) == 0:
        selectfile = None
    _root.destroy()
    return selectfile

from tkinter import messagebox
def dialog_error(message):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    messagebox.showerror(title=txt_error[LANG], message=message)
    _root.destroy()
    
def dialog_yesno(message):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    yesorno = messagebox.askquestion('', message, icon='warning')
    _root.destroy()
    return yesorno    
    
import base64
from PIL import Image, ImageDraw
from PIL.Image import Resampling
def StyledButton(button_text, fill, text_color, font=None, tooltip=None, key=None, visible=True,
              pad=None, bind_return_key=False, button_width=None):
    multi = 4
    btn_w = ((len(button_text) if button_width is None else button_width) * 5 + 20) * multi
    height = 18 * multi
    btn_img = Image.new('RGBA', (btn_w, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(btn_img)
    x0 = y0 = 0
    radius = 10 * multi
    d.ellipse((x0, y0, x0 + radius * 2, height), fill=fill)
    d.ellipse((btn_w - radius * 2 - 1, y0, btn_w - 1, height), fill=fill)
    d.rectangle((x0 + radius, y0, btn_w - radius, height), fill=fill)
    data = io.BytesIO()
    btn_img.thumbnail((btn_w // 3, height // 3), Resampling.LANCZOS)
    btn_img.save(data, format='png', quality=100)
    btn_img = base64.b64encode(data.getvalue())
    return sg.Button(button_text=button_text, image_data=btn_img, button_color=(text_color, text_color),
                     tooltip=tooltip, key=key, pad=pad, enable_events=False, size=(button_width, 1),
                     bind_return_key=bind_return_key, font=font, visible=visible, border_width=0)

####################################################################################
### MAIN GUI WINDOW
####################################################################################
# Default selected classes
listCB = []
lineCB = []
sorted_txt_classes_lang = sorted(txt_classes[LANG])
for k in range(0,len(sorted_txt_classes_lang)):
    lineCB = lineCB+[sg.CB(sorted_txt_classes_lang[k], key=sorted_txt_classes_lang[k], size=(12,1), default=True, background_color=background_color, text_color=text_color)]
    if k%3==2:
        listCB = listCB+[lineCB]
        lineCB = []
if lineCB:
    listCB = listCB+[lineCB]
select_frame = sg.Frame(txt_selectclasses[LANG], listCB, font=FONT_NORMAL, expand_x=True, expand_y=True, background_color=background_color)

# Credits
credits_layout = [
    [sg.Text("DeepFaune - version "+VERSION)],
    [sg.Text("Copyright CNRS - Licence CeCILL")],
    [sg.Text("https://www.deepfaune.cnrs.fr", font=('Any 13', 14, 'underline'), enable_events=True, key='-URL-')]
]

# Main window
txt_file = {'fr':"Fichier", 'gb':"File"}
txt_pref = {'fr':"Préférences", 'gb':"Preferences"}
txt_help = {'fr':"Aide", 'gb':"Help"}
txt_import = {'fr':"Importer", 'gb':"Import"}
txt_importimage = {'fr':"Images", 'gb':"Images"}
txt_importvideo = {'fr':"Vidéos", 'gb':"Videos"}
txt_export = {'fr':"Exporter les résultats", 'gb':"Export results"}
txt_ascsv = {'fr':"Format CSV", 'gb':"As CSV"}
txt_asxlsx = {'fr':"Format XSLX", 'gb':"As XSLX"}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'gb':"Create subfolders"}
txt_copy = {'fr':"Copier les fichiers", 'gb':"Copy files"}
txt_move = {'fr':"Déplacer les fichiers", 'gb':"Move files"}
txt_language = {'fr':"Langue", 'gb':"Language"}
txt_credits = {'fr':"A propos", 'gb':"About DeepFaune"}
menu_def = [
    ['&'+txt_file[LANG], [
        '&'+txt_import[LANG],[txt_importimage[LANG],txt_importvideo[LANG]],
        '&'+txt_export[LANG],[txt_ascsv[LANG],txt_asxlsx[LANG]],
        '&'+txt_createsubfolders[LANG], [txt_copy[LANG],txt_move[LANG]]
    ]],
    ['&'+txt_pref[LANG], [
        txt_language[LANG], ['fr', 'gb']
    ]],
    ['&'+txt_help[LANG], [
        '&Version',
        '&'+txt_credits[LANG]
    ]]
]

layout = [
    [
        sg.MenubarCustom(menu_def, pad=(0,0), font=FONT_NORMAL, bar_font=FONT_NORMAL,
                      background_color=background_color, text_color=text_color,
                      bar_background_color=background_color, bar_text_color=text_color,
                      key='-CUST MENUBAR-')
    ],
    [
        [sg.Frame('',[
            [
                sg.Column([
                    [sg.Table(values=[],
                              headings=['Filename'], justification = "l", 
                              vertical_scroll_only=False, auto_size_columns=False, col_widths=[20], expand_y=True,#num_rows=24, 
                              enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
                              background_color=background_color, text_color=text_color,
                              key='-TAB-')],
                    [
                        sg.Combo(values=[txt_all[LANG]]+sorted_txt_classes_lang+[txt_undefined[LANG],txt_empty[LANG]], background_color=background_color, text_color=text_color, enable_events=True,
                                 default_value=txt_all[LANG], size=(12, 1), bind_return_key=True, key="-RESTRICT-"),
                        sg.Button(key='-PREVIOUS-', image_data=PREVIOUS_BUTTON_IMG, button_color=(background_color,background_color), tooltip='previous track'),
                        sg.Button(key='-NEXT-', image_data=NEXT_BUTTON_IMG, button_color=(background_color,background_color), tooltip='next track')
                     ]
                ], background_color=background_color, expand_y=True),
                sg.Column([ 
                    [sg.Frame('',
                              [[sg.Image(filename=r'icons/1316-black-large.png', key='-IMAGE-', size=(933, 700), background_color=background_color)]]
                              , background_color=background_color)
                     ],
                    [sg.Text('Prediction:', background_color=background_color, text_color=text_color, size=(10, 1)),
                     sg.Combo(values=list(sorted_txt_classes_lang+[txt_empty[LANG]]+[txt_other[LANG]]), default_value="", enable_events=True,
                              background_color=background_color, text_color=text_color, size=(15, 1), bind_return_key=True, key='-PREDICTION-'),
                     sg.Text("\tScore: 0.0", background_color=background_color, text_color=text_color, key='-SCORE-'),
                     sg.Text("\t"+txt_count[LANG]+": 0", background_color=background_color, text_color=text_color, key='-COUNT-')]
                ], background_color=background_color)
            ]
        ], background_color=background_color, expand_y=True)]
    ],
    [
        sg.Frame('',[
            [
                StyledButton(txt_configrun[LANG], accent_color, background_color, key='-CONFIG-', button_width=5+len(txt_configrun[LANG]), pad=(5, (7, 5))),
                sg.ProgressBar(1, orientation='h', border_width=1, expand_x=True, key='-PROGBAR-', bar_color=accent_color)
            ],
        ], expand_x=True, background_color=background_color)
    ]
]

window = sg.Window("DeepFaune - CNRS",layout, margins=(0,0), font = FONT_MED, resizable=True, background_color=background_color).Finalize()
window.read(timeout=0)

from tkinter import TclError
from contextlib import suppress
with suppress(TclError):
    window.TKroot.tk.call('source', SUN_VALLEY_TCL)
window.TKroot.tk.call('set_theme', 'dark')

window['-CONFIG-'].Update(disabled=True)
window['-PREDICTION-'].Update(disabled=True)
window['-RESTRICT-'].Update(disabled=True)
#window['-PREVIOUS-'].Update(disabled=True)
#window['-NEXT-'].Update(disabled=True)



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

curridx = -1 # current filenames index
rowidx = -1 # current tab row index
testdir = None
hasrun = False
imgmoved  = False
frgbprint("terminé","done")

while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == txt_credits[LANG]:
        #########################
        ## CREDITS
        #########################
        import webbrowser
        webbrowser.open("https://www.deepfaune.cnrs.fr")
        continue
    elif event == txt_importimage[LANG] or event == txt_importvideo[LANG]: 
        #########################
        ## LOADING MEDIAS
        #########################
        if event == txt_importimage[LANG]:
            VIDEO = False
        if event == txt_importvideo[LANG]:
            VIDEO = True
        window['-PROGBAR-'].update_bar(0)
        window['-IMAGE-'].update(filename=r'icons/1316-black-large.png', size=(933, 700))
        hasrun = False
        curridx = -1
        window['-PREDICTION-'].Update(disabled=True)
        window['-RESTRICT-'].Update(disabled=True)
        testdir = dialog_get_dir(txt_browse[LANG]) #sg.popup_get_folder(txt_browse[LANG], background_color=background_color, no_window=True)
        if testdir != None:
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
                dialog_error(txt_incorrect[LANG]) #sg.popup_error(txt_incorrect[LANG], keep_on_top=True)
                window['-CONFIG-'].Update(disabled=True)
                #window['-PREVIOUS-'].Update(disabled=True)
                #window['-NEXT-'].Update(disabled=True)
            else:
                window.Element('-TAB-').Update(values=[basename(f) for f in filenames])
                window['-CONFIG-'].Update(disabled=False)
                #window['-PREVIOUS-'].Update(disabled=False)
                #window['-NEXT-'].Update(disabled=False)
                curridx = 0
                rowidx = 0
                subsetidx = list(range(0,len(filenames)))
                window['-TAB-'].update(select_rows=[curridx])
    elif event == '-CONFIG-':
        #########################
        ## CONFIGURE & RUN
        #########################
        import copy
        if VIDEO:
            sequencespin = []
        else:
            sequencespin = [sg.Text(txt_sequencemaxlag[LANG]+'\t', expand_x=True, background_color=background_color, text_color=text_color),
                            sg.Spin(values=[i for i in range(0, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-', background_color=background_color, text_color=text_color)]
        layoutconfig = [
            [select_frame],
            [sg.Frame(txt_paramframe[LANG], font=FONT_MED, expand_x=True, expand_y=True, layout=[
                [sg.Text(txt_confidence[LANG]+'\t', expand_x=True, background_color=background_color, text_color=text_color),
                 sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), change_submits=True, enable_events=True,
                         background_color=background_color, text_color=text_color, key='-THRESHOLD-')],
                sequencespin
            ], background_color=background_color)],
            [
                StyledButton(txt_run[LANG], accent_color, background_color, button_width=5+len(txt_run[LANG]), key='-RUN-')
            ]
        ]
        windowconfig = sg.Window(txt_configrun[LANG], copy.deepcopy(layoutconfig),  margins=(0, 0),
                                 background_color=background_color, finalize=True)
        with suppress(TclError):
            windowconfig.TKroot.tk.call('source', SUN_VALLEY_TCL)
        windowconfig.TKroot.tk.call('set_theme', 'dark')
        configabort = False
        while True:
            eventconfig, valuesconfig = windowconfig.read(timeout=10)
            if eventconfig == '-RUN-':
                break
            elif eventconfig in (sg.WIN_CLOSED, 'Exit'):
                configabort = True
                break
        windowconfig.close()
        if not configabort:
            threshold = float(valuesconfig['-THRESHOLD-'])
            if not VIDEO:
                maxlag = float(valuesconfig['-LAG-'])
            forbiddenclasses = []
            for label in sorted_txt_classes_lang:
                if not valuesconfig[label]:
                    forbiddenclasses += [label]
            if len(forbiddenclasses):
                frgbprint("Classes non selectionnées : ", "Unselected classes: ", end="")
                print(forbiddenclasses)
            ########################
            # Predictions using CNNs
            ########################
            window['-CONFIG-'].Update(disabled=True)
            frgbprint("Chargement des paramètres... ", "Loading model parameters... ", end="")
            window.refresh()
            if VIDEO:
                from predictTools import PredictorVideo
                BATCH_SIZE = 12 # Batch size for predictor, in number of images
            else:
                from predictTools import Predictor
                BATCH_SIZE = 8
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
            window['-PREDICTION-'].Update(disabled=False)
            window['-RESTRICT-'].Update(disabled=False)
            window['-CONFIG-'].Update(disabled=False)
    elif (event == txt_ascsv[LANG] or event == txt_asxlsx[LANG]) and hasrun == True:
        #########################
        ## EXPORTING RESULTS
        #########################
        predictedclass, predictedscore, _, count = predictor.getPredictions()
        if VIDEO:
            predictedclass_base, predictedscore_base = predictedclass, predictedscore
        else:
            predictedclass_base, predictedscore_base, _, count = predictor.getPredictionsBase()
        preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                'prediction':predictedclass, 'score':predictedscore,
                                'count':count})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        if event == txt_ascsv[LANG]:
            csvpath =  dialog_get_file(txt_savepredictions[LANG], initialdir=testdir, initialfile="deepfaune.csv", defaultextension=".csv")
            if csvpath:
                frgbprint("Enregistrement dans "+csvpath, "Saving to "+csvpath)
                preddf.to_csv(csvpath, index=False)
        if event == txt_asxlsx[LANG]:
            xlsxpath =  dialog_get_file(txt_savepredictions[LANG], initialdir=testdir, initialfile="deepfaune.xlsx", defaultextension=".xlsx")
            if xlsxpath:
                frgbprint("Enregistrement dans "+xlsxpath, "Saving to "+xlsxpath)
                preddf.to_excel(xlsxpath, index=False)
    elif (testdir is not None) \
         and ((event == '-TAB-' and len(values['-TAB-'])>0) or  event == '-PREVIOUS-' or event == '-NEXT-') \
         and (len(subsetidx)>0):
        #########################
        ## BROWSING MEDIAS
        #########################
        if event == '-TAB-':
            rowidx = values['-TAB-'][0]
        else:
            if event == '-NEXT-':
                rowidx = rowidx+1
                if rowidx==len(subsetidx):
                    rowidx = 0
            if event == '-PREVIOUS-':
                rowidx = rowidx-1
                if rowidx==-1:
                    rowidx = len(subsetidx)-1           
        curridx = subsetidx[rowidx]
        if not imgmoved: 
            if VIDEO:
                cap = cv2.VideoCapture(filenames[curridx])
                lag = int(cap.get(5) / 3)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if hasrun:           
                    while ((BATCH_SIZE - 1) * lag > total_frames):
                        lag = lag - 1         
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
                    predictedclass_curridx, predictedscore_curridx, predictedbox_curridx, count_curridx = predictor.getPredictions(curridx)
                    if predictedclass_curridx is not txt_empty[LANG]:
                        draw_boxes(imagecv,predictedbox_curridx)
                    window['-PREDICTION-'].update(value=predictedclass_curridx)
                    window['-PREDICTION-'].Update(disabled=False)
                    window['-SCORE-'].Update("\tScore: "+str(predictedscore_curridx))
                    window['-COUNT-'].Update("\t"+txt_count[LANG]+": "+str(count_curridx))
            imagecv = cv2.resize(imagecv, (933,700))
            is_success, png_buffer = cv2.imencode(".png", imagecv)
            bio = BytesIO(png_buffer)
            window['-IMAGE-'].update(data=bio.getvalue())
        if event == '-PREVIOUS-' or event == '-NEXT-':
            # updating position in Table
            window['-TAB-'].update(select_rows=[rowidx])
            window['-TAB-'].Widget.see(rowidx+1)        
    elif (event == txt_copy[LANG] or event == txt_move[LANG]) and hasrun == True:
        #########################
        ## CREATING SUBFOLDERS
        #########################
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
        if event == txt_copy[LANG]:
            confirm = dialog_yesno(txt_wanttocopy[LANG]+join(testdir,"deepfaune_"+now)+"?")
            if confirm == 'yes':
                frgbprint("Copie vers "+join(testdir,"deepfaune_"+now), "Copying to "+join(testdir,"deepfaune_"+now))
        if event == txt_move[LANG]:
            confirm = dialog_yesno(txt_wanttomove[LANG]+join(testdir,"deepfaune_"+now)+"?")
            if confirm == 'yes':
                frgbprint("Déplacement vers "+join(testdir,"deepfaune_"+now), "Moving to "+join(testdir,"deepfaune_"+now))
                imgmoved = True
        if confirm == 'yes':
            import shutil
            predictedclass, predictedscore, _, _ = predictor.getPredictions()
            mkdir(join(testdir,"deepfaune_"+now))
            for subfolder in set(predictedclass):
                mkdir(join(testdir,"deepfaune_"+now,subfolder))
            if txt_copy[LANG]:
                for k in range(nbfiles):
                    shutil.copyfile(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
            if txt_move[LANG]:
                for k in range(nbfiles):
                    shutil.move(filenames[k], unique_new_filename(testdir, now, predictedclass[k], basename(filenames[k])))
    elif event == '-PREDICTION-':
        #########################
        ## CORRECTING PREDICTION
        #########################
        # color activated when possible to use keyboard on this element
        if hasrun:
            predictor.setPrediction(curridx, values['-PREDICTION-'], 1.0)
        window.Element('-PREDICTION-').Update(select=False)
        window.Element('-SCORE-').Update("\tScore: 1.0")
    elif event == '-RESTRICT-':
        #########################
        ## BROWSING RESTRICTION
        #########################
        if values['-RESTRICT-'] == txt_all[LANG]:
            subsetidx = list(range(0,len(filenames)))
        else:
            predictedclass, _, _, _ = predictor.getPredictions()
            subsetidx = list(np.where(np.array(predictedclass)==values['-RESTRICT-'])[0])
        if len(subsetidx)>0:
            window.Element('-TAB-').Update(values=[basename(f) for f in [filenames[k] for k in subsetidx]])
            window['-TAB-'].update(select_rows=[0])
        else:
            dialog_error(txt_classnotfound[LANG])
            window.Element('-TAB-').Update(values=[])
            window['-IMAGE-'].update(filename=r'icons/1316-black-large.png', size=(933, 700))
            window.Element('-PREDICTION-').Update(value="")
            window['-PREDICTION-'].Update(disabled=True)
            window.Element('-SCORE-').Update("\tScore: 0.0")
            window.Element('-COUNT-').Update("\tCount: 0")
        curridx = 0
        rowidx = 0
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
window.close()

