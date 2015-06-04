# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configitem',
            name='typ',
            field=models.PositiveIntegerField(choices=[(1, b'Character'), (2, b'Number'), (3, b'Boolean')], default=1, verbose_name=b'Type of value'),
        ),
    ]
