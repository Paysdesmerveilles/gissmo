# -*- coding: utf-8 -*-

BUY = 0
GET = 1
SEND = 2
TEST = 3
FIX = 4
DISCARD = 5
DECOMMISSION = 6
RUN = 7
REMOVE = 8
MAINTAIN = 9
CORRECT = 10
FAIL = 11
TURN_UP = 12
DISAPPEAR = 13

TRANSITION_CHOICES = (
    (BUY, 'Buy'),
    (GET, 'Get'),
    (SEND, 'Send'),
    (TEST, 'Test'),
    (FIX, 'Fix'),
    (DISCARD, 'Discard'),
    (DECOMMISSION, 'Decommission'),
    (RUN, 'Run'),
    (REMOVE, 'Remove'),
    (MAINTAIN, 'Maintain'),
    (CORRECT, 'Correct'),
    (FAIL, 'Fail'),
    (TURN_UP, 'Turn up'),
    (DISAPPEAR, 'Disappear'),
)
