from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^setnotice', views.setNotice, name='setNotice'),
   url(r'^getnotice', views.getNotice, name='getnotice'),
   url(r'^setsuggest', views.setSuggest, name='setSuggest'),
   url(r'^getsuggest', views.getSuggest, name='getSuggest'),
   url(r'^setinfo', views.setPropertyInfo, name='setPropertyInfo'),
   url(r'^getinfo', views.getPropertyInfo, name='getPropertyInfo'),
   url(r'^setrepair', views.setProprtyRepair, name='setProprtyRepair'),
   url(r'^getrepair', views.getProprtyRepair, name='getProprtyRepair'),
   url(r'^setstatus', views.setProcessStatus, name='setProcessStatus'),
]
