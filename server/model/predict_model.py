"""
Usage:
    python predict_model.py --model 20180125_203820/model.h5 --driver_id 1
"""

from keras.models import load_model

import os
import pandas as pd
import click


@click.command()
@click.option('--model', help="Saved model to load and predict with.")
@click.option('--driver_id', default=1, nargs=1, help="Driver to treat as real driver.")
def predict(model, driver_id):
    TIMESTEPS = 60  # if the preformatted csv's were used, they were made with timesteps of 60
    model = load_model(model)

    # prepare data
    path = os.path.join("data", "formatted_data", str(driver_id), "test_merged.csv")
    test_data = pd.read_csv(path, sep=',')
    test_data.drop(["trip_start"], axis=1, inplace=True)  # this is a useless row for training
    # extract train labels
    test_labels = test_data["driver_label"].as_matrix()
    test_data.drop(["driver_label"], axis=1, inplace=True)

    # extract train features
    test_data = test_data.as_matrix()
    num_samples = test_data.shape[0]
    num_features = test_data.shape[1]
    test_data = test_data.reshape(int(num_samples/TIMESTEPS), TIMESTEPS, num_features)
    test_labels = test_labels.reshape(int(num_samples/TIMESTEPS), TIMESTEPS)

    print(test_data.shape)
    print(test_labels.shape)

    for idx, thing in enumerate(test_data):
        thing = thing.reshape(1, TIMESTEPS, num_features)
        prediction = model.predict(thing)
        print("=================")
        print("Prediction:")
        print(prediction)
        print("Actual:")
        print(test_labels[idx])

if __name__ == "__main__":
    predict()
