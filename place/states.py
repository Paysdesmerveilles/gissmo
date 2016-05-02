# -*- coding: utf-8 -*-

AVAILABLE = 0
TESTING = 1
READY = 2
RUNNING = 3
FAILURE = 4
CLOSED = 5

STATE_CHOICES = (
    (AVAILABLE, 'Available'),
    (TESTING, 'Testing'),
    (READY, 'Ready'),
    (RUNNING, 'Running'),
    (FAILURE, 'Failure'),
    (CLOSED, 'Closed'),
)

NEXT_STATES = {
    AVAILABLE: [
        TESTING,
        READY,
        CLOSED],
    TESTING: [
        AVAILABLE,
        CLOSED],
    READY: [
        AVAILABLE,
        RUNNING,
        CLOSED],
    RUNNING: [
        READY,
        FAILURE,
        CLOSED],
    FAILURE: [
        RUNNING,
        FAILURE,
        CLOSED],
    CLOSED: [],
}
