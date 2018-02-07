# coding:utf-8
import os
from celery import Celery
import json
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
import time
    
@youlinapp.task    
def TimingTaskWithWeather():
    from comServices.views import PushCommunityWeather
    PushCommunityWeather()
    response_data = {}
    response_data['flag'] = 'weather is ok'
    return response_data
#     import sys
#     default_encoding = 'utf-8'
#     if sys.getdefaultencoding() != default_encoding:
#         reload(sys)
#         sys.setdefaultencoding(default_encoding)
#     config = readIni()
#     pushTitle = '天气快报'
#     pushContent = weatherInfoDict['content']
#     apiKey = config.get("SDK", "apiKey")
#     secretKey = config.get("SDK", "secretKey")
#     _jpush = jpush.JPush(apiKey,secretKey) 
#     tagSuffix = config.get('topic', "tagSuffix")
#     tagNormalName = tagSuffix + str(weatherInfoDict['community_id'])
#     tagSuffix = config.get('report', "tagSuffix")
#     tagAdminName = tagSuffix+str(weatherInfoDict['community_id'])
#     tagSuffix = config.get('property', "tagSuffix")
#     tagPropertyName = tagSuffix+str(weatherInfoDict['community_id'])
# 
#     from core.settings import HOST_IP,RES_URL
#     currentPushTime = long(time.time()*1000)
# 
#     evaDict = {}
#     evaDict['title'] = pushTitle
#     evaDict['content'] = pushContent
#     evaDict['pushTime'] = currentPushTime
#     evaDict['wprTime'] = weatherInfoDict['time']
#     evaDict['weaId'] = weatherInfoDict['weaorzoc_id']
#     evaDict['pushType'] = 8
#     evaDict['contentType'] = 1
#     evaDict['communityId'] = communityId
#     evaDict['userAvatar'] = HOST_IP+RES_URL+'res/default/avatars/default-avatar.png'
#     recordId = createPushRecord(8,1,pushTitle,pushContent,currentPushTime,8001,json.dumps(evaDict),communityId,8001)
#     evaDict['recordId'] = recordId
#     pushExtra = evaDict
#     push = _jpush.create_push()
#     push.audience = jpush.all_
#     push.audience = jpush.audience(
#                 jpush.tag(tagNormalName,tagAdminName,tagPropertyName),
#             )
#     push.notification = jpush.notification(
#         android=jpush.android(pushContent,pushTitle,None,pushExtra)
#     )
#     push.options = {"time_to_live":86400, "sendno":9527, "apns_production":True}
#     push.platform = jpush.all_
#     push.send()
                