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

# shape
print(dataset.shape)

# head
print(dataset.head(20))

# descriptions
print(dataset.describe())

# class distribution
# print(dataset.groupby('class').size())