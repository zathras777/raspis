import os

from django.db import models
from django import forms
from django.dispatch import Signal

config_updated = Signal(providing_args=["group"])

YESNO = ((True, 'Yes'),(False, 'No'))
TYP_CHOICES = ((1, 'Character'),(2, 'Number'), (3,'Boolean'))

class ConfigGroup(models.Model):
    name = models.CharField('Setting group name', max_length = 50)
    desc = models.CharField('Description', max_length = 100)
    
    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return "Config Group %s" % self.name

    def get(self, key):
        for ci in self.configitem_set.all():
            if ci.key.lower() == key:
                return ci.value or ci.dflt
        return ''

    def set(self, key, val):
        for ci in self.configitem_set.all():
            if ci.key.lower() == key:
                ci.value = val
                ci.save()
                return
                
    def settings(self):
        rv = {}
        for ci in self.configitem_set.all():
            rv[ci.key.lower()] = ci.value or ci.dflt
        return rv
        
class ConfigItem(models.Model):
    group = models.ForeignKey(ConfigGroup)
    key = models.CharField('Key', max_length = 50)
    value = models.CharField('Current Value', max_length = 200, blank = True)
    dflt = models.CharField('Default Value', max_length = 200, blank = True)
    rqd = models.BooleanField('Required?', default = False)
    desc = models.CharField('Description', max_length = 100)
    typ = models.PositiveIntegerField('Type of value', choices = TYP_CHOICES)
    
    class Meta:
        ordering = ['group__name', 'key']
        
    def __unicode__(self):
        return u'%s : %s' % (self.group, self.key)

    def settings_value(self):
        ''' Return the required value for use by SiteSettings '''
        val = self.value or self.dflt
        if self.typ == 3: return True if val.lower() == 'true' else False
        elif self.typ == 2: return int(val)
        return val
        
    def get_field_for_type(self):
        if self.typ == 1: return forms.CharField()
        elif self.typ == 2: return forms.IntegerField()
        elif self.typ == 3: return forms.BooleanField()
        
    def make_field(self):
        fld = self.get_field_for_type()
        if self.dflt or self.value:
            fld.initial = self.value or self.dflt 
        fld.required = self.rqd
        fld.help_text = self.desc
        return fld

def insert_required(verbosity = 1):
    if verbosity > 0:
        print "Adding config settings..."

    groups = [ ('site', 'General site settings'), 
               ('seo', 'Settings related to SEO'),
               ('twitter', 'Twitter settings'), 
               ('options', 'Site options') ]
    grps = {}
    rqd_settings = [
        ['site', 'url', '', True, 'URL of site'],
        ['site', 'name', 'UnNamed Site', True, 'Name of Site'],
        ['site', 'copyright', '&copy; 2012', False, 'Copyright statement'],
        ['site', 'author', 'Unknown Author', True, 
         'Authors name to display on site'],
        ['seo', 'description', 'A photo site', False,
         'Description of site (max 160 chars)'],
        ['seo', 'keywords', 'photo,category', False, 'Keywords for the site'],
        ['seo', 'google_analytic', '', False, 'Google analytics code', 1],
        ['options', 'twitter', True, False, 'Enable twitter buttons', 3],
        ['twitter', 'username', '', False, 'Twitter Username'],
        ['twitter', 'CONSUMER_KEY', '', False, 'Twitter API consumer key'],
        ['twitter', 'CONSUMER_SECRET', '', False, 'Twitter API consumer secret'],
        ['twitter', 'ACCESS_KEY', '', False, 'Twitter API access key'],
        ['twitter', 'ACCESS_SECRET', '', False, 'Twitter API access secret'],

    ]
    for g in groups:
        gg, ctd = ConfigGroup.objects.get_or_create(name = g[0])
        if ctd:
            gg.desc = g[1]
            gg.save()
        grps[g[0]] = gg
        
    for r in rqd_settings:
        try:
            ck = ConfigItem.objects.get(group = grps[r[0]], key=r[1])
        except ConfigItem.DoesNotExist:
            if verbosity > 1:
                print "Inserting config item '%s' for group '%s'" % (r[1], r[0])
            if len(r) == 5:
                r.append(1)
            ci = ConfigItem(group = grps[r[0]], key=r[1], dflt=r[2],rqd = r[3],
                            desc = r[4], typ=r[5])
            ci.save()


