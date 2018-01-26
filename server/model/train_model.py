from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.layers import LSTM
from keras.utils import plot_model
from keras.callbacks import TensorBoard
from keras.optimizers import Adam
import tensorflow

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import pprint
import datetime


DRIVER_ID = 1
TIMESTEPS = 60  # if the preformatted csv's were used, they were made with timesteps of 60

dirs = ["train", "val", "test"]
paths = [os.path.join("data", "formatted_data", str(DRIVER_ID), "train_merged.csv"),  # train
         os.path.join("data", "formatted_data", str(DRIVER_ID), "val_merged.csv"),  # val
         os.path.join("data", "formatted_data", str(DRIVER_ID), "test_merged.csv")]  # test
samples = []  # number of samples
features = []  # number of features
data = []
labels = []
train_session = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
if not os.path.exists(train_session):
    os.makedirs(train_session)
print("=============================================")
print("Saving session in ./{}".format(train_session))
print("=============================================")

# load the data
for idx, path in enumerate(paths):
    set_data = pd.read_csv(path, sep=',')
    set_data.drop(["trip_start"], axis=1, inplace=True)  # this is a useless row for training

    # extract train labels
    set_labels = set_data["driver_label"].as_matrix()
    set_data.drop(["driver_label"], axis=1, inplace=True)

    # extract train features
    set_data = set_data.as_matrix()
    num_samples = set_data.shape[0]
    num_features = set_data.shape[1]
    samples.append(num_samples)
    features.append(num_features)
    print("{} shape before".format(dirs[idx]))
    print(set_data.shape)
    print(set_labels.shape)
    set_data = set_data.reshape(int(num_samples/TIMESTEPS), TIMESTEPS, num_features)
    set_labels = set_labels.reshape(int(num_samples/TIMESTEPS), TIMESTEPS)
    print("{} shape after".format(dirs[idx]))
    print(set_data.shape)
    print(set_labels.shape)

    data.append(set_data)
    labels.append(set_labels)

model = Sequential()
model.add(Conv1D(filters=32, kernel_size=1, input_shape=(TIMESTEPS, features[0]), kernel_initializer='uniform', activation='relu'))
model.add(MaxPooling1D(pool_size=1))
model.add(LSTM(200, dropout=0.3))
model.add(Dense(TIMESTEPS, activation='sigmoid', init='uniform'))
#model.add(Activation('sigmoid'))
model.compile(loss="binary_crossentropy", optimizer=Adam(lr=0.03), metrics=["binary_accuracy", "accuracy"])

print(model.summary())
plot_model(model, to_file=os.path.join(train_session, "model.png"), show_shapes=True, show_layer_names=True)
tensorboard = TensorBoard(log_dir=os.path.join(train_session, "tensorboard_log"))

# train the model
history = model.fit(data[0], labels[0], epochs=50, batch_size=TIMESTEPS, validation_data=(data[1], labels[1]), verbose=1, callbacks=[tensorboard])

# save the model
model.save(os.path.join(train_session, "model.h5"))

# list all data in history
print(history.history.keys())

# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
# plt.show()
plt.savefig(os.path.join(train_session, "model_accuracy.png"))

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
# plt.show()
plt.savefig(os.path.join(train_session, "model_loss.png"))

scores = model.evaluate(data[2], labels[2], verbose=1)
print("Accuracy: {:.2f}%".format(scores[1]*100))
