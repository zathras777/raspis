from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from dashboard.forms import CategoryForm, photoForm, szForm, UserForm, UserPwForm, pageForm

from utils.staff import staff_required
from raspis.models import *
from config.models import *
from config.forms import ConfigForm
from config.context import SiteSettings
from utils.json_encoding import JSONResponse
from utils.photos import *

@staff_required
def home(request):
    where = 'home'
    pics = Photo.objects.count()
    cats = Category.objects.count()
    return render(request, 'dashboard/index.html', locals())

@staff_required
def settings(request, grp_name = 'site'):
    where = 'settings'
    if request.method == 'POST':
        form = ConfigForm(grp_name, request.POST)
        if form.is_valid():
            form.save()
#        else:
    else:
        form = ConfigForm(grp_name)
    grp = ConfigGroup.objects.get(name = grp_name)
    grps = ConfigGroup.objects.all().order_by('name')
    ss = SiteSettings()
    current = ss.settings
    return render(request, 'dashboard/settings.html', locals())

@staff_required
def categories(request):
    cats = Category.objects.all()
    where = 'categories'
    return render(request, 'dashboard/categories.html', locals())

@staff_required
def category_edit(request, slug=None):
    cat = None
    if slug is not None:
        cat = get_object_or_404(Category, slug = slug)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance = cat)
        if form.is_valid():
            form.save()
            messages.info(request, "Category updated")
            return HttpResponseRedirect(reverse('dashboard_categories'))
    else:
        form = CategoryForm(instance = cat)

    if slug is not None:
        pics = cat.photos.all()
        avail = Photo.objects.exclude(id__in = [p.id for p in pics])

    return render(request, 'dashboard/category_edit.html', locals())

@staff_required
def category_remove(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    name = cat.name
    cat.delete()
    messages.info(request, "Removed category %s" % name)
    return HttpResponseRedirect(reverse('dashboard_categories'))

@csrf_exempt
@staff_required
def category_photo_add(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    if not request.method == 'POST' or not request.POST.has_key('id'):
        raise Http404
    pic = get_object_or_404(Photo, pk = request.POST['id'])
    cat.add_photo(pic)
    return HttpResponse('OK')

@staff_required
def category_photo_get(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    rv = {}
    if cat.image is not None:
        t = cat.image.photo.get_thumbnail('Small')
        if t:
            rv['url'] = t.img.url
            rv['width'] = t.img.width
            rv['height'] = t.img.height

    return JSONResponse(rv)

@csrf_exempt
@staff_required
def category_photo_set(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    if not request.method == 'POST' or not request.POST.has_key('id'):
        raise Http404
    pic = get_object_or_404(Photo, pk=request.POST['id'])
    if not pic in cat.photos.all():
        cat.add_photo(pic)
    t = pic.get_thumbnail('Category')
    if t:
        cat.image = t
        cat.save()
    return HttpResponse('OK')

@staff_required
def category_photo_flip(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    cat.flip_image()
    return HttpResponse('OK')

@csrf_exempt
@staff_required
def category_photo_remove(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    if not request.method == 'POST' or not request.POST.has_key('id'):
        raise Http404
    photo = get_object_or_404(Photo, pk = request.POST['id'])
    cat.remove_photo(photo)
    return HttpResponse("OK")

@csrf_exempt
@staff_required
def category_ajax(request):
    if not request.method == 'POST':
        raise Http404
    try:
        cat = Category.objects.get(slug=request.POST.get('slug', ''))
    except Category.DoesNotExist:
        cat = None
    action = request.POST.get('action', '')
    photo = get_object_or_404(Photo, pk = request.POST.get('id', 0))
    if action in ['add','move']:
       photo_category_set(photo, cat)
    elif action == 'remove':
        cat.remove_picture(photo)
    return HttpResponse('OK')

@staff_required
def pages(request):
    pages = Page.objects.all()
    where = 'pages'
    return render(request, 'dashboard/pages.html', locals())

@staff_required
def page_edit(request, slug = None):
    page = None
    if slug:
        page = get_object_or_404(Page, slug = slug)
    if request.method == 'POST':
        form = pageForm(request.POST, instance = page)
        if form.is_valid():
            form.save()
            messages.info(request, "Page updated")
            return HttpResponseRedirect(reverse('dashboard_pages'))
    else:
        form = pageForm(instance = page)
    return render(request, 'dashboard/page_edit.html', locals())

@staff_required
def page_remove(request, slug):
    Page.objects.filter(slug = slug).delete()
    messages.info(request, "Page removed")
    return HttpResponseRedirect(reverse('dashboard_pages'))

@staff_required
def photos(request):
    where = 'pictures'
    cats = Category.objects.all()
    uncat = Photo.objects.filter(category__isnull=True)
    return render(request, 'dashboard/photos.html', locals())

@staff_required
def upload(request):
    where = 'upload'
    if request.method == 'POST':
        form = photoForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            msg = "Picture uploaded OK"
            if form.cleaned_data['category'] is not None:
                cat = form.cleaned_data['category']
                cat.add_photo(p)
                msg += " and added to category %s" % cat.name
            messages.info(request, msg)
            return HttpResponseRedirect(".")
    else:
        form = photoForm()
    return render(request, 'dashboard/upload.html', locals())

@staff_required
def photo_edit(request, pid):
    photo = get_object_or_404(Photo, pk = pid)
    if request.method == 'POST':
        form = photoForm(request.POST, request.FILES, instance = photo)
        if form.is_valid():
            p = form.save()
            photo_category_set(p, form.cleaned_data['category'])
            messages.info(request, "Picture details updated")
            return HttpResponseRedirect(reverse('dashboard_photos'))
    else:
        form = photoForm(instance = photo)
    return render(request, 'dashboard/photo_edit.html', locals())

@csrf_exempt
@staff_required
def picture_ajax(request):
    if request.method != 'POST':
        raise Http404
    photo = get_object_or_404(Photo, pk = request.POST.get('id', 0))
    action = request.POST.get('action', '')
    if action == 'remove':
        photo.delete()
    return HttpResponse('OK')

@staff_required
def photo_thumbs(request, pid):
    photo = get_object_or_404(Photo, pk = pid)
    return render(request, 'dashboard/thumbs.html', locals())


@staff_required
def photo_thumbs_generate(request, pid):
    photo = get_object_or_404(Photo, pk = pid)
    photo.make_thumbnails()
    messages.info(request, "Thumbnails regenerated")
    return HttpResponseRedirect(reverse('photo_thumbs', args=[pid]))

@staff_required
def sizes(request):
    sizes = ThumbnailSize.objects.all()
    where = 'sizes'
    return render(request, 'dashboard/sizes.html', locals())

@staff_required
def size_edit(request, sid = None):
    sz = None
    if sid is not None:
        sz = get_object_or_404(ThumbnailSize, pk = sid)
    if request.method == 'POST':
        form = szForm(request.POST, instance = sz)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard_sizes'))
    else:
        form = szForm(instance = sz)
    return render(request, 'dashboard/size_edit.html', locals())

@staff_required
def users(request):
    where = 'users'
    users = User.objects.all()
    return render(request, 'dashboard/users.html', locals())

@staff_required
def user_edit(request, uid = None):
    u = None
    if uid is not None:
        u = get_object_or_404(User, pk = uid)
    if request.method == 'POST':
        form = UserForm(request.POST, instance = u)
        if form.is_valid():
            u = form.save(commit = False)
            if uid is None:
                u.set_unusable_password()
            u.save()
            form.save_m2m()
            messages.info(request, "Update user details for %s" % u.username)
            return HttpResponseRedirect(reverse('dashboard_users'))
    else:
        form = UserForm(instance = u)
    return render(request, 'dashboard/user_edit.html', locals())

@staff_required
def user_pw(request, uid):
    u = get_object_or_404(User, pk = uid)
    if request.method == 'POST':
        form = UserPwForm(request.POST)
        if form.is_valid():
            if not request.POST.has_key('pw1') or not request.POST.has_key('pw2'):
                messages.info(request, "You MUST enter the password twice")
                return HttpResponseRedirect(".")
            if len(request.POST['pw1']) == 0 or len(request.POST['pw2']) == 0:
                messages.info(request, "Blank passwords are not permitted")
                return HttpResponseRedirect(".")
            if request.POST['pw1'] != request.POST['pw2']:
                messages.info(request, "Passwords MUST be the same.")
                return HttpResponseRedirect(".")
            if len(request.POST['pw1']) < 4:
                messages.info(request, "Passwords MUST be more than 4 characters.")
                return HttpResponseRedirect(".")
            u.set_password(request.POST['pw1'])
            u.save()
            messages.info(request, "Password has been set")
            return HttpResponseRedirect(reverse('dashboard_users'))
    else:
        form = UserPwForm()
    return render(request, 'dashboard/user_pw.html', locals())

@staff_required
def views(request):
    where = 'views'
    photos = PhotoCounter.objects.all().order_by('views')
    cats = CategoryCounter.objects.all().order_by('views')
    return render(request, 'dashboard/views.html', locals())

@staff_required
def daily(request):
    from datetime import date
    where = 'daily'
    past = DailyPhoto.objects.filter(dt__lt = date.today())
    present = DailyPhoto.objects.filter(dt = date.today())
    if len(present):
        present = present[0]
    future = DailyPhoto.objects.filter(dt__gt = date.today())
    return render(request, 'dashboard/daily.html', locals())

@staff_required
def actions(request):
    where = 'actions'
    return render(request, 'dashboard/actions.html', locals())

@staff_required
def regenerate_thumbnails(request):
    for p in Photo.objects.all():
        p.make_thumbnails()
    messages.info(request, "Thumbnails have been regenerated.")
    return HttpResponseRedirect(reverse('dashboard_actions'))
