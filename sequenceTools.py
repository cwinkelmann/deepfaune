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

txt_empty = {'fr':"vide", 'gb':"empty"}
LANG = 'gb'

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
def correctPredictionWithSequenceSingleDirectory(sub_df_filename, sub_predictedclass_base, sub_predictedscore_base, seqnuminit=0):
    seqnum = np.repeat(seqnuminit, sub_df_filename.shape[0])
    sub_predictedclass = sub_predictedclass_base.copy()
    sub_predictedscore = sub_predictedscore_base.copy()
    ## Getting date from exif, or draw random fake date
    dates = np.array([getDateTaken(file) for file in sub_df_filename['filename']])
    withoutdate = np.where(dates == None)[0]
    dates[withoutdate] = [randomDate(int(i)) for i in withoutdate]
    
    ## Sorting dates and computing lag
    from datetime import timedelta
    datesstrip =  np.array([datetime.strptime(date, "%Y:%m:%d %H:%M:%S") for date in dates])
    datesorder = np.argsort(datesstrip)
    datesstripSorted = np.sort(datesstrip)
    
    def majorityVotingInSequence(i1, i2):
        df = pd.DataFrame({'prediction':[sub_predictedclass_base[k] for k in datesorder[i1:(i2+1)]], 'score':[sub_predictedscore_base[k] for k in datesorder[i1:(i2+1)]]})
        majority = df.groupby(['prediction']).sum()
        if list(majority.index) == [txt_empty[LANG]]:
            for k in datesorder[i1:(i2+1)]:
                sub_predictedclass[k] = txt_empty[LANG]
                sub_predictedscore[k] = sub_predictedscore_base[k]
        else:
            majority = majority[majority.index != txt_empty[LANG]] # skipping empty images in sequence
            best = np.argmax(majority['score']) # selecting class with best total score
            majorityclass = majority.index[best]
            majorityscore = df.groupby(['prediction']).mean()['score'][best] # overall score as the mean for this class
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
        if lag<timedelta(seconds=20): # subsequent images in sequence
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
        dirname = str(df['filename'][i])[:-len(str(df['filename'][i]).split("/")[-1])]
        try:
            dirindex = dirs.index(dirname)
        except:
            dirindex = len(dirs)
            dirs.append(dirname)
        numdir[i] = dirindex
    filesOrder = np.argsort(numdir)
    # returns a vector of the order of the files sorted by directory
    return filesOrder

def correctPredictionWithSequence(filenames, predictclass_base, predictscore_base):
    nbrows = len(filenames)
    predictclass = [0]*nbrows
    predictscore = [0]*nbrows
    seqnum = [0]*nbrows
    currdir = str(filenames['filename'][0])[:-len(str(filenames['filename'][0]).split("/")[-1])]
    lowerbound = 0
    for i in range(1, nbrows):
        dirname = str(filenames['filename'][i])[:-len(str(filenames['filename'][i]).split("/")[-1])]
        if currdir != dirname:
            currdir = dirname
            predictclass[lowerbound:i], predictscore[lowerbound:i], seqnum[lowerbound:i] = correctPredictionWithSequenceSingleDirectory(filenames.iloc[lowerbound:i,:], predictclass_base[lowerbound:i], predictscore_base[lowerbound:i], seqnuminit=max(seqnum))
            lowerbound = i
    predictclass[lowerbound:nbrows], predictscore[lowerbound:nbrows], seqnum[lowerbound:nbrows] = correctPredictionWithSequenceSingleDirectory(filenames.iloc[lowerbound:nbrows,:], predictclass_base[lowerbound:nbrows], predictscore_base[lowerbound:nbrows], seqnuminit=max(seqnum))
    return predictclass, predictscore, seqnum

def reorderAndCorrectPredictionWithSequence(filenames, predictclass_base, predictscore_base, lang):
    global LANG
    LANG = lang
    order = getFilesOrder(filenames)
    filenames = pd.DataFrame({'filename':[filenames['filename'][k] for k in order]})
    predictclass_base = [predictclass_base[k] for k in order]
    predictscore_base = [predictscore_base[k] for k in order]
    predictclass, predictscore, seqnum = correctPredictionWithSequence(filenames, predictclass_base, predictscore_base)
    return filenames, predictclass_base, predictscore_base, predictclass, predictscore, seqnum
    
