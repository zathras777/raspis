import os

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('dashboard.views',
    url(r'^$', 'home', name='admin_home'),
    
    url(r'^settings/$', 'settings', name='admin_settings'),
    url(r'^settings/(?P<grp_name>[a-z]+)/$', 'settings', name='settings_grp'),

    url(r'^categories/$', 'categories'),
    url(r'^categories/new/$', 'category_edit'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/$', 'category_edit', name='category_edit'),
    url(r'^categories/remove/(?P<slug>[a-z_]+)/$', 'category_remove'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/add/$', 'category_photo_add'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/remove/$', 'category_photo_remove'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/get/$', 'category_photo_get'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/set/$', 'category_photo_set'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/flip/$', 'category_photo_flip'),
    url(r'^categories/ajax/$', 'category_ajax', name='category_ajax'),

    url(r'^pages/$', 'pages'),
    url(r'^pages/new/$', 'page_edit'),
    url(r'^pages/edit/(?P<slug>[a-z_]+)/$', 'page_edit'),
    url(r'^pages/remove/(?P<slug>[a-z_]+)/$', 'page_remove'),
    
    url(r'^pictures/$', 'photos'),
    url(r'^picture/edit/(?P<pid>\d+)/$', 'photo_edit', name='photo_edit'),
    url(r'^pictures/ajax/$', 'picture_ajax', name='picture_ajax'),
    url(r'^picture/thumbs/(?P<pid>\d+)/$', 'photo_thumbs', name='photo_thumbs'),
    url(r'^picture/thumbs/(?P<pid>\d+)/generate/$', 'photo_thumbs_generate', 
        name='photo_thumbs_generate'),

    url(r'^sizes/$', 'sizes'),
    url(r'^sizes/new/$', 'size_edit'),
    url(r'^sizes/edit/(?P<sid>\d+)/$', 'size_edit'),

    url(r'^users/$', 'users'),
    url(r'^users/new/$', 'user_edit'),
    url(r'^users/edit/(?P<uid>\d+)/$', 'user_edit'),
    url(r'^users/pw/(?P<uid>\d+)/$', 'user_pw'),

    url(r'^upload/$', 'upload'),
    url(r'^views/$', 'views'),
    url(r'^daily/$', 'daily'),
    url(r'^actions/$', 'actions'),
    url(r'^actions/thumbnails/$', 'regenerate_thumbnails'),
)

