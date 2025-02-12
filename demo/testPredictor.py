# Copyright CNRS 2024

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
import os
import time
import typing
from pathlib import Path
import pandas as pd
from loguru import logger

from predictTools import PredictorImage


def find_images(images_dir: Path):
    """
    Find all images in the test directory
    """
    assert images_dir.exists(), f"Directory {images_dir} does not exist"

    return sorted(
        [f for f in images_dir.rglob('*.[Jj][Pp][Gg]')] +
        [f for f in images_dir.rglob('*.[Jj][Pp][Ee][Gg]')] +
        [f for f in images_dir.rglob('*.[Bb][Mm][Pp]')] +
        [f for f in images_dir.rglob('*.[Tt][Ii][Ff]')] +
        [f for f in images_dir.rglob('*.[Gg][Ii][Ff]')] +
        [f for f in images_dir.rglob('*.[Pp][Nn][Gg]')]
    )

# if (len(sys.argv)!=3):
#     print("Usage: python testPredictor.py <IMAGEPATH> <CSVFILENAME>")
#     exit()

## IMPORT DEEPFAUNE CLASSES
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
curdir = Path("/Users/christian/PycharmProjects/hnee/deepfaune_software/demo")
# sys.path.append(curdir+'/../') # to add the deepfaune path

def prediction_wrapper(filenames: typing.List[Path])->pd.DataFrame:
    """
    wrap the prediction logic into a one liner
    """

    ## PREDICTOR OBJECT
    LANG = 'en'
    maxlag = 20
    threshold = 0.5
    BATCH_SIZE = 16

    predictor = PredictorImage(filenames, threshold, maxlag, LANG, BATCH_SIZE=BATCH_SIZE)
    ## RUNNING BATCHES OF PREDICTION
    ## ONE AT A TIME
    while True:
        batch_start_time = time.time()  # Start timing the batch

        batch, k1, k2, k1seq, k2seq = predictor.nextBatch()
        if k1 == len(filenames): break
        print(f"current batch: {batch} out of {len(filenames)//BATCH_SIZE}")
        batch_end_time = time.time()  # Start timing the batch
        print(f"Batch time: {batch_end_time - batch_start_time:.3f} seconds. Time per image: {(batch_end_time - batch_start_time) / BATCH_SIZE:.3f} seconds")


    ## OR ALL TOGETHER
    # predictor.allBatch()

    ## GETTING THE RESULTS
    ## without using the sequences
    # predictedclass_base, predictedscore_base, best_boxes, count = predictor.getPredictionsBase()
    # or using the sequences
    predictedclass, predictedscore, best_boxes, count = predictor.getPredictions()
    ## OUTPUT
    dates = predictor.getDates()
    seqnum = predictor.getSeqnums()
    preddf = pd.DataFrame({'filename': predictor.getFilenames(),
                           'dates': predictor.getDates(),
                           'seqnum': seqnum,
                           # 'predictionbase': predictedclass_base,
                           #'scorebase': predictedscore_base,
                           'prediction': predictedclass,
                           'score': predictedscore,
                           'count': count,
                           "getPredictedTop1": predictor.getPredictedTop1()
                           })
    return preddf



