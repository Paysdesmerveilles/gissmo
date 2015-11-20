#!/usr/bin/env python3

import requests

# Configuration
server = 'localhost:8002'
username = 'olivier'
password = 'olivier'

service_url = 'http://%s/api/' % (server)
auth_url = 'http://%s/api-auth/login/' % (server)

print("### Display all sites: ###")
url = service_url + 'sites/?format=json'


# Functions
def fetch_data(url):
    # Fetch URL
    request = requests.get(url, auth=(username, password))
    if request.status_code != 200:
        request.raise_for_status()
    # Use JSON result
    js = request.json()
    next_page = js.get('next', None)
    return js, next_page

# As API activates pagination, we need to fetch more than 1 URL
js, next_page = fetch_data(url)
while next_page:
    result = js.get('results', [])
    # Parse sites
    for site in result:
        name = site.get('name', '')
        code = site.get('code', '')
        _type = site.get('type', 'Unknown')
        print('%s: %s. (%s)' % (code, name, _type))
    js, next_page = fetch_data(next_page)
