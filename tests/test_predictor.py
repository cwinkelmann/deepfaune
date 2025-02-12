from pathlib import Path

from loguru import logger

from demo.testPredictor import find_images, prediction_wrapper


def test_find_images():
    images_dir = Path("/Users/christian/PycharmProjects/hnee/deepfaune_software/demo")
    filenames = find_images(images_dir)
    print(filenames)
    assert len(filenames) == 3

def test_prediction_wrapper():
    ## IMAGE FILES
    images_dir = Path("/Users/christian/PycharmProjects/hnee/deepfaune_software/demo")
    output_csv = Path("/Users/christian/PycharmProjects/hnee/deepfaune_software/demo/predictions.csv")


    filenames = find_images(images_dir)
    logger.debug(f"Found {len(filenames)} images in {images_dir}")

    preddf = prediction_wrapper(filenames)

    preddf.to_csv(output_csv, index=False)

    print(f"Done, results saved in {output_csv}")

    assert preddf.shape[0] == 5