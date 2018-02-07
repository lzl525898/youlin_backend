import os
from celery import Celery
# import json
from PIL import Image
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
from users.models import BlackList
from core.settings import PUSH_STATUS

@youlinapp.task
def AsyncMakeThumbnail(userDir,bigImg,smallImg,percent, suffix = None):
    filePath = userDir + bigImg
    im = Image.open(filePath)
    mode = im.mode
    if mode not in ('L', 'RGB'):
        im = im.convert('RGB')
    width, height = im.size
    n = int(percent)
    nwidth = int(width * n/100)
    nheight = int(height * n/100)
    thumb = im.resize((nwidth,nheight), Image.ANTIALIAS)
    if suffix:
        thumb.save(userDir+smallImg+suffix)
    else:
        thumb.save(userDir+smallImg)

@youlinapp.task
def AsyncAMR2WAV(senderId,topicId,newVideo,iosDevice):
    
    if str(iosDevice) == 'ios':
        wav2amrPath = '/opt/youlin_backend/media/youlin/res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'
        wav2amr = 'ffmpeg -i '+wav2amrPath+newVideo+' '+(wav2amrPath+newVideo)[:-4]+'.amr'
        os.system(amr2wav)
    else:
        amr2wavPath = '/opt/youlin_backend/media/youlin/res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'
        amr2wav = 'ffmpeg -i '+amr2wavPath+newVideo+' '+(amr2wavPath+newVideo)[:-4]+'.wav'
        os.system(amr2wav)

@youlinapp.task
def AsyncDelTopic(topicId,communityId):
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    tagNormalName = tagSuffix + str(communityId)
    tagSuffix = config.get('report', "tagSuffix")
    tagAdminName = tagSuffix+str(communityId)
    tagSuffix = config.get('property', "tagSuffix")
    tagPropertyName = tagSuffix+str(communityId)
    pushContent = str(topicId)
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
                u"push_del_topic",
                None,
                None
            )
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send() 
    
@youlinapp.task
def AsyncAddTopic(topicId, user_id, curComId, currentCommunityId):
    blackList = ''
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(user_id))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList = blackList + str(blkListOtherQuerySet[i].user_id) + '-'
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(user_id))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList = blackList + str(blkListOwnQuerySet[i].black_id) + '-'
    except Exception,e:
        blackList = str(Exception)+"====="+str(e)
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(user_id).encode('utf-8') + ":" \
                 +str(curComId).encode('utf-8')
   
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
                blackList
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send() 

@youlinapp.task
def AsyncUpdateTopic(topicId, currentCommunityId):
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8')
   
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
                u"push_update_topic",
                None,
                None
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send() 

@youlinapp.task
def AsyncAddCommentPush(topicId, senderId, currentCommunityId,commentCount):
    blackList = ''
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(senderId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList = blackList + str(blkListOtherQuerySet[i].user_id) + '-'
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(senderId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList = blackList + str(blkListOwnQuerySet[i].black_id) + '-'
    except Exception,e:
        blackList = str(Exception)+"====="+str(e)
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderId).encode('utf-8') + ":" \
                 +str(currentCommunityId).encode('utf-8')+ ":" \
                 +str(commentCount).encode('utf-8')
   
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
                u"push_new_comm",
                None,
                blackList
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()

@youlinapp.task
def AsyncDelCommentPush(topicId, senderId, communityId, commentId, commentCount):
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderId).encode('utf-8') + ":" \
                 +str(communityId).encode('utf-8') + ":" \
                 +str(commentId).encode('utf-8') + ":" \
                 +str(commentCount).encode('utf-8')
   
    tagSuffix = config.get('topic', "tagSuffix")
    tagNormalName = tagSuffix + str(communityId)
    tagSuffix = config.get('report', "tagSuffix")
    tagAdminName = tagSuffix+str(communityId)
    tagSuffix = config.get('property', "tagSuffix")
    tagPropertyName = tagSuffix+str(communityId)

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
                u"push_del_comm",
                None,
                None
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_      
    push.send() 
    
@youlinapp.task
def AsyncReportTopic(apiKey, secretKey, tagSuffix, communityId, custom_content, message, pTitle):
    tagName = tagSuffix+str(communityId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': pTitle}
    pushExtra.update(custom_content)
#    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.tag(tagName),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=message.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(message,pTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()  
    
@youlinapp.task
def AsyncShareCommunityNews(apiKey, secretKey, alias, recipyId, customContent, pushContent, pushTitle):
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(recipyId)
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
def AsyncReplayCommentPush(apiKey,secretKey,custom_content,currentAlias,message,customTitle):
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': customTitle}
    pushExtra.update(custom_content)
#    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=message.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(message,customTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()  

@youlinapp.task
def AsyncSayHelloPush(apiKey,secretKey,custom_content,currentAlias,message,customTitle):
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = {'pTitle': customTitle}
    pushExtra.update(custom_content)
#    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                ios=jpush.ios(alert=message.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(message,customTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()  