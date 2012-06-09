from photo.models import *
from raspis.models import PhotoCounter

def photo_category(photo):
    ''' Return the category that a photo belongs to, or None '''
    if photo.category_set.count() == 0:
        return None
    return photo.category_set.all()[0]

def photo_category_set(photo, cat):
    ''' Put the photo in the category specified, or remove from current
        category if cat is None.
    '''
    current = photo_category(photo)
    if current is not None and cat != current:
        current.remove_photo(photo)
        if cat is None:
            return
    cat.add_photo(photo)

def record_photo_view(photo):
    c, ctd = PhotoCounter.objects.get_or_create(photo = photo)
    c.views += 1
    c.save()

