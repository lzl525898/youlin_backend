from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^addtopic/$', views.postNewTopic, name='postNewTopic'),###########################################
    url(r'^updatetopic/$', views.updateTopic, name='updateTopic'),###########################################
    url(r'^gettopic/$', views.getTopic, name='getTopic'),###########################################
    url(r'^getMytopic/$', views.getMyTopic, name='getMyTopic'),###########################################
    url(r'^addcomm/$', views.addComment, name='addComment'),###########################################
    url(r'^delcomm/$', views.delComment, name='delComment'),###########################################
    url(r'^repcomm/$', views.replayComment, name='replayComment'),
    url(r'^getcomm/$', views.getComment, name='getComment'),###########################################
    url(r'^findtopic/$', views.searchTopic, name='searchTopic'),###########################################
    url(r'^hitpraise/$', views.clickPraise, name='clickPraise'),###########################################
    url(r'^intotopic/$', views.intoDetailTopic, name='intoDetailTopic'),###########################################
    url(r'^deltopic/$', views.deleteTopic, name='deleteTopic'),###########################################
    url(r'^enroll/$', views.activityEnroll, name='activityEnroll'),###########################################
    url(r'^canenroll/$', views.cancelEnroll, name='cancelEnroll'),###########################################
    url(r'^detenroll/$', views.detailEnroll, name='detailEnroll'),###########################################
    url(r'^delstatus/$', views.getTopicDeleteStatus, name='getTopicDeleteStatus'),###########################################
    url(r'^report/$', views.reportTopicHandle, name='reportTopicHandle'),###########################################
    url(r'^addCol/$', views.addCollection, name='addCollection'),###########################################
    url(r'^delCol/$', views.delCollection, name='delCollection'),###########################################
    url(r'^getCol/$', views.getCollectTopic, name='getCollectTopic'),###########################################
    url(r'^getCount/$', views.getTopicCounts, name='getTopicCounts'),###########################################
    url(r'^getReport/$', views.getReportInfo, name='getReportInfo'),###########################################
    url(r'^newShare/$', views.shareCommunityNews, name='shareCommunityNews'),###########################################
]
