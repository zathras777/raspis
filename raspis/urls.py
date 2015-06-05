try:
    from django.conf.urls import include, url
except ImportError:
    from django.conf.urls.defaults import include, urls

from django.contrib import admin
from django.conf import settings
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static

from raspis import feeds, views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^today/$', views.today),

    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, name="login"),
    url(r'^login/redirect/$', views.login_redirect, name="login_redirect"),
    url(r'^logout/$', logout, name="logout"),

    url(r'^feed/rss/$', feeds.photoFeed(), name='rss'),
    url(r'^feed/atom/$', feeds.photoAtomFeed(), name='atom'),

    url(r'^ajax/categories/$', views.ajax_categories),

    url(r'^c/(?P<slug>[a-z_]+)/$', views.category, name='category'),
    url(r'^c/(?P<slug>[a-z_]+)/gallery/$', views.category_gallery),
    url(r'^c/(?P<slug>[a-z_]+)/slideshow/$', views.category_slideshow, name='category_slideshow'),

    url(r'^p/(?P<slug>[a-z_]+)/$', views.page, name='page'),

    url(r'^original/(?P<pid>\d+)/$', views.original, name='original'),
    url(r'^pic/(?P<pid>\d+)/$', views.show, name='show'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)