# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-03-01 12:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170228_1627'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loggerhistory',
            name='action_id',
        ),
        migrations.RemoveField(
            model_name='loggerhistory',
            name='geometry',
        ),
    ]
