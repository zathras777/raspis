# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name=b'Name')),
                ('slug', models.SlugField(editable=False)),
                ('desc', models.CharField(blank=True, max_length=250, verbose_name=b'Description')),
                ('visible', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=True, verbose_name=b'Is this category visible?')),
                ('image', models.ForeignKey(blank=True, editable=False, null=True, to='photo.Thumbnail')),
                ('photos', models.ManyToManyField(to='photo.Photo')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('views', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(to='raspis.Category')),
            ],
        ),
        migrations.CreateModel(
            name='DailyPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateField(unique=True)),
                ('photo', models.ForeignKey(to='photo.Photo')),
            ],
            options={
                'ordering': ['-dt'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField(editable=False)),
                ('url', models.URLField(blank=True, max_length=300, verbose_name=b'External Link')),
                ('content', models.TextField(blank=True)),
                ('first_dt', models.DateField(blank=True, null=True, verbose_name=b'First date to be displayed')),
                ('last_dt', models.DateField(blank=True, null=True, verbose_name=b'Last date to be displayed')),
            ],
        ),
        migrations.CreateModel(
            name='PhotoCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('views', models.PositiveIntegerField(default=0)),
                ('photo', models.ForeignKey(to='photo.Photo')),
            ],
        ),
    ]
