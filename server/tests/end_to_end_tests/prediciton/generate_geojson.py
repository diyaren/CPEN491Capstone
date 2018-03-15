# generate some biased log data
from random import uniform
import json
import pprint


def generate_driver_data(fp, points, starting_lat, delta_lat, starting_long, delta_long):
    # generate some biased data for driver1
    with open(fp, 'w') as f:
        features = []
        for idx, i in enumerate(list(range(points))):
            features.append({
                "geometry": {
                    "coordinates": [starting_lat + uniform(-1,1)*idx*delta_lat, starting_long + uniform(-1,1)*idx*delta_long],
                    "type": "Point"
                },
                "properties": {
                    "accuracy": "12.0",
                    "altitude": "12.9",
                    "bearing": "123.2",
                    "provider": "gps",
                    "speed": "13.2",
                    "time": "2018-02-27T06:12:12.000Z",
                    "time_long": "1519714121000"},
                "type": "Feature"
            })
        ret = {
            "features": features,
            "type": "FeatureCollection"
        }

        json.dump(ret, f)

if __name__ == "__main__":
    generate_driver_data("super_biased_driver1.geojson", 142, -123.2557982, -0.000021, 49.2676523, -0.000011)
    generate_driver_data("super_biased_driver2.geojson", 152, -123.25269178, -0.000021, 49.26446524, -0.000011)
