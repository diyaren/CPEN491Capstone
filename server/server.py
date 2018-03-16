from flask import Flask, jsonify, request, json
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pusher_push_notifications import PushNotifications
from random import randint
import time
import multiprocessing
import sys
import utils

# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/model')
# from predict_model import predict


app = Flask(__name__)


pn_client = PushNotifications(
    instance_id='105aa624-524f-4fca-84a5-ee1f86872ece',
    secret_key='74E645E65BAE00A26F2EE06464DF4D6',
)

#DB setup
DEFAULT_DB_PATH = 'test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/' + DEFAULT_DB_PATH

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Logs(db.Model):
    driverID = db.Column(db.Integer, primary_key=True)
    sessionNum = db.Column(db.Integer, primary_key=True)
    sampleNum = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(255))
    timeLong = db.Column(db.Integer)
    xCoord = db.Column(db.Float)
    yCoord = db.Column(db.Float)
    __tablename__ = 'Logs'


class TMAs(db.Model):
    tmaID = db.Column(db.Integer, primary_key=True)
    xCoord = db.Column(db.Float)
    yCoord = db.Column(db.Float)
    __tablename__ = 'TMAs'


class FalsePredictions(db.Model):
    driverID = db.Column(db.Integer, primary_key=True)
    sessionNum = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(255))
    __tablename__ = 'FalsePredictions'


class LogsSchema(ma.ModelSchema):
    class Meta:
        model = Logs


class TMAsSchema(ma.ModelSchema):
    class Meta:
        model = TMAs


class FalsePredictionsSchema(ma.ModelSchema):
    class Meta:
        model = FalsePredictions


# Translation from tmaID to current driverID according to dispatch system
def tmaID_to_driverID(tma_id):
    # TODO hookup to dispatch
    return tma_id;


# placeholder model
def make_prediction(driver_id):
    time.sleep(5)  # example model take 5s to make predictions
    x = randint(0, 9)
    if x < 3:
        return 0
    else:
        return 1


# placeholder multiprocessing model
def make_prediction_async(driver_id, session_num, start_time):
    print('async: making prediction')
    time.sleep(5)  # example model take 5s to make predictions
    x = randint(0, 9)
    if x < 3:
        #push notification
        response = pn_client.publish(
            interests=['prediction'],
            publish_body={
                'fcm': {
                    'notification': {
                        'title': 'Hi!',
                        'body': 'This is my first Push Notification!'
                    }
                }
            }
        )
        print(response['publishId'])
        # store pending confirmation
        new_false_prediction = FalsePredictions(driverID=driver_id, sessionNum=session_num, time=start_time)
        db.session.add(new_false_prediction)
        db.session.commit()
    print('async: prediction made for driver' + driver_id)
    return


#false async prediction to test data flow
def make_false_prediction_async(driver_id, session_num, start_time):
    print('async: making false prediction')
    time.sleep(5)
    #push notification here too

    #store pending confirmation
    new_false_prediction = FalsePredictions(driverID=driver_id, sessionNum=session_num, time=start_time)
    db.session.add(new_false_prediction)
    db.session.commit()
    print('async: false prediction made')
    return


# QUICK TEST ROUTE; IGNORE
@app.route('/db/<int:tma_id>', methods=['POST'])
def db_test_route(tma_id):
    return jsonify({"status": "success", "data": None}), 200


#Test for push notifications
@app.route('/tma/push', methods=['POST'])
def push_notif():
    response = pn_client.publish(
        interests=['prediction'],
        publish_body={
            'fcm': {
                'notification': {
                    'title': 'Hi!',
                    'body': 'This is my first Push Notification!',
                }
            }
        }
    )
    print(response['publishId'])
    return 'push notification sent', 200


# Endpoints to enable TMA tracking functionalities

# Get locations of registered TMAs
@app.route('/tma', methods=['GET'])
def get_tma():
    tmas = TMAs.query.all()
    tmas_result = TMAsSchema(many=True).dump(tmas)
    return jsonify({"status": "success", "data": {"tmas": tmas_result}}), 200


# Create/Register a new TMA
@app.route('/tma/<int:tma_id>', methods=['POST'])
def post_tma(tma_id):
    exists = db.session.query(TMAs.tmaID).filter_by(tmaID=tma_id).scalar()

    if exists is not None:
        return jsonify({"status": "fail", "data": {"tma_id": "%s already exists" % tma_id}}), 409
    else:
        new_tma = TMAs(tmaID=tma_id)
        db.session.add(new_tma)
        db.session.commit()
        return jsonify({"status": "success", "data": None}), 201


# Update a single TMA's location
@app.route('/tma/<int:tma_id>', methods=['PUT'])
def put_tma(tma_id):
    tma = TMAs.query.get(tma_id)
    coordinates = request.json.get('coordinates')

    if tma is None:
        return jsonify({"status": "fail", "data": {"tma_id": "%s does not exist" % tma_id}}), 404
    elif coordinates is None:
        return jsonify({"status": "fail", "data": {"coordinates": "No coordinates list in body of request"}}), 400
    else:
        tma.xCoord = coordinates[0]
        tma.yCoord = coordinates[1]
        db.session.commit()
        return jsonify({"status": "success", "data": None}), 200


# Unregister a single TMA
@app.route('/tma/<int:tma_id>', methods=['DELETE'])
def delete_tma(tma_id):
    tma = TMAs.query.get(tma_id)

    if tma is None:
        return jsonify({"status": "fail", "data": {"tma_id": "%s does not exist" % tma_id}}), 404
    else:
        db.session.delete(tma)
        db.session.commit()
        return jsonify({"status": "fail", "data": None}), 200


# Endpoints for model predictions

# Update prediction for a single driver based on log
@app.route('/prediction/<int:tma_id>', methods=['POST'])
def post_prediction(tma_id):
    tma_exists = db.session.query(TMAs.tmaID).filter_by(tmaID=tma_id).scalar()
    if tma_exists is None:
        return jsonify({"status": "fail", "data": {"tma_id": "%s is not registered" % tma_id}}), 400

    driver_id = tmaID_to_driverID(tma_id)
    if driver_id is None:
        return jsonify({"status": "fail",
                        "data": {"tma_id": "%s does not correspond to a driver according to dispatch" % tma_id}}), 404

    if 'log' not in request.files:
        return jsonify({"status": "fail", "data": {"log": "no log file attached"}}), 400
    else:
        file = request.files['log']
        data = json.loads(file.read())
        try:
            new_session_num = db.session.query(func.max(Logs.sessionNum)).filter_by(driverID=driver_id).scalar() + 1
        except TypeError:
            new_session_num = 0
        new_sample_num = 0
        start_time = data['features'][0]['properties']['time']
        for feature in data['features']:
            (x, y) = utils.cartesian(feature['geometry']['coordinates'][1],
                                     feature['geometry']['coordinates'][0])[:2]
            new_log = Logs(
                driverID=driver_id,
                sessionNum=new_session_num,
                sampleNum=new_sample_num,
                time=feature['properties']['time'],
                timeLong=feature['properties']['time_long'],
                xCoord=x,
                yCoord=y
            )
            db.session.add(new_log)
            new_sample_num += 1
        db.session.commit()

        # temp prediction
        p = multiprocessing.Process(target=make_prediction_async, args=(driver_id, new_session_num, start_time))
        #p = multiprocessing.Process(target=make_false_prediction_async, args=(driver_id, new_session_num, start_time,))
        p.start()
        return jsonify({"status": "success", "data": None}), 200


# Confirm whether driver anomly was correct or incorrect
@app.route('/prediction/<int:driver_id>', methods=['PATCH'])
def patch_prediction(driver_id):
    prediction_confirmation = request.json.get('prediction_confirmation')
    if prediction_confirmation is None:
        return jsonify({"status": "fail",
                        "data": {"prediction_confirmation": "No {prediction_confirmation} in body of request"}}), 400

    session_num = request.json.get('session_num')
    if session_num is None:
        return jsonify({"status": "fail", "data": {"session_num": "No {session_num} in body of request"}}), 400

    if prediction_confirmation:
        logs = db.session.query(Logs).filter_by(
            driverID=driver_id,
            sessionNum=session_num
        )
        logs.delete()
        db.session.commit()
    else:
        #retrain on this driver with new data already in database
        print('retraining')

    false_prediction = db.session.query(FalsePredictions).filter_by(
        driverID=driver_id,
        sessionNum=session_num
    )
    false_prediction.delete()
    db.session.commit()
    return jsonify({"status": "success", "data": None}), 200

# Get all the false predictions which are pending confirmation
@app.route('/prediction/false', methods=['GET'])
def get_false_predictions():
    false_predictions = FalsePredictions.query.all()
    false_predictions_result = FalsePredictionsSchema(many=True).dump(false_predictions)
    return jsonify({"status": "success", "data": {"false_predictions": false_predictions_result}}), 200


def init_db(args):
    if len(args) >= 2:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/' + args[1]

    db.create_all()


if __name__ == '__main__':
    init_db(sys.argv)
    app.run(host="0.0.0.0")
