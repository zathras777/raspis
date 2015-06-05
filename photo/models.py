import os
import hashlib
import math
from os.path import basename, splitext, exists

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from django.db import models
from django.db.models.signals import post_delete, post_save

from raspis.constants import YESNO


# Helper functions

# This is used to get the path to upload an image to. It sets the path based
# on the displayDate field, meaning every photo will be in it's own
# directory.


def photo_path(instance, filename):
    if not instance.displayDate:
        return 'unknown/%s' % filename
    dt = instance.displayDate.strftime("%Y/%m")
    return os.path.join('originals', dt, filename)

# This is used to get the path to upload a thumbnail into. The path is the
# same as that used for the main image, but this function is needed as the
# references are different.
def thumbnailPath(instance, filename):
    if not instance.photo or not instance.photo.img:
        return 'unknown/%s' % filename
    dt = instance.photo.displayDate.strftime("%Y/%m")
    return os.path.join('thumbnails', dt, filename)

class ThumbnailSize(models.Model):
    name = models.CharField(max_length = 30, unique=True)
    width = models.PositiveIntegerField(default = 0)
    height = models.PositiveIntegerField(default = 0, blank = True)
    square = models.BooleanField(default = False, choices = YESNO)
    absolute = models.BooleanField(default = False, choices = YESNO)

    def __unicode__(self): return u'%s' % self.name

    @property
    def filename_name(self):
        return u'%s' % self.name.replace(" ", "_")

    @property
    def crop_required(self):
        if self.square or self.absolute:
            return True
        return False

    @property
    def longest(self):
        if self.square:
            return float(self.width)
        if self.width >= self.height:
            return float(self.width)
        return float(self.height)

    def make_crop(self, img_sz):
        if self.square:
            left = (img_sz[0] - self.width) / 2
            top = (img_sz[1] - self.width) / 2
            w = h = self.width
            return left, top, left + self.width, top + self.width
        if self.absolute:
            left = (img_sz[0] - self.width) / 2
            top = (img_sz[1] - self.height) / 2
            return left, top, left + self.width, top + self.height

class Photo(models.Model):
    title = models.CharField(max_length = 100, blank = True)
    date_added = models.DateTimeField(auto_now_add = True)
    date = models.DateField("Photo Date", editable = False, null = True)
    image = models.ImageField(upload_to = 'originals')
    md5 = models.CharField(max_length = 32, editable = False, blank = True)

#    category = models.ForeignKey('Category', blank = True, null = True)

    def __unicode__(self):
        if len(self.title):
            return u'%s' % self.title
        return self.image.name

    def make_thumbnails(self):
        ''' Generate all required thumbnails. Some additional logic to ensure
            we don't have duplicates.
            NB This removes the current thumbnail image, so any modifications
               made to the thumbnail will be lost.
        '''
        for sz in ThumbnailSize.objects.all():
            ck = self.thumbnail_set.filter(size = sz)
            if len(ck):
                if len(ck) > 1:
                    for t in ck[1:]:
                        t.delete()
                t = ck[0]
            else:
                t = Thumbnail(photo = self, size = sz)
                t.save()
            t.make_thumbnail()

    def get_thumbnail(self, name):
        t = self.thumbnail_set.filter(size__name = name)
        if len(t) == 1:
            return t[0]
        try:
            sz = ThumbnailSize.objects.get(name = name)
        except ThumbnailSize.DoesNotExist:
            return None
        t, ctd = self.thumbnail_set.get_or_create(photo = self, size = sz)
        t.make_thumbnail()
        return t

    @property
    def longest(self):
        if self.image:
            return float(max(self.image.width, self.image.height))
        return 0.0

    @property
    def shortest(self):
        if self.image:
            return float(min(self.image.width, self.image.height))
        return 0.0

    def update_md5(self):
        m = hashlib.md5()
        fH = open(self.image.path, 'rb')
        m.update(fH.read())
        fH.close()
        self.md5 = m.hexdigest()

    def record_view(self):
        c, ctd = PhotoCounter.objects.get_or_create(photo = self)
        c.views += 1
        c.save()

class Thumbnail(models.Model):
    photo = models.ForeignKey(Photo)
    size = models.ForeignKey(ThumbnailSize)
    img = models.ImageField(upload_to='thumbnails', null = True)

    def __unicode__(self):
        return u'%s [%d, %s]' % (self.photo.title, self.id, self.size.name)

    def get_new_size(self, sz):
        # if square, shortest must be at least the required dimension
        if self.size.square:
            ratio = float(self.size.width) / self.photo.shortest
        elif self.size.absolute:
            ratio = max((float(self.size.width) / self.photo.image.width),
                        (float(self.size.height) / self.photo.image.height))
        else:
            ratio = float(self.size.longest) / self.photo.longest
        if ratio > 1.0:
            ratio = 1.0
        w = math.ceil(ratio * sz[0])
        h = math.ceil(ratio * sz[1])
        return int(w), int(h)

    def make_thumbnail(self):
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        if self.img and exists(self.img.path):
            os.remove(self.img.path)

        orig = Image.open(self.photo.image.path)
        fName, ext = splitext(basename(self.photo.image.name))
        thumb_filename = '%s_%s%s' % (self.photo.id, self.size.filename_name, ext)

        new_sz = self.get_new_size(orig.size)
        orig.thumbnail(new_sz, Image.ANTIALIAS)

        if self.size.crop_required:
            cropped = self.size.make_crop(new_sz)
            orig = orig.crop(cropped)

        if ext.lower() in ['.jpeg', '.jpg']:
            DJANGO_TYPE = 'image/jpeg'
            PIL_TYPE = 'jpeg'
        elif ext.lower() in ['.png']:
            DJANGO_TYPE = 'image/png'
            PIL_TYPE = 'png'
        elif ext.lower() == '.gif':
            DJANGO_TYPE = 'image/gif'
            PIL_TYPE = 'gif'

        temp_handle = StringIO()
        orig.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)
        suf = SimpleUploadedFile(thumb_filename, temp_handle.read(),
                                 content_type=DJANGO_TYPE)
        self.img.save(thumb_filename, suf, save=True)
#        self.insert_copyright()

    def flip(self):
        from PIL import Image
        orig = Image.open(self.img.path)
        ni = orig.transpose(Image.FLIP_LEFT_RIGHT)
        ni.save(self.img.path)

"""
pyexiv2 is python 2.x only, so until a replacement can be found - don't do this!
    def insert_copyright(self):
        try:
            metadata = pyexiv2.ImageMetadata(self.img.path)
            metadata.read()
        except IOError:
            return
        try:
            cfg = ConfigItem.objects.get(group='settings', key='site_author')
            name = cfg.value or cfg.dflt
            # todo - copyright? year?
            copy = 'Copyright %s. All rights reserved.' % name
            metadata['Exif.Image.Copyright'] = copy
            metadata['Exif.Image.Artist'] = name
            metadata['Iptc.Application2.Copyright'] = [copy]
            metadata['Iptc.Application2.Byline'] = [name]
            metadata['Xmp.xmpRights.Marked'] = True
            metadata['Xmp.dc.creator'] = [name]
            metadata.write()
        except:
            pass
"""


def insert_required(verbosity):
    if verbosity > 0:
        print("Checking preloaded data...")
    rqd_sizes = { 'Category': [ 600, 400, False, True ],
                  'Small Square': [ 75, 0, True, False ],
                  'Square':   [ 150, 0, True, False ],
                  'Small': [ 150, 0, False, False ],
                  'Medium': [ 300, 0, False, False ],
                  'Large': [ 800, 0, False, False ],
                }
    for r in sorted(rqd_sizes.keys()):
        try:
            ck = ThumbnailSize.objects.get(name = r)
        except ThumbnailSize.DoesNotExist:
            data = rqd_sizes[r]
            if verbosity > 1:
                print("Inserting Thumbnail Size '%s'" % r)
            ts = ThumbnailSize(name=r, width=data[0], height=data[1],
                               square=data[2], absolute=data[3])
            ts.save()

def cleanFiles(sender, **kwargs):
    inst = kwargs.get('instance', None)
    if inst is None:
        return
    for field in sender._meta.get_fields():
        if isinstance(field, models.ImageField):
            f = getattr(inst, field.name)
            if not (f):
                continue
            m = inst.__class__._default_manager
            if os.path.exists(f.path) and not \
                m.filter(**{'%s__exact' % field.name: getattr(inst, field.name)})\
                .exclude(pk=inst._get_pk_val()):
                os.remove(f.path)

def updateThumbnails(sender, **kwargs):
    inst = kwargs.get('instance', None)
    if not inst:
        return

    # update existing thumbnails...
    for t in Thumbnail.objects.filter(size = inst):
        t.make_thumbnail()

    if kwargs.get('created', False):
        # Just created, so add thumbnail size for existing photos
        for p in Photo.objects.all():
            t = Thumbnail(photo=p, size=inst)
            t.make_thumbnail()

def update_photo(sender, **kwargs):
    inst = kwargs.get('instance', None)
    if not inst:
        return
    inst.make_thumbnails()
    # set date here

post_delete.connect(cleanFiles, sender=Photo, dispatch_uid="PhotoRemove")
post_delete.connect(cleanFiles, sender=Thumbnail, dispatch_uid="ThumbnailRemove")
# Check model selector for change of object type
post_save.connect(updateThumbnails, sender=ThumbnailSize, dispatch_uid='updateThumbnails')
post_save.connect(update_photo, sender=Photo, dispatch_uid='make_thumbnails')

