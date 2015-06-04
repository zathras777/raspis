import urlparse

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from raspis.models import *
from photo.models import *
from raspis.models import Category, Page, DailyPhoto
from utils.json import JSONResponse
from utils.photos import photo_category, record_photo_view
from utils.gallery import make_gallery

def home(request):
    # Handle the case where we weren't on the first page of the categories
    # and clicked the home link...
    if request.session.get('indexp', 0) > 0:
        referer = request.META.get('HTTP_REFERER', '')
        if referer and urlparse.urlparse(referer).path == '/':
            request.session['indexp'] = 0
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def ajax_categories(request):
    start = 0
    p = int(request.GET.get('p', '0'))
    w = int(request.GET.get('w', '4'))
    n = max(int(math.floor(w / 250)), 2)
    start = p * n
    finish = start + n
    cats = Category.objects.filter(visible = True)
    request.session['indexp'] = p
    if start > len(cats):
        raise Http404
    rv = {'page': p, 'more': bool(finish < len(cats)),
          'cats': [c.as_dict() for c in cats[start:finish]]}
    return JSONResponse(rv)

def category_json(cat):
    rv = {'cat': cat.as_dict()}
    n = 0
    cats = Category.objects.filter(visible = True)
    for c in cats:
        if c == cat:
            break
        n += 1
    rv['n'] = n
    if n:
        rv['prev'] = cats[n - 1].as_dict()
    if n < len(cats) - 1:
        rv['next'] = cats[n + 1].as_dict()
    return rv

def category(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    rv = category_json(cat)
    if not request.user.is_staff:
        cat.record_view()
    return render_to_response('category.html', locals(),
                              context_instance=RequestContext(request))

def category_gallery(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    gallery = make_gallery(cat.photos.all(), int(request.GET['width']))
    return JSONResponse(gallery)

def category_slideshow(request, slug):
    cat = get_object_or_404(Category, slug = slug)
    images = slideshow_images(cat)
    return JSONResponse({'images': images})

def show(request, pid):
    photo = get_object_or_404(Photo, pk = pid)
    category = photo_category(photo)
    if not request.user.is_staff:
        record_photo_view(photo)
    image = photo.get_thumbnail("Large")
    return render_to_response('picture.html', locals(),
                                  context_instance=RequestContext(request))

def page(request, slug):
    p = get_object_or_404(Page, slug=slug)
    if p.url:
        return HttpResponseRedirect(p.url)
    return render_to_response('page.html', locals(),
                                  context_instance=RequestContext(request))

def today(request):
    from datetime import date
    dt = date.today()
    try:
        dp = DailyPhoto.objects.get(dt=dt)
        category = photo_category(dp.photo)
        if not request.user.is_staff:
            record_photo_view(dp.photo)
        image = dp.photo.get_thumbnail('Large')
    except DailyPhoto.DoesNotExist:
        dp = None
    return render_to_response('today.html', locals(),
                              context_instance=RequestContext(request))

def slideshow_images(cat):
    rv = []
    for i in cat.photos.all():
        img = i.get_thumbnail("Large")
        if img:
            rv.append({'href': img.img.url, 'title': i.title})
    return rv

@login_required
def login_redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('dashboard.views.home'))

@login_required
def original(request, pid):
    if not request.user.is_staff:
        # todo - add check to see if user is allowed!
        return HttpResponseForbidden("You do not have permission to download originals")
    photo = get_object_or_404(Photo, pk = pid)
    image_data = open(photo.image.path, 'rb').read()
    response = HttpResponse(image_data, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename='+os.path.basename(photo.image.path)
    return response
