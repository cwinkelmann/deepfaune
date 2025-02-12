from pathlib import Path

import pytest
from loguru import logger

from deepfaune.inference import prediction_wrapper
from deepfaune.util.evaluation import SimpleEvaluator
from deepfaune.util.files import find_images
from deepfaune.util.species_mapping import deepfaune_prediction2trapper


def base_folder():
    # get current directory
    current_file = Path(__file__).resolve()
    current_directory = current_file.parent

    images_dir = current_directory / "../demo"
    return images_dir

@pytest.fixture
def base_folderfixture():
        return base_folder()

@pytest.fixture
def integration_folder_fixture():
    # get current directory
    current_file = Path(__file__).resolve()
    current_directory = current_file.parent

    images_dir = current_directory / "../testdata"
    return images_dir

@pytest.fixture
def filenames():
    images_dir = base_folder()
    print(f"images dir: {images_dir.resolve()}")
    filenames = find_images(images_dir)
    logger.debug(f"Found {len(filenames)} images in {images_dir}")
    if len(filenames) == 0:
        raise FileNotFoundError(f"No images found in {images_dir}")
    return filenames

@pytest.fixture
def df_ground_truth():

    return df_ground_truth

def test_find_images(base_folderfixture):

    filenames = find_images(base_folderfixture)

    assert len(filenames) == 1

@pytest.mark.skip(reason="Skipping this test temporarily")
def test_integration(filenames, df_ground_truth):
    """
    integration test for multiple functions and a slightly bigger dataset
    """

    df_predictions = prediction_wrapper(filenames)
    sE = SimpleEvaluator(df_predictions=df_predictions, df_annotations=df_ground_truth)
    sE.prepare_trapper_predictions()
    sE.map_predictions_to_annotations_species(deepfaune_prediction2trapper)

    df_analysis, metrics = sE.analyse_predictions()


    assert metrics.accurary == 0.90