from django.db import models


class Player(models.Model):
    # player types
    OBSERVATORY = 1
    ENGINEER = 2
    ORGANIZATION = 3
    COMPANY = 4
    SERVICE_COMPANY = 5
    UNKNOWN = 6
    OTHER = 7
    PLAYER_TYPE_CHOICES = (
        (OBSERVATORY, 'Observatory/Laboratory'),
        (ENGINEER, 'Engineer/Technician'),
        (ORGANIZATION, 'Network'),
        (COMPANY, 'Company'),
        (SERVICE_COMPANY, 'Customer service Company'),
        (UNKNOWN, 'Unknown'),
        (OTHER, 'Other'),
    )

    # fields
    user = models.OneToOneField('auth.User')
    _type = models.IntegerField(
        choices=PLAYER_TYPE_CHOICES,
        default=OTHER,
        verbose_name="type")

    def __str__(self):
        return self.user.username
