# -*- coding: utf-8 -*-

TEST_FAIL = 0
TEST_SUCCESS = 1
FAILURE = 2
FIX = 3
TRANSITION_CHOICES = (
    (TEST_FAIL, 'Test failed'),
    (TEST_SUCCESS, 'Test succeeded'),
    (FAILURE, 'Have a failure'),
    (FIX, 'Fixed'),
)
