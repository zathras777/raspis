# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField(editable=False, null=True, verbose_name=b'Photo Date')),
                ('image', models.ImageField(upload_to=b'originals')),
                ('md5', models.CharField(blank=True, editable=False, max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(null=True, upload_to=b'thumbnails')),
                ('photo', models.ForeignKey(to='photo.Photo')),
            ],
        ),
        migrations.CreateModel(
            name='ThumbnailSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('width', models.PositiveIntegerField(default=0)),
                ('height', models.PositiveIntegerField(blank=True, default=0)),
                ('square', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=False)),
                ('absolute', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=False)),
            ],
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='size',
            field=models.ForeignKey(to='photo.ThumbnailSize'),
        ),
    ]
