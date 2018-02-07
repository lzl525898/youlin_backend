"""
WSGI config for pinterest_example project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

from os.path import dirname,abspath
PROJECT_DIR = dirname(dirname(abspath(__file__)))
import sys
sys.path.insert(0,PROJECT_DIR)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ['PYTHON_EGG_CACHE'] = '/opt/youlin_backend/.python-egg'
application = get_wsgi_application()

try:
	from dj_static import Cling
except ImportError:
	pass
else:
	application = Cling(application)
