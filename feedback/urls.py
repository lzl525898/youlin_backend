from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^submitFeedback/$', views.setFeedBack, name='setFeedBack'),
]
