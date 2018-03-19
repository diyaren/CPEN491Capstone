import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib

from .feature_generation.feature_generation import features_from_trip


def predict_model(driver_id=None, model_fp=None, trip=None):
    """
    :param driver_id driver identification number
    :param model_fp absolute filepath to pickled model (os.path)
    :param trip list of positions, ie: [[x0, y0], [x1, y1], ...]
    :return prediction float, % confident that it is the correct driver
    """
    assert driver_id
    assert model_fp
    assert trip

    # verify path
    if model_fp.split(".")[1] != "pkl":
        model_fp = os.path.join(model_fp, driver_id + ".pkl")

    # generate features
    features = np.array([features_from_trip(trip)])
    assert features.shape[0] == 1

    model = joblib.load(model_fp)
    prediction = model.predict_proba(features)

    return prediction


def train_model(driver_id=None, model_fp=None, positive_trips=None, negative_trips=None):
    """
    :param model_fp absolute filepath to pickled model (os.path)
    :param driver_id driver identification number
    :param positive_trips list of trips from the driver to identify [[list_of_trip0_points], [list_of_trip1_points],...]
    :param negative_trips list of trips from not the driver [[list_of_trip0_points], [list_of_trip1_points],...]
    :return None
    """
    assert model_fp
    assert driver_id
    assert positive_trips
    assert negative_trips

    # ensure same amount of positive and negative data
    assert len(positive_trips) == len(negative_trips), "There should be an equal number of positive and negative trips"

    train_data = []
    train_labels = []
    for trip in positive_trips:
        assert len(trip) > 1, "Positive training trips need to contain more than 1 point, need more training data"
        train_data.append(features_from_trip(trip))
        train_labels.append(1)

    for trip in negative_trips:
        assert len(trip) > 1, "Negative training trips need to contain more than 1 point, need more training data"
        train_data.append(features_from_trip(trip))
        train_labels.append(0)

    assert len(train_data) == len(train_labels)
    assert len(train_data) == (len(positive_trips) + len(negative_trips))

    model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=5000)
    )
    model.fit(train_data, np.ravel(train_labels))

    # save the model
    if model_fp.split(".")[1] != "pkl":
        model_fp = os.path.join(model_fp, driver_id + ".pkl")

    print("saving model for driver {0} to {1}".format(driver_id, model_fp))
    joblib.dump(model, model_fp)
