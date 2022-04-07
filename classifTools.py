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

####################################################################################
### LOADING CLASSIFIER
####################################################################################
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D,Activation
from tensorflow.keras.models import Model
from keras.applications.resnet_v2 import ResNet50V2
from tensorflow.keras.applications.efficientnet import EfficientNetB3
import numpy as np

backbone = "efficientnet"
hdf5 = "efficientnet_22classesOnlycroppedImgAugB3.hdf5"
workers = 1

class Classifier:
    
    def __init__(self, classes, nbfiles):
        self.nbclasses=len(classes)
        if backbone == "resnet":
            base_model = ResNet50V2(include_top=False, weights=None, input_shape=(300,300,3))
        elif backbone == "efficientnet":
            base_model = EfficientNetB3(include_top=False, weights=None, input_shape=(300,300,3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        #x = Dense(512)(x) #256,1024, etc. may work as well
        x = Dense(self.nbclasses)(x) #number of classes
        preds = Activation("softmax")(x)
        self.model = Model(inputs=base_model.input,outputs=preds)
        self.model.load_weights(hdf5)
        nbclasses=len(classes)
        self.prediction = np.zeros(shape=(nbfiles,nbclasses+1), dtype=np.float32)
        self.prediction[:,nbclasses] = 1 # by default, predicted as empty
        self.classes = classes
        
    def predicting(self, nbfiles, cropped_data, idxnonempty, k1):
        
        if len(idxnonempty):
            self.prediction[idxnonempty,0:self.nbclasses] = self.model.predict(cropped_data[[idx-k1 for idx in idxnonempty],:,:,:], workers=workers)
            self.prediction[idxnonempty,self.nbclasses] = 0 # not empty
        return self.prediction
