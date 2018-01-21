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

# install requirements
pip install -r requirements.txt

```

## Formatting Data
If you want to format more of your own data or mess with feature engineering, download the big
[axa dataset](https://github.com/ChicagoBoothML/DATA___Kaggle___AXADriverTelematicsAnalysis).
and save its contents to ```./data/axa_original```

```
cd data/

# see available options, default args should be fine
python format_data.py --help

# formatted data will be in ./data/formatted_data
```
