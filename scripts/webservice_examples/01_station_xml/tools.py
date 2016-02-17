# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests


def get(url):
    data = []
    request = requests.get(url)
    if request:
        data = request.json()
    return data
