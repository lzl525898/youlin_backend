import os
from celery import Celery
# import json
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
from core.settings import PUSH_STATUS

@youlinapp.task
def AsyncAuditSubmit(apiKey, secretKey, alias, user_id, customContent, pushContent, pushTitle):
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(user_id)
    pushExtra = {'pTitle': pushTitle}
    pushExtra.update(customContent)
#    pushExtra = customContent
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),                       
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()

@youlinapp.task
def AsyncAddressAuditSubmit(apiKey,secretKey,alias,user_id,customContent,pushContent,pushTitle):
    from users.models import User
    uObectj = User.objects.get(user_id=long(user_id))
    userCache = uObectj.user_handle_cache
    addrCache = uObectj.addr_handle_cache
    uObectj.addr_handle_cache = (int(addrCache) + 1)%1000
    uObectj.save()
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': pushTitle}
    pushExtra.update(customContent)
#    pushExtra = customContent
    currentAlias = alias + str(user_id)
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
            jpush.alias(currentAlias),
        )
    push.notification = jpush.notification(
            ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),
            android=jpush.android(pushContent,pushTitle,None,pushExtra)
        )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send() 
    
    
@youlinapp.task
def AsyncCommonSubmit(apiKey,secretKey,alias,user_id,customContent,pushContent,pushTitle):
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(user_id)
    pushExtra = {'pTitle': pushTitle}
    pushExtra.update(customContent)
#    pushExtra = customContent
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()

@youlinapp.task
def AsyncSetWelcomeTopic(topicId,sender_id,sender_community_id):
    config = readIni()
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(sender_id).encode('utf-8') + ":" \
                 +str(sender_community_id).encode('utf-8')
   
    tagSuffix = config.get('topic', "tagSuffix")
    tagNormalName = tagSuffix + str(sender_community_id)
    tagSuffix = config.get('report', "tagSuffix")
    tagAdminName = tagSuffix+str(sender_community_id)
    tagSuffix = config.get('property', "tagSuffix")
    tagPropertyName = tagSuffix+str(sender_community_id)
    
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
    push.options = {"time_to_live":60, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send() 


@youlinapp.task
def AsyncPushNew(apiKey,secretKey,custom_content,tagName,message,customTitle):
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
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()  
    
@youlinapp.task
def AsyncCFailureCauseWithAudit(apiKey, secretKey, alias, login_account, customContent, pushContent, pushTitle):
    from users.models import User
    uObectj = User.objects.get(user_id=long(login_account))
    userCache = uObectj.user_handle_cache
    addrCache = uObectj.addr_handle_cache
    uObectj.addr_handle_cache = (int(addrCache) + 1)%1000
    uObectj.save()
    pushExtra = {'pTitle': pushTitle}
    pushExtra.update(customContent)
#    pushExtra = customContent
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(login_account)
    pushExtra = customContent 
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()
    


