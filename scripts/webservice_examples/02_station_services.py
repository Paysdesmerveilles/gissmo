#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

server = 'localhost'
port = '8000'

if port:
    server = ':'.join([server, port])

service_url = 'http://%s/api/v1/' % (server)

# Exact URL to parse sites.
site_url = service_url + 'sites/?format=json'
equipment_url = service_url + 'equipments/?format=json'
service_url = service_url + 'services/?format=json'


def fetch_data(url):
    request = requests.get(url)
    return request.json()


def main():
    sites = fetch_data(site_url)
    for site in sites:
        code = site.get('code', '')
        print(code)
        # fetch linked equipment
        equipments = fetch_data(equipment_url + '&station=%s' % code)
        for equipment in equipments:
            name = equipment.get('name', '')
            equip_id = equipment.get('id', '')
            print('\t%s' % name)
            services = fetch_data(service_url + '&equipment=%s' % equip_id)
            for service in services:
                s_protocol = service.get('protocol', '')
                s_port = service.get('port', '')
                s_ip = service.get('ip', '')
                print('\t\t%s | %s | %s' % (s_protocol, s_port, s_ip))


if __name__ == '__main__':
    main()
