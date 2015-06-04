from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from photo.models import Photo
from config.context import SiteSettings

site = SiteSettings()


class photoFeed(Feed):
    title = site['site_name']
    description = site['seo_description']
    link = "/"

    def link(self):
        return "http://%s/" % site['site_url']

    def items(self):
        print("items")
        return Photo.objects.all().order_by('-date_added')[:15]

    def item_title(self, item):
        if len(item.title):
            return item.title
        return "Untitled"

    def item_description(self, item):
        img = item.get_thumbnail('Medium')
        return '''<p>%s</p><p><img src="%s" width="%d" height="%d"/></p>''' % \
                   (item.title, img.img.url, img.img.width, img.img.height)

    def item_link(self, item):
        return "http://%s/pic/%d/" % (site['site_url'], item.id)

    copyright = site['site_copyright']


class photoAtomFeed(photoFeed):
    feed_type = Atom1Feed
