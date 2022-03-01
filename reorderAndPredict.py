#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 10:37:12 2022

@author: Elias Chetouane, Vincent Miele

To use this, just write 'from <path/>reorderAndPredict.py import reorderAndPredictWithSequence'
where <path/> is the path of this file.
"""

####################################################################################
### PREDICTION TOOL USING EXIF INFO & SEQUENCES, TIME DELTA = 20s
####################################################################################
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

def get_date_taken(path):
    try:
        date = Image.open(path)._getexif()[36867]
    except:
        date = None
    return date

def correctPredictionWithSequence(sub_df_filename, sub_predictedclass_base, sub_predictedscore_base, seqnuminit=0):
    seqnum = np.repeat(seqnuminit, sub_df_filename.shape[0])
    sub_predictedclass = sub_predictedclass_base.copy()
    sub_predictedscore = sub_predictedscore_base.copy()
    ## Getting date from exif, or draw random fake date
    dates = np.array([get_date_taken(file) for file in sub_df_filename['filename']])
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
### ORDERING FILES BY DIRECTORY AND CALLING THE PREDICTION TOOL USING EXIF
####################################################################################

import numpy as np

def getOrder(df):
    nbrows = len(df)
    numdir = np.array([0]*nbrows)
    dirs = []
    for i in range(0, nbrows):
        dirname = str(df['filename'][i])[:-len(str(df['filename'][i]).split("/")[-1])]
        try:
            t = dirs.index(dirname)
        except:
            t = len(dirs)
            dirs.append(dirname)
        numdir[i] = t
    filesOrder = np.argsort(numdir)
    # returns a vector of the order of the files sorted by directory
    return filesOrder

def getPredictions(filenames, predictclass_base, predictscore_base):
    nbrows = len(filenames)
    predictclass = [0]*nbrows
    predictscore = [0]*nbrows
    seqnum = [0]*nbrows
    currdir = str(filenames['filename'][0])[:-len(str(filenames['filename'][0]).split("/")[-1])]
    lower_bound = 0
    for i in range(1, nbrows):
        dirname = str(filenames['filename'][i])[:-len(str(filenames['filename'][i]).split("/")[-1])]
        if currdir != dirname:
            currdir = dirname
            predictclass[lower_bound:i], predictscore[lower_bound:i], seqnum[lower_bound:i] = correctPredictionWithSequence(filenames.iloc[lower_bound:i,:], predictclass_base[lower_bound:i], predictscore_base[lower_bound:i], seqnuminit=max(seqnum))
            lower_bound = i
    predictclass[lower_bound:i+1], predictscore[lower_bound:i+1], seqnum[lower_bound:i+1] = correctPredictionWithSequence(filenames.iloc[lower_bound:i+1,:], predictclass_base[lower_bound:i+1], predictscore_base[lower_bound:i+1], seqnuminit=max(seqnum))
    return predictclass, predictscore, seqnum

def reorderAndPredictWithSequence(filenames, predictclass_base, predictscore_base):
    order = getOrder(filenames)
    filenames = pd.DataFrame({'filename':[filenames['filename'][k] for k in order]})
    predictclass_base = [predictclass_base[k] for k in order]
    predictscore_base = [predictscore_base[k] for k in order]
    predictclass, predictscore, seqnum = getPredictions(filenames, predictclass_base, predictscore_base)
    return filenames, predictclass_base, predictscore_base, predictclass, predictscore, seqnum
    