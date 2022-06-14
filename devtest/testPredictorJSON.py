import sys
import os
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from predictTools import PredictorJSON

txt_classes = ["badger","ibex","red deer","chamois","cat","roe deer","dog","squirrel","human","lagomorph","wolf","lynx","marmot","micromammal","mouflon","sheep","mustelide","bird","fox","wild boar","cow","vehicle"]
LANG = 'gb' # or 'fr'
predictor = PredictorJSON(sys.argv[1], 0.5, txt_classes+["empty"], "undefined")
predictor.allBatch()
filenames, predictedclass_base, predictedscore_base = predictor.getPredictions()

df = pd.DataFrame({'file':filenames, 'class':predictedclass_base, 'score':predictedscore_base})

print(df)
