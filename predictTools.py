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

from detectTools import Detector, DetectorJSON, YOLO_THRES, MDV5_THRES
from classifTools import txt_animalclasses, CROP_SIZE, Classifier
from fileManager import FileManager

txt_classes = {'fr': txt_animalclasses['fr']+["humain","vehicule"],
               'en': txt_animalclasses['en']+["human","vehicle"],
               'it': txt_animalclasses['it']+["umano","veicolo"],
               'de': txt_animalclasses['de']+["Mensch","Fahrzeug"]
               }
txt_empty = {'fr':"vide", 'en':"empty", 'it':"vuoto", 'de':"Leer"}
txt_undefined = {'fr':"indéfini", 'en':"undefined", 'it':"indeterminato", 'de':"Undefiniert"}

MAXLOGIT = 15. # arbitrary maximal logit value, used for classes human/vehicule/empty

####################################################################################
### PREDICTOR BASE
####################################################################################
class PredictorBase(ABC):
    def __init__(self, filenames, threshold, LANG, BATCH_SIZE=8):
        self.LANG = LANG
        self.BATCH_SIZE = BATCH_SIZE
        self.fileManager = FileManager(filenames)
        self.classifier = Classifier()
        self.cropped_data = torch.ones((self.BATCH_SIZE,3,CROP_SIZE,CROP_SIZE))
        self.nbclasses = len(txt_classes[self.LANG])
        self.idxhuman = len(txt_animalclasses[self.LANG]) # idx of 'human' class in prediction
        self.idxvehicle = self.idxhuman+1 # idx of 'vehicle' class in prediction
        self.idxforbidden = [] # idx of forbidden classes
        self.prediction = np.zeros(shape=(self.fileManager.nbFiles(), self.nbclasses+1), dtype=np.float32) # logit score
        self.prediction[:,-1] = MAXLOGIT # by default, predicted as empty
        self.predictedclass = [""]*self.fileManager.nbFiles()
        self.predictedscore = [0.]*self.fileManager.nbFiles()
        self.bestboxes = np.zeros(shape=(self.fileManager.nbFiles(), 4), dtype=np.float32)
        self.count = [0]*self.fileManager.nbFiles()
        self.threshold = threshold # classification step
        self.detectionthreshold = 0. # detection step
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

    def setClassificationThreshold(threshold):
        self.threshold = threshold
        
    def setDetectionThreshold(self, threshold):
        self.detectionthreshold = threshold
            
    def getPredictions(self, k=None):
        if k is not None:
            if self.predictedclass[k]=="": # prediction not ready yet
                return self.predictedclass[k], self.predictedscore[k], None, 0
            else:
                return self.predictedclass[k], self.predictedscore[k], self.bestboxes[k,], self.count[k]
        else:            
            return self.predictedclass, self.predictedscore, self.bestboxes, self.count

    def getPredictedClass(self, k):
        return self.predictedclass[k]
        
    def setPredictedClass(self, k, label, score=MAXLOGIT):
        self.predictedclass[k] = label
        self.predictedscore[k] = score

    def setPredictedCount(self, k, count):
        self.count[k] = count
        
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
        if self.predictedclass == [] or predictor.predictedclass == []:
            self.predictedclass = []
        else:
            self.predictedclass += predictor.predictedclass
        if self.predictedscore == [] or predictor.predictedscore == []:
             self.predictedscore = []
        else:            
            self.predictedscore += predictor.predictedscore
        self.resetBatch()        
        
    def __averageLogitInSequence(self, predinseq):
        isempty = (predinseq[:,-1]>0)
        ishuman = (predinseq[:,self.idxhuman]>0)
        isvehicle = (predinseq[:,self.idxvehicle]>0)
        isanimal = ((isempty+ishuman+isvehicle)==False)
        if sum(isempty)==predinseq.shape[0]: # testing all image are empty
            return txt_empty[self.LANG], 1.
        else:
            mostfrequent = np.argsort([sum(isanimal), sum(ishuman), sum(isvehicle)])[-1] # discarding empty images
            if mostfrequent==0: # animal                
                predinseq = predinseq[isanimal,1:(len(txt_animalclasses[self.LANG])+1)]
                if len(self.idxforbidden):
                    predinseq[:,self.idxforbidden] = 0.
                averagelogits = np.mean(predinseq,axis=0)
                best = np.argmax(averagelogits) # selecting class with best average logit
                bestclass = txt_classes[self.LANG][best]
                bestscore = np.exp(averagelogits[best])/sum(np.exp(averagelogits))# softmax(average logit)
            else:
                if mostfrequent==1: # human
                    bestclass = txt_classes[self.LANG][self.idxhuman]
                    bestscore = 1.
                else: # vehicle
                    bestclass = txt_classes[self.LANG][self.idxvehicle]
                    bestscore = 1.
            return bestclass, int(bestscore*100)/100.
                         
####################################################################################
### PREDICTOR IMAGE BASE
####################################################################################
class PredictorImageBase(PredictorBase):    
    def __init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE=8):
        PredictorBase.__init__(self, filenames, threshold, LANG, BATCH_SIZE) # inherits all
        self.fileManager.findSequences(maxlag)
        self.fileManager.reorderBySeqnum()

    def getPredictionsBase(self, k=None):
        if k is not None:
            return self._PredictorBase__score2class(self.prediction[k,]), self.bestboxes[k,], self.count[k]
        else:   
            predictedclass_base = [""]*self.fileManager.nbFiles()
            predictedscore_base = [0.]*self.fileManager.nbFiles()
            for k in range(0,self.fileManager.nbFiles()):
                predictedclass_base[k], predictedscore_base[k] = self._PredictorBase__averageLogitInSequence(self.prediction[k:(k+1),])   
            return predictedclass_base, predictedscore_base, self.bestboxes, self.count

    def setPredictedClassInSequence(self, k, label, score=MAXLOGIT):
        self.setPredictedClass(k, label, score)
        seqnum = self.fileManager.getSeqnums()
        k1seq = k2seq = k
        while (k1seq-1)>=0 and seqnum[(k1seq-1)]==seqnum[k]:
            k1seq = k1seq-1
            self.setPredictedClass(k1seq, label, score)
        while (k2seq+1)<len(seqnum) and seqnum[(k2seq+1)]==seqnum[k]:
            k2seq = k2seq+1
            self.setPredictedClass(k2seq, label, score)

    def correctPredictionsInSequenceBatch(self):
        seqnum = self.fileManager.getSeqnums()
        k1seq = self.k1 # first sequence in batch
        k2seq = self.k2 ## last sequence in batch
        subseqnum = np.array(self.fileManager.getSeqnums()[k1seq:k2seq])
        while (k1seq-1)>=0 and seqnum[(k1seq-1)]==seqnum[self.k1]:
            # previous batch contains images of the first sequence present in the current batch
            k1seq = k1seq-1
        if k2seq<len(seqnum):
            if seqnum[k2seq]==seqnum[(k2seq-1)]:
                # next batch contains images of the last sequence present in the current batch
                while seqnum[(k2seq-1)]==seqnum[self.k2-1] and (k2seq-1>0):
                    k2seq = k2seq-1
        subseqnum = np.array(self.fileManager.getSeqnums()[k1seq:k2seq])
        if len(subseqnum)>0:
            for num in range(min(subseqnum), max(subseqnum)+1):
                idx4num = k1seq + np.nonzero(subseqnum==num)[0]
                bestclass, bestscore = self._PredictorBase__averageLogitInSequence(self.prediction[idx4num,])
                for k in idx4num:
                    self.predictedclass[k] = bestclass
                    self.predictedscore[k] = bestscore
        return k1seq, k2seq
                
    def correctPredictionsInSequence(self):
        self.k1 = 0 # batch start
        self.k2 = self.fileManager.nbFiles()
        self.correctPredictionsInSequenceBatch()

####################################################################################
### PREDICTOR IMAGE
####################################################################################
class PredictorImage(PredictorImageBase):    
    def __init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE=8):
        PredictorImageBase.__init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE) # inherits all
        self.detector = Detector()
        self.setDetectionThreshold(YOLO_THRES)

    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, self.k1, self.k2
        else:
            idxanimal = []
            for k in range(self.k1,self.k2):
                try:
                    imagecv = cv2.imdecode(np.fromfile(self.fileManager.getFilename(k), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                except:
                    imagecv = None
                if imagecv is None:
                    pass # corrupted image, considered as empty
                else:
                    croppedimage, category, box, count = self.detector.bestBoxDetection(imagecv, self.detectionthreshold)
                    self.bestboxes[k] = box
                    self.count[k] = count
                    if category > 0: # not empty
                        self.prediction[k,-1] = 0.
                    if category == 1: # animal
                        self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                        idxanimal.append(k)
                    if category == 2: # human
                        self.prediction[k,self.idxhuman] = MAXLOGIT
                    if category == 3: # vehicle
                        self.prediction[k,self.idxvehicle] = MAXLOGIT
            if len(idxanimal): # predicting species in images with animal 
                self.prediction[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxanimal],:,:,:], withsoftmax=False)            
            k1_batch = self.k1
            k2_batch = self.k2
            k1seq_batch, k2seq_batch = self.correctPredictionsInSequenceBatch()
            # switching to next batch
            self.k1 = self.k2
            self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1
            # returning batch results
            return self.batch-1, k1_batch, k2_batch, k1seq_batch, k2seq_batch
        
####################################################################################
### PREDICTOR VIDEO 
####################################################################################
class PredictorVideo(PredictorBase):
    def __init__(self, filenames, threshold, LANG, BATCH_SIZE=8):
         PredictorBase.__init__(self, filenames, threshold, LANG, BATCH_SIZE) # inherits all
         self.keyframes = [0]*self.fileManager.nbFiles()
         self.detector = Detector()
         self.setDetectionThreshold(YOLO_THRES)

    def resetBatch(self):
        self.k1 = 0
        self.k2 = 1
        self.batch = 1
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k1
        else:   
            idxanimal = []
            idxnonempty = []
            predictionallframe = np.zeros(shape=(self.BATCH_SIZE, self.nbclasses), dtype=np.float32)
            predictionallframe[:,-1] = MAXLOGIT # by default, predicted as empty
            bestboxesallframe = np.zeros(shape=(self.BATCH_SIZE, 4), dtype=np.float32)
            maxcount = 0            
            videocap = cv2.VideoCapture(self.fileManager.getFilename(self.k1))
            total_frames = int(videocap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames==0:
                pass # corrupted video, considered as empty
            else:
                fps = int(videocap.get(5))
                lag = int(fps/3) # lag between two successive frames
                while((self.BATCH_SIZE-1)*lag>total_frames):
                    lag = lag-1 # reducing lag if video duration is less than self.BATCH_SIZE sec
                k = 0 # frame k in position kframe
                for kframe in range(0, self.BATCH_SIZE*lag, lag): 
                    videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                    ret,frame = videocap.read()
                    if ret == False:
                        pass # Corrupted or unavailable image, considered as empty
                    else:
                        imagecv = frame
                        croppedimage, category, box, count = self.detector.bestBoxDetection(imagecv, self.detectionthreshold)
                        bestboxesallframe[k] = box
                        if count>maxcount:
                            maxcount = count
                        if category > 0: # not empty
                            idxnonempty.append(k)
                            predictionallframe[k,-1] = 0.
                        if category == 1: # animal
                            self.cropped_data[k,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                            idxanimal.append(k)
                        if category == 2: # human
                            predictionallframe[k,self.idxhuman] = MAXLOGIT
                        if category == 3: # vehicle
                            predictionallframe[k,self.idxvehicle] = MAXLOGIT
                    k = k+1
            videocap.release()
            if len(idxanimal): # predicting species in frames with animal 
                predictionallframe[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx for idx in idxanimal],:,:,:], withsoftmax=False)
            self.predictedclass[self.k1], self.predictedscore[self.k1] = self._PredictorBase__averageLogitInSequence(predictionallframe)
            if len(idxnonempty): # not empty
                self.prediction[self.k1,-1] = 0.# using max score to select key frame
                tidxmax = np.unravel_index(np.argmax(predictionallframe[idxnonempty,:], axis=None), predictionallframe[idxnonempty,:].shape)
                self.keyframes[self.k1] = idxnonempty[tidxmax[0]]
            self.bestboxes[self.k1] = bestboxesallframe[self.keyframes[self.k1]]
            self.count[self.k1] = maxcount
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+1,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch

    def setDetectionThreshold(self, threshold):
        self.yolothreshold = threshold

    def getKeyFrames(self, index):
        return self.keyframes[index]

####################################################################################
### PREDICTOR IMAGE FROM JSON
####################################################################################
class PredictorJSON(PredictorImageBase):    
    def __init__(self, jsonfilename, threshold, maxlag, LANG, BATCH_SIZE=8):
         self.detector = DetectorJSON(jsonfilename)
         self.setDetectionThreshold(MDV5_THRES)
         PredictorImageBase.__init__(self, self.detector.getFilenames(), threshold, maxlag, LANG, BATCH_SIZE) # inherits all
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, [],[]
        else:
            idxanimal = []
            for k in range(self.k1,self.k2):
                croppedimage, category = self.detector.nextBestBoxDetection(self.detectionthreshold)
                if category > 0: # not empty
                    self.prediction[k,-1] = 0
                if category == 1: # animal
                    self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                    idxanimal.append(k)
                if category == 2: # human
                     self.prediction[k,self.idxhuman] = MAXLOGIT
                if category == 3: # vehicle
                     self.prediction[k,self.idxvehicle] = MAXLOGIT
            if len(idxanimal):
                self.prediction[idxanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxanimal],:,:,:], withsoftmax=False)            
            k1seq_batch, k2seq_batch = self.correctPredictionsInSequenceBatch()
            # switching to next batch
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch
        
    def merge(self, predictor):
        PredictorImageBase.merge(predictor)
        self.detector.merge(predictor.detector)
        
