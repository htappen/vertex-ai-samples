# Getting started: Training and prediction with Keras in AI Platform

This code uses [`tf.keras`](https://www.tensorflow.org/guide/keras) to train a
classifier on the [Census Income Data
Set](https://archive.ics.uci.edu/ml/datasets/Census+Income). It's designed so
you can run the training on [Vertex AI custom job](https://cloud.google.com/vertex-ai/docs/training/create-custom-job).

To get started, simply run `python scripts/start_job.py --project <PROJECT ID> --location <GCP LOCATION> --staging_bucket <FOLDER TO PUT ARTIFACTS>`