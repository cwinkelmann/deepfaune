# DEEPFAUNE SOFTWARE USER MANUAL (v0.2)

---
## GENERAL PRESENTATION
---
This document describes the DeepFaune software that is a **graphical interface for users to easily use the classification model 
developed by our team to automatically sort out camera-trap images.** Installation steps, user guidelines and an example of how to use this software are described below. The DeepFaune software can be used on a standard personal computer (PC) with Windows, Linux or MacOS operating systems. 

This software is part of an on-going research project and thus evolves regularly. Updates are available here [https://www.deepfaune.cnrs.fr/].

---
## OVERVIEW
---
### Features

The DeepFaune software offers a user-friendly interface to make **locally-stored image classification** easy. The user simply needs to select the folder containing the images to classify and to launch the program. The classification model then predicts, for each image, **if the image is empty or contains a given taxonomic group** detected with the highest confidence score (eg. the image may be predicted as containing a red deer with 92% confidence). 

The **results are available as a table** (`.csv` or `.xlsx` format) associating each image to its predicted class and to the confidence score. The classified images can then be stored in **taxa-specific sub-directories**, enabling to store all the images containing a given taxonomic group in the same folder.

The user needs to set two parameters to run the model: the minimum confidence threshold as well as the maximum time difference within a sequence of images. Both parameters are explained hereafter.

The **confidence threshold** is the miminum threshold for which a prediction is kept (eg. with a 50% threshold, any image predicted with a score under 50% will be predicted as "uncertain"). Setting a high confidence threshold enables to classify images quickly and with little error, but it leaves the user with more images to classify by hand (as they are then classified as "uncertain). Setting a low confidence threshold will inversely produce less "uncertain" images but the overall quality of predictions will be lower. The best threshold value then depends on a number of factors, such as the aim of the study, the studied species, if the user is able to manually sort out more "uncertain" images etc. We leave the user to decide on which value to set. 

Certain camera traps are programmed to take a series of photos for each trigger event (eg. the camera-trap is set on "burst mode", taking three consecutive photos when it is triggered by movement). We consider these consecutive images as part of the same "sequence", which all belong to a single detection event. The **maximum time difference** within a sequence enables to identify images beloning to the same camera-trap event thanks to the date saved in the exif. This time difference corresponds to the maximum time between two consecutive images for them to be considered as belonging to the same "sequence" (eg. with a 2 seconds time difference, all consecutive images that are within 2 seconds from each other are predicted as belonging to the same class). 

CAREFUL: The information concerning where the images were taken ("study area") does not exist in our dataset. The user must then be careful to store images taken in different sites in seperate folders. If the images of different sites are pooled together in the same folder, the model's "sequence" information will be incorrect. 


### Interface layout

The interface is composed of one main window, subdivided in different tabs: 

- a first tab with the commands enabling to select the folder with images to classify, define the classification parameters and the list of real-time commands that are performed by the software
- a second tab with a window to visualize the results in table format and options to choose the output modalities


A second window allows the user to visualize the images and their associated predictions. 


---
## INSTALLATION
---

The`DeepFaune` softwarea can be run on a standard computer. 

#### For users with Windows
**No technical pre-requisits, no prior installation needed.**

- Download the `.zip` archive correponding to the latest version on [https://pbil.univ-lyon1.fr/software/download/deepfaune/](https://pbil.univ-lyon1.fr/software/download/deepfaune/)
- Extract the files from the `.zip` file in the folder of your choice
- Click on `deepfauneGUI.exe` (careful, launching may take several seconds).

#### For users with Linux, Mac (ou Windows that have notions on how to used Python)
Refer to the instructions available at: [https://plmlab.math.cnrs.fr/deepfaune/software](https://plmlab.math.cnrs.fr/deepfaune/software).


---
## USER GUIDELINES
---

#### STEP 1 : Launch the software
Windows : Double-click on `deepfauneGUI.exe`

Linux / Mac OS : In the terminal, launch `python deepfauneGUI.py`

#### STEP 2 : Choice of language
The first window to open enables the user to select the language; select French (Français) or English.

#### STEP 3 : Loading parameters
The program will load the parameters of the classification model. This step can take a few seconds.

#### STEP 4 : Select the folder containing the images that need to be classified 
Select the folder to sort out by clicking on the "Choose" button, on the higher left corner in the Image folder section. The images that need classification need to be stored in the same parent folder.

#### STEP 5 : Define the confidence threshold 
The confidence threshold is the miminum threshold for which a prediction is kept (eg. with a 50% threshold, any image predicted with a score under 50% will be predicted as "uncertain").
Select the confidence threshold in the "Confidence threshold" section by increasing/decreasing the value using the up/down arrows on the right.

#### STEP 6 : Define the maximum time difference within a sequence
The maximum time difference within a sequence corresponds to the maximum time between two consecutive images for them to be considered as belonging to the same "sequence" (eg. with a 2 seconds time difference, all consecutive images that are within 2 seconds from each other are predicted as belonging to the same class). 
Select the maximum time difference within a sequences (in seconds) in the "Max delay / sequence" section by increasing/decreasing the value using the up/down arrows on the right.

#### STEP 7 : Launch the prediction

Once the parameter values have been defined, launch the prediction by clicking on the "Launch" button.
The processing bar will fill up as the model completes each task. It is full when the program has finished.

Several command lines will appear. The lines that appear keep track of all the tasks that are performed by the program. These lines indicate which folder has been selected, the number of images contained in the folder, how many tasks have been completed (in batches = groups of images that are classified at the same time) and the autocorrection steps that are performed according to the sequence paramater.

#### STEP 8 : Visualizing the results in a table
The predictions appear in a table, on the second tab, which contains the name of the file, the prediction and the confidence score that are associated to the prediction, for each line. 

#### STEP 9 : Visualizing the results as a slide show
The images that have been classified by the model can be visualized independently in a seperate window by clicking on the "Display images" button. This will display all the images for which predictions have been made. 
To display only a single image, the user must select the image in the table section of the interace by clicking on it (it then becomes highlighted) and the click on the button "Display selected image".

Once the predictions are completed, **a new window for visualizing the results as a slide show is available by clicking on the "Display images" button. This new window enables to:

- manually verify the predictions made by the model for each image in the dataset
- modify the prediction if the latter is considered incorrect.

The display window is composed of a section displaying the image, the association prediction ("Prediction") and the buttons enabling to perform the following actions. 

To navigate between images, click on the "Next" and "Previous" buttons.
To select only certain images, choose the "All images", "Undefined images", "Empty images" or "Non-empty images".

To exit this display window, click on the "Close" button.

#### STEP 10 : Correcting the results in the slide show 
To modify the predictions of the model, type in the name of the correct class in the "Prediction" section  or select among the avaialble classes thanks to the drop-down menu (click on the small arrow on the right)

To exit this window, click on the "Close" button.


#### STEP 11 : Save the results in CSV or XLSX format 
The results are available as table in `.csv` and `.xlsx` formats. To save the results as a table, click on the button "Save to CSV" or "Save to XLSX" according to the chosen format. 


#### STEP 11 bis : Saving the results in seperate sub-directories
The results are saved in the parent folder (containing the iamges to classify) in a folder named « deepdaune_{DATE}_{TIME} ». The date and time contained in the name of the folder are the date and time when the user launched the program. 
The images are then organized by taxonomic group; all images predicted as the same taxonomic group are saved under the same sub-folder. **Each sub-folder is identified using the name of the taxonomic group** and is savec in the results folder « deepdaune_{DATE}_{HEURE} ».

Comment : The images can be organized according to 2 modalities by choosing either "Copy files" or "Move files" BEFORE creating the sb-folders: 

- by copying the image files from the parent folder to the new taxon-specific sub-folders
- by moving the image files from the parent folder to the new taxon-specific sub-folders.

---
## LICENSE
---
DeepFaune is developed under est a CeCILL licence, compatible with GNU GPL. The use of part or all the DeepFaune software for commercial purposes is strictly prohibitted.

---
## CONTACT
---
For any question or comment, please contact Simon et Vincent:

simon.chamaille@cefe.cnrs.fr / vincent.miele@univ-lyon1.fr
