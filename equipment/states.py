# -*- coding: utf-8 -*-

UNKNOWN = 0
NEW = 1
TEST = 2
AVAILABLE = 3
USED = 4
FAILURE = 5
BROKEN = 6
WASTE = 7
TRANSIT = 8
SPARE = 9
LOST = 10

STATE_CHOICES = (
    (UNKNOWN, 'Unknown'),
    (NEW, 'New'),
    (TEST, 'To be test'),
    (AVAILABLE, 'Available'),
    (USED, 'Running'),
    (FAILURE, 'Failure'),
    (BROKEN, 'Broken'),
    (WASTE, 'Waste'),
    (TRANSIT, 'In transit'),
    (SPARE, 'Spare part'),
    (LOST, 'Lost'),
)

NEXT_STATES = {
    UNKNOWN: [
        LOST,
        NEW],
    NEW: [
        LOST,
        TEST],
    TEST: [
        LOST,
        WASTE,
        BROKEN,
        SPARE,
        TRANSIT,
        AVAILABLE],
    AVAILABLE: [
        LOST,
        TRANSIT,
        USED],
    USED: [
        LOST,
        TEST,
        USED,
        FAILURE],
    FAILURE: [
        LOST,
        TEST,
        FAILURE,
        USED],
    BROKEN: [
        LOST,
        WASTE,
        SPARE,
        TRANSIT,
        TEST],
    WASTE: [
        LOST],
    TRANSIT: [
        LOST,
        TEST],
    SPARE: [
        LOST],
    LOST: [
        TEST],
}
