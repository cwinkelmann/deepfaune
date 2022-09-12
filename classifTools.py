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
from os import environ

import torch
from matplotlib import pyplot as plt
from torchvision.transforms import InterpolationMode, transforms

from devtest.model import Model

environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # silencing TensorFlow
from cv2 import cvtColor,COLOR_BGR2RGB,resize

CROP_SIZE = 300
NBCLASSE = 22
BACKBONE = "efficientnet_b3"
weight_path = "efficientnet_b3_22_produc3.pt"

txt_classes = {'fr':["blaireau","bouquetin","cerf","chamois","chat","chevreuil","chien","ecureuil","equide","lagomorphe","loup","lynx","marmotte","micromammifere","mouflon","mouton","mustelide" ,"oiseau","ours","renard","sanglier","vache"]  ,
              'gb':["badger", "ibex", "deer", "chamois", "cat", "roe_deer", "dog", "squirrel", "equid", "lagomorph", "wolf", "lynx", "marmot", "small_mammal", "mouflon", "sheep", "mustelid" ",bird", "bear", "fox", "wild_boar", "cow"]}

    
####################################################################################
### CLASSIFIER 
####################################################################################
class Classifier:
    
    def __init__(self):
        self.model = Model(backbone=BACKBONE, num_classes=NBCLASSE)
        self.model.load_weights(weight_path)
        self.transforms = transforms.Compose(
    [transforms.ToPILImage(),transforms.Resize((300, 300), interpolation=InterpolationMode.NEAREST),
         transforms.ToTensor()])
        
    def predictOnBatch(self, batchtensor, workers=1):
        return self.model.predict(batchtensor)

    # croppedimage in BGR loaded by opencv
    def preprocessImage(self, croppedimage):
        batch = self.transforms(croppedimage)
        #gestion plusieurs images
        if len(batch.shape) == 3:
            batch = batch.unsqueeze(dim=0)
        return batch
