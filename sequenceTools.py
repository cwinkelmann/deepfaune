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

import pandas as pd
import random
from PIL import Image
from time import time
from datetime import datetime
import os.path as op

txt_empty = {'fr':"vide", 'gb':"empty"}

def randomDate(seed):
    random.seed(seed)
    d = random.randint(1, int(time()))
    return datetime.fromtimestamp(d).strftime("%Y:%m:%d %H:%M:%S")

def getDateTaken(path):
    try:
        date = Image.open(path)._getexif()[36867]
    except:
        date = None
    return date

####################################################################################
### MAJORITY VOTING IN SEQUENCES OF IMAGES
####################################################################################
def correctPredictionWithSequenceSingleDirectory(sub_df_filename, dates, sub_predictedclass_base, sub_predictedscore_base, maxlag, LANG, seqnuminit = 0):
    seqnum = np.repeat(seqnuminit, sub_df_filename.shape[0])
    sub_predictedclass = sub_predictedclass_base.copy()
    sub_predictedscore = sub_predictedscore_base.copy()
    
    ## Sorting dates and computing lag
    from datetime import timedelta
    datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
    datesorder = np.argsort(datesstrip)
    datesstripSorted = np.sort(datesstrip)
    
    def majorityVotingInSequence(i1, i2):
        df = pd.DataFrame({'prediction':[sub_predictedclass_base[k] for k in datesorder[i1:(i2+1)]], 'score':[sub_predictedscore_base[k] for k in datesorder[i1:(i2+1)]]})
        majority = df.groupby(['prediction']).sum()
        meanscore = df.groupby(['prediction']).mean()['score']
        if list(majority.index) == [txt_empty[LANG]]:
            for k in datesorder[i1:(i2+1)]:
                sub_predictedclass[k] = txt_empty[LANG]
                sub_predictedscore[k] = sub_predictedscore_base[k]
        else:
            notempty = (majority.index != txt_empty[LANG]) # skipping empty images in sequence
            majority = majority[notempty]
            meanscore = meanscore[notempty]
            best = np.argmax(majority['score']) # selecting class with best total score
            majorityclass = majority.index[best]
            majorityscore = meanscore[best] # overall score as the mean for this class
            for k in datesorder[i1:(i2+1)]:
                if sub_predictedclass_base[k]!= txt_empty[LANG]:
                    sub_predictedclass[k] = majorityclass 
                    sub_predictedscore[k] = int(majorityscore*100)/100.
                else:
                    sub_predictedclass[k] = txt_empty[LANG]
                    sub_predictedscore[k] = sub_predictedscore_base[k]
            
    ## Treating sequences
    curseqnum = 1
    i1 = i2 = 0 # sequences boundaries
    for i in range(1,len(datesstripSorted)):
        lag = datesstripSorted[i]-datesstripSorted[i-1]
        if lag<timedelta(seconds=maxlag): # subsequent images in sequence
            pass
        else: # sequence change
            majorityVotingInSequence(i1, i2)
            seqnum[datesorder[i1:(i2+1)]] += curseqnum
            curseqnum += 1
            i1 = i
        i2 = i
    majorityVotingInSequence(i1, i2)
    seqnum[datesorder[i1:(i2+1)]] += curseqnum
    return sub_predictedclass, sub_predictedscore, seqnum

####################################################################################
### ORDERING FILES BY DIRECTORY AND CALLING MAJORITY VOTING
####################################################################################
import numpy as np

def getFilesOrder(df):
    nbrows = len(df)
    numdir = np.array([0]*nbrows)
    dirs = []
    for i in range(0, nbrows):
        dirname = op.dirname(str(df['filename'][i]))
        try:
            dirindex = dirs.index(dirname)
        except:
            dirindex = len(dirs)
            dirs.append(dirname)
        numdir[i] = dirindex
    # Getting file ordering for successive, keeping ordering inside dir 
    filesOrder = np.where(numdir==0)[0]
    for idx in range(1,max(numdir)+1):
        filesOrder = np.concatenate((filesOrder,np.where(numdir==idx)[0]))
    # returns a vector of the order of the files sorted by directory
    return filesOrder

def getDates(df_filename):
    dates = np.array([getDateTaken(file) for file in df_filename['filename']])
    withoutdate = np.where(dates == None)[0]
    dates[withoutdate] = [randomDate(int(i)) for i in withoutdate]
    return dates

def correctPredictionWithSequence(df_filename, dates, predictedclass_base, predictedscore_base, maxlag, LANG):
    nbrows = len(df_filename)
    predictedclass = [0]*nbrows
    predictedscore = [0]*nbrows
    seqnum = [0]*nbrows
    currdir = op.dirname(str(df_filename['filename'][0]))
    lowerbound = 0
    for i in range(1, nbrows):
        dirname = op.dirname(str(df_filename['filename'][i]))
        if currdir != dirname:
            currdir = dirname
            predictedclass[lowerbound:i], predictedscore[lowerbound:i], seqnum[lowerbound:i] = correctPredictionWithSequenceSingleDirectory(df_filename.iloc[lowerbound:i,:], dates[lowerbound:i], predictedclass_base[lowerbound:i], predictedscore_base[lowerbound:i], maxlag, LANG, max(seqnum))
            lowerbound = i
    predictedclass[lowerbound:nbrows], predictedscore[lowerbound:nbrows], seqnum[lowerbound:nbrows] = correctPredictionWithSequenceSingleDirectory(df_filename.iloc[lowerbound:nbrows,:], dates[lowerbound:nbrows], predictedclass_base[lowerbound:nbrows], predictedscore_base[lowerbound:nbrows], maxlag, LANG, max(seqnum))
    return predictedclass, predictedscore, seqnum


def reorderAndCorrectPredictionWithSequence(df_filename, predictedclass_base, predictedscore_base, maxlag, LANG):
    order = getFilesOrder(df_filename)
    df_filename = pd.DataFrame({'filename':[df_filename['filename'][k] for k in order]})
    predictedclass_base = [predictedclass_base[k] for k in order]
    predictedscore_base = [predictedscore_base[k] for k in order]
    dates = getDates(df_filename)
    predictedclass, predictedscore, seqnum = correctPredictionWithSequence(df_filename, dates, predictedclass_base, predictedscore_base, maxlag, LANG)
    return df_filename, predictedclass_base, predictedscore_base, predictedclass, predictedscore, seqnum
    

####################################################################################
### IMAGE COMPARATOR
####################################################################################
import cv2

class ImageDiff:
    
    def __init__(self):
        self.previmage = np.zeros((1,1,3), np.uint8)

    def nextSimilarity(self, image):
        height, width = image.shape[:2]
        prevheight, prevwidth = self.previmage.shape[:2]
        image = cv2.blur(image,(5,5))
        if height==prevheight and width==prevwidth:
            errorL2 = cv2.norm(self.previmage, image, cv2.NORM_L2 )
            similarity = 1 - errorL2 / ( height * width )
        else:
            similarity = 0.
        self.previmage = image.copy()
        return similarity

    
from PIL import ImageChops, ImageFilter
class ImageBoxDiff:
    
    def __init__(self):
        self.prevblur = None
        self.prevshape = (1,1)
      
    def nextSimilarity(self, image):
        blur = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((700,600)).filter(ImageFilter.GaussianBlur(radius = 2))
        if image.shape[:2] == self.prevshape:
            diff = ImageChops.difference(self.prevblur, blur).convert("L")
            threshold = 30
            diffthres = diff.point(lambda p: p > threshold and 255) # point = pixelwise action
            # take min value in 5x5 window
            diffthres = diffthres.filter(ImageFilter.MinFilter(5))
            bbox = diffthres.getbbox()
            # Returns four coordinates in the format (left, upper, right, lower)
            if bbox != None:
                similarity = 0.
            else:
                similarity = 1.
        else:
            similarity = 0.
        self.prevblur = blur
        self.prevshape = image.shape[:2]
        return similarity
