#!/usr/bin/env python

import os
import sys
import re
from datetime import datetime

from django.core.management import call_command, setup_environ

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INSTALL_PATH = os.path.join(ROOT_DIR, 'install')

admins = {}
subst_vars = {
    'DB_ENGINE': "django.db.backends.sqlite3",
    'DB_NAME': os.path.join(ROOT_DIR, 'development.db'),
    'DB_USER': '',
    'DB_PASSWD': '',
    'DB_HOST': '',
    'DB_PORT': '',
    'TZ': 'Europe/London',
    'USE_TZ': True,
    'LANG': 'en-us',
    'USE_I18N': False,

    # URL's we refer to in the settings file
    'MEDIA_URL': '/media/',
    'STATIC_URL': '/static/',
    # Directories we refer to in the settings file
    'LOCAL_DIR': os.path.join(ROOT_DIR, 'local'),
    'MEDIA_DIR': os.path.join(ROOT_DIR, 'media'),
    'ROOT_DIR': ROOT_DIR,
    'STATIC_DIR': os.path.join(ROOT_DIR, 'static'),
    'TEMPLATE_DIR': os.path.join(ROOT_DIR, 'templates'),
}

def make_secret_key():
    from random import choice
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-=+)'
    subst_vars['SECRET_KEY'] = ''.join([choice(chars) for i in range(50)])
    
def copy_subst_settings(src, dest):
    inpF = open(src, 'r')
    raw = inpF.read()
    inpF.close()

    subst_vars['TIME_DATE'] = datetime.today().strftime("%H:%I %d %B %Y")
    
    for k,v in subst_vars.items():
        val = "'%s'" % v if type(v) == str else "%s" % v
        raw = re.sub('@%s@' % k, val, raw)

    admin_strings = ["('%s', '%s')" % (k,v) for k,v in admins.items()]
    raw = re.sub('@ADMINS@', ",\n".join(admin_strings), raw)

    outF = open(dest, "w")
    outF.write(raw)
    outF.close()


def string_question(q, a = '', rqd = False, min_length = 0):
    print q
    raw = raw_input("[%s]: " % a)
    if len(raw) == 0 and len(a) > 0:
        raw = a
    if min_length > 0 and len(raw) < min_length:
        print "Your reply is too short. Minimum of %d characters required" % min_length
        return ask_question(q, a, rqd, min_length)
    if rqd and len(raw) == 0:
        print "An answer is required"
        return ask_question(q, a, rqd, min_length)
    return raw

def bool_question(q, a = False):
    print q, "(Y/N)"
    raw = raw_input("[%s]: " % ('Y' if a else 'N'))
    if len(raw) == 0:
        return a
    if 'y' in raw.lower():
        return True
    return False

def option_question(q, opts, dflt = 1):
    print q
    print "Please select from the following options:\n"
    nopts = 1
    for o in opts:
        print "%10s : %s" % ("%2d" % nopts, o[0])
        nopts += 1
    if dflt < 1 or dflt > nopts:
        dflt = 1
    n = raw_input("[%s]: " % dflt)
    if len(n) == 0 or not n.isdigit():
        return dflt
    return int(n)
    
def db_questions():
    print '''
In order to function we require a database. Please answer the following...
'''
    db_options = [
      ('MySQL', 'mysql'),
      ('Postgres', 'postgresql_psycopg2'),
      ('Oracle', 'oracle')
    ]
    engine = option_question("Which database engine will you be using?", db_options)
    subst_vars['DB_ENGINE'] = 'django.db.backends.' + db_options[engine - 1][1]
    subst_vars['DB_NAME'] = string_question('Database name?', '', True)
    subst_vars['DB_USER'] = string_question('Database user?', '', True)
    subst_vars['DB_PASSWD'] = string_question('Database user password?', '', True)
    if not bool_question('''Are you happy to accept the default hostname and port
for the database server?''', True):
        subst_vars['DB_HOST'] = string_question('Database server hostname?', '', True)
        subst_vars['DB_PORT'] = string_question('Database server port number?', '', True)

def add_admins():
    print "\nAdministrators\nThe admins listed in the settings file will be sent emails when something goes wrong!"
    while bool_question("Do you want to add an admin?"):
        add_an_admin()

def add_an_admin():
    name = string_question("Name of admin")
    email = string_question("Email address")
    if len(name) and len(email):
        admins[name] = email

def add_user():
    from django.contrib.auth.models import User
    print '''
Superuser Account

The site needs a superuser account. This will likely be the account you will
use for your site administration needs.
'''
    username = string_question("Username to use?", "admin", True)
    first_name = string_question("First name?")
    last_name = string_question("Last name?")
    password = string_question("Password to use?", '', True, min_length = 6)

    u, ctd = User.objects.get_or_create(username = username)
    u.first_name = first_name
    u.last_name = last_name
    u.is_active = True
    u.is_staff = True
    u.is_superuser = True
    u.set_password(password)
    u.save()
    return ("%s %s" % (first_name, last_name)).strip()
    
def set_site_details(url, name, author):
    import raspis.settings
    setup_environ(raspis.settings)
    from config.models import ConfigGroup
    cgrp = ConfigGroup.objects.get(name = 'site')
    cgrp.set('url', url)
    cgrp.set('name', name)
    cgrp.set('author', author)

    from django.contrib.sites.models import Site
    ss = Site.objects.get(pk = 1)
    ss.domain = url
    ss.name = name
    ss.save()
    
def syncdb():
    call_command('syncdb', interactive = False)
         
def collectstatic():
    call_command('collectstatic', interactive = False)

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspis.settings")
    sys.path.insert(0, ROOT_DIR)
    subst_vars['TIME_DATE'] = datetime.today().strftime("%H:%I %d %B %Y")
    print '''raspis configuration.
    
First, a few questions...
'''
    site_url = string_question("What is the URL for the site (can be changed later)?", "127.0.0.1:8000", True)
    site_name = string_question("What name do you want to give the site?", "raspis", True)
    local = bool_question("Setup as a local development site?")
    if not local:
        db_questions()
    else:
        if os.path.exists(subst_vars['DB_NAME']) and \
           bool_question("The development db exists. Do you want to remove it?"):
            os.unlink(subst_vars['DB_NAME'])
            
    subst_vars['DEBUG'] = local
    subst_vars['EMAIL_SUBJECT_PREFIX'] = "[%s]" % site_name.upper()
    make_secret_key()

    add_admins()
    
    print "\nNow creating configuration files..."
    file_ops = (
        ('settings.py', 'raspis'),
        ('application.wsgi', ''),
        ('local_wsgi.py', 'raspis'),
    )
    for ops in file_ops:
        src = os.path.join(INSTALL_PATH, ops[0] + '.install')
        dest = os.path.join(ROOT_DIR, ops[1], ops[0])
        print "    ", ops[0]
        copy_subst_settings(src, dest)

    print "\nNow attempting to create the database tables and populate with initial data..."
    syncdb()

    import raspis.settings
    setup_environ(raspis.settings)
    from django.contrib.auth.models import User
    
    if User.objects.count() == 0:
        site_user = add_user()
    else:
        site_user = User.objects.all()[0].get_full_name()
        
    set_site_details(site_url, site_name, site_user)
    print "\nCollecting required static files...\n"
    collectstatic()
    
    print "\nConfiguration is now complete."
    
