# Try and import from newer django installs, but fallback gracefully
try:
    from django.conf.urls import include, url
except ImportError:
    from django.conf.urls.defaults import include, url

from dashboard import views

urlpatterns = [
    url(r'^$', views.home, name='admin_home'),

    url(r'^settings/$', views.settings, name='admin_settings'),
    url(r'^settings/(?P<grp_name>[a-z]+)/$', views.settings, name='settings_grp'),

    url(r'^categories/$', views.categories, name='dashboard_categories'),
    url(r'^categories/new/$', views.category_edit),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/$', views.category_edit, name='category_edit'),
    url(r'^categories/remove/(?P<slug>[a-z_]+)/$', views.category_remove),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/add/$', views.category_photo_add),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/remove/$', views.category_photo_remove),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/get/$', views.category_photo_get, name='category_photo_get'),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/set/$', views.category_photo_set),
    url(r'^categories/edit/(?P<slug>[a-z_]+)/photo/flip/$', views.category_photo_flip),
    url(r'^categories/ajax/$', views.category_ajax, name='category_ajax'),

    url(r'^pages/$', views.pages, name='dashboard_pages'),
    url(r'^pages/new/$', views.page_edit),
    url(r'^pages/edit/(?P<slug>[a-z_]+)/$', views.page_edit),
    url(r'^pages/remove/(?P<slug>[a-z_]+)/$', views.page_remove),

    url(r'^pictures/$', views.photos, name='dashboard_pictures'),
    url(r'^picture/edit/(?P<pid>\d+)/$', views.photo_edit, name='photo_edit'),
    url(r'^pictures/ajax/$', views.picture_ajax, name='picture_ajax'),
    url(r'^picture/thumbs/(?P<pid>\d+)/$', views.photo_thumbs, name='photo_thumbs'),
    url(r'^picture/thumbs/(?P<pid>\d+)/generate/$', views.photo_thumbs_generate,
        name='photo_thumbs_generate'),

    url(r'^sizes/$', views.sizes, name='dashboard_sizes'),
    url(r'^sizes/new/$', views.size_edit),
    url(r'^sizes/edit/(?P<sid>\d+)/$', views.size_edit),

    url(r'^users/$', views.users, name='dashboard_users'),
    url(r'^users/new/$', views.user_edit),
    url(r'^users/edit/(?P<uid>\d+)/$', views.user_edit),
    url(r'^users/pw/(?P<uid>\d+)/$', views.user_pw),

    url(r'^upload/$', views.upload),
    url(r'^views/$', views.views),
    url(r'^daily/$', views.daily),
    url(r'^actions/$', views.actions, name='dashboard_actions'),
    url(r'^actions/thumbnails/$', views.regenerate_thumbnails),
]
