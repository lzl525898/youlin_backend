from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^api1.0/$', views.postYouLinAPI, name='postYouLinAPI'),
]
