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
import sys
import pandas as pd
import cv2
import numpy as np
import os
import datetime as dt
from io import BytesIO
from pathlib import Path, PurePath
from os.path import basename

testdir = sys.argv[1]
currentdir = os.path.dirname(sys.argv[0])
if currentdir != '': currentdir=currentdir+'/'
df_filename = pd.DataFrame({'filename':sorted(
    [f for f in  Path(testdir).rglob('*.[Jj][Pp][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(testdir).rglob('*.[Jj][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(testdir).rglob('*.[Bb][Mm][Pp]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(testdir).rglob('*.[Tt][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(testdir).rglob('*.[Gg][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(testdir).rglob('*.[Pp][Nn][Gg]') if not f.parents[1].match('*deepfaune_*')]
    )})
nbfiles = df_filename.shape[0]

### SETTINGS
sg.ChangeLookAndFeel('Reddit')
sg.LOOK_AND_FEEL_TABLE["Reddit"]["BORDER"]=0

curridx = 0
layout = [[sg.Image(key="-IMAGE-")],
          [sg.Button('Close', key='-CLOSE-'),
           sg.Button("Previous", key='-PREVIOUS-'),
           sg.Button("OK", bind_return_key=True, key='-OK-'),
           sg.Button("Error", bind_return_key=True, key='-ERROR-')],
           [sg.Text("Image 1/"+str(nbfiles), key='-NUM-')]]
windowimg = sg.Window(basename(df_filename['filename'][curridx]), layout, size=(600, 500), font = ("Arial", 14), finalize=True) 

image = cv2.imread(str(df_filename['filename'][curridx]))

if image is None:
    image = np.zeros((400,400,3), np.uint8)
else:
    image = cv2.resize(image, (400,400))
    
is_success, png_buffer = cv2.imencode(".png", image)
bio = BytesIO(png_buffer)
windowimg["-IMAGE-"].update(data=bio.getvalue())

errors = []

while(True):
    eventimg, valuesimg = windowimg.read(timeout=10)
    
    if eventimg in (sg.WIN_CLOSED, '-CLOSE-'):
        break
    
    if eventimg == '-OK-' or eventimg == '-PREVIOUS-' or eventimg == '-ERROR-':
        if eventimg == '-OK-':
            curridx = curridx+1
            if curridx >= nbfiles:
                curridx = nbfiles - 1
                # in case we clicked error before
                if errors[0] == str(df_filename['filename'][curridx]):
                    del errors[0]
        elif eventimg == '-ERROR-':
            errors.insert(0, str(df_filename['filename'][curridx]))
            curridx = curridx+1
            if curridx >= nbfiles:
                curridx = nbfiles - 1
        else :
            curridx = curridx-1
            if curridx<=-1:
                curridx = 0
            if errors[0] == str(df_filename['filename'][curridx]):
                del errors[0]
                
        image = cv2.imread(str(df_filename['filename'][curridx]))
        if image is None:
            image = np.zeros((400,400,3), np.uint8)
        else:
            image = cv2.resize(image, (400,400))
        is_success, png_buffer = cv2.imencode(".png", image)
        bio = BytesIO(png_buffer)
        windowimg["-IMAGE-"].update(data=bio.getvalue())
        windowimg.TKroot.title(basename(df_filename['filename'][curridx]))
        windowimg.Element("-NUM-").update("Image "+str(curridx+1)+"/"+str(nbfiles))
testdir = PurePath(testdir)
dirname = testdir.parts[-1]
date = str(dt.date.today()).replace('-', '')
time = str(dt.datetime.now()).split(" ")[1].split(".")[0].replace(':', '')
login = os.getlogin()

try:
    os.mkdir(currentdir+"logs")
except:
    pass

log = open(currentdir+"logs/"+dirname+"-"+date+"-"+time+"-"+login+".txt", "a")
for err in errors:
    log.write(err+"\n")
log.close()

windowimg.close()
