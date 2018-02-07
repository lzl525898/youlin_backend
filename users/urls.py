from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^modifypwd/$', views.modifypwd, name='modifypwd'),##########################################
    url(r'^getInfo/$', views.getPersonalInfo, name='getPersonalInfo'),##########################################
    url(r'^upload/$', views.uploadUserInfo, name='uploadUserInfo'),##########################################
    url(r'^login/$', views.loginUser, name='loginUser'),##########################################
    url(r'^regist/$', views.registNewUser, name='registNewUser'),##########################################
    url(r'^check/$', views.checkPhoneExist, name='checkPhoneExist'),##########################################
    url(r'^updatepwd/$', views.updatePasswd, name='updatePasswd'),##########################################
    url(r'^addfamily/$', views.addFamily, name='addFamily'),##########################################
    url(r'^updatefamily/$', views.modifiFamily, name='modifiFamily'),##########################################
    url(r'^delfamily/$', views.deleFamilyRecord, name='deleFamilyRecord'),##########################################
    url(r'^curaddrflag/$', views.updatePrimaryAddr, name='updatePrimaryAddr'),##########################################
    url(r'^userfamily/$', views.handleFamily, name='handleFamily'),##########################################
    url(r'^neighbors/$', views.getNeighbors, name='getNeighbors'),##########################################
    url(r'^setadmin/$', views.setAdminPermiss, name='setAdminPermiss'),
    url(r'^setPushInfo/$', views.setUserPushInfo, name='setUserPushInfo'),
    url(r'^regEasemob/$', views.registEasemob, name='registEasemob'),##########################################
    url(r'^setLogOff/$', views.setPhoneLogoff, name='setPhoneLogoff'),##########################################
    url(r'^loginStatus/$', views.checkPushChannelExist, name='checkPushChannelExist'),##########################################
    url(r'^getStatus/$', views.getPublicStatus, name='getPublicStatus'),##########################################
    url(r'^checkToken/$', views.checkIMEI, name='checkIMEI'),##########################################
    url(r'^blacklist/$', views.handleBlackList, name='handleBlackList'),##########################################
]
