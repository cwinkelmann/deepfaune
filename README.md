#  WELCOME TO DEEPFAUNE SOFTWARE REPOSITORY


<img src="img/1316.jpg" width="20%">
<img src="img/logoINEE.png" width="50%" align=right>

---
WARNING : our software is still under development. Model parameters (section 3) are not publicly available yet. 
---

---

# 1. INSTALLING DEEPFAUNE SOFTWARE

---

**STEP 1**

First of all, get the `zip` archive by clicking on the button ![button](img/button.jpg) on the top right of this page.

This will open the following window where you can dowload the whole directory as a `zip` file (warning, it's a huge file):

![button](img/buttonzip.jpg) 

Then, uncompress the zip file on your Desktop.

**STEP 2**

**Linux:**

- Python 3.x (and `pip` which might be called `pip3` on your system)
- Tensorflow: `pip install tensorflow`
- Pandas: `pip install pandas`
- Numpy: `pip install numpy`
- PIL: `pip install pillow`
- (optional) openpyxl: `pip install openpyxl`

Alternatively, you can use `conda`.

**Windows**

- Anaconda Individual Edition: available [here](https://www.anaconda.com/products/individual) (install can take time)

WARNING: during installation, you will be asked to choose a path to install Ananconda files. It will be `C:\Users\yourname\anaconda3` by default. PLEASE REMEMBER THIS PATH FOR FURTHER USE.

- Open Anaconda window, search for `tensorflow` and click to install it, , as explained [here](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-packages/)

- (optional) Open Anaconda window, search for `openpyxl` and click to install it

- Edit file `deepfauneGUI.bat` and replace `\Users\Laurie\anaconda3` by the path that you chose just before


---

# 2. DOWNLOADING DEEPFAUNE MODEL PARAMETERS (not available - in progress)
---
Download the model parameters inside the folder where you can find `deepfauneGUI.py`:

- Animal detector parameters: [checkpoints.zip](http://)

- Classifier parameters: [efficientnet_MDcheckOnlycroppedImgAug.hdf5](http://)

Then unzip the file `checkpoints.zip` and you are done !

---

# 3. RUNNING DEEPFAUNE SOFTWARE

---

**Linux**

In a terminal, launch `python deepfauneGUI.py`

**Windows**

Click on `deepfauneGUI.bat` or `deepfauneGUI.vbs`

HAVE FUN NOW !!

---

# 4. CONTACT

---

For any question, bug or feedback, feel free to send an email to [Vincent Miele](https://lbbe.univ-lyon1.fr/-Miele-Vincent-.html) <!--or use the Gitlab Service Desk-->


---

# 5. LICENCE

---

`deepfaune` is released under the [CeCILL](http://www.cecill.info) licence, compatible with [GNU GPL](http://www.gnu.org/licenses/gpl-3.0.html)

Commercial use of any element of `deepfaune` is forbidden.

---

# 6. TROUBLESHOOTING

---

**T1:** How can I learn more about machine learning ?

You can watch these [series of 3 french videos](https://imaginecology.sciencesconf.org) (video 1 is the easiest).

<br>
<br>

---
---
Logo artwork: Rochak Shukla - www.freepik.com

