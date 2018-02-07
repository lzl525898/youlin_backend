# coding:utf-8
from django.http import HttpResponse
from users.models import User,FamilyRecord,Admin,BlackList
from community.models import Comment, Topic, Media_files, Activity, Praise, EnrollActivity, ReportTopic,CollectionTopic
from rest_framework.decorators import api_view
from django.core import serializers
from django.conf import settings
from PIL import Image
import re
import os
import json
import time
import random
import jpush as jpush
from push.views import createPushRecord,readIni
from push.sample import pushMsgToTag,pushMsgToSingleDevice
from django.db.models import Q
from community.views import *
from property.tasks import *
from models import PropertyInfo
from addrinfo.models import Community
# 1 user 2 address 3 property 4 topic
def getCustomDict(senderUserId,currentPushTime,pTitle,userAvatar,topicId,message1,infoTitle,infoContent,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('userId',senderUserId)
    dicts.setdefault('pushType',3)
    dicts.setdefault('contentType',1) # 1 notice 2 repairing 3 repaired
    dicts.setdefault('pushTime',currentPushTime)
    dicts.setdefault('title',pTitle)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('message',message1)
    dicts.setdefault('pushTitle',infoTitle)
    dicts.setdefault('communityId',communityId)
    dicts.setdefault('pushContent',infoContent)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

def getCustomDictWithRepair(senderUserId,currentPushTime,pTitle,userAvatar,topicId,message1,infoTitle,infoContent,repairStatus,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('userId',senderUserId)
    dicts.setdefault('pushType',3)
    dicts.setdefault('contentType',1) # 1 notice 2 repairing 3 repaired
    dicts.setdefault('pushTime',currentPushTime)
    dicts.setdefault('title',pTitle)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('message',message1)
    dicts.setdefault('pushTitle',infoTitle)
    dicts.setdefault('pushContent',infoContent)
    dicts.setdefault('repairStatus',repairStatus)
    dicts.setdefault('communityId',communityId)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts
    
@api_view(['GET','POST'])
def setNotice(request):  
    data = {}
    sendTitle = None
    senderName = None
    senderUserId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        sendTitle                      = request.POST.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#3
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        senderUserId                   = request.POST.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.POST.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.display_name          = request.POST.get('display_name', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        topicObj.sender_community_id   = request.POST.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    else:
        sendTitle                      = request.GET.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        senderUserId                   = request.GET.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.GET.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    # tag push
    try:        
        config = readIni()
        pushTitle = config.get("property", "title")
        customTitle = config.get("property", "content0")
        tagSuffix = config.get('topic', "tagSuffix")
        tagSuffix1 = config.get('report', "tagSuffix")
        pushContent = str(topicId).encode('utf-8') + ":" \
                     +str(user_id).encode('utf-8') + ":" \
                     +str(currentCommunityId).encode('utf-8')
        currentPushTime = long(time.time()*1000)
        userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
        message1 = senderName.encode('utf-8') + config.get("property", "content1") + " "\
                  +sendTitle.encode('utf-8') + " "+config.get("property", "content2")       
        custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1)
        recordId = createPushRecord(3,1,customTitle,message1,currentPushTime,1002,json.dumps(custom_content),currentCommunityId,1002)      
        custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,recordId)
        
        apiKey = config.get("SDK", "apiKey")
        secretKey = config.get("SDK", "secretKey")
        tagName = tagSuffix+str(currentCommunityId)
        tagName1 = tagSuffix1+str(currentCommunityId)
        _jpush = jpush.JPush(apiKey,secretKey) 
        pushExtra = custom_content
        push = _jpush.create_push()
        push.audience = jpush.all_
        push.audience = jpush.audience(
                    jpush.tag(tagName),
                    jpush.tag(tagName1),
                )
        push.notification = jpush.notification(
                    android=jpush.android(message1,customTitle,None,pushExtra)
                )
        push.options = {"time_to_live":3600, "sendno":9527, "apns_production":True}
        push.platform = jpush.all_
        try:
            push.send()
        except:
            pass
        data['flag'] = "ok"
        data['topic_id'] = topicId
        data['user_id'] = user_id
        data['error'] = json.dumps(ret)
        return HttpResponse(json.dumps(data), content_type="application/json")
    except:
        pass
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return HttpResponse(json.dumps(data), content_type="application/json")

@api_view(['GET','POST'])
def getNotice(request):  
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        categoryType   = request.POST.get('category_type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        categoryType   = request.GET.get('category_type', None)
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(userId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(userId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
        
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    if targetId == 0:
        topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:6]
    else:
        topicNum = int(count)
        if topicNum==1:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
#         commentNum = topicQuerySet[i].comment_num
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        communityId = topicQuerySet[i].sender_community_id
        objectType = topicQuerySet[i].object_data_id
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            praiseObj = Praise.objects.get(topic=long(curTopciId),user=long(userId))
            praiseType = 1 # his praise
        except:
            praiseType = 0 # no praise
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        if objectType == 1:
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag)
            ListActivity.append(activityDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                comm_senderAddr = commQuerySet[i].senderAddress
                comm_senderFamilyId = commQuerySet[i].senderFamilyId
                comm_senderLevel = commQuerySet[i].senderLevel
                comm_commId = commQuerySet[i].getCommentId()
                comm_senderNcRoleId = commQuerySet[i].senderNcRoleId
                comm_sendTime = commQuerySet[i].sendTime
                comm_contentType = commQuerySet[i].contentType
                comm_senderId = commQuerySet[i].senderId
                comm_displayName = commQuerySet[i].displayName
                comm_content = commQuerySet[i].content
                comm_senderName = commQuerySet[i].senderName
                comm_topicId = commQuerySet[i].topic.getTopicId()
                comm_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(comm_senderAddr,comm_senderFamilyId,comm_senderLevel,comm_commId,comm_senderNcRoleId,comm_sendTime,\
                                              comm_contentType,comm_senderId,comm_displayName,comm_content,comm_senderName,comm_topicId,comm_senderAvatar)
                ListComment.append(commentDicts)

        topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                         cacheKey,ListMediaFile,ListComment,ListActivity)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    if ListMerged:
        topicString = json.dumps(ListMerged)
        return HttpResponse(topicString, content_type="application/json")
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")    

    
@api_view(['GET','POST'])
def setSuggest(request):  
    data = {}
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        title                          = request.POST.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#5
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        topicObj.sender_id             = request.POST.get('sender_id', None)
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.display_name          = request.POST.get('display_name', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        topicObj.sender_community_id   = request.POST.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    else:
        title                          = request.GET.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        topicObj.sender_id             = request.GET.get('sender_id', None)
        topicObj.sender_name           = request.GET.get('sender_name', None)
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return HttpResponse(json.dumps(data), content_type="application/json")


@api_view(['GET','POST'])
def getSuggest(request):  
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        categoryType   = request.POST.get('category_type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        categoryType   = request.GET.get('category_type', None)
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    if targetId == 0:
        topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:6]
    else:
        topicNum = int(count)
        if topicNum == 1:
            topicQuerySet = Topic.objects.filter(topic_id=long(targetId),sender_community_id=long(communityId),topic_category_type=categoryType)
        else:
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = topicQuerySet[i].comment_num
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        communityId = topicQuerySet[i].sender_community_id
        objectType = topicQuerySet[i].object_data_id
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            praiseObj = Praise.objects.get(topic=long(curTopciId),user=long(userId))
            praiseType = 1 # his praise
        except:
            praiseType = 0 # no praise
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        if objectType == 1:
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag)
            ListActivity.append(activityDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                comm_senderAddr = commQuerySet[i].senderAddress
                comm_senderFamilyId = commQuerySet[i].senderFamilyId
                comm_senderLevel = commQuerySet[i].senderLevel
                comm_commId = commQuerySet[i].getCommentId()
                comm_senderNcRoleId = commQuerySet[i].senderNcRoleId
                comm_sendTime = commQuerySet[i].sendTime
                comm_contentType = commQuerySet[i].contentType
                comm_senderId = commQuerySet[i].senderId
                comm_displayName = commQuerySet[i].displayName
                comm_content = commQuerySet[i].content
                comm_senderName = commQuerySet[i].senderName
                comm_topicId = commQuerySet[i].topic.getTopicId()
                comm_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(comm_senderAddr,comm_senderFamilyId,comm_senderLevel,comm_commId,comm_senderNcRoleId,comm_sendTime,\
                                              comm_contentType,comm_senderId,comm_displayName,comm_content,comm_senderName,comm_topicId,comm_senderAvatar)
                ListComment.append(commentDicts)

        topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                         cacheKey,ListMediaFile,ListComment,ListActivity)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    if ListMerged:
        topicString = json.dumps(ListMerged)
        return HttpResponse(topicString, content_type="application/json")
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")  
    
@api_view(['GET','POST'])      
def setPropertyInfo(request):

    if request.method == 'POST':
        title         = request.POST.get('name', None)
        phone         = request.POST.get('phone', None)
        address       = request.POST.get('address', None)
        office_hours  = request.POST.get('office_hours', None)
        community_id  = request.POST.get('community_id', None)
        sender_id     = request.POST.get('sender_id', None)
    else:
        title         = request.GET.get('name', None)
        phone         = request.GET.get('phone', None)
        address       = request.GET.get('address', None)
        office_hours  = request.GET.get('office_hours', None)
        community_id  = request.GET.get('community_id', None)
        sender_id     = request.GET.get('sender_id', None)
        
    propertyInfo = PropertyInfo.objects.create(name = title,phone = phone,address=address,\
                                       office_hours=office_hours,sender_id=sender_id,community_id=community_id)
    info_id = propertyInfo.getInfoId()
    response_data = {}
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])   
def getPropertyInfo(request):
    if request.method == 'POST':
        community_id  = request.POST.get('community_id', None)
    else:
        community_id  = request.GET.get('community_id', None)
        
    serviceQuerySet = PropertyInfo.objects.filter(community_id=community_id)
    if serviceQuerySet:
        title = serviceQuerySet[0].name
        phone = serviceQuerySet[0].phone
        address = serviceQuerySet[0].address
        office_hours = serviceQuerySet[0].office_hours
        infosDict = getInfosDict(title,phone,address,office_hours)
        return HttpResponse(json.dumps(infosDict), content_type="application/json")
    else: 
        response_data = {}
        response_data['flag'] = 'null'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def getInfosDict(title,phone,address,office_hours):
    dicts = {}
    dicts.setdefault('title', title)
    dicts.setdefault('flag', "ok")
    dicts.setdefault('phone', phone)
    dicts.setdefault('address', address)
    dicts.setdefault('office_hours', office_hours)
    return dicts  

@api_view(['GET','POST'])
def setProprtyRepair(request):  
    data = {}
    topicObj = None
    topicTime = None
    sendTitle = None
    senderName = None
    senderUserId = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        sendTitle                      = request.POST.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#4
        topicTime                      = request.POST.get('topic_time', None)
        topicObj.topic_time            = topicTime
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        senderUserId                   = request.POST.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.POST.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.display_name          = request.POST.get('display_name', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        topicObj.sender_community_id   = request.POST.get('sender_community_id', None)
        topicObj.process_status        = 1
        topicObj.process_data          = getProcessData(topicTime)
        topicObj.cache_key             = genCacheKey()
    else:
        sendTitle                      = request.GET.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)#4
        topicTime                      = request.GET.get('topic_time', None)
        topicObj.topic_time            = topicTime
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        senderUserId                   = request.GET.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.GET.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.process_status        = 1
        topicObj.process_data          = getProcessData(topicTime)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    # tag push
    try:     
        config = readIni()
        tagSuffix = config.get('property', "tagSuffix")
        pushTitle = config.get('property', "repairTitle")
        customTitle = config.get("property", "content3")
        pushContent = str(topicId).encode('utf-8') + ":" \
                     +str(user_id).encode('utf-8') + ":" \
                     +str(currentCommunityId).encode('utf-8')
        currentPushTime = long(time.time()*1000)
        userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
        message1 = senderName.encode('utf-8') + config.get("property", "content4") + " "\
                  +sendTitle.encode('utf-8') + " "+config.get("property", "content5")       
        custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1)
        recordId = createPushRecord(3,2,customTitle,message1,currentPushTime,1003,json.dumps(custom_content),currentCommunityId,1003)      
        custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,recordId)
        
        apiKey = config.get("SDK", "apiKey")
        secretKey = config.get("SDK", "secretKey")
        tagName = tagSuffix+str(currentCommunityId)
        _jpush = jpush.JPush(apiKey,secretKey) 
        pushExtra = custom_content
        push = _jpush.create_push()
        push.audience = jpush.all_
        push.audience = jpush.audience(
                    jpush.tag(tagName),
                )
        push.notification = jpush.notification(
                    android=jpush.android(message1,customTitle,None,pushExtra)
                )
        push.options = {"time_to_live":3600, "sendno":9527, "apns_production":True}
        push.platform = jpush.all_
        try:
            push.send()  
        except:
            pass
        data['flag'] = "ok"
        data['topic_id'] = topicId
        data['user_id'] = user_id
        return HttpResponse(json.dumps(data), content_type="application/json")
    except:
        pass
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return HttpResponse(json.dumps(data), content_type="application/json")  

@api_view(['GET','POST'])
def getProprtyRepair(request):  
    queryset= None
    userPhone = None
    praiseObj = None
    curTopciId = None
    curUserFamilyName = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    ListAdminInfo = []    

    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        categoryType   = request.POST.get('category_type', None)#4
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        categoryType   = request.GET.get('category_type', None)
    
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    try:
        queryset= Admin.objects.get(user_id=userId,community_id=communityId,admin_type = 4)
    except:
        queryset = None
    property_user_id = 1
    if queryset is not None:
        if targetId == 0:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:10]
        else:
            topicNum = int(count)
            if topicNum == 1:#get singal repair
                topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType)
            else:
                topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:topicNum] # <
    else:
        serviceQuerySet = Admin.objects.filter(community_id=communityId,admin_type = 4)
        serviceSize = serviceQuerySet.count()
        adminArray = []
        for i in range(0,serviceSize,1):
            adminArray.append(serviceQuerySet[i].user_id)
        userQuerySet = User.objects.filter(user_id__in=adminArray)
        adminArray = []   
        userSize = userQuerySet.count()
        for i in range(0,userSize,1):
            adminDicts = {}
            adminDicts['user_id']   = userQuerySet[i].user_id
            adminDicts['user_nick'] = userQuerySet[i].user_nick
            ListAdminInfo.append(adminDicts)
        if targetId == 0:
            topicQuerySet = Topic.objects.filter(sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:6]
        else:
            topicNum = int(count)
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            userPhone = User.objects.get(user_id=long(senderId)).user_phone_number
        except:
            userPhone = None
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = topicQuerySet[i].comment_num
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        communityId = topicQuerySet[i].sender_community_id
        objectType = topicQuerySet[i].object_data_id
        process_status = topicQuerySet[i].process_status
        process_data = topicQuerySet[i].process_data
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            curUserFamilyName = FamilyRecord.objects.get(family_id=senderFamilyId,user_id=senderId).family_name
        except:
            curUserFamilyName = None
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)

        topicDict = getTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,process_status,userPhone,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,curUserFamilyName,\
                                         cacheKey,ListMediaFile,process_data,ListAdminInfo)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    if ListMerged:
        topicString = json.dumps(ListMerged)
        ListAdminInfo = []
        return HttpResponse(topicString, content_type="application/json")
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")  
    
def getTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,process_status,phone,collectStatus,\
                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,communityId,\
                         commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,familyName,cacheKey,mediaDict,process_data,\
                         property_userId,systemTime):
    dicts = {}
    dicts.setdefault('systemTime',systemTime)
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('forumId',forumId)
    dicts.setdefault('forumName',forumName)
    dicts.setdefault('senderId',senderId)
    dicts.setdefault('senderName',senderName)
    dicts.setdefault('senderLevel',senderLevel)
    dicts.setdefault('senderPortrait',senderPortrait)
    dicts.setdefault('displayName',displayName)
    dicts.setdefault('process_status',process_status)
    dicts.setdefault('process_data',process_data)
    dicts.setdefault('property_userId',property_userId)
    dicts.setdefault('senderFamilyId',senderFamilyId)
    dicts.setdefault('senderFamilyAddr',senderFamilyAddr)
    dicts.setdefault('topicTime',topicTime)
    dicts.setdefault('topicTitle',topicTitle)
    dicts.setdefault('topicContent',topicContent)
    dicts.setdefault('topicCategoryType',topicCategoryType)
    dicts.setdefault('objectType',objectType)
    dicts.setdefault('communityId',communityId)
    dicts.setdefault('commentNum',commentNum)
    dicts.setdefault('likeNum',likeNum)
    dicts.setdefault('circleType',circleType)
    dicts.setdefault('visiableType',visiableType)
    dicts.setdefault('sendStatus',sendStatus)
    dicts.setdefault('viewNum',viewNum)
    dicts.setdefault('hotFlag',hotFlag)
    dicts.setdefault('cacheKey',cacheKey)
    dicts.setdefault('phone',phone)
    dicts.setdefault('familyName',familyName)
    dicts.setdefault('collectStatus',collectStatus)
    if mediaDict:
        dicts.setdefault('mediaFile',mediaDict)
    else:
        dicts.setdefault('mediaFile',None)
    return dicts

def getProcessData(topic_time):
    
    dicts = {}
    dicts.setdefault("1",topic_time.encode('utf-8'))
    dicts.setdefault("2","")
    dicts.setdefault("3","")
    return dicts

@api_view(['GET','POST'])
def setProcessStatus(request): 
    ListAdmin = [] 
    if request.method == 'POST':
        topic_id        = request.POST.get('topic_id', None)
        process_data    = request.POST.get('process_data', None)
        process_status  = request.POST.get('process_status', None)
        userId          = request.POST.get('user_id', None)
        communityId     = request.POST.get('community_id', None)
    else:
        topic_id        = request.GET.get('topic_id', None)
        process_data    = request.GET.get('process_data', None)
        process_status  = request.GET.get('process_status', None)
        userId          = request.GET.get('user_id', None)
        communityId     = request.GET.get('community_id', None)
    currentCommunityId = communityId
    topicQuerySet = Topic.objects.get(topic_id=topic_id)
    topicQuerySet.process_data = process_data
    topicQuerySet.process_status = process_status
    topicQuerySet.save()
    user_obj = User.objects.get(user_id=topicQuerySet.sender_id)
    senderUserId = user_obj.getTargetUid()# tui song gei shui
    config = readIni()
    pushTitle = config.get("property", "content3")
    customTitle = config.get("property", "noticeTitle")
    userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
    currentPushTime = long(time.time()*1000)
    if(process_status == str(2)):
        pushContent = config.get("property", "content6")+ topicQuerySet.topic_title.encode('utf-8') + config.get("property", "content7")
    else:   #process_status == 3
        pushContent = config.get("property", "content8")+ topicQuerySet.topic_title.encode('utf-8') + config.get("property", "content9")
    custom_content = getCustomDict(userId,currentPushTime,customTitle,userAvatar,topic_id,pushContent,pushTitle,pushContent)
    recordId = createPushRecord(3,2,pushTitle,pushContent,currentPushTime,long(senderUserId),json.dumps(custom_content),currentCommunityId,1004)      
    custom_content = getCustomDict(userId,currentPushTime,customTitle,userAvatar,topic_id,pushContent,pushTitle,pushContent,recordId)
   
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    aliasSuffix = config.get("SDK", "youlin")
    tagAlias = aliasSuffix+str(senderUserId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(tagAlias),
            )
    push.notification = jpush.notification(
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":True}
    push.platform = jpush.all_
    try:
        push.send()  
    except:
        pass
    data = {}
    data['flag'] = "ok"
    data['process_data'] = process_data
    data['process_status'] = process_status
    return HttpResponse(json.dumps(data), content_type="application/json") 

#创建物业公告
def SetNotice(request):  
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    data = {}
    sendTitle = None
    senderName = None
    senderUserId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        sendTitle                      = request.POST.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#3
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        senderUserId                   = request.POST.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.POST.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        curComId                       = request.POST.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        try:
            curUserName = User.objects.get(user_id=long(senderUserId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
    else:
        sendTitle                      = request.GET.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        senderUserId                   = request.GET.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.GET.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    config = readIni()
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    pushTitle = config.get("property", "title")
    customTitle = config.get("property", "content0")
    tagSuffix = config.get('topic', "tagSuffix")
    tagSuffix1 = config.get('report', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(user_id).encode('utf-8') + ":" \
                 +str(currentCommunityId).encode('utf-8')
    currentPushTime = long(time.time()*1000)
    userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
    message1 = senderName.encode('utf-8') + config.get("property", "content1") + " "\
              +sendTitle.encode('utf-8') + " "+config.get("property", "content2")       
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,curComId)
    recordId = createPushRecord(3,1,customTitle,message1,currentPushTime,1002,json.dumps(custom_content),currentCommunityId,1002)      
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,curComId,recordId)
    
    AsyncSetNotice.delay(apiKey, secretKey, currentCommunityId, custom_content, tagSuffix, tagSuffix1, message1, customTitle ,topicId,user_id)
 #   AsyncNoticePush.delay(topicId,user_id,currentCommunityId)
    
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return data

#获取物业公告
def GetNotice(request):  
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        categoryType   = request.POST.get('category_type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        categoryType   = request.GET.get('category_type', None)
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(userId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(userId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    if count is None:# pull down
        if targetId == 0:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType,topic_id__gt=targetId).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if topicNum==1:#用户更新
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
#         commentNum = topicQuerySet[i].comment_num
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            curUserName = User.objects.get(user_id = long(senderId)).user_nick
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        
        objectType = topicQuerySet[i].object_data_id
        object_data = topicQuerySet[i].object_type
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            praiseObj = Praise.objects.get(topic=long(curTopciId),user=long(userId))
            praiseType = 1 # his praise
        except:
            praiseType = 0 # no praise
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        if objectType == 1:
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag)
            ListActivity.append(activityDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                comm_senderAddr = commQuerySet[i].senderAddress
                comm_senderFamilyId = commQuerySet[i].senderFamilyId
                comm_senderLevel = commQuerySet[i].senderLevel
                comm_commId = commQuerySet[i].getCommentId()
                comm_senderNcRoleId = commQuerySet[i].senderNcRoleId
                comm_sendTime = commQuerySet[i].sendTime
                comm_contentType = commQuerySet[i].contentType
                comm_senderId = commQuerySet[i].senderId
                comm_displayName = commQuerySet[i].displayName
                comm_content = commQuerySet[i].content
                comm_senderName = commQuerySet[i].senderName
                comm_topicId = commQuerySet[i].topic.getTopicId()
                comm_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(comm_senderAddr,comm_senderFamilyId,comm_senderLevel,comm_commId,comm_senderNcRoleId,comm_sendTime,\
                                              comm_contentType,comm_senderId,comm_displayName,comm_content,comm_senderName,comm_topicId,comm_senderAvatar)
                ListComment.append(commentDicts)
        curSystemTime = long(time.time()*1000)
        topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                         cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    if ListMerged:
        return ListMerged
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return response_data

#创建物业建议
def SetSuggest(request):  
    data = {}
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        title                          = request.POST.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#5
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        senderUserId                   = request.POST.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role        = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        curComId                       = request.POST.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        try:
            curUserName = User.objects.get(user_id=long(senderUserId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
    else:
        title                          = request.GET.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        topicObj.sender_id             = request.GET.get('sender_id', None)
        topicObj.sender_name           = request.GET.get('sender_name', None)
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role        = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    
    AsyncSuggestPush.delay(topicId,user_id,currentCommunityId)
    
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return data

#获取物业建议
def GetSuggest(request):  
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        categoryType   = request.POST.get('category_type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        categoryType   = request.GET.get('category_type', None)
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(userId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(userId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)    
    if count is None:# pull down
        if targetId == 0:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType,topic_id__gt=targetId).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if topicNum==1:#用户更新
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <    
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
#         commentNum = topicQuerySet[i].comment_num
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            curUserName = User.objects.get(user_id = long(senderId)).user_nick
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        
        objectType = topicQuerySet[i].object_data_id
        object_data = topicQuerySet[i].object_type
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            praiseObj = Praise.objects.get(topic=long(curTopciId),user=long(userId))
            praiseType = 1 # his praise
        except:
            praiseType = 0 # no praise
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        if objectType == 1:
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag)
            ListActivity.append(activityDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                comm_senderAddr = commQuerySet[i].senderAddress
                comm_senderFamilyId = commQuerySet[i].senderFamilyId
                comm_senderLevel = commQuerySet[i].senderLevel
                comm_commId = commQuerySet[i].getCommentId()
                comm_senderNcRoleId = commQuerySet[i].senderNcRoleId
                comm_sendTime = commQuerySet[i].sendTime
                comm_contentType = commQuerySet[i].contentType
                comm_senderId = commQuerySet[i].senderId
                comm_displayName = commQuerySet[i].displayName
                comm_content = commQuerySet[i].content
                comm_senderName = commQuerySet[i].senderName
                comm_topicId = commQuerySet[i].topic.getTopicId()
                comm_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(comm_senderAddr,comm_senderFamilyId,comm_senderLevel,comm_commId,comm_senderNcRoleId,comm_sendTime,\
                                              comm_contentType,comm_senderId,comm_displayName,comm_content,comm_senderName,comm_topicId,comm_senderAvatar)
                ListComment.append(commentDicts)
        curSystemTime = long(time.time()*1000)
        topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                         cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    if ListMerged:
        return ListMerged
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return response_data

#获取物业信息
def GetPropertyInfo(request):
    if request.method == 'POST':
        community_id  = request.POST.get('community_id', None)
    else:
        community_id  = request.GET.get('community_id', None)
        
    serviceQuerySet = PropertyInfo.objects.filter(community_id=community_id)
    if serviceQuerySet:
        title = serviceQuerySet[0].name
        phone = serviceQuerySet[0].phone
        address = serviceQuerySet[0].address
        office_hours = serviceQuerySet[0].office_hours
        infosDict = getInfosDict(title,phone,address,office_hours)
        return infosDict
    else: 
        response_data = {}
        response_data['flag'] = 'none'
        return response_data
    
#设置物业报修
def SetProprtyRepair(request):  
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    data = {}
    topicObj = None
    topicTime = None
    sendTitle = None
    senderName = None
    senderUserId = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        sendTitle                      = request.POST.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)#4
        topicTime                      = request.POST.get('topic_time', None)
        topicObj.topic_time            = topicTime
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        senderUserId                   = request.POST.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.POST.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.sender_nc_role        = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        curComId                       = request.POST.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.process_status        = 1
        topicObj.process_data          = getProcessData(topicTime)
        topicObj.cache_key             = genCacheKey()
        try:
            curUserName = User.objects.get(user_id=long(senderUserId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
    else:
        sendTitle                      = request.GET.get('topic_title', None)
        title                          = sendTitle
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.GET.get('topic_content', None)
        topicObj.topic_category_type   = request.GET.get('topic_category_type', None)#4
        topicTime                      = request.GET.get('topic_time', None)
        topicObj.topic_time            = topicTime
        topicObj.forum_id              = request.GET.get('forum_id', None)
        topicObj.forum_name            = request.GET.get('forum_name', None)
        senderUserId                   = request.GET.get('sender_id', None)
        topicObj.sender_id             = senderUserId
        senderName                     = request.GET.get('sender_name', None)
        topicObj.sender_name           = senderName
        topicObj.sender_lever          = request.GET.get('sender_lever', None)
        topicObj.sender_portrait       = request.GET.get('sender_portrait', None)
        topicObj.sender_nc_role       = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        topicObj.sender_community_id   = request.GET.get('sender_community_id', None)
        topicObj.process_status        = 1
        topicObj.process_data          = getProcessData(topicTime)
        topicObj.cache_key             = genCacheKey()
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    # tag push    
    config = readIni()
    tagSuffix = config.get('property', "tagSuffix")
    pushTitle = config.get('property', "repairTitle")
    customTitle = config.get("property", "content3")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(user_id).encode('utf-8') + ":" \
                 +str(currentCommunityId).encode('utf-8')
    currentPushTime = long(time.time()*1000)
    userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
    message1 = senderName.encode('utf-8') + config.get("property", "content4") + " "\
              +sendTitle.encode('utf-8') + " "+config.get("property", "content5")       
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,curComId)
    recordId = createPushRecord(3,2,customTitle,message1,currentPushTime,1003,json.dumps(custom_content),currentCommunityId,1003)      
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,customTitle,message1,curComId,recordId)
    
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    
    AsyncSetProprtyRepair.delay(apiKey, secretKey, currentCommunityId, custom_content, message1, customTitle, tagSuffix)

    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return data
    
#获取报修状态(修改过。。。。。。。。。。。。。。。。。。。。)
def GetProprtyRepair(request):  
    queryset= None
    userPhone = None
    praiseObj = None
    curTopciId = None
    curUserFamilyName = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    ListAdminInfo = []    

    if request.method == 'POST':
        userId       = request.POST.get('user_id', None)
        communityId  = request.POST.get('community_id', None)
        topic_id     = request.POST.get('topic_id', None)
        count        = request.POST.get('count', None)
        categoryType = request.POST.get('category_type', None)#4
        processType  = request.POST.get('process_type', None)# 1 2 3
    else:
        userId       = request.GET.get('user_id', None)
        communityId  = request.GET.get('community_id', None)
        topic_id     = request.GET.get('topic_id', None)
        count        = request.GET.get('count', None)
        categoryType = request.GET.get('category_type', None)
        processType  = request.GET.get('process_type', None)
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(userId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(userId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    if processType is None:
        processType = 0
    try:
        queryset= Admin.objects.get(user_id=userId,community_id=communityId,admin_type = 4)
    except:
        queryset = None
    property_user_id = 1
    
    if queryset is not None:
        if targetId == 0:
            if int(processType)==3:
                topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType,process_status=processType).exclude(sender_id__in=blackList).exclude(delete_type=4).order_by('-topic_id')[:10]
            else:
                topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(process_status=3).order_by('-topic_id')[:10]
        else:
            topicNum = int(count)
            if topicNum == 1:#get singal repair
                if int(processType)==3:
                    topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType,process_status=processType).exclude(sender_id__in=blackList).exclude(delete_type=4)
                else:
                    topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(process_status=3)
            else:
                if int(processType)==3:
                    topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType,process_status=processType).exclude(sender_id__in=blackList).exclude(delete_type=4).order_by('-topic_id')[:topicNum] # <
                else:
                    topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_category_type=categoryType).exclude(sender_id__in=blackList).exclude(process_status=3).order_by('-topic_id')[:topicNum] # <
    else:
        serviceQuerySet = Admin.objects.filter(community_id=communityId,admin_type = 4)
        serviceSize = serviceQuerySet.count()
        adminArray = []
        for i in range(0,serviceSize,1):
            adminArray.append(serviceQuerySet[i].user_id)
        userQuerySet = User.objects.filter(user_id__in=adminArray)
        adminArray = []   
        userSize = userQuerySet.count()
        for i in range(0,userSize,1):
            adminDicts = {}
            adminDicts['user_id']   = userQuerySet[i].user_id
            adminDicts['user_nick'] = userQuerySet[i].user_nick
            ListAdminInfo.append(adminDicts)
        if targetId == 0:
            if int(processType)==3:
                topicQuerySet = Topic.objects.filter(sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType,process_status=processType).exclude(sender_id__in=blackList).order_by('-topic_id')[:6]
            else:
                topicQuerySet = Topic.objects.filter(sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).exclude(process_status=3).exclude(sender_id__in=blackList).order_by('-topic_id')[:6]
        else:
            topicNum = int(count)
            if int(processType)==3:
                topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType,process_status=processType).exclude(sender_id__in=blackList).order_by('-topic_id')[:topicNum] # <
            else:    
                topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).exclude(process_status=3).exclude(sender_id__in=blackList).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            userPhone = User.objects.get(user_id=long(senderId)).user_phone_number
        except:
            userPhone = None
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = topicQuerySet[i].comment_num
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            curUserName = User.objects.get(user_id = long(senderId)).user_nick
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        objectType = topicQuerySet[i].object_data_id
        object_data = topicQuerySet[i].object_type
        colStatus = 0
        process_status = topicQuerySet[i].process_status
        process_data = topicQuerySet[i].process_data
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        try:
            curUserFamilyName = FamilyRecord.objects.get(family_id=senderFamilyId,user_id=senderId).family_name
        except:
            curUserFamilyName = None
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicDict = getTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,process_status,userPhone,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,curUserFamilyName,\
                                         cacheKey,ListMediaFile,process_data,ListAdminInfo,curSystemTime)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    if ListMerged:
        return ListMerged
    else:
        response_data = {}
        response_data['flag'] = 'no'
        if queryset is None:#普通用户
            repairCount = Topic.objects.filter(sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).count()
        else:#物业管理
            repairCount = Topic.objects.filter(sender_id=long(userId),sender_community_id=long(communityId),topic_category_type=categoryType).exclude(delete_type=4).count()
        if int(repairCount)==0:
            response_data['empty'] = 'no' #no表示已完成 未完成 都没有
        else:
            response_data['empty'] = 'ok'
        return response_data
    
#设置报修状态    
def SetProcessStatus(request): 
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    ListAdmin = [] 
    if request.method == 'POST':
        topic_id        = request.POST.get('topic_id', None)
        process_data    = request.POST.get('process_data', None)
        process_status  = request.POST.get('process_status', None)
        userId          = request.POST.get('user_id', None)
        communityId     = request.POST.get('community_id', None)
    else:
        topic_id        = request.GET.get('topic_id', None)
        process_data    = request.GET.get('process_data', None)
        process_status  = request.GET.get('process_status', None)
        userId          = request.GET.get('user_id', None)
        communityId     = request.GET.get('community_id', None)
    currentCommunityId = communityId
    topicQuerySet = Topic.objects.get(topic_id=topic_id)
    topicQuerySet.process_data = process_data
    topicQuerySet.process_status = process_status
    topicQuerySet.save()
    user_obj = User.objects.get(user_id=topicQuerySet.sender_id)
    senderUserId = user_obj.getTargetUid()# tui song gei shui
    config = readIni()
    pushTitle = config.get("property", "content3")
    customTitle = config.get("property", "noticeTitle")
    userAvatar = settings.RES_URL+'res/default/avatars/default-property.png'
    currentPushTime = long(time.time()*1000)
    if(process_status == str(2)):
        pushContent = config.get("property", "content6")+ topicQuerySet.topic_title.encode('utf-8') + config.get("property", "content7")
    else:   #process_status == 3
        pushContent = config.get("property", "content8")+ topicQuerySet.topic_title.encode('utf-8') + config.get("property", "content9")
    custom_content = getCustomDictWithRepair(userId,currentPushTime,customTitle,userAvatar,topic_id,pushContent,pushTitle,pushContent,process_status,communityId)
    recordId = createPushRecord(3,2,pushTitle,pushContent,currentPushTime,long(senderUserId),json.dumps(custom_content),currentCommunityId,1004)      
    custom_content = getCustomDictWithRepair(userId,currentPushTime,customTitle,userAvatar,topic_id,pushContent,pushTitle,pushContent,process_status,communityId,recordId)
   
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    aliasSuffix = config.get("SDK", "youlin")
    
    AsyncSetProcessStatus.delay(apiKey, secretKey, aliasSuffix, senderUserId, custom_content, pushContent, pushTitle)
    
    data = {}
    data['flag'] = "ok"
    data['process_data'] = process_data
    data['process_status'] = process_status
    return data

