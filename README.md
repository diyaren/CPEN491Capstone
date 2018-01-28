# cpen491
Capstone project for Cab4You

## Setting up
### First install the necessary frameworks
```
pip install -r /path/to/requirements.txt
```
### To test, run this command in the `env/` directory:
```
python manage.py runserver
```
<br><br>
Now try some API calls like:<br>
```
curl -H 'Accept: application/json; indent=4' -u <username>:<password> http://127.0.0.1:8000/users/
```
