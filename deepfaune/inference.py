import sys
import os
import time
import typing
from pathlib import Path
import pandas as pd
from loguru import logger

from predictTools import PredictorImage


def prediction_wrapper(filenames: typing.List[Path]) -> pd.DataFrame:
    """
    wrap the prediction logic into a one liner
    """

    ## PREDICTOR OBJECT
    LANG = 'en'
    maxlag = 20
    threshold = 0.5
    BATCH_SIZE = 48

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
    preddf = pd.DataFrame({'fileName': predictor.getFilenames(),
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
