import os
import sys
import unittest
import json

TEST_DB = 'unittest.db'
TEST_DATA = 'test_data2.geojson'
TEST_NEG_SAMPLES = 'neg_samples.geojson'

two_up = os.path.abspath(os.path.join(__file__, '../../..'))
sys.path.append(two_up)

from server import app, db, FalsePredictions, Logs
from utils import cartesian


class BasicUnitTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/' + TEST_DB
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        pass

    # TESTS
    def test_get_tmas(self):
        res = self.app.get('/tma')
        self.assertEqual(res.status_code, 200)

    def test_post_tma(self):
        res = self.app.post('/tma/0')
        self.assertEqual(res.status_code, 201)

    def test_post_tma_twice(self):
        res = self.app.post('/tma/0')
        res = self.app.post('/tma/0')
        self.assertEqual(res.status_code, 409)

    def test_delete_tma(self):
        res = self.app.post('/tma/0')
        res = self.app.delete('/tma/0')
        self.assertEqual(res.status_code, 200)

    def test_delete_tma_twice(self):
        res = self.app.post('/tma/0')
        res = self.app.delete('/tma/0')
        res = self.app.delete('/tma/0')
        self.assertEqual(res.status_code, 404)

    def test_put_tma(self):
        res = self.app.post('/tma/0')
        res = self.app.put('/tma/0',
                           data=json.dumps(dict(coordinates=[1.0, 42.0])),
                           content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.app.get('/tma')
        data = json.loads(res.get_data(as_text=True))
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data']['tmas'][0]['xCoord'], 1.0)
        self.assertEqual(data['data']['tmas'][0]['yCoord'], 42.0)

    def test_put_tma_no_tma(self):
        res = self.app.put('/tma/0',
                           data=json.dumps(dict()),
                           content_type='application/json')
        self.assertEqual(res.status_code, 404)

    def test_put_tma_no_coords(self):
        res = self.app.post('/tma/0')
        res = self.app.put('/tma/0',
                           data=json.dumps(dict()),
                           content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_get_false_predictions(self):
        new_false_prediction = FalsePredictions(driverID=0, sessionNum=0, time='test_time')
        db.session.add(new_false_prediction)
        db.session.commit()

        res = self.app.get('prediction/false')
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.get_data(as_text=True))
        self.assertEqual(data['data']['false_predictions'][0]['time'], 'test_time')

    def test_patch_prediction_true(self):
        new_false_prediction = FalsePredictions(driverID=0, sessionNum=0, time='test_time')
        db.session.add(new_false_prediction)
        db.session.commit()

        res = self.app.patch('prediction/0',
                             data=json.dumps(dict(session_num=0, prediction_confirmation=True)),
                             content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.app.get('prediction/false')
        data = json.loads(res.get_data(as_text=True))
        self.assertEqual(len(data['data']['false_predictions']), 0)

    def test_patch_prediction_false(self):
        new_false_prediction = FalsePredictions(driverID=0, sessionNum=0, time='test_time')
        db.session.add(new_false_prediction)
        db.session.commit()

        res = self.app.patch('prediction/0',
                             data=json.dumps(dict(session_num=0, prediction_confirmation=True)),
                             content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.app.get('prediction/false')
        data = json.loads(res.get_data(as_text=True))
        self.assertEqual(len(data['data']['false_predictions']), 0)

    def test_patch_prediction_no_confirmation(self):
        res = self.app.patch('prediction/0',
                             data=json.dumps(dict(session_num=0)),
                             content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_prediction_no_session_num(self):
        res = self.app.patch('prediction/0',
                             data=json.dumps(dict(prediction_confirmation=True)),
                             content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_prediction_bad_tma(self):
        with open(TEST_DATA, 'rb') as fp:
            data = {'log': fp}
            res = self.app.post('/prediction/1',
                                data=data,
                                content_type='multipart/form-data')
            self.assertEqual(res.status_code, 400)

    def test_post_prediction_no_log(self):
        res = self.app.post('tma/1')
        with open(TEST_DATA, 'rb') as fp:
            data = {'not_log': fp}
            res = self.app.post('/prediction/1',
                                data=data,
                                content_type='multipart/form-data')
            self.assertEqual(res.status_code, 400)
    '''
    def test_post_prediction(self):
        init_neg_samples()
        res = self.app.post('tma/1')

        with open(TEST_DATA, 'rb') as fp:
            data = {'log': fp}

            res = self.app.post('/prediction/1',
                                data=data,
                                content_type='multipart/form-data')
            self.assertEqual(res.status_code, 200)
    '''


# HELPERS
def init_neg_samples():
    with open(TEST_NEG_SAMPLES, 'rb') as fp:
        data = json.loads(fp.read())
        new_session_num = 0
        new_sample_num = 0

        # need to normalize trip to start at 0,0
        x0 = data['features'][0]['geometry']['coordinates'][1]
        y0 = data['features'][0]['geometry']['coordinates'][0]
        (x0, y0) = cartesian(x0, y0)[:2]
        for feature in data['features']:
            (x, y) = cartesian(feature['geometry']['coordinates'][1],
                               feature['geometry']['coordinates'][0])[:2]
            new_log = Logs(
                driverID=2,
                sessionNum=new_session_num,
                sampleNum=new_sample_num,
                time=feature['properties']['time'],
                timeLong=feature['properties']['time_long'],
                xCoord=x - x0,
                yCoord=y - y0
            )
            db.session.add(new_log)
            new_sample_num += 1
        db.session.commit()


if __name__ == '__main__':
    unittest.main()
