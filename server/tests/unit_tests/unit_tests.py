import os
import sys
import unittest
import json

TEST_DB = 'unittest.db'

two_up = os.path.abspath(os.path.join(__file__, '../../..'))
sys.path.append(two_up)

from server import app, db, FalsePredictions


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

    def test_post_prediction(self):
        res = self.app.post('tma/1')

        with open('test_data.geojson', 'rb') as fp:
            data = {'log': (fp, fp.name)}

            res = self.app.post('/prediction/1',
                                data=data,
                                content_type='multipart/form-data')
            self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()
