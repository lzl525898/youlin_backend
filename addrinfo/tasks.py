# coding:utf-8
import os
from celery import Celery
import json
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
from core.settings import PUSH_STATUS
import time

@youlinapp.task
def AsyncSetWelcome(topicId, sender_id, sender_community_id):
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
def TimingTaskWithEvaluatiorRecord(uid,userId,communityId):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    from addrinfo.models import UserEvaluatiorRecord,BusinessCircle
    uerQuerySet = UserEvaluatiorRecord.objects.filter(uer_uid=str(uid),user_id=long(userId),uer_status=2)
    if int(uerQuerySet.count())>10:
        pass
    else:
        uerQuerySet = UserEvaluatiorRecord.objects.filter(uer_uid=str(uid),user_id=long(userId),uer_status=0)#
        userSize = uerQuerySet.count()
        if int(userSize)<=0: #说明该商家还没有评论过
            userEvaObj = UserEvaluatiorRecord(uer_uid=str(uid),user_id=long(userId))
            userEvaObj.save()
            config = readIni()
            pushTitle = config.get("evaluation", "title")
            pushContent = config.get("evaluation", "content0")
            alias = config.get("SDK", "youlin")
            apiKey = config.get("SDK", "apiKey")
            secretKey = config.get("SDK", "secretKey")
            _jpush = jpush.JPush(apiKey,secretKey) 
            currentAlias = alias + str(userId)
            bcObj = BusinessCircle.objects.get(bc_uid=str(uid),community_id=long(communityId))
            from core.settings import HOST_IP,RES_URL
            currentPushTime = long(time.time()*1000)
            import re
            targetTag = str(bcObj.bc_tag)
            targetIndex = 0
            #0美食 1 宾馆 2 生活娱乐
            pattern = re.compile('酒店',re.UNICODE)
            if pattern.match(targetTag): 
                    targetIndex = 1
            else:
                pattern = re.compile('美食',re.UNICODE)
                if pattern.match(targetTag):
                    targetIndex = 0
                else:
                    pattern0 = re.compile('美食',re.UNICODE)
                    pattern1 = re.compile('酒店',re.UNICODE)
                    if pattern0.match(targetTag) is None and pattern1.match(targetTag) is None:
                        targetIndex = 2
            evaDict = {}
            evaDict['uid'] = uid
            evaDict['userId'] = userId
            evaDict['communityId'] = communityId
            evaDict['tag'] = targetIndex
            evaDict['title'] = pushTitle
            evaDict['content'] = pushContent
            evaDict['pushTime'] = currentPushTime
            evaDict['uerId'] = userEvaObj.getBizCirRecordId()
            evaDict['pushType'] = 7
            evaDict['contentType'] = 1
            evaDict['shopName'] = bcObj.bc_name
            evaDict['userAvatar'] = RES_URL+'res/default/avatars/bizcir-eval.png'
            recordId = createPushRecord(7,1,pushTitle,pushContent,currentPushTime,7001,json.dumps(evaDict),communityId,7001)
            evaDict['recordId'] = recordId
            pushExtra = evaDict
            
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
                