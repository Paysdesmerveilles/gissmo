#!/usr/bin/env python3

import requests

# Configuration
server = 'localhost:8002'
username = 'olivier'
password = 'olivier'

service_url = 'http://%s/api/' % (server)
auth_url = 'http://%s/api-auth/login/' % (server)

print("### Display all sites: ###")
url = service_url + 'site/?format=json'

# Fetch URL
request = requests.get(url, auth=(username, password))
if request.status_code != 200:
    request.raise_for_status()
# Use JSON result
js = request.json()
# Parse sites
for site in js:
    name = site.get('name', '')
    code = site.get('code', '')
    _type = site.get('type', 'Unknown')
    print('%s: %s. (%s)' % (code, name, _type))
