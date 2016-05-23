# -*- coding: utf-8 -*-

# agency types
OBSERVATORY = 0
NETWORK = 1
BUSINESS = 2
CUSTOMER_SERVICE = 3
UNKNOWN = 4
TYPE_CHOICES = (
    (OBSERVATORY, 'Observatory/Laboratory'),
    (NETWORK, 'Network'),
    (BUSINESS, 'Business'),
    (CUSTOMER_SERVICE, 'Customer service Company'),
    (UNKNOWN, 'Unknown'),
)
