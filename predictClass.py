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

from detectTools import detecting
import classifTools
from sequenceTools import reorderAndCorrectPredictionWithSequence
import numpy as np
from PIL import Image

txt_undefined = {'fr':"indéfini", 'gb':"undefined"}
txt_empty = {'fr':"vide", 'gb':"empty"}
txt_classes = {'fr':["blaireau","bouquetin","cerf","chamois","chat","chevreuil","chien","ecureuil","humain","lagomorphe","loup","lynx","marmotte","micromammifere","mouflon","mouton","mustelide","oiseau","renard","sanglier","vache","vehicule"],
              'gb':["badger","ibex","red deer","chamois","cat","roe deer","dog","squirrel","human","lagomorph","wolf","lynx","marmot","micromammal","mouflon","sheep","mustelide","bird","fox","wild boar","cow","vehicle"]}

YOLO_SIZE=608
CROP_SIZE=300
BATCH_SIZE = 8

class Predict:
    
    def __init__(self, df_filename, maxlag, threshold, LANG):
        self.df_filename = df_filename
        self.cropped_data = np.ones(shape=(BATCH_SIZE,CROP_SIZE,CROP_SIZE,3), dtype=np.float32)
        self.predictedclass_base = []
        self.predictedscore_base = []
        self.predictedclass = []
        self.predictedscore = []
        self.seqnum = []
        self.maxlag = maxlag
        self.LANG = LANG
        self.classes = txt_classes[LANG]
        self.classesempty = self.classes + [txt_empty[LANG]]
        self.threshold = threshold
        self.nbfiles = self.df_filename.shape[0]
        self.classifier = classifTools.Classifier(self.classes, self.nbfiles)
    
    def prediction2class(self, prediction):
        class_pred = [txt_undefined[self.LANG] for i in range(len(prediction))] 
        score_pred = [0. for i in range(len(prediction))] 
        for i in range(len(prediction)):
            pred = prediction[i]
            if(max(pred)>=self.threshold):
                class_pred[i] = self.classesempty[np.argmax(pred)]
            score_pred[i] = int(max(pred)*100)/100.
        return class_pred, score_pred
    
    def getPredictions(self):
        k1 = 0
        k2 = min(k1+BATCH_SIZE,self.nbfiles)
        batch = 1
        images_data = np.empty(shape=(1,YOLO_SIZE,YOLO_SIZE,3), dtype=np.float32)
        while(k1<self.nbfiles):
            #frgbprint("Traitement du batch d'images "+str(batch)+"...", "Processing batch of images "+str(batch)+"...", end="")
            idxnonempty = []
            for k in range(k1,k2):
                ## LOADING image and convert ton float 32 numpy array
                image_path = self.df_filename["filename"][k]
                try:
                    original_image = Image.open(image_path)
                    original_image.getdata()[0]
                except OSError:
                    pass # Corrupted image, considered as empty
                else:
                    resized_image = original_image.resize((YOLO_SIZE, YOLO_SIZE))
                    image_data = np.asarray(resized_image).astype(np.float32)
                    image_data = image_data / 255. # PIL image is int8, this array is float32 and divided by 255
                    images_data[0,:,:,:] = image_data
                    self.cropped_data =  detecting(self.cropped_data, images_data, k1, k, idxnonempty, CROP_SIZE)
            ## Update
            #window['-PROGBAR-'].update_bar(batch*BATCH_SIZE/nbfiles)
            #frgbprint(" terminé", " done")
            prediction = self.classifier.predicting(self.nbfiles, self.cropped_data, idxnonempty, k1, self.classes, self.LANG)
            predictedclass_batch, predictedscore_batch = self.prediction2class(prediction[k1:k2,])
            #window.Element('-TABRESULTS-').Update(values=np.c_[[basename(f) for f in df_filename["filename"][k1:k2]], predictedclass_batch, predictedscore_batch].tolist())
            k1 = k2
            k2 = min(k1+BATCH_SIZE,self.nbfiles)
            batch = batch+1
        #frgbprint("Autocorrection en utilisant les séquences...", "Autocorrecting using sequences...", end="")
        self.predictedclass_base, self.predictedscore_base = self.prediction2class(prediction)        
        self.df_filename, self.predictedclass_base, self.predictedscore_base, self.predictedclass, self.predictedscore, self.seqnum = reorderAndCorrectPredictionWithSequence(self.df_filename, self.predictedclass_base, self.predictedscore_base, self.maxlag, self.LANG)
        return self.df_filename, self.predictedclass_base, self.predictedscore_base, self.predictedclass, self.predictedscore, self.seqnum
                






