evaluator
=========

Python script for evaluating classification tasks against ground truth.

```
./evaluator.py -h
usage: evaluator.py [-h] -p PREDICTION_FILE -g GROUND_TRUTH_FILE
                    [-b BINARY_PREDICTION_FILE] [--icd]

Evaluate the predictions against ground truth.

optional arguments:
  -h, --help            show this help message and exit
  -p PREDICTION_FILE, --prediction_file PREDICTION_FILE
                        Predictions file.
  -g GROUND_TRUTH_FILE, --ground_truth_file GROUND_TRUTH_FILE
                        Ground truth file.
  -b BINARY_PREDICTION_FILE, --binary_prediction_file BINARY_PREDICTION_FILE
                        Binary prediction to filter the prediction_file on.
  --icd                 Whether the evaluation is using ICD code; in which
                        case consider only first three characters (CXX).
                        Default is False
```

The format of the predictions file is:

```
docId[tab]classification1[tab]classification2[tab]...[tab]classificationN
```

i.e., one or more classification are processed per document. If any one is correct then the document is correct.

The ground truth file is simply:


```
docId[tab]classification
```


The binary_prediction_file is used to filter the predictions file according to a binary "0" or "1" label. Its format is:

```
docId[tab]classification
```

where classification = 0 or 1

The --icd flag is used when processing ICD codes where you only care about the first three characters, e.g., CXX. The default is false (i.e., not ICD).
