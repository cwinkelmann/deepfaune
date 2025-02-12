from pathlib import Path

import pandas as pd
import pytest
from loguru import logger

from deepfaune.inference import prediction_wrapper
from deepfaune.util.evaluation import SimpleEvaluator
from deepfaune.util.files import find_images

def get_base_folder():
    # get current directory
    current_file = Path(__file__).resolve()
    current_directory = current_file.parent

    images_dir = current_directory / "../testdata"
    return images_dir

@pytest.fixture
def base_folderfixture():
    return get_base_folder()


@pytest.fixture
def df_ground_truth():
    base_folder = get_base_folder()
    df_ground_truth = pd.read_csv(base_folder / "ground_truth.csv")

    return df_ground_truth

@pytest.fixture
def df_predictions():
    base_folder = get_base_folder()
    df_predictions = pd.read_csv(base_folder / "predictions.csv")

    return df_predictions


def test_analyse_predictions(df_ground_truth, df_predictions):
    ## IMAGE FILES
    sE = SimpleEvaluator(df_predictions=df_predictions, df_annotations=df_ground_truth)
    sE.analyse_predictions()

    assert round(sE.accuracy, 4) == 0.8913
    assert len(sE.false_positives) == 2
    assert len(sE.false_negatives) == 1
    ## Check the false negatives
    assert sE.false_negatives.iloc[0]["mediaID"] == 42
    assert sE.false_negatives.iloc[0]["image_name"] == "EMPTY42.JPG"

    assert len(sE.true_negatives) == 4

