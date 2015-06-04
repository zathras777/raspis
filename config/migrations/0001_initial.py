# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name=b'Setting group name')),
                ('desc', models.CharField(max_length=100, verbose_name=b'Description')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ConfigItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, verbose_name=b'Key')),
                ('value', models.CharField(blank=True, max_length=200, verbose_name=b'Current Value')),
                ('dflt', models.CharField(blank=True, max_length=200, verbose_name=b'Default Value')),
                ('rqd', models.BooleanField(default=False, verbose_name=b'Required?')),
                ('desc', models.CharField(max_length=100, verbose_name=b'Description')),
                ('typ', models.PositiveIntegerField(choices=[(1, b'Character'), (2, b'Number'), (3, b'Boolean')], verbose_name=b'Type of value')),
                ('group', models.ForeignKey(to='config.ConfigGroup')),
            ],
            options={
                'ordering': ['group__name', 'key'],
            },
        ),
    ]
