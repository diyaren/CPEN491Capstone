from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn import metrics
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

import os
import pprint
import datetime

TRAIN_TRIPS = 150  # train on 160 of a driver's trips
NEG_TEST_TRIPS = 200 - TRAIN_TRIPS  # how many negative samples in the test set

REPEAT_RUNS = 50  # how many times to train/evaluate model
ACCURACY_THRESHOLD = 0.50  # threshold for measuring classification accuracy

PCA_COMPONENTS = 50

auc_pr_results = []
accuracies = []
precisions = []
recalls = []
tpr = []  # sensitivity
tnr = []  # specificity
fpr = []  # fall-out
fnr = []  # 
npv = []
f1 = []
for i in list(range(REPEAT_RUNS)):
    data = []
    labels = []
    #train_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #if not os.path.exists(train_session):
    #   os.makedirs(train_session)
    #print("=============================================")
    #print("Saving session in ./{}".format(train_session))
    #print("=============================================")

    # load the data, shape is (NUM_DRIVERS * 200, NUM_FEATURES)
    trips = np.load('myfeatures.npy')  # (18400, 77), 92 drivers

    number_of_drivers = trips.shape[0] / 200
    TRUTH_DRIVER = random.randint(1, number_of_drivers) # driver to build model for
    print("Training a model for driver id {}".format(TRUTH_DRIVER))
    truth_driver_start_idx = (TRUTH_DRIVER - 1) * 200


    # extract trips for positive training samples
    train_driver = trips[truth_driver_start_idx:truth_driver_start_idx + TRAIN_TRIPS, :]  # (TRAIN_TRIPS, NUM_FEATURES), 160 of the true driver's trips

    # extract trips for an equal number of randomly sampled negative training samples
    truth_driver_trips_idx = np.linspace(truth_driver_start_idx, truth_driver_start_idx + 200 - 1, 200)
    possible_other_driver_trips_idx = np.arange(trips.shape[0])
    possible_other_driver_trips_idx = np.delete(possible_other_driver_trips_idx, truth_driver_trips_idx)
    other_driver_trips = np.random.choice(possible_other_driver_trips_idx, TRAIN_TRIPS + NEG_TEST_TRIPS, replace=False)
    other_driver_train_trips = other_driver_trips[:TRAIN_TRIPS]
    other_driver_test_trips = other_driver_trips[TRAIN_TRIPS:]
    assert len(other_driver_train_trips) == TRAIN_TRIPS
    assert len(other_driver_test_trips) == NEG_TEST_TRIPS
    train_others = trips[other_driver_train_trips, :]

    # extract positive test trips
    test_driver = trips[truth_driver_start_idx + TRAIN_TRIPS:truth_driver_start_idx + 200, :]  # (40, NUM_FEATURES)
    test_others = trips[other_driver_test_trips, :]


    train_labels = np.concatenate((np.ones(shape=(train_driver.shape[0], 1)),
        np.zeros(shape=(train_others.shape[0], 1))),
        axis=0)
    test_labels = np.concatenate((np.ones(shape=(test_driver.shape[0], 1)),
        np.zeros(shape=(test_others.shape[0], 1))),
        axis=0)

    scalar = preprocessing.StandardScaler()
    train_data = np.concatenate((train_driver, train_others), axis=0)
    train_data = scalar.fit(train_data).transform(train_data)

    test_data = np.concatenate((test_driver, test_others), axis=0)
    test_data = scalar.transform(test_data)

    # train the model
    #model = svm.SVC(C=1000, kernel='rbf', decision_function_shape="ovr")
    model = RandomForestClassifier(n_estimators=1000)
    model.fit(train_data, np.ravel(train_labels))
    #model1 = RandomForestClassifier(n_estimators=1000)
    #model2 = ExtraTreesClassifier(n_estimators=1000)
    #model3 = GradientBoostingClassifier(n_estimators=1000)
    #model1.fit(train_data, np.ravel(train_labels))
    #model2.fit(train_data, np.ravel(train_labels))
    #model3.fit(train_data, np.ravel(train_labels))

    # save the model
    #joblib.dump(model, os.path.join(train_session, "model.pkl"))

    # use the model to predict
    ret = model.predict(test_data)
    #ret1 = model1.predict_proba(test_data)
    #ret2 = model2.predict_proba(test_data)
    #ret3 = model3.predict_proba(test_data)
    #ensembled_predictions = (np.array(ret1[:,1]) + np.array(ret2[:,1]) + np.array(ret3[:,1])) / 3
    accuracy_test = []

    # samples
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    print("Calculating accuracy: ")
    for idx, prediction in enumerate(ret):
    #for idx, prediction in enumerate(ensembled_predictions):
        if prediction > ACCURACY_THRESHOLD:
            if 1 == test_labels[idx][0]:
                true_positives += 1
                result = 1
            else:
                false_positives += 1
                result = 0
        else:
            if 0 == test_labels[idx][0]:
                true_negatives += 1
                result = 1
            else:
                false_negatives += 1
                result = 0

        accuracy_test.append(result)

    precisions.append((true_positives)/(true_positives + false_positives))
    tpr.append(true_positives / (true_positives + false_negatives))
    tnr.append(true_negatives / (true_negatives + false_positives))
    fpr.append(false_positives / (true_negatives + false_positives))
    fnr.append(false_negatives / (true_positives + false_negatives))
    npv.append(true_negatives / (false_negatives + true_negatives))
    f1.append((2 * true_positives)/(2 * true_positives + false_positives + false_negatives))
    accuracies.append((true_positives + true_negatives)/(true_positives + false_positives + false_negatives + true_negatives))

    precision, recall, thresholds = metrics.precision_recall_curve(test_labels, ret)
    #precision, recall, thresholds = metrics.precision_recall_curve(test_labels, ensembled_predictions)
    AUC_PR = metrics.auc(recall, precision)
    auc_pr_results.append(AUC_PR)

    print("true_positives: {0}, false_positives: {1}, true_negatives: {2}, false_negatives: {3}".format(true_positives, false_positives, true_negatives, false_negatives))
    print("false positive rate: {}".format(fpr[-1]))
    print("false negative rate: {}".format(fnr[-1]))
    print("Accuracy: {0} PR: {1}".format(accuracies[-1], AUC_PR))

print("Results from 100 runs:")
print("\nAUC PR scores")
print("min: {}".format(min(auc_pr_results)))
print("max: {}".format(max(auc_pr_results)))
print("mean: {}".format(np.mean(auc_pr_results)))
print("std: {}".format(np.std(auc_pr_results)))
print("var: {}".format(np.var(auc_pr_results)))
print("\nAccuracy scores")
print("min: {}".format(min(accuracies)))
print("max: {}".format(max(accuracies)))
print("mean: {}".format(np.mean(accuracies)))
print("std: {}".format(np.std(accuracies)))
print("var: {}".format(np.var(accuracies)))
print("\nTrue Positive Rate (recall or sensitivity)")
print("min: {}".format(min(tpr)))
print("max: {}".format(max(tpr)))
print("mean: {}".format(np.mean(tpr)))
print("std: {}".format(np.std(tpr)))
print("var: {}".format(np.var(tpr)))
print("\nTrue Negative Rate (specificity)")
print("min: {}".format(min(tnr)))
print("max: {}".format(max(tnr)))
print("mean: {}".format(np.mean(tnr)))
print("std: {}".format(np.std(tnr)))
print("var: {}".format(np.var(tnr)))
print("\nFalse Positive Rate")
print("min: {}".format(min(fpr)))
print("max: {}".format(max(fpr)))
print("mean: {}".format(np.mean(fpr)))
print("std: {}".format(np.std(fpr)))
print("var: {}".format(np.var(fpr)))
print("\nFalse Negative Rate")
print("min: {}".format(min(fnr)))
print("max: {}".format(max(fnr)))
print("mean: {}".format(np.mean(fnr)))
print("std: {}".format(np.std(fnr)))
print("var: {}".format(np.var(fnr)))
print("\nF1 Score")
print("min: {}".format(min(f1)))
print("max: {}".format(max(f1)))
print("mean: {}".format(np.mean(f1)))
print("std: {}".format(np.std(f1)))
print("var: {}".format(np.var(f1)))
print("\nPrecision")
print("min: {}".format(min(precisions)))
print("max: {}".format(max(precisions)))
print("mean: {}".format(np.mean(precision)))
print("std: {}".format(np.std(precisions)))
print("var: {}".format(np.var(precisions)))
print("\nNegative Predictive Value")
print("min: {}".format(min(npv)))
print("max: {}".format(max(npv)))
print("mean: {}".format(np.mean(npv)))
print("std: {}".format(np.std(npv)))
print("var: {}".format(np.var(npv)))
