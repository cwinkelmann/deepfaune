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


from PIL import Image
def get_date_taken(path):
   try:
       date = Image.open(path)._getexif()[36867]
   except:
       date = None
   return(date)
       
       
dates = np.array([get_date_taken(file) for file in df_filename["filename"]])
withdate = np.where(dates != None)

dates = dates[withdate]
from datetime import datetime
datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
datesorder = np.argsort(datesstrip)
lag =  datesstrip[datesorder][2:dates.shape[0]] - datesstrip[datesorder][1:(dates.shape[0]-1)]
from datetime import timedelta
np.where(lag<timedelta(seconds=10))
