#!/usr/bin/env python3

import requests

# Configuration
server = 'localhost:8002'
username = 'olivier'
password = 'olivier'

service_url = 'http://%s/api/' % (server)
auth_url = 'http://%s/api-auth/login/' % (server)

url = service_url + 'station/?format=json'

# Fetch URL
request = requests.get(url, auth=(username, password))
if request.status_code != 200:
    request.raise_for_status()
# Use JSON result
js = request.json()
# Parse stations
for station in js:
    name = station.get('name', '')
    code = station.get('code', '')
    _type = station.get('type', 'Unknown')
    print('%s: %s. (%s)' % (code, name, _type))
