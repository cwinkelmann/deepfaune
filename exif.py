import numpy as np
import pandas as pd
from os import listdir
from os.path import join, basename

testdir = "/home/vmiele/Projects/deepfaune/code/gui/outofsample_data"
df_filename = pd.DataFrame({'filename':[join(testdir,filename) for filename in sorted(listdir(testdir))
                                        if filename.endswith(".jpg") or filename.endswith(".JPG")
                                        or filename.endswith(".jpeg") or filename.endswith(".JPEG")
                                        or filename.endswith(".bmp") or filename.endswith(".BMP")
                                        or filename.endswith(".tif") or filename.endswith(".TIF")
                                        or filename.endswith(".gif") or filename.endswith(".GIF")
                                        or filename.endswith(".png") or filename.endswith(".PNG")]})
nbfiles = df_filename.shape[0]


predictedclass = ['test' for i in range(nbfiles)]


## Getting date from exif, or draw random fake date
from PIL import Image
def get_date_taken(path):
   try:
       date = Image.open(path)._getexif()[36867]
   except:
       date = None
   return(date)

import random
from time import time
def randomDate(seed):
    random.seed(seed)
    d = random.randint(1, int(time()))
    return datetime.fromtimestamp(d).strftime("%Y:%m:%d %H:%M:%S")

dates = np.array([get_date_taken(file) for file in df_filename["filename"]])
withoutdate = np.where(dates == None)[0]
dates[withoutdate] = [randomDate(int(i)) for i in withoutdate]

## Sorting dates and computing lag
from datetime import datetime, timedelta
datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
datesorder = np.argsort(datesstrip)
lagv =  datesstripSorted[2:len(datesstripSorted)] - datesstripSorted[1:(len(datesstripSorted)-1)]
np.where(lagv<timedelta(seconds=20))[0]

## Treating sequences
i1 = i2 = 0 # sequences boundaries
for i in range(1,len(datesstripSorted)):
   lag = datesstripSorted[i]-datesstripSorted[i-1]
   if lag<timedelta(seconds=20): # subsequent images in sequence
      pass
   else: # sequence change
      print("treating sequence ",i1,i2)
      print(datesstrip[datesorder[i1]],datesstrip[datesorder[i2]])
      i1 = i
   i2 = i
print("treating sequence ",i1,i2)   

def predictionWithSequence(i1, i2):
   [predictedclass[k] for k in datesorder[i1:(i2+1)]]
