from pathlib import Path

import pytest
from loguru import logger

from deepfaune.inference import prediction_wrapper
from deepfaune.util.files import find_images

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

def test_find_images(base_folderfixture):

    filenames = find_images(base_folderfixture)

    assert len(filenames) == 1

def test_prediction_wrapper(filenames):
    ## IMAGE FILES

    preddf = prediction_wrapper(filenames)

    assert preddf.shape[0] == 1

    assert list(preddf.columns) == ['fileName', 'dates', 'seqnum', 'prediction', 'score', 'count', 'getPredictedTop1']
    assert Path(preddf.iloc[0]["fileName"]).name == "squirrel.JPG"