import numpy as np
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.datasets import load_digits
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing


def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - An object to be used as a cross-validation generator.
          - An iterable yielding train/test splits.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt





TRUTH_DRIVER = 29  # driver to build model for
TRAIN_TRIPS = 150  # train on 160 of a driver's trips
NEG_TEST_TRIPS = 200 - TRAIN_TRIPS  # how many negative samples in the test set

REPEAT_RUNS = 50  # how many times to train/evaluate model
ACCURACY_THRESHOLD = 0.50  # threshold for measuring classification accuracy

PCA_COMPONENTS = 50

trips = np.load('myfeatures.npy')  # (18400, 77), 92 drivers

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

scalar = preprocessing.StandardScaler()
train_data = np.concatenate((train_driver, train_others), axis=0)
train_data = scalar.fit(train_data).transform(train_data)

test_data = np.concatenate((test_driver, test_others), axis=0)
test_data = scalar.transform(test_data)






X=np.concatenate((train_data, test_data), axis=0)
y=np.concatenate((train_labels,test_labels), axis=0)

title = "Learning Curves"
# Cross validation with 100 iterations to get smoother mean test and train
# score curves, each time with 20% data randomly selected as a validation set.
cv = ShuffleSplit(n_splits=20, test_size=0.2, random_state=0)

estimator = RandomForestClassifier(n_estimators=1000)
estimator.fit(train_data, np.ravel(train_labels))
plot_learning_curve(estimator, title, X, y, ylim=(0, 1.05), cv=cv, n_jobs=4)


plt.show()