"""
Evaluation functions
"""
from pathlib import Path

import pandas as pd




class SimpleEvaluator:
    def __init__(self, df_predictions: pd.DataFrame,
                        df_annotations: pd.DataFrame):
        self.df_predictions = df_predictions
        self.df_annotations = df_annotations

        self.df_merged = None
        self.false_positives = None
        self.false_negatives = None
        self.true_negatives = None
        self.true_positives = None
        self.accuracy = None

    def prepare_trapper_predictions(self) -> pd.DataFrame:
        self.df_predictions["imageName"] = self.df_predictions["fileName"].apply(lambda x: Path(x).name)
        self.df_predictions["mediaID"] = self.df_predictions["fileName"].apply(lambda x: int(Path(x).stem))

        return self.df_predictions

    def analyse_predictions(self):
        """
        Analyse the predictions and compare them to the annotations
        """


        df_predictions = self.df_predictions[["mediaID", "fileName", "prediction", "score" ]]
        df_annotations = self.df_annotations[["mediaID", "commonName"]]
        df_merged = df_annotations.merge(df_predictions, left_on="mediaID", right_on="mediaID", how="outer", suffixes=("_pred", "_anno"))

        df_merged["correct"] = df_merged["prediction"] == df_merged["commonName"]

        # calculate a simple accuracy, for this to be correct the predictions need to contain all data
        self.accuracy = df_merged["correct"].mean()

        # items where an prediction is not Null, but there is nothing on the image, i.e. false positive
        self.false_positives = df_merged[(df_merged["prediction"].notnull()) & (df_merged["commonName"].isnull())]
        # false negatives: items where there is an annotation, but no prediction
        self.false_negatives = df_merged[(df_merged["prediction"].isnull()) & (df_merged["commonName"].notnull())]
        # true negatives
        self.true_negatives = df_merged[(df_merged["prediction"].isnull()) & (df_merged["commonName"].isnull())]
        # true positives where prediction and annotation are the same
        self.true_positives = df_merged[(df_merged["prediction"].notnull()) & (df_merged["commonName"].notnull()) & (df_merged["correct"])]

        self.df_merged = df_merged

    def stats(self):
        return {
            "accuracy": self.accuracy,
            "false_positives": len(self.false_positives),
            "false_negatives": len(self.false_negatives),
            "true_negatives": len(self.true_negatives),
            "true_positives": len(self.true_positives)
        }

    def map_predictions_to_annotations_species(self, species_mapping):
        """
        rename every prediction so it matches the species names in the annotations
        """

        self.df_predictions["prediction"] = self.df_predictions["prediction"].apply(lambda x: species_mapping.get(x, x))
        return self.df_predictions

