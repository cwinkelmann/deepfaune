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

import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import os.path as op

def getFilesOrder(filenames):
    nbrows = len(filenames)
    numdir = np.array([0]*nbrows)
    dirs = []
    for i in range(0, nbrows):
        dirname = op.dirname(filenames[i])
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

def getDateFromExif(filename):
    try:
        date = Image.open(filename)._getexif()[36867]
    except:
        date = ''
    return date



class FileManager:
    
    def __init__(self, filenames):
        self.order = getFilesOrder(filenames)
        self.filenames = filenames
        self.nbrows = len(filenames)
        self.seqnum = [0]*self.nbrows
        self.dates = []
    
    def findSequences(self, maxlag):
        if self.dates == []:
            self.findDates()
        currdir = op.dirname(str(self.filenames[self.order[0]]))
        currseqnum = 1
        lowerbound = 0
        for i in range(1, self.nbrows):
            dirname = op.dirname(self.filenames[self.order[i]])
            if currdir != dirname:
                currdir = dirname
                subdates = [self.dates[k] for k in self.order[lowerbound:i]]
                datesorder = np.argsort(subdates)
                self.seqnum[self.order[datesorder[0]+lowerbound]] = currseqnum
                for j in range(1, i-lowerbound):
                    date = datetime.strptime(subdates[datesorder[j]], "%Y:%m:%d %H:%M:%S")
                    datepre = datetime.strptime(subdates[datesorder[j-1]], "%Y:%m:%d %H:%M:%S")
                    lag = date-datepre
                    if lag>timedelta(seconds=maxlag):
                        currseqnum += 1
                    self.seqnum[self.order[datesorder[j]+lowerbound]] = currseqnum
                currseqnum += 1
                lowerbound = i    
        # same as the content of the for loop
        subdates = [self.dates[k] for k in self.order[lowerbound:i+1]]
        datesorder = np.argsort(subdates)
        self.seqnum[self.order[datesorder[0]+lowerbound]] = currseqnum        
        for j in range(1, i-lowerbound+1):
            date = datetime.strptime(subdates[datesorder[j]], "%Y:%m:%d %H:%M:%S")
            datepre = datetime.strptime(subdates[datesorder[j-1]], "%Y:%m:%d %H:%M:%S")
            lag = date-datepre
            if lag>timedelta(seconds=maxlag):
                currseqnum += 1
            self.seqnum[self.order[datesorder[j]+lowerbound]] = currseqnum
            
    def findDates(self):
        self.dates = [getDateFromExif(file) for file in self.filenames]
    
    def getMaxSeqnum(self):
        return max(self.seqnum)
    
    def getFileNamesBySeqnum(self, num):
        indices = np.nonzero(self.seqnum==num)[0]
        res = [self.filenames[k] for k in indices]
        return res
    
    def getSeqnums(self):
        return self.seqnum
    
    def getDates(self):
        return self.dates
    
    def getFileNames(self):
        return self.filenames
    
    def getFileName(self, k):
        return self.filenames[k]
    
    def merge(self, fileManager):
        m = self.getMaxSeqnum()
        self.filenames = self.filenames + fileManager.getFileNames()
        self.seqnum = self.seqnum + [k+m for k in fileManager.getSeqnums()]
        self.dates = self.dates + fileManager.getDates()
        self.nbrows = len(self.filenames)
        self.order = getFilesOrder(self.filenames)
    
    
        
