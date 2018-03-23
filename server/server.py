from flask import Flask, jsonify, request, json
from sqlalchemy import func, and_
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from pusher_push_notifications import PushNotifications
import time
import multiprocessing
import os
import sys

import utils
from model.random_forest import predict_model, train_model

PREDICTION_THRESHOLD = 0.3
CURDIR = os.path.abspath(os.curdir)
TRAINED_MODELS_DIR = os.path.join(CURDIR, "model", "trained_models")

app = Flask(__name__)

pn_client = PushNotifications(
    instance_id='105aa624-524f-4fca-84a5-ee1f86872ece',
    secret_key='74E645E65BAE00A26F2EE06464DF4D6',
)

#DB setup
DEFAULT_DB_PATH = 'test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/' + DEFAULT_DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# Asynchronous Prediction Using ML Model
def make_prediction_async(driver_id, session_num, start_time):
    model_fp = os.path.join(TRAINED_MODELS_DIR, str(driver_id) + ".pkl")

    if not os.path.exists(TRAINED_MODELS_DIR):
        os.makedirs(TRAINED_MODELS_DIR)

    if os.path.isfile(model_fp):
        # if model exists
        print("using trained model for driver: {}".format(driver_id))
        print("fp: {}".format(model_fp))

        # grab most recent trip session
        logs = db.session.query(Logs).filter(and_(Logs.driverID==driver_id, Logs.sessionNum==session_num)).order_by(
            Logs.sessionNum.asc(),
            Logs.sampleNum.asc())
        logs_result = LogsSchema(many=True).dump(logs)

        trip = []
        for position in logs_result.data:
            trip.append([position["xCoord"], position["yCoord"]])

        prediction = predict_model(driver_id, model_fp, trip)[0][1]  # returned value is probabilities of [negative_driver, positive_driver]

        print("Model's confidence in the driver: {}".format(prediction))
        # act on prediction
        if prediction < PREDICTION_THRESHOLD:
            print("anomaly detected, sending push notification for driver_id: {}".format(driver_id))
            # send notification
            response = pn_client.publish(
                interests=['prediction'],
                publish_body={
                    'fcm': {
                        'notification': {
                            'title': 'anomaly detected',
                            'body': str(driver_id)
                        }
                    }
                }
            )

            # store pending confirmation
            new_false_prediction = FalsePredictions(driverID=driver_id, sessionNum=session_num, time=start_time)
            db.session.add(new_false_prediction)
            db.session.commit()
    else:
        # else train a new model
        print("training new model for driver: {}".format(driver_id))

        # grab all positive trips
        logs = db.session.query(Logs).filter(Logs.driverID==driver_id).order_by(
            Logs.sessionNum.asc(),
            Logs.sampleNum.asc())
        logs_result = LogsSchema(many=True).dump(logs)

        pos_trips = []
        temp_trip = []
        session_number = 0
        for position in logs_result.data:
            if position["sessionNum"] == session_number:
                temp_trip.append([position["xCoord"], position["yCoord"]])
            else:
                # new session
                pos_trips.append(temp_trip)
                temp_trip = []
                session_number = position["sessionNum"]
        # when there is only 1 session in the db
        if not pos_trips:
            pos_trips.append(temp_trip)


        # grab same number of negative trips
        logs = db.session.query(Logs).filter(Logs.driverID!=driver_id).order_by(
            Logs.sessionNum.asc(),
            Logs.sampleNum.asc())
        logs_result = LogsSchema(many=True).dump(logs)

        pos_sessions = len(pos_trips)  # ensure balanced training set
        neg_sessions = 0
        neg_trips = []
        temp_trip = []
        session_number = 0
        for idx, position in enumerate(logs_result.data):
            if neg_sessions >= pos_sessions:
                break

            if position["sessionNum"] == session_number:
                temp_trip.append([position["xCoord"], position["yCoord"]])
            else:
                # new session
                neg_trips.append(temp_trip)
                temp_trip = []
                session_number = position["sessionNum"]
                neg_sessions += 1
        # when there is only 1 session in the db
        if not neg_trips:
            neg_trips.append(temp_trip)

        # normalize the two sample sets
        if len(neg_trips) < len(pos_trips):
            del pos_trips[len(neg_trips):]

        train_model(driver_id, model_fp, pos_trips, neg_trips)


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


# QUICK TEST ROUTES; IGNORE
@app.route('/db/<int:tma_id>', methods=['POST'])
def db_test_route(tma_id):
    return jsonify({"status": "success", "data": None}), 200


@app.route("/test_logs", methods=["GET"])
def db_test_logs():
    max_session_num = db.session.query(func.max(Logs.sessionNum)).filter_by(driverID=1).scalar()
    logs = db.session.query(Logs).filter(and_(Logs.driverID==1, Logs.sessionNum==max_session_num)).order_by(
        Logs.sessionNum.asc(),
        Logs.sampleNum.asc())
    logs_result = LogsSchema(many=True).dump(logs)
    return jsonify({"logs": logs_result}), 200


@app.route("/test_logs_negs", methods=["GET"])
def db_test_logs_neg():
    logs = db.session.query(Logs).filter(Logs.driverID!=1).order_by(
        Logs.driverID.asc(),
        Logs.sessionNum.asc(),
        Logs.sampleNum.asc())
    logs_result = LogsSchema(many=True).dump(logs)
    return jsonify({"logs": logs_result}), 200


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
    return jsonify({"status": "success", "data": {"tmas": tmas_result.data}}), 200


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
        return jsonify({"status": "success", "data": None}), 200


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

    print(request.files)
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

        # need to normalize trip to start at 0,0
        x0 = data['features'][0]['geometry']['coordinates'][1]
        y0 = data['features'][0]['geometry']['coordinates'][0]
        (x0, y0) = utils.cartesian(x0, y0)[:2]
        for feature in data['features']:
            (x, y) = utils.cartesian(feature['geometry']['coordinates'][1],
                                     feature['geometry']['coordinates'][0])[:2]
            new_log = Logs(
                driverID=driver_id,
                sessionNum=new_session_num,
                sampleNum=new_sample_num,
                time=feature['properties']['time'],
                timeLong=feature['properties']['time_long'],
                xCoord=x-x0,
                yCoord=y-y0
            )
            db.session.add(new_log)
            new_sample_num += 1
        db.session.commit()

        # temp prediction
        p = multiprocessing.Process(target=make_prediction_async, args=(driver_id, new_session_num, start_time,))
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
        model_fp = os.path.join(TRAINED_MODELS_DIR, str(driver_id) + ".pkl")

        #retrain on this driver by removing the old model
        if os.path.isfile(model_fp):
            os.remove(model_fp)
            print('removed model for driver {}, it will be created during next prediction'.format(str(driver_id)))

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
    return jsonify({"status": "success", "data": {"false_predictions": false_predictions_result.data}}), 200


def init_db(args):
    if len(args) >= 2:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/' + args[1]

    db.create_all()


if __name__ == '__main__':
    init_db(sys.argv)
    app.run(host="0.0.0.0")
