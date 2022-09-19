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

import sys
####################################################################################
### LOADING CLASSIFIER
####################################################################################
from os import environ

import numpy as np
import timm
import torch
import torch.nn as nn
from PIL import Image
from torchvision.transforms import InterpolationMode, transforms

from cv2 import cv2

CROP_SIZE = 300
NBCLASSE = 22
BACKBONE = "efficientnet_b3"
weight_path = "efficientnet_b3_22_produc3.pt"

txt_classes = {
    'fr': ["blaireau", "bouquetin", "cerf", "chamois", "chat", "chevreuil", "chien", "ecureuil", "equide", "lagomorphe",
           "loup", "lynx", "marmotte", "micromammifere", "mouflon", "mouton", "mustelide", "oiseau", "ours", "renard",
           "sanglier", "vache"],
    'gb': ["badger", "ibex", "deer", "chamois", "cat", "roe deer", "dog", "squirrel", "equid", "lagomorph", "wolf",
           "lynx", "marmot", "micromammal", "mouflon", "sheep", "mustelid" ",bird", "bear", "fox", "wild boar", "cow"]}


####################################################################################
### CLASSIFIER
####################################################################################
class Classifier:

    def __init__(self):
        self.model = Model(backbone=BACKBONE, num_classes=NBCLASSE)
        self.model.loadWeights(weight_path)
        self.transforms = transforms.Compose(
    [transforms.Resize((300, 300), interpolation=InterpolationMode.NEAREST),
         transforms.ToTensor()])

    def predictOnBatch(self, batchtensor, workers=1):
        return self.model.predict(batchtensor)

    # croppedimage in BGR loaded by opencv
    def preprocessImage(self, croppedimage):
        croppedimage = cv2.cvtColor(croppedimage, cv2.COLOR_BGR2RGB)
        croppedimagePil = Image.fromarray(croppedimage)
        batch = self.transforms(croppedimagePil)
        batch = batch.unsqueeze(dim=0)
        return batch


####################################################################################
### MODEL
####################################################################################

class Model(nn.Module):
    def __init__(self, backbone="efficientnet_b3", num_classes=10):
        """
        Constructor of model using pre-train image detector with classifier

        :param backbone: name of pre-train model (see >>>timm.list_models(pretrained=True))  : str
        :param num_classes: number of class for classification : int
        """
        super().__init__()
        if backbone not in timm.list_models(pretrained=True):
            raise Exception("{} is not a known pretrain model \n Please choose a model in this list :"
                            "({})".format(backbone, timm.list_models(pretrained=True)))
        self.base_model = timm.create_model(backbone, pretrained=True, num_classes=num_classes)
        self.backbone = backbone
        self.num_classes = num_classes

    def forward(self, input):
        x = self.base_model(input)
        return x

    def predict(self, data):
        """
        Predict on test DataLoader
        :param test_loader: test dataloader: torch.utils.data.DataLoader
        :return: numpy array of predictions without soft max
        """
        self.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        total_output = []
        with torch.no_grad():
            x = data.to(device)
            output = self.forward(x).softmax(dim=1)
            total_output += output.tolist()

        return np.array(total_output)

    def loadWeights(self, path):
        """
        :param path: path of .pt save of model
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if path[-3:] != ".pt":
            path += ".pt"

        print("#" * 20)
        print("\n Loading...")
        try:
            params = torch.load(path, map_location=device)
            args = params['args']
            if self.backbone != args['backbone']:
                raise Exception("You load a model ({}) that does not have the same architecture as the initial model "
                                "({})".format(args['backbone'], self.backbone))
            if self.num_classes != args['num_classes']:
                raise Exception("You load a model ({}) that does not have the same number of class"
                                "({})".format(args['num_classes'], self.num_classes))

            self.backbone = args['backbone']
            self.num_classes = args['num_classes']
            self.load_state_dict(params['state_dict'])
            print("\n The loading checkpoint was successful ! \n")
            print("\tModel : ", self.backbone)
            print("\tNumber of classes : ", self.num_classes)
            print("")
        except Exception as e:
            print("\n/!\ Can't load checkpoint model /!\ because :\n\n " + str(e), file=sys.stderr)
            raise e
        print("#" * 20)
