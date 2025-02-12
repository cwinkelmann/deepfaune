# Commandline interface/API to deepfaune

This is a commandline interface to the deepfaune software. It is a Python package that can be installed using pip. It provides a commandline interface to the deepfaune software, which is a software for the classification of wildlife images.

If everything is installed correctly ( python 3.11, requirements.txt and requirements-dev.txt installed), you can run the following commands:


```shell
# get help on how to used the predictor
python cli_predictor.py --help


# predict all the animals in the testdata folder
python cli_predictor.py --images-dir ../testdata --output-csv ./prediction_testdata.csv

```

Check prediction_testdata.csv if it aligns with the expected output


```shell
python cli_evaluator.py --help

# evaluate the predictions
python cli_evaluator.py --predictions-csv ./prediction_testdata.csv --groundtruth-csv ../testdata/groundtruth.csv


python cli_evaluator.py --predictions-csv trapper_photos_2.csv --annotations-csv observations_0_2.csv
```

