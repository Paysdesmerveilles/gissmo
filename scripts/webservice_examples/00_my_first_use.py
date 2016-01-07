#!/usr/bin/env python3

import requests

# Configuration
server = 'localhost'
port = '8000'
if port:
    server = ':'.join([server, port])

service_url = 'http://%s/api/v1/' % (server)
pagination = False  # If True, fetch info regarding pagination axis

print("### Display all sites: ###")
url = service_url + 'sites/?format=json'


# Functions
def fetch_data(url):
    next_page = None
    # Fetch URL
    request = requests.get(url)
    if request.status_code != 200:
        request.raise_for_status()
    # Use JSON result
    js = request.json()
    if pagination:
        next_page = js.get('next', None)
    return js, next_page


def list_stations(data):
    """
    Display each station in given data.
    """
    for site in data:
        name = site.get('name', '')
        code = site.get('code', '')
        _type = site.get('type', 'Unknown')
        print('%s: %s. (%s)' % (code, name, _type))


def main():
    if pagination:
        # As API activates pagination, we need to fetch more than 1 URL
        js, next_page = fetch_data(url)
        while next_page:
            result = js.get('results', [])
            # Parse sites
            list_stations(result)
            js, next_page = fetch_data(next_page)
    else:
        js, next_page = fetch_data(url)
        list_stations(js)


if __name__ == '__main__':
    main()
