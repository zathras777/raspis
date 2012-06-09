import urlparse

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden, HttpResponseRedirect, QueryDict

# Import the wraps function, with fall back for Python 2.3 and 2.4
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

def staff_required(f):
    ''' Decorator to check whether a user if staff.
        Code is based on code from contrib.auth.decorators and 
        contrib.auth.views 
    '''
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            # Assume we will need the full uri of the page requested...
            path = request.build_absolute_uri()
            # If the scheme (http or https) and the net location are the
            # same we simply need to pass the path as the next location.
            # If they differ we need to pass the full uri.
            login_scheme, login_netloc = urlparse.urlparse(settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()

            login_url_parts = list(urlparse.urlparse(settings.LOGIN_URL))
            querystring = QueryDict(login_url_parts[4], mutable=True)
            querystring['next'] = path
            login_url_parts[4] = querystring.urlencode(safe='/')
            return HttpResponseRedirect(urlparse.urlunparse(login_url_parts))

        if not request.user.is_staff:
            return HttpResponseForbidden("You do not have permission to view this page")

        return f(request, *args, **kwargs)
    return wraps(f)(decorator)

