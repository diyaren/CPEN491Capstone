from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import svm
from sklearn.externals import joblib
from sklearn import metrics
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import pprint
import datetime

TRUTH_DRIVER = 29  # driver to build model for
TRAIN_TRIPS = 150  # train on 160 of a driver's trips
NEG_TEST_TRIPS = 200 - TRAIN_TRIPS  # how many negative samples in the test set

REPEAT_RUNS = 10  # how many times to train/evaluate model
ACCURACY_THRESHOLD = 0.50  # threshold for measuring classification accuracy

auc_pr_results = []
accuracies = []
for i in list(range(REPEAT_RUNS)):
	data = []
	labels = []
	#train_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	#if not os.path.exists(train_session):
	#	os.makedirs(train_session)
	#print("=============================================")
	#print("Saving session in ./{}".format(train_session))
	#print("=============================================")

	# load the data, shape is (NUM_DRIVERS * 200, NUM_FEATURES)
	trips = np.load(os.path.join('feature_generation', 'myfeatures.npy'))  # (18400, 77), 92 drivers

	number_of_drivers = trips.shape[0] / 200
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

	train_data = np.concatenate((train_driver, train_others),axis=0)  
	test_data = np.concatenate((test_driver, test_others),axis=0)  

	# train the model
	model1 = RandomForestClassifier(n_estimators=100, max_depth=6)
	model2 = ExtraTreesClassifier(n_estimators=600, max_depth=6)
	model3 = GradientBoostingClassifier(n_estimators=1900, max_depth=6)
	model1.fit(train_data, np.ravel(train_labels))
	model2.fit(train_data, np.ravel(train_labels))
	model3.fit(train_data, np.ravel(train_labels))

	# save the model
	#joblib.dump(model, os.path.join(train_session, "model.pkl"))

	# use the model to predict
	ret1 = model1.predict_proba(test_data)
	ret2 = model2.predict_proba(test_data)
	ret3 = model3.predict_proba(test_data)
	ensembled_predictions = (np.array(ret1[:,1]) + np.array(ret2[:,1]) + np.array(ret3[:,1])) / 3
	accuracy_test = []
	print("Calculating accuracy: ")
	#for idx, prediction1 in enumerate(ret1[:,1]):
	for idx, prediction in enumerate(ensembled_predictions):
		prediction = 1 if (prediction > ACCURACY_THRESHOLD) else 0
		result = 1 if prediction == test_labels[idx] else 0
		accuracy_test.append(result)

	accuracy_score = sum(accuracy_test) / len(accuracy_test)
	accuracies.append(accuracy_score)

	#precision, recall, thresholds = metrics.precision_recall_curve(test_labels, ret[:,1])
	precision, recall, thresholds = metrics.precision_recall_curve(test_labels, ensembled_predictions)
	AUC_PR = metrics.auc(recall, precision)
	auc_pr_results.append(AUC_PR)

	print("Accuracy: {0} PR: {1}".format(accuracy_score, AUC_PR))

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
