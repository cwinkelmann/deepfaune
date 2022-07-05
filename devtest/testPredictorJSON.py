import sys
import os
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from predictTools import PredictorJSON

LANG = 'fr'
maxlag = 20
threshold = 0.5

predictor = PredictorJSON(sys.argv[1], threshold, LANG)
predictor.allBatch()
df_filename, predictedclass_base, predictedscore_base, predictedclass, predictedscore, seqnum, dates = predictor.getPredictionsWithSequence(maxlag)

preddf = pd.DataFrame({'filename':df_filename["filename"], 'dates':dates, 'seqnum':seqnum, 'predictionbase':predictedclass_base, 'scorebase':predictedscore_base, 'prediction':predictedclass, 'score':predictedscore})

preddf.to_csv("results.csv")
print('Done, results saved in "results.csv"')
