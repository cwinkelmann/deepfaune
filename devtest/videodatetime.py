import ffmpeg
import sys
from pprint import pprint # for printing Python dictionaries in a human-readable way

# read the audio/video file from the command line arguments
testdir = sys.argv[1]

from pathlib import Path

filenames = sorted(
    [str(f) for f in  Path(testdir).rglob('*.[Aa][Vv][Ii]')] +
    [str(f) for f in  Path(testdir).rglob('*.[Mm][Pp]4')] +
    [str(f) for f in  Path(testdir).rglob('*.[Mm][Pp][Ee][Gg]')] +
    [str(f) for f in  Path(testdir).rglob('*.[Mm][Oo][Vv]')] +
    [str(f) for f in  Path(testdir).rglob('*.[Mm]4[Vv]')]
)

for filename in filenames:
    # uses ffprobe command to extract all possible metadata from the media file
    try:        
        print(filename,ffmpeg.probe(filename)["streams"][0]['tags']['creation_time'])
    except KeyError:
        print(filename,"unavailable")
