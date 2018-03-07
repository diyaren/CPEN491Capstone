from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os
from random import randint
from pusher_push_notifications import PushNotifications


UPLOAD_DIR = 'logs/'	#temp dir

app = Flask(__name__)
app.config['UPLOAD_DIR'] = UPLOAD_DIR


pn_client = PushNotifications(
    instance_id='105aa624-524f-4fca-84a5-ee1f86872ece',
    secret_key='74E645E65BAE00A26F2EE06464DF4D6',
)

#import sys

#sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/model')
#from predict_model import predict

"""
TODO
- decide on request content-header format: DONE
- decide on location data format: DONE
- write tmaIDs to file or DB for crash resistance
- utilize file save and restore for models/Implement models
- use file upload for logs: DONE
- use celery for async task? if model takes too long to compute
- add notifying CMA of driver anomly
"""

# Current data structure for TMA registration and location storage; change to file/DB later
tma_locations = {}
#temp data structure to register driver models and results; to be replaced with machine learning model archnitecture
driver_results = {}
#saved log IDs from driver anomlys
logIDs = []

#Translation from tmaID to current driverID according to dispatch system
def tmaID_to_driverID(tma_id):
	#TODO hookup to dispatch
	return tma_id;

#placeholder model
def make_prediction(driver_id):
	x = randint(0,9)
	if x < 3:
		return False
	else:
		return True
	
#Endpoints to enable TMA tracking functionalities

#Get locations of registered TMAs
@app.route('/tma', methods=['GET'])
def get_tma():
	return jsonify(tma_locations), 200

#Create/Register a new TMA
@app.route('/tma/<string:tma_id>', methods=['POST'])
def post_tma(tma_id):
	if tma_id in tma_locations:
		return jsonify({'error': 'tma_id "%s" already exists' % tma_id}), 409
	else:
		tma_locations[tma_id] = {}
		return 'tma created with tma_id "%s"' % tma_id, 201

#Update a single TMA's location
@app.route('/tma/<string:tma_id>', methods=['PUT'])
def  put_tma(tma_id):
	location_data = request.json.get('location_data')
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" does not exist' % tma_id}), 404
	elif location_data == None:
		return jsonify({'error':'No {location_data} in body of request'}), 400
	else:
		tma_locations[tma_id] = location_data
		return 'tma %s location data updated' % tma_id, 200

#Unregister a single TMA
@app.route('/tma/<string:tma_id>', methods=['DELETE'])
def  delete_tma(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" does not exist' % tma_id}), 404
	else:
		del tma_locations[tma_id]
		return 'tma with tma_id "%s" deleted' % tma_id, 200

#Endpoints for driver models
		
#Create a new model for a driver
@app.route('/model/<string:tma_id>', methods=['POST'])
def post_model(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 404
	if driver_id in driver_results:
		return jsonify({'error':'tma_id "%s" corresponds to a driver which already has a model' % tma_id}), 403
		
	driver_results[driver_id] = 0
	return 'model for driver "%s" created' % driver_id, 201

#Train a single driver model with a log
@app.route('/model/<string:tma_id>', methods=['PATCH'])
def patch_model(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 404
	if driver_id not in driver_results:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver model' % tma_id}), 400
		
	if 'log' not in request.files:
		return jsonify({'error':'no log file attached'}), 400
	else:
		file = request.files['log']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
		return 'saved file', 200

#Delete a single driver model
@app.route('/model/<string:tma_id>', methods=['DELETE'])
def delete_model(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 400
	if driver_id not in driver_results:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver model' % tma_id}), 400
	
	del driver_results[driver_id]
	return 'model for driver "%s" deleted' % driver_id, 200
	
#Endpoints for model predictions

#Get most recent prediction for a single driver
@app.route('/model/<string:tma_id>/result', methods=['GET'])
def get_model_result(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 400
	if driver_id not in driver_results:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver model' % tma_id}), 400
		
	result = driver_results[driver_id]
	if result == 0:
		return jsonify({'result':'not yet calculated'}), 204
	elif result == -1:
		return jsonify({'result':False}), 200
	else:
		return jsonify({'result':True}), 200

#Update prediction for a single driver based on log
@app.route('/model/<string:tma_id>/result', methods=['PATCH'])
def patch_model_result(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 404
	if driver_id not in driver_results:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver model' % tma_id}), 400
		
	if 'log' not in request.files:
		return jsonify({'error':'no log file attached'}), 400
	else:
		file = request.files['log']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
		
	#temp prediction
	pred = make_prediction(driver_id)
	driver_results[driver_id] = make_prediction(driver_id)
	if pred == False:
		logIDs.append(driver_id)		# just insert driver_id as a log_id for now
		response = pn_client.publish(
    		interests=['prediction'],
    		"fcm": {
      			"notification": {
        			"title": "Hi!",
        			"body": "This is my first Push Notification!"
      			}
    		}
		)
		print(response['publishId'])
	return 'log saved, prediction made', 200
	

#Confirm whether driver anomly was correct or incorrect
@app.route('/model/<string:tma_id>/result', methods=['PUT'])
def put_model_result(tma_id):
	if tma_id not in tma_locations:
		return jsonify({'error':'tma_id "%s" is not registered' % tma_id}), 404
	driver_id = tmaID_to_driverID(tma_id)
	if driver_id == None:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver according to dispatch' % tma_id}), 404
	if driver_id not in driver_results:
		return jsonify({'error':'tma_id "%s" does not correspond to a driver model' % tma_id}), 400
	result_confirm = request.json.get('result_confirm')
	if result_confirm == None:
		return jsonify({'error':'No {result_confirm} in body of request'}), 400
		
	logIDs.remove(driver_id)	#remove log after processing confirmation
	return 'log correction applied (or not)', 200
	

if __name__ == "__main__":
	app.run(host="0.0.0.0")
