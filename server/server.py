from flask import Flask, jsonify, request
app = Flask(__name__)

"""
TODO
- decide on request content-header format
- decide on location data format
- 
- utilize file save and restore for models
- use file upload for logs?
- use celery for async task? if model takes too long to compute
"""

#format of this dictionary needs to be clarified
tma_locations = {
	'1' : {'long': 42, 'lat': 84}
}

#Tracking Functionalities
@app.route('/location', methods=['GET', 'POST'])
def location():
	if request.method == 'GET':
	#return all tma locations
		return jsonify(tma_locations), 200
	
	elif request.method == 'POST':
		tma_id = request.form.get('tma_id')		#TODO: decide if using form or json request objects
		if tma_id == None:
			return jsonify({'Error': 'No tma_id field'}), 400
		else:
			tma_locations[tma_id] = {'long': 100, 'lat': 200}	#Additional location data TBD
			return jsonify({'response': 'successfully updated location'}), 200
			
@app.route('/model', methods=['POST'])
def model():
	"""
	response.file to access any files
	use response.form.get('tma_id') to open model from file
	
	format log?
	celery? input data into model, response async?
	
	push notifications/notify app
	"""
	return jsonify({'response': 'dummy response'}), 200
