import sys

import click
from pathlib import Path
current_file = Path(__file__).resolve()
current_directory = current_file.parent
sys.path.append(str(current_directory / "../")) # to add the deepfaune path

from deepfaune.inference import prediction_wrapper
from deepfaune.util.files import find_images

def validate_input_dir(ctx, param, value):
    path = Path(value)
    if not path.exists() or not path.is_dir():
        raise click.BadParameter(f"Input directory '{value}' does not exist or is not a directory.")
    return path

def validate_output_file(ctx, param, value):
    return Path(value)

@click.command()
@click.option(
    "--images-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    callback=validate_input_dir,
    help="Path to the directory containing images for prediction.",
)
@click.option(
    "--output-csv",
    default="predictions.csv",
    type=click.Path(writable=True),
    callback=validate_output_file,
    help="Path to save the prediction results (CSV format).",
)
def predict(images_dir, output_csv):
    "CLI tool to run predictions on a folder of images."
    click.echo(f"Scanning images in: {images_dir}")
    filenames = find_images(images_dir)
    if not filenames:
        click.echo("No images found in the directory.", err=True)
        return

    click.echo(f"Found {len(filenames)} images. Running prediction...")
    preddf = prediction_wrapper(filenames)
    preddf.to_csv(output_csv, index=False)
    click.echo(f"Done! Results saved in {output_csv}")

if __name__ == "__main__":
    predict()
