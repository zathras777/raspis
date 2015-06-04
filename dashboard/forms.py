from django.contrib.auth.models import User

from photo.models import *
from raspis.models import *
from config.models import *
from utils.photos import photo_category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['photos']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['desc'].widget.attrs['size']='50'


class pageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = []


class photoForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      empty_label = 'No category',
                                      required = False)

    class Meta:
        model = Photo
        fields = ['image','title']

    def __init__(self, *args, **kwargs):
        super(photoForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['size']='50'
        if kwargs.get('instance', None):
            self.fields['category'].initial = photo_category(kwargs['instance'])


class editPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image','title']


class szForm(forms.ModelForm):
    class Meta:
        model = ThumbnailSize
        exclude = []


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login','password','groups', 'user_permissions','date_joined']


class UserPwForm(forms.Form):
    pw1 = forms.CharField(widget=forms.PasswordInput(),
                          max_length=20, label="New Password")
    pw2 = forms.CharField(widget=forms.PasswordInput(),
                          max_length=20, label="New Password (again)")

