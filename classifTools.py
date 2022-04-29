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
from tensorflow.keras.applications.efficientnet import EfficientNetB3
from tensorflow.keras.applications.efficientnet import preprocess_input
from cv2 import cvtColor,COLOR_BGR2RGB,resize

CROP_SIZE = 300
hdf5 = "efficientnet_22classesOnlycroppedImgAugB3.hdf5"
txt_classes = {'fr':["blaireau","bouquetin","cerf","chamois","chat","chevreuil","chien","ecureuil","humain","lagomorphe","loup","lynx","marmotte","micromammifere","mouflon","mouton","mustelide","oiseau","renard","sanglier","vache","vehicule"],
              'gb':["badger","ibex","red deer","chamois","cat","roe deer","dog","squirrel","human","lagomorph","wolf","lynx","marmot","micromammal","mouflon","sheep","mustelide","bird","fox","wild boar","cow","vehicle"]}
NBCLASSES = len(txt_classes['fr'])
    
####################################################################################
### CLASSIFIER 
####################################################################################
class Classifier:
    
    def __init__(self):
        base_model = EfficientNetB3(include_top=False, weights=None, input_shape=(CROP_SIZE,CROP_SIZE,3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(NBCLASSES)(x) #number of classes
        preds = Activation("softmax")(x)
        self.model = Model(inputs=base_model.input,outputs=preds)
        self.model.load_weights(hdf5)
        
    def predictOnBatch(self, batchtensor, workers=1):
        return self.model.predict(batchtensor, workers=workers)
    
    def preprocessImage(self, croppedimage):
        # Convert img to RGB
        croppedimage2classifier =  resize(cvtColor(croppedimage, COLOR_BGR2RGB), (CROP_SIZE,CROP_SIZE))
        # This method does nothing and only kept as a placeholder
        # to align the API surface between different versions of model
        return preprocess_input(croppedimage2classifier)
