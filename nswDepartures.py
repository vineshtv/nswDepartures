import sys
import os
import requests
import argparse
import datetime as dt
from dateutil import tz
import pytz
from collections import defaultdict
import bisect

'''
stopid = '201016' #busttop at central towards wollstonecraft.
stopid = '2000336' #central pl 16
stopid = '206429' #foxsports
stopid = '2065138' #Busstop at wollstonecraft towards sydney
stopid = '200064' #Busstop at central.
stopid = '2065161'  #Wollstonecraft p1
stopid = '206022' #Waverton bustop
stopid = '206511' #Wollstonecraft bustop near the railway station
'''


class QueryNswDepartures(object):
    def __init__(self, stop_id):
        self.api_key = os.environ.get('NSW_API_KEY')
        self.api_base_url = 'https://api.transport.nsw.gov.au/v1/tp/'
        self.api_call = 'departure_mon'
        self.stopid = stop_id  # '200064'  # By default queries the bustop at central
        self.stop_name = ''
        self.params = {
            'outputFormat': 'rapidJSON',
            'coordOutputFormat': 'EPSG:4326',
            'mode': 'direct',
            'type_dm': 'stop',
            'name_dm': self.stopid,
            'depArrMacro': 'dep',
            'itdDate': dt.datetime.today().strftime("%Y%m%d"),
            'itdTime': dt.datetime.today().strftime("%H%M"),
            'TfNSWTR': 'true'
        }
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'apikey {self.api_key}'
        }
        self.departures = defaultdict(list)

    @property
    def stopid(self):
        return self.__stopid

    @stopid.setter
    def stopid(self, stopid):
        self.__stopid = stopid

    def query_departures(self):
        self.params['name_dm'] = self.stopid
        try:
            response = requests.get(f'{self.api_base_url}{self.api_call}',
                                    params=self.params,
                                    headers=self.headers)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        if response.status_code == 200:
            data = response.json()

            # Get the stop name
            self.stop_name = data.get('locations')[0].get('name', '')

            # Timezone calculations
            utc_tz = tz.tzutc()

            for event in data['stopEvents']:
                # Try to get the estimated departure time and if it is
                # not present, then get the planned departure time
                dpt = event.get('departureTimeEstimated', event.get('departureTimePlanned'))
                dpt_utc = dt.datetime.strptime(dpt, '%Y-%m-%dT%H:%M:%SZ')
                transport = event.get('transportation')
                diff = round((dpt_utc.replace(tzinfo=utc_tz) - dt.datetime.now(pytz.utc)).total_seconds()/60)
                bisect.insort(self.departures[transport['number']], diff)
        else:
            print(f'Error querying the API!!')

    def query(self):
        self.query_departures()

        print(f'Stop: {self.stopid} - {self.stop_name}')
        for k, v in self.departures.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    #Argparse
    parser = argparse.ArgumentParser(description='Query the nsw open data API to get departure timings for a stop')

    parser.add_argument('--stop', '-s', help='Stop ID. (default:200064)', default='200064')
    args=parser.parse_args()

    q = QueryNswDepartures(args.stop)

    q.query()
