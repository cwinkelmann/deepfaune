import sys
import os
from pathlib import Path
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from predictTools import Predictor

LANG = 'fr'
maxlag = 20
threshold = 0.5

df_filename = pd.DataFrame({'filename':sorted(
    [f for f in  Path(sys.argv[1]).rglob('*.[Jj][Pp][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(sys.argv[1]).rglob('*.[Jj][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(sys.argv[1]).rglob('*.[Bb][Mm][Pp]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(sys.argv[1]).rglob('*.[Tt][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(sys.argv[1]).rglob('*.[Gg][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [f for f in  Path(sys.argv[1]).rglob('*.[Pp][Nn][Gg]') if not f.parents[1].match('*deepfaune_*')]
)})

predictor = Predictor(df_filename, threshold, LANG)
predictor.allBatch()
df_filename, predictedclass_base, predictedscore_base, predictedclass, predictedscore, seqnum, dates = predictor.getPredictionsWithSequence(maxlag)

preddf = pd.DataFrame({'filename':df_filename["filename"], 'dates':dates, 'seqnum':seqnum, 'predictionbase':predictedclass_base, 'scorebase':predictedscore_base, 'prediction':predictedclass, 'score':predictedscore})

preddf.to_csv("results.csv")
print('Done, results saved in "results.csv"')
