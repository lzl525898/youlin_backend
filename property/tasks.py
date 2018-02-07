# coding:utf-8
import os
from celery import Celery
# import json
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
from core.settings import PUSH_STATUS

@youlinapp.task
def AsyncSetNotice(apiKey, secretKey, currentCommunityId, custom_content, tagSuffix,\
                   tagSuffix1, message, customTitle, topicId,user_id):
#     import sys
#     default_encoding = 'utf-8'
#     if sys.getdefaultencoding() != default_encoding:
#         reload(sys)
#         sys.setdefaultencoding(default_encoding)
    try:
        config = readIni()
        apiKey = config.get("SDK", "apiKey")
        secretKey = config.get("SDK", "secretKey")
        tagSuffix = config.get('topic', "tagSuffix")
        tagNormalName = tagSuffix + str(currentCommunityId)
        tagSuffix = config.get('report', "tagSuffix")
        tagAdminName = tagSuffix+str(currentCommunityId)
        _jpush = jpush.JPush(apiKey,secretKey) 
        pushExtra = {'pTitle': customTitle}
        pushExtra.update(custom_content)
    #    pushExtra = custom_content
        push = _jpush.create_push()
        push.audience = jpush.all_
        push.audience = jpush.audience(
                    jpush.tag(tagNormalName,tagAdminName),
                )
        push.notification = jpush.notification(
                    ios=jpush.ios(alert=message.encode('utf-8'), badge="+1", extras=pushExtra),
                    android=jpush.android(message,customTitle,None,pushExtra)
                )
        push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
        push.platform = jpush.all_
        push.send()
    except Exception,e:
        return str(e);
    AsyncNoticePush(topicId,user_id,currentCommunityId)
    
@youlinapp.task
def AsyncSetProprtyRepair(apiKey, secretKey, currentCommunityId, custom_content, message, customTitle, tagSuffix):
#     import sys
#     default_encoding = 'utf-8'
#     if sys.getdefaultencoding() != default_encoding:
#         reload(sys)
#         sys.setdefaultencoding(default_encoding)
    tagName = tagSuffix+str(currentCommunityId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': customTitle}
    pushExtra.update(custom_content)
#    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.tag(tagName),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=message.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(message,customTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()  
    
@youlinapp.task
def AsyncSetProcessStatus(apiKey, secretKey, aliasSuffix, senderUserId, custom_content, pushContent, pushTitle):
    tagAlias = aliasSuffix+str(senderUserId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': pushTitle}
    pushExtra.update(custom_content)
#    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(tagAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send() 
    
@youlinapp.task
def AsyncNoticePush(topicId,user_id,currentCommunityId):
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(user_id).encode('utf-8') + ":" \
                 +str(currentCommunityId).encode('utf-8')
   
    tagSuffix = config.get('topic', "tagSuffix")
    tagNormalName = tagSuffix + str(currentCommunityId)
    tagSuffix = config.get('report', "tagSuffix")
    tagAdminName = tagSuffix+str(currentCommunityId)
    tagSuffix = config.get('property', "tagSuffix")
    tagPropertyName = tagSuffix+str(currentCommunityId)

    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    _jpush = jpush.JPush(apiKey,secretKey) 
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.tag(tagNormalName,tagAdminName,tagPropertyName),
            )
    push.message = jpush.message(
                pushContent,
                u"push_new_topic",
                None,
                None
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send()
    
@youlinapp.task
def AsyncSuggestPush(topicId,user_id,currentCommunityId):
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(user_id).encode('utf-8') + ":" \
                 +str(currentCommunityId).encode('utf-8')
   
    tagSuffix = config.get('topic', "tagSuffix")
    tagNormalName = tagSuffix + str(currentCommunityId)
    tagSuffix = config.get('report', "tagSuffix")
    tagAdminName = tagSuffix+str(currentCommunityId)
    tagSuffix = config.get('property', "tagSuffix")
    tagPropertyName = tagSuffix+str(currentCommunityId)

    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    _jpush = jpush.JPush(apiKey,secretKey) 
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.tag(tagNormalName,tagAdminName,tagPropertyName),
            )
    push.message = jpush.message(
                pushContent,
                u"push_new_topic",
                None,
                None
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send() 

