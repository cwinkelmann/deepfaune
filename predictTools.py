# Copyright CNRS 2023

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
import torch
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from math import log

from detectTools import Detector, DetectorJSON
from classifTools import txt_animalclasses, CROP_SIZE, Classifier
from fileManager import FileManager

txt_classes = {'fr': txt_animalclasses['fr']+["humain","vehicule"],
               'gb': txt_animalclasses['gb']+["human","vehicle"]}
txt_empty = {'fr':"vide", 'gb':"empty"}
txt_undefined = {'fr':"indéfini", 'gb':"undefined"}


class PredictorBase(ABC):
    def __init__(self, filenames, threshold, LANG, BATCH_SIZE=8):
        self.LANG = LANG
        self.BATCH_SIZE = BATCH_SIZE
        self.fileManager = FileManager(filenames)
        self.cropped_data = torch.ones((self.BATCH_SIZE,3,CROP_SIZE,CROP_SIZE))
        self.nbclasses = len(txt_classes[self.LANG])
        self.idxhuman = len(txt_animalclasses[self.LANG]) # idx of 'human' class in prediction
        self.idxvehicle = self.idxhuman+1 # idx of 'vehicle' class in prediction
        self.idxforbidden = [] # idx of forbidden classes
        self.prediction = np.zeros(shape=(self.fileManager.nbFiles(), self.nbclasses+1), dtype=np.float32)
        self.prediction[:,-1] = 1. # by default, predicted as empty
        self.predictedclass = [""]*self.fileManager.nbFiles()
        self.predictedscore = [0.]*self.fileManager.nbFiles()
        self.bestboxes = np.zeros(shape=(self.fileManager.nbFiles(), 4), dtype=np.float32)
        self.count = [0]*self.fileManager.nbFiles()
        self.threshold = threshold
        self.resetBatch()    
    
    def resetBatch(self):
        self.k1 = 0 # batch start
        self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles()) # batch end
        self.batch = 1 # batch num
        
    def allBatch(self):
        self.resetBatch()
        while self.k1<self.fileManager.nbFiles():
            self.nextBatch()

    @abstractmethod
    def nextBatch(self):
        pass
            
    def getPredictions(self, k=None):
        if k is not None:
            if self.predictedclass[k]=="": # correction not yet done
                return self.predictedclass[k], self.predictedscore[k], None, 0
            else:
                return self.predictedclass[k], self.predictedscore[k], self.bestboxes[k,], self.count[k]
        else:            
            return self.predictedclass, self.predictedscore, self.bestboxes, self.count

    def setPrediction(self, k, label, score):
        self.predictedclass[k] = label
        self.predictedscore[k] = score
        
    def getFilenames(self):
        return self.fileManager.getFilenames()
    
    def getSeqnums(self):
        return self.fileManager.getSeqnums()
    
    def getDates(self):
        return self.fileManager.getDates()

    def setForbiddenClasses(self, forbiddenclasses):
        self.idxforbidden = [idx for idx in range(0,len(txt_classes[self.LANG]))
                             if txt_classes[self.LANG][idx] in forbiddenclasses]
        
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
      
    def __score2class(self, pred):
        txt_classesempty_lang = txt_classes[self.LANG] + [txt_empty[self.LANG]]
        if len(self.idxforbidden):
            pred[self.idxforbidden] = 0.
            pred = pred/np.sum(pred)
        idxmax = np.argmax(pred)
        if max(pred)>self.threshold:
            return txt_classesempty_lang[idxmax], int(max(pred)*100)/100.
        else:
            return txt_undefined[self.LANG], int(max(pred)*100)/100.            

    def __majorityVotingInSequence(self, df_prediction):
        print("df:",df_prediction)
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
    
    def correctPredictionsWithSequenceBatch(self):
        seqnum = self.fileManager.getSeqnums()
        k1seq = self.k1 # first sequence in batch
        k2seq = self.k2 ## last sequence in batch
        print(self.k1,self.k2)
        print(k1seq,k2seq)
        subseqnum = np.array(self.fileManager.getSeqnums()[k1seq:k2seq])
        print("Treating? ",subseqnum)
        while (k1seq-1)>=0 and seqnum[(k1seq-1)]==seqnum[self.k1]:
            # previous batch contains images of the first sequence present in the current batch
            k1seq = k1seq-1
        if k2seq<len(seqnum):
            if seqnum[k2seq]==seqnum[(k2seq-1)]:
                # next batch contains images of the last sequence present in the current batch
                while seqnum[(k2seq-1)]==seqnum[self.k2-1] and (k2seq-1>0):
                    k2seq = k2seq-1
        print(k1seq,k2seq)
        subseqnum = np.array(self.fileManager.getSeqnums()[k1seq:k2seq])
        print("Treating ",subseqnum)
        if len(subseqnum)>0:
            for num in range(min(subseqnum), max(subseqnum)+1):
                idx4num = k1seq + np.nonzero(subseqnum==num)[0]
                df_prediction = pd.DataFrame({'prediction':[self.predictedclass_base[k] for k in idx4num],
                                              'score':[self.predictedscore_base[k] for k in idx4num]})
                majorityclass, meanscore = self.__majorityVotingInSequence(df_prediction)
                for k in idx4num:
                    self.predictedclass[k] = majorityclass
                    self.predictedscore[k] = meanscore
        return k1seq, k2seq
                
    def correctPredictionsWithSequence(self):
        self.k1 = 0 # batch start
        self.k2 = self.fileManager.nbFiles()
        self.correctPredictionsWithSequenceBatch()
    
    
class Predictor(PredictorBase):
    
    def __init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE=8):
        super().__init__(filenames, threshold, LANG, BATCH_SIZE) # inherits all
        self.predictedclass_base = [""]*self.fileManager.nbFiles()
        self.predictedscore_base = [0.]*self.fileManager.nbFiles()
        self.detector = Detector()
        self.classifier = Classifier()
        self.fileManager.findSequences(maxlag)
        self.fileManager.reorderBySeqnum()

    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2
        else:
            idxanimal = []
            for k in range(self.k1,self.k2):
                try:
                    imagecv = cv2.imread(self.fileManager.getFilename(k))
                except:
                    imagecv = None
                if imagecv is None:
                    pass # Corrupted image, considered as empty
                else:
                    croppedimage, category, box, count = self.detector.bestBoxDetection(imagecv)
                    self.bestboxes[k] = box
                    self.count[k] = count
                    if category > 0: # not empty
                        self.prediction[k,-1] = 0.
                    if category == 1: # animal
                        self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                        idxanimal.append(k)
                    if category == 2: # human
                        self.prediction[k,self.idxhuman] = 1.
                    if category == 3: # vehicle
                        self.prediction[k,self.idxvehicle] = 1.
            if len(idxanimal): # predicting species in images with animal 
                self.prediction[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxanimal],:,:,:])            
            for k in range(self.k1,self.k2):
                self.predictedclass_base[k], self.predictedscore_base[k] = self._PredictorBase__score2class(self.prediction[k,])
            k1_batch = self.k1
            k2_batch = self.k2
            k1seq_batch, k2seq_batch = self.correctPredictionsWithSequenceBatch()
            # switching to next batch
            self.k1 = self.k2
            self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1
            # returning batch results
            return self.batch-1, k1_batch, k2_batch, k1seq_batch, k2seq_batch
                    
    def getPredictionsBase(self, k=None):
        if k is not None:
            return self.predictedclass_base[k], self.predictedscore_base[k], self.bestboxes[k,], self.count[k]
        else:            
            return self.predictedclass_base, self.predictedscore_base, self.bestboxes, self.count
        
class PredictorVideo(PredictorBase):

    def __init__(self, filenames, threshold, LANG, BATCH_SIZE=8):
         super().__init__(filenames, threshold, LANG, BATCH_SIZE) # inherits all
         self.keyframes = [0]*self.fileManager.nbFiles()
         self.detector = Detector()
         self.classifier = Classifier()

    def resetBatch(self):
        self.k1 = 0
        self.k2 = 1
        self.batch = 1
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1
        else:   
            idxanimal = []
            idxnonempty = []
            video_path = self.fileManager.getFilename(self.k1)
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(video.get(5))
            lag = int(fps/3) # lag between two successive frames
            while((self.BATCH_SIZE-1)*lag>total_frames):
                lag = lag-1 # reducing lag if video duration is less than self.BATCH_SIZE sec
            predictionallframe = np.zeros(shape=(self.BATCH_SIZE, self.nbclasses), dtype=np.float32)
            bestboxesallframe = np.zeros(shape=(self.BATCH_SIZE, 4), dtype=np.float32)
            k = 0
            for kframe in range(0, self.BATCH_SIZE*lag, lag):
                video.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                ret,frame = video.read()
                if not ret:
                    pass # Corrupted or unavailable image, considered as empty
                else:
                    imagecv = frame
                    croppedimage, category, box, count = self.detector.bestBoxDetection(imagecv)
                    bestboxesallframe[k] = box
                    if category > 0: # not empty
                        idxnonempty.append(k)
                    if category == 1: # animal
                        self.cropped_data[k,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                        idxanimal.append(k)
                    if category == 2: # human
                        predictionallframe[k,self.idxhuman] = 1.
                    if category == 3: # vehicle
                        predictionallframe[k,self.idxvehicle] = 1.
                k = k+1
            if len(idxanimal): # predicting species in frames with animal 
                predictionallframe[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx for idx in idxanimal],:,:,:])
            if len(idxnonempty): # not empty
                self.prediction[self.k1,-1] = 0.
                # print((predictionallframe[idxnonempty,:]*100).astype(int))
                # max score in frames with animal/human/vehicle
                tidxmax = np.unravel_index(np.argmax(predictionallframe[idxnonempty,:], axis=None), predictionallframe[idxnonempty,:].shape)
                self.keyframes[self.k1] = idxnonempty[tidxmax[0]]
                # using max score as video score
                self.prediction[self.k1,tidxmax[1]] = predictionallframe[idxnonempty,:][tidxmax[0],tidxmax[1]]
                # or using average score of this class when predicted as video score
                # idxmax4all = np.argmax(predictionallframe[idxnonempty,:], axis=1)
                # self.prediction[self.k1,tidxmax[1]] = np.sum(predictionallframe[idxnonempty,:][np.where(idxmax4all==tidxmax[1])[0],tidxmax[1]],axis=0)/len(np.where(idxmax4all==tidxmax[1])[0])
            self.predictedclass[self.k1], self.predictedscore[self.k1] = self._PredictorBase__score2class(self.prediction[self.k1,])
            self.bestboxes[self.k1] = bestboxesallframe[self.keyframes[self.k1]]
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+1,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch
        
    def getKeyFrames(self, index):
        return self.keyframes[index]

class PredictorJSON(PredictorBase):
    
    def __init__(self, jsonfilename, threshold, LANG, BATCH_SIZE=8):
         self.detector = DetectorJSON(jsonfilename)
         self.classifier = Classifier()
         super().__init__(self.detector.getFilenames(), threshold, LANG, BATCH_SIZE) # inherits all
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, [],[]
        else:
            idxanimal = []
            for k in range(self.k1,self.k2):
                croppedimage, category = self.detector.nextBestBoxDetection()
                if category > 0: # not empty
                    self.prediction[k,-1] = 0
                if category == 1: # animal
                    self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                    idxanimal.append(k)
                if category == 2: # human
                     self.prediction[k,self.idxhuman] = 1.
                if category == 3: # vehicle
                     self.prediction[k,self.idxvehicle] = 1.
            if len(idxanimal):
                self.prediction[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxanimal],:,:,:])            
            for k in range(self.k1,self.k2):
                self.predictedclass_base[k], self.predictedscore_base[k] = self._PredictorBase__score2class(self.prediction[k,])
            k1seq_batch, k2seq_batch = self.correctPredictionsWithSequenceBatch()
            # switching to next batch
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch
        
    def merge(self, predictor):
        super().merge(predictor)
        self.detector.merge(predictor.detector)
        
