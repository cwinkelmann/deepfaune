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

import sys
import os
from os.path import join, basename
import cv2

## IMPORT DEEPFAUNE CLASSES
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../') # to add the deepfaune path

from detectTools import DetectorJSON
from fileManager import FileManager

if (len(sys.argv)!=6):
    print("Usage: python json2cropped.py <FILE.JSON> <CROPPEDANIMALPATH> <CROPPEDHUMANPATH> <CROPPEDVEHICLEPATH> <THRESHOLD>")
    exit()
jsonfilename = sys.argv[1]
CROPPEDANIMALPATH = sys.argv[2]
CROPPEDHUMANPATH = sys.argv[3]
CROPPEDVEHICLEPATH = sys.argv[4]
threshold = float(sys.argv[5])


detector = DetectorJSON(jsonfilename, threshold)

prevfilename = ''
kbox = 0
while True:
    try:
        # filenames
        print("toto---------------------------------------------")
        filename  = detector.getCurrentFilename()
        print("tata---------------------------------------------")
        prefix = basename(filename).rsplit(".",1)[0]
        if filename == prevfilename:
            kbox += 1
        else:
            prevfilename = filename
            kbox = 0
        # cropping in RGB format
        croppedimage, category = detector.nextBoxDetection()
        if category>0:
            if category == 1:
                croppedfilename = join(CROPPEDANIMALPATH,prefix+"_crop"+str(kbox)+".jpg")
            if category == 2: # human
                croppedfilename = join(CROPPEDHUMANPATH,prefix+"_crop"+str(kbox)+".jpg")
            if category == 3: # vehicle
                croppedfilename = join(CROPPEDVEHICLEPATH,prefix+"_crop"+str(kbox)+".jpg")
            print(filename, croppedfilename, category)
            if croppedimage != []:
                cv2.imwrite(croppedfilename, croppedimage)
    except IndexError:
        break
        
        
        
