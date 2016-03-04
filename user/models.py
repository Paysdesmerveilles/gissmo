from django.db import models
from django.contrib.auth.models import User


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
#    user = models.ManyToOneField('auth.User')
    name = models.CharField(max_length=50)
    _type = models.IntegerField(
        choices=PLAYER_TYPE_CHOICES,
        default=OTHER,
        verbose_name="type")

    def __str__(self):
        return self.name


class GissmoUser(User):
    """
    All users needs to be added in Player list.
    This object add a mandatory link between User and Player.
    """
    player = models.ForeignKey('user.Player')


class Project(models.Model):
    users = models.ManyToManyField('auth.User')
