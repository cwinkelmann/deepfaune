import sys
import numpy as np
import timm
import torch
import torch.nn as nn
from timm.optim import create_optimizer_v2
from timm.scheduler import CosineLRScheduler
from torchmetrics import Accuracy
from tqdm import tqdm
import torch.autograd.profiler as profiler
from torch.profiler import profile, tensorboard_trace_handler, ProfilerActivity, schedule


class Model(nn.Module):
    def __init__(self, backbone="resnet50", num_classes=10):
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

    def load_weights(self, path):
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
