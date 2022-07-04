import sys
import os
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from predictTools import PredictorJSON

txt_classes = ["badger","ibex","red deer","chamois","cat","roe deer","dog","squirrel","human","lagomorph","wolf","lynx","marmot","micromammal","mouflon","sheep","mustelide","bird","fox","wild boar","cow","vehicle"]
maxlag = 20
threshold = 0.5

predictor = PredictorJSON(sys.argv[1], threshold, txt_classes, "empty", "undefined")
predictor.allBatch()

predictor2 = PredictorJSON(sys.argv[2], threshold, txt_classes, "empty", "undefined")
predictor2.allBatch()

predictor.merge(predictor2)

filenames = predictor.getFileNames()
predictedclass_base, predictedscore_base = predictor.getPredictions()
predictedclass, predictedscore, seqnum = predictor.getPredictionsWithSequences(maxlag)
dates = predictor.getDates()

preddf = pd.DataFrame({'filename':filenames, 'dates':dates, 'seqnum':seqnum, 'predictionbase':predictedclass_base, 'scorebase':predictedscore_base, 'prediction':predictedclass, 'score':predictedscore})

preddf.to_csv("results.csv")
print('Done, results saved in "results.csv"')
