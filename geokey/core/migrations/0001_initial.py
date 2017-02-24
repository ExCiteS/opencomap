# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoggerHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('project_id', models.IntegerField(null=True)),
                ('category_id', models.IntegerField(null=True)),
                ('user_id', models.IntegerField(null=True)),
                ('usergroup_id', models.IntegerField(null=True)),
                ('subset_id', models.IntegerField(null=True)),
                ('location_id', models.IntegerField(null=True)),
                ('observation_id', models.IntegerField(null=True)),
                ('comment_id', models.IntegerField(null=True)),
                ('action', models.CharField(max_length=300)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, geography=True)),
                ('action_id', models.CharField(default=b'created', max_length=20, choices=[(b'created', b'created'), (b'deleted', b'deleted'), (b'updated', b'updated')])),
                ('historical', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
            ],
        ),
    ]