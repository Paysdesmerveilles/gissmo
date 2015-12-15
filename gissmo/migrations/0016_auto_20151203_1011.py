# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0015_auto_20151202_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentchannel',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='commentchannelauthor',
            name='author',
        ),
        migrations.RemoveField(
            model_name='commentchannelauthor',
            name='comment_channel',
        ),
        migrations.RemoveField(
            model_name='commentnetwork',
            name='network',
        ),
        migrations.RemoveField(
            model_name='commentnetworkauthor',
            name='author',
        ),
        migrations.RemoveField(
            model_name='commentnetworkauthor',
            name='comment_network',
        ),
        migrations.RemoveField(
            model_name='commentstationsite',
            name='station',
        ),
        migrations.RemoveField(
            model_name='commentstationsiteauthor',
            name='author',
        ),
        migrations.RemoveField(
            model_name='commentstationsiteauthor',
            name='comment_station',
        ),
        migrations.DeleteModel(
            name='CommentChannel',
        ),
        migrations.DeleteModel(
            name='CommentChannelAuthor',
        ),
        migrations.DeleteModel(
            name='CommentNetwork',
        ),
        migrations.DeleteModel(
            name='CommentNetworkAuthor',
        ),
        migrations.DeleteModel(
            name='CommentStationSite',
        ),
        migrations.DeleteModel(
            name='CommentStationSiteAuthor',
        ),
    ]
