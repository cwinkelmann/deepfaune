#  WELCOME TO DEEPFAUNE SOFTWARE REPOSITORY


<img src="icons/logoINEE.png" width="50%" align=center>
<br>


---
# NEWS
---

## Oct 4, 2024
Release v1.2.0 is available on Windows, Linux and MacOS.  

* New categories 'beaver','fallow deer', 'otter' and 'raccoon'  (in french 'castor', 'daim', 'ragondin' and 'raton laveur').
* New column 'Top1' (predicted class, even below  the threshold) is now in csv/xslx export.
* Light modernization of the software design.
* More efficient classification model, still based on vit_large_patch14_dinov2 architecture.
* Videos and sequences can be played.
* Metadata can be displayed in a separate windows.
* Brightness can be changed.
* On Windows, images can be opened in explorer


Supported categories/species : BADGER, BEAR, BEAVER, BIRD, CAT, CHAMOIS/ISARD, COW, DOG, EQUID, FALLOW DEER, FOX, GENET, GOAT, HEDGEHOG, IBEX, LAGOMORPH, LYNX, MARMOT, MICROMAMMAL, MOUFLON, MUSTELID, NUTRIA, OTTER, RACCOON, RED DEER, ROE DEER, SHEEP, SQUIRREL, WILD BOAR, WOLF + HUMAN + VEHICULE + EMPTY 

Classification performances are available [here](https://plmlab.math.cnrs.fr/deepfaune/software/-/blob/master/README.md?ref_type=heads#performance).
---
# INSTALL
---

## FOR WINDOWS USERS
`Deepfaune` sofware is released under the [CeCILL](http://www.cecill.info) licence, compatible with [GNU GPL](http://www.gnu.org/licenses/gpl-3.0.html).

The latest versions are available at:
[https://pbil.univ-lyon1.fr/software/download/deepfaune/](https://pbil.univ-lyon1.fr/software/download/deepfaune/)

1. Download the latest `zip` file
2. Uncompress the file on your Desktop
3. Double-click on `deepfaune_installer.exe` to install the software on your computer


## FOR LINUX / MAC OS USERS (and WINDOWS  USERS used to Python)
`Deepfaune` sofware is released under the [CeCILL](http://www.cecill.info) licence, compatible with [GNU GPL](http://www.gnu.org/licenses/gpl-3.0.html).

### 1. Get the source code of the latest release, directly from this site. 

Option1 (latest version, recommended): clone the repository by clicking on the blue button above.

Option2 (latest stable version):  get the `zip` archive by clicking on the button `Download` (next to "Create release") on the last row of [https://plmlab.math.cnrs.fr/deepfaune/software/-/tags](https://plmlab.math.cnrs.fr/deepfaune/software/-/tags). 
Then, uncompress the zip file.

###  2. Download and unzip the model parameters
The model parameters are protected by the [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/) (Attribution-NonCommercial-ShareAlike 4.0 International).

Download the model parameters *inside the deepfaune folder* where you can find `deepfauneGUI.py`:

- Animal detector parameters: for version 1.1.x [deepfaune-yolov8s_960.pt](https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.1/)

- Classifier parameters: for version 1.2.x [deepfaune-vit_large_patch14_dinov2.lvd142m.v2.pt](https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.2/)

### 3. Install the dependencies

We need Python 3.x , plus additional dependencies:

- PyTorch: `pip install torch torchvision`
- Yolov8: `pip install ultralytics`
- Timm: `pip install timm`
- Pandas: `pip install pandas`
- Numpy: `pip install numpy`
- OpenCV: `pip install opencv-python`
- PIL: `pip install pillow`
- DILL: `pip install dill`
- hachoir: `pip install hachoir`
- (optional, for Excel users only) openpyxl: `pip install openpyxl`

For some users, it may be necessary to install `python-tk` or `python3-tk` as well, when you have a message `no module tkinter`...

**Setting up your Python environment:**

On Linux, it can be recommended to create a virtual environement with:
```
python3 -m venv envdeepfaune
source env/bin/activatedeepfaune
pip install XXX
```

On Mac (& Linux) it is also recommended to use Anaconda:
```
conda create -n deepfaune
conda activate deepfaune
pip install XXX
```

On Windows, install these dependencies using **[Anaconda Individual Edition](https://www.anaconda.com/products/individual)** (WARNING: during installation of Anaconda, you will be asked to choose a path to install Ananconda files. It will be `C:\Users\yourname\anaconda3` by default. PLEASE REMEMBER THIS PATH FOR FURTHER USE).

- Open Anaconda window, search for `torchvision` and click to install it, , as explained [here](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-packages/)
- and so on for the other dependencies listed above.

---
# USING DEEPFAUNE
---

### Running the Python script

In a terminal, launch `python deepfauneGUI.py` or `python.exe deepfauneGUI.py`

Now you can use the GUI !


### Using the API

You can implement your own scripts using the DeepFaune API. *Minimal examples* are available in the [demo/ directory](https://plmlab.math.cnrs.fr/deepfaune/software/-/tree/master/demo/).


---
# PERFORMANCE
---

We measured the performance (accuracy) of the classification model available in the latest stable release:
<br>

| Species    | Validation set | Out-of-sample Test set |
| -------- | ------- |------- |
| blaireau / badger      |     98,44% |  98,61% |
| bouquetin      |     91,74% | -       |
| castor / beaver        |          - |  30,21% |
| cerf / red deer          |     96,99% |  95,27% |
| chamois        |     98,08% |  95,72% |
| chat / cat          |     92,92% |  94,90% |
| chevre / goat        |     82,93% |  64,99% |
| chevreuil / roe deer     |     98,89% |  98,49% |
| chien / dog         |     88,67% |  94,08% |
| daim / fallow deer          |     99,01% |  93,09% |
| ecureuil / squirrel      |     99,03% |  97,49% |
| equide         |     99,64% |  81,13% |
| genette / genet       |     97,12% | -       |
| herisson / hedgehog       |     89,29% | 100,00% |
| lagomorphe     |     99,00% |  98,45% |
| loup / wolf          |     99,34% |  96,83% |
| loutre / otter    |     98,85% |  76,98% |
| lynx           |     99,08% |  95,22% |
| marmotte       |     99,11% |  99,26% |
| micromammifere / micromammals |     96,99% |  95,53% |
| mouflon        |     83,78% |  85,09% |
| mouton / sheep        |     99,69% |  97,58% |
| mustelide      |     96,58% |  96,53% |
| oiseau / bird        |     98,42% |  98,15% |
| ours / bear          |     83,97% |  97,52% |
| ragondin / nutria      |     76,80% |  33,33% |
| ratonlaveur / racoon    |     91,59% | 100,00% |
| renard / fox        |     98,07% |  98,58% |
| sanglier / wild boar      |     99,19% |  98,76% |
| vache / cow         |     99,86% |  93,02% |


---
# CONTACT
---

For any question, bug or feedback, feel free to send an email to [Vincent Miele](https://vmiele.gitlab.io/) <!--or use the Gitlab Service Desk-->


---
# LICENSE
---

All of the source code to this product is available under the [CeCILL](http://www.cecill.info), compatible with [GNU GPL](http://www.gnu.org/licenses/gpl-3.0.html).

All the model parameters (PyTorch weights in '.pt' files) are available under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Commercial use of any element of `DeepFaune` (code or model parameters) is forbidden.

Know your rights.


---
# REFERENCES
---

[Rig23] Rigoudy, N., Dussert G., the DeepFaune consortium, Spataro, B., Miele, V. & Chamaillé-Jammes, S. (2023) *The DeepFaune initiative: a collaborative effort towards the automatic identification of the European fauna in camera-trap images.* [European Journal of Wildlife Research](https://link.springer.com/article/10.1007/s10344-023-01742-7)

[Dus24] Dussert, G., Chamaillé-Jammes, S. Dray, S. &  Miele, V. (2024) *Being confident in confidence scores: calibration in deep learning models for camera trap image sequences* [Remote Sensing in Ecology and Conservation](https://zslpublications.onlinelibrary.wiley.com/doi/10.1002/rse2.412)

[Mie21] Miele, V., Dray, S., & Gimenez, O. (2021). *Images, écologie et deep learning.* [Regards sur la biodiversité](https://sfecologie.org/regard/r95-fev-2021-miele-dray-gimenez-deep-learning/)


---

# FREQUENTLY ASKED QUESTIONS

---

> How can I learn more about machine learning for ecology?

You can dig into [this paper list](https://ecostat.gitlab.io/imaginecology/papers.html).

> Is the `deepfaune` software free?

Yes, it is a free software, commercial use is forbidden (see LICENSE section). If you appreciate our work, please cite our work and/or contribute by sharing with us your annotated images.

> Can I have access to the images used in the DeepFaune project?

No. We do not share the images of our partners.

> Can I contribute to the DeepFaune project with my images?

It would be great!! You can contact us to see how you can send us your images (we have different solutions). We will store them in a secure server with private access to the members of the deepfaune project.
 
> Who is developing this DeepFaune project?

A team in CNRS-INEE leaded by Simon Chamaillé-Jammes (CEFE) and Vincent Miele (LBBE). Please have a look at our website [https://www.deepfaune.cnrs.fr/](https://www.deepfaune.cnrs.fr/).

<br>
<br>

---
---
Logo artwork: Rochak Shukla - www.freepik.com

