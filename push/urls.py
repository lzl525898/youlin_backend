from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^pushRecord/$', views.getPushRecord, name='getPushRecord'),
    url(r'^delRecord/$', views.deleteRecords, name='deleteRecords'),
    url(r'^recordStatus/$', views.setClickStatus, name='setClickStatus'),
]
