import requests
import json
import time
import random
import sys

URL = 'https://williamstest.joincartel.com'
NUM_TMAS = 5
DATA_FILE = 'marine_to_kingsway.geojson'
UPDATE_FREQ = 3


if __name__ == "__main__":
    i = 0;
    base_locations = []
    data_max_index = 0

    with open(DATA_FILE, 'r') as fp:
        data = json.loads(fp.read())
        data_max_index = len(data['features']) - 1

    for x in range(NUM_TMAS):
        r = requests.delete(URL+'/tma/'+str(x), verify=False)
        r = requests.post(URL+'/tma/'+str(x), verify=False)
        base_locations.append( random.randint(0, data_max_index) )

    print('TMA simulations started')
    while 1:
        with open(DATA_FILE, 'r') as fp:
            for x in range(NUM_TMAS):
                coord_index = (i*UPDATE_FREQ + base_locations[x]) % data_max_index
                coordinates = data['features'][coord_index]['geometry']['coordinates']
                r = requests.put(URL+'/tma/'+str(x),
                                 json={"coordinates": coordinates},
                                 verify=False)
                print('Updated TMA ' + str(x) + 'with coordinates ' + str(coordinates))
        i += 1
        time.sleep(UPDATE_FREQ)
