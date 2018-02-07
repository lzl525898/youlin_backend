# coding:utf-8
from django.http import HttpResponse
from users.models import User,FamilyRecord,BlackList,Admin,Remarks
from community.models import Comment, Topic, Media_files, Activity, Praise, EnrollActivity, ReportTopic,CollectionTopic,SecondHand,SayHello,FavouriteList
from rest_framework.decorators import api_view
from django.core import serializers
from django.conf import settings
from PIL import Image,ImageDraw,ImageChops,ImageEnhance
# import ImageDraw
# import ImageChops
# import ImageEnhance
import re
import sys
import os
import json
import time
import random
import jpush as jpush
from push.views import createPushRecord,readIni
from push.sample import pushMsgToTag,pushMsgToSingleDevice
from django.db.models import Q
from web.models import News,NewsPush
from addrinfo.models import Community
from community.tasks import *
from core.settings import SHARE_NEWS
from pip.utils import display_path

def imgGenName(filename):
    fName = time.strftime('%m%d%M%S')+str(random.randint(1000,9999))+filename[filename.rfind('.'):]
    return fName

def imgGenPath(user_id, topic_id):
    userDir = settings.MEDIA_ROOT+'youlin/res/'+str(user_id)+'/topic/' + str(topic_id) + '/'
    if os.path.exists(userDir):
        pass
    else:
        try:
            os.makedirs(userDir, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                pass
            else:raise    
    return userDir

#图片缩放
def makeThumbnail(userDir, bigImg, smallImg, percent, suffix = None):
    filePath = userDir + bigImg
    im = Image.open(filePath)
    mode = im.mode
    if mode not in ('L', 'RGB'):
        im = im.convert('RGB')
    width, height = im.size
    if width>300:
        nwidth = 300
        nheight = int(height * 300/width)
        size = (nwidth, nheight)
        im.thumbnail(size, Image.ANTIALIAS) 
    if suffix:
        im.save(userDir+smallImg+suffix)
    else:
        im.save(userDir+smallImg)

#圆形图片
def makeCircleAvatr(avatr_path,path):
    ima = Image.open(path).convert("RGBA")
#     mode = ima.mode
#     if mode not in ('L', 'RGB'):
#         ima = ima.convert('RGB')
    size = ima.size
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        ima = ima.resize((r2, r2), Image.ANTIALIAS)
    imb = Image.new('RGBA', (r2, r2),(255,255,255,0))
    R,G,B,A = imb.split()
    pima = ima.load()
    pimb = imb.load()
    r = float(r2/2) #圆心横坐标
    for i in range(r2):
        for j in range(r2):
            lx = abs(i-r+0.5) #到圆心距离的横坐标
            ly = abs(j-r+0.5)#到圆心距离的纵坐标
            l  = pow(lx,2) + pow(ly,2)
            if l <= pow(r, 2):
                pimb[i,j] = pima[i,j]
    draw = ImageDraw.Draw(imb) 
#     width,height = imb.size 
#     draw.arc((0,0,width-1,height-1),0,360,fill=(255,186,2))
#     contrast = ImageEnhance.Contrast(imb) #对比度增强 
#     contrast_img = contrast.enhance(3.0)  
#     contrast_img.save(avatr_path) 
#     cropped = autoCrop(imb)
#     cropped.save(avatr_path)
    imb.save(avatr_path)

# #圆形图片
# def makeCircleAvatr(avatr_path,path):
#     ima = Image.open(path).convert("RGBA")
# #     mode = ima.mode
# #     if mode not in ('L', 'RGB'):
# #         ima = ima.convert('RGB')
#     size = ima.size
#     # 因为是要圆形，所以需要正方形的图片
#     r2 = min(size[0], size[1])
#     if size[0] != size[1]:
#         ima = ima.resize((r2, r2), Image.ANTIALIAS)
#     imb = Image.new('RGBA', (r2, r2),(255,255,255,0))
#     R,G,B,A = imb.split()
#     pima = ima.load()
#     pimb = imb.load()
#     r = float(r2/2) #圆心横坐标
#     for i in range(r2):
#         for j in range(r2):
#             lx = abs(i-r+0.5) #到圆心距离的横坐标
#             ly = abs(j-r+0.5)#到圆心距离的纵坐标
#             l  = pow(lx,2) + pow(ly,2)
#             if l <= pow(r, 2):
#                 pimb[i,j] = pima[i,j]
#     circle = Image.new('L', (r2, r2), 0)
#     draw = ImageDraw.Draw(circle)
#     draw.ellipse((0, 0, r2, r2), fill=255)
#     alpha = Image.new('L', (r2, r2), 255)
#     alpha.paste(circle, (0, 0))
#     imb.putalpha(alpha)
#     imb.save(avatr_path)
#     draw = ImageDraw.Draw(imb) 
#     width,height = imb.size 
#     draw.arc((0,0,width-1,height-1),0,360,fill=(255,186,2))
#     contrast = ImageEnhance.Contrast(imb) #对比度增强 
#     contrast_img = contrast.enhance(3.0)  
#     contrast_img.save(avatr_path) 
#     cropped = autoCrop(imb)
#     cropped.save(avatr_path)
#     imb.save(avatr_path)

def autoCrop(image,backgroundColor=None):
    def mostPopularEdgeColor(image):
        im = image
        if im.mode != 'RGB':
            im = image.convert("RGB")
        width,height = im.size
        left   = im.crop((0,1,1,height-1))
        right  = im.crop((width-1,1,width,height-1))
        top    = im.crop((0,0,width,1))
        bottom = im.crop((0,height-1,width,height))
        pixels = left.tostring() + right.tostring() + top.tostring() + bottom.tostring()
        counts = {}
        for i in range(0,len(pixels),3):
            RGB = pixels[i]+pixels[i+1]+pixels[i+2]
            if RGB in counts:
                counts[RGB] += 1
            else:
                counts[RGB] = 1  
        mostPopularColor = sorted([(count,rgba) for (rgba,count) in counts.items()],reverse=True)[0][1]
        return ord(mostPopularColor[0]),ord(mostPopularColor[1]),ord(mostPopularColor[2])
    bbox = None
    if 'A' in image.getbands():
        bbox = image.split()[list(image.getbands()).index('A')].getbbox()
    elif image.mode=='RGB':
        if not backgroundColor:
            backgroundColor = mostPopularEdgeColor(image)
        bg = Image.new("RGB", image.size, backgroundColor)
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
    else:
        raise NotImplementedError, "Sorry, this function is not implemented yet for images in mode '%s'." % image.mode
    if bbox:
        image = image.crop(bbox)  
    return image


def genCacheKey():
    cacheKey = int(time.time()) + int(random.randint(100,999))
    return cacheKey

@api_view(['GET','POST'])
def updateTopic(request):
    data = {}
    curComId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        topicId                        = request.POST.get('topic_id', None)
        topicObj                       = Topic.objects.get(topic_id=long(topicId))
        topicObj.topic_title           = request.POST.get('topic_title', None)
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)
        topicObj.topic_time            = request.POST.get('topic_time', None)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        topicObj.sender_id             = request.POST.get('sender_id', None)
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.collect_status        = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.display_name          = request.POST.get('display_name', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        curComId                       = request.POST.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        if topicObj.object_data_id == '1':
            activityId = updateActivity(topicId, topicObj, request)
    topicObj.save()
    Media_files.objects.filter(topic_id=long(topicId),comment_id=0).delete()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
    # tag push
    try:        
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
        push.options = {"time_to_live":86400, "sendno":9527, "apns_production":True}
        push.platform = jpush.all_
        try:       
            push.send() 
        except:
            pass
        data['flag']         = "ok"
        data['topic_id']     = topicId
        data['user_id']      = user_id
        data['community_id'] = curComId
        data['status'] = "push"
        return HttpResponse(json.dumps(data), content_type="application/json")
    except:
        pass
    data['flag']         = "ok"
    data['topic_id']     = topicId
    data['community_id'] = curComId
    data['user_id']      = user_id
    return HttpResponse(json.dumps(data), content_type="application/json")

@api_view(['GET','POST'])
def postNewTopic(request):
    data = {}
    curComId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        title                          = request.POST.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        topicObj.sender_id             = request.POST.get('sender_id', None)
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.collect_status        = request.POST.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.POST.get('sender_family_id', None)
        topicObj.sender_family_address = request.POST.get('sender_family_address', None)
        topicObj.display_name          = request.POST.get('display_name', None)
        topicObj.object_data_id        = request.POST.get('object_data_id', None)
        topicObj.circle_type           = request.POST.get('circle_type', None)
        topicObj.send_status           = request.POST.get('send_status', None)
        topicObj.sender_city_id        = request.POST.get('sender_city_id', None)
        curComId                       = request.POST.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        if topicObj.object_data_id == '1':
            activityId = createActivity(topicId, topicObj, request)
        elif topicObj.object_data_id == '3':
            newsId = request.POST.get('new_id', None)
            topicObj.object_type = newsId
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
        topicObj.collect_status        = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        curComId                       = request.GET.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        if topicObj.object_data_id == '1':
            activityId = createActivity(topicId, topicObj, request)
        elif topicObj.object_data_id == '3':
            newsId = request.GET.get('new_id', None)
            try:
                newsObj = News.objects.get(new_id = newsId)
            except:
                pass
            servhost = request.get_host()
            new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+newsId
            pic_url = 'https://'+servhost+newsObj.new_small_pic
            newDict = getNewsDict(newsObj,pic_url,new_url)
            topicObj.object_type = json.dumps(newDict)
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()  
    # tag push
    try:        
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
                    None
                )
        push.options = {"time_to_live":0, "sendno":9527, "apns_production":True}
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

def getSecondDict(secondObj,communityLng,communityLag):
    dicts = {}
    dicts.setdefault('_id', secondObj.getSecondHandId())
    dicts.setdefault('topic_id', secondObj.topic.getTopicId())
    dicts.setdefault('startTime', secondObj.startTime)
    dicts.setdefault('endTime', secondObj.endTime)
    dicts.setdefault('label', secondObj.label)
    dicts.setdefault('price', secondObj.price)
    dicts.setdefault('tradeStatus', secondObj.tradeStatus)
    dicts.setdefault('oldornew', secondObj.oldornew)
    dicts.setdefault('communityLng', communityLng)
    dicts.setdefault('communityLag', communityLag)
    return dicts

def getNewsDict(newsObj,pic_url,new_url,communityLng=None,communityLag=None,subObj=None):
    dicts = {}
    dicts.setdefault('new_title', newsObj.new_title)
    dicts.setdefault('new_id', newsObj.new_id)
    dicts.setdefault('new_add_time', newsObj.new_add_time)
    dicts.setdefault('new_small_pic', pic_url)
    dicts.setdefault('new_url', new_url)
    if communityLng is not None:
        dicts.setdefault('communityLng', communityLng)
    if communityLag is not None:
        dicts.setdefault('communityLag', communityLag)
    if subObj is not None:
        from core.settings import HOST_IP
        dicts.setdefault('sub_url', HOST_IP + subObj.s_url)
        dicts.setdefault('sub_name', subObj.s_name)
    return dicts

def updateActivity(topicId, topicObj,request):
    data = request.POST.copy()
    try:
        activityObj = Activity.objects.get(topic_id = long(topicId))
        activityObj.startTime = data['startTime']
        activityObj.endTime = data['endTime']
        activityObj.location = data['location']
        activityObj.content = data['content']
        activityObj.tag = '无'
        activityObj.enrollUserCount = 0
        activityObj.enrollNeCount   = 0
        activityObj.processStatus   = 0
        activityObj.save()
        activityId = activityObj.getActivityId()
    except:
        return None
    
def createActivity(topicId, topicObj,request):
    #pureContent = request.POST.get('content', None)  #纯活动内容 不包含时间
    data = request.POST.copy()
    activity = Activity.objects.create(topic_id = topicId,startTime= data['startTime'],endTime=data['endTime'],\
                                       location=data['location'],tag='无',enrollUserCount=0,\
                                       enrollNeCount=0,processStatus=0,content=data['content'])
    activityId = activity.getActivityId()
    #activityDict = getActivityDict(activityId,topicId,data)
    
    return activityId

def createSecondHandle(topicId,request):
    strPrice = request.POST.get('price', None)
    if strPrice is None:
        strPrice = 0
    oldOrnew = request.POST.get('oldornew', None)
    if oldOrnew is None:# 1-10
        oldOrnew = 0
    categoryType = request.POST.get('goodstype', None)
    if categoryType is None:
        categoryType = 0#u'其他'
    elif categoryType.encode('utf-8')=='其他':
        categoryType = 0
    elif categoryType.encode('utf-8')=='手机':
        categoryType = 1
    elif categoryType.encode('utf-8')=='数码':
        categoryType = 2
    elif categoryType.encode('utf-8')=='家用电器':
        categoryType = 3
    elif categoryType.encode('utf-8')=='代步工具':
        categoryType = 4
    elif categoryType.encode('utf-8')=='母婴用品':
        categoryType = 5
    elif categoryType.encode('utf-8')=='服装鞋帽':
        categoryType = 6
    elif categoryType.encode('utf-8')=='家具家居':
        categoryType = 7
    elif categoryType.encode('utf-8')=='电脑':
        categoryType = 8
    elif categoryType.encode('utf-8')=='全部':
        categoryType = -1
    curTime = long(time.time()*1000)
    SecondHandObj = SecondHand.objects.create(topic_id = topicId,price=strPrice,oldornew=oldOrnew,\
                                               startTime=curTime,tradeStatus=1,label=categoryType)
    secondHandleId = SecondHandObj.getSecondHandId()
    return secondHandleId

def getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag):
    dicts = {}
    dicts.setdefault('activityId',activityObj.activity_id) #活动id
    dicts.setdefault('topicId',activityObj.topic_id)   #话题id
    dicts.setdefault('startTime',activityObj.startTime) #起始时间
    dicts.setdefault('endTime',activityObj.endTime) #结束时间
    dicts.setdefault('location',activityObj.location) #活动地址
    dicts.setdefault('tag',activityObj.tag)
    dicts.setdefault('signFlag',activityObj.signFlag)
    dicts.setdefault('confirmFlag',activityObj.confirmFlag)
    dicts.setdefault('lotteryFlag',activityObj.lotteryFlag)
    dicts.setdefault('enrollUserCount',activityObj.enrollUserCount) #大人
    dicts.setdefault('enrollNeCount',activityObj.enrollNeCount) #小孩
    dicts.setdefault('checkinUserCount',activityObj.checkinUserCount)
    dicts.setdefault('checkinNeCount',activityObj.checkinNeCount)
    dicts.setdefault('rosterStatus',activityObj.rosterStatus)
    dicts.setdefault('processStatus',activityObj.processStatus)
    dicts.setdefault('ncId',activityObj.ncId)
    dicts.setdefault('longitude',activityObj.longitude)
    dicts.setdefault('latitude',activityObj.latitude)
    dicts.setdefault('enrollTotal',total) #报名总数
    dicts.setdefault('enrollFlag',enrollFlag) # false 表示当前用户
    dicts.setdefault('communityLng',communityLng)
    dicts.setdefault('communityLag',communityLag)
    dicts.setdefault('content',activityObj.content)
    return dicts

def genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,collectStatus,\
                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,communityId,\
                         commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,cacheKey,mediaDict,commDict,activityDict,systemTime,\
                         deleteType=None):
    dicts = {}
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('forumId',forumId)
    dicts.setdefault('forumName',forumName)
    dicts.setdefault('senderId',senderId)
    dicts.setdefault('senderName',senderName)
    dicts.setdefault('senderLevel',senderLevel)
    dicts.setdefault('senderPortrait',senderPortrait)
    dicts.setdefault('displayName',displayName)
    dicts.setdefault('praiseType',praiseType)
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
    dicts.setdefault('collectStatus',collectStatus)
    dicts.setdefault('systemTime',systemTime)
    if mediaDict:
        dicts.setdefault('mediaFile',mediaDict)
    else:
        dicts.setdefault('mediaFile',None)
    if commDict:
        dicts.setdefault('comments',commDict)
    else:
        dicts.setdefault('comments',None)
    if activityDict:
        dicts.setdefault('objectData',activityDict)
    else:
        dicts.setdefault('objectData',None)
    if deleteType:
        dicts.setdefault('deleteType',deleteType)
    else:
        dicts.setdefault('deleteType',None)
    return dicts

def genMediaFilesDict(resId,resPath,contentType):
    dicts = {}
    dicts.setdefault('resId', resId)
    dicts.setdefault('resPath', resPath)
    dicts.setdefault('contentType', contentType)
    return dicts

def genImageFilesDict(resId,resPath,contentType):
    dicts = {}
    dicts.setdefault('resId', resId)
    dicts.setdefault('resPath', resPath)
    dicts.setdefault('voicePath', None)
    dicts.setdefault('contentType', contentType)
    return dicts

def genVideoFilesDict(resId,resPath,contentType,videoLength):
    dicts = {}
    dicts.setdefault('resId', resId)
    dicts.setdefault('resPath', None)
    dicts.setdefault('voicePath', resPath)
    dicts.setdefault('contentType', contentType)
    dicts.setdefault('videoLength', videoLength)
    return dicts

def genCommentDict(senderAddress,senderFamilyId,senderLevel,commId,senderNcRoleId,sendTime,\
                   contentType,senderId,displayName,content,senderName,topicId,senderAvatar):
    dicts = {}
    dicts.setdefault('senderAddress', senderAddress)
    dicts.setdefault('senderFamilyId', senderFamilyId)
    dicts.setdefault('senderLevel', senderLevel)
    dicts.setdefault('commId', commId)
    dicts.setdefault('senderNcRoleId', senderNcRoleId)
    dicts.setdefault('sendTime', sendTime)
    dicts.setdefault('contentType', contentType)
    dicts.setdefault('senderId', senderId)
    dicts.setdefault('displayName', displayName)
    dicts.setdefault('content', content)
    dicts.setdefault('senderName', senderName)
    dicts.setdefault('topicId', topicId)
    dicts.setdefault('senderAvatar', senderAvatar)
    return dicts

def genCommResDict(resPath):
    dicts = {}
    dicts.setdefault('resPath', resPath)
    return dicts

@api_view(['GET','POST'])
def clickPraise(request):
    topicObj = None
    topicLikeNum = None
    response_data = {}
    userId     = request.POST.get('user_id', None)#hit user
    topicId    = request.POST.get('topic_id', None)
    handleType = request.POST.get('type', None) # 1 is hit  0 no hit
    hitStatus = 0
    try:
        topicObj = Topic.objects.get(topic_id=long(topicId))
        topicLikeNum = topicObj.like_num
        if topicLikeNum is None:
            topicLikeNum = 0
    except:
        response_data['flag'] = 'ok'
        response_data['userId'] = userId
        response_data['likeNum'] = -1
        response_data['hitStatus'] = hitStatus
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if 1 == int(handleType):#1 ok 
        Praise.objects.get_or_create(topic=long(topicId),user=long(userId))
        hitStatus = 1
        if topicObj is not None:
            topicLikeNum = topicLikeNum + 1
            topicObj.like_num = topicLikeNum
            topicObj.save()
    else:#2 no
        try:
            Praise.objects.filter(topic=long(topicId),user=long(userId)).delete()
            hitStatus = 0
            if topicObj is not None:
                topicLikeNum = topicLikeNum - 1
                topicObj.like_num = topicLikeNum
                topicObj.save()
        except:
            response_data['flag'] = 'error'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    
    response_data['flag'] = 'ok'
    response_data['userId'] = userId
    response_data['likeNum'] = topicLikeNum
    response_data['hitStatus'] = hitStatus
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def getTopicDeleteStatus(request):
    response_data = {}
    communityId = request.POST.get('community_id', None)
    topicId     = request.POST.get('topic_id', None)
    try:
        topicObj = Topic.objects.get(sender_community_id=long(communityId),topic_id=long(topicId))
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

@api_view(['GET','POST'])
def getTopic(request):
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
        adminType   = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
    if topic_id is None:
        topic_id = 0
    targetId = int(topic_id)
    if count is None:# pull down
        if targetId == 0:
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
            topicQuerySet = Topic.objects.filter(topic_category_type=2,sender_community_id=long(communityId)).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,sender_community_id=long(communityId)).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,topic_id__gt=targetId,sender_community_id=long(communityId)).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,topic_id__lt=targetId,sender_community_id=long(communityId)).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==2:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).order_by('-topic_id')[:topicNum] #admin
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
        communityId = topicQuerySet[i].sender_community_id
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId))
            curUserName = User.objects.get(user_id = long(senderId))
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
        if objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag)
            ListActivity.append(activityDict)
        if objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+str(object_data)
            pic_url = 'https://'+servhost+newsObj.new_small_pic
            newDict = getNewsDict(newsObj,pic_url,new_url)
            ListActivity.append(newDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
def deleteTopic(request):
    response_data = {}
    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topicId     = request.POST.get('topic_id', None)
    topicType   = request.POST.get('topic_type', None)
    processType = request.POST.get('process_type', None)
    
    if topicId is None:#删除所有报修
        if int(topicType)==4:#删除报修
            if processType is None:
                processType = 0
            if userId is None:
                response_data['flag'] = 'user_id_error' 
                return HttpResponse(json.dumps(response_data), content_type="application/json")   
            try:
                userObjWithRepair = Admin.objects.get(admin_type=4,user_id=long(userId))
            except Exception,e:
                userObjWithRepair = None
                response_data['Exception'] = str(Exception)
                response_data['Error'] = str(e)
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            if int(processType)==3:
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,process_status=processType)
                else:
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,sender_id=long(userId),process_status=processType)
            else:
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4).exclude(process_status=3)
                else:
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,sender_id=long(userId)).exclude(process_status=3)
            topicIdList = []
            size = topicQuerySet.count()
            for i in range(0,size,1):
                topicIdList.append(topicQuerySet[i].getTopicId())
            if userObjWithRepair is not None:#表示此用户位物业管理员
                try:
                    for i in range(len(topicIdList)):
                        topicObjWithRepair = Topic.objects.get(topic_id=topicIdList[i],sender_community_id=communityId)
                        topicObjWithRepair.delete_type = 4  # 4表示物业管理员删除了，但用户可看
                        topicObjWithRepair.save()
                except:
                    response_data['flag'] = 'delete_all_repair_error' 
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                try:
                    for i in range(len(topicIdList)):
                        Praise.objects.filter(topic=topicIdList[i]).delete()
                        Media_files.objects.filter(topic_id=topicIdList[i]).delete()
                        Comment.objects.filter(topic_id=topicIdList[i]).delete()
                        CollectionTopic.objects.filter(topic_id=long(topicIdList[i])).delete()
                        try:
                            activityArray = Activity.objects.filter(topic_id=topicIdList[i])
                            if activityArray is not None:
                                actObj = activityArray[0]
                                aId = actObj.getActivityId()
                                EnrollActivity.objects.filter(activity_id=aId).delete()
                                actObj.delete()
                        except:
                            pass
                        Topic.objects.filter(topic_id=topicIdList[i],sender_community_id=communityId).delete()
                        delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicIdList[i])
                        os.popen(delFileString)
                except Exception,e:
                    response_data['Exception'] = str(Exception)
                    response_data['Error'] = str(e)
                    return HttpResponse(json.dumps(response_data), content_type="application/json")  
            response_data['flag'] = 'ok'
            response_data['list'] = str(topicIdList)
            return HttpResponse(json.dumps(response_data), content_type="application/json")  
        else:
            response_data['flag'] = 'all_delete_error'
            return HttpResponse(json.dumps(response_data), content_type="application/json") 
    else:
        if topicType is None:
            Praise.objects.filter(topic=topicId).delete()
            Media_files.objects.filter(topic_id=topicId).delete()
            Comment.objects.filter(topic_id=topicId).delete()
            CollectionTopic.objects.filter(topic_id=long(topicId)).delete()
            try:
                activityArray = Activity.objects.filter(topic_id=topicId)
                if activityArray is not None:
                    actObj = activityArray[0]
                    aId = actObj.getActivityId()
                    EnrollActivity.objects.filter(activity_id=aId).delete()
                    actObj.delete()
            except:
                pass
            Topic.objects.filter(topic_id=topicId,sender_community_id=communityId).delete()
            delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicId)
            os.popen(delFileString)
        else:#表示删除的是物业报修帖子
            if int(topicType) == 4:
                if userId is None:
                    response_data['flag'] = 'user_id_error' 
                    return HttpResponse(json.dumps(response_data), content_type="application/json")    
                try:
                    userObjWithRepair = Admin.objects.get(admin_type=4,user_id=long(userId))
                except Exception,e:
                    userObjWithRepair = None
#                     response_data['flag'] = 'topic_repair_error' 
#                     response_data['Exception'] = str(Exception)
#                     response_data['Error'] = str(e)
#                     return HttpResponse(json.dumps(response_data), content_type="application/json")    
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    try:
                        topicObjWithRepair = Topic.objects.get(topic_id=topicId,sender_community_id=communityId)
                        topicObjWithRepair.delete_type = 4  # 4表示物业管理员删除了，但用户可看
                        topicObjWithRepair.save()
                    except:
                        response_data['flag'] = 'topic_repair_error' 
                        return HttpResponse(json.dumps(response_data), content_type="application/json")    
                else:
                    Praise.objects.filter(topic=topicId).delete()
                    Media_files.objects.filter(topic_id=topicId).delete()
                    Comment.objects.filter(topic_id=topicId).delete()
                    CollectionTopic.objects.filter(topic_id=long(topicId)).delete()
                    try:
                        activityArray = Activity.objects.filter(topic_id=topicId)
                        if activityArray is not None:
                            actObj = activityArray[0]
                            aId = actObj.getActivityId()
                            EnrollActivity.objects.filter(activity_id=aId).delete()
                            actObj.delete()
                    except:
                        pass
                    Topic.objects.filter(topic_id=topicId,sender_community_id=communityId).delete()
                    delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicId)
                    os.popen(delFileString)
            else:
                response_data['flag'] = 'repair_error'
                return HttpResponse(json.dumps(response_data), content_type="application/json")    
        response_data['flag'] = 'ok'
        return HttpResponse(json.dumps(response_data), content_type="application/json")    

@api_view(['GET','POST'])
def intoDetailTopic(request):
    viewNum = None
    topicObj = None
    response_data = {}
    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topicId     = request.POST.get('topic_id', None)
    try:
        topicObj = Topic.objects.get(topic_id=long(topicId),sender_community_id=long(communityId))
        viewNum = topicObj.view_num
        if viewNum is None:
            viewNum = 1
        else:
            viewNum = viewNum + 1
        topicObj.view_num = viewNum
        topicObj.save()
        response_data['flag'] = 'ok'
        response_data['viewNum'] = viewNum
    except:
        response_data['flag'] = 'no'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def searchTopic(request):
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    if request.method == 'POST': 
        communityId = request.POST.get('community_id', None)
        keyWord     = request.POST.get('key_word', None)
        topic_id    = request.POST.get('topic_id', None)
        count       = request.POST.get('count', None)
        userId      = request.POST.get('user_id', None)
    else:
        communityId = request.GET.get('community_id', None)
        keyWord     = request.GET.get('key_word', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        userId      = request.GET.get('user_id', None)
    if count is None:
        count = 8
    topicNum = int(count)
    if topic_id is None:
        topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),topic_title__icontains=keyWord)\
                                     .order_by('-topic_id')[:topicNum]
    else:
        targetId = long(topic_id)
        topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord)\
                                     .order_by('-topic_id')[:topicNum] # <
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
        object_data = topicQuerySet[i].object_type
        colStatus = 0
        try:
            colObj = CollectionTopic.objects.get(topic_id=long(topicId),user_id=long(userId),community_id=long(communityId))
            colStatus = 3
        except:
            colStatus = 0
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        try:
            praiseObj = Praise.objects.get(topic=long(curTopciId),user=long(userId))
            praiseType = 1 # his praise
        except:
            praiseType = 0 # no praise
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
        if objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+str(object_data)
            pic_url = 'https://'+servhost+newsObj.new_small_pic
            newDict = getNewsDict(newsObj,pic_url,new_url)
            ListActivity.append(newDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
                ListComment.append(commentDicts)

        topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                         senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                         communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                         cacheKey,ListMediaFile,ListComment,ListActivity)
        ListMerged.append(topicDict)
        ListComment = []
        ListMediaFile = []
    if ListMerged:
        topicString = json.dumps(ListMerged)
        return HttpResponse(topicString, content_type="application/json")
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def genCommDetailDict(senderAddress,senderFamilyId,senderLevel,commId,senderNcRoleId,sendTime,videoLength,\
                      contentType,senderId,displayName,content,senderName,topicId,senderAvatar,mediaDict,\
                      systemTime,remarkName=None):
    dicts = {}
    dicts.setdefault('systemTime', systemTime)
    dicts.setdefault('senderAddress', senderAddress)
    dicts.setdefault('senderFamilyId', senderFamilyId)
    dicts.setdefault('senderLevel', senderLevel)
    dicts.setdefault('commId', commId)
    dicts.setdefault('senderNcRoleId', senderNcRoleId)
    dicts.setdefault('sendTime', sendTime)
    dicts.setdefault('contentType', contentType)
    dicts.setdefault('senderId', senderId)
    dicts.setdefault('displayName', displayName)
    dicts.setdefault('content', content)
    dicts.setdefault('videoLength', videoLength)
    dicts.setdefault('senderName', senderName)
    dicts.setdefault('topicId', topicId)
    dicts.setdefault('senderAvatar', senderAvatar)
    if mediaDict:
        dicts.setdefault('mediaFiles',mediaDict)
    else:
        dicts.setdefault('mediaFiles', None)
    if remarkName:
        dicts.setdefault('remarkName',remarkName)
        dicts.setdefault('commentType',2)#1表示一级回复 2表示二级回复
    else:
        dicts.setdefault('remarkName','null')
        dicts.setdefault('commentType',1)
    return dicts

@api_view(['GET','POST'])
def getComment(request):
    ListComment = []
    ListMediaFile = []
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id', None)
        commentId   = request.POST.get('comment_id', None)
        count       = request.POST.get('count', None)
        commType    = request.POST.get('type', None)
    else:
        topicId     = request.GET.get('topic_id', None)
        commentId   = request.GET.get('comment_id', None)
        count       = request.GET.get('count', None)
        commType    = request.GET.get('type', None)
    if 1 == int(commType):#init
        commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__gt=long(commentId)).order_by('comment_id')
    elif 2 == int(commType):#down
        commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__gt=long(commentId)).order_by('comment_id')
    else:#up
        if commentId is None:
            commQuerySet = Comment.objects.filter(topic_id=long(topicId)).order_by('-comment_id')[:count]
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__lt=long(commentId)).order_by('-comment_id')[:count]
    commSize = commQuerySet.count()
    for i in range(0,commSize,1):
        senderAddr = commQuerySet[i].senderAddress
        senderFamilyId = commQuerySet[i].senderFamilyId
        senderLevel = commQuerySet[i].senderLevel
        commId = commQuerySet[i].getCommentId()
        senderNcRoleId = commQuerySet[i].senderNcRoleId
        sendTime = commQuerySet[i].sendTime
        contentType = commQuerySet[i].contentType
        senderId = commQuerySet[i].senderId
        displayName = commQuerySet[i].displayName
        content = commQuerySet[i].content
        senderName = commQuerySet[i].senderName
        videoTime= commQuerySet[i].videoTime
        topicId = commQuerySet[i].topic.getTopicId()
        senderObj = None
        try:
            senderObj = User.objects.get(user_id=long(senderId))
            senderAvatar = senderObj.user_portrait
        except:
            senderObj = None
            senderAvatar = commQuerySet[i].senderAvatar
        if 1 == int(contentType):# image
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=commId)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                if contentType == 'image':
                    mediaDict = genImageFilesDict(resId,resPath,contentType)
                else:
                    mediaDict = genVideoFilesDict(resId,resPath,contentType,videoTime)
                ListMediaFile.append(mediaDict)           
        elif 2 == int(contentType):# video
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=commId)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDict = genVideoFilesDict(resId,resPath,contentType,videoTime)
                ListMediaFile.append(mediaDict)  
        commentDicts = genCommDetailDict(senderAddr,senderFamilyId,senderLevel,commId,senderNcRoleId,sendTime,videoTime,\
                                         contentType,senderId,displayName,content,senderName,topicId,senderAvatar,ListMediaFile)
        ListMediaFile = []
        ListComment.append(commentDicts)
    if ListComment:
        commString = json.dumps(ListComment)
        return HttpResponse(commString, content_type="application/json")
    else:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def commImgGenPath(user_id, topic_id):
    userDir = settings.MEDIA_ROOT+'youlin/res/'+str(user_id)+'/topic/comment/' + str(topic_id) + '/'
    if os.path.exists(userDir):
        pass
    else:
        try:
            os.makedirs(userDir, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                pass
            else:raise    
    return userDir

@api_view(['GET','POST'])
def addComment(request):
    currentCommunityId = None
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        senderId    = request.POST.get('sender_id')
        senderTime  = request.POST.get('sendTime')
        content     = request.POST.get('content')
        contentType = request.POST.get('contentType') # 0 normal 1 image 2 video
        sendCommty  = request.POST.get('community_id')
        videoLength = request.POST.get('video_length',None)
    else:
        topicId     = request.GET.get('topic_id')
        senderId    = request.GET.get('sender_id')
        senderTime  = request.GET.get('sendTime')
        content     = request.GET.get('content')
        contentType = request.GET.get('contentType') # 0 normal 1 image 2 video
        sendCommty  = request.GET.get('community_id')
        videoLength = request.GET.get('video_length',None)
 
    if 0 == int(sendCommty):
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    usrObj = User.objects.get(user_id=senderId)
    currentCommunityId = usrObj.user_community_id
    senderAvatar = usrObj.user_portrait
    senderName = usrObj.user_nick
    senderFamilyId = usrObj.user_family_id
    senderLevel = usrObj.user_level
    try:
        frObj = FamilyRecord.objects.get(user_id=senderId,family_id=senderFamilyId)
    except:
        response_data = {}
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
    senderAddr = frObj.family_community  # community+block

    displayName = senderName+'@'+senderAddr

    curTime = long(time.time()*1000)

    commentObj = Comment.objects.create(content=content,topic_id=topicId,sendTime=curTime,\
                                        senderId=senderId,senderNcRoleId=0,contentType=contentType)
    commentId = commentObj.getCommentId()
    commentObj.senderAddress = senderAddr
    commentObj.senderAvatar = senderAvatar
    commentObj.senderName = senderName
    commentObj.senderFamilyId = senderFamilyId
    commentObj.senderLevel = senderLevel
    commentObj.displayName = displayName
    if videoLength is None:
        commentObj.videoTime = 0
    else:
        commentObj.videoTime = str(videoLength)
        
    commentObj.save()  
    
    if 1 == int(contentType): # image
        commImage = request.FILES.get('image', None)
        if commImage is not None:
            newImage = imgGenName(commImage.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = commImgGenPath(senderId, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in commImage.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
        else:
            response_data['flag'] = 'not_find_image'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif 2 == int(contentType): # video    
        commVideo = request.FILES.get('video', None)
        if commVideo is not None:
            newVideo = imgGenName(commVideo.name) # new video
            userDir = commImgGenPath(senderId, topicId)
            streamfile = open(userDir+newVideo, 'wb+')
            for chunk in commVideo.chunks():
                streamfile.write(chunk)
            streamfile.close()
            mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='video')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ newVideo
            mediaFileObj.save()
            ##########################################################################################################
            #格式转化
            #amr2wavPath = '/opt/youlin_backend/media/youlin/res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'
            #amr2wav = 'ffmpeg -i '+amr2wavPath+newVideo+' '+(amr2wavPath+newVideo)[:-4]+'.wav'
            #os.system(amr2wav)
        else:
            response_data['flag'] = 'not,find,video'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    commNum = 0
    topicObj = Topic.objects.get(topic_id=topicId)
    if topicObj.comment_num is None:
        commNum = 1
    else:
        commNum = int(topicObj.comment_num) + 1
    topicObj.comment_num = commNum
    topicObj.save()
    # push info
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderId).encode('utf-8') + ":" \
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
                u"push_new_comm",
                None,
                None
            )
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":True}
    push.platform = jpush.all_
    try:       
        push.send() 
    except:
        pass

    response_data = {}
    response_data['flag'] = 'ok'
    response_data['commentId'] = commentId
    response_data['display'] = displayName
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def delComment(request):
    response_data = {}
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        commentId   = request.POST.get('comment_id')
        communityId = request.POST.get('community_id')
        senderId    = request.POST.get('user_id')
    else:
        topicId     = request.GET.get('topic_id')
        commentId   = request.GET.get('comment_id')
        communityId = request.GET.get('community_id')
        senderId    = request.GET.get('user_id')
        
    Comment.objects.filter(comment_id=long(commentId),topic_id=long(topicId)).delete();
    commNum = 0
    try:
        topicObj = Topic.objects.get(topic_id=topicId)
        if topicObj.comment_num is None:
            commNum = 0
        else:
            if int(topicObj.comment_num)==0:
                commNum = 0
            else:
                commNum = int(topicObj.comment_num) - 1
        topicObj.comment_num = commNum
        topicObj.save()
    except:
        pass
    # push
    config = readIni()
    tagSuffix = config.get('topic', "tagSuffix")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderId).encode('utf-8') + ":" \
                 +str(communityId).encode('utf-8') + ":" \
                 +str(commentId).encode('utf-8')
   
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
    push.options = {"time_to_live":0, "sendno":9527, "apns_production":True}
    push.platform = jpush.all_
    try:       
        push.send() 
    except:
        pass

    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def replayComment(request):
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        senderId    = request.POST.get('sender_id') # senderUserID
        replayId    = request.POST.get('replay_id') # replayUserID
        senderTime  = request.POST.get('sendTime')
        content     = request.POST.get('content')
        contentType = request.POST.get('contentType') # 0 normal 1 image 2 video
    else:
        topicId     = request.GET.get('topic_id')
        senderId    = request.GET.get('sender_id') # senderUserID
        replayId    = request.GET.get('replay_id') # replayUserID
        senderTime  = request.GET.get('sendTime')
        content     = request.GET.get('content')
        contentType = request.GET.get('contentType') # 0 normal 1 image 2 video

    usrObj = User.objects.get(user_id=senderId)
    
    senderAvatar = usrObj.user_portrait
    senderName = usrObj.user_nick
    senderFamilyId = usrObj.user_family_id
    senderLevel = usrObj.user_level

    frObj = FamilyRecord.objects.get(user_id=senderId,family_id=senderFamilyId)
    
    senderAddr = frObj.family_community  # community+block

    displayName = senderName+'@'+senderAddr

    commentObj = Comment.objects.create(content=content,topic_id=topicId,sendTime=senderTime,\
                                        senderId=senderId,senderNcRoleId=0,contentType=contentType)
    commentId = commentObj.getCommentId()
    commentObj.senderAddress = senderAddr
    commentObj.senderAvatar = senderAvatar
    commentObj.senderName = senderName
    commentObj.senderFamilyId = senderFamilyId
    commentObj.senderLevel = senderLevel
    commentObj.displayName = displayName

    commentObj.save()

    if 1 == int(contentType): # image
        commImage = request.FILES.get('image', None)
        if commImage is not None:
            newImage = imgGenName(commImage.name) # new image
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = commImgGenPath(senderId, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in commImage.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(userDir, bigImage, smaillImage,30)
            mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
        else:
            response_data['flag'] = 'not,find,image'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif 2 == int(contentType): # video    
        commVideo = request.FILES.get('video', None)
        if commVideo is not None:
            newVideo = imgGenName(commVideo.name) # new video
            userDir = commImgGenPath(senderId, topicId)
            streamfile = open(userDir+newVideo, 'wb+')
            for chunk in commVideo.chunks():
                streamfile.write(chunk)
            streamfile.close()
            mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='video')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ newVideo
            mediaFileObj.save()
        else:
            response_data['flag'] = 'not,find,video'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    commNum = 0
    topicObj = Topic.objects.get(topic_id=topicId)
    if topicObj.comment_num is None:
        commNum = 1
    else:
        commNum = int(topicObj.comment_num) + 1
    topicObj.comment_num = commNum
    topicObj.save()

    response_data = {}
    response_data['flag'] = 'ok'
    response_data['commentId'] = commentId
    response_data['display'] = displayName
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@api_view(['GET','POST'])
def activityEnroll(request):
    data = None
    listEnroll = []
    enrollData = []
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    enrollObj = EnrollActivity.objects.get_or_create(activity_id=data['activityId'],user_id=data['userId'],enrollUserCount=data['enrollUserCount'],\
                                        enrollNeCount=data['enrollNeCount'])
    count = None
    try:
        count = enrollTotal(data['activityId'])
    except:
        count = 0
    response_data = {}
    if enrollObj: 
        response_data['flag']    = 'ok'
        response_data['count']   = count
    else:
        response_data['flag']    = 'no' 
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

@api_view(['GET','POST'])
def detailEnroll(request):
    data = None
    listEnroll = []
    enrollData = []
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    enrollLists = EnrollActivity.objects.filter(activity_id = data['activityId'])
    enrollSize = enrollLists.count()
    enrollTotal = 0
    for i in range(0,enrollSize,1):   
        userId = enrollLists[i].user_id
        userObj = User.objects.get(user_id = userId)
        enrollId = enrollLists[i].enroll_id
        enrollUserCount = enrollLists[i].enrollUserCount
        enrollNeCount = enrollLists[i].enrollNeCount
        total = enrollNeCount+enrollUserCount
        enrollDict = getEnrollActivityDict(enrollId,userId,userObj.user_nick,userObj.user_portrait,enrollUserCount,enrollNeCount,total)
        listEnroll.append(enrollDict)
        enrollTotal = total + enrollTotal
        
    enrollData = getEnrollDataDict(data['activityId'],enrollTotal,listEnroll)  
    return HttpResponse(json.dumps(enrollData), content_type="application/json") 

def getEnrollDataDict(activityId,enrollTotal,listEnroll):
    
    dict = {}
    dict.setdefault('activityId',activityId)
    dict.setdefault('enrollTotal',enrollTotal)
    dict.setdefault('enrollData',listEnroll)
    return dict
    
def getEnrollActivityDict(enrollId,userId,userNick,userPortrait,enrollUserCount,enrollNeCount,total):
    
    dict = {}
    dict.setdefault('enrollId',enrollId)
    dict.setdefault('userId',userId)
    dict.setdefault('userNick',userNick)
    dict.setdefault('userPortrait',userPortrait)
    dict.setdefault('enrollUserCount',enrollUserCount)
    dict.setdefault('enrollNeCount',enrollNeCount)
    dict.setdefault('total',total)
    return dict    
    
@api_view(['GET','POST'])
def cancelEnroll(request):
    response_data = {} 
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    try:
        EnrollActivity.objects.filter(activity_id=data['activityId'],user_id=data['userId']).delete()
        total = enrollTotal(data['activityId'])
        response_data['enrollTotal']= total
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def enrollTotal(activityId): 
    
    enrollLists = EnrollActivity.objects.filter(activity_id = activityId)
    enrollSize = enrollLists.count()
    enrollTotal = 0
    for i in range(0,enrollSize,1):   
        enrollUserCount = enrollLists[i].enrollUserCount
        enrollNeCount = enrollLists[i].enrollNeCount
        total = enrollNeCount+enrollUserCount
        enrollTotal = total + enrollTotal
    return enrollTotal

def getDTopicDetail(topicId,title,content,nick,img_count,avatar,time,objectType,deleteType):
    dict = {}
    dict.setdefault('topicId',topicId)
    dict.setdefault('title',title)
    dict.setdefault('content',content)
    dict.setdefault('nick',nick)
    dict.setdefault('img_count',img_count)
    dict.setdefault('avatar',avatar)
    dict.setdefault('time',time)
    dict.setdefault('topicType',objectType)
    dict.setdefault('deleteType',deleteType)
    return dict

@api_view(['GET','POST'])
def reportTopicHandle(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    topicDetailList = []
    newReportId = None
    if request.method == 'POST':
        topicId        = request.POST.get('topic_id')
        complainUserId = request.POST.get('complain_id')
        senderUserId   = request.POST.get('sender_id')
        communityId    = request.POST.get('community_id')
        title          = request.POST.get('title')
        content        = request.POST.get('content')
    else:
        topicId        = request.GET.get('topic_id')
        complainUserId = request.GET.get('complain_id')
        senderUserId   = request.GET.get('sender_id')
        communityId    = request.GET.get('community_id')
        title          = request.GET.get('title')
        content        = request.GET.get('content')
    
    curTime = long(time.time()*1000)
    
    reportObj = ReportTopic(topic_id=long(topicId),complain_user_id=long(complainUserId),\
                            sender_user_id=long(senderUserId),community_id=long(communityId),\
                            title=title,content=content,time=curTime)
    reportObj.save()
    newReportId = reportObj.getReportId()
    try:
        reportCount = ReportTopic.objects.filter(topic_id=long(topicId),community_id=long(communityId)).count()
    except:
        reportCount = 0
    reportInterval = 2
    if int((reportCount%reportInterval) < (reportInterval-1)):    
        response_data = {}
        response_data['flag'] = 'ok'   
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    userObj = User.objects.get(user_id=senderUserId)
    topicObj = Topic.objects.get(topic_id=topicId)
    try:
        topicTitle = topicObj.topic_title
    except:
        topicTitle = None
    try:
        topicContent = topicObj.topic_content
    except:
        topicContent = None
    try:
        senderNick = topicObj.sender_name
    except:
        senderNick = None
    try:
        senderAvatar = topicObj.sender_portrait
    except:
        senderAvatar = None
    try:
        topicTime = topicObj.topic_time
    except:
        topicTime = None
    if topicObj.send_status==1:
        img_count = Media_files.objects.filter(topic_id=topicId,comment_id=0).count()
    else:
        img_count = 0
    try:
        objectType = topicObj.object_data_id
        if objectType is None:
            objectType = 0
        elif objectType == 'null':
            objectType = 0
    except:
        objectType = 0
    try:
        deleteType = topicObj.delete_type
        if deleteType is None:
            deleteType = 0
        elif deleteType == 'null':
            deleteType = 0
    except:
        deleteType = 0    
    topicDetailList.append(getDTopicDetail(topicId,topicTitle,topicContent,senderNick,img_count,senderAvatar,topicTime,objectType,deleteType))    
    
    config = readIni()
    tagSuffix = config.get("report", "tagSuffix")
    pushTitle = config.get("report", "pushTitle")
    pTitle = config.get("report", "title")
    userAvatar = settings.RES_URL+'res/default/avatars/default-police.png'
    currentPushTime = long(time.time()*1000)
    userNick = userObj.user_nick.encode('utf-8')
    message1 = config.get("report", "content1") +" "+userNick+" "+config.get("report", "content2")+\
               topicTitle+config.get("report", "content3")+\
               pTitle+config.get("report", "content4")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderUserId).encode('utf-8') + ":" \
                 +str(communityId).encode('utf-8')
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,pTitle,message1,newReportId)
    recordId = createPushRecord(4,1,pTitle,message1,currentPushTime,1001,json.dumps(custom_content),communityId,1001)      
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,pTitle,message1,newReportId,recordId,topicDetailList)

    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    tagName = tagSuffix+str(communityId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    pushExtra = custom_content
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.tag(tagName),
            )
    push.notification = jpush.notification(
                android=jpush.android(message1,pTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":True}
    push.platform = jpush.all_
    try:
        push.send()  
    except:
        pass
    response_data = {}
    response_data['flag'] = 'ok'   
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def getCustomDict(senderUserId,currentPushTime,pTitle,userAvatar,topicId,message1,infoTitle,infoContent,repairId,communityId,recordId=None,topicDetail=None):
    dicts = {}
    dicts.setdefault('userId',senderUserId)
    dicts.setdefault('pushType',4)
    dicts.setdefault('contentType',1)
    dicts.setdefault('pushTime',currentPushTime)
    dicts.setdefault('title',pTitle)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('message',message1)
    dicts.setdefault('pushTitle',infoTitle)
    dicts.setdefault('pushContent',infoContent)
    dicts.setdefault('repairId',repairId)
    dicts.setdefault('communityId',communityId)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    if topicDetail is None:
        pass
    else:
        dicts.setdefault('topicDetail',topicDetail)
    return dicts
    
@api_view(['GET','POST'])
def getMyTopic(request):
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []

    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topic_id    = request.POST.get('topic_id', None)
    topicNum    = request.POST.get('count', None)
        
    if topic_id is None:
        topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),sender_id=userId).exclude(topic_category_type=4).order_by('-topic_id')[:topicNum]
    else:
        targetId = int(topic_id)
        topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),sender_id=userId).exclude(topic_category_type=4).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait=1
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
        if objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+str(object_data)
            pic_url = 'https://'+servhost+newsObj.new_small_pic
            newDict = getNewsDict(newsObj,pic_url,new_url)
            ListActivity.append(newDict)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
def delCollection(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    try:
        CollectionTopic.objects.get(user_id = data['user_id'],topic_id = data['topic_id'],community_id=data['community_id']).delete()
        response_data['flag'] = 'ok'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    except:
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@api_view(['GET','POST']) 
def addCollection(request):
    
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    response_data = {}
    try:
        CollectionTopic.objects.get_or_create(user_id = data['user_id'],topic_id = data['topic_id'],community_id=data['community_id'])
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
 
@api_view(['GET','POST']) 
def getCollectTopic(request):
    
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
        topicNum    = request.POST.get('count', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        topicNum    = request.GET.get('count', None)
    colQuerySet = CollectionTopic.objects.filter(user_id=userId,community_id=communityId)
    size = colQuerySet.count()
    topicIds = []
    if colQuerySet:
        for i in range(0,size,1):
             id = colQuerySet[i].topic_id
             topicIds.append(id)
        
        if topic_id is None:
            topicQuerySet = Topic.objects.filter(topic_id__in = topicIds).order_by('-topic_id')[:topicNum]
        else:
            targetId = int(topic_id)
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,topic_id__in = topicIds).order_by('-topic_id')[:topicNum] #<
        size = topicQuerySet.count()
        
        for i in range(0,size,1):
            topicId = topicQuerySet[i].getTopicId()
            curTopciId = topicId
            forumId = topicQuerySet[i].forum_id
            forumName = topicQuerySet[i].forum_name
            senderId = topicQuerySet[i].sender_id
            senderName = topicQuerySet[i].sender_name
            senderLevel = topicQuerySet[i].sender_lever
            senderPortrait=1
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
            if objectType == 3:  # news
                try:
                    newsObj = News.objects.get(new_id = int(object_data))
                except:
                    newsObj = None
                servhost = request.get_host()
                new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+str(object_data)
                pic_url = 'https://'+servhost+newsObj.new_small_pic
                newDict = getNewsDict(newsObj,pic_url,new_url)
                ListActivity.append(newDict)
            if commentNum is None:
                ListComment = []
            else:
                commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).order_by('-comment_id')[:2]
                commSize = commQuerySet.count()
                for i in range(0,commSize,1):   
                    com_senderAddr = commQuerySet[i].senderAddress
                    com_senderFamilyId = commQuerySet[i].senderFamilyId
                    com_senderLevel = commQuerySet[i].senderLevel
                    com_commId = commQuerySet[i].getCommentId()
                    com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                    com_sendTime = commQuerySet[i].sendTime
                    com_contentType = commQuerySet[i].contentType
                    com_senderId = commQuerySet[i].senderId
                    com_displayName = commQuerySet[i].displayName
                    com_content = commQuerySet[i].content
                    com_senderName = commQuerySet[i].senderName
                    com_topicId = commQuerySet[i].topic.getTopicId()
                    com_senderAvatar = commQuerySet[i].senderAvatar
                    commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                                  com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
            response_data['flag'] = 'no'#meiyou gengduo le
            return HttpResponse(json.dumps(response_data), content_type="application/json") 
    else:
        response_data = {}
        response_data['flag'] = 'no2'
        return HttpResponse(json.dumps(response_data), content_type="application/json") 
    
@api_view(['GET','POST'])
def getTopicCounts(request):
    myPostNum = None
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
    try:
        myPostNum = Topic.objects.filter(sender_id=long(userId),sender_community_id=communityId).exclude(topic_category_type=4).count()
        mycollectNum = CollectionTopic.objects.filter(user_id=long(userId),community_id=communityId).count()
    except:
        myPostNum = 0
        mycollectNum = 0
        response_data['flag'] = 'no'
        response_data['myPost'] = myPostNum
        response_data['mycolNum'] = mycollectNum
        return HttpResponse(json.dumps(response_data), content_type="application/json") 
    if myPostNum is None:
        myPostNum = 0
    if mycollectNum is None:
        mycollectNum = 0
    response_data['flag'] = 'ok'
    response_data['myPost'] = myPostNum
    response_data['mycolNum'] = mycollectNum
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

def genReportDicts(complain_user_id,sender_user_id,community_id,title,content,report_id,time):
    dicts = {}
    dicts.setdefault('complain_user_id',complain_user_id)
    dicts.setdefault('sender_user_id',sender_user_id)
    dicts.setdefault('community_id',community_id)
    dicts.setdefault('title',title)
    dicts.setdefault('time',time)
    dicts.setdefault('content',content)
    dicts.setdefault('report_id',report_id)
    return dicts

@api_view(['GET','POST'])
def getReportInfo(request):
    ListMerged = []
    response_data = {}
    if request.method == 'POST':
        user_id  = request.POST.get('user_id', None)
        topic_id = request.POST.get('topic_id', None)
    else:
        user_id  = request.GET.get('user_id', None)
        topic_id = request.GET.get('topic_id', None)
        
    reportQuerySet = ReportTopic.objects.filter(topic_id=long(topic_id)).order_by('title')
    size = reportQuerySet.count();
    if size <= 0:
        response_data['flag'] = 'none' 
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    for i in range(0,size,1):
        complain_user_id = reportQuerySet[i].complain_user_id
        sender_user_id   = reportQuerySet[i].sender_user_id
        community_id     = reportQuerySet[i].community_id
        title            = reportQuerySet[i].title
        content          = reportQuerySet[i].content
        report_id        = reportQuerySet[i].getReportId()
        time             = reportQuerySet[i].time
        ListMerged.append(genReportDicts(complain_user_id,sender_user_id,community_id,title,content,report_id,time))
    return HttpResponse(json.dumps(ListMerged), content_type="application/json")

def getShareNewsDict(newsObj,pic_url,new_url,new_sender,new_sender_nick,new_sender_url,pushType,contentType,pushTime,title,pushContent,communityId,record_id):
    dicts = {}
    dicts.setdefault('new_title', newsObj.new_title)
    dicts.setdefault('new_id', newsObj.new_id)
    dicts.setdefault('new_add_time', newsObj.new_add_time)
    dicts.setdefault('new_small_pic', pic_url)
    dicts.setdefault('new_url', new_url)
    dicts.setdefault('new_sender', new_sender)
    dicts.setdefault('new_sender_nick', new_sender_nick)
    dicts.setdefault('userAvatar', new_sender_url)
    dicts.setdefault('pushType', pushType)
    dicts.setdefault('contentType', contentType)
    dicts.setdefault('pushTime', pushTime)
    dicts.setdefault('title', title)
    dicts.setdefault('content', pushContent)
    dicts.setdefault('communityId', communityId)
    if record_id is None:
        pass
    else:
        dicts.setdefault('recordId', record_id)
    return dicts

@api_view(['GET','POST'])
def shareCommunityNews(request):
    newsObj = None
    response_data = {}
    if request.method == 'POST':
        senderId    = request.POST.get('sender_id', None)
        recipyId    = request.POST.get('recipy_id', None)
        newsId      = request.POST.get('news_id', None)
        communityId = request.POST.get('community_id', None)
    else:
        senderId    = request.GET.get('sender_id', None)
        recipyId    = request.GET.get('recipy_id', None)
        newsId      = request.GET.get('news_id', None)
        communityId = request.GET.get('community_id', None)
    try:
        BlackList.objects.get(user_id=long(recipyId),black_id=long(senderId))
        response_data['flag'] = 'black'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    except:
        pass
    try:
        newsObj = News.objects.get(new_id = newsId,community_id=long(communityId))
    except:
        newsObj = None
        response_data['flag'] = 'no_id'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    servhost = request.get_host()
    new_url = 'https://'+servhost+'/adminpush/web/getNews/?id='+str(newsId)
    pic_url = 'https://'+servhost+newsObj.new_small_pic
    userNick = None
    user_portrait = None
    try:
        userObj = User.objects.get(user_id=long(senderId))
        userNick = userObj.user_nick
        user_portrait = userObj.user_portrait
    except:
        userNick = None
        
    config = readIni()
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    
    if userNick is None:
        pushTitle = '匿名'
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    else:
        pushTitle = userNick
        userAvatar = user_portrait
    pushContent = config.get("news", "content2")
    currentPushTime = long(time.time()*1000)
    
    customContent = getShareNewsDict(newsObj,pic_url,new_url,3001,userNick,userAvatar,1,5,currentPushTime,pushTitle,pushContent,communityId,None)
    recordId = createPushRecord(1,5,pushTitle,pushContent,currentPushTime,3001,json.dumps(customContent),communityId,3001)
    customContent = getShareNewsDict(newsObj,pic_url,new_url,3001,userNick,userAvatar,1,5,currentPushTime,pushTitle,pushContent,communityId,recordId)
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(recipyId)
    pushExtra = customContent
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
    push.notification = jpush.notification(
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":True}
    push.platform = jpush.all_
    try:
        push.send()
    except:
        response_data['flag'] = 'push_error'
        response_data['result'] = currentAlias
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    

#发送帖子    
def PostNewTopic(request):
    data = {}
    curComId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        title                          = request.POST.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        curSenderId                    = request.POST.get('sender_id', None)
        topicObj.sender_id             = curSenderId
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.collect_status        = request.POST.get('sender_nc_role', None)
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
            curUserName = User.objects.get(user_id=long(curSenderId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
        if topicObj.object_data_id == '1':#活动
            activityId = createActivity(topicId, topicObj, request)
        elif topicObj.object_data_id == '3':#新闻
            newsId = request.POST.get('new_id', None)
            topicObj.object_type = newsId
        elif topicObj.object_data_id == '4':#置换
            createSecondHandle(topicId,request)
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
        topicObj.collect_status        = request.GET.get('sender_nc_role', None)
        topicObj.sender_family_id      = request.GET.get('sender_family_id', None)
        topicObj.sender_family_address = request.GET.get('sender_family_address', None)
        topicObj.display_name          = request.GET.get('display_name', None)
        topicObj.object_data_id        = request.GET.get('object_data_id', None)
        topicObj.circle_type           = request.GET.get('circle_type', None)
        topicObj.send_status           = request.GET.get('send_status', None)
        topicObj.sender_city_id        = request.GET.get('sender_city_id', None)
        curComId                       = request.GET.get('sender_community_id', None)
        topicObj.sender_community_id   = curComId
        topicObj.cache_key             = genCacheKey()
        if topicObj.object_data_id == '1':
            activityId = createActivity(topicId, topicObj, request)
        elif topicObj.object_data_id == '3':
            newsId = request.GET.get('new_id', None)
            try:
                newsObj = News.objects.get(new_id = newsId)
            except:
                pass
            servhost = request.get_host()
            new_url = 'https://'+servhost+SHARE_NEWS+newsId
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            newDict = getNewsDict(newsObj,pic_url,new_url)
            topicObj.object_type = json.dumps(newDict)
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
            
    AsyncAddTopic.delay(topicId, user_id, curComId, currentCommunityId)
    
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return data
    
#修改帖子
def UpdateTopic(request):
    data = {}
    curComId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':                                                                      
        topicId                        = request.POST.get('topic_id', None)
        try:
            topicObj                       = Topic.objects.get(topic_id=long(topicId))
        except:
            data['error1']         = "topicId is empty"
        topicObj.topic_title           = request.POST.get('topic_title', None)
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        curSenderId                    = request.POST.get('sender_id', None)
        topicObj.sender_id             = curSenderId
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
#         topicObj.collect_status        = request.POST.get('sender_nc_role', None)
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
            curUserName = User.objects.get(user_id=long(curSenderId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
        
        if topicObj.object_data_id == '1':
            activityId = updateActivity(topicId, topicObj, request)
    topicObj.save()
    Media_files.objects.filter(topic_id=long(topicId),comment_id=0).delete()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
    AsyncUpdateTopic.delay(topicId, currentCommunityId)
    data['flag']         = "ok"
    data['topic_id']     = topicId
    data['community_id'] = curComId
    data['user_id']      = user_id
    data['systemTime']   = long(time.time()*1000)
    return data

#获取活动
def GetSingleActivity(request):
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
        adminType   = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
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
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,topic_id__gt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,topic_id__lt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==2:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] #admin
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
        if objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag)
            ListActivity.append(newDict)
        else:
            dicts = {}
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
        response_data['systemTime'] = long(time.time()*1000)
        return response_data
    
#获取话题
def GetSingleTopic(request):
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
        adminType   = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
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
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,topic_id__gt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,topic_id__lt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==2:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] #admin
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
        if objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            from web.models import Subscription
            subObj = Subscription.objects.get(community_id=long(communityId))
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag,subObj)
            ListActivity.append(newDict)
        else:
            if 1 != int(senderId):
                dicts = {}
                dicts.setdefault('communityLng',communityLng)
                dicts.setdefault('communityLag',communityLag)
                ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
                ListComment.append(commentDicts)
        curSystemTime = long(time.time()*1000)        
        if 1 == int(senderId):
            sayHelloStatus = 0
            if SayHello.objects.filter(user_id=long(userId),topic_id=long(curTopciId)).count() > 0:
                sayHelloStatus = 1 #表示已经打过招呼
            else:
                sayHelloStatus = 0 #表示没有打过招呼
            dicts = {}
            dicts.setdefault('sayHelloStatus',sayHelloStatus)
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
            topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                             senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                             communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                             cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime)
        else:
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
        response_data['systemTime'] = long(time.time()*1000)
        return response_data

#获取单个以物换物
def GetSingleBarter(request):
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
        adminType   = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
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
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=4,topic_id__gt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=4,topic_id__lt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==2:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).order_by('-topic_id')[:topicNum] #admin
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
        if objectType == 4:  # change
            secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
            secondHandDict = getSecondDict(secondHandObj,communityLng,communityLag)
            ListActivity.append(secondHandDict)
        elif objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag)
            ListActivity.append(newDict)
        else:
            dicts = {}
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
        response_data['systemTime'] = long(time.time()*1000)
        return response_data

#获取帖子
def GetTopic(request):
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
        adminType   = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
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
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
            topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
        elif targetId == -1:
            topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
        else:
            topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],topic_id__gt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            if 1==int(topicNum):
                topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4)
            else:
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],topic_id__lt=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==0:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #normal
        elif int(adminType)==2:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
        elif int(adminType)==4:
            topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
#         senderName = topicQuerySet[i].sender_name
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
        deleteType = topicQuerySet[i].delete_type
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
        if objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)            
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            from web.models import Subscription
            subObj = Subscription.objects.get(community_id=long(communityId))
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag,subObj)
            ListActivity.append(newDict)
        #elif objectType == 4:  # change
        #    secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        #    secondHandDict = getSecondDict(secondHandObj,communityLng,communityLag)
        #    ListActivity.append(secondHandDict)
        else:
            if 1 != int(senderId):
                dicts = {}
                dicts.setdefault('communityLng',communityLng)
                dicts.setdefault('communityLag',communityLag)
                ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
                ListComment.append(commentDicts)
        curSystemTime = long(time.time()*1000)
        if 1 == int(senderId):
            sayHelloStatus = 0
            if SayHello.objects.filter(user_id=long(userId),topic_id=long(curTopciId)).count() > 0:
                sayHelloStatus = 1 #表示已经打过招呼
            else:
                sayHelloStatus = 0 #表示没有打过招呼
            dicts = {}
            dicts.setdefault('sayHelloStatus',sayHelloStatus)
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
            topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                             senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                             communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                             cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime,deleteType)
        else:
            topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                             senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                             communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                             cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime,deleteType)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    if ListMerged:
        return ListMerged
    else:
        response_data = {}
        response_data['flag'] = 'no'
        response_data['systemTime'] = long(time.time()*1000)
        return response_data

#获取我发的帖子
def GetMyTopic(request):
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []

    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topic_id    = request.POST.get('topic_id', None)
    topicNum    = request.POST.get('count', None)
    
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
        topicQuerySet = Topic.objects.filter(sender_community_id=long(communityId),sender_id=userId).exclude(topic_category_type=4).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum]
    else:
        targetId = int(topic_id)
        topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,sender_community_id=long(communityId),sender_id=userId).exclude(topic_category_type=4).exclude(object_data_id=4).exclude(delete_type=2).order_by('-topic_id')[:topicNum] # <
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
#         senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait=1
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            from web.models import Subscription
            subObj = Subscription.objects.get(community_id=long(communityId))
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag,subObj)
            ListActivity.append(newDict)
        else:
            dicts = {}
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
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
        response_data['systemTime'] = long(time.time()*1000)
        return response_data

#单独或去帖子回复总数
def GetCommentCountFromTopic(request):
    blackList = []
    if request.method == 'POST':
        topicId = request.POST.get('topic_id')
        userId  = request.POST.get('user_id')
    else:
        topicId = request.GET.get('topic_id')
        userId  = request.GET.get('user_id')
    blkListOtherQuerySet = BlackList.objects.filter(black_id = long(userId))
    blkListSize = blkListOtherQuerySet.count()
    for i in range(0,blkListSize,1):
        blackList.append(blkListOtherQuerySet[i].user_id)
    blkListOwnQuerySet = BlackList.objects.filter(user_id = long(userId))
    blkListSize = blkListOwnQuerySet.count()
    for i in range(0,blkListSize,1):
        blackList.append(blkListOwnQuerySet[i].black_id)
    if len(blackList):
        commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
    else:
        commNum = Comment.objects.filter(topic_id=topicId).count()
    response_data = {}
    response_data['flag'] = 'ok'
    response_data['count'] = commNum
    return response_data
#添加回复
def AddComment(request):
    blackList = []
    repUserId = None
    response_data = {}
    currentCommunityId = None
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        senderId    = request.POST.get('sender_id')
        senderTime  = long(time.time()*1000)
        content     = request.POST.get('content')
        contentType = request.POST.get('contentType') # 0 normal 1 image 2 video
        sendCommty  = request.POST.get('community_id')
        videoLength = request.POST.get('video_length',None)
        repUserId   = request.POST.get('replay_user_id',None)
        iosDevice   = request.POST.get('ios',None)
    else:
        topicId     = request.GET.get('topic_id')
        senderId    = request.GET.get('sender_id')
        senderTime  = long(time.time()*1000)
        content     = request.GET.get('content')
        contentType = request.GET.get('contentType') # 0 normal 1 image 2 video
        sendCommty  = request.GET.get('community_id')
        videoLength = request.GET.get('video_length',None)
        iosDevice   = request.GET.get('ios',None)
    if iosDevice is None:
        iosDevice = 'android'
    else:
        iosDevice = 'ios'
    if repUserId is not None:
        if content:
            try:
                str_split = content.split(':')#按照:截取
                content = str_split[1]
            except:
                repUserId = None
                content = request.POST.get('content')
    if repUserId is not None:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(senderId))
        blkListSize0 = blkListOtherQuerySet.count()
        for i in range(0,blkListSize0,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(senderId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
        if long(repUserId) in blackList:
            response_data['flag'] = 'black'
            return response_data
    curTopicSenderId = None
    try:
        curTopicObj = Topic.objects.get(topic_id=long(topicId))
        curTopicSenderId = curTopicObj.sender_id
        delete_type = curTopicObj.delete_type
        try:
            delType = int(delete_type)
            if int(delType) == 2:
                response_data['flag'] = 'none'
                return response_data
        except:
            pass
    except:
        response_data['flag'] = 'none'
        return response_data
    if 0 == int(sendCommty):
        response_data['flag'] = 'no'
        return response_data
    usrObj = User.objects.get(user_id=senderId)
    currentCommunityId = usrObj.user_community_id
    senderAvatar = usrObj.user_portrait
    try:
        remObj = Remarks.objects.get(target_id=long(curTopicSenderId),remuser_id=long(senderId))
        senderName = remObj.user_remarks
    except:
        senderName = usrObj.user_nick
    senderName = usrObj.user_nick
    senderFamilyId = usrObj.user_family_id
    senderLevel = usrObj.user_level
    try:
        frObj = FamilyRecord.objects.get(user_id=senderId,family_id=senderFamilyId)
    except Exception,e:
        response_data = {}
        response_data['err1'] = str(Exception)
        response_data['err2'] = str(e)
        response_data['flag'] = 'no'
        return response_data
    
    commNum = 0
#     topicObj = Topic.objects.get(topic_id=topicId)
#     if topicObj.comment_num is None:
#         commNum = 1
#     else:
#         commNum = int(topicObj.comment_num) + 1
#     topicObj.comment_num = commNum
#     topicObj.save()
    if repUserId is None:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(senderId))
        blkListSize0 = blkListOtherQuerySet.count()
        for i in range(0,blkListSize0,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(senderId))
        blkListSize1 = blkListOwnQuerySet.count()
        for i in range(0,blkListSize1,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    if len(blackList):
        topicSenderId = Topic.objects.get(topic_id=long(topicId)).sender_id
        if long(topicSenderId) == long(senderId):#表示是自己发的帖子
            if long(topicSenderId) in blackList:
                commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
                AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
                response_data['flag'] = 'black'
                return response_data
            else:
                senderAddr = frObj.family_community  # community+block

                displayName = senderName+'@'+senderAddr
            
                curTime = long(time.time()*1000)
                if repUserId is None:
                    repUserId = 0
                commentObj = Comment.objects.create(content=content,topic_id=topicId,sendTime=curTime,replayId=long(repUserId),\
                                                    senderId=senderId,senderNcRoleId=0,contentType=contentType)
                commentId = commentObj.getCommentId()
                commentObj.senderAddress = senderAddr
                commentObj.senderAvatar = senderAvatar
                commentObj.senderName = senderName
                commentObj.senderFamilyId = senderFamilyId
                commentObj.senderLevel = senderLevel
                commentObj.displayName = displayName
                if videoLength is None:
                    commentObj.videoTime = 0
                else:
                    commentObj.videoTime = str(videoLength)
                commentObj.save()  
                
                if 1 == int(contentType): # image
                    commImage = request.FILES.get('image', None)
                    if commImage is not None:
                        newImage = imgGenName(commImage.name) # new image
                        bigImage = '0' + newImage # big image
                        smaillImage = newImage # smaill image
                        userDir = commImgGenPath(senderId, topicId)
                        streamfile = open(userDir+bigImage, 'wb+')
                        for chunk in commImage.chunks():
                            streamfile.write(chunk)
                        streamfile.close()
                        makeThumbnail(userDir, bigImage, smaillImage,30)
                        mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='image')
                        mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ smaillImage
                        mediaFileObj.save()
                    else:
                        response_data['flag'] = 'not_find_image'
                        return response_data
                elif 2 == int(contentType): # video    
                    commVideo = request.FILES.get('video', None)
                    if commVideo is not None:
                        newVideo = imgGenName(commVideo.name) # new video
                        userDir = commImgGenPath(senderId, topicId)
                        streamfile = open(userDir+newVideo, 'wb+')
                        for chunk in commVideo.chunks():
                            streamfile.write(chunk)
                        streamfile.close()
                        mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='video')
                        mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ newVideo
                        mediaFileObj.save()
                        #格式转化
#                         AsyncAMR2WAV.delay(senderId,topicId,newVideo,iosDevice)
                    else:
                        response_data['flag'] = 'not,find,video'
                        return response_data
                commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
                AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
        else:
            if blkListSize0>0:
                blackList.append(long(senderId))
            if long(topicSenderId) in blackList:
                try:
                    blackList.remove(long(senderId))
                except Exception,e:
                    response_data['Error'] = str(e)
                commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
                AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
                response_data['flag'] = 'black'
                return response_data
            else:
                senderAddr = frObj.family_community  # community+block

                displayName = senderName+'@'+senderAddr
            
                curTime = long(time.time()*1000)
                if repUserId is None:
                    repUserId = 0
                commentObj = Comment.objects.create(content=content,topic_id=topicId,sendTime=curTime,replayId=long(repUserId),\
                                                    senderId=senderId,senderNcRoleId=0,contentType=contentType)
                commentId = commentObj.getCommentId()
                commentObj.senderAddress = senderAddr
                commentObj.senderAvatar = senderAvatar
                commentObj.senderName = senderName
                commentObj.senderFamilyId = senderFamilyId
                commentObj.senderLevel = senderLevel
                commentObj.displayName = displayName
                if videoLength is None:
                    commentObj.videoTime = 0
                else:
                    commentObj.videoTime = str(videoLength)
                commentObj.save()  
                
                if 1 == int(contentType): # image
                    commImage = request.FILES.get('image', None)
                    if commImage is not None:
                        newImage = imgGenName(commImage.name) # new image
                        bigImage = '0' + newImage # big image
                        smaillImage = newImage # smaill image
                        userDir = commImgGenPath(senderId, topicId)
                        streamfile = open(userDir+bigImage, 'wb+')
                        for chunk in commImage.chunks():
                            streamfile.write(chunk)
                        streamfile.close()
                        makeThumbnail(userDir, bigImage, smaillImage,30)
                        mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='image')
                        mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ smaillImage
                        mediaFileObj.save()
                    else:
                        response_data['flag'] = 'not_find_image'
                        return response_data
                elif 2 == int(contentType): # video    
                    commVideo = request.FILES.get('video', None)
                    if commVideo is not None:
                        newVideo = imgGenName(commVideo.name) # new video
                        userDir = commImgGenPath(senderId, topicId)
                        streamfile = open(userDir+newVideo, 'wb+')
                        for chunk in commVideo.chunks():
                            streamfile.write(chunk)
                        streamfile.close()
                        mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='video')
                        mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ newVideo
                        mediaFileObj.save()
                        #格式转化
#                         AsyncAMR2WAV.delay(senderId,topicId,newVideo,iosDevice)
                    else:
                        response_data['flag'] = 'not,find,video'
                        return response_data
                try:
                    blackList.remove(long(senderId))
                except Exception,e:
                    response_data['Error'] = str(e)
                commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
                AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
    else:
        senderAddr = frObj.family_community  # community+block

        displayName = senderName+'@'+senderAddr
    
        curTime = long(time.time()*1000)
        
        if repUserId is None:
            repUserId = 0
        commentObj = Comment.objects.create(content=content,topic_id=topicId,sendTime=curTime,replayId=long(repUserId),\
                                            senderId=senderId,senderNcRoleId=0,contentType=contentType)
        commentId = commentObj.getCommentId()
        commentObj.senderAddress = senderAddr
        commentObj.senderAvatar = senderAvatar
        commentObj.senderName = senderName
        commentObj.senderFamilyId = senderFamilyId
        commentObj.senderLevel = senderLevel
        commentObj.displayName = displayName
        if videoLength is None:
            commentObj.videoTime = 0
        else:
            commentObj.videoTime = str(videoLength)
        commentObj.save()  
        
        if 1 == int(contentType): # image
            commImage = request.FILES.get('image', None)
            if commImage is not None:
                newImage = imgGenName(commImage.name) # new image
                bigImage = '0' + newImage # big image
                smaillImage = newImage # smaill image
                userDir = commImgGenPath(senderId, topicId)
                streamfile = open(userDir+bigImage, 'wb+')
                for chunk in commImage.chunks():
                    streamfile.write(chunk)
                streamfile.close()
                makeThumbnail(userDir, bigImage, smaillImage,30)
                mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='image')
                mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ smaillImage
                mediaFileObj.save()
            else:
                response_data['flag'] = 'not_find_image'
                return response_data
        elif 2 == int(contentType): # video    
            commVideo = request.FILES.get('video', None)
            if commVideo is not None:
                newVideo = imgGenName(commVideo.name) # new video
                userDir = commImgGenPath(senderId, topicId)
                streamfile = open(userDir+newVideo, 'wb+')
                for chunk in commVideo.chunks():
                    streamfile.write(chunk)
                streamfile.close()
                mediaFileObj = Media_files(topic_id=topicId, resId=0, comment_id=commentId, contentType='video')
                mediaFileObj.resPath = settings.RES_URL+'res/'+str(senderId)+'/topic/comment/'+str(topicId)+'/'+ newVideo
                mediaFileObj.save()
                #格式转化
#                 AsyncAMR2WAV.delay(senderId,topicId,newVideo,iosDevice)
            else:
                response_data['flag'] = 'not,find,video'
                return response_data
        commNum = Comment.objects.filter(topic_id=topicId).count()
        AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
    #推送到某人
    #pattern = re.compile(r'回复 ')
    #match = pattern.match(content[0:7]) #使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    if repUserId is not None:
        import sys
        default_encoding = 'utf-8'
        if sys.getdefaultencoding() != default_encoding:
            reload(sys)
            sys.setdefaultencoding(default_encoding)
        config = readIni()
        alias = config.get("SDK", "youlin")
        currentPushTime = long(time.time()*1000)
        customTitle = config.get('comment', "title")
        pushTitle = config.get("comment", "pushTitle")
        userAvatar = senderAvatar
        topicTitle = Topic.objects.get(topic_id=long(topicId)).topic_title
        topicType = Topic.objects.get(topic_id=long(topicId)).object_data_id
        userNick = senderName
        message = config.get("comment", "content1") +" "+userNick+" "+config.get("comment", "content2")+\
                   topicTitle+config.get("comment", "content3")
        custom_content = getReplayDetailDict(senderId,repUserId,6,1,message,1010,\
                                             currentPushTime,pushTitle,userAvatar,customTitle,topicId,topicType,sendCommty)
        recordId = createPushRecord(6,1,customTitle,message,currentPushTime,\
                                    1010,custom_content,currentCommunityId,1010)
        custom_content = getReplayDetailDict(senderId,repUserId,6,1,message,1010,\
                                             currentPushTime,pushTitle,userAvatar,customTitle,topicId,topicType,sendCommty,recordId)
        apiKey = config.get("SDK", "apiKey")
        secretKey = config.get("SDK", "secretKey")
        currentAlias = alias + str(repUserId)
        
        AsyncReplayCommentPush.delay(apiKey,secretKey,custom_content,currentAlias,message,customTitle)

    response_data['flag'] = 'ok'
    response_data['commentId'] = commentId
    response_data['display'] = displayName
    return response_data

def getReplayDetailDict(senderId,replaySenderId,pushType,contentType,message,commentType,\
                        pushTime,pushTitle,userAvatar,title,topicId,topicType,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('communityId',communityId)
    dicts.setdefault('userId',senderId)
    dicts.setdefault('replayUserId',replaySenderId)
    dicts.setdefault('pushType',pushType)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushTitle',pushTitle)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('topicId',topicId)
    dicts.setdefault('message',message)
    dicts.setdefault('topicType',topicType)
    dicts.setdefault('commentType',commentType)#说明回复类型
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

#删除回复
def DelComment(request):
    response_data = {}
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        commentId   = request.POST.get('comment_id')
        communityId = request.POST.get('community_id')
        senderId    = request.POST.get('user_id')
    else:
        topicId     = request.GET.get('topic_id')
        commentId   = request.GET.get('comment_id')
        communityId = request.GET.get('community_id')
        senderId    = request.GET.get('user_id')
    try:
        topObj = Topic.objects.get(topic_id = long(topicId))
        delete_type = topObj.delete_type
        try:
            delType = int(delete_type)
            if int(delType) == 2:
                response_data['flag'] = 'none'
                return response_data
        except:
            pass
    except:
        response_data['flag'] = 'none'
        return response_data
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(senderId))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(senderId))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
    try:
        Comment.objects.get(comment_id=long(commentId),topic_id=long(topicId)).delete();
        commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
#         try:
#             topicObj = Topic.objects.get(topic_id=topicId)
#             if topicObj.comment_num is None:
#                 commNum = 0
#             else:
#                 if int(topicObj.comment_num)==0:
#                     commNum = 0
#                 else:
#                     commNum = int(topicObj.comment_num) - 1
#             topicObj.comment_num = commNum
#             topicObj.save()
#         except:
#             response_data['flag'] = 'no_topicId'
#             return response_data
        AsyncDelCommentPush.delay(topicId, senderId, communityId, commentId,commNum)
    except:
        response_data['flag'] = 'no_commentId'
        return response_data
    response_data['flag'] = 'ok'
    return response_data

#获取回复
def GetComment(request):
    userNick = None
    ListComment = []
    ListMediaFile = []
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        topicId     = request.POST.get('topic_id', None)
        commentId   = request.POST.get('comment_id', None)
        count       = request.POST.get('count', None)
        commType    = request.POST.get('type', None)
    else:
        userId      = request.GET.get('user_id', None)
        topicId     = request.GET.get('topic_id', None)
        commentId   = request.GET.get('comment_id', None)
        count       = request.GET.get('count', None)
        commType    = request.GET.get('type', None)
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
    
    if 1 == int(commType):#init
        commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__gt=long(commentId)).exclude(senderId__in=blackList).order_by('comment_id')
    elif 2 == int(commType):#down
        commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__gt=long(commentId)).exclude(senderId__in=blackList).order_by('comment_id')
    else:#up
        if commentId is None:
            commQuerySet = Comment.objects.filter(topic_id=long(topicId)).exclude(senderId__in=blackList).order_by('-comment_id')[:count]
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(topicId),comment_id__lt=long(commentId)).exclude(senderId__in=blackList).order_by('-comment_id')[:count]
    commSize = commQuerySet.count()
    for i in range(0,commSize,1):
        senderAddr = commQuerySet[i].senderAddress
        senderFamilyId = commQuerySet[i].senderFamilyId
        senderLevel = commQuerySet[i].senderLevel
        commId = commQuerySet[i].getCommentId()
        senderNcRoleId = commQuerySet[i].senderNcRoleId
        sendTime = commQuerySet[i].sendTime
        contentType = commQuerySet[i].contentType
        senderId = commQuerySet[i].senderId
        replayId = commQuerySet[i].replayId
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            remObj = None
            senderName = commQuerySet[i].senderName
        senderObj = None
        try:
            senderObj = User.objects.get(user_id=long(senderId))
            userNick = senderObj.user_nick
            curCommunityName = Community.objects.get(community_id=long(senderObj.user_community_id)).community_name
            displayName = senderName + '@' + curCommunityName
        except:
            senderObj = None
            displayName = commQuerySet[i].displayName
        content = commQuerySet[i].content
        if long(replayId) == -1:#表示此回复是欢迎信息
            userReplayContnet = None
        elif long(replayId) == 0:#表示一级回复
            userReplayContnet = None
        else:
            try:
                userReplayObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(replayId))
                userReplayContnet = userReplayObj.user_remarks
            except:
                try:
                    commentUserNick = User.objects.get(user_id=long(replayId)).user_nick
                except:
                    commentUserNick = 'null'
                userReplayContnet = commentUserNick
#         if long(replayId) == -1:#表示此回复是欢迎信息
#             pass
#         else:
#             try:
#                 remWithContentObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(replayId))
#                 userRemarksWithContnet = remWithContentObj.user_remarks
#             except:
#                 userRemarksWithContnet = None
#             if userRemarksWithContnet is not None:#表示已经被修改备注
#                 import sys
#                 default_encoding = 'utf-8'
#                 if sys.getdefaultencoding() != default_encoding:
#                     reload(sys)
#                     sys.setdefaultencoding(default_encoding)
#                 str_split = content.split(':')#按照:截取
#                 #pattern = re.compile()
#                 #match = pattern.match(content[0:7]) #使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
#                 contentEnd = None
#                 try:
#                     contentEnd = str_split[1]
#                     content = r'回复 '+senderName+":"+contentEnd
#                 except:
#                     content = r'回复 '+senderName+":"
        videoTime= commQuerySet[i].videoTime
        topicId = commQuerySet[i].topic.getTopicId()
        senderObj = None
        try:
            senderAvatar = senderObj.user_portrait
        except:
            senderObj = None
            senderAvatar = commQuerySet[i].senderAvatar
        if 1 == int(contentType):# image
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=commId)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                if contentType == 'image':
                    mediaDict = genImageFilesDict(resId,resPath,contentType)
                else:
                    mediaDict = genVideoFilesDict(resId,resPath,contentType,videoTime)
                ListMediaFile.append(mediaDict)           
        elif 2 == int(contentType):# video
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=commId)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                contentType = mediaFileObjs[j].contentType
                mediaDict = genVideoFilesDict(resId,resPath,contentType,videoTime)
                ListMediaFile.append(mediaDict)  
        curSystemTime = long(time.time()*1000)
        commentDicts = genCommDetailDict(senderAddr,senderFamilyId,senderLevel,commId,senderNcRoleId,sendTime,videoTime,\
                                         contentType,senderId,displayName,content,senderName,topicId,senderAvatar,ListMediaFile,\
                                         curSystemTime,userReplayContnet)
        ListMediaFile = []
        ListComment.append(commentDicts)
    if ListComment:
        return ListComment
    else:
        response_data = {}
        response_data['flag'] = 'no'
        response_data['systemTime'] = long(time.time()*1000)
        return response_data
    
#搜索帖子
def SearchTopic(request):
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
        adminType   = request.POST.get('type', None)
        keyWord     = request.POST.get('key_word', None)
        categType   = request.POST.get('category_type', None)#0全部 1 话题 2 活动  3 公告  5 建议  
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        count       = request.GET.get('count', None)
        adminType   = request.GET.get('type', None)
        keyWord     = request.GET.get('key_word', None)
        categType   = request.GET.get('category_type', None)
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
         #   topicQuerySet = Topic.objects.filter(Q(sender_community_id=long(communityId))|Q(forum_id=1)).order_by('-topic_id')[:6]
        if targetId == 0:
            if int(categType) == 0:#全部
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
            elif int(categType) == 1:#话题
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
            elif int(categType) == 2:#活动
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
            elif int(categType) == 3:#公告
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
            elif int(categType) == 5:#建议
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:6]
        elif targetId == -1:
            if int(categType) == 0:#全部
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 1:#话题
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 2:#活动
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 3:#公告
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 5:#建议
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
        else:
            if int(categType) == 0:#全部
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],topic_id__gt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 1:#话题
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,topic_id__gt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 2:#活动
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,topic_id__gt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 3:#公告
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id__gt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
            elif int(categType) == 5:#建议
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id__gt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')
    else:#pull up
        topicNum = int(count)
        if adminType is None:
            if int(categType) == 0:#全部
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
            elif int(categType) == 1:#话题
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
            elif int(categType) == 2:#活动
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
            elif int(categType) == 3:#公告
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
            elif int(categType) == 5:#建议
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id__lt=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] # <
        elif int(adminType)==2:
            if int(categType) == 0:#全部
                topicQuerySet = Topic.objects.filter(topic_category_type__in=[2,3,5],topic_id=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
            elif int(categType) == 1:#话题
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=0,topic_id=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
            elif int(categType) == 2:#活动
                topicQuerySet = Topic.objects.filter(topic_category_type=2,object_data_id=1,topic_id=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
            elif int(categType) == 3:#公告
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
            elif int(categType) == 5:#建议
                topicQuerySet = Topic.objects.filter(topic_category_type=int(categType),topic_id=targetId,sender_community_id=long(communityId),topic_title__icontains=keyWord).exclude(sender_id__in=blackList).exclude(delete_type=2).exclude(object_data_id=4).order_by('-topic_id')[:topicNum] #admin
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
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
        if objectType == 1: # Activity
            activityObj = Activity.objects.get(topic_id=topicId)
            total = enrollTotal(activityObj.activity_id)
            flagObj = EnrollActivity.objects.filter(activity_id=activityObj.activity_id,user_id=userId)
            if flagObj:
                enrollFlag = "true"
            else:
                enrollFlag = "false"
            activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
            ListActivity.append(activityDict)
        elif objectType == 3:  # news
            try:
                newsObj = News.objects.get(new_id = int(object_data))
            except:
                newsObj = None
            servhost = request.get_host()
            new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
            tmp_pic_url = newsObj.new_small_pic
            if tmp_pic_url[:4]=='http':
                pic_url = tmp_pic_url
            else:
                pic_url = 'https://'+servhost+tmp_pic_url
            from web.models import Subscription
            subObj = Subscription.objects.get(community_id=long(communityId))
            newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag,subObj)
            ListActivity.append(newDict)
        else:
            if 1 != int(senderId):
                dicts = {}
                dicts.setdefault('communityLng',communityLng)
                dicts.setdefault('communityLag',communityLag)
                ListActivity.append(dicts)
        if commentNum is None:
            ListComment = []
        else:
            commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
            commSize = commQuerySet.count()
            for i in range(0,commSize,1):   
                com_senderAddr = commQuerySet[i].senderAddress
                com_senderFamilyId = commQuerySet[i].senderFamilyId
                com_senderLevel = commQuerySet[i].senderLevel
                com_commId = commQuerySet[i].getCommentId()
                com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                com_sendTime = commQuerySet[i].sendTime
                com_contentType = commQuerySet[i].contentType
                com_senderId = commQuerySet[i].senderId
                com_displayName = commQuerySet[i].displayName
                com_content = commQuerySet[i].content
                com_senderName = commQuerySet[i].senderName
                com_topicId = commQuerySet[i].topic.getTopicId()
                com_senderAvatar = commQuerySet[i].senderAvatar
                commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                              com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
                ListComment.append(commentDicts)
        curSystemTime = long(time.time()*1000)
        if 1 == int(senderId):
            sayHelloStatus = 0
            if SayHello.objects.filter(user_id=long(userId),topic_id=long(curTopciId)).count() > 0:
                sayHelloStatus = 1 #表示已经打过招呼
            else:
                sayHelloStatus = 0 #表示没有打过招呼
            dicts = {}
            dicts.setdefault('sayHelloStatus',sayHelloStatus)
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
            topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                             senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                             communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                             cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime)
        else:
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
        
#帖子点赞    
def ClickPraise(request):
    topicObj = None
    topicLikeNum = None
    response_data = {}
    userId     = request.POST.get('user_id', None)#hit user
    topicId    = request.POST.get('topic_id', None)
    handleType = request.POST.get('type', None) # 1 is hit  0 no hit
    hitStatus = 0
    try:
        topicObj = Topic.objects.get(topic_id=long(topicId))
        senderId = topicObj.sender_id
        
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
        if long(senderId) in blackList:
            response_data['flag'] = 'black'
            response_data['likeNum'] = -1
            return response_data

        topicLikeNum = topicObj.like_num
        if topicLikeNum is None:
            topicLikeNum = 0
    except:
        response_data['flag'] = 'no_topicId'
        response_data['hitStatus'] = hitStatus
        return response_data
    try:
        objTop = Topic.objects.get(topic_id = long(topicId))
        try:
            delete_type = objTop.delete_type
            deleteType = int(delete_type)
            if int(deleteType)==2:
                response_data['flag'] = 'ok'
                response_data['likeNum'] = -1
                return response_data
        except:
            pass
    except:
        pass
    if 1 == int(handleType):#1 ok 
        Praise.objects.get_or_create(topic=long(topicId),user=long(userId))
        hitStatus = 1
        if topicObj is not None:
            topicLikeNum = topicLikeNum + 1
            topicObj.like_num = topicLikeNum
            topicObj.save()
    else:#2 no
        try:
            Praise.objects.filter(topic=long(topicId),user=long(userId)).delete()
            hitStatus = 0
            if topicObj is not None:
                topicLikeNum = topicLikeNum - 1
                topicObj.like_num = topicLikeNum
                topicObj.save()
        except:
            response_data['flag'] = 'error'
            return response_data
    
    response_data['flag'] = 'ok'
    response_data['userId'] = userId
    response_data['likeNum'] = topicLikeNum
    response_data['hitStatus'] = hitStatus
    return response_data

def genPraiseDict(userId,userNick,userGender,userPortrait,phone,userProfession,userPraiseId,
                  userSignature,userLevel,userEmail,userBirthday,userfamilyAddr,communityId):
    dicts = {}
    dicts.setdefault('user_id', userId)
    dicts.setdefault('user_nick', userNick)
    dicts.setdefault('user_gender', userGender)
    dicts.setdefault('user_portrait', userPortrait)
    dicts.setdefault('user_phone', phone)
    dicts.setdefault('user_profession', userProfession)
    dicts.setdefault('user_signature', userSignature)
    dicts.setdefault('user_level', userLevel)
    dicts.setdefault('user_email', userEmail)
    dicts.setdefault('user_birthday', userBirthday)
    dicts.setdefault('user_family_addr', userfamilyAddr)
    dicts.setdefault('praise_id', userPraiseId)
    dicts.setdefault('community_id', communityId)
    return dicts

#返回点赞详细信息
def GetPraiseDetail(request):
    response_data = {}
    if request.method == 'POST':
        topicId  = request.POST.get('topic_id', None)
        status   = request.POST.get('status', None)
        praiseId = request.POST.get('praise_id', None)
    else:
        topicId  = request.GET.get('topic_id', None)
        status   = request.GET.get('status', None)
        praiseId = request.GET.get('praise_id', None)
        
    if topicId is None:
        response_data['flag'] = 'parameter error'
        return response_data
    pLength = Praise.objects.filter(topic=long(topicId)).count()
    defaultLength = 4
    if status is None:#长按点赞
        praiseQuerySet = Praise.objects.filter(topic=long(topicId))[:defaultLength]
        size = praiseQuerySet.count()
        userIdList = []
        length = 0
        if long(size)>(defaultLength-1):
            length = (defaultLength-1)
        else:
            length = size
        for i in range(0,length,1):
            userIdList.append(praiseQuerySet[i].user)
        praiseList = []
        for i in range(len(userIdList)):
            userObj = User.objects.get(user_id=long(userIdList[i]))
            userId         = userIdList[i]
            userNick       = userObj.user_nick
            userGender     = userObj.user_gender
            userPortrait   = userObj.user_portrait
            userPhone      = userObj.user_phone_number
            userProfession = userObj.user_profession
            userSignature  = userObj.user_signature
            userLevel      = userObj.user_level
            userEmail      = userObj.user_email
            userBirthday   = userObj.user_birthday
            userfamilyAddr = userObj.user_family_address
            communityId    = userObj.user_community_id  
            userPraiseId   = praiseQuerySet[i].getPraiseId()
            praiseList.append(genPraiseDict(userId,userNick,userGender,userPortrait,userPhone,userProfession,userPraiseId,
                                            userSignature,userLevel,userEmail,userBirthday,userfamilyAddr,communityId))
        response_data['count'] = pLength
        response_data['detail'] = praiseList
    else:#获取点赞列表，默认返回20个
        defaultLength = 20
        if praiseId is None:#第一次list
            praiseQuerySet = Praise.objects.filter(topic=long(topicId))[:defaultLength]
        else:#上拉刷新list
            praiseQuerySet = Praise.objects.filter(topic=long(topicId),_id__gt=long(praiseId))[:defaultLength]#大于
        size = praiseQuerySet.count()
        userIdList = []
        for i in range(0,size,1):
            userIdList.append(praiseQuerySet[i].user)
        praiseList = []
        for i in range(len(userIdList)):
            userObj = User.objects.get(user_id=long(userIdList[i]))
            userId         = userIdList[i]
            userNick       = userObj.user_nick
            userGender     = userObj.user_gender
            userPortrait   = userObj.user_portrait
            userPhone      = userObj.user_phone_number
            userProfession = userObj.user_profession
            userSignature  = userObj.user_signature
            userLevel      = userObj.user_level
            userEmail      = userObj.user_email
            userBirthday   = userObj.user_birthday
            userfamilyAddr = userObj.user_family_address
            communityId    = userObj.user_community_id  
            userPraiseId   = praiseQuerySet[i].getPraiseId()
            praiseList.append(genPraiseDict(userId,userNick,userGender,userPortrait,userPhone,userProfession,userPraiseId,
                                            userSignature,userLevel,userEmail,userBirthday,userfamilyAddr,communityId))
        response_data['count'] = pLength
        response_data['detail'] = praiseList
    return response_data
    
#进入帖子详情
def IntoDetailTopic(request):
    viewNum = None
    topicObj = None
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
    try:
        topicObj = Topic.objects.get(topic_id=long(topicId),sender_community_id=long(communityId))
        viewNum = topicObj.view_num
        if viewNum is None:
            viewNum = 1
        else:
            viewNum = viewNum + 1
        topicObj.view_num = viewNum
        topicObj.save()
        response_data['flag'] = 'ok'
        response_data['viewNum'] = viewNum
    except Exception,e:
        response_data['Exception'] = str(Exception)
        response_data['error'] = str(e)
        response_data['flag'] = 'no'
    return response_data

#删除帖子
def DeleteTopic(request):
    response_data = {}
    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topicId     = request.POST.get('topic_id', None)
    topicType   = request.POST.get('topic_type', None)
    processType = request.POST.get('process_type', None)
    
    
    
    if topicId is None:#删除所有报修
        if int(topicType)==4:#删除报修
            if processType is None:
                processType = 0
            if userId is None:
                response_data['flag'] = 'user_id_error' 
                return response_data  
            try:
                userObjWithRepair = Admin.objects.get(admin_type=4,user_id=long(userId))
            except Exception,e:
                userObjWithRepair = None
            if int(processType)==3:
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,process_status=processType)
                else:
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,sender_id=long(userId),process_status=processType)
            else:
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4).exclude(process_status=3)
                else:
                    topicQuerySet = Topic.objects.filter(sender_community_id=communityId,topic_category_type=4,sender_id=long(userId)).exclude(process_status=3)
            topicIdList = []
            size = topicQuerySet.count()
            for i in range(0,size,1):
                topicIdList.append(topicQuerySet[i].getTopicId())
            if userObjWithRepair is not None:#表示此用户位物业管理员
                try:
                    for i in range(len(topicIdList)):
                        topicObjWithRepair = Topic.objects.get(topic_id=topicIdList[i],sender_community_id=communityId)
                        topicObjWithRepair.delete_type = 4  # 4表示物业管理员删除了，但用户可看
                        topicObjWithRepair.save()
                except:
                    response_data['flag'] = 'delete_all_repair_error' 
                    return response_data
            else:
                try:
                    for i in range(len(topicIdList)):
                        Praise.objects.filter(topic=topicIdList[i]).delete()
                        Media_files.objects.filter(topic_id=topicIdList[i]).delete()
                        Comment.objects.filter(topic_id=topicIdList[i]).delete()
                        CollectionTopic.objects.filter(topic_id=long(topicIdList[i])).delete()
                        try:
                            activityArray = Activity.objects.filter(topic_id=topicIdList[i])
                            if activityArray is not None:
                                actObj = activityArray[0]
                                aId = actObj.getActivityId()
                                EnrollActivity.objects.filter(activity_id=aId).delete()
                                actObj.delete()
                        except:
                            pass
                        Topic.objects.filter(topic_id=topicIdList[i],sender_community_id=communityId).delete()
                        delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicIdList[i])
                        os.popen(delFileString)
                except Exception,e:
                    response_data['Exception'] = str(Exception)
                    response_data['Error'] = str(e)
                    return response_data
            response_data['flag'] = 'ok'
            response_data['list'] = str(topicIdList)
            return response_data 
        else:
            response_data['flag'] = 'all_delete_error'
            return response_data
    else:
        if topicType is None:#删除帖子 不可删除收藏、帖子内容
            Praise.objects.filter(topic=topicId).delete()
            Media_files.objects.filter(topic_id=topicId).delete()
            Comment.objects.filter(topic_id=topicId).delete()
#             try:
#                 activityArray = Activity.objects.filter(topic_id=topicId)
#                 if activityArray is not None:
#                     actObj = activityArray[0]
#                     aId = actObj.getActivityId()
#                     EnrollActivity.objects.filter(activity_id=aId).delete()
#                     actObj.delete()
#             except:
#                 pass
#             CollectionTopic.objects.filter(topic_id=long(topicId)).delete()
#             Topic.objects.get(topic_id=topicId,sender_community_id=communityId).delete()
            topicObj = Topic.objects.get(topic_id=topicId,sender_community_id=communityId)
            topicObj.delete_type = 2 #表示该帖已经被删除
            topicObj.save()
            delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicId)
            os.popen(delFileString)
            
            AsyncDelTopic.delay(topicId,communityId)
            
        else:#表示删除的是物业报修帖子
            if int(topicType) == 4:
                if userId is None:
                    response_data['flag'] = 'user_id_error' 
                    return response_data  
                try:
                    userObjWithRepair = Admin.objects.get(admin_type=4,user_id=long(userId))
                except Exception,e:
                    userObjWithRepair = None
#                     response_data['flag'] = 'topic_repair_error' 
#                     response_data['Exception'] = str(Exception)
#                     response_data['Error'] = str(e)
#                     return HttpResponse(json.dumps(response_data), content_type="application/json")    
                if userObjWithRepair is not None:#表示此用户位物业管理员
                    try:
                        topicObjWithRepair = Topic.objects.get(topic_id=topicId,sender_community_id=communityId)
                        topicObjWithRepair.delete_type = 4  # 4表示物业管理员删除了，但用户可看
                        topicObjWithRepair.save()
                    except:
                        response_data['flag'] = 'topic_repair_error' 
                        return response_data
                else:
                    Praise.objects.filter(topic=topicId).delete()
                    Media_files.objects.filter(topic_id=topicId).delete()
                    Comment.objects.filter(topic_id=topicId).delete()
                    CollectionTopic.objects.filter(topic_id=long(topicId)).delete()
                    try:
                        activityArray = Activity.objects.filter(topic_id=topicId)
                        if activityArray is not None:
                            actObj = activityArray[0]
                            aId = actObj.getActivityId()
                            EnrollActivity.objects.filter(activity_id=aId).delete()
                            actObj.delete()
                    except:
                        pass
                    Topic.objects.filter(topic_id=topicId,sender_community_id=communityId).delete()
                    delFileString = 'rm -rf /opt/youlin_backend/media/youlin/res/' + str(userId) + '/topic/' + str(topicId)
                    os.popen(delFileString)
            else:
                response_data['flag'] = 'repair_error'
                return response_data
        response_data['flag'] = 'ok'
        return response_data

#设置活动报名
def ActivityEnroll(request):
    data = None
    listEnroll = []
    enrollData = []
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    enrollObj = EnrollActivity.objects.get_or_create(activity_id=data['activityId'],user_id=data['userId'],enrollUserCount=data['enrollUserCount'],\
                                        enrollNeCount=data['enrollNeCount'])
    count = None
    try:
        count = enrollTotal(data['activityId'])
    except:
        count = 0
    response_data = {}
    if enrollObj: 
        response_data['flag']    = 'ok'
        response_data['count']   = count
    else:
        response_data['flag']    = 'no' 
    return response_data

#取消活动报名
def CancelEnroll(request):
    response_data = {} 
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    try:
        EnrollActivity.objects.filter(activity_id=data['activityId'],user_id=data['userId']).delete()
        total = enrollTotal(data['activityId'])
        response_data['enrollTotal']= total
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return response_data

#报名详情
def DetailEnroll(request):
    data = None
    listEnroll = []
    enrollData = []
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    enrollLists = EnrollActivity.objects.filter(activity_id = data['activityId'])
    enrollSize = enrollLists.count()
    enrollTotal = 0
    for i in range(0,enrollSize,1):   
        userId = enrollLists[i].user_id
        userObj = User.objects.get(user_id = userId)
        enrollId = enrollLists[i].enroll_id
        enrollUserCount = enrollLists[i].enrollUserCount
        enrollNeCount = enrollLists[i].enrollNeCount
        total = enrollNeCount+enrollUserCount
        enrollDict = getEnrollActivityDict(enrollId,userId,userObj.user_nick,userObj.user_portrait,enrollUserCount,enrollNeCount,total)
        listEnroll.append(enrollDict)
        enrollTotal = total + enrollTotal
        
        
    
    enrollData = getEnrollDataDict(data['activityId'],enrollTotal,listEnroll)  
    return enrollData

#获取帖子是否被删除
def GetTopicDeleteStatus(request):
    response_data = {}
    userId      = request.POST.get('user_id', None)
    communityId = request.POST.get('community_id', None)
    topicId     = request.POST.get('topic_id', None)
    senderId    = request.POST.get('sender_id', None)
    
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
    if long(senderId) in blackList:
        response_data['flag'] = 'black'
        return response_data
    
    try:
        topicObj = Topic.objects.get(sender_community_id=long(communityId),topic_id=long(topicId))
        deleteType = topicObj.delete_type
        if deleteType is None:
            deleteType = 0
        if '2' == str(deleteType):
            response_data['flag'] = 'no'
        else:
            response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return response_data

#举报帖子
def ReportTopicHandle(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    topicDetailList = []
    newReportId = None
    if request.method == 'POST':
        topicId        = request.POST.get('topic_id')
        complainUserId = request.POST.get('complain_id')
        senderUserId   = request.POST.get('sender_id')
        communityId    = request.POST.get('community_id')
        title          = request.POST.get('title')
        content        = request.POST.get('content')
    else:
        topicId        = request.GET.get('topic_id')
        complainUserId = request.GET.get('complain_id')
        senderUserId   = request.GET.get('sender_id')
        communityId    = request.GET.get('community_id')
        title          = request.GET.get('title')
        content        = request.GET.get('content')
    
    try:
        topObj = Topic.objects.get(topic_id = long(topicId))
        delete_type = topObj.delete_type
        try:
            delType = int(delete_type)
            if delType == 2:
                response_data = {}
                response_data['flag'] = 'none'   
                return response_data
        except:
            pass
    except:
        response_data = {}
        response_data['flag'] = 'none'   
        return response_data
    curTime = long(time.time()*1000)
    
    reportObj = ReportTopic(topic_id=long(topicId),complain_user_id=long(complainUserId),\
                            sender_user_id=long(senderUserId),community_id=long(communityId),\
                            title=title,content=content,time=curTime)
    reportObj.save()
    newReportId = reportObj.getReportId()
    try:
        reportCount = ReportTopic.objects.filter(topic_id=long(topicId),community_id=long(communityId)).count()
    except:
        reportCount = 0
    reportInterval = 2
    if int((reportCount%reportInterval) < (reportInterval-1)):    
        response_data = {}
        response_data['flag'] = 'ok'   
        return response_data
    userObj = User.objects.get(user_id=senderUserId)
    topicObj = Topic.objects.get(topic_id=topicId)
    try:
        topicTitle = topicObj.topic_title
    except:
        topicTitle = None
    try:
        topicContent = topicObj.topic_content
    except:
        topicContent = None
    try:
        senderNick = topicObj.sender_name
    except:
        senderNick = None
    try:
        senderAvatar = topicObj.sender_portrait
    except:
        senderAvatar = None
    try:
        topicTime = topicObj.topic_time
    except:
        topicTime = None
    if topicObj.send_status==1:
        img_count = Media_files.objects.filter(topic_id=topicId,comment_id=0).count()
    else:
        img_count = 0
    try:
        objectType = topicObj.object_data_id
        if objectType is None:
            objectType = 0
        elif objectType == 'null':
            objectType = 0
    except:
        objectType = 0
    try:
        deleteType = topicObj.delete_type
        if deleteType is None:
            deleteType = 0
        elif deleteType == 'null':
            deleteType = 0
    except:
        deleteType = 0
    topicTitleContent = topicTitle[8:] + '...'
    topicContentInfo = topicContent[200:] + '...'
    topicDetailList.append(getDTopicDetail(topicId,topicTitleContent,topicContentInfo,senderNick,img_count,senderAvatar,topicTime,objectType,deleteType))    
    
    config = readIni()
    tagSuffix = config.get("report", "tagSuffix")
    pushTitle = config.get("report", "pushTitle")
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    pTitle = config.get("report", "title")
    userAvatar = settings.RES_URL+'res/default/avatars/default-police.png'
    currentPushTime = long(time.time()*1000)
    userNick = userObj.user_nick.encode('utf-8')
    message1 = config.get("report", "content1") +" "+userNick+" "+config.get("report", "content2")+\
               topicTitleContent+config.get("report", "content3")+\
               pTitle+config.get("report", "content4")
    pushContent = str(topicId).encode('utf-8') + ":" \
                 +str(senderUserId).encode('utf-8') + ":" \
                 +str(communityId).encode('utf-8')
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,pTitle,message1,newReportId,communityId)
    recordId = createPushRecord(4,1,pTitle,message1,currentPushTime,1001,json.dumps(custom_content),communityId,1001)      
    custom_content = getCustomDict(senderUserId,currentPushTime,pushTitle,userAvatar,topicId,pushContent,pTitle,message1,newReportId,communityId,recordId,topicDetailList)

    AsyncReportTopic.delay(apiKey, secretKey, tagSuffix, communityId, custom_content, message1, pTitle)
    
    response_data = {}
    response_data['flag'] = 'ok'   
    return response_data

#添加收藏
def AddCollection(request):
    
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    response_data = {}

    try:
        userId = data['user_id']
        senderId = data['sender_id']
        topicId = data['topic_id']
        try:
            topObj = Topic.objects.get(topic_id = long(topicId))
            delete_type = topObj.delete_type
            try:
                delType = int(delete_type)
                if delType == 2:
                    response_data['flag'] = 'none'
                    return response_data
            except:
                pass
        except:
            response_data['flag'] = 'none'
            return response_data
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
        if long(senderId) in blackList:
            response_data['flag'] = 'black'
            return response_data
        
        CollectionTopic.objects.get_or_create(user_id = long(userId),topic_id = topicId,\
                                              community_id=data['community_id'],sender_id=long(senderId))
        response_data['flag'] = 'ok'
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['error'] = str(e)
    return response_data

#删除我的收藏
def DelMyCollection(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    try:
        userId = data['user_id']
        topicId = data['topic_id']
        communityId = data['community_id']
        topicObj = Topic.objects.get(topic_id=long(topicId),sender_community_id=long(communityId))
        senderId = topicObj.sender_id
        
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
        if long(senderId) in blackList:
            response_data['flag'] = 'black'
            return response_data
        
        CollectionTopic.objects.get(user_id = long(userId),topic_id = long(topicId),community_id=long(communityId)).delete()
        response_data['flag'] = 'ok'
        return response_data
    except Exception,e:
        response_data['flag'] = 'no'
        return response_data
    
#删除收藏
def DelCollection(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        data = request.GET.copy()
    try:
        userId = data['user_id']
        topicId = data['topic_id']
        communityId = data['community_id']
        topicObj = Topic.objects.get(topic_id=long(topicId),sender_community_id=long(communityId))
        senderId = topicObj.sender_id
        
        try:
            delete_type = topicObj.delete_type
            try:
                delType = int(delete_type)
                if delType == 2:
                    response_data['flag'] = 'none'
                    return response_data
            except:
                pass
        except:
            response_data['flag'] = 'none'
            return response_data
        
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
        if long(senderId) in blackList:
            response_data['flag'] = 'black'
            return response_data
        
        CollectionTopic.objects.get(user_id = long(userId),topic_id = long(topicId),community_id=long(communityId)).delete()
        response_data['flag'] = 'ok'
        return response_data
    except Exception,e:
        response_data['flag'] = 'no'
        return response_data

#获取收藏帖子
def GetCollectTopic(request):
    
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
        topicNum    = request.POST.get('count', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        topic_id    = request.GET.get('topic_id', None)
        topicNum    = request.GET.get('count', None)
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
    
    colQuerySet = CollectionTopic.objects.filter(user_id=userId,community_id=communityId)
    size = colQuerySet.count()
    topicIds = []
    if colQuerySet:
        for i in range(0,size,1):
             id = colQuerySet[i].topic_id
             topicIds.append(id)
        
        if topic_id is None:
            topicQuerySet = Topic.objects.filter(topic_id__in = topicIds).exclude(sender_id__in=blackList).order_by('-topic_id')[:topicNum]
        else:
            targetId = int(topic_id)
            topicQuerySet = Topic.objects.filter(topic_id__lt=targetId,topic_id__in = topicIds).exclude(sender_id__in=blackList).order_by('-topic_id')[:topicNum] #<
        size = topicQuerySet.count()
        
        for i in range(0,size,1):
            topicId = topicQuerySet[i].getTopicId()
            curTopciId = topicId
            forumId = topicQuerySet[i].forum_id
            forumName = topicQuerySet[i].forum_name
            senderId = topicQuerySet[i].sender_id
            try:
                remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
                senderName = remObj.user_remarks
            except:
                senderName = topicQuerySet[i].sender_name
            senderLevel = topicQuerySet[i].sender_lever
            senderPortrait=1
            senderPortrait = User.objects.get(user_id = senderId).user_portrait
            senderFamilyId =  topicQuerySet[i].sender_family_id
            senderFamilyAddr = topicQuerySet[i].sender_family_address
            topicTime = topicQuerySet[i].topic_time
            topicTitle = topicQuerySet[i].topic_title
            topicContent = topicQuerySet[i].topic_content
            topicCategoryType = topicQuerySet[i].topic_category_type
            commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
            likeNum = topicQuerySet[i].like_num
            circleType = topicQuerySet[i].circle_type
            visiableType = topicQuerySet[i].visiable_type
            sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
            viewNum = topicQuerySet[i].view_num
            hotFlag = topicQuerySet[i].hot_flag
            deleteType = topicQuerySet[i].delete_type
            communityId = topicQuerySet[i].sender_community_id
            communityLng = None#经度
            communityLag = None#维度
            try:
                communityObj = Community.objects.get(community_id=long(communityId))
                communityLng = communityObj.community_lng
                communityLag = communityObj.community_lat
            except Exception,e:
                communityLng = str(Exception)
                communityLag = str(e)
            displayName = None
            try:
                curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
                try:
                    curUserName = remObj.user_remarks
                except:
                    curUserName = senderName
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
                activityDict = getActivityDict(activityObj,total,enrollFlag,communityLng,communityLag)
                ListActivity.append(activityDict)
            elif objectType == 3:  # news
                try:
                    newsObj = News.objects.get(new_id = int(object_data))
                except:
                    newsObj = None
                servhost = request.get_host()
                new_url = 'http://'+servhost+SHARE_NEWS+str(object_data)
                tmp_pic_url = newsObj.new_small_pic
                if tmp_pic_url[:4]=='http':
                    pic_url = tmp_pic_url
                else:
                    pic_url = 'https://'+servhost+tmp_pic_url
                from web.models import Subscription
                subObj = Subscription.objects.get(community_id=long(communityId))
                newDict = getNewsDict(newsObj,pic_url,new_url,communityLng,communityLag,subObj)
                ListActivity.append(newDict)
            elif objectType == 4:  # change
                secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
                secondHandDict = getSecondDict(secondHandObj,communityLng,communityLag)
                ListActivity.append(secondHandDict)
            else:
                if 1 != int(senderId):
                    dicts = {}
                    dicts.setdefault('communityLng',communityLng)
                    dicts.setdefault('communityLag',communityLag)
                    ListActivity.append(dicts)
            if commentNum is None:
                ListComment = []
            else:
                commQuerySet = Comment.objects.filter(topic_id=long(curTopciId)).exclude(senderId__in=blackList).order_by('-comment_id')[:2]
                commSize = commQuerySet.count()
                for i in range(0,commSize,1):   
                    com_senderAddr = commQuerySet[i].senderAddress
                    com_senderFamilyId = commQuerySet[i].senderFamilyId
                    com_senderLevel = commQuerySet[i].senderLevel
                    com_commId = commQuerySet[i].getCommentId()
                    com_senderNcRoleId = commQuerySet[i].senderNcRoleId
                    com_sendTime = commQuerySet[i].sendTime
                    com_contentType = commQuerySet[i].contentType
                    com_senderId = commQuerySet[i].senderId
                    com_displayName = commQuerySet[i].displayName
                    com_content = commQuerySet[i].content
                    com_senderName = commQuerySet[i].senderName
                    com_topicId = commQuerySet[i].topic.getTopicId()
                    com_senderAvatar = commQuerySet[i].senderAvatar
                    commentDicts = genCommentDict(com_senderAddr,com_senderFamilyId,com_senderLevel,com_commId,com_senderNcRoleId,com_sendTime,\
                                                  com_contentType,com_senderId,com_displayName,com_content,com_senderName,com_topicId,com_senderAvatar)
                    ListComment.append(commentDicts)
            curSystemTime = long(time.time()*1000)
            if 1 == int(senderId):
                sayHelloStatus = 0
                try:
                    SayHello.objects.get(user_id=long(userId),topic_id=long(curTopciId))
                    sayHelloStatus = 1 #表示已经打过招呼
                except:
                    sayHelloStatus = 0 #表示没有打过招呼
                dicts = {}
                dicts.setdefault('sayHelloStatus',sayHelloStatus)
                dicts.setdefault('communityLng',communityLng)
                dicts.setdefault('communityLag',communityLag)
                ListActivity.append(dicts)
                topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                                 senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                                 communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                                 cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime,deleteType)
            else:
                topicDict = genResponseTopicDict(topicId,forumId,forumName,senderId,senderName,senderLevel,senderPortrait,displayName,praiseType,colStatus,\
                                                 senderFamilyId,senderFamilyAddr,topicTime,topicTitle,topicContent,topicCategoryType,objectType,\
                                                 communityId,commentNum,likeNum,circleType,visiableType,sendStatus,viewNum,hotFlag,\
                                                 cacheKey,ListMediaFile,ListComment,ListActivity,curSystemTime,deleteType)
            ListMerged.append(topicDict)
            ListComment = []
            ListActivity = []
            ListMediaFile = [] 
        if ListMerged:
            return ListMerged
        else:
            response_data = {}
            response_data['flag'] = 'no'#meiyou gengduo le
            return response_data
    else:
        response_data = {}
        response_data['flag'] = 'no2'
        return response_data
    
#获取我的和收藏个数    
def GetTopicCounts(request):
    myPostNum = None
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
    try:
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
        myPostNum = Topic.objects.filter(sender_id=long(userId),sender_community_id=communityId).exclude(topic_category_type=4).exclude(delete_type=2).count()
        mycollectNum = CollectionTopic.objects.filter(user_id=long(userId),community_id=communityId).exclude(sender_id__in=blackList).count()
        myCredit = User.objects.get(user_id=long(userId)).user_credit
    except:
        myPostNum = 0
        mycollectNum = 0
        myCredit = 0
        response_data['flag'] = 'no'
        response_data['myPost'] = myPostNum
        response_data['mycolNum'] = mycollectNum
        response_data['myCredit'] = myCredit
        return response_data
    if myPostNum is None:
        myPostNum = 0
    if mycollectNum is None:
        mycollectNum = 0
    if myCredit is None:
        myCredit = 0
    response_data['flag'] = 'ok'
    response_data['myPost'] = myPostNum
    response_data['mycolNum'] = mycollectNum
    response_data['myCredit'] = myCredit
    return response_data

#获取举报详情
def GetReportInfo(request):
    ListMerged = []
    response_data = {}
    if request.method == 'POST':
        user_id  = request.POST.get('user_id', None)
        topic_id = request.POST.get('topic_id', None)
    else:
        user_id  = request.GET.get('user_id', None)
        topic_id = request.GET.get('topic_id', None)
        
    reportQuerySet = ReportTopic.objects.filter(topic_id=long(topic_id)).order_by('title')
    size = reportQuerySet.count();
    if size <= 0:
        response_data['flag'] = 'none' 
        return response_data
    for i in range(0,size,1):
        complain_user_id = reportQuerySet[i].complain_user_id
        sender_user_id   = reportQuerySet[i].sender_user_id
        community_id     = reportQuerySet[i].community_id
        title            = reportQuerySet[i].title
        content          = reportQuerySet[i].content
        report_id        = reportQuerySet[i].getReportId()
        time             = reportQuerySet[i].time
        ListMerged.append(genReportDicts(complain_user_id,sender_user_id,community_id,title,content,report_id,time))
    return ListMerged

#分享小区新闻
def ShareCommunityNews(request):
    newsObj = None
    response_data = {}
    if request.method == 'POST':
        senderId    = request.POST.get('sender_id', None)
        recipyId    = request.POST.get('recipy_id', None)
        newsId      = request.POST.get('news_id', None)
        communityId = request.POST.get('community_id', None)
    else:
        senderId    = request.GET.get('sender_id', None)
        recipyId    = request.GET.get('recipy_id', None)
        newsId      = request.GET.get('news_id', None)
        communityId = request.GET.get('community_id', None)
    try:
        BlackList.objects.get(user_id=long(recipyId),black_id=long(senderId))
        response_data['flag'] = 'black'
        return response_data
    except:
        pass
    try:
        newsObj = News.objects.get(new_id = newsId,community_id=long(communityId))
    except:
        newsObj = None
        response_data['flag'] = 'no_id'
        return response_data
    servhost = request.get_host()
    new_url = 'http://'+servhost+SHARE_NEWS+str(newsId)
    tmp_pic_url = newsObj.new_small_pic
    if tmp_pic_url[:4]=='http':
        pic_url = tmp_pic_url
    else:
        pic_url = 'https://'+servhost+tmp_pic_url
    userNick = None
    user_portrait = None
    try:
        userObj = User.objects.get(user_id=long(senderId))
        userNick = userObj.user_nick
        user_portrait = userObj.user_portrait
    except:
        userNick = None
        
    config = readIni()
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    
    if userNick is None:
        pushTitle = '匿名'
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    else:
        pushTitle = userNick
        userAvatar = user_portrait
    pushContent = config.get("news", "content2")
    currentPushTime = long(time.time()*1000)
    
    customContent = getShareNewsDict(newsObj,pic_url,new_url,3001,userNick,userAvatar,1,5,currentPushTime,pushTitle,pushContent,communityId,None)
    recordId = createPushRecord(1,5,pushTitle,pushContent,currentPushTime,3001,json.dumps(customContent),communityId,3001)
    customContent = getShareNewsDict(newsObj,pic_url,new_url,3001,userNick,userAvatar,1,5,currentPushTime,pushTitle,pushContent,communityId,recordId)
    
    AsyncShareCommunityNews.delay(apiKey, secretKey, alias, recipyId, customContent, pushContent, pushTitle)
    
    response_data['flag'] = 'ok'
    return response_data

#打招呼
def SayHelloFun(request):
    repUserId = None
    currentCommunityId = None
    if request.method == 'POST':
        topicId     = request.POST.get('topic_id')
        senderId    = request.POST.get('user_id')
        content     = request.POST.get('content')
    else:
        topicId     = request.GET.get('topic_id')
        senderId    = request.GET.get('user_id')
        content     = request.GET.get('content')
    blackList = []
    blkListOtherQuerySet = BlackList.objects.filter(black_id = long(senderId))
    blkListSize0 = blkListOtherQuerySet.count()
    for i in range(0,blkListSize0,1):
        blackList.append(blkListOtherQuerySet[i].user_id)
    blkListOwnQuerySet = BlackList.objects.filter(user_id = long(senderId))
    blkListSize1 = blkListOwnQuerySet.count()
    for i in range(0,blkListSize1,1):
        blackList.append(blkListOwnQuerySet[i].black_id)
    repUserId = Topic.objects.get(topic_id=long(topicId)).cache_key
    if long(repUserId) in blackList:
        response_data = {}
        response_data['flag'] = 'black'
        return response_data
    if len(blackList):
        usrObj = User.objects.get(user_id=senderId)
        currentCommunityId = usrObj.user_community_id
        senderAvatar = usrObj.user_portrait
        senderName = usrObj.user_nick
        senderFamilyId = usrObj.user_family_id
        senderLevel = usrObj.user_level
        try:
            frObj = FamilyRecord.objects.get(user_id=senderId,family_id=senderFamilyId)
        except:
            response_data = {}
            response_data['flag'] = 'no'
            return response_data
        
        SayHello.objects.create(topic_id=long(topicId),user_id=long(senderId))
        
        senderAddr = frObj.family_community  # community+block
        displayName = senderName+'@'+senderAddr
        curTime = long(time.time()*1000)
        commentObj = Comment.objects.create(content=content,topic_id=long(topicId),sendTime=curTime,replayId=-1,\
                                            senderId=long(senderId),senderNcRoleId=0,contentType=0)
        commentId = commentObj.getCommentId()
        commentObj.senderAddress = senderAddr
        commentObj.senderAvatar = senderAvatar
        commentObj.senderName = senderName
        commentObj.senderFamilyId = senderFamilyId
        commentObj.senderLevel = senderLevel
        commentObj.displayName = displayName
        commentObj.videoTime = 0
        commentObj.save() 
        commNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
    else:
        usrObj = User.objects.get(user_id=senderId)
        currentCommunityId = usrObj.user_community_id
        senderAvatar = usrObj.user_portrait
        senderName = usrObj.user_nick
        senderFamilyId = usrObj.user_family_id
        senderLevel = usrObj.user_level
        try:
            frObj = FamilyRecord.objects.get(user_id=senderId,family_id=senderFamilyId)
        except:
            response_data = {}
            response_data['flag'] = 'no'
            return response_data
        
        SayHello.objects.create(topic_id=long(topicId),user_id=long(senderId))
        
        senderAddr = frObj.family_community  # community+block
        displayName = senderName+'@'+senderAddr
        curTime = long(time.time()*1000)
        commentObj = Comment.objects.create(content=content,topic_id=long(topicId),sendTime=curTime,replayId=-1,\
                                            senderId=long(senderId),senderNcRoleId=0,contentType=0)
        commentId = commentObj.getCommentId()
        commentObj.senderAddress = senderAddr
        commentObj.senderAvatar = senderAvatar
        commentObj.senderName = senderName
        commentObj.senderFamilyId = senderFamilyId
        commentObj.senderLevel = senderLevel
        commentObj.displayName = displayName
        commentObj.videoTime = 0
        commentObj.save() 
        commNum = Comment.objects.filter(topic_id=topicId).count()
        
    AsyncAddCommentPush.delay(topicId,senderId,currentCommunityId,commNum)
    
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    config = readIni()
    alias = config.get("SDK", "youlin")
    currentPushTime = long(time.time()*1000)
    customTitle = senderName
    pushTitle = config.get("comment", "pushTitle")
    userAvatar = senderAvatar
    topicTitle = Topic.objects.get(topic_id=long(topicId)).topic_title
    topicType = 11 #欢迎专用
    message = senderName+config.get("comment", "content4")
    custom_content = getReplayDetailDict(senderId,repUserId,6,1,message,senderId,\
                                         currentPushTime,pushTitle,userAvatar,customTitle,topicId,topicType,currentCommunityId)
    recordId = createPushRecord(6,1,customTitle,message,currentPushTime,\
                                senderId,custom_content,currentCommunityId,senderId)
    custom_content = getReplayDetailDict(senderId,repUserId,6,1,message,senderId,\
                                         currentPushTime,pushTitle,userAvatar,customTitle,topicId,topicType,currentCommunityId,recordId)
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    currentAlias = alias + str(repUserId)
    
    AsyncReplayCommentPush.delay(apiKey,secretKey,custom_content,currentAlias,message,customTitle)
    
    response_data = {}
    response_data['flag'] = 'ok'
    response_data['commentId'] = commentId
    response_data['display'] = displayName
    response_data['commCount'] = commNum
    response_data['repUserId'] = repUserId
    response_data['repUserName'] = currentAlias
    return response_data

#获取系统时间
def GetSystemTime(request):
    response_data = {}
    response_data['system_time'] = long(time.time()*1000)
    return response_data

#获取公众号
def GetSubscription(request):
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
    else:
        community_id = request.GET.get('community_id')
    from web.models import Subscription
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    try:
        subObj = Subscription.objects.get(community_id=long(community_id))
        from core.settings import HOST_IP
        subUrl = HOST_IP + subObj.s_url
        scription = subObj.s_name
        response_data = {}
        response_data['flag'] = 'ok'
        response_data['yl_msg'] = '欢迎来到['+scription+']社区新闻'
        response_data['img_url'] = subUrl
        response_data['scription'] = scription
        return response_data
    except:
        response_data = {}
        response_data['flag'] = 'no'
        response_data['yl_msg'] = '当前小区未开通社区新闻'
        response_data['img_url'] = 'none'
        response_data['scription'] = 'none'
        return response_data
###################################################################################################
###################################################################################################
#添加旧物置换
def PostOldReplacement(request):
    data = {}
    curComId = None
    topicObj = None
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        title                          = request.POST.get('topic_title', None)
        topicObj                       = Topic.objects.create(topic_title=title)
        topicId                        = topicObj.getTopicId()
        topicObj.topic_content         = request.POST.get('topic_content', None)
        topicObj.topic_category_type   = request.POST.get('topic_category_type', None)
        topicObj.topic_time            = long(time.time()*1000)
        topicObj.forum_id              = request.POST.get('forum_id', None)
        topicObj.forum_name            = request.POST.get('forum_name', None)
        curSenderId                    = request.POST.get('sender_id', None)
        topicObj.sender_id             = curSenderId
        topicObj.sender_name           = request.POST.get('sender_name', None)
        topicObj.sender_lever          = request.POST.get('sender_lever', None)
        topicObj.sender_portrait       = request.POST.get('sender_portrait', None)
        topicObj.collect_status        = request.POST.get('sender_nc_role', None)
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
            curUserName = User.objects.get(user_id=long(curSenderId)).user_nick
            curCommunityName = Community.objects.get(community_id=long(curComId)).community_name
            topicObj.display_name      = curUserName + '@' + curCommunityName
        except:
            topicObj.display_name      = request.POST.get('display_name', None)
        if topicObj.object_data_id == '4':#置换
            createSecondHandle(topicId,request)
    topicObj.delete_type = 0
    topicObj.save()
    currentCommunityId = topicObj.sender_community_id
    user_id = topicObj.sender_id
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(user_id, topicId)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            mediaFileObj = Media_files(topic=topicObj, resId=1, comment_id=0, contentType='image')
            mediaFileObj.resPath = settings.RES_URL+'res/'+str(user_id)+'/topic/'+str(topicId)+'/'+ smaillImage
            mediaFileObj.save()
            
    AsyncAddTopic.delay(topicId, user_id, curComId, currentCommunityId)
    
    data['flag'] = "ok"
    data['topic_id'] = topicId
    data['user_id'] = user_id
    return data

def GenSingleOldReplaceDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,curSystemTime,price,communityName,\
                            favouriteInfo,viewNum,commentNum,likeType,likeNum,topicTime,mediaList,topicInfo,topicLabel,tradeStatus,buyerInfo):
    dicts = {}
    dicts.setdefault('communityName', communityName)
    dicts.setdefault('senderPortrait', senderPortrait)
    dicts.setdefault('topicTitle', topicTitle)
    dicts.setdefault('topicContent', topicContent)
    dicts.setdefault('userNick', displayName.split('@')[0])
    dicts.setdefault('sendData', sendData)
    dicts.setdefault('qualityGrade', qualityGrade)
    dicts.setdefault('price', price)
    dicts.setdefault('viewNum', viewNum)
    dicts.setdefault('commentNum', commentNum)
    dicts.setdefault('likeType', likeType)
    dicts.setdefault('likeNum', likeNum)
    dicts.setdefault('mediaList', mediaList)
    dicts.setdefault('topicInfo', topicInfo)
    dicts.setdefault('topicTime',topicTime)
    dicts.setdefault('systemTime',curSystemTime)
    dicts.setdefault('topicType',topicLabel)
    dicts.setdefault('tradeStatus',tradeStatus)
    dicts.setdefault('favouriteInfo',favouriteInfo)
    dicts.setdefault('buyerInfo',buyerInfo)
    return dicts

def GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,curSystemTime,\
                          price,viewNum,commentNum,likeType,likeNum,topicTime,mediaList,topicInfo,topicLabel,favouriteInfo=None,tradeStatus=None):
    dicts = {}
    dicts.setdefault('senderPortrait', senderPortrait)
    dicts.setdefault('topicTitle', topicTitle)
    dicts.setdefault('topicContent', topicContent)
    dicts.setdefault('displayName', displayName)
    dicts.setdefault('sendData', sendData)
    dicts.setdefault('qualityGrade', qualityGrade)
    dicts.setdefault('price', price)
    dicts.setdefault('viewNum', viewNum)
    dicts.setdefault('commentNum', commentNum)
    dicts.setdefault('likeType', likeType)
    dicts.setdefault('likeNum', likeNum)
    dicts.setdefault('mediaList', mediaList)
    dicts.setdefault('topicInfo', topicInfo)
    dicts.setdefault('topicTime',topicTime)
    dicts.setdefault('systemTime',curSystemTime)
    dicts.setdefault('topicType',topicLabel)
    if favouriteInfo is not None:
        dicts.setdefault('favouriteNum',favouriteInfo)
    if tradeStatus is not None:
        dicts.setdefault('tradeStatus',tradeStatus)
    return dicts

#获取旧物帖子详情
def GetSingleOldReplace(request):
    praiseObj = None
    curTopciId = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListComment = []
    ListMediaFile = []
    ListActivity = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    if topicId is None:
        topicId = 0
    targetId = int(topicId)    
    if adminType is None:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2)
    elif int(adminType)==2:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(delete_type=2)
    else:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2)
    size = topicQuerySet.count()
    for i in range(0,size,1):
        topicId = topicQuerySet[i].getTopicId()
        curTopciId = topicId
        forumId = topicQuerySet[i].forum_id
        forumName = topicQuerySet[i].forum_name
        senderId = topicQuerySet[i].sender_id
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = topicQuerySet[i].sender_name
        senderLevel = topicQuerySet[i].sender_lever
        senderPortrait = User.objects.get(user_id = senderId).user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        senderFamilyId =  topicQuerySet[i].sender_family_id
        senderFamilyAddr = topicQuerySet[i].sender_family_address
        topicTime = topicQuerySet[i].topic_time
        topicTitle = topicQuerySet[i].topic_title
        topicContent = topicQuerySet[i].topic_content
        topicCategoryType = topicQuerySet[i].topic_category_type
        commentNum = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        likeNum = topicQuerySet[i].like_num
        circleType = topicQuerySet[i].circle_type
        visiableType = topicQuerySet[i].visiable_type
        sendStatus = topicQuerySet[i].send_status  # 1 is request mediafiles  
        viewNum = topicQuerySet[i].view_num
        hotFlag = topicQuerySet[i].hot_flag
        communityId = topicQuerySet[i].sender_community_id
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityObj = Community.objects.get(community_id=long(communityId))
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = Community.objects.get(community_id=long(communityId)).community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = topicQuerySet[i].display_name
        cacheKey = topicQuerySet[i].cache_key
        objectType = topicQuerySet[i].object_data_id
        object_data = topicQuerySet[i].object_type
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        if objectType == 4:  # change
            secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
            secondHandDict = getSecondDict(secondHandObj,communityLng,communityLag)
            ListActivity.append(secondHandDict)
        else:
            dicts = {}
            dicts.setdefault('communityLng',communityLng)
            dicts.setdefault('communityLag',communityLag)
            ListActivity.append(dicts)
        buyerInfo = []
        favourQuerySet = FavouriteList.objects.filter(topic=long(topicId),status=3)
        favourLength = favourQuerySet.count()
        for j in range(0,favourLength,1):
            tmpUserObj = User.objects.get(user_id = favourQuerySet[j].user)
            buyerDict = {}
            buyerDict['userId'] = tmpUserObj.getTargetUid()
            buyerDict['userNick'] = tmpUserObj.user_nick
            imgUrl = tmpUserObj.user_portrait
            if imgUrl is None or imgUrl=='null' or imgUrl=='NULL':
                imgUrl = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
            buyerDict['userPortrait'] = imgUrl
            buyerDict['userAddress'] = tmpUserObj.user_family_address
            buyerInfo.append(buyerDict)
        favouriteInfo = []
        favourQuerySet = FavouriteList.objects.filter(topic=long(topicId),status=1)
        favourLength = favourQuerySet.count()
        for k in range(0,favourLength,1):
            tmpUserObj = User.objects.get(user_id = favourQuerySet[k].user)
            favouriteDict = {}
            favouriteDict['userId'] = tmpUserObj.getTargetUid()
            favouriteDict['userNick'] = tmpUserObj.user_nick
            imgUrl = tmpUserObj.user_portrait
            if imgUrl is None or imgUrl=='null' or imgUrl=='NULL':
                imgUrl = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
            favouriteDict['userPortrait'] = imgUrl
            favouriteInfo.append(favouriteDict)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['communityId'] = communityId
        if int(secondHandDict['oldornew'])==0:
            qualityGrade = u'全新'
        elif int(secondHandDict['oldornew'])==1:
            qualityGrade = u'九成新'
        elif int(secondHandDict['oldornew'])==2:
            qualityGrade = u'八成新'
        elif int(secondHandDict['oldornew'])==3:
            qualityGrade = u'七成新'
        elif int(secondHandDict['oldornew'])==4:
            qualityGrade = u'六成新'
        elif int(secondHandDict['oldornew'])==5:
            qualityGrade = u'五成新'
        elif int(secondHandDict['oldornew'])==6:
            qualityGrade = u'五成新以下'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        topicLabel = secondHandDict['label']
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        if long(senderId) == long(userId):#表明是发布者
            #交易状态  1 上架中 2 洽谈中 3 下架  secondHandDict['tradeStatus']
            topicTradeStatus = secondHandDict['tradeStatus']
            if int(topicTradeStatus)==1 or int(topicTradeStatus)==2:
                topicTradeStatus = '下架商品'
            elif int(topicTradeStatus)==3:
                topicTradeStatus = '重新发布'
            elif int(topicTradeStatus)==4:
                topicTradeStatus = '联系买家'
        else:#表明是买家
            #查找我喜欢的表中有相关的买家操作状态
            try:
                #证明当前用户已经喜欢了该物品  #1我想要  2洽谈中  3取消交易
                favourObj = FavouriteList.objects.get(topic=long(topicId),user=long(userId))
                if int(favourObj.status)==1:
                    topicTradeStatus = '洽谈中'
                elif int(favourObj.status)==2:
                    topicTradeStatus = '我想要'
                elif int(favourObj.status)==3:
                    topicTradeStatus = '联系物主'
            except:
                #证明当前用户尚未喜欢该物品
                topicTradeStatus = '我想要'
        topicDict = GenSingleOldReplaceDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,curSystemTime,secondHandDict['price'],curCommunityName,\
                                            favouriteInfo,viewNum,commentNum,likeType,likeNum,topicTime,ListMediaFile,topicInfoDict,topicLabel,topicTradeStatus,buyerInfo)
        ListMerged.append(topicDict)
        ListComment = []
        ListActivity = []
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data
#详情页返回后，判断该旧物置换是否可见，如果可见则返回详细细节
def CheckMyOldTakeback(request):
    response_data = {}
    ListMediaFile = [] 
    if request.method == 'POST':
        userId  = request.POST.get('user_id', None)
        topicId = request.POST.get('topic_id', None)
    else:
        userId  = request.GET.get('user_id', None)
        topicId = request.GET.get('topic_id', None)
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
    try:
        topicQuertSet = Topic.objects.filter(topic_id=topicId,object_data_id=4,topic_category_type=2).exclude(sender_id__in=blackList).exclude(delete_type=2)
        topicLength = topicQuertSet.count()
        topicObj = topicQuertSet[0]
        forumId      = topicObj.forum_id
        senderId     = topicObj.sender_id
        topicTime    = topicObj.topic_time
        topicTitle   = topicObj.topic_title
        topicContent = topicObj.topic_content
        sendStatus   = topicObj.send_status
        viewNum      = topicObj.view_num
        secondObj = SecondHand.objects.get(topic_id=long(topicId))
        topicLabel   = secondObj.label
        price        = secondObj.price
        oldornew     = secondObj.oldornew
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).count()
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        favourQuerySet = FavouriteList.objects.filter(topic=long(topicId),status=1)
        favourLength = favourQuerySet.count()
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel,favourLength)
        
        response_data['flag'] = 'ok'
        response_data['info'] = topicDict
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['length'] = topicLength
        response_data['error'] = str(e)
    return response_data
        
#获取我收摊的旧物置换帖子
def GetMyOldTakeback(request):
    praiseObj = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)

    from django.db import connection
    cursor = connection.cursor()
    if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus = 3 \
                            and A.object_data_id=4 and topic_category_type=2 and A.sender_id = "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus = 3 and \
                            A.topic_id < "+str(topicId)+" and A.object_data_id=4 and  A.sender_id = "+str(userId)+" \
                            and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
    else:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus = 3 and \
                            A.delete_type <> 2 and A.object_data_id=4 and A.sender_id = "+str(userId)+" and \
                            topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus = 3 and \
                            A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                            and A.topic_id < "+str(topicId)+" and A.sender_id = "+str(userId)+" order by A.topic_id desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).count()
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data

#获取我发的在卖的旧物置换帖子
def GetMyOldReplacement(request):
    praiseObj = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)

    from django.db import connection
    cursor = connection.cursor()
    if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 \
                            and A.object_data_id=4 and topic_category_type=2 and A.sender_id = "+str(userId)+" \
                            and B.tradeStatus <> 4 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                            A.topic_id < "+str(topicId)+" and A.object_data_id=4 and  A.sender_id = "+str(userId)+" \
                            and topic_category_type=2 and B.tradeStatus <> 4 and A.sender_community_id = "+str(communityId)+" \
                            order by A.topic_id desc limit 6")
    else:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                            A.delete_type <> 2 and A.object_data_id=4 and A.sender_id = "+str(userId)+" and \
                            topic_category_type=2 and B.tradeStatus <> 4 and A.sender_community_id = "+str(communityId)+" \
                            order by A.topic_id desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                            A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and B.tradeStatus <> 4 \
                            and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id = "+str(userId)+" order by A.topic_id desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data

#获取旧物置换帖子
def GetOldReplacement(request):
    praiseObj = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    from django.db import connection
    cursor = connection.cursor()
    if len(blackList)==0:#证明没用被加入黑名单
        if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 \
                                and A.object_data_id=4 and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                                and B.tradeStatus <> 4 order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and B.tradeStatus <> 4 \
                                and A.topic_id < "+str(topicId)+" and A.object_data_id=4 and A.sender_community_id = "+str(communityId)+" \
                                and topic_category_type=2 order by A.topic_id desc limit 6")
        else:
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and B.tradeStatus <> 4 \
                                and A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                                order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and B.tradeStatus <> 4 \
                                and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                order by A.topic_id desc limit 6")
    else:
        blackUserId = ''
        for i in blackList:
            blackUserId = blackUserId + str(i) + ','
        blackUserId = blackUserId[:-1]
        if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                and B.tradeStatus <> 4 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                and B.tradeStatus <> 4 and A.topic_id < "+long(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                order by A.topic_id desc limit 6")
        else:
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                                and B.tradeStatus <> 4 and A.sender_id not in ("+blackUserId+") order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and B.tradeStatus <> 4 \
                                and A.sender_id not in ("+blackUserId+") and A.sender_community_id = "+str(communityId)+" \
                                and A.topic_id < "+long(topicId)+" order by A.topic_id desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data

#搜索旧物置换帖子
def SearchOldReplace(request):
    praiseObj = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        incontent   = request.POST.get('incontent', None) #包含哪些内容
        adminType   = request.POST.get('type', None)
        topicType   = request.POST.get('topic_type', None)#0其他1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        incontent   = request.GET.get('incontent', None) #包含哪些内容
        adminType   = request.GET.get('type', None)
        topicType   = request.GET.get('topic_type', None)#0其他1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
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
    from django.db import connection
    cursor = connection.cursor()
    if topicType is None:
        if len(blackList)==0:#证明没用被加入黑名单
            if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 \
                                    and A.object_data_id=4 and topic_category_type=2 and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.topic_id < "+str(topicId)+" and A.object_data_id=4 and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 and A.topic_id < \
                                    "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' order by A.topic_id desc limit 6")
        else:
            blackUserId = ''
            for i in blackList:
                blackUserId = blackUserId + str(i) + ','
            blackUserId = blackUserId[:-1]
            if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' and A.sender_community_id = "+str(communityId)+" \
                                    order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                    and A.topic_id < "+long(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' order by A.topic_id desc limit 6")
            else:
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 \
                                    and A.sender_id not in ("+blackUserId+") and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 \
                                    and A.sender_id not in ("+blackUserId+") and A.topic_id < "+long(topicId)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' and A.sender_community_id = "+str(communityId)+" \
                                    order by A.topic_id desc limit 6")
    else:
        if len(blackList)==0:#证明没用被加入黑名单
            if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 \
                                    and A.object_data_id=4 and topic_category_type=2 and B.label = "+str(topicType)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' and A.sender_community_id = "+str(communityId)+" \
                                    order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.topic_id < "+str(topicId)+" and A.object_data_id=4 and B.label = "+str(topicType)+" \
                                    and topic_category_type=2 and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and B.label = "+str(topicType)+" \
                                    and topic_category_type=2 and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 \
                                    and A.topic_id < "+str(topicId)+" and B.label = "+str(topicType)+" and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
        else:
            blackUserId = ''
            for i in blackList:
                blackUserId = blackUserId + str(i) + ','
            blackUserId = blackUserId[:-1]
            if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' and A.sender_community_id = "+str(communityId)+" \
                                    order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                    and A.topic_id < "+long(topicId)+" and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' \
                                    and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                if long(topicId)==0:#初始化
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 or A.delete_type is null and A.object_data_id=4 and topic_category_type=2 \
                                    and A.sender_id not in ("+blackUserId+") and A.sender_community_id = "+str(communityId)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' order by A.topic_id desc limit 6")
                else:
                    cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                    A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                    left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                    A.delete_type <> 2 or A.delete_type is null and A.object_data_id=4 and topic_category_type=2 \
                                    and A.sender_id not in ("+blackUserId+") and A.topic_id < "+long(topicId)+" \
                                    and A.topic_title like '%%"+incontent.encode('utf-8')+"%%' and A.sender_community_id = "+str(communityId)+" \
                                    order by A.topic_id desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data
    
#按类型获取旧物置换帖子
def GetOldReplaceWithType(request):
    praiseObj = None
    json_data = []
    ListMerged = []
    mediaDict = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
        topicType   = request.POST.get('topic_type', None)#0其他1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
        topicType   = request.GET.get('topic_type', None)#0其他1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
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
    from django.db import connection
    cursor = connection.cursor()
    if len(blackList)==0:#证明没用被加入黑名单
        if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 \
                                and A.object_data_id=4 and topic_category_type=2 and B.label = "+str(topicType)+" \
                                and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.topic_id < "+str(topicId)+" and A.object_data_id=4 and B.label = "+str(topicType)+" \
                                and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
        else:
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 and A.object_data_id=4 and B.label = "+str(topicType)+" \
                                and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 and A.object_data_id=4 and topic_category_type=2 \
                                and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                and B.label = "+str(topicType)+" order by A.topic_id desc limit 6")
    else:
        blackUserId = ''
        for i in blackList:
            blackUserId = blackUserId + str(i) + ','
        blackUserId = blackUserId[:-1]
        if int(adminType)==2:#表示管理员可以看到已经删除的的帖子
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                and A.sender_community_id = "+str(communityId)+" order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.sender_id not in ("+blackUserId+") and A.object_data_id=4 and topic_category_type=2 \
                                and A.topic_id < "+long(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                                order by A.topic_id desc limit 6")
        else:
            if long(topicId)==0:#初始化
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 or A.delete_type is null and A.object_data_id=4 and topic_category_type=2 \
                                and A.sender_id not in ("+blackUserId+") and A.sender_community_id = "+str(communityId)+" \
                                order by A.topic_id desc limit 6")
            else:
                cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                                A.like_num, A.send_status, A.view_num, B.label, B.price, B.oldornew from yl_topic as A \
                                left join yl_sencondhandle as B on A.topic_id = B.topic_id where B.tradeStatus <> 3 and \
                                A.delete_type <> 2 or A.delete_type is null and A.object_data_id=4 and topic_category_type=2 \
                                and A.sender_id not in ("+blackUserId+") and A.sender_community_id = "+str(communityId)+" \
                                and A.topic_id < "+long(topicId)+" order by A.topic_id desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                              curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                              ListMediaFile,topicInfoDict,topicLabel)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data = {}
    response_data['lists'] = ListMerged
    return response_data

#旧物置换上架商品 (只能是发布者)
def MyReplaceShelves(request):
    response_data = {}
    if request.method == 'POST':
        topicId = request.POST.get('topic_id', None) #加关注、取消关注的topicid
    else:
        topicId = request.GET.get('topic_id', None) #加关注、取消关注的topicid
    try:
        secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        secondHandObj.tradeStatus = 1
        secondHandObj.save()
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return response_data  

#设置交易完成时所需要的用户列表
def DealUserList(request):
    userList = []
    response_data = {}
    if request.method == 'POST':
        userId  = request.POST.get('user_id', None) #卖家的userId
        topicId = request.POST.get('topic_id', None) 
    else:
        userId  = request.GET.get('user_id', None)
        topicId = request.GET.get('topic_id', None)
    flQuertSet = FavouriteList.objects.filter(topic=long(topicId),sender=long(userId),status=1)
    size = flQuertSet.count()
    for i in range(0,size,1) :
        useid = flQuertSet[i].user
        userObj = User.objects.get(user_id=useid)
        dicts = {}
        dicts['user_nick'] = userObj.user_nick
        dicts['user_id'] = userObj.getTargetUid()
        portrait = userObj.user_portrait
        try:
            portrait = portrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            portrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        dicts['user_avatar'] = portrait
        dicts['user_address'] = userObj.user_family_address
        userList.append(dicts)
    response_data['lists'] = userList
    return response_data
#旧物置换交易完成商品 (只能是发布者)
def TransactionCompletion(request):
    response_data = {}
    if request.method == 'POST':
        buyUser = request.POST.get('buy_user', None) #买家的userId
        topicId = request.POST.get('topic_id', None) #加关注、取消关注的topicid   
    else:
        buyUser = request.GET.get('buy_user', None)
        topicId = request.GET.get('topic_id', None) #加关注、取消关注的topicid
    try:
        curSystemTime = long(time.time()*1000)
        secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        secondHandObj.tradeStatus = 4 #交易完成
        secondHandObj.save()
        flObj = FavouriteList.objects.get(topic=long(topicId),user=long(buyUser),status=1)
        flObj.status = 3 #1洽谈中  2取消交易 3交易完成
        flObj.time = curSystemTime
        flObj.save()
        response_data['flag'] = 'ok'
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['error'] = str(e)
    return response_data

#我的 我卖出的 交易完成的（卖家身份）
def GetSellWithFinish(request):
    response_data = {}
    ListMerged = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    from django.db import connection
    cursor = connection.cursor()
    if int(adminType) == 0:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 4 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id = "+str(userId)+" order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 4 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id = "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==2:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 4 and A.object_data_id=4 and topic_category_type=2 \
                            and A.sender_id = "+str(userId)+" and A.sender_community_id = "+str(communityId)+" \
                            order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 4 and A.object_data_id=4 and topic_category_type=2 \
                            and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id = "+str(userId)+" order by C.time desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        tradeStatus  = topicObj[6] # 1上架中 2洽谈中 3下架  4交易完成
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                          curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                          ListMediaFile,topicInfoDict,topicLabel,None,tradeStatus)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data['lists'] = ListMerged
    return response_data

#我的 我买到的 交易完成的（买家身份）
def GetBuyWithFinish(request):
    response_data = {}
    ListMerged = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    from django.db import connection
    cursor = connection.cursor()
    if int(adminType) == 0:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 3 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id <> "+str(userId)+" order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 3 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id <> "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==2:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 3 and A.object_data_id=4 and topic_category_type=2 \
                            and A.sender_id <> "+str(userId)+" and A.sender_community_id = "+str(communityId)+" \
                            order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 3 and A.object_data_id=4 and topic_category_type=2 \
                            and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id <> "+str(userId)+" order by C.time desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        tradeStatus  = topicObj[6] # 1上架中 2洽谈中 3下架  4交易完成
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                          curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                          ListMediaFile,topicInfoDict,topicLabel,None,tradeStatus)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data['lists'] = ListMerged
    return response_data
    
#洽谈中的我买的(买家身份)
def GetOldBuyWithTalks(request):
    response_data = {}
    ListMerged = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    from django.db import connection
    cursor = connection.cursor()
    if adminType is None:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id <> "+str(userId)+" order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id <> "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==0:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id <> "+str(userId)+" order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id <> "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==2:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.object_data_id=4 and topic_category_type=2 \
                            and A.sender_id <> "+str(userId)+" and A.sender_community_id = "+str(communityId)+" \
                            order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where C.status = 1 and A.object_data_id=4 and topic_category_type=2 \
                            and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id <> "+str(userId)+" order by C.time desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        tradeStatus  = topicObj[6] # 1上架中 2洽谈中 3下架  4交易完成
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                          curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                          ListMediaFile,topicInfoDict,topicLabel,None,tradeStatus)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data['lists'] = ListMerged
    return response_data    
    
#洽谈中的我卖的 （卖家身份）
def GetOldSellWithTalks(request):
    response_data = {}
    ListMerged = []
    ListMediaFile = []
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        topicId     = request.POST.get('topic_id', None) # 0 表示初始化  非0开始正式加载
        userId      = request.POST.get('user_id', None)
        adminType   = request.POST.get('type', None)
    else:
        communityId = request.GET.get('community_id', None)
        topicId     = request.GET.get('topic_id', None)
        userId      = request.GET.get('user_id', None)  
        adminType   = request.GET.get('type', None)
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
    from django.db import connection
    cursor = connection.cursor()
    if adminType is None:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_id = "+str(userId)+" and A.sender_community_id = "+str(communityId)+" \
                            order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id = "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==0:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.sender_id = "+str(userId)+" and A.sender_community_id = "+str(communityId)+" \
                            order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.delete_type <> 2 and A.object_data_id=4 \
                            and topic_category_type=2 and A.topic_id < "+str(topicId)+" and A.sender_id = "+str(userId)+" \
                            and A.sender_community_id = "+str(communityId)+" order by C.time desc limit 6")
    elif int(adminType)==2:
        if long(topicId)==0:#初始化
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.object_data_id=4 and topic_category_type=2 \
                            and A.sender_community_id = "+str(communityId)+" and A.sender_id = "+str(userId)+" order by C.time desc limit 6")
        else:
            cursor.execute("select A.topic_id, A.forum_id, A.sender_id, A.topic_time, A.topic_title, A.topic_content,\
                            B.tradeStatus, A.send_status, A.view_num, B.label, B.price, B.oldornew, C.time from yl_topic as A \
                            left join yl_sencondhandle as B on A.topic_id = B.topic_id left join yl_favouritelist as \
                            C on C.topic = A.topic_id where B.tradeStatus = 2 and A.object_data_id=4 and topic_category_type=2 \
                            and A.topic_id < "+str(topicId)+" and A.sender_community_id = "+str(communityId)+" \
                            and A.sender_id = "+str(userId)+" order by C.time desc limit 6")
    queryList = cursor.fetchall()
    for topicObj in queryList:
        topicId      = topicObj[0]
        forumId      = topicObj[1]
        senderId     = topicObj[2]
        topicTime    = topicObj[3]
        topicTitle   = topicObj[4]
        topicContent = topicObj[5]
        tradeStatus  = topicObj[6] # 1上架中 2洽谈中 3下架  4交易完成
        sendStatus   = topicObj[7]
        viewNum      = topicObj[8]
        topicLabel   = topicObj[9]
        price        = topicObj[10]
        oldornew     = topicObj[11]
        userObj      = User.objects.get(user_id = senderId)
        curComyId    = userObj.user_community_id
        communityObj = Community.objects.get(community_id=long(curComyId))
        commentNum   = Comment.objects.filter(topic_id=topicId).exclude(senderId__in=blackList).count()
        
        try:
            remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(senderId))
            senderName = remObj.user_remarks
        except:
            senderName = userObj.user_nick
        senderPortrait = userObj.user_portrait
        try:
            senderPortrait = senderPortrait.replace('123.57.9.62','www.youlinzj.cn')
        except:
            senderPortrait = None
        communityLng = None#经度
        communityLag = None#维度
        try:
            communityLng = communityObj.community_lng
            communityLag = communityObj.community_lat
        except Exception,e:
            communityLng = str(Exception)
            communityLag = str(e)
        displayName = None
        try:
            curCommunityName = communityObj.community_name
            try:
                curUserName = remObj.user_remarks
            except:
                curUserName = senderName
            displayName = curUserName + '@' + curCommunityName
        except:
            displayName = senderName + '@' + curCommunityName
        try:
            FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            likeType = 1 # his like
        except:
            likeType = 0 # no like
        likeNum = FavouriteList.objects.filter(topic=long(topicId),status=1).count()
        if sendStatus == 1:
            mediaFileObjs = Media_files.objects.filter(topic_id=topicId,comment_id=0)
            objLength = mediaFileObjs.count()
            for j in range(0,objLength,1):
                resId = mediaFileObjs[j].resId
                resPath = mediaFileObjs[j].resPath
                try:
                    resPath = resPath.replace('123.57.9.62','www.youlinzj.cn')
                except:
                    resPath = None
                contentType = mediaFileObjs[j].contentType
                mediaDicts = genMediaFilesDict(resId,resPath,contentType)
                ListMediaFile.append(mediaDicts)
        curSystemTime = long(time.time()*1000)
        topicInfoDict = {}
        topicInfoDict['communityLng'] = communityLng;
        topicInfoDict['communityLag'] = communityLag;
        topicInfoDict['topicId'] = topicId
        topicInfoDict['senderId'] = senderId
        topicInfoDict['communityId'] = curComyId
        if oldornew is None:
            oldornew = -1
        if int(oldornew)==0:
            qualityGrade = u'全新'
        elif int(oldornew)==1:
            qualityGrade = u'九成新'
        elif int(oldornew)==2:
            qualityGrade = u'八成新'
        elif int(oldornew)==3:
            qualityGrade = u'七成新'
        elif int(oldornew)==4:
            qualityGrade = u'六成新'
        elif int(oldornew)==5:
            qualityGrade = u'五成新'
        elif int(oldornew)==6:
            qualityGrade = u'五成新以下'
        else:
            qualityGrade = u'上传参数错误'
        from web.views_wx import sendTime
        sendData = sendTime(topicTime/1000)
        if likeNum is None or likeNum=='null' or likeNum=='NULL':
            likeNum = 0
        if topicLabel is None or topicLabel=='null' or topicLabel=='NULL':
            topicLabel = u'其他'
        elif int(topicLabel)==0:
            topicLabel = u'其他'
        elif int(topicLabel)==1:
            topicLabel = u'手机'
        elif int(topicLabel)==2:
            topicLabel = u'数码'
        elif int(topicLabel)==3:
            topicLabel = u'家用电器'
        elif int(topicLabel)==4:
            topicLabel = u'代步工具'
        elif int(topicLabel)==5:
            topicLabel = u'母婴用品'
        elif int(topicLabel)==6:
            topicLabel = u'服装鞋帽'
        elif int(topicLabel)==7:
            topicLabel = u'家具家居'
        elif int(topicLabel)==8:
            topicLabel = u'电脑'
        if senderPortrait is None or senderPortrait=='null' or senderPortrait=='NULL':
            senderPortrait = 'https://www.youlinzj.cn/media/youlin/res/default/avatars/default-normal-avatar.png'
        #交易状态  1上架 2交易中 3下架（交易完成）4下架（未交易）secondHandDict['tradeStatus']
        if viewNum is None or viewNum=='null' or viewNum=='NULL':
            viewNum = 0
        topicDict = GenOldReplacementDict(senderPortrait,topicTitle,topicContent,displayName,sendData,qualityGrade,\
                                          curSystemTime,price,viewNum,commentNum,likeType,likeNum,topicTime,\
                                          ListMediaFile,topicInfoDict,topicLabel,None,tradeStatus)
        ListMerged.append(topicDict)
        ListMediaFile = [] 
    response_data['lists'] = ListMerged
    return response_data

#判断是否下架、交易完成
def CheckSecondStatus(request):
    response_data = {}
    if request.method == 'POST':
        topicId      = request.POST.get('topic_id', None)
    else:
        topicId      = request.GET.get('topic_id', None)
    try:
        secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        #  1上架中 2洽谈中 3下架  4交易完成
        status = secondHandObj.tradeStatus 
        if int(status) == 1:
            response_data['flag'] = 'up'
        elif  int(status) == 3:
            response_data['flag'] = 'down'
        elif int(status) == 4:
            response_data['flag'] = 'finish'
    except:
        response_data['flag'] = 'error'
    return response_data

#点击我想要、我不想要
def MyFavourite(request):
    response_data = {}
    if request.method == 'POST':
        favourStatus = request.POST.get('favour_status', None) #1洽谈中 2取消交易
        userId       = request.POST.get('user_id', None) #加关注、取消关注的userid
        topicId      = request.POST.get('topic_id', None) #加关注、取消关注的topicid
        senderId     = request.POST.get('sender_id', None)
        communityId  = request.POST.get('community_id', None)
        adminType    = request.POST.get('user_type', None)
    else:
        favourStatus = request.GET.get('favour_status', None) 
        userId       = request.GET.get('user_id', None) #加关注、取消关注的userid
        topicId      = request.GET.get('topic_id', None) #加关注、取消关注的topicid
        senderId     = request.GET.get('sender_id', None)
        communityId  = request.GET.get('community_id', None)
        adminType    = request.GET.get('user_type', None)
    if int(favourStatus)==3:#卖家自己下架商品
        secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        secondHandObj.tradeStatus = 3
        secondHandObj.save()
        """
        flQuerySet = FavouriteList.objects.filter(topic=long(topicId),user=long(userId))
        flSize = flQuerySet.count()
        for i in range(0,flSize,1):
            flObj = flQuerySet[i]
            flObj.status = 2 #取消交易
            flObj.save()
        """
        response_data['status'] = 'ok'
        return response_data  
    #trade_status #1上架中  2洽谈中  3下架  
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
    if topicId is None:
        topicId = 0
    targetId = int(topicId)    
    if adminType is None:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2)
    elif int(adminType)==2:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,sender_community_id=long(communityId)).exclude(delete_type=2)
    else:
        topicQuerySet = Topic.objects.filter(topic_id=targetId,topic_category_type=2,object_data_id=4,sender_community_id=long(communityId)).exclude(sender_id__in=blackList).exclude(delete_type=2)
    size = topicQuerySet.count()
    if size == 0: #证明加入了黑名单
        response_data['status'] = 'black' #被加入了黑名单
        return response_data    
    try:
        secondHandObj = SecondHand.objects.get(topic_id=long(topicId))
        if int(secondHandObj.tradeStatus)==3:#表明已经下架
            response_data['status'] = 3 #表明已经下架
            return response_data    
    except:
        response_data['status'] = 'error' #异常
    try:
        curSystemTime = long(time.time()*1000)
        if int(favourStatus)==1:#当前操作是洽谈中
            favourTuple = FavouriteList.objects.get_or_create(topic=long(topicId),user=long(userId))
            if favourTuple[1]==True:#新创建的对象
                favourTuple[0].sender = senderId
                favourTuple[0].status = 1 #洽谈中
            else:#已经存在了
                favourTuple[0].status = 1 #洽谈中
            favourTuple[0].time = curSystemTime
            favourTuple[0].save()
            secondHandObj.tradeStatus = 2
            secondHandObj.save()
            status = 1
        elif int(favourStatus)==2:#当前操作时要取消关注    
            flObj = FavouriteList.objects.get(topic=long(topicId),user=long(userId),status=1)
            flObj.status = 2 #取消交易
            flObj.time = curSystemTime
            flObj.save()
            flQuerySet = FavouriteList.objects.filter(topic=long(topicId),status=1)
            if flQuerySet.count() == 0:#需要修改sencond的表中的状态
                secondHandObj.tradeStatus = 1
                secondHandObj.save()
            status = 2
    except Exception,e:
        response_data['error'] = str(e) # 操作失败
        response_data['status'] = 'failure' # 操作失败
    response_data['status'] = 'ok'
    return response_data    
        