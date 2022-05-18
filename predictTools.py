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

from detectTools import Detector
from classifTools import Classifier
from sequenceTools import ImageBoxDiff

from detectTools import YOLO_SIZE
from classifTools import CROP_SIZE, NBCLASSES

BATCH_SIZE = 8

class Predictor:
    
    def __init__(self, df_filename, threshold, txt_classesempty, txt_undefined):
        self.df_filename = df_filename
        self.cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
        self.nbclasses=len(txt_classesempty)-1
        self.nbfiles = self.df_filename.shape[0]
        self.prediction = np.zeros(shape=(self.nbfiles, self.nbclasses+1), dtype=np.float32)
        self.prediction[:,self.nbclasses] = 1 # by default, predicted as empty
        self.predictedclass_base = []
        self.predictedscore_base = []
        self.txt_classesempty = txt_classesempty
        self.txt_undefined = txt_undefined
        self.threshold = threshold
        self.detector = Detector()
        self.classifier = Classifier()
        self.idiff = ImageBoxDiff()
        if (self.nbclasses!=NBCLASSES):
            raise SystemExit('Incoherent number of classes between classes list and classifier shape.')
        self.resetBatch()
    
    def prediction2class(self, prediction):
        class_pred = [self.txt_undefined for i in range(len(prediction))] 
        score_pred = [0. for i in range(len(prediction))] 
        for i in range(len(prediction)):
            pred = prediction[i]
            if(max(pred)>=self.threshold):
                class_pred[i] = self.txt_classesempty[np.argmax(pred)]
            score_pred[i] = int(max(pred)*100)/100.
        return class_pred, score_pred

    def resetBatch(self):
        self.k1 = 0 # batch start
        self.k2 = min(self.k1+BATCH_SIZE,self.nbfiles) # batch end
        self.batch = 1 # batch num

    def nextBatch(self):
        if self.k1>=self.nbfiles:
            return self.batch, self.k1, self.k2, [],[]
        else:
            idxnonempty = []
            for k in range(self.k1,self.k2):
                image_path = str(self.df_filename["filename"][k])
                original_image = cv2.imread(image_path)
                similarityWithPreviousImage = self.idiff.nextSimilarity(original_image)
                if similarityWithPreviousImage<0.99:
                    if original_image is None:
                        pass # Corrupted image, considered as empty
                    else:
                        croppedimage, nonempty = self.detector.bestBoxDetection(original_image)
                        if nonempty:
                            self.cropped_data[k-self.k1,:,:,:] =  self.classifier.preprocessImage(croppedimage)
                            idxnonempty.append(k)
                else:
                    #print("Images",self.df_filename["filename"][k-1],"and",self.df_filename["filename"][k],"are identical => predicted as empty")
                    try:
                        idxnonempty.remove(k-1)
                    except:
                        pass
                    self.prediction[k-1,0:self.nbclasses] = 0
                    self.prediction[k-1,self.nbclasses] = 1 # previous is also empty since too similar
            if len(idxnonempty):
                self.prediction[idxnonempty,0:self.nbclasses] = self.classifier.predictOnBatch(self.cropped_data[[idx-self.k1 for idx in idxnonempty],:,:,:], cv2.getNumThreads())
                self.prediction[idxnonempty,self.nbclasses] = 0 # not empty
            predictedclass_batch, predictedscore_batch = self.prediction2class(self.prediction[self.k1:self.k2,])
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+BATCH_SIZE,self.nbfiles)
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch, predictedclass_batch, predictedscore_batch
    
    def allBatch(self):
        self.resetBatch()
        while self.k1<self.nbfiles:
            pred.nextBatch()
        
    def getPredictions(self):
        self.predictedclass_base, self.predictedscore_base = self.prediction2class(self.prediction)  
        return self.predictedclass_base, self.predictedscore_base
                



class PredictorVideo(Predictor):
    
    def __init__(self, df_filename, threshold, txt_classesempty, txt_undefined):
         super().__init__(df_filename, threshold, txt_classesempty, txt_undefined) # inherits all

    def resetBatch(self):
        self.k1 = 0
        self.k2 = 1
        self.batch = 1
    
    def nextBatch(self):
        if self.k1>=self.nbfiles:
            return self.batch, self.k1, self.k2, [],[]
        else:   
            idxnonempty = []      
            video_path = str(self.df_filename["filename"][self.k1])   
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(video.get(5))
            duration= int(total_frames / fps)
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
            predictedclass_batch, predictedscore_batch = self.prediction2class(self.prediction[self.k1:self.k2,], cv2.getNumThreads())   
            k1_batch = self.k1
            k2_batch = self.k2
            self.k1 = self.k2
            self.k2 = min(self.k1+1,self.nbfiles)
            self.batch = self.batch+1  
            return self.batch-1, k1_batch, k2_batch, predictedclass_batch, predictedscore_batch
    
