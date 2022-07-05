import sys
import os
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from predictTools import PredictorJSON

LANG = 'gb'
maxlag = 20
threshold = 0.5

predictor = PredictorJSON(sys.argv[1], threshold, LANG)
predictor.allBatch()
filenames = predictor.getFileNames()
predictedclass_base, predictedscore_base = predictor.getPredictions()
predictedclass, predictedscore, seqnum = predictor.getPredictionsWithSequences(maxlag)
dates = predictor.getDates()

preddf = pd.DataFrame({'filename':filenames, 'dates':dates, 'seqnum':seqnum, 'predictionbase':predictedclass_base, 'scorebase':predictedscore_base, 'prediction':predictedclass, 'score':predictedscore})

preddf.to_csv("results.csv")
print('Done, results saved in "results.csv"')
