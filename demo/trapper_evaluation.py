"""
Evaluating the performance of deepfaune on the trapper data

"""
from pathlib import Path

import pandas as pd
from loguru import logger

from deepfaune.util.files import find_images


# def main(images_dir: Path):
#     filenames = find_images(images_dir)
#     logger.debug(f"Found {len(filenames)} images in {images_dir}")
#
#     preddf = prediction_wrapper(filenames)
#
#     preddf.to_csv(output_csv, index=False)
#
#     print(f"Done, results saved in {output_csv}")




if __name__ == "__main__":
    # images_dir = Path("/Users/christian/data/camera_trapping/trapper_photos_6")
    images_dir = Path('/Users/christian/Library/CloudStorage/GoogleDrive-christian.winkelmann@gmail.com/My Drive/Datasets/trapper/trapper_photos_2')

    # annotations_path = Path("/Users/christian/data/camera_trapping/trapper_photos_6/metadata.csv")
    annotations_path = Path('/Users/christian/Library/CloudStorage/GoogleDrive-christian.winkelmann@gmail.com/My Drive/Datasets/trapper/observations_0_2.csv')

    output_csv = Path(f"/Users/christian/PycharmProjects/hnee/deepfaune_software/demo/{images_dir.name}.csv")

    df_merged = analyse_predictions(df_predictions=pd.read_csv(output_csv),
                        df_annotations=pd.read_csv(annotations_path))

    df_merged.to_csv(output_csv.parent / f"prediction_comparison_{images_dir.name}.csv", index=False)