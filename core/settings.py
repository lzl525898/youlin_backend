"""
Django settings for pinterest_example project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import urlparse
import socket
from datetime import timedelta
from celery.schedules import crontab
from __builtin__ import True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# on Heroku redis connection parameters come from environment variables
redis_url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost:6379'))

STREAM_REDIS_CONFIG = {
    'default': {
        'host': redis_url.hostname,
        'port': redis_url.port,
        'password': redis_url.password,
        'db': 0
    },
}

BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
MEDIA_ROOT = os.path.join(BASE_ROOT, 'media/')
STATIC_ROOT = os.path.join(BASE_ROOT, 'static/')
DOCS_ROOT = os.path.join(BASE_ROOT, 'docs/')
TEMPLATE_ROOT = os.path.join(BASE_ROOT, 'templates/')
TEMPLATE_ASSET_ROOT = os.path.join(BASE_ROOT, 'static/assets/templates/')
TEMPLATE_WEB_ROOT = os.path.join(BASE_ROOT, 'web/templates/')
#RES_URL = 'http://'+socket.gethostbyname(socket.gethostname())+'/media/youlin/'
# HOST_IP = 'https://123.57.9.62'
PUSH_STATUS = False
HOST_IP = 'https://www.youlinzj.cn'
MEDIA_YL = '/media/youlin/'
RES_URL = HOST_IP+ MEDIA_YL
YL_BACNEND = HOST_IP+'/yl/web/admin'
SHARE_URL = HOST_IP + '/yl'
SHARE_NEWS = '/yl/web/getNews/?id='
NEW_VERSION_URL = 'http://openbox.mobilem.360.cn/index/d/sid/3254442'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
MEDIA_URL = '/media/'
TEMPLATE_DIRS = (
    TEMPLATE_ROOT,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    TEMPLATE_WEB_ROOT,
    TEMPLATE_ASSET_ROOT,
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

COMPRESS_PRECOMPILERS = (
    ('text/x-sass', 'sass {infile} {outfile}'),
    ('text/x-scss', 'sass --scss {infile} {outfile}'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ib_^kc#v536)v$x!h3*#xs6&l8&7#4cqi^rjhczu85l9txbz+w'
#SECRET_KEY = 'ib_^kc#v536)v$x!h3*#xs6&l8&7#4cqi^rjhczu85lmtxbz+w'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['123.57.9.62']

import djcelery
djcelery.setup_loader()

#from celery import platforms
#platforms.C_FORCE_ROOT = True

CELERY_TIMEZONE='Asia/Shanghai'
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_URL = 'redis://localhost:6379'  
CELERY_RESULT_BACKEND = 'redis://localhost:6379' 
CELERY_ACCEPT_CONTENT = ['application/json']  
CELERY_TASK_SERIALIZER = 'json'  
CELERY_RESULT_SERIALIZER = 'json' 
CELERYBEAT_SCHEDULER = 'celery.beat.PersistentScheduler'
#celery.beat.PersistentScheduler
#djcelery.schedulers.DatabaseScheduler
CELERYBEAT_SCHEDULE = {
    'add-every-day-7-morning': {
        'task': 'users.tasks.CeleryBeatScheduleWithNews',
        'schedule': crontab(hour=8, minute=30),
    },
    'add-every-day-6-morning': {
        'task': 'comServices.tasks.TimingTaskWithWeather',
        'schedule': crontab(hour=6, minute=0),
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'luckyforlei@163.com'
EMAIL_HOST_PASSWORD = 'lucky@163.com'
DEFAULT_FROM_EMAIL = 'youlin <luckyforlei>'
EMAIL_RECV_USER = 'zelei@nfs-hlj.com'



CKEDITOR_MEDIA_PREFIX = "/static/ckeditor/"
CKEDITOR_UPLOAD_PATH = os.path.join(BASE_ROOT, 'media/youlin')
# CKEDITOR_JQUERY_URL = '/opt/workspace/youlin_backend/static/admin/js/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER=True   
#CKEDITOR_UPLOAD_PREFIX = RES_URL+"life/"

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'core',
    'south',
    'djcelery',
#    'compressor',
    'rest_framework',
    'users',
    'push',
    'addrinfo',
    'community',
    'comServices',
    'web',
    'property',
    'feedback',
    'ckeditor',
    'exchange',
    'yl_api',
    'haystack',
)
# CKEDITOR_JQUERY_URL = '/opt/workspace/youlin_backend/static/admin/js/jquery.min.js'
# CKEDITOR_UPLOAD_PATH = "youlin/newspic"
# CKEDITOR_IMAGE_BACKEND = "pillow"
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.http.SetRemoteAddrFromForwardedFor',
#    'django.middleware.csrf.CsrfResponseMiddleware',
)

REST_FRAMEWORK = {  
#    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',), 	
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',), 
#    'PAGINATE_BY': 10
#     'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly']
}

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'youlin',
        'USER': 'root',
        'PASSWORD': 'CRteam2o!6',
        'HOST':'localhost',
        'PORT':'3306',
        'OPTIONS':{'charset':'utf8mb4'},
    }
}

#WHOOSH_INDEX = os.path.join('/usr/local/lib/python2.7/dist-packages/whoosh','whoosh_index')
#HAYSTACK_SITECONF='/opt/youlin_backend/whoosh_index'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 1
HAYSTACK_DEFAULT_OPERATOR = 'OR'
HAYSTACK_CONNECTIONS = { 
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine', 
        'PATH': os.path.join(BASE_ROOT, 'whoosh_index'),
        'OPERATOR': 'OR',
    },
}
#HAYSTACK_SITECONF = '/opt/youlin_backend/whoosh_index'
#HAYSTACK_SEARCH_ENGINE = 'haystack.backends.whoosh_backend.WhooshEngine'
#HAYSTACK_WHOOSH_PATH = os.path.join(BASE_ROOT, 'whoosh_index')


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ("css", os.path.join(STATIC_ROOT,'css')),
    ("js", os.path.join(STATIC_ROOT,'js')),
    ("images", os.path.join(STATIC_ROOT,'images')),
    ("font", os.path.join(STATIC_ROOT,'font')),
    ("avatars", os.path.join(STATIC_ROOT,'avatars')),
     ("assets", os.path.join(STATIC_ROOT,'assets')),
     ("guaguale", os.path.join(STATIC_ROOT,'guaguale')),
     ("baoxiang", os.path.join(STATIC_ROOT,'baoxiang')),
)
#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates', 
#        'DIRS': 
#            [ 
#                TEMPLATE_ROOT,
#            ], 
#    }, 
#    { 
#        'BACKEND': 'django.template.backends.jinja2.Jinja2', 
#        'DIRS': 
#            [ 
#                '/home/html/jinja2', 
#            ], 
#    },
#]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(message)s'
            #'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'stream_framework': {
            'handlers': ['console'],
            'level': 'WARNING',
            'filters': []
        },
        'redis': {
            'handlers': ['console'],
            'level': 'WARNING',
            'filters': []
        },
        '': {
            'handlers': [],
            'level': 'WARNING',
            'filters': []
        },
    }
}
