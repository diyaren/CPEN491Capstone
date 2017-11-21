import pandas
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC


# Load dataset
url = "./dataset.csv"
names = ['id', 'timestamp', 'session_id', 'user_id', 'pc_throttle', 'pc_brake', 'pc_steering', 'pc_rpm', 'pc_speed', 'pc_pos_x', 'pc_pos_y', 'pc_pos_z', 'pc_laptime', 'pc_race_state', 'pc_lap_number', 'pc_lap_distance', 'vr_pos_x', 'vr_pos_y', 'vr_pos_z', 'vr_rotation_x', 'vr_rotation_y', 'vr_rotation_z', 'logitech_acceleration', 'logitech_brake', 'logitech_steering']
dataset = pandas.read_csv(url, names=names)

# class distribution
# print(dataset.groupby('user_id').size())

# # shape
# print(dataset.shape)

# # head
# print(dataset.head(20))

# # descriptions
# print(dataset.describe())

# Split-out validation dataset
array = dataset.values
X = array[:,4:10]
Y = array[:,3]
# print(type(X))
# print(Y)
validation_size = 0.20
seed = 7
X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)

X_train = list(X_train)
Y_train = list(Y_train)
print(type(X_train))
# print(X_train)
print(type(Y_train))
# print(Y_train)

# Test options and evaluation metric
seed = 7
scoring = 'accuracy'

# Spot Check Algorithms
models = []
models.append(('LR', LogisticRegression()))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC()))
# evaluate each model in turn
results = []
names = []
for name, model in models:
	kfold = model_selection.KFold(n_splits=10, random_state=seed)
	cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
	results.append(cv_results)
	names.append(name)
	msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
	print(msg)

# # Compare Algorithms
# fig = plt.figure()
# fig.suptitle('Algorithm Comparison')
# ax = fig.add_subplot(111)
# plt.boxplot(results)
# ax.set_xticklabels(names)
# plt.show()

# Make predictions on validation dataset
knn = KNeighborsClassifier()
knn.fit(X_train, Y_train)
predictions = knn.predict(X_validation)
print(accuracy_score(Y_validation, predictions))
print(confusion_matrix(Y_validation, predictions))
print(classification_report(Y_validation, predictions))