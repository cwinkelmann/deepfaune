"""
Evaluating the performance of deepfaune on the trapper data

"""
from pathlib import Path

import pandas as pd
from loguru import logger

from demo.testPredictor import find_images, prediction_wrapper


def main():
    filenames = find_images(images_dir)
    logger.debug(f"Found {len(filenames)} images in {images_dir}")

    preddf = prediction_wrapper(filenames)

    preddf.to_csv(output_csv, index=False)

    print(f"Done, results saved in {output_csv}")


def analyse_predictions(df_predictions: pd.DataFrame,
                        df_annotations: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse the predictions and compare them to the annotations
    """
    df_predictions["image_name"] = df_predictions["filename"].apply(lambda x: Path(x).name)
    df_predictions["mediaID"] = df_predictions["filename"].apply(lambda x: int(Path(x).stem))

    df_predictions = df_predictions[["mediaID", "image_name", "prediction", "score", ]]
    df_annotations = df_annotations[["mediaID", "commonName", "count"]]
    df_merged = df_predictions.merge(df_annotations, left_on="mediaID", right_on="mediaID", how="left", suffixes=("_pred", "_anno"))

    return df_merged

if __name__ == "__main__":
    images_dir = Path(
        "/Users/christian/data/camera_trapping/trapper/trapper_photos_6")
    annotations_path = Path(
        "/Users/christian/data/camera_trapping/trapper_photos_6/metadata.csv")
    output_csv = Path(f"/Users/christian/PycharmProjects/hnee/deepfaune_software/demo/{images_dir.name}.csv")

    # main()
    df_merged = analyse_predictions(df_predictions=pd.read_csv(output_csv),
                        df_annotations=pd.read_csv(annotations_path))

    df_merged.to_csv(output_csv.parent / f"prediction_comparison_{images_dir.name}.csv", index=False)