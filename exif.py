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
import random
predictedscore = [random.random() for i in range(nbfiles)]


from PIL import Image
def get_date_taken(path):
   try:
      date = Image.open(path)._getexif()[36867]
   except:
      date = None
   return date

import random
from time import time
from datetime import datetime
def randomDate(seed):
    random.seed(seed)
    d = random.randint(1, int(time()))
    return datetime.fromtimestamp(d).strftime("%Y:%m:%d %H:%M:%S")
 
   
def correctPredictionWithSequence():
   ## Getting date from exif, or draw random fake date
   dates = np.array([get_date_taken(file) for file in df_filename["filename"]])
   withoutdate = np.where(dates == None)[0]
   dates[withoutdate] = [randomDate(int(i)) for i in withoutdate]
   
   ## Sorting dates and computing lag
   from datetime import timedelta
   datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
   datesorder = np.argsort(datesstrip)
   datesstripSorted = np.sort(datesstrip)
   
   def majorityVotingInSequence(i1, i2):
      df = pd.DataFrame({'prediction':[predictedclass[k] for k in datesorder[i1:(i2+1)]], 'score':[predictedscore[k] for k in datesorder[i1:(i2+1)]]})
      majority = df.groupby(['prediction']).sum()
      if list(majority.index) == ['vide']:
         pass # only empty images
      else:
         majority = majority[majority.index != 'vide'] # skipping empty images in sequence
         best = np.argmax(majority['score']) # selecting class with best total score
         majorityclass = majority.index[best]
         majorityscore = df.groupby(['prediction']).mean()['score'][best] # overall score as the mean for this class
         for k in datesorder[i1:(i2+1)]:
            predictedclass[k] = majorityclass 
            predictedscore[k] = majorityscore
      
   ## Treating sequences
   i1 = i2 = 0 # sequences boundaries
   for i in range(1,len(datesstripSorted)):
      lag = datesstripSorted[i]-datesstripSorted[i-1]
      if lag<timedelta(seconds=20): # subsequent images in sequence
         pass
      else: # sequence change
         print("treating sequence ",i1,i2)
         majorityVotingInSequence(i1, i2)
         i1 = i
      i2 = i
   print("treating sequence ",i1,i2)
   majorityVotingInSequence(i1, i2)
   return predictedclass, predictedscore

