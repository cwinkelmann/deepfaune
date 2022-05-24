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
from io import BytesIO
from pathlib import Path
from os.path import basename

testdir = sys.argv[1]
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
           sg.Button("Error", bind_return_key=True, key='-ERROR-')]]
windowimg = sg.Window(basename(df_filename['filename'][curridx]), layout, size=(650, 600), font = ("Arial", 14), finalize=True) 

image = cv2.imread(str(df_filename['filename'][curridx]))

if image is None:
    image = np.zeros((600,500,3), np.uint8)
else:
    image = cv2.resize(image, (600,500))
    
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
                try:
                    errors.remove(str(df_filename['filename'][curridx]))
                except:
                    pass
        elif eventimg == '-ERROR-':
            errors.append(str(df_filename['filename'][curridx]))
            curridx = curridx+1
            if curridx >= nbfiles:
                curridx = nbfiles - 1
        else :
            curridx = curridx-1
            if curridx<=-1:
                curridx = 0
            try:
                errors.remove(str(df_filename['filename'][curridx]))
            except:
                pass
                
        image = cv2.imread(str(df_filename['filename'][curridx]))
        if image is None:
            image = np.zeros((600,500,3), np.uint8)
        else:
            image = cv2.resize(image, (600,500))
        is_success, png_buffer = cv2.imencode(".png", image)
        bio = BytesIO(png_buffer)
        windowimg["-IMAGE-"].update(data=bio.getvalue())
        windowimg.TKroot.title(basename(df_filename['filename'][curridx]))

log = open("log.txt", "a")
for err in errors:
    log.write(err+"\n")
log.close()

windowimg.close()