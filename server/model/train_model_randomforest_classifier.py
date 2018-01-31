from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn import metrics
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import pprint
import datetime


DRIVER_ID = 1
TIMESTEPS = 5
NUM_FEATURES = 77

data = []
labels = []
train_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
if not os.path.exists(train_session):
    os.makedirs(train_session)
print("=============================================")
print("Saving session in ./{}".format(train_session))
print("=============================================")

# load the data
trips = np.load(os.path.join('feature_generation', 'myfeatures.npy'))  # (18400, 77), 92 drivers
train_driver = trips[0:160, :]  # (160, NUM_FEATURES), 160 of the first driver's trips
train_others = trips[200:360, :]  # (160, NUM_FEATURES), 1 other driver, 160 trips
test_driver = trips[160:200, :]  # (40, NUM_FEATURES)
test_others = trips[360:400, :]  # (40, NUM_FEATURES), 1 other drivers, 40 trips

train_labels = np.concatenate((np.ones(shape=(train_driver.shape[0], 1)),
                               np.zeros(shape=(train_others.shape[0], 1))),
                               axis=0)
test_labels = np.concatenate((np.ones(shape=(test_driver.shape[0], 1)),
                              np.zeros(shape=(test_others.shape[0], 1))),
                              axis=0)

train_data = np.concatenate((train_driver, train_others),axis=0)  
test_data = np.concatenate((test_driver, test_others),axis=0)  

# train the model
model = RandomForestClassifier(n_estimators=950, random_state=1, verbose=1, oob_score=True)
model.fit(train_data, np.ravel(train_labels))

# save the model
joblib.dump(model, os.path.join(train_session, "model.pkl"))

# use the model to predict
ret = model.predict_proba(test_data)
print("Printing out final test case: ")
for idx, thing in enumerate(ret[:,1]):
    print("Prediction: {0}  Expected:  {1}".format(thing, test_labels[idx]))

precision, recall, thresholds = metrics.precision_recall_curve(test_labels, ret[:,1])
print("PR: {}".format(metrics.auc(recall, precision)))
