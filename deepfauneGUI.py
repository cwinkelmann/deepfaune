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
import ctypes
import platform
try: # high resolution issue on Windows
    if platform.platform().lower().startswith("windows"):
        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass

####################################################################################
### VERSION
####################################################################################
VERSION = "1.0.0"

####################################################################################
### PARAMETERS
####################################################################################
listlang = ['fr', 'en', 'it', 'de']
import configparser
config = configparser.ConfigParser()
config.read('settings.ini')
try:
    LANG = config.get('General','language')
except configparser.NoOptionError:
    LANG = "fr"
try:
    countactivated = config.getboolean('General','count')
except configparser.NoOptionError:
    countactivated = False
VIDEO = False 
threshold = threshold_default = 0.8
maxlag = maxlag_default = 10 # seconds

####################################################################################
### GUI TEXT
####################################################################################
from predictTools import txt_undefined, txt_empty, txt_classes
txt_other =  {'fr':"autre", 'en':"other",
              'it':"altro", 'de':"andere Klasse"}
txt_browse = {'fr':"Choisir", 'en':"Select",
              'it':"Scegliere", 'de':"Wählen"}
txt_incorrect = {'fr':"Dossier incorrect - aucun media trouvé", 'en':"Incorrect folder - no media found",
                 'it':"File scorretto - media non trovato", 'de':"Falscher Ordner - keine Medien gefunden"}
txt_confidence = {'fr':"Seuil de confiance", 'en':"Confidence threshold",
                  'it':"Livello minimo di affidabilita", 'de':"Konfidenzniveau"}
txt_sequencemaxlag = {'fr':"Durée maximale entre images consécutives\n d'une séquence (secondes)",
                      'en':"Maximum length between consecutive images\n in a sequence (seconds)",
                      'it':"Durata massima tra immagini consecutive\n in una sequenza (secondi)",
                      'de':"Maximale Dauer zwischen aufeinanderfolgenden Bildern\n in einer Sequenz (Sekunden)"}
txt_configrun = {'fr':"Configurer et lancer", 'en':"Configure & Run",
                 'it':"Configurare e inviare", 'de':"Konfigurieren und starten"}
txt_run = {'fr':"Lancer", 'en':"Run",
           'it':"Inviare", 'de':"Starten"}
txt_paramframe = {'fr':"Paramètres", 'en':"Parameters",
                  'it':"Parametri", 'de':"Parameter"}
txt_selectclasses = {'fr':"Sélection des classes", 'en':"Classes selection",
                     'it':"Selezione delle classi", 'de':"Auswahl der Klassen"}
txt_all = {'fr':"toutes", 'en':"all",
           'it':"tutte", 'de':"Alles"}
txt_classnotfound = {'fr':"Aucun média pour cette classe", 'en':"No media found for this class",
                     'it':"Nessun media per questa classe", 'de':"Keine Medien für diese Klasse gefunden"}
txt_filename = {'fr':"Nom de fichier", 'en':"Filename",
                'it':"Nome del file", 'de':"Dateiname"}
txt_prediction = {'fr':"Prédiction", 'en':"Prediction",
                  'it':"Predizione", 'de':"Vorhersage"}
txt_count = {'fr':"Comptage", 'en':"Count",
             'it':"Conto", 'de':"Zählung"}
txt_seqnum = {'fr':"Numéro de séquence", 'en':"Sequence ID",
              'it':"Sequenza ID", 'de':"Sequenz ID"}
txt_error = {'fr':"Erreur", 'en':"Error",
             'it':"Errore", 'de':"Fehler"}
txt_errorclass = {'fr':"erreur", 'en':"error",
                  'it':"errore", 'de':"Fehler"}
txt_fileerror = {'fr':"Fichier illisible", 'en':"Unreadable file",
                 'it':"File illeggibile", 'de':"Unlesbare Datei"}
txt_savepredictions = {'fr':"Voulez-vous enregistrer les prédictions dans ", 'en':"Do you want to save predictions in ",
                       'it':"Volete registrare le predizioni nel ", 'de':"Möchten Sie Vorhersagen speichern"}
txt_destcopy = {'fr':"Copier dans des sous-dossiers de", 'en':"Copy in subfolders of",
                'it':"Copiare nei sotto file di", 'de':"In Unterordner Kopieren"}
txt_destmove = {'fr':"Déplacer vers des sous-dossiers de", 'en':"Move to subfolders of",
                'it':"Spostare nei sotto file di", 'de':"In Unterordner Verschieben"}
txt_loadingmetadata = {'fr':"Chargement des metadonnées... (cela peut prendre du temps)", 'en':"Loading metadata... (this may take a while)",
                       'it':"Carica dei metadata... (puo essere lungo)", 'de':"Laden der Metadaten... (dies kann eine Weile dauern)"}
txt_restart = {'fr':"Redémarrage nécessaire pour changer la langue. Arréter le logiciel ?",
               'en':"Restart required to change the language. Stopping the software?",
               'it':"Per cambiare la lingua è necessario un riavvio. Arresto del software ?",
               'de':"Neustart erforderlich, um die Sprache zu ändern. Wollen Sie die Software stoppen?"}

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
def debugprint(txt_fr, txt_en, end='\n'):
    if LANG=="fr":
        print(txt_fr, end=end)
    else:
        print(txt_en, end=end)

def draw_boxes(imagecv, box=None):
    if box is not None:
        if np.count_nonzero(box)>0: # is not default empty box
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
    btn_img.thumbnail((btn_w // 3, height // 3))
    btn_img.save(data, format='png', quality=100)
    btn_img = base64.b64encode(data.getvalue())
    return sg.Button(button_text=button_text, image_data=btn_img,
                     button_color=(text_color, background_color), mouseover_colors=(text_color, background_color),
                     tooltip=tooltip, key=key, pad=pad, enable_events=True, size=(button_width, 1),
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
select_frame = sg.Frame(txt_selectclasses[LANG], listCB, font=FONT_NORMAL, expand_x=True, expand_y=True,
                        background_color=background_color) # required here to avoid element reuse (not accepted) 

# Main window
txt_file = {'fr':"Fichier", 'en':"File",
            'it':"File", 'de':"Datei"}
txt_pref = {'fr':"Préférences", 'en':"Preferences",
            'it':"Preferenze", 'de':"Präferenzen"}
txt_help = {'fr':"Aide", 'en':"Help",
            'it':"Aiuto", 'de':"Hilfe"}
txt_import = {'fr':"Importer", 'en':"Import",
              'it':"Caricare", 'de':"Importieren"}
txt_importimage = {'fr':"Images", 'en':"Images",
                   'it':"Immagine", 'de':"Bilder"}
txt_importvideo = {'fr':"Vidéos", 'en':"Videos",
                   'it':"Video", 'de':"Videos"}
txt_export = {'fr':"Exporter les résultats", 'en':"Export results",
              'it':"Esportare i risultati", 'de':"Resultate exportieren"}
txt_ascsv = {'fr':"Format CSV", 'en':"As CSV",
             'it':"Formato CSV", 'de':"Als CSV"}
txt_asxlsx = {'fr':"Format XSLX", 'en':"As XSLX",
              'it':"Formato XSLX", 'de':"Als XLSX"}
txt_createsubfolders = {'fr':"Créer des sous-dossiers", 'en':"Create subfolders",
                        'it':"Creare dei sotto file", 'de':"Unterordner erstellen"}
txt_copy = {'fr':"Copier les fichiers", 'en':"Copy files",
            'it':"Copiare i file", 'de':"Dateien kopieren"}
txt_move = {'fr':"Déplacer les fichiers", 'en':"Move files",
            'it':"Spostare i file", 'de':"Dateien verschieben"}
txt_language = {'fr':"Langue", 'en':"Language",
                'it':"Lingua", 'de':"Sprache"}
txt_activatecount = {'fr':"Activer le comptage (expérimental)", 'en':"Activate count (experimental)",
                     'it':"Attivare il conto (sperimentale)", 'de':"Zählung aktivieren (experimentell)"}
txt_deactivatecount = {'fr':"Désactiver le comptage (expérimental)", 'en':"Deactivate count (experimental)",
                       'it':"Disattivare il conto (sperimentale)", 'de':"Zählung desaktivieren (experimentell)"}
txt_credits = {'fr':"A propos", 'en':"About DeepFaune",
               'it':"A proposito", 'de':"Über DeepFaune"}
if countactivated:
    txt_statuscount = txt_deactivatecount[LANG]
else:
    txt_statuscount = txt_activatecount[LANG]
    
menu_def = [
    ['&'+txt_file[LANG], [
        '&'+txt_import[LANG],[txt_importimage[LANG],txt_importvideo[LANG]],
        '!'+txt_export[LANG],[txt_ascsv[LANG],txt_asxlsx[LANG]],
        '!'+txt_createsubfolders[LANG], [txt_copy[LANG],txt_move[LANG]]
    ]],
    ['&'+txt_pref[LANG], [
        txt_language[LANG], listlang,
        txt_statuscount
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
                        sg.Combo(values=[txt_all[LANG]]+sorted_txt_classes_lang+[txt_undefined[LANG],txt_empty[LANG]],
                                 background_color=background_color, text_color=text_color, enable_events=True,
                                 default_value=txt_all[LANG], size=(12, 1), bind_return_key=False, key='-RESTRICT-'),
                        sg.Button(key='-PREVIOUS-', image_data=PREVIOUS_BUTTON_IMG, button_color=(background_color,background_color), tooltip=None),
                        sg.Button(key='-NEXT-', image_data=NEXT_BUTTON_IMG, button_color=(background_color,background_color), tooltip=None)
                     ]
                ], background_color=background_color, expand_y=True),
                sg.Column([ 
                    [sg.Frame('',
                              [[sg.Image(filename=r'icons/1316-black-large-933x700.png', key='-IMAGE-', size=(933, 700), background_color=background_color)]]
                              , background_color=background_color)
                     ],
                    [sg.Text(txt_prediction[LANG]+':', background_color=background_color, text_color=text_color, size=(10, 1)),
                     sg.Combo(values=list(sorted_txt_classes_lang+[txt_undefined[LANG],txt_other[LANG],txt_empty[LANG]]),
                              default_value="", enable_events=True,
                              background_color=background_color, text_color=text_color, size=(15, 1), bind_return_key=True, key='-PREDICTION-'),
                     sg.Text("   Score: 0.0", background_color=background_color, text_color=text_color, key='-SCORE-'),
                     sg.Text("", background_color=background_color, text_color=text_color, key='-SEQNUM-'),
                     sg.Text("\t"+txt_count[LANG]+":", background_color=background_color, text_color=text_color, visible=countactivated, key='-COUNT-'),
                     sg.Input(default_text="0", size=(2, 1), enable_events=True, key='-COUNTER-', background_color=background_color, text_color=text_color, visible=countactivated,
                              disabled_readonly_background_color=background_color, disabled_readonly_text_color=text_color)] # not used if media are videos
                ], background_color=background_color, expand_x=True)
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
window['-COUNTER-'].Update(disabled=True)
window['-COUNTER-'].bind("<Return>", "_Enter") # to generate an event only after return key
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

def updateMenuActivateCount():
    if menu_def[1][1][2] == txt_activatecount[LANG]:
        menu_def[1][1][2] = txt_deactivatecount[LANG]
    else:
        menu_def[1][1][2] = txt_activatecount[LANG]
    window[txt_pref[LANG]].Update(menu_def[1])
            
def updatePredictionInfo(disabled):
    if disabled is True:
        window['-PREDICTION-'].Update(value="")
        window['-PREDICTION-'].Update(disabled=True)
        window['-SCORE-'].Update("   Score: 0.0")
        if countactivated:
            window['-COUNTER-'].Update(value=0)
            window['-COUNTER-'].Update(disabled=True)
        if VIDEO:
            window['-SEQNUM-'].Update("")
        else:
            window['-SEQNUM-'].Update("\t"+txt_seqnum[LANG]+": NA")
    else:
        window['-PREDICTION-'].Update(disabled=False)
        if countactivated:
            window['-COUNTER-'].Update(disabled=False)
    
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
txt_new_classes_lang = []

while True:
    event, values = window.read(timeout=10)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event in listlang:
        config.set('General', 'language', event)
        if event != LANG:
            with open("settings.ini", "w") as inif:
                config.write(inif)
            yesorno = dialog_yesno(txt_restart[LANG])
            if yesorno == 'yes':
                break
    elif event == txt_activatecount[LANG]:
        #########################
        ## (DE)ACTIVATING COUNT
        #########################
        countactivated = True
        if predictorready and len(subsetidx)>0:
            _, _, _, count_curridx = predictor.getPredictions(curridx)
            window['-COUNTER-'].Update(value=count_curridx)
        else:
            window['-COUNTER-'].Update(value=0)
        window['-COUNT-'].Update(visible=True)
        window['-COUNTER-'].Update(visible=True)
        config.set('General', 'count', 'True')
        with open("settings.ini", "w") as inif:
            config.write(inif)
        updateMenuActivateCount()
    elif event == txt_deactivatecount[LANG]:
        countactivated = False
        window['-COUNT-'].Update(visible=False)
        window['-COUNTER-'].Update(visible=False)
        config.set('General', 'count', 'False')
        with open("settings.ini", "w") as inif:
            config.write(inif)
        updateMenuActivateCount()
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
                BATCH_SIZE = 8
            if event == txt_importvideo[LANG]:
                VIDEO = True
                BATCH_SIZE = 12
            predictorready = False
            curridx = -1
            window['-RTIME-'].Update("00:00:00")
            window['-PROGBAR-'].update_bar(0)
            window['-IMAGE-'].update(filename=r'icons/1316-black-large-933x700.png', size=(933, 700))
            window['-RESTRICT-'].Update(value=txt_all[LANG], disabled=True)
            updatePredictionInfo(disabled=True)
            updateMenuExport(disabled=True)
            updateMenuSubfolders(disabled=True)
            debugprint("Dossier sélectionné : "+testdir, "Selected folder: "+testdir)
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
                debugprint("Nombre de vidéos : "+str(nbfiles), "Number of videos: "+str(nbfiles))
            else:
                debugprint("Nombre d'images : "+str(nbfiles), "Number of images: "+str(nbfiles))
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
                window['-TAB-'].update(select_rows=[0])
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
                            sg.Spin(values=[i for i in range(0, 60)], initial_value=maxlag_default, size=(4, 1), enable_events=True, key='-LAG-', background_color=background_color, text_color=text_color)]
        layoutconfig = [
            [select_frame],
            [sg.Frame(txt_paramframe[LANG], font=FONT_MED, expand_x=True, expand_y=True, layout=[
                [sg.Text(txt_confidence[LANG]+'\t', expand_x=True, background_color=background_color, text_color=text_color),
                 sg.Spin(values=[i/100. for i in range(25, 100)], initial_value=threshold_default, size=(4, 1), enable_events=True,
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
                debugprint("Classes non selectionnées : ", "Unselected classes: ", end="")
                print(forbiddenclasses)
        ########################
        ## RUN
        ########################
        if not configabort:            
            if VIDEO:
                from predictTools import PredictorVideo
            else:
                from predictTools import PredictorImage
            if VIDEO:
                predictor = PredictorVideo(filenames, threshold, LANG, BATCH_SIZE)
                window['-TAB-'].Update(row_colors=tuple((k,text_color,background_color)
                                                        for k in range(0, nbfiles))) # color reset is required
            else:
                if len(filenames)>1000:
                    popup_win = popup(txt_loadingmetadata[LANG])
                predictor = PredictorImage(filenames, threshold, maxlag, LANG, BATCH_SIZE)
                if len(filenames)>1000:
                    popup_win.close()
                filenames = predictor.getFilenames()
                seqnums = predictor.getSeqnums()
                window.Element('-TAB-').Update(values=[[basename(f)] for f in filenames]) # color reset is induced
            curridx = 0
            rowidx = 0
            subsetidx = list(range(0,len(filenames)))
            batchduration = deque(maxlen=20)
            window['-TAB-'].update(select_rows=[0])
            window['-PREDICTION-'].Update(disabled=True)
            window['-COUNTER-'].Update(disabled=True)
            window['-RESTRICT-'].Update(value=txt_all[LANG], disabled=True)
            predictor.setForbiddenClasses(forbiddenclasses)
            ###
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
                window['-RTIME-'].Update("00:00:00")
            ###
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
        if countactivated:
            preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                    'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                    'prediction':predictedclass, 'score':predictedscore,
                                    'count':count})
        else:
            preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                    'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                    'prediction':predictedclass, 'score':predictedscore})
        preddf.sort_values(['seqnum','filename'], inplace=True)
        if event == txt_ascsv[LANG]:
            csvpath =  dialog_get_file(txt_savepredictions[LANG], initialdir=testdir, initialfile="deepfaune.csv", defaultextension=".csv")
            if csvpath:
                debugprint("Enregistrement dans "+csvpath, "Saving to "+csvpath)
                preddf.to_csv(csvpath, index=False)
        if event == txt_asxlsx[LANG]:
            xlsxpath =  dialog_get_file(txt_savepredictions[LANG], initialdir=testdir, initialfile="deepfaune.xlsx", defaultextension=".xlsx")
            if xlsxpath:
                debugprint("Enregistrement dans "+xlsxpath, "Saving to "+xlsxpath)
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
                videocap = cv2.VideoCapture(filenames[curridx])
                total_frames = int(videocap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(videocap.get(5))
                lag = int(fps/3) # lag between two successive frames
                while ((BATCH_SIZE - 1) * lag > total_frames):
                    lag = lag - 1 
                if predictorready:
                    kframe = predictor.getKeyFrames(curridx)*lag # possibly 0 if video not treated by predictor yet
                else:
                    kframe = 0
                videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                ret, imagecv = videocap.read()
                while ret==False and (kframe+lag)<=((BATCH_SIZE-1)*lag): # ignoring corrupted frames (useless when key frame are found by predictor)
                    kframe = kframe+lag
                    videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                    ret, imagecv = videocap.read()
                videocap.release()
                if not ret:
                    imagecv = None
            else:
                try:
                    imagecv = cv2.imdecode(np.fromfile(filenames[curridx], dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                except:
                    imagecv = None
            if imagecv is None:
                imagecv = np.zeros((700,933,3), np.uint8)
                cv2.putText(imagecv, text=txt_fileerror[LANG], org=(300, 350), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 0, 255),thickness=1)
                if predictorready:
                    predictor.setPredictedClass(curridx, txt_errorclass[LANG], 0.0)
                    window['-PREDICTION-'].update(value=txt_errorclass[LANG])
                    window['-SCORE-'].Update("   Score: 0.0")
                    if countactivated:
                        window['-COUNTER-'].Update(value=0)
            else:
                if predictorready:
                    predictedclass_curridx, predictedscore_curridx, predictedbox_curridx, count_curridx = predictor.getPredictions(curridx)
                    window['-PREDICTION-'].update(value=predictedclass_curridx)
                    window['-SCORE-'].Update("   Score: "+str(predictedscore_curridx))
                    if countactivated:
                        window['-COUNTER-'].Update(value=count_curridx)
                    if predictedclass_curridx is not txt_empty[LANG]:
                        draw_boxes(imagecv,predictedbox_curridx)
                imagecv = cv2.resize(imagecv, (933,700))
            is_success, png_buffer = cv2.imencode(".png", imagecv)
            bio = BytesIO(png_buffer)
            window['-IMAGE-'].update(data=bio.getvalue())
            if predictorready and not VIDEO:
                window['-SEQNUM-'].Update("\t"+txt_seqnum[LANG]+": "+str(seqnums[curridx]))
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
                debugprint("Copie vers "+join(destdir,"deepfaune_"+now), "Copying to "+join(destdir,"deepfaune_"+now))
        if event == txt_move[LANG]:
            destdir = dialog_get_dir(txt_destmove[LANG], initialdir=testdir)
            if destdir is not None:
                debugprint("Déplacement vers "+join(destdir,"deepfaune_"+now), "Moving to "+join(destdir,"deepfaune_"+now))
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
        if predictorready:
            # if predicted empty associated to another class, set count to 1
            if predictor.getPredictedClass(curridx) == txt_empty[LANG]:
                if values['-PREDICTION-'] != txt_empty[LANG]:
                    window['-COUNTER-'].Update(value=1)
                    predictor.setPredictedCount(curridx, 1)
            # if predicted non empty associated to another class, set count to 0
            if values['-PREDICTION-'] == txt_empty[LANG]:
                if predictor.getPredictedClass(curridx) != txt_empty[LANG]:
                    window['-COUNTER-'].Update(value=0)
                    predictor.setPredictedCount(curridx, 0)
            if VIDEO:
                predictor.setPredictedClass(curridx, values['-PREDICTION-'])
            else:
                predictor.setPredictedClassInSequence(curridx, values['-PREDICTION-'])
            window['-PREDICTION-'].Update(select=False)
            window['-SCORE-'].Update("   Score: 1.0")
        # new class proposed by the user ?
        if not values['-PREDICTION-'] in sorted_txt_classes_lang+[txt_undefined[LANG],txt_other[LANG],txt_empty[LANG]]+txt_new_classes_lang:
            txt_new_classes_lang.append(values['-PREDICTION-']) 
            window['-PREDICTION-'].Update(values=sorted(sorted_txt_classes_lang+txt_new_classes_lang)+[txt_undefined[LANG],txt_other[LANG],txt_empty[LANG]],
                                          value=values['-PREDICTION-'])
            valuerestrict = values['-RESTRICT-']
            window['-RESTRICT-'].Update(values=[txt_all[LANG]]+sorted(sorted_txt_classes_lang+txt_new_classes_lang)+[txt_undefined[LANG],txt_empty[LANG]],
                                        value=valuerestrict)
    elif event == '-COUNTER-' + "_Enter":
        if predictorready:
            try:
                newcount = int(values['-COUNTER-'])
                predictor.setPredictedCount(curridx, values['-COUNTER-'])
            except ValueError:
                window['-COUNTER-'].Update(value=count_curridx)
            #window['-COUNTER-'].TKEntry.configure(insertontime=0) # no blinking cursor
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
            updatePredictionInfo(disabled=False)
            window.Element('-TAB-').Update(values=[[basename(f)] for f in [filenames[k] for k in subsetidx]])
            window['-TAB-'].Update(row_colors = tuple((k,accent_color,background_color)
                                                      for k in range(0, len(subsetidx)))) # row in accent_color because prediction is available
            window['-TAB-'].update(select_rows=[0])
        else:
            updatePredictionInfo(disabled=True)
            window.Element('-TAB-').Update(values=[])
            window['-IMAGE-'].update(filename=r'icons/1316-black-large-933x700.png', size=(933, 700))
            dialog_error(txt_classnotfound[LANG])
        curridx = 0
        rowidx = 0
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
    if thread is not None:
        if thread.is_alive() == False:
            #########################
            ## WORK TERMINATED IN THREAD
            #########################
            thread = None
            updateMenuExport(disabled=False)
            updateMenuSubfolders(disabled=False) 
            window['-RESTRICT-'].Update(disabled=False)
            updatePredictionInfo(disabled=False)
            window['-CONFIG-'].Update(button_color=(background_color, background_color))
window.close()

