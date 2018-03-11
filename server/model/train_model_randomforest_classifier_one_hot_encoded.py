from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import svm
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn import metrics
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import pprint
import datetime

DRIVER_SAMPLES = 40 #  number of drivers in the encoding
TRAIN_TRIPS = 160 # use this many training trips
TEST_TRIPS = 200 - TRAIN_TRIPS  # this many test trips

REPEAT_RUNS = 1  # how many times to train/evaluate model
ACCURACY_THRESHOLD = 0.50  # threshold for measuring classification accuracy

auc_pr_results = []
accuracies = []
for i in list(range(REPEAT_RUNS)):
	# load the data, shape is (NUM_DRIVERS * 200, NUM_FEATURES)
	trips = np.load(os.path.join('feature_generation', 'myfeatures.npy'))  # (18400, 126) = 92 drivers, 126 features
	number_of_drivers = int(trips.shape[0] / 200)
	number_of_features = int(trips.shape[1])

	# randomly select DRIVER_SAMPLES drivers from data, drivers are index 0
	drivers = np.random.choice(np.arange(number_of_drivers), DRIVER_SAMPLES)

	# extract training data
	train_data = []
	train_labels = []
	test_data = []
	test_labels = []
	for idx, driver in enumerate(drivers):
		driver_start_idx = int((driver) * 200)
		next_driver_start_idx = int((driver + 1) * 200)

		train_data.extend(trips[driver_start_idx:(driver_start_idx + TRAIN_TRIPS)][:])  # shape is (TRAIN_TRIPS, number_of_features)
		temp_labels = np.ones(TRAIN_TRIPS) * idx
		train_labels.extend(temp_labels)

		test_data.extend(trips[(driver_start_idx + TRAIN_TRIPS):next_driver_start_idx][:])  # shape is (TEST_TRIPS, number_of_features)
		temp_labels = np.ones(TEST_TRIPS) * idx
		test_labels.extend(temp_labels)

	assert(np.array(train_data).shape == ((DRIVER_SAMPLES * TRAIN_TRIPS), number_of_features))
	assert(np.array(train_labels).shape == ((DRIVER_SAMPLES * TRAIN_TRIPS), ))
	assert(np.array(test_data).shape == ((DRIVER_SAMPLES * TEST_TRIPS), number_of_features))
	assert(np.array(test_labels).shape == ((DRIVER_SAMPLES * TEST_TRIPS), ))
	
	# train the model
	model1 = RandomForestClassifier(n_estimators=1000)
	model1.fit(train_data, np.ravel(train_labels))

	# save the model
	#joblib.dump(model, os.path.join(train_session, "model.pkl"))

	# use the model to predict
	ret1 = model1.predict_proba(test_data)
	accuracy_test = []
	print("Calculating accuracy: ")
	predictions = np.argmax(ret1, axis=1)  # axis=1 means "row-wise", ie along each test case
	right = 0
	wrong = 0
	for idx, prediction in enumerate(predictions):
		print("predict: {0}({1}), truth: {2}".format(prediction, ret1[idx][prediction], test_labels[idx]))
		if prediction == test_labels[idx]:
			right += 1
		else:
			wrong += 1
	print("right: {0}, wrong: {1}, total: {2}".format(right, wrong, right + wrong))
