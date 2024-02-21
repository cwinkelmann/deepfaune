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

DEFAULTLOGIT = 15. # arbitrary default logit value, used for classes human/vehicule/empty

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
        self.prediction[:,-1] = DEFAULTLOGIT # by default, predicted as empty
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

    def setClassificationThreshold(self, threshold):
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
        
    def setPredictedClass(self, k, label, score=DEFAULTLOGIT):
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

    def setForbiddenAnimalClasses(self, forbiddenanimalclasses):
        # index of fobidden classes, only animal classes
        # that are at the beginning of the classes list
        self.idxforbidden = [idx for idx in range(0,len(txt_animalclasses[self.LANG]))
                             if txt_animalclasses[self.LANG][idx] in forbiddenanimalclasses]
        
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
                idxanimal = list(range(0,len(txt_animalclasses[self.LANG])))
                predinseq = predinseq[isanimal,] # only images with animals
                predinseq = predinseq[:, idxanimal] # only animal classes
                if len(self.idxforbidden):
                    idxanimal = np.delete(idxanimal, self.idxforbidden)
                    predinseq = np.delete(predinseq, self.idxforbidden, axis=1)
                averagelogits = np.mean(predinseq,axis=0)
                temperature = 0.937 if predinseq.shape[0] == 1 else 0.865 # different temperature for image level and sequence level
                averagelogits /= temperature
                bestidx = idxanimal[np.argmax(averagelogits)] # selecting class with best average logit
                bestscore = np.exp(averagelogits[np.argmax(averagelogits)])/sum(np.exp(averagelogits)) # softmax(average logit)
            else:
                if mostfrequent==1: # human
                    bestidx = self.idxhuman
                    bestscore = 1.
                else: # vehicle
                    bestidx = self.idxvehicle
                    bestscore = 1.
            if bestscore<self.threshold: # convert to undefined, if necessary
                bestclass = txt_undefined[self.LANG]
            else:
                bestclass = txt_classes[self.LANG][bestidx]
            return bestclass, int(bestscore*100)/100.
                         
####################################################################################
### PREDICTOR IMAGE BASE
####################################################################################
class PredictorImageBase(PredictorBase):
    @abstractmethod
    def __init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE=8):
        PredictorBase.__init__(self, filenames, threshold, LANG, BATCH_SIZE) # inherits all
        self.fileManager.findSequences(maxlag)
        self.fileManager.reorderBySeqnum()
        self.detector = None

    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k2, self.k1, self.k2
        else:
            rangeanimal = []
            for k in range(self.k1,self.k2):
                croppedimage, category, box, count, humanboxes = self.detector.bestBoxDetection(self.fileManager.getFilename(k), self.detectionthreshold)
                self.bestboxes[k] = box
                self.count[k] = count
                if category > 0: # not empty
                    self.prediction[k,-1] = 0.
                if category == 1: # animal
                    self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                    rangeanimal.append(k)
                if category == 2: # human
                    self.prediction[k,self.idxhuman] = DEFAULTLOGIT
                if category == 3: # vehicle
                    self.prediction[k,self.idxvehicle] = DEFAULTLOGIT
                if humanboxes is not None: # humans
                    self.humanboxes[self.fileManager.getFilename(k)] = humanboxes
            if len(rangeanimal): # predicting species in images with animal 
                self.prediction[rangeanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[k-self.k1 for k in rangeanimal],:,:,:], withsoftmax=False)
            k1_batch = self.k1
            k2_batch = self.k2
            k1seq_batch, k2seq_batch = self.correctPredictionsInSequenceBatch()
            # switching to next batch
            self.k1 = self.k2
            self.k2 = min(self.k1+self.BATCH_SIZE,self.fileManager.nbFiles())
            self.batch = self.batch+1
            # returning batch results
            return self.batch-1, k1_batch, k2_batch, k1seq_batch, k2seq_batch

    def getPredictionsBase(self, k=None):
        if k is not None:
            return self._PredictorBase__score2class(self.prediction[k,]), self.bestboxes[k,], self.count[k]
        else:   
            predictedclass_base = [""]*self.fileManager.nbFiles()
            predictedscore_base = [0.]*self.fileManager.nbFiles()
            for k in range(0,self.fileManager.nbFiles()):
                predictedclass_base[k], predictedscore_base[k] = self._PredictorBase__averageLogitInSequence(self.prediction[k:(k+1),])   
            return predictedclass_base, predictedscore_base, self.bestboxes, self.count

    def setPredictedClassInSequence(self, k, label, score=DEFAULTLOGIT):
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
                range4num = k1seq + np.nonzero(subseqnum==num)[0]
                bestclass, bestscore = self._PredictorBase__averageLogitInSequence(self.prediction[range4num,])
                for k in range4num:
                    self.predictedclass[k] = bestclass
                    self.predictedscore[k] = bestscore
        return k1seq, k2seq
                
    def correctPredictionsInSequence(self):
        self.k1 = 0 # batch start
        self.k2 = self.fileManager.nbFiles()
        self.correctPredictionsInSequenceBatch()

    def getHumanBoxes(self, filename):
        try:
            return(self.humanboxes[filename])
        except KeyError:
            return None

    def getHumanPresence(self, k=None):
        if k == None:
            return [self.getHumanBoxes(filename) is not None for filename in self.fileManager.getFilenames()]
        else:
            return (self.getHumanBoxes(filename) is not None)

    def merge(self, predictor):
        self.k1, self.k2 = self.fileManager.nbFiles() # positionning at the junction between the two predictors
        self.fileManager.merge(predictor.fileManager)
        self.prediction = np.concatenate((self.prediction, predictor.prediction), axis=0)
        self.predictedclass += predictor.predictedclass
        self.predictedscore += predictor.predictedscore
        self.correctPredictionsInSequenceBatch() # correcting current sequence at the junction
        self.detector.merge(predictor.detector)
        self.resetBatch()   

####################################################################################
### PREDICTOR IMAGE
####################################################################################
class PredictorImage(PredictorImageBase):
    ## Predictor performing detections with our own detector, from filenames
    def __init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE=8):
        PredictorImageBase.__init__(self, filenames, threshold, maxlag, LANG, BATCH_SIZE) # inherits all
        self.detector = Detector()
        self.setDetectionThreshold(YOLO_THRES)
        self.humanboxes = dict()

####################################################################################
### PREDICTOR JSON
####################################################################################
class PredictorJSON(PredictorImageBase):
    ## Predictor using MDv5 detections, listed in jsonfilename
    def __init__(self, jsonfilename, threshold, maxlag, LANG, BATCH_SIZE=8):
        detectorjson = DetectorJSON(jsonfilename)
        PredictorImageBase.__init__(self, detectorjson.getFilenames(), threshold, maxlag, LANG, BATCH_SIZE) # inherits all
        self.detector = detectorjson
        self.setDetectionThreshold(MDV5_THRES)
        self.humanboxes = dict()

####################################################################################
### PREDICTOR VIDEO 
####################################################################################
class PredictorVideo(PredictorBase):
    def __init__(self, filenames, threshold, LANG, BATCH_SIZE=8):
         PredictorBase.__init__(self, filenames, threshold, LANG, BATCH_SIZE) # inherits all
         self.keyframes = [0]*self.fileManager.nbFiles()
         self.detector = Detector()
         self.setDetectionThreshold(YOLO_THRES)
         self.humanpresence = [False]*self.fileManager.nbFiles()

    def resetBatch(self):
        self.k1 = 0
        self.k2 = 1
        self.batch = 1
    
    def nextBatch(self):
        if self.k1>=self.fileManager.nbFiles():
            return self.batch, self.k1, self.k1
        else:   
            rangeanimal = []
            rangenonempty = []
            predictionallframe = np.zeros(shape=(self.BATCH_SIZE, self.nbclasses+1), dtype=np.float32) # nbclasses+empty
            predictionallframe[:,-1] = DEFAULTLOGIT # by default, predicted as empty
            bestboxesallframe = np.zeros(shape=(self.BATCH_SIZE, 4), dtype=np.float32)
            maxcount = 0            
            videocap = cv2.VideoCapture(self.fileManager.getFilename(self.k1))
            total_frames = int(videocap.get(cv2.CAP_PROP_FRAME_COUNT))
            kframetotal = []
            if total_frames==0:
                pass # corrupted video, considered as empty
            else:
                fps = int(videocap.get(5))
                # lag between two successive frames,
                # first 2/3*BATCH_SIZE spaced with a small lag for the video beginning
                # next 1/3*BATCH_SIZE spaced with a large lag for the remaining video
                nbframebegin = int(self.BATCH_SIZE*2/3+0.5)
                nbframeremain = self.BATCH_SIZE-nbframebegin 
                lagbegin = int(fps/3)
                while((nbframebegin-1)*lagbegin>total_frames):
                    lagbegin = lagbegin-1 # reducing lagbegin if video duration is small
                kframebegin = [k*lagbegin for k in range(0,nbframebegin)]
                lagremain = int( (total_frames-kframebegin[-1])/nbframeremain )
                if lagremain>0:
                    kframeremain = [kframebegin[-1]+(k+1)*lagremain for k in range(0,nbframeremain)]
                else:
                    kframeremain = []
                kframetotal = kframebegin+kframeremain
                k = 0 # frame k in position kframe
                for kframe in kframetotal: 
                    videocap.set(cv2.CAP_PROP_POS_FRAMES, kframe)
                    ret,frame = videocap.read()
                    if ret == False:
                        pass # Corrupted or unavailable image, considered as empty
                    else:
                        imagecv = frame
                        croppedimage, category, box, count, humanboxes = self.detector.bestBoxDetection(imagecv, self.detectionthreshold)
                        bestboxesallframe[k] = box
                        if count>maxcount:
                            maxcount = count
                        if category > 0: # not empty
                            rangenonempty.append(k)
                            predictionallframe[k,-1] = 0.
                        if category == 1: # animal
                            self.cropped_data[k,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                            rangeanimal.append(k)
                        if category == 2: # human
                            predictionallframe[k,self.idxhuman] = DEFAULTLOGIT
                        if category == 3: # vehicle
                            predictionallframe[k,self.idxvehicle] = DEFAULTLOGIT
                        if humanboxes is not None: # humans in at least one frame
                            self.humanpresence[self.k1] = True
                    k = k+1
            videocap.release()
            if len(rangeanimal): # predicting species in frames with animal 
                predictionallframe[rangeanimal,0:len(txt_animalclasses[self.LANG])] = self.classifier.predictOnBatch(self.cropped_data[[k for k in rangeanimal],:,:,:], withsoftmax=False)
            self.predictedclass[self.k1], self.predictedscore[self.k1] = self._PredictorBase__averageLogitInSequence(predictionallframe)
            if len(rangenonempty): # selecting key frame to display when not empty
                self.prediction[self.k1,-1] = 0.
                # using max score
                if self.predictedclass[self.k1] == txt_classes[self.LANG][self.idxhuman]: # human
                    kmax = np.argmax(predictionallframe[rangenonempty,self.idxhuman])
                else:
                    if self.predictedclass[self.k1] == txt_classes[self.LANG][self.idxvehicle]: # vehicle
                        kmax = np.argmax(predictionallframe[rangenonempty,self.idxvehicle])
                    else: # animal
                        predictionallframeanimal = predictionallframe[rangenonempty,0:len(txt_animalclasses[self.LANG])]
                        kmax = np.unravel_index(np.argmax(predictionallframeanimal , axis=None), predictionallframeanimal.shape)[0]
                self.keyframes[self.k1] = kframetotal[rangenonempty[kmax]]
                self.bestboxes[self.k1] = bestboxesallframe[rangenonempty[kmax]]
            self.count[self.k1] = maxcount
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+1,self.fileManager.nbFiles())
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch

    def getKeyFrames(self, index):
        return self.keyframes[index]
        
    def getHumanPresence(self, k=None):
        if k == None:
            return self.humanpresence
        else:
            return self.humanpresence[k]
