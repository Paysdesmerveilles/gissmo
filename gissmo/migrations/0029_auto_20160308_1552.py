# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0028_auto_20160308_1004'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='intervdoc',
            options={'verbose_name': 'Document (interv.)', 'verbose_name_plural': 'Documents (interv.)'},
        ),
    ]
