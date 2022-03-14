#  WELCOME TO DEEPFAUNE SOFTWARE REPOSITORY


<img src="icons/1316.jpg" width="20%">
<img src="icons/logoINEE.png" width="50%" align=right>



---
# FOR WINDOWS USERS
---

The latest versions are available at:
[https://pbil.univ-lyon1.fr/software/download/deepfaune/](https://pbil.univ-lyon1.fr/software/download/deepfaune/)

1. Download the latest `zip` file
2. Uncompress the file on your Desktop
3. Double-click on `deepfauneGUI.exe`


---
# FOR LINUX USERS (or WINDOWS USERS used to Python)
---

### 1. Get the source code of the latest release, directly from this site. 
First of all, get the `zip` archive by clicking on the button ![button](icons/button.jpg) on the top right of [https://plmlab.math.cnrs.fr/deepfaune/software/-/tags](the TAGS page). This will open the following window where you can download the whole directory as a `zip` file (warning, it's a huge file):
![button](icons/buttonzip.jpg) 
Then, uncompress the zip file.

### 2. Install the prerequisites

On Linux or Windows with PyPi:

- Python 3.x (and `pip` which might be called `pip3` on your system)
- Tensorflow: `pip install tensorflow`
- Pandas: `pip install pandas`
- Numpy: `pip install numpy`
- PIL: `pip install pillow`
- (optional) openpyxl: `pip install openpyxl`

On Windows with [Anaconda Individual Edition](https://www.anaconda.com/products/individual) (install can take time):

WARNING: during installation, you will be asked to choose a path to install Ananconda files. It will be `C:\Users\yourname\anaconda3` by default. PLEASE REMEMBER THIS PATH FOR FURTHER USE.

- Open Anaconda window, search for `tensorflow` and click to install it, , as explained [here](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-packages/)
- (optional) Open Anaconda window, search for `openpyxl` and click to install it

###  3. Download the model parameters
Download the model parameters inside the folder where you can find `deepfauneGUI.py`:
- Animal detector parameters: [checkpoints.zip](https://pbil.univ-lyon1.fr/software/download/deepfaune/)
- Classifier parameters: [efficientnet_xxxx.hdf5](https://pbil.univ-lyon1.fr/software/download/deepfaune/)

Then unzip the file `checkpoints.zip` and you are done !


#### 4. Running the Python script

In a terminal, launch `python deepfauneGUI.py` or `python.exe deepfauneGUI.py`

HAVE FUN NOW !!

---
# CONTACT
---

For any question, bug or feedback, feel free to send an email to [Vincent Miele](https://lbbe.univ-lyon1.fr/-Miele-Vincent-.html) <!--or use the Gitlab Service Desk-->


---
# LICENCE
---

`deepfaune` is released under the [CeCILL](http://www.cecill.info) licence, compatible with [GNU GPL](http://www.gnu.org/licenses/gpl-3.0.html)

Commercial use of any element of `deepfaune` is forbidden.

---
# REFERENCES
---

[Rig22] Rigoudy, N., the DeepFaune consortium, Spataro, B., Miele, V. & Chamaillé-Jammes, S. (2022) *The DeepFaune initiative: a collaborative effort towards the automatic identification of the French fauna in camera-trap images.* Preprint bioRxiv

[Mie21] Miele, V., Dray, S., & Gimenez, O. (2021). *Images, écologie et deep learning.* Regards sur la biodiversité.


---

# FREQUENTLY ASKED QUESTIONS

---

**T1:** How can I learn more about machine learning ?

You can watch these [series of 3 french videos](https://imaginecology.sciencesconf.org) (video 1 is the easiest).

**T2:** Is the `deepfaune` software free ?

Yes. But, if you appreciate our work, please contribute by sharing with us your annotated images. You can contact us to see how you can send us your images (we have different solutions). We will store them in a secure server with private access to the members of the deepfaune project.

**T3:** Can I have access to the images used in the DeepFaune project ?

No. We do not share the images of our partners.

 
<br>
<br>

---
---
Logo artwork: Rochak Shukla - www.freepik.com

