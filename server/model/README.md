# cpen491/server/model/
directory for the **ML model** component of the project

## Installing Dependencies
```
# create a virtualenv
virtualenv venv

# on windows
source venv/scripts/activate

# or OSX/Linux
source venv/bin/activate

# Note on requirements:
# requirements.txt has tensorflow-gpu as a requirement, if you're not running
# with gpu, change it to just tensorflow. You can also try Theano as a backend,
# but.  You'd also have to change train_model.py [to take Theano as a backend](https://keras.io/#switching-from-tensorflow-to-cntk-or-theano).

# install requirements
pip install -r requirements.txt

```

## Formatting Data (optional, preformatted data is data/formatted_data/)
If you want to format more of your own data or mess with feature engineering, download the big
[axa dataset](https://github.com/ChicagoBoothML/DATA___Kaggle___AXADriverTelematicsAnalysis).
and save its contents to ```./data/axa_original```
```
cd data/

# see available options, default args should be fine
python format_data.py --help

# formatted data will be in ./data/formatted_data
```

## Visualizing Training
Keras supports Tensorboard, so you can watch the training curves during the session.
```
# in one console
python train_model.py

# in another console
tensorboard --logdir={the_session_directory}/tensorboard_log

# in a browser go to the url printed out by the tensorboard console
```

## Prediction After Training
After training, a directory of the form ```{date}_{time}/``` will be created.
This directory has the following structure:
```
20180125_223145/                      # directory of the training session
	tensorboard_log/	      # directory containing log for tensorboard
	    events.out.tfevents...    # tensorboard log
	model.h5		      # model saved after training (Keras compatible HDF5 format)
	model.png		      # Graphviz diagram of model structure
	model_accuracy.png	      # model accuracy during training and testing
	model_loss.png		      # loss during model training and testing
```

After training is complete, you can run the following to observe the output of
the test set.
```
# pipe the output to a file, because there's a lot
python predict_model.py --model 20180125_223145/model.h5 --driver_id 1 > test_output
```
