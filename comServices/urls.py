from django.conf.urls import url

from . import views
from . import views_pingpp

urlpatterns = [
    url(r'^loadService/$', views.loadCommunityService, name='loadCommunityService'),
    url(r'^getNews/$', views.getNewsList, name='getNewsList'),
    url(r'^charge/$', views_pingpp.GenCharge, name='GenCharge'),
]
