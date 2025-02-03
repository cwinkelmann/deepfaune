# Copyright CNRS 2024

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
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

def getFilesOrder(filenames):
    nbfiles = len(filenames)
    if nbfiles==0:
        return np.array([])
    numdir = np.array([0]*nbfiles)
    dirs = []
    for i in range(0, nbfiles):
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

def isLagUnderMaxlag(date1, date2, maxlag):
    try:
        date = datetime.strptime(date2, "%Y:%m:%d %H:%M:%S")
        datepre = datetime.strptime(date1, "%Y:%m:%d %H:%M:%S")
        lag = date-datepre
        return(lag<=timedelta(seconds=maxlag))
    except ValueError:
        return(False)

def getDateFromMetadata(filename):
    date = "NA"  # default
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):  # Image file
        try:
            date = Image.open(filename)._getexif()[36867]
        except: # TypeError
            pass
    elif filename.lower().endswith(('.mov', '.mp4', '.mkv')):  # Video file
        try:
            date = extractMetadata(createParser(filename)).get('creation_date')
        except: # KeyError
            pass
    return date


class FileManager:
    
    def __init__(self, filenames):
        self.order = getFilesOrder(filenames)
        self.filenames = filenames
        self.seqnum = [1+k for k in range(0,len(self.filenames))]
        self.dates = ['']*len(self.filenames)
        self.__findDates()

    def __findDates(self):
        self.dates = [getDateFromMetadata(file) for file in self.filenames]

    def reorderBySeqnum(self):
        idx = 0
        seqnum = np.array(self.seqnum)
        for num in range(1, max(seqnum)+1):
            idx4num = np.nonzero(seqnum==num)[0]
            self.order[idx:(idx+len(idx4num))] = idx4num
            idx = idx+len(idx4num)
        self.filenames = [self.filenames[k] for k in self.order]
        self.seqnum = [self.seqnum[k] for k in self.order]
        self.dates = [self.dates[k] for k in self.order]
        self.order = [k for k in range(0,len(self.filenames))]

    def findSequences(self, maxlag):
        currdir = op.dirname(self.filenames[self.order[0]])
        currseqnum = 1
        lowerbound = 0
        i = 0
        for i in range(1, len(self.filenames)):
            dirname = op.dirname(self.filenames[self.order[i]])
            if currdir != dirname:
                currdir = dirname
                subdates = [self.dates[k] for k in self.order[lowerbound:i]]
                datesorder = np.argsort(subdates)
                self.seqnum[self.order[datesorder[0]+lowerbound]] = currseqnum
                for j in range(1, i-lowerbound):
                    try:
                        if not isLagUnderMaxlag(subdates[datesorder[j-1]], subdates[datesorder[j]], maxlag):
                            currseqnum += 1
                    except:
                        currseqnum += 1
                    self.seqnum[self.order[datesorder[j]+lowerbound]] = currseqnum
                currseqnum += 1
                lowerbound = i    
        # same as the content of the for loop
        subdates = [self.dates[k] for k in self.order[lowerbound:i+1]]
        datesorder = np.argsort(subdates)
        self.seqnum[self.order[datesorder[0]+lowerbound]] = currseqnum        
        for j in range(1, i-lowerbound+1):
            try:
                if not isLagUnderMaxlag(subdates[datesorder[j-1]], subdates[datesorder[j]], maxlag):
                    currseqnum += 1
            except:
                currseqnum += 1
            self.seqnum[self.order[datesorder[j]+lowerbound]] = currseqnum
            
    def getMaxSeqnum(self):
        return max(self.seqnum)
    
    def getFilenamesBySeqnum(self, num):
        seqnum = np.array(self.seqnum)
        indices = np.nonzero(seqnum==num)[0]
        res = [self.filenames[k] for k in indices]
        return res
    
    def getSeqnums(self):
        return self.seqnum
    
    def getDates(self):
        return self.dates

    def nbFiles(self):
        return len(self.filenames)
                      
    def getFilenames(self):
        return self.filenames
    
    def getFilename(self, k):
        return self.filenames[k]
    
    def getSortedFilename(self, k):
        return self.filenames[self.order[k]]

    def merge(self, fileManager, maxlag):
        m = self.getMaxSeqnum()
        if isLagUnderMaxlag(self.dates[-1], fileManager.dates[0], maxlag) and \
           op.dirname(self.filenames[-1])==op.dirname(fileManager.filenames[0]):
            self.seqnum += [(k-1)+m for k in fileManager.getSeqnums()]
        else:
            self.seqnum += [k+m for k in fileManager.getSeqnums()]
        self.filenames += fileManager.getFilenames()
        self.dates += fileManager.getDates()
        self.order = getFilesOrder(self.filenames)
    
    
        
