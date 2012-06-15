import os

# Try and import from newer django installs, but fallback gracefully
try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from raspis.feeds import photoFeed, photoAtomFeed

urlpatterns = patterns('',
    url(r'^$', 'raspis.views.home', name='home'),

    url(r'^today/$', 'raspis.views.today'),

    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name="login"),    
    url(r'^login/redirect/$', 'raspis.views.login_redirect', name="login_redirect"),    
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),

    url(r'^feed/rss/$', photoFeed(), name='rss'),
    url(r'^feed/atom/$', photoAtomFeed(), name='atom'),
    
    url(r'^ajax/categories/$', 'raspis.views.ajax_categories'),
    
    url(r'^c/(?P<slug>[a-z_]+)/$', 'raspis.views.category', name='category'),
    url(r'^c/(?P<slug>[a-z_]+)/gallery/$', 'raspis.views.category_gallery'),
    url(r'^c/(?P<slug>[a-z_]+)/slideshow/$', 'raspis.views.category_slideshow', name='category_slideshow'),

    url(r'^p/(?P<slug>[a-z_]+)/$', 'raspis.views.page', name='page'),

    url(r'^original/(?P<pid>\d+)/$', 'raspis.views.original', name='original'),
    url(r'^pic/(?P<pid>\d+)/$', 'raspis.views.show', name='show'),

)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT})
    )

