import sys
import click
import pandas as pd
from pathlib import Path

from deepfaune.util.species_mapping import deepfaune_prediction2trapper

current_file = Path(__file__).resolve()
current_directory = current_file.parent
sys.path.append(str(current_directory / "../")) # to add the deepfaune path
from loguru import logger

from deepfaune.util.evaluation import SimpleEvaluator

# Ensure deepfaune package is available
current_file = Path(__file__).resolve()
current_directory = current_file.parent
sys.path.append(str(current_directory / "../"))

def validate_file(ctx, param, value):
    """Ensure the given path is a valid file."""
    path = Path(value)
    if not path.exists() or not path.is_file():
        raise click.BadParameter(f"File '{value}' does not exist.")
    return path


@click.command()
@click.option(
    "--predictions-csv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    callback=validate_file,
    help="Path to the CSV file containing model predictions.",
)
@click.option(
    "--annotations-csv",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    callback=validate_file,
    help="Path to the CSV file containing ground truth annotations.",
)
@click.option(
    "--output-csv",
    default=None,
    type=click.Path(writable=True),
    help="Path to save the evaluation results (CSV format). If not provided, will be saved next to predictions CSV.",
)
def evaluate(predictions_csv: Path, annotations_csv: Path, output_csv: Path):
    """CLI tool to evaluate predictions against ground truth annotations."""
    logger.info(f"Loading predictions from: {predictions_csv}")
    logger.info(f"Loading ground truth annotations from: {annotations_csv}")

    # Load data
    df_predictions = pd.read_csv(predictions_csv)
    df_annotations = pd.read_csv(annotations_csv)

    sE = SimpleEvaluator(df_predictions=df_predictions, df_annotations=df_annotations)
    sE.prepare_trapper_predictions()
    sE.map_predictions_to_annotations_species(deepfaune_prediction2trapper)


    sE.analyse_predictions()

    # Determine output file path
    if output_csv is None:
        output_csv = predictions_csv.parent / f"prediction_comparison_{predictions_csv.stem}.csv"

    # Save results
    sE.df_merged.to_csv(output_csv, index=False)
    logger.success(f"Evaluation results saved in {output_csv}")

    logger.info(f"Stats: {sE.stats()}")



if __name__ == "__main__":
    evaluate()
