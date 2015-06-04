from django.db import models
from photo.models import Thumbnail, Photo
from raspis.constants import YESNO


class Category(models.Model):
    name = models.CharField('Name', max_length=30)
    slug = models.SlugField(editable=False)
    desc = models.CharField('Description', max_length=250, blank=True)
    visible = models.BooleanField('Is this category visible?', default=True, choices=YESNO)

    image = models.ForeignKey(Thumbnail, null=True, blank=True, editable=False)

    photos = models.ManyToManyField(Photo)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __unicode__(self): return u'%s' % self.name

    def save(self, *args, **kwargs):
        if self.image is None and self.photo_set.count():
            self.image = self.photo_set.all()[0].get_thumbnail('Category')
        super(Category, self).save(*args, **kwargs)

    @property
    def photo(self):
        if self.image is None:
            return None
        return self.image.photo

    def set_image(self, photo = None):
        if self.photos.count() == 0:
            self.image = None
            self.save()
            return

        if photo is None and self.image is None:
            photo = self.photos.all()[0]
        if photo:
            self.image = photo.get_thumbnail('Category')
            self.save()

    def add_photo(self, photo):
        self.photos.add(photo)
        self.set_image()

    def remove_photo(self, photo):
        if self.image and self.image.photo == photo:
            self.image = None
            self.save()
        self.photos.remove(photo)
        self.set_image()

    def save(self, *args, **kwargs):
        self.slug = self.name.lower().replace(' ', '_')
        super(Category, self).save(*args, **kwargs)

    def as_dict(self):
        d = {'name': self.name, 'slug': self.slug, 'desc': self.desc}
        if self.image and self.image.img:
            d['image'] = {'url': self.image.img.url,
                          'width': self.image.img.width,
                          'height': self.image.img.height}
        return d

    def flip_image(self):
        if self.image:
            self.image.flip()
            self.image.photo.get_thumbnail('Small').flip()

    def record_view(self):
        c, ctd = CategoryCounter.objects.get_or_create(category = self)
        c.views += 1
        c.save()

class Page(models.Model):
    title = models.CharField(max_length = 50)
    slug = models.SlugField(editable = False)
    url = models.URLField('External Link',max_length = 300, blank = True)
    content = models.TextField(blank = True)
    first_dt = models.DateField("First date to be displayed", null = True, blank = True)
    last_dt = models.DateField("Last date to be displayed", null = True, blank = True)

    def __unicode__(self):
        return u'Page: %s' % self.title

    def save(self, *args, **kwargs):
        self.slug = self.title.lower().replace(' ', '_')
        super(Page, self).save(*args, **kwargs)

class PhotoCounter(models.Model):
    photo = models.ForeignKey(Photo)
    views = models.PositiveIntegerField(default = 0)

    def __unicode__(self):
        return "%d views of %s" % (self.views, self.photo.title)

class CategoryCounter(models.Model):
    category = models.ForeignKey(Category)
    views = models.PositiveIntegerField(default = 0)

    def __unicode__(self):
        return "%d views of %s" % (self.views, self.category.name)

class DailyPhoto(models.Model):
    dt = models.DateField(unique=True)
    photo = models.ForeignKey(Photo)

    class Meta:
        ordering = ['-dt']

    def __unicode__(self):
        return "Daily photo for %s : %s" % (self.dt.strftime("%d %b %Y"), self.photo.title)

