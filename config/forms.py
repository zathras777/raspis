from django import forms
from django.dispatch import Signal

''' When an instance of ConfigForm is saved, this signal is emitted.
    The siteSettings class (in context.py) catches the signal and updates
    the settings for the group that was affected.
'''
config_updated = Signal(providing_args=["group"])

from models import ConfigGroup, ConfigItem

class ConfigForm(object):
    def __init__(self, grp = 'settings', data = {}):
        self.group = ConfigGroup.objects.get(name = grp)
        self.settings = ConfigItem.objects.filter(group = self.group)
        self.form = None
        if len(self.settings):
            self._make_form()
        self.data = data
        if self.form and len(self.data):
            self.form.data = data
            self.form.is_bound = True
            self.form.full_clean()

    def __getattr__(self, name):
        if self.form and hasattr(self.form, name):
            return getattr(self.form, name)
        return None

    def _make_form(self):
        self.form = forms.Form()
        for s in self.settings:
            self.form.fields[s.key] = s.make_field()        

    def is_valid(self):
        if not self.form:
            return False
        return self.form.is_valid()
    
    def save(self):
        if not self.form or len(self.data) == 0:
            return False
        for s in self.settings:
            s.value = self.form.cleaned_data[s.key]
            s.save()
        config_updated.send(sender=None, group=self.group)
        return True

