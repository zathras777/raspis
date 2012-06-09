from django.conf import settings
from datetime import date

from models import Category, Page

def top_level_categories():
    return [c.as_dict() for c in Category.objects.filter(top_level = True)]

def visible_pages():
    dt = date.today()
    rv = []
    for p in Page.objects.all():
        if p.first_dt is None and p.last_dt is None:
            rv.append({'title': p.title, 'slug': p.slug, 'url': p.url})
        elif p.first_dt and p.first_dt < dt and p.last_dt and p.last_dt >= dt:
            rv.append(p)
        elif p.last_dt and p.last_dt >= dt:
            rv.append(p)
        elif p.first_dt and p.first_dt <= dt:
            rv.append(p)
    return rv
    
def site_settings(request):
    rv = {'debug': settings.DEBUG}
    if not 'dashboard' in request.path and not 'admin' in request.path:
        rv['pages'] = visible_pages()
        for k in ['indexp', 'catp']:
            rv[k] = request.session.get(k, 0)
    rv['mobile'] = getattr(request, 'mobile', False)
    return rv

