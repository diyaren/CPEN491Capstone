import requests
import sys

URL = 'https://williamstest.joincartel.com'

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python sim_tma_post_log.py [.geojson file] [tma_id]')
        exit(0)

    files = {'log': open(sys.argv[1], 'rb')}
    r = requests.post(URL + '/prediction/' + sys.argv[2], files=files, verify=False)
    print('request sent')
