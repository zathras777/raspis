#!/usr/bin/env python

import sys
import datetime
import tweepy

from os.path import abspath, dirname, join, exists
from datetime import date

from django.core.management import setup_environ

fvPath = abspath(join(dirname(abspath(__file__)), '..'))
sys.path.insert(0, fvPath)

def dpForDate(dt):
    try:
        dp = DailyPhoto.objects.get(dt = dt)
    except DailyPhoto.DoesNotExist:
        if DailyPhoto.objects.count():
            used = DailyPhoto.objects.values_list('photo__id')
            avail = Photo.objects.exclude(id__in=used[0]).order_by('?')[0]
        else:
            avail = Photo.objects.order_by('?')[0]
        dp = DailyPhoto(dt = dt, photo = avail)
        dp.save()
    return dp

if __name__ == '__main__':

    import raspis.settings
    setup_environ(raspis.settings)

    from raspis.models import *
    from config.context import SiteSettings
    
    ss = SiteSettings()
    
    dt = date.today()
    dp = dpForDate(dt)
    
    msg = "Photo for %s - %s http://%s/pic/%d/" % (
                       ss['site_url'], dp.dt.strftime("%d %B %Y"), dp.photo.title, dp.photo.id)
  
    try:
        auth = tweepy.OAuthHandler(ss['twitter_consumer_key'], ss['twitter_consumer_secret'])
        auth.set_access_token(ss['twitter_access_key'], ss['twitter_access_secret'])
        api = tweepy.API(auth)
        api.update_status(msg)
    except TypeError:
        pass
        
    dp = dpForDate(dt + timedelta(1))

