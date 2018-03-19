# cpen491/server/model/
directory for the **ML model** component of the project

Files in ```./trained_models/``` contain trained models, format of filename is ```[driver_id].pkl```.  
Other ```*.py``` files in the current directory contain methods for predicting/training various models.

## Installing Dependencies
```
# create a virtualenv
virtualenv venv

# on windows
source venv/scripts/activate

# or OSX/Linux
source venv/bin/activate

# install requirements
pip install -r requirements.txt

```

## Formatting Data
If you want to format more of your own data or mess with feature engineering, download the big
[axa dataset](https://github.com/ChicagoBoothML/DATA___Kaggle___AXADriverTelematicsAnalysis).
and save its contents to ```./data/axa_original```

## Train model 
This will save the model in a directory like `/20180131_071447` which will contain the pickled model
```
python train_model_randomforest_classifier.py
```
