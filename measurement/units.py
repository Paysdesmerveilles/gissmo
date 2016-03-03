# GPS purposes
DEGREES = 0
METERS = 1
SECONDS_PER_SAMPLE = 2
SAMPLES_PER_SECOND = 3

POSITION_UNIT_CHOICES = (
    (DEGREES, "Degrees"),
    (METERS, "Meters"),
)

# all units
UNIT_CHOICES = (
    (DEGREES, 'Degrees'),
    (METERS, 'Meters'),
    (SECONDS_PER_SAMPLE, 'Secondes/sample'),
    (SAMPLES_PER_SECOND, 'Samples/S'),
)

# channel calibration
METER = 0
METER_PER_SECOND = 1
METER_PER_SECOND2 = 2
CALIBRATION_CHOICES = (
    (METER, 'Displacement in meters'),
    (METER_PER_SECOND, 'Velocity in meters per second'),
    (METER_PER_SECOND2, 'Acceleration in meters per second squared'),
)
