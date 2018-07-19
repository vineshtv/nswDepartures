# nswDepartures
A simple python program which queries the NSW open data API and returns all the departures from a particular stop

API Queried: https://api.transport.nsw.gov.au/v1/tp/departure_mon/

Usage - 

python nswDepartures.py <stopid>

where stopid is the id number of any stop.
For eg - 
The stop id of the bustop at central opposite to the Tafe building is - 200064
The stop id for platform 16 at central is - 2000336

The script returns a list of routes and its realtime departures in minutes.

Note: The script sources an environment variable which is the API key to query the NSW API.
