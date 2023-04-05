import sys
import os
from pathlib import Path
import pandas as pd

curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(curdir+'/../')

## DEEPFAUNE objects
from fileManager import FileManager

maxlag = 20

filenames = sorted(
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Jj][Pp][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Jj][Pp][Ee][Gg]') if not f.parents[1].match('*deepfaune_*')] +
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Bb][Mm][Pp]') if not f.parents[1].match('*deepfaune_*')] +
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Tt][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Gg][Ii][Ff]') if not f.parents[1].match('*deepfaune_*')] +
    [str(f) for f in  Path(sys.argv[1]).rglob('*.[Pp][Nn][Gg]') if not f.parents[1].match('*deepfaune_*')]
)

fileManager  = FileManager(filenames)
fileManager.findSequences(maxlag)
fileManager.reorderBySeqnum()

seqnum = fileManager.getSeqnums()
dates = fileManager.getDates()

preddf = pd.DataFrame({'filename':filenames, 'dates':dates, 'seqnum':seqnum})

preddf.to_csv("results.csv")
print('Done, results saved in "results.csv"')
