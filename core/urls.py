from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from core.views import OnlineNetwork
import django.contrib.auth

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^ping/', OnlineNetwork),
                       url(r'^youlin/', include('yl_api.urls')),
                       url(r'^feedback/', include('feedback.urls')),
                       url(r'^push/', include('push.urls')),
                       url(r'^yl/', include('web.urls')),
                       url(r'^apiproperty/', include('property.urls')),
                       url(r'^comsrv/', include('comServices.urls')),
                       url(r'^address/', include('addrinfo.urls')),
                       url(r'^comm/', include('community.urls')),
                       url(r'^users/', include('users.urls')),
                       url(r'^$', 'web.views_site.index',
                           name='index'),
                       # the admin
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^auth/', include('django.contrib.auth.urls')),
                       )

if settings.DEBUG:
    urlpatterns = patterns('',
                           url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                           url(r'', include(
                               'django.contrib.staticfiles.urls')),
                           ) + urlpatterns

# make sure we register verbs when django starts
from core import verbs
