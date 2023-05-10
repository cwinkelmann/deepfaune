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
txt_other =  {'fr':"autre", 'gb':"other", 'it':"altro"}
txt_browse = {'fr':"Choisir", 'gb':"Select", 'it':"Scegliere"}
txt_incorrect = {'fr':"Dossier incorrect - aucun media trouvé", 'gb':"Incorrect folder - no media found", 'it':"File scorretto - media non trovato"}
txt_confidence = {'fr':"Seuil de confiance", 'gb':"Confidence threshold", 'it':"Livello minimo di affidabilita"}
txt_sequencemaxlag = {'fr':"Intervalle max / séquence (secondes)", 'gb':"Sequence max lag (seconds)", 'it':"Intervallo massimo / sequenza (secondi)"}
txt_configrun = {'fr':"Configurer et lancer", 'gb':"Configure & Run", 'it':"Configurare e inviare"}
txt_run = {'fr':"Lancer", 'gb':"Run", 'it':"Inviare"}
txt_nextpred = {'fr':"Suivant", 'gb':"Next", 'it':"Prossimo"}
txt_prevpred = {'fr':"Précédent", 'gb':"Previous", 'it':"Precedente"}
txt_paramframe = {'fr':"Paramètres", 'gb':"Parameters", 'it':"Parametri"}
txt_selectclasses = {'fr':"Sélection des classes", 'gb':"Classes selection", 'it':"Selezione delle classi"}
txt_close  = {'fr':"Fermer", 'gb':"Close", 'it':"Chiudere"}
txt_all = {'fr':"toutes", 'gb':"all", 'it':"tutte"}
txt_classnotfound = {'fr':"Aucun média pour cette classe", 'gb':"No media found for this class", 'it':"Nessun media per questa classe"}
txt_filename = {'fr':"Nom de fichier", 'gb':"Filename", 'it':"Nome del file"}
txt_prediction = {'fr':"Prédiction", 'gb':"Prediction", 'it':"Predizione"}
txt_count = {'fr':"Comptage", 'gb':"Count", 'it':"Conto"}
txt_seqnum = {'fr':"Numéro de séquence", 'gb':"Sequence ID", 'it':"Sequenza"}
txt_error = {'fr':"Erreur", 'gb':"Error", 'it':"Errore"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'gb':"Do you want to save predictions in ",
                       'it':"Volete registrare le predizioni nel"}
txt_destcopy = {'fr':"Copier dans des sous-dossiers de :", 'gb':"Copy in subfolders of:", 'it':"Copiare nei sotto file di"}
txt_destmove = {'fr':"Déplacer vers des sous-dossiers de :", 'gb':"Move to subfolders of:", 'it':"Spostare nei sotto file di"}
#txt_wanttocopy = {'fr':"Voulez-vous copier les médias vers des sous-dossiers de ", 'gb':"Do you want to copy medias in subfolders of ", 'it':""}
#txt_wanttomove = {'fr':"Voulez-vous déplacer les déplacer vers des sous-dossiers de ", 'gb':"Do you want to move medias in subfolders of ", 'it':""}
txt_loadingmetadata = {'fr':"Chargement des metadonnées... (cela peut prendre du temps)", 'gb':"Loading metadata... (this may take a while)",
                       'it':"Carica dei metadata... (puo essere lungo)"}

####################################################################################
### THEME SETTINGS
####################################################################################
from b64_images import *

DEFAULT_THEME = {'accent': '#00bfff', 'background': '#121212', 'text': '#d7d7d7', 'alternate_background': '#222222'}
settings: dict = {'theme': DEFAULT_THEME.copy()}
accent_color, text_color, background_color = settings['theme']['accent'], settings['theme']['text'], settings['theme']['background']

SUN_VALLEY_TCL = 'theme/sun-valley.tcl'
SUN_VALLEY_THEME = 'dark' # 'light' not coherent with DEFAULT THEME
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
from tkinter import filedialog, messagebox
def dialog_get_dir(title, initialdir=None):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    selectdir = filedialog.askdirectory(title=title, initialdir=initialdir, parent=_root)
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

def dialog_yesno(message):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    yesorno = messagebox.askquestion('', message, icon='warning', parent=_root)
    _root.destroy()
    return yesorno

def dialog_error(message):
    _root = tkinter.Tk()
    _root.tk.call('source', SUN_VALLEY_TCL)
    _root.tk.call('set_theme', 'light')
    _root.withdraw()
    messagebox.showerror(title=txt_error[LANG], message=message, parent=_root)
    _root.destroy()
    
def popup(message):
    layout = [[sg.Text(message, background_color=background_color, text_color=text_color)]]
    windowpopup = sg.Window('Message', layout, no_titlebar=True, keep_on_top=True,
                            font = FONT_MED, background_color=background_color, finalize=True)
    from tkinter import TclError
    from contextlib import suppress
    with suppress(TclError):
        windowpopup.TKroot.tk.call('source', SUN_VALLEY_TCL)
    windowpopup.TKroot.tk.call('set_theme', SUN_VALLEY_THEME)
    return windowpopup
    
import base64
from PIL import Image, ImageDraw
from PIL.Image import Resampling
def StyledButton(button_text, fill, text_color, background_color, font=None, tooltip=None, key=None, visible=True,
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
    return sg.Button(button_text=button_text, image_data=btn_img,
                     button_color=(text_color, background_color), mouseover_colors=(text_color, background_color),
                     tooltip=tooltip, key=key, pad=pad, enable_events=False, size=(button_width, 1),
                     bind_return_key=bind_return_key, font=font, visible=visible, border_width=0)

def StyledMenu(menu_definition, text_color, background_color, text_font, key):    
    bar_text = text_color
    bar_bg = background_color
    bar_font = text_font
    font = text_font
    menu_bg = background_color
    menu_text = text_color
    disabled_text_color = 'gray'
    row = []
    for menu in menu_def:
        text = menu[0]
        if sg.MENU_SHORTCUT_CHARACTER in text:
            text = text.replace(sg.MENU_SHORTCUT_CHARACTER, '')
        if text.startswith(sg.MENU_DISABLED_CHARACTER):
            disabled = True
            text = text[len(sg.MENU_DISABLED_CHARACTER):]
        else:
            disabled = False
        button_menu = sg.ButtonMenu(text, menu, border_width=0, button_color=(bar_text, bar_bg), key=text, pad=(0, 0), disabled=disabled,
                                    font=bar_font, item_font=font, disabled_text_color=disabled_text_color, text_color=menu_text, background_color=menu_bg) #, tearoff=tearoff)
        button_menu.part_of_custom_menubar = True
        #button_menu.custom_menubar_key = key if key is not None else k
        row += [button_menu]
    return(sg.Column([row], pad=(0,0), background_color=bar_bg, expand_x=True, key=key))


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

# Main window
txt_file = {'fr':"Fichier", 'gb':"File", 'it':"File"}
txt_pref = {'fr':"Préférences", 'gb':"Preferences", 'it':"Preferenze"}
txt_help = {'fr':"Aide", 'gb':"Help", 'it':"Aiuto"}
txt_import = {'fr':"Importer", 'gb':"Import", 'it':"Caricare"}
txt_importimage = {'fr':"Images", 'gb':"Images", 'it':"Immagine"}
txt_importvideo = {'fr':"Vidéos", 'gb':"Videos", 'it':"Video"}
txt_export = {'fr':"Exporter les résultats", 'gb':"Export results", 'it':"Esportare i risultati"}
txt_ascsv = {'fr':"Format CSV", 'gb':"As CSV", 'it':"Formato CSV"}
txt_asxlsx = {'fr':"Format XSLX", 'gb':"As XSLX", 'it':"Formato XSLX"}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'gb':"Create subfolders", 'it':"Creare dei sotto file"}
txt_copy = {'fr':"Copier les fichiers", 'gb':"Copy files", 'it':"Copiare i file"}
txt_move = {'fr':"Déplacer les fichiers", 'gb':"Move files", 'it':"Spostare i file"}
txt_language = {'fr':"Langue", 'gb':"Language", 'it':"Lingua"}
txt_credits = {'fr':"A propos", 'gb':"About DeepFaune", 'it':"A proposito"}
menu_def = [
    ['&'+txt_file[LANG], [
        '&'+txt_import[LANG],[txt_importimage[LANG],txt_importvideo[LANG]],
        '!'+txt_export[LANG],[txt_ascsv[LANG],txt_asxlsx[LANG]],
        '!'+txt_createsubfolders[LANG], [txt_copy[LANG],txt_move[LANG]]
    ]],
    ['!'+txt_pref[LANG], [
        txt_language[LANG], ['fr', 'gb', 'it']
    ]],
    ['&'+txt_help[LANG], [
        '&Version', [VERSION],
        '&'+txt_credits[LANG]
    ]]
]

layout = [
    [
        StyledMenu(menu_def, text_color=text_color, background_color=background_color, text_font=FONT_NORMAL, key='-MENUBAR-')
    ],
    [
        [sg.Frame('',[
            [
                sg.Column([
                    [sg.Table(values=[], font=FONT_NORMAL,
                              headings=[txt_filename[LANG]], justification = "l", 
                              vertical_scroll_only=False, auto_size_columns=False, col_widths=[20], expand_y=True,
                              enable_events=True, select_mode = sg.TABLE_SELECT_MODE_BROWSE,
                              background_color=background_color, text_color=text_color,
                              key='-TAB-')],
                    [
                        sg.Combo(values=[txt_all[LANG]]+sorted_txt_classes_lang+[txt_undefined[LANG],txt_empty[LANG]], background_color=background_color, text_color=text_color, enable_events=True,
                                 default_value=txt_all[LANG], size=(12, 1), bind_return_key=False, key='-RESTRICT-'),
                        sg.Button(key='-PREVIOUS-', image_data=PREVIOUS_BUTTON_IMG, button_color=(background_color,background_color), tooltip='previous track'),
                        sg.Button(key='-NEXT-', image_data=NEXT_BUTTON_IMG, button_color=(background_color,background_color), tooltip='next track')
                     ]
                ], background_color=background_color, expand_y=True),
                sg.Column([ 
                    [sg.Frame('',
                              [[sg.Image(filename=r'icons/1316-black-large-933x700.png', key='-IMAGE-', size=(933, 700), background_color=background_color)]]
                              , background_color=background_color)
                     ],
                    [sg.Text(txt_prediction[LANG]+':', background_color=background_color, text_color=text_color, size=(10, 1)),
                     sg.Combo(values=list(sorted_txt_classes_lang+[txt_empty[LANG]]+[txt_other[LANG]]), default_value="", enable_events=True,
                              background_color=background_color, text_color=text_color, size=(15, 1), bind_return_key=False, key='-PREDICTION-'),
                     sg.Text("\tScore: 0.0", background_color=background_color, text_color=text_color, key='-SCORE-'),
                     sg.Text("\t"+txt_count[LANG]+": NA", background_color=background_color, text_color=text_color, key='-COUNT-'),
                     sg.Text("", background_color=background_color, text_color=text_color, key='-SEQNUM-')]
                     #sg.Text("\t"+txt_seqnum[LANG]+": NA", background_color=background_color, text_color=text_color, key='-SEQNUM-')] not OK if media are videos
                ], background_color=background_color)
            ]
        ], background_color=background_color, expand_y=True)]
    ],
    [
        sg.Frame('',[
            [
                StyledButton(txt_configrun[LANG], accent_color, "gray", background_color, key='-CONFIG-', button_width=8+len(txt_configrun[LANG]), pad=(5, (7, 5))),
                sg.ProgressBar(1, orientation='h', border_width=1, expand_x=True, key='-PROGBAR-', bar_color=accent_color), sg.Text("00:00:00", background_color=background_color, text_color=text_color, key='-RTIME-')
            ],
        ], expand_x=True, background_color=background_color)
    ]
]

window = sg.Window("DeepFaune - CNRS",layout, margins=(0,0),
                   font = FONT_MED,
                   resizable=True, background_color=background_color).Finalize()
window.read(timeout=0)
window['-PREDICTION-'].Update(disabled=True)
window['-RESTRICT-'].Update(disabled=True)

from tkinter import TclError
from contextlib import suppress
with suppress(TclError):
    window.TKroot.tk.call('source', SUN_VALLEY_TCL)
window.TKroot.tk.call('set_theme', SUN_VALLEY_THEME)


####################################################################################
### GUI UTILS (after it is created)
####################################################################################
def updateMenuExport(disabled):
    if disabled == True:
        menu_def[0][1][2] = '!'+txt_export[LANG]
    else:
        menu_def[0][1][2] = '&'+txt_export[LANG]
    window[txt_file[LANG]].Update(menu_def[0])

def updateMenuSubfolders(disabled):
    if disabled == True:
        menu_def[0][1][4] = '!'+txt_createsubfolders[LANG]
    else:
        menu_def[0][1][4] = '&'+txt_createsubfolders[LANG]
    window[txt_file[LANG]].Update(menu_def[0])

def updateCurridxPrediction(disabled):
    if disabled is True:
        window['-PREDICTION-'].Update(value="")
        window['-PREDICTION-'].Update(disabled=True)
        window['-SCORE-'].Update("\tScore: 0.0")
        window['-COUNT-'].Update("\t"+txt_count[LANG]+": NA")
        if VIDEO:
            window['-SEQNUM-'].Update("")            
        else:
            window['-SEQNUM-'].Update("\t"+txt_seqnum[LANG]+": NA")
    else:
        pass
    
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
import time
from collections import deque
from statistics import mean

curridx = -1 # current filenames index
rowidx = -1 # current tab row index
updatecurridxrequired = False # do we need to refresh the prediction info for curridx
testdir = None
thread = None
predictorready = False
imgmoved  = False
batchduration = deque(maxlen=20)

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
        newtestdir = dialog_get_dir(txt_browse[LANG]) # we keep the previous testdir, if not None
        if newtestdir != None:
            testdir = newtestdir
            if event == txt_importimage[LANG]:
                VIDEO = False
            if event == txt_importvideo[LANG]:
                    VIDEO = True
            predictorready = False
            curridx = -1
            window['-RTIME-'].Update("00:00:00")
            window['-PROGBAR-'].update_bar(0)
            window['-IMAGE-'].update(filename=r'icons/1316-black-large-933x700.png', size=(933, 700))
            window['-RESTRICT-'].Update(value=txt_all[LANG], disabled=True)
            updateCurridxPrediction(disabled=True)
            updateMenuExport(disabled=True)
            updateMenuSubfolders(disabled=True)
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
                testdir = None
                window['-TAB-'].Update(values=[[]])
                window['-CONFIG-'].Update(button_color=("gray", background_color))
                dialog_error(txt_incorrect[LANG])
            else:
                curridx = 0
                rowidx = 0
                subsetidx = list(range(0,len(filenames)))
                window['-TAB-'].Update(values=[[basename(f)] for f in filenames])
                window['-TAB-'].Update(row_colors=tuple((k,text_color,background_color)
                                                        for k in range(0, 1))) # bug, first row color need to be hard reset
                window['-TAB-'].update(select_rows=[curridx])
                window['-CONFIG-'].Update(button_color=(background_color, background_color))
    elif event == '-CONFIG-' and testdir is not None and thread is None:
        #########################
        ## CONFIGURE
        #########################
        import copy
        if VIDEO:
            sequencespin = []
        else:
            sequencespin = [sg.Text(txt_sequencemaxlag[LANG]+'\t', expand_x=True, background_color=background_color, text_color=text_color),
                            sg.Spin(values=[i for i in range(0, 60)], initial_value=maxlag_default, size=(4, 1), change_submits=True, enable_events=True, key='-LAG-', background_color=background_color, text_color=text_color)]
        layoutconfig = [
            [sg.Frame(txt_selectclasses[LANG], listCB, font=FONT_NORMAL, expand_x=True, expand_y=True,
                      background_color=background_color)],
            [sg.Frame(txt_paramframe[LANG], font=FONT_MED, expand_x=True, expand_y=True, layout=[
                [sg.Text(txt_confidence[LANG]+'\t', expand_x=True, background_color=background_color, text_color=text_color),
                 sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), change_submits=True, enable_events=True,
                         background_color=background_color, text_color=text_color, key='-THRESHOLD-')],
                sequencespin
            ], background_color=background_color)],
            [
                StyledButton(txt_run[LANG], accent_color, background_color, background_color, button_width=8+len(txt_run[LANG]), key='-RUN-')
            ]
        ]
        windowconfig = sg.Window(txt_configrun[LANG], copy.deepcopy(layoutconfig),  
                                 font = FONT_MED, margins=(0, 0),
                                 background_color=background_color, finalize=True)
        with suppress(TclError):
            windowconfig.TKroot.tk.call('source', SUN_VALLEY_TCL)
        windowconfig.TKroot.tk.call('set_theme', SUN_VALLEY_THEME)
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
        ## RUN
        ########################
        if not configabort:            
            if VIDEO:
                from predictTools import PredictorVideo
                BATCH_SIZE = 12 # Batch size for predictor, in number of images
            else:
                from predictTools import Predictor
                BATCH_SIZE = 8
            if VIDEO:
                predictor = PredictorVideo(filenames, threshold, LANG, BATCH_SIZE)
                window['-TAB-'].Update(row_colors=tuple((k,text_color,background_color)
                                                        for k in range(0, nbfiles))) # color reset is required
            else:
                if len(filenames)>1000:
                    popup_win = popup(txt_loadingmetadata[LANG])
                predictor = Predictor(filenames, threshold, maxlag, LANG, BATCH_SIZE)                
                if len(filenames)>1000:
                    popup_win.close()
                filenames = predictor.getFilenames()
                seqnums = predictor.getSeqnums()
                window.Element('-TAB-').Update(values=[[basename(f)] for f in filenames]) # color reset is induced
            curridx = 0
            rowidx = 0
            batchduration = deque(maxlen=20)
            window['-TAB-'].update(select_rows=[curridx])
            predictor.setForbiddenClasses(forbiddenclasses)
            def runPredictor():
                global window, nbfiles, BATCH_SIZE, VIDEO, updatecurridxrequired 
                if VIDEO:
                    while True:
                        start = time.time()
                        batch, k1, k2 = predictor.nextBatch()
                        end = time.time()
                        batchduration.append(end-start)
                        if k1==nbfiles: break
                        window['-RTIME-'].Update(time.strftime("%H:%M:%S",
                                                                 time.gmtime(mean(batchduration)*(nbfiles-batch))))
                        window['-PROGBAR-'].update_bar(batch/nbfiles)
                        window['-TAB-'].Update(row_colors = tuple((k,accent_color,background_color)
                                                                  for k in range(k1, k2)))
                        if curridx>=k1 and curridx<k2: # current video must be refreshed
                            updatecurridxrequired = True
                else:
                    while True:
                        start = time.time()
                        batch, k1, k2, k1seq_batch, k2seq_batch = predictor.nextBatch()
                        end = time.time()
                        batchduration.append(end-start)
                        if k1==nbfiles: break
                        window['-RTIME-'].Update(time.strftime("%H:%M:%S",
                                                                 time.gmtime(mean(batchduration)*(1+int(nbfiles/BATCH_SIZE)-batch))))
                        window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)     
                        window['-TAB-'].Update(row_colors=tuple((k,accent_color,background_color)
                                                                for k in range(k1seq_batch, k2seq_batch)))
                        if curridx>=k1seq_batch and curridx<k2seq_batch: # current image must be refreshed
                            updatecurridxrequired = True
            thread = threading.Thread(target=runPredictor)
            thread.daemon = True
            thread.start() 
            predictorready = True
            window['-CONFIG-'].Update(button_color=("gray", background_color))
    elif event == txt_ascsv[LANG] or event == txt_asxlsx[LANG]:
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
         and (event == '-TAB-' and len(values['-TAB-'])>0) \
         and (len(subsetidx)>0):
        #########################
        ## SHOW SELECTED MEDIA
        ## AND ITS PREDICTION
        #########################
        rowidx = values['-TAB-'][0]       
        curridx = subsetidx[rowidx]
        if not imgmoved: 
            if VIDEO:
                cap = cv2.VideoCapture(filenames[curridx])
                lag = int(cap.get(5) / 3)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if predictorready:           
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
                    imagecv = cv2.imdecode(np.fromfile(filenames[curridx], dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                except:
                    imagecv = None
            if imagecv is None:
                imagecv = np.zeros((700,933,3), np.uint8)
            else:
                if predictorready:
                    predictedclass_curridx, predictedscore_curridx, predictedbox_curridx, count_curridx = predictor.getPredictions(curridx)
                    window['-PREDICTION-'].update(value=predictedclass_curridx)
                    window['-PREDICTION-'].Update(disabled=False)
                    window['-SCORE-'].Update("\tScore: "+str(predictedscore_curridx))
                    window['-COUNT-'].Update("\t"+txt_count[LANG]+": "+str(count_curridx))
                    if not VIDEO:
                        window['-SEQNUM-'].Update("\t"+txt_seqnum[LANG]+": "+str(seqnums[curridx]))
                    if predictedclass_curridx is not txt_empty[LANG]:
                        draw_boxes(imagecv,predictedbox_curridx)
                imagecv = cv2.resize(imagecv, (933,700))
            is_success, png_buffer = cv2.imencode(".png", imagecv)
            bio = BytesIO(png_buffer)
            window['-IMAGE-'].update(data=bio.getvalue())
    elif updatecurridxrequired == True \
         and event != '-TAB-' and event != '-PREVIOUS-' and event != '-NEXT-':
        #########################
        ## UPDATING PREDICTION FOR CURRENT MEDIA
        #########################
        rowidx = values['-TAB-'][0]
        # touching position in Table, will send an event
        window['-TAB-'].update(select_rows=[rowidx])
        updatecurridxrequired = False
    elif (testdir is not None) \
         and (event == '-PREVIOUS-' or event == '-NEXT-') \
         and (len(subsetidx)>0):
        #########################
        ## NEXT/PREVIOUS MEDIA
        #########################
        rowidx = values['-TAB-'][0]
        if event == '-NEXT-':
            rowidx = rowidx+1
            if rowidx==len(subsetidx):
                rowidx = 0
        if event == '-PREVIOUS-':
            rowidx = rowidx-1
            if rowidx==-1:
                rowidx = len(subsetidx)-1
        curridx = subsetidx[rowidx]
        # updating position in Table, will send an event
        window['-TAB-'].update(select_rows=[rowidx])
        window['-TAB-'].Widget.see(rowidx+1)
    elif event == txt_copy[LANG] or event == txt_move[LANG]:
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
        destdir = None
        if event == txt_copy[LANG]:
            destdir = dialog_get_dir(txt_destcopy[LANG], initialdir=testdir)
            if destdir is not None:
                frgbprint("Copie vers "+join(destdir,"deepfaune_"+now), "Copying to "+join(destdir,"deepfaune_"+now))
        if event == txt_move[LANG]:
            destdir = dialog_get_dir(txt_destmove[LANG], initialdir=testdir)
            if destdir is not None:
                frgbprint("Déplacement vers "+join(destdir,"deepfaune_"+now), "Moving to "+join(destdir,"deepfaune_"+now))
                imgmoved = True
        if destdir is not None:
            import shutil
            predictedclass, predictedscore, _, _ = predictor.getPredictions()
            mkdir(join(destdir,"deepfaune_"+now))
            for subfolder in set(predictedclass):
                mkdir(join(destdir,"deepfaune_"+now,subfolder))
            if event == txt_copy[LANG]:
                for k in range(nbfiles):
                    shutil.copyfile(filenames[k], unique_new_filename(destdir, now, predictedclass[k], basename(filenames[k])))
            if event == txt_move[LANG]:
                for k in range(nbfiles):
                    shutil.move(filenames[k], unique_new_filename(destdir, now, predictedclass[k], basename(filenames[k])))
    elif event == '-PREDICTION-':
        #########################
        ## CORRECTING PREDICTION
        #########################
        # color activated when possible to use keyboard on this element
        if predictorready:
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
            window.Element('-TAB-').Update(values=[[basename(f)] for f in [filenames[k] for k in subsetidx]])
            window['-TAB-'].update(select_rows=[0])
        else:
            dialog_error(txt_classnotfound[LANG])
            window.Element('-TAB-').Update(values=[])
            window['-IMAGE-'].update(filename=r'icons/1316-black-large-933x700.png', size=(933, 700))
            updateCurridxPrediction(disabled=True)
            dialog_error(txt_classnotfound[LANG])
        curridx = 0
        rowidx = 0
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
    if thread is not None:
        if thread.is_alive() == False:
            thread = None
            updateMenuExport(disabled=False)
            updateMenuSubfolders(disabled=False) 
            window['-PREDICTION-'].Update(disabled=False)
            window['-RESTRICT-'].Update(disabled=False)      
            window['-CONFIG-'].Update(button_color=(background_color, background_color))
window.close()

