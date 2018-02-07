from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^addrVerify/$', views.addressVerify, name='addressVerify'),
]
