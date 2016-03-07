from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=50)
    manager = models.ForeignKey('user.Player')
    sites = models.ManyToMany('place.Site', blank=True)
    users = models.ManyToMany('user.GissmoUser', blank=True)
