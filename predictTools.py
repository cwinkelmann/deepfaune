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
import cv2
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

import torch

from detectTools import Detector, DetectorJSON
from classifTools import txt_classes, CROP_SIZE, Classifier
from fileManager import FileManager

BATCH_SIZE = 8
txt_undefined = {'fr':"indéfini", 'gb':"undefined"}
txt_empty = {'fr':"vide", 'gb':"empty"}

class PredictorBase(ABC):
    def __init__(self, filenames, threshold, LANG):
        self.LANG = LANG
        self.fileManager = FileManager(filenames)
        self.cropped_data = torch.ones((BATCH_SIZE,3,CROP_SIZE,CROP_SIZE))
        self.nbclasses=len(txt_classes[LANG])
        self.prediction = np.zeros(shape=(self.fileManager.nbFiles(), self.nbclasses+1), dtype=np.float32)
        self.prediction[:,self.nbclasses] = 1. # by default, predicted as empty
        self.predictedclass_base = [txt_undefined[LANG]]*self.fileManager.nbFiles()
        self.predictedscore_base = [0.]*self.fileManager.nbFiles()
        self.predictedclass = []
        self.predictedscore = []
        self.threshold = threshold
        self.resetBatch()    
    
    def resetBatch(self):
        self.k1 = 0 # batch start
        self.k2 = min(self.k1+BATCH_SIZE,self.fileManager.nbFiles()) # batch end
        self.batch = 1 # batch num
        
    def allBatch(self):
        self.resetBatch()
        while self.k1<self.fileManager.nbFiles():
            self.nextBatch()
        
    @abstractmethod
    def nextBatch(self):
        pass
    
    def getPredictions(self):
        return self.predictedclass_base, self.predictedscore_base
            
    def getPredictionsWithSequences(self, maxlag):
        if self.predictedclass == []:
            self.__correctPredictionsWithSequence(maxlag)
        return self.predictedclass, self.predictedscore
    
    def getFilenames(self):
        return self.fileManager.getFilenames()
    
    def getSeqnums(self):
        return self.fileManager.getSeqnums()
    
    def getDates(self):
        return self.fileManager.getDates()
        
    def merge(self, predictor):
        if type(self).__name__ != type(predictor).__name__ or self.nbclasses != predictor.nbclasses:
            exit("You can not merge incompatible predictors (incompatible type or number of classes)")
        self.fileManager.merge(predictor.fileManager)
        self.prediction = np.concatenate((self.prediction, predictor.prediction), axis=0)
        if self.predictedclass_base == [] or predictor.predictedclass_base == []:
            self.predictedclass_base = []
        else:
            self.predictedclass_base += predictor.predictedclass_base
        if self.predictedscore_base == [] or predictor.predictedscore_base == []:
             self.predictedscore_base = []
        else:            
            self.predictedscore_base += predictor.predictedscore_base
        if self.predictedclass == [] or predictor.predictedclass == []:
            self.predictedclass = []
        else:
            self.predictedclass += predictor.predictedclass
        if self.predictedscore == [] or predictor.predictedscore == []:
             self.predictedscore = []
        else:            
            self.predictedscore += predictor.predictedscore
        self.resetBatch()
        
    def __prediction2class(self, batchOnly=True):
        if batchOnly:
            k1 = self.k1
            k2 = self.k2
        else:
            k1 = 0
            k2 = self.fileManager.nbFiles()
        txt_classesempty_lang = txt_classes[self.LANG] + [txt_empty[self.LANG]]
        for k in range(k1,k2):
            pred = self.prediction[k,]
            if(max(pred)>=self.threshold):
                self.predictedclass_base[k] = txt_classesempty_lang[np.argmax(pred)]
            self.predictedscore_base[k] = int(max(pred)*100)/100.
    
    def __majorityVotingInSequence(self, df_prediction):
        txt_empty_lang = txt_empty[self.LANG]
        majority = df_prediction.groupby(['prediction']).sum()
        meanscore = df_prediction.groupby(['prediction']).mean()['score']
        if list(majority.index) == [txt_empty_lang]:
            return txt_empty_lang, 1.
        else:
            notempty = (majority.index != txt_empty_lang) # skipping empty images in sequence
            majority = majority[notempty]
            meanscore = meanscore[notempty]
            best = np.argmax(majority['score']) # selecting class with best total score
            majorityclass = majority.index[best]
            majorityscore = meanscore[best] # overall score as the mean for this class
            return majorityclass, int(majorityscore*100)/100.
    
    def __correctPredictionsWithSequence(self, maxlag):
        self.predictedclass = [""]*self.fileManager.nbFiles()
        self.predictedscore = [0]*self.fileManager.nbFiles()
        txt_empty_lang = txt_empty[self.LANG]
        self.fileManager.findSequences(maxlag)
        seqnum = np.array(self.fileManager.getSeqnums())
        for i in range(1, max(seqnum)+1):
            indices = np.nonzero(seqnum==i)[0]
            df_prediction = pd.DataFrame({'prediction':[self.predictedclass_base[k] for k in indices], 'score':[self.predictedscore_base[k] for k in indices]})
            majorityclass, meanscore = self.__majorityVotingInSequence(df_prediction)
            for j in indices:
                if self.predictedclass[j] != txt_empty_lang:
                    self.predictedclass[j] = majorityclass
                    self.predictedscore[j] = meanscore
    
    
class Predictor(PredictorBase):
    
    def __init__(self, filenames, threshold, LANG):
        super().__init__(filenames, threshold, LANG) # inherits all
        self.detector = Detector()
        self.classifier = Classifier()

    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, [],[]
        else:
            idxnonempty = []
            for k in range(self.k1,self.k2):
                image_path = self.fileManager.getFilename(k)
                original_image = cv2.imread(image_path)
                if original_image is None:
                    pass # Corrupted image, considered as empty
                else:
                    croppedimage, nonempty = self.detector.bestBoxDetection(original_image)
                    if nonempty:
                        self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                        idxnonempty.append(k)
            if len(idxnonempty):
                self.prediction[idxnonempty,0:self.nbclasses] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxnonempty],:,:,:])
                self.prediction[idxnonempty,self.nbclasses] = 0 # not empty
            self._PredictorBase__prediction2class(batchOnly=True)
            predictedclass_batch = self.predictedclass_base[self.k1:self.k2]
            predictedscore_batch = self.predictedscore_base[self.k1:self.k2]
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch, predictedclass_batch, predictedscore_batch
                


class PredictorVideo(PredictorBase):
    
    def __init__(self, filenames, threshold, LANG):
         super().__init__(filenames, threshold, LANG) # inherits all
         self.detector = Detector()
         self.classifier = Classifier()

    def resetBatch(self):
        self.k1 = 0
        self.k2 = 1
        self.batch = 1
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, [],[]
        else:   
            idxnonempty = []      
            video_path = self.fileManager.getFilename(self.k1)
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(video.get(5))
            # print ("fps=" + str(fps))
            # print("duration=" + str(duration))
            lag = fps # lag between two successice frames
            while((BATCH_SIZE-1)*lag>total_frames):
                lag = lag-1 # reducing lag if video duration is less than BATCH_SIZE sec
            k = 0
            for kframe in range(0, BATCH_SIZE*lag, lag):
                video.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                ret,frame = video.read()
                if not ret:
                    pass # Corrupted or unavailable image, considered as empty
                else:
                    original_image = frame
                    croppedimage, nonempty = self.detector.bestBoxDetection(original_image)
                    if nonempty:
                        self.cropped_data[k,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                        idxnonempty.append(k)
                k = k+1
            if len(idxnonempty):
                predictionbynonemptyframe = self.classifier.predictOnBatch(self.cropped_data[[idx for idx in idxnonempty],:,:,:])
                self.prediction[self.k1,0:self.nbclasses] = np.sum(predictionbynonemptyframe,axis=0)/len(idxnonempty)
                self.prediction[self.k1,self.nbclasses] = 0 # not empty
            self._PredictorBase__prediction2class(batchOnly=True)
            predictedclass_batch = self.predictedclass_base[self.k1:self.k2]
            predictedscore_batch = self.predictedscore_base[self.k1:self.k2]
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+1,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch, predictedclass_batch, predictedscore_batch
        


class PredictorJSON(PredictorBase):
    
    def __init__(self, jsonfilename, threshold, LANG):
         self.detector = DetectorJSON(jsonfilename)
         self.classifier = Classifier()
         super().__init__(self.detector.getFilenames(), threshold, LANG) # inherits all
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, [],[]
        else:
            idxnonempty = []
            for k in range(self.k1,self.k2):
                croppedimage, category = self.detector.nextBestBoxDetection()
                if category > 0: # not empty
                    self.prediction[k,self.nbclasses] = 0.
                if category == 1: # animal
                    self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                    idxnonempty.append(k)
                # if category == 2: # human
                #     self.prediction[k,idx_human] = 1.
                # if category == 3: # vehicle
                #     self.prediction[k,idx_vehicle] = 1.
            if len(idxnonempty):
                self.prediction[idxnonempty,0:self.nbclasses] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxnonempty],:,:,:], cv2.getNumThreads())
                self.prediction[idxnonempty,self.nbclasses] = 0 # not empty
            self._PredictorBase__prediction2class(batchOnly=True)
            predictedclass_batch = self.predictedclass_base[self.k1:self.k2]
            predictedscore_batch = self.predictedscore_base[self.k1:self.k2]
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch, predictedclass_batch, predictedscore_batch
        
    def merge(self, predictor):
        super().merge(predictor)
        self.detector.merge(predictor.detector)
        
        
