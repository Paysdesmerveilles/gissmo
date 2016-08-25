from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models


fs = FileSystemStorage(location=settings.MEDIA_ROOT)


class Type(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return '%s' % self.name


class Document(models.Model):
    _type = models.ForeignKey('document.Type', verbose_name='Type')
    owner = models.ForeignKey('auth.User')
    title = models.CharField(max_length=40)
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Registration date')
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name='Private link')
    start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Starting date')
    end = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ending date')
    _file = models.FileField(
        blank=True,
        storage=fs,
        verbose_name='File',
        upload_to='document/%Y/%m/%d/')

    def __str__(self):
        return '%s' % self.title
