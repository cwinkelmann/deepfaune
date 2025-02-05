#  WELCOME TO DEEPFAUNE SOFTWARE REPOSITORY


<img src="icons/logoINEE.png" width="50%" align=center>
<br>


---
# NEWS
---

## Feb 5, 2025
Release v1.3.0 is available for test.

* New categories 'bison','rein deer' and 'wolverine'  (in french 'bison', 'renne' and 'glouton').
* Even more efficient classification model, still based on vit_large_patch14_dinov2 architecture.
* Use of more icons instead of text in software design.
* Animal counts and human counts are managed independently, and displayed in the interface.
* Column 'HumanPresence' replaced by 'HumanCount'.


Supported categories/species : BADGER, BEAR, BEAVER, BIRD, BISON, CAT, CHAMOIS/ISARD, COW, DOG, EQUID, FALLOW DEER, FOX, GENET, GOAT, HEDGEHOG, IBEX, LAGOMORPH, LYNX, MARMOT, MICROMAMMAL, MOUFLON, MOOSE, MUSTELID, NUTRIA, OTTER, RACCOON, RED DEER, REIN DEER, ROE DEER, SHEEP, SQUIRREL, WILD BOAR, WOLF + HUMAN + VEHICULE + EMPTY 

Classification performance is available [here](https://plmlab.math.cnrs.fr/deepfaune/software/-/blob/master/README.md?ref_type=heads#performance).

## Oct 4, 2024
Release v1.2.0 is available on Windows, Linux and MacOS.  

Supported categories/species : BADGER, BEAR, BEAVER, BIRD, CAT, CHAMOIS/ISARD, COW, DOG, EQUID, FALLOW DEER, FOX, GENET, GOAT, HEDGEHOG, IBEX, LAGOMORPH, LYNX, MARMOT, MICROMAMMAL, MOUFLON, MUSTELID, NUTRIA, OTTER, RACCOON, RED DEER, ROE DEER, SHEEP, SQUIRREL, WILD BOAR, WOLF + HUMAN + VEHICULE + EMPTY 


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
| Classes | Validation | Out-of-sample Test | Val Support | Out-of-sample Test Support |
|---------|------------|------|-------------|--------------|
| bison / bison | 99,66% | 99,87% | 4363 | 4608 |
| blaireau / badger | 99,33% | 99,26% | 4315 | 4314 |
| bouquetin / ibex | 95,68% | NA | 880 | 0 |
| castor / beaver | 38,57% | 54,55% | 70 | 11 |
| cerf / red deer | 97,86% | 95,83% | 12322 | 80393 |
| chamois / chamois | 99,62% | 96,40% | 7710 | 5674 |
| chat / cat | 97,60% | 96,30% | 1832 | 1541 |
| chevre / goat | 98,81% | 82,35% | 758 | 1031 |
| chevreuil / roe deer | 99,29% | 97,86% | 13923 | 17935 |
| chien / dog | 96,69% | 95,30% | 1661 | 319 |
| daim / fallow deer | 99,39% | 95,26% | 12041 | 718 |
| ecureuil / squirrel | 98,98% | 92,09% | 1659 | 834 |
| elan / moose | 99,66% | 98,86% | 4770 | 3064 |
| equide / equid | 96,67% | 95,68% | 3061 | 324 |
| genette / genet | 99,04% | NA | 208 | 0 |
| glouton / wolverine | 98,56% | 89,71% | 209 | 272 |
| herisson / hedgehog | 95,24% | 100,00% | 63 | 8 |
| lagomorphe / lagomorph | 98,91% | 99,40% | 3683 | 3490 |
| loup / wolf | 98,62% | 99,34% | 1744 | 152 |
| loutre / otter | 82,44% | 100,00% | 131 | 2 |
| lynx / lynx | 99,22% | 100,00% | 1285 | 1047 |
| marmotte / marmot | 100,00% | 98,86% | 448 | 1488 |
| micromammifere / micromammal | 97,79% | 99,13% | 770 | 115 |
| mouflon / mouflon | 92,76% | 82,42% | 221 | 711 |
| mouton / sheep | 99,41% | 98,64% | 8780 | 6560 |
| mustelide / mustelide | 98,54% | 96,17% | 1303 | 2196 |
| oiseau / bird | 99,50% | 97,82% | 6054 | 6550 |
| ours / bear | 96,92% | 97,41% | 1362 | 1157 |
| ragondin / nutria| 76,99% | 53,33% | 113 | 30 |
| ratonlaveur / racoon | 98,95% | 98,00% | 1715 | 50 |
| renard / fox | 99,04% | 97,99% | 7521 | 16422 |
| renne / rein deer | 98,52% | 98,65% | 1421 | 518 |
| sanglier / wild boar | 98,49% | 98,90% | 7675 | 20135 |
| vache /cow | 99,49% | 98,07% | 6902 | 2545 |


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

