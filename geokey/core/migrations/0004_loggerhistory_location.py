# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-03-01 21:59
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170301_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='loggerhistory',
            name='location',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True),
        ),
    ]