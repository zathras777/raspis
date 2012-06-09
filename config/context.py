from models import ConfigGroup, ConfigItem, config_updated
from forms import config_updated

''' Global variable to cache an instance of the SiteSettings object. '''
siteObj = None

class SiteSettings(object):  
    ''' The SiteSettings class is a wrapper around the various configuration
        groups that have been created. 
    '''

    def __init__(self):
        self.settings = {}
        for g in ConfigGroup.objects.all():
            self.update_group(g)

    def update_group(self, grp):
        for ci in grp.configitem_set.all():
            self.settings["%s_%s" % (grp.name, ci.key.lower())] = ci.settings_value()

    def __getitem__(self, key):
        return self.settings.get(key, '')
        
def site_settings(request):
    ''' This is used to append the settings from the global SiteSettings
        object to this request. If the global object has not been created,
        it is created.
    '''
    global siteObj
    if siteObj is None:
        siteObj = SiteSettings()
    return siteObj.settings

def config_update_handler(sender, **kwargs):
    group = kwargs.get('group', None)
    global siteObj
    if siteObj:
        siteObj.update_group(group)

config_updated.connect(config_update_handler)

