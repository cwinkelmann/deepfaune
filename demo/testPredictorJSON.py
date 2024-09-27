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
import pandas as pd

if (len(sys.argv)!=3):
    print("Usage: python testPredictor.py <JSONFILENAME> <CSVFILENAME>")
    exit()


## IMPORT DEEPFAUNE CLASSES
curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../') # to add the deepfaune path

from predictTools import PredictorJSON

## JSON FILE
jsonfilename = sys.argv[1]

## PREDICTOR OBJECT
LANG = 'en'
maxlag = 20
threshold = 0.5
predictor = PredictorJSON(jsonfilename, threshold, maxlag, LANG)

## RUNNING BATCHES OF PREDICTION
predictor.allBatch()

## GETTING THE RESULTS
## without using the sequences
predictedclass_base, predictedscore_base, best_boxes, count = predictor.getPredictionsBase()
## or using the sequences
predictedclass, predictedscore, best_boxes, count = predictor.getPredictions()

## OUTPUT
filenames = predictor.getFilenames()
dates = predictor.getDates()
seqnum = predictor.getSeqnums()
preddf = pd.DataFrame({'filename':filenames, 'dates':dates, 'seqnum':seqnum, 'predictionbase':predictedclass_base, 'scorebase':predictedscore_base, 'prediction':predictedclass, 'score':predictedscore})
preddf.to_csv(sys.argv[2], index=False)
print('Done, results saved in '+sys.argv[2])
