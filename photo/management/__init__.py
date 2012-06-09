from django.db.models.signals import post_syncdb

from photo import models as pmodels

def do_install(sender, **kwargs):
    if len(kwargs.get('created_models', [])) == 0:
        return
    pmodels.insert_required(kwargs.get('verbosity', 0))

post_syncdb.connect(do_install, sender=pmodels)

