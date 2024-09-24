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
import cv2
import numpy as np
import threading
import io
import os
import multiprocessing
import urllib
multiprocessing.freeze_support()
os.environ["PYTORCH_JIT"] = "0"

####################################################################################
### VERSION
####################################################################################
VERSION = "1.1.0"

####################################################################################
### PARAMETERS
####################################################################################
VIDEO = False # by default
threshold = threshold_default = 0.8
maxlag = maxlag_default = 10 # seconds
listlang = ['fr', 'en', 'it', 'de']

## From settings.ini
import configparser
config = configparser.ConfigParser()

def configget(option, defaultvalue):
    config.read('settings.ini')
    try:
        if defaultvalue  in ['True','False']:
            value = config.getboolean('General',option)
        else:
            value = config.get('General',option)
    except configparser.NoOptionError:
        value = defaultvalue == 'True' if defaultvalue  in ['True','False'] else defaultvalue
    return(value)
            
def configsetsave(option, value):
    config.set('General', option, value)
    with open("settings.ini", "w") as inif:
        config.write(inif)

LANG = configget('language', 'fr')
countactivated = configget('count', 'False')
humanbluractivated = configget('humanblur', 'False')
checkupdate = configget('checkupdate', 'True')        
####################################################################################
### GUI TEXT
####################################################################################
from predictTools import txt_undefined, txt_empty, txt_classes
from classifTools import txt_animalclasses
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
txt_selectclasses = {'fr':"Sélection des classes animales", 'en':"Animal classes selection",
                     'it':"Selezione delle animale classi", 'de':"Auswahl der Animal Klassen"}
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
txt_visitwebsite = {'fr': "Aller sur le site",
                    'en': 'Visit the website',
                    'it': 'Vai al sito web',
                    'de': 'Auf die Website gehen'}
txt_newupdate = {'fr': "Mise à jour du logiciel",
                'en': 'Software update',
                'it': 'Aggiornamento software',
                'de': 'Software-Update'}
txt_newupdatelong = {'fr': "Une nouvelle mise à jour est disponible sur le site",
                     'en': 'A new update is available on the website',
                     'it': 'Un nuovo aggiornamento è disponibile sul sito web',
                     'de': 'Ein neues Update ist auf der Website verfügbar'}
txt_disablecheckupdate = {'fr': "Ne plus me le rappeler",
                          'en': "Do not remind me again",
                          'it': 'Non ricordarmelo più',
                          'de': 'Erinnere mich nicht mehr daran'}
txt_enablecheckupdate = {'fr': "Me le rappeler plus tard",
                         'en': "Remind me later",
                         'it': 'Ricordamelo più tardi',
                         'de': 'Erinnere mich später'}
####################################################################################
### THEME SETTINGS
####################################################################################
from b64_images import *

DEFAULT_THEME = {'accent': '#24a0ed', 'background': '#1c1c1c', 'text': '#d7d7d7', 'alt_background': '#2f2f2f'}
accent_color, text_color, background_color, alt_background = DEFAULT_THEME['accent'], DEFAULT_THEME['text'], DEFAULT_THEME['background'], DEFAULT_THEME['alt_background']

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
            cv2.rectangle(imagecv, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), max(1,imagecv.shape[0]//200))

def blur_boxes(imagecv, boxes=None):
    if boxes is not None:
        for box in boxes:
            if np.count_nonzero(box)>0: # is not default empty box
                ROI = imagecv[int(box[1]):int(box[3]),int(box[0]):int(box[2])]
                blur = cv2.blur(ROI, (151,151)) 
                imagecv[int(box[1]):int(box[3]),int(box[0]):int(box[2])] = blur

def copyfile_blur(src, dst, boxes=None):
    if boxes is None:
        shutil.copyfile(src, dst)
    else:
        imagecv = cv2.imdecode(np.fromfile(src, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        blur_boxes(imagecv, boxes)
        cv2.imwrite(dst, imagecv)

import tkinter
from tkinter import filedialog, messagebox
def dialog_get_dir(title, initialdir=None):
    # rooting to the main PySimpleGUI window
    # does not work here dute to color problems in the dialog box
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
    # rooting to the main PySimpleGUI window
    # does not work here dute to color problems in the dialog box
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
    # rooting to the main PySimpleGUI window
    yesorno = messagebox.askquestion('', message, icon='warning', parent=window.TKroot)
    return yesorno

def dialog_error(message):
    # rooting to the main PySimpleGUI window
    messagebox.showerror(title=txt_error[LANG], message=message, parent=window.TKroot)
    
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
### CHECKING SCREEN SIZE & RESOLUTION FOR IMAGE DISPLAY
####################################################################################
# Image display
from io import BytesIO
def cv2bytes(imagecv, imsize=None):
    if imsize is not None and imsize[0]>0 and imsize[1]>0:
        imagecv_resized = cv2.resize(imagecv, imsize)
    else:
        imagecv_resized = imagecv
    is_success, png_buffer = cv2.imencode(".png", imagecv_resized)
    bio = BytesIO(png_buffer)
    return bio.getvalue()

# Initial logo image
logoimagecv = cv2.imdecode(np.fromfile("icons/1316-black-large-933x700.png", dtype=np.uint8), cv2.IMREAD_UNCHANGED)    
curimagecv = logoimagecv

# Checking screen possibilities and sizing image accordinglyimport ctypes
import platform
DEFAULTIMGSIZE = (width,height) = (933,700)
try:
    if platform.platform().lower().startswith("windows"):
        root = sg.tk.Tk()
        root.attributes("-alpha", 0)
        root.state('zoomed')
        root.update()
        width  = root.winfo_width()
        height = root.winfo_height()
        root.destroy()
    else:
       width, height = sg.Window.get_screen_size() 
except:
    pass


correctedimgsize = (min(DEFAULTIMGSIZE[0],int(width*0.65)),
                    min(DEFAULTIMGSIZE[1],int(width*0.65*DEFAULTIMGSIZE[0]/DEFAULTIMGSIZE[1]), int(height*0.75)))           

curimagecv = cv2.resize(curimagecv, correctedimgsize)

####################################################################################
### MAIN GUI WINDOW
####################################################################################
sorted_txt_classes_lang = sorted(txt_classes[LANG])
sorted_txt_animalclasses_lang = sorted(txt_animalclasses[LANG])
# Default selected classes, ONLY ANIMAL CLASSES
listCB = []
lineCB = []
for k in range(0,len(sorted_txt_animalclasses_lang)):
    lineCB = lineCB+[sg.CB(sorted_txt_animalclasses_lang[k], key=sorted_txt_animalclasses_lang[k], size=(12,1), default=True, background_color=background_color, text_color=text_color)]
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
txt_copywithhumanblur = {'fr':"Copier les fichiers (avec floutage des humains)",
                         'en':"Copy files (with human blurring)",
                         'it':"Copiare i file (con la sfocatura degli umani)",
                         'de':"Dateien kopieren (mit Die Unschärfe von Menschen)"}
txt_language = {'fr':"Langue", 'en':"Language",
                'it':"Lingua", 'de':"Sprache"}
txt_activatecount = {'fr':"Activer le comptage (expérimental)", 'en':"Activate count (experimental)",
                     'it':"Attivare il conto (sperimentale)", 'de':"Zählung aktivieren (experimentell)"}
txt_deactivatecount = {'fr':"Désactiver le comptage (expérimental)", 'en':"Deactivate count (experimental)",
                       'it':"Disattivare il conto (sperimentale)", 'de':"Zählung desaktivieren (experimentell)"}
txt_activatehumanblur = {'fr':"Activer le floutage des humains (images seulement)", 'en':"Activate human blurring (image only)",
                         'it':"Attivare la sfocatura degli umani (solo immagini)", 'de':"Die Unschärfe von Menschen aktivieren (nur die Bilder)"}
txt_deactivatehumanblur = {'fr':"Desactiver le floutage des humains  (images seulement)", 'en':"Deactivate human blurring  (image only)",
                           'it':"Disattivare la sfocatura degli umani (solo immagini)", 'de':"die Unschärfe von Menschen desaktivieren (nur die Bilder)"}
txt_credits = {'fr':"A propos", 'en':"About DeepFaune",
               'it':"A proposito", 'de':"Über DeepFaune"}
if countactivated:
    txt_statuscount = txt_deactivatecount[LANG]
else:
    txt_statuscount = txt_activatecount[LANG]
if humanbluractivated:
    txt_statushumanblur = txt_deactivatehumanblur[LANG]
    txt_subfoldersoptions = [txt_copy[LANG], txt_copywithhumanblur[LANG]]
else:
    txt_statushumanblur = txt_activatehumanblur[LANG]
    txt_subfoldersoptions = [txt_copy[LANG]]
    
menu_def = [
    ['&'+txt_file[LANG], [
        '&'+txt_import[LANG],[txt_importimage[LANG],txt_importvideo[LANG]],
        '!'+txt_export[LANG],[txt_ascsv[LANG],txt_asxlsx[LANG]],
        '!'+txt_createsubfolders[LANG], txt_subfoldersoptions
    ]],
    ['&'+txt_pref[LANG], [
        txt_language[LANG], listlang,
        txt_statuscount,
        '!'+txt_statushumanblur
    ]],
    ['&'+txt_help[LANG], [
        '&Version', [VERSION],
        '&'+txt_credits[LANG]
    ]]
]

# Constants for slider design
SLIDER_WIDTH = 30
SLIDER_HEIGHT = 120
SLIDER_HANDLE_RADIUS = 9

# Function to draw the vertical slider on the Graph
def draw_slider(graph, value):
    graph.erase()
    handle_y = value * SLIDER_HEIGHT
    trough_x = SLIDER_WIDTH / 2
    graph.draw_line((trough_x, 0), (trough_x, SLIDER_HEIGHT), color='#cccccc', width=4)
    graph.draw_circle((trough_x, handle_y), SLIDER_HANDLE_RADIUS, fill_color=accent_color, line_color='#2f8cff')


layout = [
    [
        StyledMenu(menu_def, text_color=text_color, background_color=background_color, text_font=FONT_NORMAL, key='-MENUBAR-')
    ],
    [
        [sg.Frame('',[
            [
                sg.Column([
                    [sg.Table(values=[[]], font=FONT_NORMAL,
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
                              [[sg.Image(cv2bytes(curimagecv), key='-IMAGE-',  background_color=background_color)]]
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
                ], background_color=background_color, expand_x=True),
                sg.Column([
                    [sg.Image(BRIGHTNESS_ICON, background_color=background_color)],
                    [sg.Push(background_color=background_color),
                     sg.Graph(
                         canvas_size=(SLIDER_WIDTH, SLIDER_HEIGHT),
                         graph_bottom_left=(0, 0),
                         graph_top_right=(SLIDER_WIDTH, SLIDER_HEIGHT),
                         key='-GAMMALEVEL-',
                         enable_events=True,
                         drag_submits=True,  # Enable drag events
                         background_color=background_color,
                     )],
                    [sg.Image(MOVIE_ICON, background_color=background_color)],
                    [sg.Button(key='-PLAY-', image_data=PLAY_BUTTON_IMG, button_color=(background_color,background_color), tooltip=None)],
                ], background_color=background_color, expand_y=True)
            ]
        ], background_color=background_color, expand_y=True)]
    ],
    [
        sg.Frame('',[
            [
                StyledButton(txt_configrun[LANG], accent_color, "gray", background_color, key='-CONFIGRUN-', button_width=8+len(txt_configrun[LANG]), pad=(5, (7, 5))),
                sg.ProgressBar(1, orientation='h', border_width=1, expand_x=True, key='-PROGBAR-', bar_color=accent_color), sg.Text("00:00:00", background_color=background_color, text_color=text_color, key='-RTIME-')
            ],
        ], expand_x=True, background_color=background_color)
    ]
]

window = sg.Window("DeepFaune - CNRS",layout, margins=(0,0),
                   font = FONT_MED, location=(0, 0),
                   resizable=True, background_color=background_color).Finalize()
window.read(timeout=0)
window['-PREDICTION-'].Update(disabled=True)
window['-RESTRICT-'].Update(disabled=True)
window['-COUNTER-'].Update(disabled=True)
window['-COUNTER-'].bind("<Return>", "_Enter") # to generate an event only after return key
window.bind('<Configure>', '-CONFIG-') # to generate an event when window is resized
window['-IMAGE-'].bind('<Double-Button-1>' , "DOUBLECLICK-")

slider_graph = window['-GAMMALEVEL-']
slider_value = 0.5
slider_enabled = False
draw_slider(slider_graph, slider_value)

from tkinter import TclError
from contextlib import suppress
with suppress(TclError):
    window.TKroot.tk.call('source', SUN_VALLEY_TCL)
window.TKroot.tk.call('set_theme', SUN_VALLEY_THEME) # if dark, implies -CONFIG- events due to internal additionnal padding

####################################################################################
### GUI UTILS (after it is created)
####################################################################################
def updateMenuImport(disabled):
    if disabled == True:
        menu_def[0][1][0] = '!'+txt_import[LANG]
    else:
        menu_def[0][1][0] = '&'+txt_import[LANG]
    window[txt_file[LANG]].Update(menu_def[0])

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

def updateMenuCount(activated):
    if activated == True:
        menu_def[1][1][2] = txt_deactivatecount[LANG]
    else:
        menu_def[1][1][2] = txt_activatecount[LANG]
    window[txt_pref[LANG]].Update(menu_def[1])
    
def updateMenuHumanBlur(activated):
    if activated == True:
        if not VIDEO:
            menu_def[1][1][3] = txt_deactivatehumanblur[LANG]
            menu_def[0][1][5] = [txt_copy[LANG], txt_copywithhumanblur[LANG]]
        else:
            menu_def[1][1][3] = '!'+txt_deactivatehumanblur[LANG]
            menu_def[0][1][5] = [txt_copy[LANG]]
            
    else:
        if not VIDEO:
            menu_def[1][1][3] = txt_activatehumanblur[LANG]
        else:
            menu_def[1][1][3] = '!'+txt_activatehumanblur[LANG]
        menu_def[0][1][5] = [txt_copy[LANG]]
    window[txt_pref[LANG]].Update(menu_def[1])
    window[txt_file[LANG]].Update(menu_def[0])
            
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


gamma_dict = {
    -4:0.2,
    -3:0.4,
    -2:0.6,
    -1:0.8,
    0: 1.,
    1: 1.5,
    2: 2.,
    3: 2.5,
    4:3.
}
def gammalevel_to_gamma(value):
    return gamma_dict[int(value)]

def gamma_correction(imagecv, gamma):
    if abs(gamma-1.0)<1e-6:
        return imagecv
    # Build a lookup table mapping pixel values [0, 255] to their gamma-corrected values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    # Apply gamma correction using the lookup table
    return cv2.LUT(imagecv, table)

imageOffset = (0,0) # space between the window and the image control itself
def updateImage(newcurimagecv=None, gamma=1.):
    global curimagecv
    if newcurimagecv is not None:
        curimagecv = newcurimagecv
    curimsize = ((window.size[0] - imageOffset[0], window.size[1] - imageOffset[1]))
    window['-IMAGE-'].update(data=cv2bytes(gamma_correction(curimagecv, gamma), curimsize))
 
def resizeImage():
    global curwindowsize
    if window.size[0] != curwindowsize[0] or window.size[1] != curwindowsize[1]:
        updateImage()
    curwindowsize = window.size

####################################################################################
### GUI IN ACTION
####################################################################################
from datetime import datetime
import pandas as pd
from os import mkdir
from os.path import join, basename
from pathlib import Path
import pkgutil
import time
from collections import deque
from statistics import mean
import queue

#########################
## GLOBAL VARIABLES
#########################
## GUI's variables
curridx = -1 # current filenames index
rowidx = -1 # current tab row index
subsetidx = [] # current subset of filenames
testdir = None
thread = None
thread_queue = queue.Queue()
predictorready = False
txt_new_classes_lang = []

## misc variables to allow resizing
configactive = False # checks if a series of config events is in progress
nbconfigseries = 0 # nb of series of config events
curwindowsize = (0,0) # current size before config events

#########################
## ASYNCHRONOUS ACTIONS
#########################
def runPredictor(): # predictor in action in a separate thread
    batchduration = deque(maxlen=20)
    if VIDEO:
        while True:
            start = time.time()
            batch, k1, k2 = predictor.nextBatch()
            end = time.time()
            if k1==nbfiles: # last batch done
                break
            batchduration.append(end-start)
            rtime = time.strftime("%H:%M:%S", time.gmtime(mean(batchduration)*(nbfiles-batch)))
            progbar = batch/nbfiles
            thread_queue.put([rtime, progbar, k1, k2])
    else:
        while True:
            start = time.time()
            batch, k1, k2, k1seq, k2seq = predictor.nextBatch()
            end = time.time()
            if k1==nbfiles:  # last batch done
                break
            batchduration.append(end-start)
            rtime = time.strftime("%H:%M:%S", time.gmtime(mean(batchduration)*(1+int(nbfiles/BATCH_SIZE)-batch)))
            progbar = batch*BATCH_SIZE/nbfiles
            thread_queue.put([rtime, progbar, k1seq, k2seq])
    thread_queue.put(["00:00:00", 1.0, nbfiles, nbfiles])

def updateFromThreadQueue(): # updating GUI using info in thread queue
    global thread, thread_queue
    try:
        rtime, progbar, k1, k2 = thread_queue.get(0)
        window['-RTIME-'].Update(rtime)
        window['-PROGBAR-'].update_bar(progbar)
        window['-TAB-'].Update(row_colors=tuple((k,accent_color,background_color)
                                                for k in range(k1, k2)))
        if curridx>=k1 and curridx<k2: # current media must be refreshed
            rowidx = values['-TAB-'][0]
            # touching position in Table, will send a -TAB- event
            window['-TAB-'].update(select_rows=[rowidx])
    except queue.Empty:
        pass
    if thread is not None:
        ## enabling GUI events when thread has terminated
        if thread.is_alive() == False:
            thread = None
            updateMenuImport(disabled=False)
            updateMenuExport(disabled=False)
            updateMenuSubfolders(disabled=False)
            window['-RESTRICT-'].Update(disabled=False)
            updatePredictionInfo(disabled=False)
            window['-CONFIGRUN-'].Update(button_color=(background_color, background_color))

def playVideoUntilOtherEvent(filename):
    global curimagecv
    previmagecv = curimagecv  
    videocap = cv2.VideoCapture(filename)
    total_frames = int(videocap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames==0:
        framecv = None # corrupted video, considered as empty
        event, values = window.read(timeout=10)
    else:
        play = True
        kframe = 0
        while(play):
            videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
            ret, framecv = videocap.read()
            if ret==True: # uncorrupted frame
                updateImage(framecv, rescale_slider(slider_value))
            kframe = kframe+5
            if kframe>=total_frames:
                kframe = 0
            event, values = window.read(timeout=10)
            updateFromThreadQueue()
            if event != '__TIMEOUT__':
                if event != '-CONFIG-' and event != "-GAMMALEVEL-":
                    play = False
    videocap.release()
    # updating position in Table,
    # such that we focus on the row/file of interest,
    # but will send a -TAB- event
    #if event != '-TAB-':
    #    rowidx = values['-TAB-'][0]
    #    window['-TAB-'].update(select_rows=[rowidx])
    #    window['-TAB-'].Widget.see(rowidx+1)
    updateImage(previmagecv, rescale_slider(slider_value))
    return event, values

def playSequenceUntilOtherEvent(filename):
    global curimagecv
    previmagecv = curimagecv
    play = True
    nbfiles = len(filenames)
    k1 = k2 = curridx
    while predictor.getSeqnums()[curridx]==predictor.getSeqnums()[max(0,k1-1)] and k1>0:
        k1 = k1-1
    while predictor.getSeqnums()[curridx]==predictor.getSeqnums()[min(nbfiles-1,k2+1)] and k2<(nbfiles-1):
        k2 = k2+1
    k = k1
    if k1==k2: # singleton
        event, values = window.read(timeout=10)
        play = False
        return event, values
    while(play):
        event, values = window.read(timeout=10)
        try:
            imagecv = cv2.imdecode(np.fromfile(filenames[k], dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        except:
            imagecv = np.zeros((DEFAULTIMGSIZE[1],DEFAULTIMGSIZE[0],3), np.uint8)
        updateImage(imagecv, rescale_slider(slider_value))
        k = k+1
        if k>k2:
            k = k1
        updateFromThreadQueue()
        if event != '__TIMEOUT__':
            if event != '-CONFIG-' and event != "-GAMMALEVEL-":
                play = False
    updateImage(previmagecv, rescale_slider(slider_value))
    return event, values
   
#########################
## MAIN LOOP
#########################
def rescale_slider(value, min_rescale=-4, max_rescale=4):
    return gamma_dict[int((1-value)*min_rescale + value*max_rescale)]

DEBUG = True

draw_popup_update = False
try:
    online_version = urllib.request.urlopen('https://pbil.univ-lyon1.fr/software/download/deepfaune/.version', timeout=1)
    online_version = online_version.read().decode().replace("\n", "")
except:
    online_version = None

if checkupdate and online_version:
    v_online_parts = list(map(int, online_version.split('.')))
    v_installed_parts = list(map(int, VERSION.split('.')))
    for v_online, v_installed in zip(v_online_parts, v_installed_parts):
        if v_online > v_installed:
            draw_popup_update = True

while True:
    event, values = window.read(timeout=10)
    if event != "__TIMEOUT__" and DEBUG is True:
        print("Step1:",event)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    
    # If the user clicks or drags the slider
    if slider_enabled and event == '-GAMMALEVEL-':  # Detect initial click
        _, mouse_y = values['-GAMMALEVEL-']
        if 0 <= mouse_y <= SLIDER_HEIGHT:
            slider_value = round((mouse_y / SLIDER_HEIGHT), 2)
            draw_slider(slider_graph, slider_value)

    #########################
    ## PLAYING VIDEO ?
    #########################
    if event == '-IMAGE-DOUBLECLICK-' and VIDEO and (len(subsetidx)>0):
        event, values = playVideoUntilOtherEvent(filenames[curridx]) # captures the window event internally
    #########################
    ## PLAYING SEQUENCE ?
    #########################
    if event == '-IMAGE-DOUBLECLICK-' and not VIDEO and (len(subsetidx)>0) and predictorready:
        event, values = playSequenceUntilOtherEvent(filenames[curridx]) # captures the window event internally
        
    if event != "__TIMEOUT__" and DEBUG is True:
        print("Step2:",event)
    #########################
    ## WINDOW RESIZING ?
    #########################
    if event == '-CONFIG-': # respond to window resize event
        configactive = True
    elif event != '-CONFIG-' and configactive == True:
        nbconfigseries = nbconfigseries+1
        configactive = False
        if nbconfigseries>1: # the first config events are internal at starting time, not a resizing event
            resizeImage()
        else:
            curwindowsize = window.size # current size before other config events (resizing or moving)
            imageOffset = (window.size[0] - window['-IMAGE-'].get_size()[0],
                           window.size[1] - window['-IMAGE-'].get_size()[1]) # offset is set after the the first config events
    #########################
    ## CHECK UPDATE
    #########################
    if draw_popup_update:
        layoutupdate = [
            [sg.Text(txt_newupdatelong[LANG] + f" (version {online_version})", expand_x=True, background_color=background_color, text_color=text_color)], 
            [StyledButton(txt_visitwebsite[LANG], accent_color, background_color, background_color,
                          button_width=15+len(txt_visitwebsite[LANG]), key='-UPDATE-'),
            StyledButton(txt_enablecheckupdate[LANG], accent_color, background_color, background_color,
                         button_width=15+len(txt_enablecheckupdate[LANG]), key='-UPDATECHECK-'),
            StyledButton(txt_disablecheckupdate[LANG], accent_color, background_color, background_color,
                         button_width=15+len(txt_disablecheckupdate[LANG]), key='-NOUPDATECHECK-')]]

        windowupdate = sg.Window(txt_newupdate[LANG], layoutupdate,  
                                 font = FONT_MED, margins=(0, 0),
                                 background_color=background_color, finalize=True)
        with suppress(TclError):
            windowupdate.TKroot.tk.call('source', SUN_VALLEY_TCL)
        windowupdate.TKroot.tk.call('set_theme', SUN_VALLEY_THEME) # if dark, implies -CONFIG- events due to internal additionnal padding

        while draw_popup_update:
            eventconfig, valuesconfig = windowupdate.read(timeout=10)
            if eventconfig == '-UPDATE-':
                import webbrowser
                webbrowser.open("https://www.deepfaune.cnrs.fr")
                draw_popup_update = False
            if eventconfig == '-NOUPDATECHECK-':
                configsetsave('checkupdate', 'False')
                draw_popup_update = False
            elif eventconfig in (sg.WIN_CLOSED, 'Exit', '-UPDATECHECK-'):
                draw_popup_update = False
        windowupdate.close()
        window.TKroot.focus_force()

    if event in listlang:
        #########################
        ## SELECTING LANGUAGE
        #########################
        configsetsave('language', event)
        if event != LANG:
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
        configsetsave('count', 'True')
        updateMenuCount(activated=True)
    elif event == txt_deactivatecount[LANG]:
        countactivated = False
        window['-COUNT-'].Update(visible=False)
        window['-COUNTER-'].Update(visible=False)
        configsetsave('count', 'False')
        updateMenuCount(activated=False)
    elif event == txt_activatehumanblur[LANG]:
        #########################
        ## (DE)ACTIVATING HUMAN BLUR
        #########################
        humanbluractivated = True
        configsetsave('humanblur', 'True')
        updateMenuHumanBlur(activated=True)
        # refresh current view; touching position in Table, will send a -TAB- event
        if testdir is not None:
            window['-TAB-'].update(select_rows=[rowidx])
    elif event == txt_deactivatehumanblur[LANG]:
        humanbluractivated = False
        configsetsave('humanblur', 'False')
        updateMenuHumanBlur(activated=False)
        # refresh current view; touching position in Table, will send a -TAB- event
        if testdir is not None:
            window['-TAB-'].update(select_rows=[rowidx])
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
            updateImage(logoimagecv)
            window['-RESTRICT-'].Update(value=txt_all[LANG], disabled=True)
            updatePredictionInfo(disabled=True)
            updateMenuExport(disabled=True)
            updateMenuSubfolders(disabled=True)
            updateMenuHumanBlur(activated=humanbluractivated)
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
                window['-CONFIGRUN-'].Update(button_color=("gray", background_color))
                slider_value = 0.5
                draw_slider(slider_graph, slider_value)
                slider_enabled = False
                dialog_error(txt_incorrect[LANG])
            else:
                curridx = 0
                rowidx = 0
                subsetidx = list(range(0,len(filenames)))
                window['-TAB-'].Update(values=[[basename(f)] for f in filenames])
                window['-TAB-'].Update(row_colors=tuple((k,text_color,background_color)
                                                        for k in range(0, 1))) # bug, first row color need to be hard reset
                window['-TAB-'].update(select_rows=[0])
                window['-CONFIGRUN-'].Update(button_color=(background_color, background_color))
                slider_enabled = True
    elif event == '-CONFIGRUN-' and testdir is not None and thread is None:
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
        windowconfig.TKroot.tk.call('set_theme', SUN_VALLEY_THEME) # if dark, implies -CONFIG- events due to internal additionnal padding

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
            forbiddenanimalclasses = []
            for label in sorted_txt_animalclasses_lang:
                if not valuesconfig[label]:
                    forbiddenanimalclasses += [label]
            if len(forbiddenanimalclasses):
                debugprint("Classes non selectionnées : ", "Unselected classes: ", end="")
                print(forbiddenanimalclasses)
        ########################
        ## RUN
        ########################
        if not configabort: 
            window['-CONFIGRUN-'].Update(button_color=("gray", background_color))
            window['-PROGBAR-'].update_bar(0)
            updateMenuImport(disabled=True)
            window['-PREDICTION-'].Update(disabled=True)
            window['-COUNTER-'].Update(disabled=True)
            window['-RESTRICT-'].Update(value=txt_all[LANG], disabled=True)           
            if VIDEO:
                from predictTools import PredictorVideo
            else:
                from predictTools import PredictorImage
            if VIDEO:
                predictor = PredictorVideo(filenames, threshold, LANG, BATCH_SIZE)
            else:
                if len(filenames)>1000:
                    popup_win = popup(txt_loadingmetadata[LANG])
                predictor = PredictorImage(filenames, threshold, maxlag, LANG, BATCH_SIZE)
                if len(filenames)>1000:
                    popup_win.close()
                seqnums = predictor.getSeqnums()
            filenames = predictor.getFilenames()
            curridx = 0
            rowidx = 0
            subsetidx = list(range(0,len(filenames)))
            window.Element('-TAB-').Update(values=[[basename(f)] for f in filenames]) # color reset is induced
            window['-TAB-'].update(select_rows=[0])
            window['-TAB-'].Update(row_colors=tuple((k,text_color,background_color)
                                                    for k in range(0, 1))) # bug, first row color need to be hard reset
            predictor.setForbiddenAnimalClasses(forbiddenanimalclasses)
            thread = threading.Thread(target=runPredictor)
            thread.daemon = True
            thread.start() 
            predictorready = True
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
                                    'count':count, 'humanpresence':predictor.getHumanPresence()})
        else:
            preddf  = pd.DataFrame({'filename':predictor.getFilenames(), 'date':predictor.getDates(), 'seqnum':predictor.getSeqnums(),
                                    'predictionbase':predictedclass_base, 'scorebase':predictedscore_base,
                                    'prediction':predictedclass, 'score':predictedscore,
                                    'humanpresence':predictor.getHumanPresence()})
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
         and (len(subsetidx)>0) or (event == "-GAMMALEVEL-" and slider_enabled):
        #########################
        ## SHOW SELECTED MEDIA
        ## AND ITS PREDICTION
        #########################
        if event != "-GAMMALEVEL-" and slider_value != 0.5 and event != '-IMAGE-DOUBLECLICK-':
            slider_value = 0.5
            draw_slider(slider_graph, slider_value)
            
        rowidx = values['-TAB-'][0]       
        curridx = subsetidx[rowidx]
        if VIDEO:
            videocap = cv2.VideoCapture(filenames[curridx])
            total_frames = int(videocap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames==0:
                 imagecv = None # corrupted video, considered as empty
            else:
                if predictorready:
                    kframe = predictor.getKeyFrames(curridx) # possibly 0 if video not treated by predictor yet
                else:
                    kframe = 0
                videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                ret, imagecv = videocap.read()
                while ret==False and (kframe+lag)<=((BATCH_SIZE-1)*lag): # ignoring corrupted frames (useless when key frame are found by predictor)
                    kframe = kframe+lag
                    videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                    ret, imagecv = videocap.read()
                if ret==False:
                    imagecv = None                        
            videocap.release()
        else:
            try:
                imagecv = cv2.imdecode(np.fromfile(filenames[curridx], dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            except:
                imagecv = None
        if imagecv is None:
            imagecv = np.zeros((DEFAULTIMGSIZE[1],DEFAULTIMGSIZE[0],3), np.uint8)
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
                if humanbluractivated:
                    if not VIDEO:
                        blur_boxes(imagecv, predictor.getHumanBoxes(filenames[curridx]))
                if predictedclass_curridx is not txt_empty[LANG]:
                    draw_boxes(imagecv, predictedbox_curridx)
        updateImage(imagecv, rescale_slider(slider_value))
        if predictorready and not VIDEO:
            window['-SEQNUM-'].Update("\t"+txt_seqnum[LANG]+": "+str(seqnums[curridx]))
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
    elif event == txt_copy[LANG] or event == txt_copywithhumanblur[LANG]:
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
        if event == txt_copy[LANG] or event == txt_copywithhumanblur[LANG]:
            destdir = dialog_get_dir(txt_destcopy[LANG], initialdir=testdir)
            if destdir is not None:
                debugprint("Copie vers "+join(destdir,"deepfaune_"+now), "Copying to "+join(destdir,"deepfaune_"+now))
        if destdir is not None:
            import shutil
            predictedclass, predictedscore, _, _ = predictor.getPredictions()
            mkdir(join(destdir,"deepfaune_"+now))
            for subfolder in set(predictedclass):
                mkdir(join(destdir,"deepfaune_"+now,subfolder))
            if event == txt_copy[LANG]:
                for k in range(nbfiles):
                    shutil.copyfile(filenames[k], unique_new_filename(destdir, now, predictedclass[k], basename(filenames[k])))
            if event == txt_copywithhumanblur[LANG] and not VIDEO:
                for k in range(nbfiles):
                    copyfile_blur(filenames[k], unique_new_filename(destdir, now, predictedclass[k], basename(filenames[k])),
                                  predictor.getHumanBoxes(filenames[k]))
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
            slider_enabled = True
            window.Element('-TAB-').Update(values=[[basename(f)] for f in [filenames[k] for k in subsetidx]])
            window['-TAB-'].Update(row_colors = tuple((k,accent_color,background_color)
                                                      for k in range(0, len(subsetidx)))) # row in accent_color because prediction is available
            window['-TAB-'].update(select_rows=[0])
        else:
            updatePredictionInfo(disabled=True)
            window.Element('-TAB-').Update(values=[[]])
            slider_enabled = False
            slider_value = 0.5
            draw_slider(slider_graph, slider_value)
            updateImage(logoimagecv)
            dialog_error(txt_classnotfound[LANG])
        curridx = 0
        rowidx = 0
    elif event == sg.TIMEOUT_KEY:
        window.refresh()
    #########################
    ## UPDATING GUI FROM THREAD INFO (thread-safe)
    #########################
    updateFromThreadQueue()
window.close()

