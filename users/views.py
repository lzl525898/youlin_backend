# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from users.models import User,Admin,BlackList,Signin,Remarks,Invitation
from users.models import FamilyRecord
from addrinfo.models import AddressDetails
from addrinfo.models import City,Community,BuildNum,AptNum,Block
from community.models import Topic
from community.views import makeThumbnail,makeCircleAvatr,imgGenName
from users.models import GiftsList,Treasurebox,UserGiftsRecord
from push.models import PushRecord
from django.core import serializers
from django.conf import settings
from PIL import Image
import sys
import re
import os
import json
import time
import datetime
import random
import jpush as jpush
from push.views import createPushRecord,readIni
from push.sample import pushMsgToSingleDevice,pushMsgToTag
from users.easemob_server import registUser
from users.tasks import *
#测试专用
# def genBlockDict(community_id, community_name, block_id=None, block_name=None): 
#     block_dict = {}
#     if block_name is None:
#         block_dict.setdefault('pk',community_id)
#         block_dict.setdefault('community_name',community_name)
#         block_dict.setdefault('block_id',0)
#     else:
#         block_dict.setdefault('pk',community_id)
#         block_dict.setdefault('community_name',community_name+'-'+block_name)
#         block_dict.setdefault('block_name',block_name)
#         block_dict.setdefault('block_id',block_id)
#     return block_dict

def genBlockDict(community_id, community_name, block_id=None, block_name=None):
    block_dict = {}
    if block_name is None:
        #3为测试小区1   4为测试小区2
        if int(community_id) == 3 or int(community_id) == 4:
            return None
        else:
            block_dict.setdefault('pk',community_id)
            block_dict.setdefault('community_name',community_name)
            block_dict.setdefault('block_id',0)
    else:
        if int(community_id) == 3 or int(community_id) == 4:
            return None
        else:
            block_dict.setdefault('pk',community_id)
            block_dict.setdefault('community_name',community_name+'-'+block_name)
            block_dict.setdefault('block_name',block_name)
            block_dict.setdefault('block_id',block_id)
    return block_dict


# 1 user 2 address 3 property 4 topic
@api_view(['GET','POST'])
def registEasemob(request):
    if request.method == 'POST':
        userName = request.POST.get('user')
    else:
        userName = request.GET.get('user')
    response_data = registUser(userName,userName)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def handleBlackList(request):
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
        blackId  = request.POST.get('black_user_id', None)
        actionId = request.POST.get('action_id', None)  #添加为1，删除为2
    else:
        userId   = request.GET.get('user_id', None)
        blackId  = request.GET.get('black_user_id', None)
        actionId = request.GET.get('action_id', None)  #添加为1，删除为2
    if userId is None or blackId is None or actionId is None:
        response_data['flag'] = 'parameter_error'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if 1 == int(actionId):#添加用户
        BlackList.objects.get_or_create(user_id=long(userId),black_id=long(blackId))
    else:
        try:
            blackObj = BlackList.objects.get(user_id=long(userId),black_id=long(blackId))
            blackObj.delete()
        except:
            response_data['flag'] = 'del_error'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@api_view(['GET','POST'])
def setUserPushInfo(request):
    response_data = {}
    userObj = None
    uId = request.POST.get('user_id')
    userId = request.POST.get('push_user_id')
    channelId = request.POST.get('push_channel_id')
    try:
        userObj = User.objects.get(user_id=uId)
    except:
        response_data['flag'] = 'none'    # userObj not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    userObj.user_push_user_id = userId
    userObj.user_push_channel_id = channelId
    userObj.save()
    response_data = {}
    response_data['flag'] = 'ok'    # userObj not exist
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def genAdminContentDict(userId,userAvatar,title,content,contentType,pushTime,pushType,admin,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('content',content)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushType',pushType) # 1 user 2 address 3 property 4 topic
    dicts.setdefault('admin',admin)
    dicts.setdefault('communityId',communityId);
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

def genAdminDetailDict(userId,cityName,communityId,communityName,address,type):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('cityName',cityName)
    dicts.setdefault('communityId',communityId)
    dicts.setdefault('communityName',communityName)
    dicts.setdefault('address',address)
    dicts.setdefault('userType',type)
    return dicts

@api_view(['GET','POST'])
def setAdminPermiss(request):
    userID = None
    userObj = None
    ListAdmin = []
    if request.method == 'POST':
        adminType   = request.POST.get('type')
        phoneNumber = request.POST.get('phone')
        communityId = request.POST.get('community')
        cityId      = request.POST.get('city')
        blockId     = request.POST.get('blockId')
        buildnumId  = request.POST.get('buildnum')
    else:
        adminType   = request.GET.get('type')
        phoneNumber = request.GET.get('phone')
        communityId = request.GET.get('community')
        cityId      = request.GET.get('city')
        blockId     = request.GET.get('blockId')
        buildnumId  = request.GET.get('buildnum')
    try:
        userObj = User.objects.get(user_phone_number=phoneNumber)
    except:
        response_data = {}
        response_data['flag'] = 'none'    # userObj not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    userObj.user_type = int(adminType)
    userId = userObj.getTargetUid()
    adminTuple = Admin.objects.get_or_create(admin_type=adminType,city_id=cityId,community_id=communityId,\
                                block_id=blockId,buildnum_id=buildnumId,user_id=userId)
    adminObj = adminTuple[0]
    communityObj = Community.objects.get(community_id=communityId)
    cityName = communityObj.city.city_name
    communityName = communityObj.community_name
    address = cityName+communityName
    config = readIni()
    currentPushTime = long(time.time()*1000)
    if 1 == int(adminType):#admin
        pushTitle = config.get("users", "title")
        familyAddr = address.encode('utf-8')
        pushContent = config.get("users", "content1")+ familyAddr + config.get("users", "content2")
        ListAdmin.append(genAdminDetailDict(userId,cityName,communityId,communityName,address,1))
        userObj.user_json = json.dumps(ListAdmin)
        adminObj.admin_info = json.dumps(ListAdmin)
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,1,currentPushTime,1,ListAdmin,communityId)
        recordId = createPushRecord(1,1,pushTitle,pushContent,currentPushTime,userId,json.dumps(customContent),communityId,userId)
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,1,currentPushTime,1,ListAdmin,communityId,recordId) 
    elif 2 == int(adminType):#admin
        pushTitle = config.get("users", "title")
        familyAddr = address.encode('utf-8')
        pushContent = config.get("users", "content1")+ familyAddr + config.get("users", "content3")
        ListAdmin.append(genAdminDetailDict(userId,cityName,communityId,communityName,address,2))
        userObj.user_json = json.dumps(ListAdmin)
        adminObj.admin_info = json.dumps(ListAdmin)
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,communityId)
        recordId = createPushRecord(1,2,pushTitle,pushContent,currentPushTime,userId,json.dumps(customContent),communityId,userId)
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,communityId,recordId)
    elif 4 == int(adminType):#wuye
        pushTitle = config.get("users", "title")
        familyAddr = address.encode('utf-8')
        pushContent = config.get("users", "content4")+ familyAddr + config.get("users", "content5")
        ListAdmin.append(genAdminDetailDict(userId,cityName,communityId,communityName,address,4))
        userObj.user_json = json.dumps(ListAdmin)
        adminObj.admin_info = json.dumps(ListAdmin)
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,4,currentPushTime,1,ListAdmin,communityId)
        recordId = createPushRecord(1,4,pushTitle,pushContent,currentPushTime,userId,json.dumps(customContent),communityId,userId)
        customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,4,currentPushTime,1,ListAdmin,communityId,recordId)
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(userId)
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
        response_data['flag'] = 'no'
        response_data['info'] = 'push failed'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    userObj.save()
    adminObj.app_time = currentPushTime
    adminObj.save()
    response_data = {}
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def checkPhoneExist(request):
    if request.method == 'POST':
        phoneNumber = request.POST.get('phonenum')
    else:
        phoneNumber = request.GET.get('phonenum')
    targetObj = User.objects.filter(user_phone_number=phoneNumber)
    response_data = {}
    if targetObj:  # can't regist,exist
        response_data['flag']    = 'exist'
        response_data['user_id'] = targetObj[0].getTargetUid()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else: # can regist
        response_data['flag'] = 'ok'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def registNewUser(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        nick   = request.POST.get('nick')
        passwd = request.POST.get('password')
        phone  = request.POST.get('phonenum') 
        recomm = request.POST.get('recommend')# 0->normal 1->property 2->building
    else:
        gender = request.GET.get('gender')
        nick   = request.GET.get('nick')
        passwd = request.GET.get('password')
        phone  = request.GET.get('phonenum')
        recomm = request.GET.get('recommend')# 0->normal 1->property 2->building
    response_data = {}
    #AES解密
    
    key = (phone+'youli').encode("utf-8")
    iv = (phone+'youli').encode("utf-8")
    passwdstr = passwd.encode("utf-8")
    pwd = decrypt(passwdstr,key,iv)
    try:
        import hashlib
        hash = hashlib.md5()
    except ImportError:
        # for Python << 2.5
        import md5
        hash = md5.new()
    hash.update(pwd)
    value = hash.hexdigest()
    hash.update(value+phone.encode("utf-8"))  #md5(md5(pwd)+phone)
    passwd = hash.hexdigest()
    if 0 == int(recomm):
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=0)
        response_data['flag'] = user[1]
        response_data['user_id'] = user[0].getTargetUid()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif 1 == int(recomm):
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=1)
        response_data['flag'] = user[1]
        response_data['user_id'] = user[0].getTargetUid()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif 2 == int(recomm):
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=2)
        response_data['flag'] = user[1]
        response_data['user_id'] = user[0].getTargetUid()
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def checkIMEI(request):
    userObj = None
    imei = None
    response_data = {}
    if request.method == 'POST':
        IMEI = request.POST.get('imei', None)
    else:
        IMEI = request.GET.get('imei', None)
    try:
        userTuple = User.objects.filter(user_push_user_id=str(IMEI))
        imei = userTuple[0].user_push_user_id
    except:
        userTuple = None
    if userTuple is None:
        response_data['flag'] = 'no' # 需要重新登录
    else:
        response_data['flag'] = 'ok' # 可以直接跳转到main
    response_data['imei'] = imei
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def getPublicStatus(request):
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
        userId    = request.POST.get('user_id', None)
    else:
        userPhone = request.GET.get('user_phone', None)
        userId    = request.GET.get('user_id', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone,user_id=userId)
    except:
        response_data['flag'] = 'none'    # userObj not exist
        response_data['status'] = 0
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if userObj is not None:
        userStatus = userObj.user_public_status
        response_data['flag'] = 'ok'
        response_data['status'] = userStatus
    else:
        response_data['flag'] = 'ok'
        response_data['status'] = 0
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@api_view(['GET','POST'])
def checkPushChannelExist(request):
    userImei = None
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
    else:
        userPhone = request.GET.get('user_phone', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone)
        userImei = userObj.user_push_user_id
    except:
        response_data['flag'] = 'none'    # userObj not exist
        response_data['channelId'] = userImei 
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if userObj is not None:
        response_data['flag'] = 'ok'
    else:
        response_data['flag'] = 'no'
    response_data['channelId'] = userImei
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def setPhoneLogoff(request):
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
        user_id   = request.POST.get('user_id', None)
        status    = request.POST.get('status', None)
    else:
        userPhone = request.GET.get('user_phone', None)
        user_id   = request.GET.get('user_id', None)
        status    = request.GET.get('status', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone)
    except:
        response_data['flag'] = 'no'    # userObj not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if userObj is not None:
        userObj.user_push_user_id = None
        userObj.user_push_channel_id = None
        userObj.save()
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def genFamilyRecordDict(family_id,family_name,family_address,family_building_num,family_apt_num,\
                        is_family_member,family_member_count,primary_flag,user_avatar,city_name,fr_id,\
                        city_id,block_name,block_id,community_name,community_id,entityType,neStatus,\
                        city_code,apt_num_id,building_num_id):
    familyRecord_dict = {}
    familyRecord_dict.setdefault('family_id', family_id)
    familyRecord_dict.setdefault('family_name', family_name)
    familyRecord_dict.setdefault('family_address', family_address)
    familyRecord_dict.setdefault('family_building_num', family_building_num)
    familyRecord_dict.setdefault('family_apt_num', family_apt_num)
    familyRecord_dict.setdefault('is_family_member', is_family_member)
    familyRecord_dict.setdefault('family_member_count', family_member_count)
    familyRecord_dict.setdefault('primary_flag', primary_flag)
    familyRecord_dict.setdefault('user_avatar', user_avatar)
    familyRecord_dict.setdefault('city_name', city_name)
    familyRecord_dict.setdefault('city_id', city_id)
    familyRecord_dict.setdefault('block_name', block_name)
    familyRecord_dict.setdefault('block_id', block_id)
    familyRecord_dict.setdefault('community_name', community_name)
    familyRecord_dict.setdefault('community_id', community_id)
    familyRecord_dict.setdefault('entity_type', entityType)
    familyRecord_dict.setdefault('ne_status', neStatus)
    familyRecord_dict.setdefault('fr_id', fr_id)
    familyRecord_dict.setdefault('city_code', city_code)
    familyRecord_dict.setdefault('apt_num_id', apt_num_id)
    familyRecord_dict.setdefault('building_num_id', building_num_id)
    return familyRecord_dict

@api_view(['GET','POST'])
def getPersonalInfo(request):
    response_data = {}
    if request.method == 'POST':
        user_phone_number = request.POST.get('user_phone_number', None)
    else:
        user_phone_number = request.GET.get('user_phone_number', None)
    if user_phone_number is None:
        response_data['flag'] = 'none_i'    # user_id not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    userObj = None
    try:
        userObj = User.objects.filter(user_phone_number=user_phone_number)
    except:
        response_data['flag'] = 'none_o'    # userObj not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if userObj:
        json_data = []
        user_json = serializers.serialize("json", userObj)
        familyRecordObj = FamilyRecord.objects.filter(user=userObj)
        if familyRecordObj:
            user_string = user_json[:-1] + ','
            json_data.extend(user_string)
            familyRecordSize = familyRecordObj.count()
            if familyRecordSize == 0:
                pass
            else:
                for i in range(0,familyRecordSize,1):
                    try:
                        family_id = familyRecordObj[i].family.getAddrDetailId()
                    except:
                        family_id = None
                    frId = familyRecordObj[i].getFamilyRecordID()
                    family_name = familyRecordObj[i].family_name
                    family_address = familyRecordObj[i].family_address
                    family_building_num = familyRecordObj[i].family_building_num
                    family_apt_num = familyRecordObj[i].family_apt_num
                    is_family_member = familyRecordObj[i].is_family_member
                    family_member_count = familyRecordObj[i].family_member_count
                    primary_flag = familyRecordObj[i].primary_flag
                    user_avatar = familyRecordObj[i].user_avatar
                    city_name = familyRecordObj[i].family_city
                    city_id = familyRecordObj[i].family_city_id
                    block_name = familyRecordObj[i].family_block
                    block_id = familyRecordObj[i].family_block_id
                    community_name = familyRecordObj[i].family_community
                    community_id = familyRecordObj[i].family_community_id
                    entityType = familyRecordObj[i].entity_type 
                    neStatus = familyRecordObj[i].ne_status
                    if i+1 == familyRecordSize:
                        fr_json = json.dumps(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                 family_apt_num,is_family_member,family_member_count,\
                                                                 primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                 block_id,community_name,community_id,entityType,neStatus))+"]"
                        json_data.extend(fr_json)
                    else:
                        fr_json = json.dumps(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                 family_apt_num,is_family_member,family_member_count,\
                                                                 primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                 block_id,community_name,community_id,entityType,neStatus))+","
                        json_data.extend(fr_json)
        else:
            json_data.extend(user_json)
        return HttpResponse(json_data,content_type="application/json")   
    else: # query fail! not exist
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def loginUser(request):
    if request.method == 'POST':
        phoneNumber = request.POST.get('phonenum')
        passwd = request.POST.get('password')
    else:
        phoneNumber = request.GET.get('phonenum')
        passwd = request.GET.get('password')
    targetObj = User.objects.filter(user_phone_number=phoneNumber)
    response_data = {}
    #passwd='n7sA/YcnzTMsmTJ96o0Lqg=='
    #print passwd
    if targetObj:  # query ok! exist
        #AES解密
        key = (phoneNumber+'youli').encode("utf-8")
        iv = (phoneNumber+'youli').encode("utf-8")
        passwdstr = passwd.encode('utf-8')
        pwd = decrypt(str(passwdstr),key,iv)
        pwdnew = password_md5(pwd,phoneNumber)
        if (targetObj[0].user_password == pwdnew):
            json_data = []
            userObj = User.objects.filter(user_phone_number=phoneNumber)
            user_json = serializers.serialize("json", userObj)
            familyRecordObj = FamilyRecord.objects.filter(user=userObj)
            if familyRecordObj:
                user_string = user_json[:-1] + ','
                json_data.extend(user_string)
                familyRecordSize = familyRecordObj.count()
                if familyRecordSize == 0:
                    pass
                else:
                    for i in range(0,familyRecordSize,1):
                        try:
                            family_id = familyRecordObj[i].family.getAddrDetailId()
                        except:
                            family_id = None
                        frId = familyRecordObj[i].getFamilyRecordID()
                        family_name = familyRecordObj[i].family_name
                        family_address = familyRecordObj[i].family_address
                        family_building_num = familyRecordObj[i].family_building_num
                        family_apt_num = familyRecordObj[i].family_apt_num
                        is_family_member = familyRecordObj[i].is_family_member
                        family_member_count = familyRecordObj[i].family_member_count
                        primary_flag = familyRecordObj[i].primary_flag
                        user_avatar = familyRecordObj[i].user_avatar
                        city_name = familyRecordObj[i].family_city
                        city_id = familyRecordObj[i].family_city_id
                        block_name = familyRecordObj[i].family_block
                        block_id = familyRecordObj[i].family_block_id
                        community_name = familyRecordObj[i].family_community
                        community_id = familyRecordObj[i].family_community_id
                        entityType = familyRecordObj[i].entity_type 
                        neStatus = familyRecordObj[i].ne_status
                        if i+1 == familyRecordSize:
                            fr_json = json.dumps(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                     family_apt_num,is_family_member,family_member_count,\
                                                                     primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                     block_id,community_name,community_id,entityType,neStatus))+"]"
                            json_data.extend(fr_json)
                        else:
                            fr_json = json.dumps(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                     family_apt_num,is_family_member,family_member_count,\
                                                                     primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                     block_id,community_name,community_id,entityType,neStatus))+","
                            json_data.extend(fr_json)
            else:
                json_data.extend(user_json)
            return HttpResponse(json_data,content_type="application/json")
        else:
            response_data['flag'] = 'no1'
            return HttpResponse(json.dumps(response_data), content_type="application/json")   
    else: # query fail! not exist
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
#  1.family_id 2.family_name(b+a) 3.family_address(all) 4.family_address_id=0 5.family_building_num 6.family_apt_num
#  7.is_family_member 8.family_member_count 9.primary_flag 10.user_nick 11.user_avatar

@api_view(['GET','POST'])
def modifypwd(request):
    response_data = {}
    if request.method == 'POST':
        phoneNumber = request.POST.get('user_phone_number')
        newPasswd = request.POST.get('user_password')
        userId = request.POST.get('user_id')
        oldPasswd = request.POST.get('user_oldpassword')
    else:
        phoneNumber = request.GET.get('user_phone_number')
        newPasswd = request.GET.get('user_password')
        userId = request.GET.get('user_id')
        oldPasswd = request.GET.get('user_oldpassword')
        
    try:
        userObj = User.objects.get(user_phone_number=phoneNumber)
    except:
        response_data['flag'] = 'no_user'    # userObj not exist
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    #AES解密
    key = (phoneNumber+'youli').encode("utf-8")
    iv = (phoneNumber+'youli').encode("utf-8")
    #old
    oldPasswdstr = oldPasswd.encode('utf-8')
    oldPwd = decrypt(str(oldPasswdstr),key,iv)
    old_Pwd = password_md5(oldPwd,phoneNumber)
    if (userObj.user_password == old_Pwd):
         #new
        newPasswdstr = newPasswd.encode('utf-8')
        newPwd = decrypt(str(newPasswdstr),key,iv)
        new_Pwd = password_md5(newPwd,phoneNumber)
        userObj.user_password = new_Pwd
        userObj.save()
        response_data['flag'] = 'ok'    
        return HttpResponse(json.dumps(response_data), content_type="application/json") 
    else:
        response_data['flag'] = 'no'    
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def genUpdateContentDict(userId,userAvatar,title,content,contentType,pushTime,pushType,admin,communityId,srvimei=None,cliImei=None,recordId=None):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('content',content)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushType',pushType) # 1 user 2 address 3 property 4 topic
    dicts.setdefault('admin',admin)
    dicts.setdefault('communityId',communityId);
    if srvimei is not None:
        dicts.setdefault('srvimei',srvimei);
    if cliImei is not None:
        dicts.setdefault('cliImei',cliImei);
    return dicts

@api_view(['GET','POST'])
def updatePasswd(request):
    srvIMEI = None
    response_data = {}
    newpassword = None
    if request.method == 'POST':
        user_phone = request.POST.get('phone', None)
        imei = request.POST.get('imei', None)
        if user_phone is None:
            response_data['flag'] = 'none_p'    # phone not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        userObj = None
        try:
            userObj = User.objects.get(user_phone_number=user_phone)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if userObj:
            newpasswd = request.POST.get('password')
            key = (user_phone+'youli').encode("utf-8")
            iv = (user_phone+'youli').encode("utf-8")
            newpasswordstr = newpasswd.encode('utf-8')
            newpwd = decrypt(str(newpasswordstr),key,iv)
            newpassword = password_md5(newpwd,user_phone)
            userId = userObj.getTargetUid()
            communityId = userObj.user_community_id
            userPhoneNum = userObj.user_phone_number
            srvIMEI = userObj.user_push_user_id
            if srvIMEI is None:#表示用户已经注销登录
                pass
            else:#表示用户仍然处于登录状态
                if str(srvIMEI) == str(imei):#表示自己手机忘记密码
                    pass
                else: #其他手机忘记密
                    config = readIni()
                    currentPushTime = long(time.time()*1000)
                    pushTitle = config.get("users", "title")
                    pushContent = config.get("users", "content9")
                    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
                    customContent = genUpdateContentDict(userId,userAvatar,pushTitle,pushContent,3,currentPushTime,1,None,communityId,srvIMEI)
                    apiKey = config.get("SDK", "apiKey")
                    secretKey = config.get("SDK", "secretKey")
                    alias = config.get("SDK", "youlin")
                    _jpush = jpush.JPush(apiKey,secretKey) 
                    currentAlias = alias + str(userId)
                    pushExtra = customContent
                    push = _jpush.create_push()
                    push.audience = jpush.all_
                    push.audience = jpush.audience(
                        jpush.alias(currentAlias),
                    )
                    push.notification = jpush.notification(
                        android=jpush.android(pushContent,pushTitle,None,pushExtra)
                    )
                    push.options = {"time_to_live":0, "sendno":9527, "apns_production":True}
                    push.platform = jpush.all_
                    try:
                        push.send()
                    except:
                        pass
            userObj.user_password = newpassword
            userObj.user_push_user_id = None
            userObj.user_push_channel_id = None
            userObj.save()
            response_data['flag'] = 'ok'
            response_data['userId'] = userId
            response_data['phone'] = userPhoneNum
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['flag'] = 'no'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def uploadUserInfo(request):
    response_data = {}
    if request.method == 'POST':
        user_phone = request.POST.get('user_phone_number', None)
        if user_phone is None:
            response_data['flag'] = 'none_p'    # phone not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        user_id = request.POST.get('user_id', None)
        if user_id is None:
            response_data['flag'] = 'none_i'    # user_id not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        userObj = None
        try:
            userObj = User.objects.get(user_phone_number=user_phone, user_id=user_id)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if userObj:
            user_portrait = request.FILES.get('user_portrait', None)
            if user_portrait is None:
                pass
            else:
                fName = user_portrait.name
                fName = time.strftime('%m%d%M%S')+str(random.randint(1000,9999))+fName[fName.rfind('.'):]
                userDir = settings.MEDIA_ROOT+'youlin/res/'+str(user_id)+'/avatars/'
                filelist=[]
                if os.path.exists(userDir):
                    pass
                else:
                    try:
                        os.makedirs(userDir, mode=0777)
                    except OSError as exc:
                        if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                            pass
                        else:raise
                filelist=os.listdir(userDir)
                for f in filelist:
                    filepath = os.path.join(userDir, f)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                streamfile = open(userDir+fName, 'wb+')
                for chunk in user_portrait.chunks():
                    streamfile.write(chunk)
                streamfile.close()
                imgUrl = settings.RES_URL + 'res/' + str(user_id) + '/avatars/' + fName
                userObj.user_portrait = imgUrl
                #Topic.objects.filter(sender_id=user_id).update(sender_portrait=imgUrl)
            user_nick = request.POST.get('user_nick', None)
            if user_nick is None:
                pass
            else:
                userObj.user_nick = user_nick
            user_news_receive = request.POST.get('receive_status', None)
            if user_news_receive is None:
                pass
            else:
                userObj.user_news_receive = user_news_receive
            user_password = request.POST.get('user_password', None)
            if user_password is None:
                pass
            else:
                userObj.user_password = user_password
            user_gender = request.POST.get('user_gender', None)
            if user_gender is None:
                pass
            else:
                userObj.user_gender = user_gender
            user_family_id = request.POST.get('user_family_id', None)
            if user_family_id is None:
                pass
            else:
                userObj.user_family_id = user_family_id
            user_family_address = request.POST.get('user_family_address', None)
            if user_family_address is None:
                pass
            else:
                userObj.user_family_address = user_family_address
            user_birthday = request.POST.get('user_birthday', None)
            if user_birthday is None:
                pass
            else:
               userObj.user_birthday = user_birthday
            user_public_status = request.POST.get('user_public_status', None)
            if user_public_status is None:
               pass
            else:
               userObj.user_public_status = user_public_status
            user_vocation = request.POST.get('user_vocation', None)
            if user_vocation is None:
                pass
            else:
                userObj.user_profession = user_vocation
            user_level = request.POST.get('user_level', None)
            if user_level is None:
                pass
            else:
                userObj.user_level = user_level
            user_signature = request.POST.get('user_signature', None)
            if user_signature is None:
                pass
            else:
                userObj.user_signature = user_signature
            user_push_user_id = request.POST.get('imei', None)
            if user_push_user_id is None:
                pass
            else:
                userObj.user_push_user_id = user_push_user_id
            userObj.save()
            response_data['flag'] = 'ok'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['flag'] = 'none'    # user not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")

"""
#    json_data = serializers.serialize("json", UserFamily.objects.filter(user__user_id__contains=5))
#    json_data = serializers.serialize("json", User.objects.filter(USER__user=5))
#    json_data = serializers.serialize("json", User.USER.all())
#    json_data = serializers.serialize("json", UserFamily.objects.filter(user__user_id__exact=8))
#    json_data = serializers.serialize("json", UserFamily.objects.select_related('user'))
#    return HttpResponse(json.dumps(response_data), content_type="application/json") 
"""

@api_view(['GET','POST'])
def handleFamily(request):
    response_data = {}
    if request.method == 'POST':
        city_name    = request.POST.get('city_name', None)
        buildnum_id  = request.POST.get('buildnum_id', None)
        community_id = request.POST.get('community_id', None)
        block_id     = request.POST.get('block_id', None)
    else:
        city_name    = request.GET.get('city_name', None)
        buildnum_id  = request.GET.get('buildnum_id', None)
        community_id = request.GET.get('community_id', None)
        block_id     = request.GET.get('block_id', None)
    if city_name:
        json_data = []
        commObj = None
        cityObj = None
        try:
            cityObj = City.objects.filter(city_name__contains=city_name)
            commObj = Community.objects.filter(city__city_name__contains=city_name)
        except:
            response_data['flag'] = 'none_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if commObj:
            json_city = serializers.serialize("json", cityObj)
            json_city_str = json_city[:-1] + ','
            json_data.extend(json_city_str)
            size = commObj.count()
            for i in range(0,size,1):
                if i+1 == size:
                    comm_id = commObj[i].getCommunityId()
                    comm_name = commObj[i].community_name
                    blockObj = Block.objects.filter(community__community_id=comm_id)
                    blockSize = blockObj.count()
                    if blockSize == 0:
                        blockDict = genBlockDict(comm_id, comm_name)
                        if blockDict is None:
                            continue
                        jsonObj = json.dumps(blockDict)
                        json_data.extend(jsonObj)
                    for j in range(0,blockSize,1):
                        blockId = blockObj[j].getBlockId()
                        blockName = blockObj[j].block_name
                        blockDict = genBlockDict(comm_id, comm_name, blockId, blockName)
                        if blockDict is None:
                            continue
                        if j+1 == blockSize:
                            jsonObj = json.dumps(blockDict)
                            json_data.extend(jsonObj)
                        else:
                            jsonObj = json.dumps(blockDict)+','
                            json_data.extend(jsonObj)
                else:
                    comm_id = commObj[i].getCommunityId()
                    comm_name = commObj[i].community_name
                    blockObj = Block.objects.filter(community__community_id=comm_id)
                    blockSize = blockObj.count()
                    if blockSize == 0:
                        blockDict = genBlockDict(comm_id, comm_name)
                        if blockDict is None:
                            continue
                        jsonObj = json.dumps(blockDict)+','
                        json_data.extend(jsonObj)
                    for j in range(0,blockSize,1):
                        blockId = blockObj[j].getBlockId()
                        blockName = blockObj[j].block_name
                        blockDict = genBlockDict(comm_id, comm_name, blockId, blockName)
                        if blockDict is None:
                            continue
                        jsonObj = json.dumps(blockDict)+','
                        json_data.extend(jsonObj)
            json_data.extend(']')
            return HttpResponse(json_data, content_type="application/json")
        else:
            response_data['flag'] = 'none_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    if block_id:
        buildObj = None
        try:
            buildObj = BuildNum.objects.filter(block__block_id=block_id)
        except:
            response_data['flag'] = 'none_o'    
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if buildObj:
            json_data = serializers.serialize("json", buildObj)
            return HttpResponse(json_data,content_type="application/json")
        else:
            response_data['flag'] = 'none_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    if community_id:
        buildObj = None
        try:
            buildObj = BuildNum.objects.filter(community__community_id=community_id)
        except:
            response_data['flag'] = 'none_o'    
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if buildObj:
            json_data = serializers.serialize("json", buildObj)
            return HttpResponse(json_data,content_type="application/json")
        else:
            response_data['flag'] = 'none_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    if buildnum_id:
        aptnumObj = None
        try:
            aptnumObj = AptNum.objects.filter(buildnum__buildnum_id=buildnum_id)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if aptnumObj:
            json_data = serializers.serialize("json", aptnumObj)
            return HttpResponse(json_data,content_type="application/json")
        else:
            response_data['flag'] = 'none_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def updatePrimaryAddr(request):
    response_data = {}
    familyRecordObj = None
    userObj = None
    familyObj = None
    adminType = None
    oldfamily_id = request.POST.get('old_family_id', None)
    family_id    = request.POST.get('family_id', None)
    user_id      = request.POST.get('user_id', None)
    neStatus     = request.POST.get('ne_status', None)
    oldneStatus  = request.POST.get('old_ne_status', None)
    userObj   = User.objects.get(user_id=user_id)
    if userObj is None:
        response_data['flag'] = 'none_u'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if family_id is None:#new is not exist
        familyObj = None
    else:#new is exist
        try:
            familyObj = AddressDetails.objects.get(ad_id=family_id)
        except:
            response_data['flag'] = 'no_familyObj'    
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    if familyObj is None:#new is not exist
        try:
            frNewObj = FamilyRecord.objects.get(ne_status = neStatus,user_id=user_id,family_id=None)
        except:
            response_data['flag'] = 'no_frNewObj'    
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if oldfamily_id is None:
            try:
                frOldObj = FamilyRecord.objects.get(ne_status = oldneStatus,user_id=user_id,family_id=None)
            except:
                response_data['flag'] = 'no_if_frOldObj'    
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            try:
                frOldObj = FamilyRecord.objects.get(user_id=user_id,family_id=oldfamily_id)
            except:
                response_data['flag'] = 'no_else_frOldObj'    
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        userObj.user_family_id = None      
        userObj.user_community_id = frNewObj.family_community_id 
        userObj.user_family_address = frNewObj.family_address
        userObj.save()
        frOldObj.primary_flag = 0
        frOldObj.save()
        frNewObj.primary_flag = 1
        frNewObj.save()
    else:#new is exist
        try:
            frNewObj = FamilyRecord.objects.get(user_id=user_id,family_id=family_id)
        except:
            response_data['flag'] = 'no_frNewObj'    
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if oldfamily_id is None:
            try:
                frOldObj = FamilyRecord.objects.get(ne_status = oldneStatus,user_id=user_id,family_id=None)
            except:
                frOldObj = None
               # response_data['flag'] = 'no_oldfamily'
               # return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            try:
                frOldObj = FamilyRecord.objects.get(user_id=user_id,family_id=oldfamily_id)
            except:
                response_data['flag'] = 'no_else_oldfamily'    
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        #set user type(admin)
        currentCommunityId = frNewObj.family_community_id 
        try:
            adminType = Admin.objects.get(community_id=currentCommunityId,user_id=user_id)
            userObj.user_type = adminType.admin_type
            userObj.user_json = adminType.admin_info
        except:
            userObj.user_type = 0
        userObj.user_family_id = frNewObj.family.getAddrDetailId()
        userObj.user_community_id = currentCommunityId
        userObj.user_family_address = frNewObj.family_address 
        userObj.save()
        if frOldObj is None:
            pass
        else:
            frOldObj.primary_flag = 0
            frOldObj.save()
        frNewObj.primary_flag = 1
        frNewObj.save()
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@api_view(['GET','POST'])
def addFamily(request):
    response_data = {}
    fadId = None
    status = None
    fRecordObj = None
    family_block = None
    if request.method == 'POST':
        city_code              = request.POST.get('city_code', None)
        family_city_id         = request.POST.get('city_id', None)
        family_community_id    = request.POST.get('community_id', None)
        family_block_id        = request.POST.get('block_id', None)
        family_building_num_id = request.POST.get('buildnum_id', None)
        family_apt_num_id      = request.POST.get('aptnum_id', None)
        family_city            = request.POST.get('city', None)
        family_community       = request.POST.get('community', None)
        family_block           = request.POST.get('block_name', None)
        family_building_num    = request.POST.get('buildnum', None)
        family_apt_num         = request.POST.get('aptnum', None)
        login_account          = request.POST.get('user_id', None)
        primary_flag           = request.POST.get('primary_flag', None)#current address
    else:
        city_code              = request.GET.get('city_code', None)
        family_city_id         = request.GET.get('city_id', None)
        family_community_id    = request.GET.get('community_id', None)
        family_block_id        = request.GET.get('block_id', None)
        family_building_num_id = request.GET.get('buildnum_id', None)
        family_apt_num_id      = request.GET.get('aptnum_id', None)
        family_city            = request.GET.get('city', None)
        family_community       = request.GET.get('community', None)
        family_block           = request.GET.get('block_name', None)
        family_building_num    = request.GET.get('buildnum', None)
        family_apt_num         = request.GET.get('aptnum', None) 
        login_account          = request.GET.get('user_id', None)
        primary_flag           = request.GET.get('primary_flag', None)#current address 
    if int(family_apt_num_id)==0:#verify failed
        status = random.randint(10000,99999)
        fRecordObj = FamilyRecord(entity_type = 0,ne_status = status,user_id=login_account,family_id=None)
    else:
        if int(family_block_id) == 0:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_building_num_id) + str(family_apt_num_id)
        else:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_block_id) + \
                    str(family_building_num_id) + str(family_apt_num_id)
        familyTuple = AddressDetails.objects.get_or_create(ad_id=fadId) 
        addrDetailsObj = familyTuple[0]
        if familyTuple[1]:#new
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name=family_city
            addrDetailsObj.building_name=family_building_num
            addrDetailsObj.community_name=family_community
            addrDetailsObj.apt_name=family_apt_num
            addrDetailsObj.block_name = family_block
            addrDetailsObj.family_name = family_building_num+"-"+family_apt_num
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
            addrDetailsObj.apt_id = family_apt_num_id
            addrDetailsObj.city_id = family_city_id
            addrDetailsObj.block_id = family_block_id
            addrDetailsObj.building_id = family_building_num_id
            addrDetailsObj.community_id = family_community_id
            addrDetailsObj.save()
        else:
            pass
        fRecordTuple = FamilyRecord.objects.get_or_create(user_id=login_account,family=addrDetailsObj) 
        fRecordObj = fRecordTuple[0]
        fRecordObj.ne_status = 0
        fRecordObj.entity_type = 0
    fRecordObj.family_name = family_building_num+"-"+family_apt_num
    fRecordObj.family_city = family_city
    fRecordObj.family_city_id = family_city_id
    fRecordObj.family_community = family_community
    fRecordObj.family_community_id = family_community_id
    fRecordObj.family_building_num = family_building_num
    fRecordObj.family_building_num_id = family_building_num_id
    fRecordObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
    if primary_flag is None:
        fRecordObj.primary_flag = 0
    else:
        fRecordObj.primary_flag = 1
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = fadId
        userObj.user_community_id = family_community_id
        if family_block is None:
            userObj.user_family_address = family_city+family_community+"-"+family_building_num+"-"+family_apt_num
        else:
            userObj.user_family_address = family_city+family_community+"-"+family_block+"-"+family_building_num+"-"+family_apt_num
        userObj.save()
        #针对小区的介绍
        #nCount = AddressDetails.objects.filter(community_id=long(family_community_id)).count()
        #if 1==nCount:
        #    setWelcomeTopicForCommunity(family_city,family_city_id,family_community,family_community_id,userObj.user_family_address,userObj.user_family_id,userObj.user_nick)
    if family_block is None:
        fRecordObj.family_block_id = 0
    else:
        fRecordObj.family_block = family_block
        fRecordObj.family_block_id = family_block_id
    userObj = User.objects.get(user_id=login_account)
    fRecordObj.family_apt_num = family_apt_num
    fRecordObj.family_apt_num_id = family_apt_num_id
    fRecordObj.is_family_member = 0
    fRecordObj.user_avatar = userObj.user_portrait
    fRecordObj.save()
    curfamilyRecord = fRecordObj.getFamilyRecordID()
    #push 
    config = readIni()
    if status is None:
        response_data['flag'] = 'ok'
        response_data['family_id'] = fadId
        response_data['frecord_id'] = curfamilyRecord
        response_data['ne_status'] = 0
    else:
        response_data['flag'] = 'ok'
        response_data['family_id'] = 0
        response_data['frecord_id'] = curfamilyRecord
        response_data['ne_status'] = status
    response_data['entity_type'] = 0
    pushTitle = config.get("users", "title")
    familyAddr = fRecordObj.family_address.encode('utf-8')
    pushContent = config.get("users", "content6")+ familyAddr + config.get("users", "content8")
    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    currentPushTime = long(time.time()*1000)
    customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,family_community_id)
    recordId = createPushRecord(2,2,pushTitle,pushContent,currentPushTime,login_account,(json.dumps(customContent)),userObj.user_community_id,login_account)
    customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,family_community_id,recordId)

    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    _jpush = jpush.JPush(apiKey,secretKey) 
    currentAlias = alias + str(login_account)
    pushExtra = customContent
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
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
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def genCustomContentDict(userId,userAvatar,title,content,contentType,pushTime,pushType,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('content',content)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushType',pushType)
    dicts.setdefault('communityId',communityId)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

@api_view(['GET','POST'])
def modifiFamily(request):
    response_data = {}
    fadId = None
    status = None
    fRecordObj = None
    family_block = None
    if request.method == 'POST':
        family_city_id         = request.POST.get('city_id', None)
        family_community_id    = request.POST.get('community_id', None)
        family_block_id        = request.POST.get('block_id', None)
        family_building_num_id = request.POST.get('buildnum_id', None)
        family_apt_num_id      = request.POST.get('aptnum_id', None)
        city_code              = request.POST.get('city_code', None)
        family_city            = request.POST.get('city', None)
        family_community       = request.POST.get('community', None)
        family_block           = request.POST.get('block', None)
        family_building_num    = request.POST.get('buildnum', None)
        family_apt_num         = request.POST.get('aptnum', None)
        login_account          = request.POST.get('user_id', None)
        family_id              = request.POST.get('family_id', None)
        neStatus               = request.POST.get('ne_status', None)
    else:
        family_city_id         = request.GET.get('city_id', None)
        family_community_id    = request.GET.get('community_id', None)
        family_block_id        = request.GET.get('block_id', None)
        family_building_num_id = request.GET.get('buildnum_id', None)
        family_apt_num_id      = request.GET.get('aptnum_id', None)
        city_code              = request.GET.get('city_code', None)
        family_city            = request.GET.get('city', None)
        family_community       = request.GET.get('community', None)
        family_block           = request.GET.get('block', None)
        family_building_num    = request.GET.get('buildnum', None)
        family_apt_num         = request.GET.get('aptnum', None) 
        login_account          = request.GET.get('user_id', None)
        family_id              = request.GET.get('family_id', None)
        neStatus               = request.GET.get('ne_status', None)
    if int(family_apt_num_id)==0:# The modified address is illegal
        if int(neStatus) == 0:
            fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),family_id=str(family_id)) 
        else:
            fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),ne_status=neStatus)   
        fRecordObj.family = None
        fRecordObj.entity_type = 0 # verify failed  
        status = random.randint(10000,99999)
        fRecordObj.ne_status = status
    else:# The modified address is valid
        if family_block_id is None:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_building_num_id) + str(family_apt_num_id)
        else:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_block_id) + \
                    str(family_building_num_id) + str(family_apt_num_id)
        familyTuple = AddressDetails.objects.get_or_create(ad_id=fadId) 
        addrDetailsObj = familyTuple[0]
        if familyTuple[1]:
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name=family_city
            addrDetailsObj.building_name=family_building_num
            addrDetailsObj.block_name = family_block
            addrDetailsObj.community_name=family_community
            addrDetailsObj.apt_name=family_apt_num
            addrDetailsObj.family_name = family_building_num+"-"+family_apt_num
            addrDetailsObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.apt_id = family_apt_num_id
            addrDetailsObj.city_id = family_city_id
            addrDetailsObj.block_id = family_block_id
            addrDetailsObj.building_id = family_building_num_id
            addrDetailsObj.community_id = family_community_id
            addrDetailsObj.save()
        else:
            pass
        if int(neStatus) == 0: 
            fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),ne_status=neStatus,family_id=family_id)   
            #fRecordObj.entity_type = 0 # verify failed   
            #fRecordObj.ne_status = neStatus
        else: 
            try:
                fRecordTuple = FamilyRecord.objects.get_or_create(user_id=long(login_account),family_id=str(fadId))
                fRecordObj = fRecordTuple[0]
            except:
                response_data['flag'] = 'none_o_f'    
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            #fRecordObj.entity_type = 1 # verify success
            fRecordObj.family = addrDetailsObj
            #fRecordObj.ne_status = 0
    fRecordObj.family_name = family_building_num+"-"+family_apt_num
    fRecordObj.family_city = family_city
    fRecordObj.family_city_id = family_city_id
    fRecordObj.family_community = family_community
    fRecordObj.family_community_id = family_community_id
    fRecordObj.family_building_num = family_building_num
    fRecordObj.family_building_num_id = family_building_num_id
    fRecordObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
    if fRecordObj.primary_flag == 0:
        fRecordObj.primary_flag = 0
    else:
        fRecordObj.primary_flag = 1
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = fadId
        userObj.user_community_id = family_community_id
        userObj.user_family_address = family_city+family_community+"-"+family_building_num+"-"+family_apt_num 
        userObj.save()
    if family_block is None:
        fRecordObj.family_block_id = 0
    else:
        fRecordObj.family_block = family_block
        fRecordObj.family_block_id = family_block_id
    fRecordObj.family_apt_num = family_apt_num
    fRecordObj.family_apt_num_id = family_apt_num_id
    fRecordObj.is_family_member = 0
    fRecordObj.user_avatar = (User.objects.get(user_id=long(login_account))).user_portrait
    fRecordObj.save()
    curfamilyRecord = fRecordObj.getFamilyRecordID()
    if fadId is None:
        response_data['flag'] = 'ok'
        response_data['ne_status'] = status
        response_data['family_id'] = 0
        response_data['frecord_id'] = curfamilyRecord
    else:
        response_data['flag'] = 'ok'
        response_data['ne_status'] = 0
        response_data['family_id'] = fadId
        response_data['frecord_id'] = curfamilyRecord
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

@api_view(['GET','POST'])
def deleFamilyRecord(request):
    response_data = {}
    if request.method == 'POST':
        familyId               = request.POST.get('family_id', None)
        login_account          = request.POST.get('user_id', None)
        primary_flag           = request.POST.get('flag', None)
        neStatus               = request.POST.get('nestatus', None)
    else:
        familyId               = request.GET.get('family_id', None) 
        login_account          = request.GET.get('user_id', None)
        primary_flag           = request.GET.get('flag', None)
        neStatus               = request.GET.get('nestatus', None)
        
    if int(primary_flag) == 0:
        pass
    else:
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = None
        userObj.user_family_address = None
        userObj.user_community_id = None
        userObj.save()
    if int(neStatus) ==0:
        family_record = FamilyRecord.objects.filter(family_id=familyId, user_id=login_account).delete()
    else:
        family_record = FamilyRecord.objects.filter(ne_status=neStatus, user_id=login_account).delete()
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,family_id,user_type,\
                    user_phone_number,user_profession,user_signature,user_level,user_public_status):
    neighbor_dict = {}
    neighbor_dict.setdefault('user_id', user_id)
    neighbor_dict.setdefault('user_nick', user_name)
    neighbor_dict.setdefault('user_type', user_type)
    neighbor_dict.setdefault('user_portrait', user_portrait)
    neighbor_dict.setdefault('user_phone_number', user_phone_number)
    neighbor_dict.setdefault('building_num', building_num)
    neighbor_dict.setdefault('aptnum', aptnum)
    neighbor_dict.setdefault('user_profession', user_profession)
    neighbor_dict.setdefault('user_signature', user_signature)
    neighbor_dict.setdefault('user_level', user_level)
    neighbor_dict.setdefault('family_id', family_id)
    neighbor_dict.setdefault('user_public_status',user_public_status)
    return neighbor_dict

@api_view(['GET','POST'])
def getNeighbors(request):
    response_data = {}
    json_data = []
    block_id      = None
    community_id  = None
    fRecordObj    = None
    if request.method == 'POST':
        apt_num      = request.POST.get('apt_num', None)
        block_id     = request.POST.get('block_id', None)
        community_id = request.POST.get('community_id', None)
    else:
        apt_num      = request.GET.get('apt_num', None)
        block_id     = request.GET.get('block_id', None)
        community_id = request.GET.get('community_id', None)
    if block_id is None:
        try:
            fRecordObj = FamilyRecord.objects.filter(family_community_id=community_id,entity_type=1).order_by('family_community_id')
        except:
            response_data['flag'] = 'none_e_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        try:
            fRecordObj = FamilyRecord.objects.filter(family_community_id=community_id,family_block_id=block_id,entity_type=1)\
                         .order_by('family_community_id')
        except:
            response_data['flag'] = 'none_e_o'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    if fRecordObj:
        size = fRecordObj.count()
        if size == 0:
            response_data['flag'] = 'none_f_o0'             
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        json_data.extend('[')
        for i in range(0, size,1):
            user_id = fRecordObj[i].user.getTargetUid()
            user_name = fRecordObj[i].user.user_nick
            user_portrait = fRecordObj[i].user.user_portrait
            user_public_status = fRecordObj[i].user.user_public_status
            building_num = fRecordObj[i].family_building_num
            aptnum = fRecordObj[i].family_apt_num
            family_id = None
            try:
                family_id = fRecordObj[i].family.getAddrDetailId()
            except:
                family_id = '0'
            user_profession = fRecordObj[i].user.user_profession
            user_signature = fRecordObj[i].user.user_signature
            user_level = fRecordObj[i].user.user_level
            user_phone_number = fRecordObj[i].user.user_phone_number
            if i+1 == size:
                jsonObj = json.dumps(genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,family_id,\
                          user_phone_number,user_profession,user_signature,user_level,user_public_status))
                json_data.extend(jsonObj)
            else:
                jsonObj = json.dumps(genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,family_id,\
                                     user_phone_number,user_profession,user_signature,user_level,user_public_status))+','
                json_data.extend(jsonObj)
        json_data.extend(']')
        return HttpResponse(json_data, content_type="application/json")
    else:
        response_data['flag'] = 'none_f_o1'#success
        return HttpResponse(json.dumps(response_data), content_type="application/json")              
#1.user_id 2.user_name 3.user_portrait 4.user_phone_number 5.addrstatus=0 6.building_num 7.aptnum 8.family_id 9.data_type=1
    
def getCacheKey():
    cacheKey = int(time.time()) + int(random.randint(100,999))
    return cacheKey  


def decrypt(passwd,key,iv):
    from Crypto.Cipher import AES
    import base64
    PADDING = '\0'
    #pwd = 'a+29eM+MoD1WM6kXkMi1YA=='
    generator = AES.new(key, AES.MODE_CBC, iv)
    recovery = generator.decrypt(base64.b64decode(passwd))
    return recovery.rstrip(PADDING)

def password_md5(pwd,phone):
    try:
        import hashlib
        hash = hashlib.md5()
    except ImportError:
        # for Python << 2.5
        import md5
        hash = md5.new()
    hash.update(pwd)
    value = hash.hexdigest()
    hash.update(value+phone.encode("utf-8"))  #md5(md5(pwd)+phone)
    passwd = hash.hexdigest()
    return passwd

def getAddressByQuerySet(cityObj):
    dicts = {}
    dicts.setdefault('pk',cityObj.getCityId())
    dictFields = {}
    dictFields.setdefault('city_name',cityObj.city_name)
    dictFields.setdefault('city_code',cityObj.city_code)
    dicts.setdefault('fields',dictFields)
    return dicts

def getCommunityByQuerySet(buildObj):
    dicts = {}
    dicts.setdefault('pk',buildObj.getBuildNumId())
    dictFields = {}
    dictFields.setdefault('building_name',buildObj.building_name)
    dictFields.setdefault('community',buildObj.community.getCommunityId())
    if buildObj.block is None:
        dictFields.setdefault('block',0)
    else:
        dictFields.setdefault('block',buildObj.block.getBlockId())
    dicts.setdefault('fields',dictFields)
    return dicts

def getAptNumberByQuerySet(aptObj):
    dicts = {}
    dicts.setdefault('pk',aptObj.getAptNumId())
    dictFields = {}
    dictFields.setdefault('apt_name',aptObj.apt_name)
    dictFields.setdefault('buildnum',aptObj.buildnum.getBuildNumId())
    dicts.setdefault('fields',dictFields)
    return dicts
    
        
def getUserListByQuerySet(userObj):
    dicts = {}
    dicts.setdefault('pk',userObj.getTargetUid())
    dictFields = {}
    dictFields.setdefault('user_nick',userObj.user_nick)
    dictFields.setdefault('user_portrait',userObj.user_portrait)
    dictFields.setdefault('user_gender',userObj.user_gender)
    dictFields.setdefault('user_phone_number',userObj.user_phone_number)
    dictFields.setdefault('user_family_id',userObj.user_family_id)
    dictFields.setdefault('user_community_id',userObj.user_community_id)
    dictFields.setdefault('user_family_address',userObj.user_family_address)
    dictFields.setdefault('user_email',userObj.user_email)
    dictFields.setdefault('user_password',userObj.user_password)
    dictFields.setdefault('user_birthday',userObj.user_birthday)
    dictFields.setdefault('user_public_status',userObj.user_public_status)
    dictFields.setdefault('user_profession',userObj.user_profession)
    dictFields.setdefault('user_level',userObj.user_level)
    dictFields.setdefault('user_signature',userObj.user_signature)
    dictFields.setdefault('user_type',userObj.user_type)
    dictFields.setdefault('user_push_user_id',userObj.user_push_user_id)
    dictFields.setdefault('user_push_channel_id',userObj.user_push_channel_id)
    newsReceive = userObj.user_news_receive
    if newsReceive is None or newsReceive == 'null' or newsReceive == 'NULL':
        newsReceive = 1
    dictFields.setdefault('user_news_receive',newsReceive)
    dictFields.setdefault('user_time',userObj.user_time)
    dictFields.setdefault('user_json',userObj.user_json)
    dictFields.setdefault('addr_handle_cache',userObj.addr_handle_cache)
    dicts.setdefault('fields',dictFields)
    return dicts

#游客登录
def LoginGuest(request):
    if request.method == 'POST':
        imei  = request.POST.get('imei')
        phone = request.POST.get('phone')
    else:
        imei  = request.GET.get('imei')
        phone = request.GET.get('phone')
    response_data = {}
    if imei is None or phone is None:
        response_data['flag'] = 'argv_error'
    from users.models import Guest
    try:
        count = Guest.objects.filter(g_phone=str(phone)).count()
        if count > 0:
            #表明已经注册过环信
            pass
        else:
            #需要重新注册环信
            pass
    except:
        #表明有重复的手机号，已经注册过环信
        pass
        
    import time
    chatNumber = long(str(time.time()*10).split('.')[0]) + long(str(time.time()*10).split('.')[0][-5:])
    return response_data

#判断第三方绑定
def JudgeThird(request):
    if request.method == 'POST':
        phoneNumber  = request.POST.get('phone_number')
    else:
        phoneNumber  = request.GET.get('phone_number')
    from users.models import Third
    response_data = {}
    try:
        #证明该手机已经被绑定
        thirdObj = User.objects.get(user_phone_number=str(phoneNumber))
        response_data['flag'] = 'exist'
    except:
        #证明该手机尚未被绑定
        response_data['flag'] = 'nonentity'
    return response_data 


def Schedule(a,b,c):
    '''''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100 #表明下载成功

def DownLoadImg(url,userid):
    import urllib
    from community.views import makeCircleAvatr,imgGenName
    userDir = settings.MEDIA_ROOT+'youlin/res/'+str(userid)+'/avatars/'
    
    if os.path.exists(userDir):
        pass
    else:
        try:
            os.makedirs(userDir, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                pass
            else:raise
    circleImage = imgGenName("tmp.jpg")
    local = os.path.join(userDir,circleImage)
    detailInfo = urllib.urlretrieve(url,local,Schedule)
    newFile = userDir+circleImage #新生成的文件路径
    makeCircleAvatr(newFile,local)
    return newFile

#第三方绑定
def BindThird(request):
    if request.method == 'POST':
        thirdAccount = request.POST.get('third_account')
        phoneNumber  = request.POST.get('phone_number')
        phoneImei    = request.POST.get('phone_imei')
        thirdNick    = request.POST.get('third_nick')
        thirdIcon    = request.POST.get('third_icon')
        thirdGender  = request.POST.get('third_gender')
        thirdNote    = request.POST.get('third_note')
        phonePasswd  = request.POST.get('user_passwd')
        thirdType    = request.POST.get('third_type')
    else:
        thirdAccount = request.GET.get('third_account')
        phoneNumber  = request.GET.get('phone_number')
        phoneImei    = request.GET.get('phone_imei')
        thirdNick    = request.GET.get('third_nick')
        thirdIcon    = request.GET.get('third_icon')
        thirdGender  = request.GET.get('third_gender')
        thirdNote    = request.GET.get('third_note')
        phonePasswd  = request.GET.get('user_passwd')
        thirdType    = request.GET.get('third_type')
    from users.models import Third
    userObj  = None
    thirdObj = None
    response_data = {}
    try:
        #证明该手机已经被注册
        userObj = User.objects.get(user_phone_number=str(phoneNumber))
        response_data['flag'] = 'ok'
        response_data['phone'] = userObj.user_phone_number
        response_data['passwd'] = userObj.user_password
        try:
            thirdObj = Third.objects.get(t_auth=str(thirdAccount),t_imei=str(phoneImei))
            thirdObj.t_nick = thirdType + '-' + thirdNick
#             tmpPath = DownLoadImg(thirdIcon,userObj.getTargetUid())
#             thirdAvatar = settings.RES_URL + tmpPath.split(settings.MEDIA_YL)[1]
            thirdObj.t_portrait = userObj.user_portrait
            thirdObj.t_gender = thirdGender
            thirdObj.t_phone_number = phoneNumber
            thirdObj.save()
        except Exception,e:
            response_data['flag'] = 'no'
            response_data['error'] = str(e)
            return response_data
        return response_data
    except:#证明该手机尚未注册
        thirdAvatar = None
        avatar_url = settings.RES_URL + 'res/default/avatars/'
        if 1==int(thirdGender):
            thirdAvatar = avatar_url + 'default-boy-avatar.png'
        elif 2==int(thirdGender):
            thirdAvatar = avatar_url + 'default-girl-avatar.png'
        elif 3==int(thirdGender):
            thirdAvatar = avatar_url + 'default-normal-avatar.png'
        try:
            thirdObj = Third.objects.get(t_auth=str(thirdAccount),t_imei=str(phoneImei))
            thirdObj.t_nick = thirdType + '-' + thirdNick
            thirdObj.t_gender = thirdGender
            thirdObj.t_phone_number = phoneNumber
            thirdObj.t_portrait = thirdAvatar
            thirdObj.save()
        except Exception,e:
            response_data['flag'] = False
            response_data['thirdType'] = thirdType
            response_data['thirdNick'] = thirdNick
            response_data['error'] = str(e)
            return response_data
        userObj = User.objects.create(user_phone_number=str(phoneNumber),user_public_status='4',user_type=0)
        userObj.user_gender = thirdGender
        userObj.user_nick = thirdType + '-' + thirdNick
        userObj.user_password = phonePasswd
        userObj.user_portrait = thirdAvatar
        userObj.user_credit = 5
        userObj.user_exp = 5
        userObj.user_handle_cache = 0
        userObj.addr_handle_cache = 0
        userObj.save()
#         thirdObj = Third.objects.get(t_auth=str(thirdAccount),t_imei=str(phoneImei))
#         tmpPath = DownLoadImg(thirdIcon,userObj.getTargetUid())
#         thirdAvatar = settings.RES_URL + tmpPath.split(settings.MEDIA_YL)[1]
#         thirdObj.t_portrait = thirdAvatar
#         thirdObj.save()
#         userObj.user_portrait = thirdAvatar
#         userObj.save()
        response_data['flag'] = True
        response_data['status'] = 'new'
        response_data['user_id'] = userObj.getTargetUid()
        response_data['type'] = 0
        response_data['fr_id'] = 0
        response_data['addr_cache'] = 0
        response_data['user_avatr'] = userObj.user_portrait
        return response_data

#第三方登录
def LoginThird(request):
    if request.method == 'POST':
        thirdAccount = request.POST.get('third_account')
        phoneImei    = request.POST.get('phone_imei')
    else:
        thirdAccount = request.GET.get('third_account')
        phoneImei    = request.GET.get('phone_imei')
    response_data = {}
    if thirdAccount is None or phoneImei is None:
        response_data['flag'] = 'argv_error'
    from users.models import Third
    count = Third.objects.filter(t_auth=str(thirdAccount)).count()
    if count > 0:
        #表明已经登录过
        phone = Third.objects.get(t_auth=str(thirdAccount),t_imei=str(phoneImei)).t_phone_number
        if phone is None or phone == 'null' or phone == 'NULL' or phone == '':
            #调用绑定第三方
            response_data['flag'] = 'exist'
        else:
            #证明已经绑定成功了
            userObj = User.objects.get(user_phone_number=str(phone))
            response_data['phone'] = userObj.user_phone_number
            response_data['passwd'] = userObj.user_password
            response_data['flag'] = 'already'
    else:
        #需要重新登录
        thirdObj =Third.objects.create(t_auth=thirdAccount)
        thirdObj.t_imei = phoneImei
        thirdObj.save()
        response_data['flag'] = 'exist'
    return response_data

#用户登录
def LoginUser(request):
    if request.method == 'POST':
        phoneNumber = request.POST.get('phonenum')
        passwd = request.POST.get('password')
    else:
        phoneNumber = request.GET.get('phonenum')
        passwd = request.GET.get('password')
    targetObj = User.objects.filter(user_phone_number=phoneNumber)
    response_data = {}
    #passwd='n7sA/YcnzTMsmTJ96o0Lqg=='
    #print passwd
#     if targetObj:  # query ok! exist
#         #AES解密
#         key = (phoneNumber+'youli').encode("utf-8")
#         iv = (phoneNumber+'youli').encode("utf-8")
#         passwdstr = passwd.encode('utf-8')
#         pwd = decrypt(str(passwdstr),key,iv)
#         pwdnew = password_md5(pwd,phoneNumber)
    if targetObj:       
        if (targetObj[0].user_password == passwd):
            json_data = []
            userObj = User.objects.get(user_phone_number=phoneNumber)
            user_json = getUserListByQuerySet(userObj)#serializers.serialize("json", userObj)
            familyRecordObj = FamilyRecord.objects.filter(user=userObj)
            if familyRecordObj:
                json_data.append(user_json)
                familyRecordSize = familyRecordObj.count()
                if familyRecordSize == 0:
                    pass
                else:
                    for i in range(0,familyRecordSize,1):
                        try:
                            family_id = familyRecordObj[i].family.getAddrDetailId()
                        except:
                            family_id = None
                        frId = familyRecordObj[i].getFamilyRecordID()
                        family_name = familyRecordObj[i].family_name
                        family_address = familyRecordObj[i].family_address
                        family_building_num = familyRecordObj[i].family_building_num
                        family_apt_num = familyRecordObj[i].family_apt_num
                        is_family_member = familyRecordObj[i].is_family_member
                        family_member_count = familyRecordObj[i].family_member_count
                        primary_flag = familyRecordObj[i].primary_flag
                        user_avatar = familyRecordObj[i].user_avatar
                        city_name = familyRecordObj[i].family_city
                        city_id = familyRecordObj[i].family_city_id
                        block_name = familyRecordObj[i].family_block
                        bolicID = familyRecordObj[i].family_block_id
                        if bolicID is None or bolicID == 'null' or bolicID == 'NULL':
                            bolicID = 0
                        block_id = bolicID
                        community_name = familyRecordObj[i].family_community
                        community_id = familyRecordObj[i].family_community_id
                        entityType = familyRecordObj[i].entity_type 
                        neStatus = familyRecordObj[i].ne_status
                        try:
                            cityObj = City.objects.get(city_id=long(city_id))
                            city_code = cityObj.city_code
                        except:
                            city_code = '0'
                        apt_num_id = familyRecordObj[i].family_apt_num_id
                        building_num_id = familyRecordObj[i].family_building_num_id
                        if i+1 == familyRecordSize:
                            json_data.append(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                     family_apt_num,is_family_member,family_member_count,\
                                                                     primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                     block_id,community_name,community_id,entityType,neStatus,
                                                                     city_code,apt_num_id,building_num_id))
                        else:
                            json_data.append(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                     family_apt_num,is_family_member,family_member_count,\
                                                                     primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                     block_id,community_name,community_id,entityType,neStatus,
                                                                     city_code,apt_num_id,building_num_id))
            else:
                json_data.append(user_json)
            return json_data
        else:
            response_data['flag'] = 'no1'
            return response_data
    else: # query fail! not exist
        response_data['flag'] = 'no'
        return response_data

#用户注销
def SetPhoneLogoff(request):
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
        user_id   = request.POST.get('user_id', None)
        status    = request.POST.get('status', None)
    else:
        userPhone = request.GET.get('user_phone', None)
        user_id   = request.GET.get('user_id', None)
        status    = request.GET.get('status', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone)
    except:
        response_data['flag'] = 'no'    # userObj not exist
        return response_data
    if userObj is not None:
        userObj.user_push_user_id = None
        userObj.user_push_channel_id = None
        userObj.save()
    response_data['flag'] = 'ok'
    return response_data

#获取个人信息
def GetPersonalInfo(request):
    response_data = {}
    if request.method == 'POST':
        user_phone_number = request.POST.get('user_phone_number', None)
    else:
        user_phone_number = request.GET.get('user_phone_number', None)
    if user_phone_number is None:
        response_data['flag'] = 'none_i'    # user_id not exist
        return response_data
    userObj = None
    try:
        userObj = User.objects.get(user_phone_number=user_phone_number)
    except:
        response_data['flag'] = 'none_o'    # userObj not exist
        return response_data
    if userObj:
        json_data = []
        user_json = getUserListByQuerySet(userObj)#serializers.serialize("json", userObj)
        familyRecordObj = FamilyRecord.objects.filter(user=userObj)
        if familyRecordObj:
            json_data.append(user_json)
            familyRecordSize = familyRecordObj.count()
            if familyRecordSize == 0:
                pass
            else:
                for i in range(0,familyRecordSize,1):
                    try:
                        family_id = familyRecordObj[i].family.getAddrDetailId()
                    except:
                        family_id = None
                    frId = familyRecordObj[i].getFamilyRecordID()
                    family_name = familyRecordObj[i].family_name
                    family_address = familyRecordObj[i].family_address
                    family_building_num = familyRecordObj[i].family_building_num
                    family_apt_num = familyRecordObj[i].family_apt_num
                    is_family_member = familyRecordObj[i].is_family_member
                    family_member_count = familyRecordObj[i].family_member_count
                    primary_flag = familyRecordObj[i].primary_flag
                    user_avatar = familyRecordObj[i].user_avatar
                    city_name = familyRecordObj[i].family_city
                    city_id = familyRecordObj[i].family_city_id
                    block_name = familyRecordObj[i].family_block
                    block_id = familyRecordObj[i].family_block_id
                    community_name = familyRecordObj[i].family_community
                    community_id = familyRecordObj[i].family_community_id
                    entityType = familyRecordObj[i].entity_type 
                    neStatus = familyRecordObj[i].ne_status
                    try:
                        cityObj = City.objects.get(city_id=long(city_id))
                        city_code = cityObj.city_code
                    except:
                        city_code = '0'
                    apt_num_id = familyRecordObj[i].family_apt_num_id
                    building_num_id = familyRecordObj[i].family_building_num_id
                    if i+1 == familyRecordSize:
                        json_data.append(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                 family_apt_num,is_family_member,family_member_count,\
                                                                 primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                 block_id,community_name,community_id,entityType,neStatus,
                                                                 city_code,apt_num_id,building_num_id))
                    else:
                        json_data.append(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                                 family_apt_num,is_family_member,family_member_count,\
                                                                 primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                                 block_id,community_name,community_id,entityType,neStatus,
                                                                 city_code,apt_num_id,building_num_id))
        else:
            json_data.append(user_json)
        return json_data
    else: # query fail! not exist
        response_data['flag'] = 'no'
        return response_data

#修改密码
def ModifyPwd(request):
    response_data = {}
    if request.method == 'POST':
        phoneNumber = request.POST.get('user_phone_number')
        newPasswd = request.POST.get('user_password')
        userId = request.POST.get('user_id')
        oldPasswd = request.POST.get('user_oldpassword')
    else:
        phoneNumber = request.GET.get('user_phone_number')
        newPasswd = request.GET.get('user_password')
        userId = request.GET.get('user_id')
        oldPasswd = request.GET.get('user_oldpassword')
        
    try:
        userObj = User.objects.get(user_phone_number=phoneNumber)
    except:
        response_data['flag'] = 'no_user'    # userObj not exist
        return response_data
#     #AES解密
#     key = (phoneNumber+'youli').encode("utf-8")
#     iv = (phoneNumber+'youli').encode("utf-8")
#     #old
#     oldPasswdstr = oldPasswd.encode('utf-8')
#     oldPwd = decrypt(str(oldPasswdstr),key,iv)
#     old_Pwd = password_md5(oldPwd,phoneNumber)
    if (userObj.user_password == oldPasswd):
         #new
#         newPasswdstr = newPasswd.encode('utf-8')
#         newPwd = decrypt(str(newPasswdstr),key,iv)
#         new_Pwd = password_md5(newPwd,phoneNumber)
        userObj.user_password = newPasswd
        userObj.save()
        response_data['flag'] = 'ok'    
        return response_data
    else:
        response_data['flag'] = 'no'    
        return response_data

#更新个人信息    
def UploadUserInfo(request):
    response_data = {}
    if request.method == 'POST':
        user_phone = request.POST.get('user_phone_number', None)
        if user_phone is None:
            response_data['flag'] = 'none_p'    # phone not exist
            return response_data
        user_id = request.POST.get('user_id', None)
        if user_id is None:
            response_data['flag'] = 'none_i'    # user_id not exist
            return response_data
        userObj = None
        try:
            userObj = User.objects.get(user_phone_number=user_phone, user_id=user_id)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return response_data
        if userObj:
            user_portrait = request.FILES.get('user_portrait', None)
            if user_portrait is None:
                pass
            else:
                fName = user_portrait.name
                userDir = settings.MEDIA_ROOT+'youlin/res/'+str(user_id)+'/avatars/'
                filelist=[]
                if os.path.exists(userDir):
                    pass
                else:
                    try:
                        os.makedirs(userDir, mode=0777)
                    except OSError as exc:
                        if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                            pass
                        else:raise
                filelist=os.listdir(userDir)
                for f in filelist:
                    filepath = os.path.join(userDir, f)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                newImage = imgGenName(fName) # new image
                bigImage = '0' + newImage # big image
                smaillImage = newImage # smaill image
                streamfile = open(userDir+bigImage, 'wb+')
                for chunk in user_portrait.chunks():
                    streamfile.write(chunk)
                streamfile.close()
                smallCircleImage = imgGenName(fName)
                bigCircleImage = '0'+smallCircleImage
                tmpNewImage = '000'+smallCircleImage
                tmpNewBigImage = '0000' + bigCircleImage
                changeNameWithPath = 'mv '+userDir+bigImage+' '+userDir+bigCircleImage
                os.system(changeNameWithPath)#上传的原始大图（方形）
                copyAvatarPic = 'cp '+userDir+bigCircleImage+' '+userDir+tmpNewImage
                os.system(copyAvatarPic)#生成一个临时文件（方形）
                makeCircleAvatr(userDir+tmpNewBigImage,userDir+tmpNewImage)#原型图
                makeThumbnail(userDir, tmpNewBigImage, smallCircleImage,25)#缩略图
                imgUrl = settings.RES_URL + 'res/' + str(user_id) + '/avatars/' + smallCircleImage
                userObj.user_portrait = imgUrl
                #Topic.objects.filter(sender_id=user_id).update(sender_portrait=imgUrl)
            user_nick = request.POST.get('user_nick', None)
            if user_nick is None:
                pass
            else:
                userObj.user_nick = user_nick
            user_news_receive = request.POST.get('receive_status', None)
            if user_news_receive is None:
                pass
            else:
                userObj.user_news_receive = user_news_receive
            user_password = request.POST.get('user_password', None)
            if user_password is None:
                pass
            else:
                userObj.user_password = user_password
            user_gender = request.POST.get('user_gender', None)
            if user_gender is None:
                pass
            else:
                base_url = settings.RES_URL + 'res/default/avatars/'
                avatar_boy     = 'default-boy-avatar.png'
                avatar_girl    = 'default-girl-avatar.png'
                avatar_default = 'default-normal-avatar.png'
                cur_avatar  =  userObj.user_portrait
                cur_suffix  = ''.join(cur_avatar.split('/')[-1:])
                if 1==int(user_gender):#男
                    if cur_avatar is not None:
                        if cur_suffix == avatar_girl:
                            userObj.user_portrait = base_url + avatar_boy
                            response_data['head_url'] = base_url + avatar_boy
                        else:
                            if cur_suffix == avatar_default:
                                userObj.user_portrait = base_url + avatar_boy
                                response_data['head_url'] = base_url + avatar_boy
                            else:
                                response_data['head_url'] = cur_avatar
                    else:
                        userObj.user_portrait = base_url + avatar_boy
                        response_data['head_url'] = base_url + avatar_boy
                elif 2==int(user_gender):#女
                    if cur_avatar is not None:
                        if cur_suffix == avatar_boy:
                            userObj.user_portrait = base_url + avatar_girl
                            response_data['head_url'] = base_url + avatar_girl
                        else:
                            if cur_suffix == avatar_default:
                                userObj.user_portrait = base_url + avatar_girl
                                response_data['head_url'] = base_url + avatar_girl
                            else:
                                response_data['head_url'] = cur_avatar
                    else:
                        userObj.user_portrait = base_url + avatar_girl
                        response_data['head_url'] = base_url + avatar_girl
                else:#保密
                    if cur_avatar is not None:
                        if cur_suffix == avatar_boy:
                            userObj.user_portrait = base_url + avatar_default
                            response_data['head_url'] = base_url + avatar_default
                        elif cur_suffix == avatar_girl:
                            response_data['head_url'] = base_url + avatar_default
                        else:
                            response_data['head_url'] = cur_avatar
                userObj.user_gender = user_gender
            user_family_id = request.POST.get('user_family_id', None)
            if user_family_id is None:
                pass
            else:
                userObj.user_family_id = user_family_id
            user_family_address = request.POST.get('user_family_address', None)
            if user_family_address is None:
                pass
            else:
                userObj.user_family_address = user_family_address
            user_birthday = request.POST.get('user_birthday', None)
            if user_birthday is None:
                pass
            else:
               userObj.user_birthday = user_birthday
            user_public_status = request.POST.get('user_public_status', None)
            if user_public_status is None:
               pass
            else:
               userObj.user_public_status = user_public_status
            user_vocation = request.POST.get('user_vocation', None)
            if user_vocation is None:
                pass
            else:
                userObj.user_profession = user_vocation
            user_level = request.POST.get('user_level', None)
            if user_level is None:
                pass
            else:
                userObj.user_level = user_level
            user_signature = request.POST.get('user_signature', None)
            if user_signature is None:
                pass
            else:
                userObj.user_signature = user_signature
            user_push_user_id = request.POST.get('imei', None)
            if user_push_user_id is None:
                pass
            else:
                userQuerySet = User.objects.filter(user_push_user_id=str(user_push_user_id))
                userCounts = userQuerySet.count()
                if userCounts > 1:
                    for i in range(0,userCounts,1):
                        userQuerySet[i].user_push_user_id = None
                        userQuerySet[i].save()
                        response_data['the_same_imei'] = userCounts
                userObj.user_push_user_id = user_push_user_id
            userObj.save()
            response_data['flag'] = 'ok'
            return response_data
        else:
            response_data['flag'] = 'none'    # user not exist
            return response_data

#注册用户        
def RegistNewUser(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        nick   = request.POST.get('nick')
        passwd = request.POST.get('password')
        phone  = request.POST.get('phonenum') 
        recomm = request.POST.get('recommend')# 0->非要请用户 1->家人 2->朋友
    else:
        gender = request.GET.get('gender')
        nick   = request.GET.get('nick')
        passwd = request.GET.get('password')
        phone  = request.GET.get('phonenum')
        recomm = request.GET.get('recommend')# 0->非要请用户 1->家人 2->朋友
    avatar_url = settings.RES_URL + 'res/default/avatars/'
    response_data = {}
#     #AES解密
#     key = (phone+'youli').encode("utf-8")
#     iv = (phone+'youli').encode("utf-8")
#     passwdstr = passwd.encode("utf-8")
#     pwd = decrypt(passwdstr,key,iv)
#     try:
#         import hashlib
#         hash = hashlib.md5()
#     except ImportError:
#         # for Python << 2.5
#         import md5
#         hash = md5.new()
#     hash.update(pwd)
#     value = hash.hexdigest()
#     hash.update(value+phone.encode("utf-8"))  #md5(md5(pwd)+phone)
#     passwd = hash.hexdigest()
    familyId = None
    if 0 == int(recomm):#未背邀请的用户
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=0)
        if 1==int(gender):
            user[0].user_portrait = avatar_url + 'default-boy-avatar.png'
        elif 2==int(gender):
            user[0].user_portrait = avatar_url + 'default-girl-avatar.png'
        user[0].user_credit = 5
        user[0].user_exp = 5
        user[0].user_handle_cache = 0
        user[0].addr_handle_cache = 0
        user[0].save()
        
        response_data['flag'] = user[1]
        response_data['user_id'] = user[0].getTargetUid()
        response_data['type'] = recomm
        response_data['fr_id'] = 0
        response_data['addr_cache'] = 0
        response_data['user_avatr'] = user[0].user_portrait
        return response_data
    elif 1 == int(recomm):#邀请为家人
        try:
            invItationTuple = Invitation.objects.filter(inv_phone=str(phone)).order_by('-inv_time')
            invObj = invItationTuple[0]
            invUserId = invObj.user_id
            invUserObj = User.objects.get(user_id=long(invUserId))
            userExp = invUserObj.user_exp
            userCredit = invUserObj.user_credit
            invfamiyId = invObj.inv_family_id
            familyId = invfamiyId
            invUserObj.user_exp = int(userExp) + 5
            invUserObj.user_credit = int(userCredit) + 5
            invUserObj.save()
            invQuerySetCount = invItationTuple.count()
            for i in range(1,invQuerySetCount,1):
                invItationTuple[i].inv_status = 3
                invItationTuple[i].save()
        except Exception,e:
            response_data['flag'] = str(Exception)
            response_data['info'] = str(e)
            return response_data
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=0)
        invObj.inv_status = 2
        invObj.save()
        if 1==int(gender):
            user[0].user_portrait = avatar_url + 'default-boy-avatar.png'
        elif 2==int(gender):
            user[0].user_portrait = avatar_url + 'default-girl-avatar.png'
        regUserPortrait = user[0].user_portrait
        user[0].user_credit = 10
        user[0].user_exp = 10
        
        registUserId = user[0].getTargetUid()
        try:
            addrDetailObj = AddressDetails.objects.get(ad_id=str(familyId))
            familyName = addrDetailObj.family_name
            familyAddress = addrDetailObj.family_address
            familyCity = addrDetailObj.city_name
            familyCityId = addrDetailObj.city_id
            familyBlock = addrDetailObj.block_name
            familyBlockId = addrDetailObj.block_id
            familyCommunityId = addrDetailObj.community_id
            familyCommunity = addrDetailObj.community_name
            familyBuildingNum = addrDetailObj.building_name
            familyBuildingNumId = addrDetailObj.building_id
            familyAptNum = addrDetailObj.apt_name
            familyAptNumId = addrDetailObj.apt_id
            familyRecordObj = FamilyRecord(family_name=familyName,family_address=familyAddress,\
                                           family_city=familyCity,family_city_id=familyCityId,\
                                           family_block=familyBlock,family_block_id=familyBlockId,\
                                           family_community_id=familyCommunityId,family_community=familyCommunity,\
                                           family_building_num=familyBuildingNum,family_building_num_id=familyBuildingNumId,\
                                           family_apt_num=familyAptNum,family_apt_num_id=familyAptNumId,\
                                           is_family_member=0,primary_flag=1,entity_type=1,ne_status=0,\
                                           user_id=registUserId,user_avatar=regUserPortrait)
            familyRecordObj.family_id=familyId
            familyRecordObj.save()
            familyRecordId = familyRecordObj.getFamilyRecordID()
            #此处为欢迎信息
            setWelcomeTopic(familyCity,familyCityId,familyCommunity,familyCommunityId,familyAddress,familyId,nick,registUserId)
        except Exception,e:
            response_data['flag'] = str(Exception)
            response_data['error'] = str(e)
            return response_data
        user[0].user_family_address = familyAddress
        user[0].user_community_id = familyCommunityId
        user[0].user_family_id = familyId
        user[0].user_handle_cache = 0
        user[0].addr_handle_cache = 0
        user[0].save()
        response_data['flag'] = user[1]
        response_data['user_id'] = registUserId
        response_data['type'] = recomm
        response_data['fr_id'] = familyRecordId
        response_data['addr_cache'] = 0
        response_data['user_avatr'] = user[0].user_portrait
        return response_data
    elif 2 == int(recomm):#邀请为朋友
        try:
            invItationTuple = Invitation.objects.filter(inv_phone=str(phone)).order_by('-inv_time')
            invObj = invItationTuple[0]
            invUserId = invObj.user_id
            invUserObj = User.objects.get(user_id=long(invUserId))
            userExp = invUserObj.user_exp
            userCredit = invUserObj.user_credit
            invUserObj.user_exp = int(userExp) + 5
            invUserObj.user_credit = int(userCredit) + 5
            invUserObj.save()
            invQuerySetCount = invItationTuple.count()
            for i in range(1,invQuerySetCount,1):
                invItationTuple[i].inv_status = 3
                invItationTuple[i].save()
        except Exception,e:
            response_data['flag'] = str(Exception)
            response_data['info'] = str(e)
            return response_data
        user = User.objects.get_or_create(user_phone_number=phone,user_gender=gender,user_nick=nick,\
                                      user_password=passwd,user_public_status='4',user_type=0)
        invObj.inv_status = 2
        invObj.save()
        if 1==int(gender):
            user[0].user_portrait = avatar_url + 'default-boy-avatar.png'
        elif 2==int(gender):
            user[0].user_portrait = avatar_url + 'default-girl-avatar.png'
        user[0].user_credit = 10
        user[0].user_exp = 10
        user[0].user_handle_cache = 0
        user[0].addr_handle_cache = 0
        user[0].save()
        response_data['flag'] = user[1]
        response_data['user_id'] = user[0].getTargetUid()
        response_data['type'] = recomm
        response_data['fr_id'] = 0
        response_data['addr_cache'] = 0
        response_data['user_avatr'] = user[0].user_portrait
        return response_data

#检查手机是否存在  
def CheckPhoneExist(request):
    if request.method == 'POST':
        phoneNumber = request.POST.get('phonenum')
    else:
        phoneNumber = request.GET.get('phonenum')
    targetObj = User.objects.filter(user_phone_number=phoneNumber)
    response_data = {}
    if targetObj:  # can't regist,exist
        response_data['flag']    = 'exist'
        response_data['user_id'] = targetObj[0].getTargetUid()
        return response_data
    else: # can regist
        response_data['flag'] = 'ok'
        return response_data

#修改密码
def UpdatePasswd(request):
    srvIMEI = None
    response_data = {}
    newpassword = None
    if request.method == 'POST':
        user_phone = request.POST.get('phone', None)
        imei = request.POST.get('imei', None)
        newpasswd = request.POST.get('password', None)
        if user_phone is None:
            response_data['flag'] = 'none_p'    # phone not exist
            return response_data
        userObj = None
        try:
            userObj = User.objects.get(user_phone_number=user_phone)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return response_data
        if userObj:
            userId = userObj.getTargetUid()
            communityId = userObj.user_community_id
            userPhoneNum = userObj.user_phone_number
            srvIMEI = userObj.user_push_user_id
            if srvIMEI is None:#表示用户已经注销登录
                pass
            else:#表示用户仍然处于登录状态
                if str(srvIMEI) == str(imei):#表示自己手机忘记密码
                    pass
                else: #其他手机忘记密                                        
                    AsyncUpdatePasswd.delay(userId,imei)

            userObj.user_password = newpasswd
            userObj.user_push_user_id = None
            userObj.user_push_channel_id = None
            userObj.save()
            response_data['flag'] = 'ok'
            response_data['userId'] = userId
            response_data['phone'] = userPhoneNum
            return response_data
        else:
            response_data['flag'] = 'no'
            return response_data
 
#添加地址    
def AddFamily(request):
    response_data = {}
    auditStatus = False
    fadId = None
    status = None
    fRecordObj = None
    family_block = None
    userCurrentCommunityId = None
    if request.method == 'POST':
        city_code              = request.POST.get('city_code', None)
        family_city_id         = request.POST.get('city_id', None)
        family_community_id    = request.POST.get('community_id', None)
        family_block_id        = request.POST.get('block_id', None)
        family_building_num_id = request.POST.get('buildnum_id', None)
        family_apt_num_id      = request.POST.get('aptnum_id', None)
        family_city            = request.POST.get('city', None)
        family_community       = request.POST.get('community', None)
        family_block           = request.POST.get('block_name', None)
        family_building_num    = request.POST.get('buildnum', None)
        family_apt_num         = request.POST.get('aptnum', None)
        login_account          = request.POST.get('user_id', None)
        primary_flag           = request.POST.get('primary_flag', None)#current address
        addr_cache             = request.POST.get('addr_cache', None)# addr verfty
    else:
        city_code              = request.GET.get('city_code', None)
        family_city_id         = request.GET.get('city_id', None)
        family_community_id    = request.GET.get('community_id', None)
        family_block_id        = request.GET.get('block_id', None)
        family_building_num_id = request.GET.get('buildnum_id', None)
        family_apt_num_id      = request.GET.get('aptnum_id', None)
        family_city            = request.GET.get('city', None)
        family_community       = request.GET.get('community', None)
        family_block           = request.GET.get('block_name', None)
        family_building_num    = request.GET.get('buildnum', None)
        family_apt_num         = request.GET.get('aptnum', None) 
        login_account          = request.GET.get('user_id', None)
        primary_flag           = request.GET.get('primary_flag', None)#current address 
        addr_cache             = request.GET.get('addr_cache', None)# addr verfty
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    try:
        User.objects.get(user_id=long(login_account),addr_handle_cache=int(addr_cache))
    except:
        response_data['flag']      = 'no'
        response_data['addr_flag'] = 'no'
        response_data['yl_msg']    = u'添加地址失败'
        return response_data
    if FamilyRecord.objects.filter(user_id=long(login_account)).count()>15:
        response_data['flag'] = 'full'
        response_data['yl_msg'] = u'您的地址太多了...'
        return response_data
    if int(family_apt_num_id)==0:#verify failed
        status = random.randint(10000,99999)
        fRecordObj = FamilyRecord(entity_type = 0,ne_status = status,user_id=login_account,family_id=None)
    else:
        if int(family_block_id) == 0:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_building_num_id) + str(family_apt_num_id)
        else:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_block_id) + \
                    str(family_building_num_id) + str(family_apt_num_id)
        familyTuple = AddressDetails.objects.get_or_create(ad_id=fadId) 
        addrDetailsObj = familyTuple[0]
        auditStatus = familyTuple[1]
        if auditStatus:#new
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name=family_city
            addrDetailsObj.building_name=family_building_num
            addrDetailsObj.community_name=family_community
            addrDetailsObj.apt_name=family_apt_num
            addrDetailsObj.block_name = family_block
            addrDetailsObj.family_name = family_building_num+"-"+family_apt_num
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
            addrDetailsObj.apt_id = family_apt_num_id
            addrDetailsObj.city_id = family_city_id
            addrDetailsObj.block_id = family_block_id
            addrDetailsObj.building_id = family_building_num_id
            addrDetailsObj.community_id = family_community_id
            addrDetailsObj.save()
        else:
            pass
        fRecordTuple = FamilyRecord.objects.get_or_create(user_id=login_account,family=addrDetailsObj) 
        fRecordObj = fRecordTuple[0]
        fRecordObj.ne_status = 0
        if auditStatus:#证明第一个人
            fRecordObj.entity_type = 1
        else:
            fRecordObj.entity_type = 0
    fRecordObj.family_name = family_building_num+"-"+family_apt_num
    fRecordObj.family_city = family_city
    fRecordObj.family_city_id = family_city_id
    fRecordObj.family_community = family_community
    fRecordObj.family_community_id = family_community_id
    fRecordObj.family_building_num = family_building_num
    fRecordObj.family_building_num_id = family_building_num_id
    fRecordObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
    if primary_flag is None:
        fRecordObj.primary_flag = 0
    else:
        fRecordObj.primary_flag = 1
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = fadId
        userObj.user_community_id = family_community_id
        if family_block is None:
            userObj.user_family_address = family_city+family_community+"-"+family_building_num+"-"+family_apt_num
        else:
            userObj.user_family_address = family_city+family_community+"-"+family_block+"-"+family_building_num+"-"+family_apt_num
        userObj.save()
        #针对小区的介绍
        #nCount = AddressDetails.objects.filter(community_id=long(family_community_id)).count()
        #if 1==nCount:
        #    setWelcomeTopicForCommunity(family_city,family_city_id,family_community,family_community_id,userObj.user_family_address,userObj.user_family_id,userObj.user_nick)
    if family_block is None:
        fRecordObj.family_block_id = 0
    else:
        fRecordObj.family_block = family_block
        fRecordObj.family_block_id = family_block_id
    userObj = User.objects.get(user_id=login_account)
    userCurrentCommunityId = userObj.user_community_id
    fRecordObj.family_apt_num = family_apt_num
    fRecordObj.family_apt_num_id = family_apt_num_id
    fRecordObj.is_family_member = 0
    fRecordObj.user_avatar = userObj.user_portrait
    fRecordObj.save()
    curfamilyRecord = fRecordObj.getFamilyRecordID()
    #push 
    config = readIni()
    if status is None:
        response_data['flag'] = 'ok'
        response_data['family_id'] = fadId
        response_data['frecord_id'] = curfamilyRecord
        response_data['ne_status'] = 0
    else:
        response_data['flag'] = 'ok'
        response_data['family_id'] = 0
        response_data['frecord_id'] = curfamilyRecord
        response_data['ne_status'] = status
    response_data['addr_flag'] = 'ok'
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    pushTitle = config.get("users", "title")
    familyAddr = fRecordObj.family_address.encode('utf-8')
    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    if auditStatus:#证明第一个人
        response_data['entity_type'] = 1
        pushContent = config.get("users", "content13")+ familyAddr + config.get("users", "content14")
        currentPushTime = long(time.time()*1000)
        customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,userCurrentCommunityId)
        recordId = createPushRecord(2,2,pushTitle,pushContent,currentPushTime,login_account,(json.dumps(customContent)),userObj.user_community_id,login_account)
        customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,userCurrentCommunityId,recordId)
        AsyncAuditFamily.delay(apiKey, secretKey, alias, login_account, customContent, pushContent, pushTitle)
        from web.views_admin import setWelcomeTopic
        setWelcomeTopic(family_city,family_city_id,family_community,family_community_id,userObj.user_family_address,userObj.user_family_id,userObj.user_nick,userObj.getTargetUid())  
    else:
        response_data['entity_type'] = 0
        pushContent = config.get("users", "content6")+ familyAddr + config.get("users", "content8")
        currentPushTime = long(time.time()*1000)
        customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,userCurrentCommunityId)
        recordId = createPushRecord(2,2,pushTitle,pushContent,currentPushTime,login_account,(json.dumps(customContent)),userObj.user_community_id,login_account)
        customContent = genCustomContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,2,currentPushTime,2,userCurrentCommunityId,recordId)

        AsyncAddFamily.delay(apiKey, secretKey, alias, login_account, customContent, pushContent, pushTitle)
    
        curTimeToStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(currentPushTime/1000))
        dictInfo = {}
        from core.settings import YL_BACNEND
        dictInfo['subject'] = config.get("mail", "content0")
        dictInfo['message'] = config.get("mail", "content1") + userObj.user_phone_number.encode('utf-8') + '(' + \
                              userObj.user_nick.encode('utf-8')+')' + config.get("mail", "content2") + \
                              curTimeToStr.encode('utf-8') + config.get("mail", "content3") + \
                              familyAddr.encode('utf-8') + config.get("mail", "content4") + \
                              YL_BACNEND.encode('utf-8')
        AsyncSendMailToSingleAdmin.delay(dictInfo)
    
    return response_data

#修改地址
def ModifiFamily(request):
    response_data = {}
    fadId = None
    status = None
    fRecordObj = None
    family_block = None
    if request.method == 'POST':
        family_city_id         = request.POST.get('city_id', None)
        family_community_id    = request.POST.get('community_id', None)
        family_block_id        = request.POST.get('block_id', None)
        family_building_num_id = request.POST.get('buildnum_id', None)
        family_apt_num_id      = request.POST.get('aptnum_id', None)
        city_code              = request.POST.get('city_code', None)
        family_city            = request.POST.get('city', None)
        family_community       = request.POST.get('community', None)
        family_block           = request.POST.get('block', None)
        family_building_num    = request.POST.get('buildnum', None)
        family_apt_num         = request.POST.get('aptnum', None)
        login_account          = request.POST.get('user_id', None)
        family_id              = request.POST.get('family_id', None)
        neStatus               = request.POST.get('ne_status', None)
        addr_cache             = request.POST.get('addr_cache', None)# addr verfty
    else:
        family_city_id         = request.GET.get('city_id', None)
        family_community_id    = request.GET.get('community_id', None)
        family_block_id        = request.GET.get('block_id', None)
        family_building_num_id = request.GET.get('buildnum_id', None)
        family_apt_num_id      = request.GET.get('aptnum_id', None)
        city_code              = request.GET.get('city_code', None)
        family_city            = request.GET.get('city', None)
        family_community       = request.GET.get('community', None)
        family_block           = request.GET.get('block', None)
        family_building_num    = request.GET.get('buildnum', None)
        family_apt_num         = request.GET.get('aptnum', None) 
        login_account          = request.GET.get('user_id', None)
        family_id              = request.GET.get('family_id', None)
        neStatus               = request.GET.get('ne_status', None)
        addr_cache             = request.GET.get('addr_cache', None)# addr verfty
    try:
        User.objects.get(user_id=long(login_account),addr_handle_cache=int(addr_cache))
    except:
        response_data['flag']      = 'no'
        response_data['addr_flag'] = 'no'
        response_data['yl_msg']    = u'修改地址失败'
        return response_data
    
    if int(family_apt_num_id)==0:# The modified address is illegal
        if int(neStatus) == 0:
            try:
                fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),family_id=str(family_id)) 
            except Exception,e:
                response_data['Exception1'] = str(Exception)
                response_data['Error1'] = str(e)
                response_data['yl_msg']    = u'修改地址失败'
                return response_data
        else:
            try:
                fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),ne_status=neStatus)   
            except Exception,e:
                response_data['Exception2'] = str(Exception)
                response_data['Error2'] = str(e)
                response_data['yl_msg']    = u'修改地址失败'
                return response_data
        fRecordObj.family = None
        fRecordObj.entity_type = 0 # verify failed  
        status = random.randint(10000,99999)
        fRecordObj.ne_status = status
    else:# The modified address is valid
        if int(family_block_id) == 0:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_building_num_id) + str(family_apt_num_id)
        else:
            fadId = str(1000) + str(city_code) + str(family_community_id) + str(family_block_id) + \
                    str(family_building_num_id) + str(family_apt_num_id)
        familyTuple = AddressDetails.objects.get_or_create(ad_id=fadId) 
        addrDetailsObj = familyTuple[0]
        if familyTuple[1]:
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name=family_city
            addrDetailsObj.building_name=family_building_num
            addrDetailsObj.block_name = family_block
            addrDetailsObj.community_name=family_community
            addrDetailsObj.apt_name=family_apt_num
            addrDetailsObj.family_name = family_building_num+"-"+family_apt_num
            addrDetailsObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.apt_id = family_apt_num_id
            addrDetailsObj.city_id = family_city_id
            addrDetailsObj.block_id = family_block_id
            addrDetailsObj.building_id = family_building_num_id
            addrDetailsObj.community_id = family_community_id
            addrDetailsObj.save()
        else:
            pass
        if int(neStatus) == 0: 
            try:
                fRecordObj = FamilyRecord.objects.get(user_id=long(login_account),family_id=family_id)
            except Exception,e:
                response_data['Exception3'] = str(Exception)
                response_data['Error3'] = str(e)
                response_data['yl_msg']    = u'修改地址失败'
                return response_data
            #fRecordObj.entity_type = 0 # verify failed   
            #fRecordObj.ne_status = neStatus
        else: 
            try:
                fRecordTuple = FamilyRecord.objects.get_or_create(user_id=long(login_account),family_id=str(fadId))
                fRecordObj = fRecordTuple[0]
            except:
                response_data['flag'] = 'none_o_f'    
                response_data['yl_msg']    = u'修改地址失败'
                return response_data
            #fRecordObj.entity_type = 1 # verify success
            fRecordObj.family = addrDetailsObj
            #fRecordObj.ne_status = 0
    fRecordObj.family_name = family_building_num+"-"+family_apt_num
    fRecordObj.family_city = family_city
    fRecordObj.family_city_id = family_city_id
    fRecordObj.family_community = family_community
    fRecordObj.family_community_id = family_community_id
    fRecordObj.family_building_num = family_building_num
    fRecordObj.family_building_num_id = family_building_num_id
    fRecordObj.family_address = family_city+family_community+family_building_num+"-"+family_apt_num
    if fRecordObj.primary_flag == 0:
        fRecordObj.primary_flag = 0
    else:
        fRecordObj.primary_flag = 1
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = fadId
        userObj.user_community_id = family_community_id
        userObj.user_family_address = family_city+family_community+"-"+family_building_num+"-"+family_apt_num 
        userObj.save()
    if family_block is None:
        fRecordObj.family_block_id = 0
    else:
        fRecordObj.family_block = family_block
        fRecordObj.family_block_id = family_block_id
    fRecordObj.family_apt_num = family_apt_num
    fRecordObj.family_apt_num_id = family_apt_num_id
    fRecordObj.is_family_member = 0
    fRecordObj.user_avatar = (User.objects.get(user_id=long(login_account))).user_portrait
    fRecordObj.entity_type = 0
    fRecordObj.family_id = fadId
    fRecordObj.save()
    curfamilyRecord = fRecordObj.getFamilyRecordID()
    if fadId is None:
        response_data['flag'] = 'ok'
        response_data['ne_status'] = status
        response_data['family_id'] = 0
        response_data['frecord_id'] = curfamilyRecord
    else:
        response_data['flag'] = 'ok'
        response_data['ne_status'] = 0
        response_data['family_id'] = fadId
        response_data['frecord_id'] = curfamilyRecord
    response_data['entity_type'] = 0
    response_data['addr_flag'] = 'ok'
    return response_data 

#删除地址
def DeleFamilyRecord(request):
    response_data = {}
    if request.method == 'POST':
        familyId               = request.POST.get('family_id', None)
        login_account          = request.POST.get('user_id', None)
        primary_flag           = request.POST.get('flag', None)
        neStatus               = request.POST.get('nestatus', None)
        familyRecordId         = request.POST.get('record_id', None)
        addr_cache             = request.POST.get('addr_cache', None)# addr verfty
    else:
        login_account          = request.GET.get('user_id', None)
        primary_flag           = request.GET.get('flag', None)
        familyRecordId         = request.GET.get('record_id', None)
        addr_cache             = request.GET.get('addr_cache', None)# addr verfty
    try:
        User.objects.get(user_id=long(login_account),addr_handle_cache=int(addr_cache))
    except:
        response_data['flag']      = 'no'
        response_data['addr_flag'] = 'no'
        response_data['yl_msg']    = u'删除地址失败'
        return response_data    
    if int(primary_flag) == 0:
        pass
    else:
        userObj = User.objects.get(user_id=login_account)
        userObj.user_family_id = None
        userObj.user_family_address = None
        userObj.user_community_id = None
        userObj.save()
    if familyRecordId is not None:
        family_record = FamilyRecord.objects.filter(fr_id=long(familyRecordId)).delete()
    else:
        if int(neStatus) ==0:
            family_record = FamilyRecord.objects.filter(family_id=familyId, user_id=login_account).delete()
        else:
            family_record = FamilyRecord.objects.filter(ne_status=neStatus, user_id=login_account).delete()
    response_data['flag'] = 'ok'
    response_data['addr_flag'] = 'ok'
    return response_data

#设置当前地址
def UpdatePrimaryAddr(request):
    response_data = {}
    familyRecordObj = None
    userObj = None
    familyObj = None
    adminType = None
    oldfamily_id = request.POST.get('old_family_id', None)
    family_id    = request.POST.get('family_id', None)
    user_id      = request.POST.get('user_id', None)
    neStatus     = request.POST.get('ne_status', None)
    oldneStatus  = request.POST.get('old_ne_status', None)
    addr_cache   = request.POST.get('addr_cache', None)# addr verfty   
    try:
        userObj   = User.objects.get(user_id=user_id,addr_handle_cache=int(addr_cache))
    except:
        response_data['flag']      = 'no'
        response_data['addr_flag'] = 'no'
        response_data['yl_msg']    = u'设置地址失败'
        return response_data    
    if userObj is None:
        response_data['flag'] = 'none_u'
        return response_data
    if family_id is None:#new is not exist
        familyObj = None
    else:#new is exist
        try:
            familyObj = AddressDetails.objects.get(ad_id=family_id)
        except:
            response_data['flag'] = 'no_familyObj'    
            return response_data
    if familyObj is None:#new is not exist
        try:
            frNewObj = FamilyRecord.objects.get(ne_status = neStatus,user_id=user_id,family_id=None)
        except:
            response_data['flag'] = 'no_frNewObj'    
            return response_data
        if oldfamily_id is None:
            try:
                frOldObj = FamilyRecord.objects.get(ne_status = oldneStatus,user_id=user_id,family_id=None)
            except:
                response_data['flag'] = 'no_if_frOldObj'    
                return response_data
        else:
            try:
                frOldObj = FamilyRecord.objects.get(user_id=user_id,family_id=oldfamily_id)
            except:
                response_data['flag'] = 'no_else_frOldObj'    
                return response_data
        userObj.user_family_id = None      
        userObj.user_community_id = frNewObj.family_community_id 
        userObj.user_family_address = frNewObj.family_address
        userObj.save()
        frOldObj.primary_flag = 0
        frOldObj.save()
        frNewObj.primary_flag = 1
        frNewObj.save()
    else:#new is exist
        try:
            frNewObj = FamilyRecord.objects.get(user_id=user_id,family_id=family_id)
        except:
            response_data['flag'] = 'no_frNewObj'    
            return response_data
        if oldfamily_id is None:
            try:
                frOldObj = FamilyRecord.objects.get(ne_status = oldneStatus,user_id=user_id,family_id=None)
            except:
                frOldObj = None
               # response_data['flag'] = 'no_oldfamily'
               # return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            try:
                frOldObj = FamilyRecord.objects.get(user_id=user_id,family_id=oldfamily_id)
            except:
                response_data['flag'] = 'no_else_oldfamily'    
                return response_data
        #set user type(admin)
        currentCommunityId = frNewObj.family_community_id 
        try:
            adminType = Admin.objects.get(community_id=currentCommunityId,user_id=user_id)
            userObj.user_type = adminType.admin_type
            userObj.user_json = adminType.admin_info
        except:
            userObj.user_type = 0
        userObj.user_family_id = frNewObj.family.getAddrDetailId()
        userObj.user_community_id = currentCommunityId
        userObj.user_family_address = frNewObj.family_address 
        userObj.save()
        if frOldObj is None:
            pass
        else:
            frOldObj.primary_flag = 0
            frOldObj.save()
        frNewObj.primary_flag = 1
        frNewObj.save()
    response_data['flag'] = 'ok'
    response_data['addr_flag'] = 'ok'
    return response_data

#添加城市、小区、楼栋、门牌
# 发布时使用genBlockDict 测试时使用 genBlockDictWithDebug  
def HandleFamily(request):
    response_data = {}
    if request.method == 'POST':
        city_name    = request.POST.get('city_name', None)
        buildnum_id  = request.POST.get('buildnum_id', None)
        community_id = request.POST.get('community_id', None)
        block_id     = request.POST.get('block_id', None)
    else:
        city_name    = request.GET.get('city_name', None)
        buildnum_id  = request.GET.get('buildnum_id', None)
        community_id = request.GET.get('community_id', None)
        block_id     = request.GET.get('block_id', None)
    if city_name:
        json_data = []
        commObj = None
        cityObj = None
        try:
            cityObj = City.objects.get(city_name__contains=city_name)
            commObj = Community.objects.filter(city__city_name__contains=city_name)
        except:
            response_data['flag'] = 'none_o'
            return response_data
        if commObj:
            json_city = getAddressByQuerySet(cityObj)#serializers.serialize("json", cityObj)
            json_data.append(json_city)
            size = commObj.count()
            for i in range(0,size,1):
                if i+1 == size:
                    comm_id = commObj[i].getCommunityId()
                    comm_name = commObj[i].community_name
                    blockObj = Block.objects.filter(community__community_id=comm_id)
                    blockSize = blockObj.count()
                    if blockSize == 0:
                        blockDict = genBlockDict(comm_id, comm_name)
                        if blockDict is None:
                            continue
                        jsonObj = blockDict
                        json_data.append(jsonObj)
                    for j in range(0,blockSize,1):
                        blockId = blockObj[j].getBlockId()
                        blockName = blockObj[j].block_name
                        blockDict = genBlockDict(comm_id, comm_name, blockId, blockName)
                        if blockDict is None:
                            continue
                        if j+1 == blockSize:
                            jsonObj = blockDict
                            json_data.append(jsonObj)
                        else:
                            jsonObj = blockDict
                            json_data.append(jsonObj)
                else:
                    comm_id = commObj[i].getCommunityId()
                    comm_name = commObj[i].community_name
                    blockObj = Block.objects.filter(community__community_id=comm_id)
                    blockSize = blockObj.count()
                    if blockSize == 0:
                        blockDict = genBlockDict(comm_id, comm_name)
                        if blockDict is None:
                            continue
                        jsonObj = blockDict
                        json_data.append(jsonObj)
                    for j in range(0,blockSize,1):
                        blockId = blockObj[j].getBlockId()
                        blockName = blockObj[j].block_name
                        blockDict = genBlockDict(comm_id, comm_name, blockId, blockName)
                        if blockDict is None:
                            continue
                        jsonObj = blockDict
                        json_data.append(jsonObj)
            return json_data
        else:
            response_data['flag'] = 'none_o'
            return response_data
    if block_id:
        json_data = []
        buildObj = None
        try:
            buildObj = BuildNum.objects.filter(block__block_id=block_id)
        except:
            response_data['flag'] = 'none_o'    
            return response_data
        if buildObj:
            size = buildObj.count()
            for i in range(0,size,1):
                jsonObj = getCommunityByQuerySet(buildObj[i])
                json_data.append(jsonObj)
            return json_data
        else:
            response_data['flag'] = 'none_o'
            return response_data
    if community_id:
        json_data = []
        buildObj = None
        try:
            buildObj = BuildNum.objects.filter(community__community_id=community_id)
        except:
            response_data['flag'] = 'none_o'    
            return response_data
        if buildObj:
            size = buildObj.count()
            for i in range(0,size,1):
                jsonObj = getCommunityByQuerySet(buildObj[i])
                json_data.append(jsonObj)
            return json_data
        else:
            response_data['flag'] = 'none_o'
            return response_data
    if buildnum_id:
        json_data = []
        aptnumObj = None
        try:
            aptnumObj = AptNum.objects.filter(buildnum__buildnum_id=buildnum_id)
        except:
            response_data['flag'] = 'none_o'    # userObj not exist
            return response_data
        if aptnumObj:
            size = aptnumObj.count()
            for i in range(0,size,1):
                jsonObj = getAptNumberByQuerySet(aptnumObj[i])
                json_data.append(jsonObj)
            return json_data
        else:
            response_data['flag'] = 'none_o'
            return response_data

#获取邻居
def GetNeighbors(request):
    response_data = {}
    json_data = []
    block_id      = None
    community_id  = None
    fRecordObj    = None
    if request.method == 'POST':
        myuser_id    = request.POST.get('user_id', None)
        apt_num      = request.POST.get('apt_num', None)
        block_id     = request.POST.get('block_id', None)
        community_id = request.POST.get('community_id', None)
    else:
        myuser_id    = request.GET.get('user_id', None)
        apt_num      = request.GET.get('apt_num', None)
        block_id     = request.GET.get('block_id', None)
        community_id = request.GET.get('community_id', None)
    
    blackList = []
    try:
        blkListOtherQuerySet = BlackList.objects.filter(black_id = long(myuser_id))
        blkListSize = blkListOtherQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOtherQuerySet[i].user_id)
        blkListOwnQuerySet = BlackList.objects.filter(user_id = long(myuser_id))
        blkListSize = blkListOwnQuerySet.count()
        for i in range(0,blkListSize,1):
            blackList.append(blkListOwnQuerySet[i].black_id)
    except:
        blackList = []
    if block_id is None:
        try:
            fRecordObj = FamilyRecord.objects.filter(family_community_id=community_id,entity_type=1,primary_flag=1).exclude(user_id__in=blackList)
        except:
            response_data['flag'] = 'none_e_o'
            return response_data
    else:
        try:
            fRecordObj = FamilyRecord.objects.filter(family_community_id=community_id,family_block_id=block_id,entity_type=1,primary_flag=1).exclude(user_id__in=blackList)
        except:
            response_data['flag'] = 'none_e_o'
            return response_data
    if fRecordObj:
        size = fRecordObj.count()
        if size == 0:
            response_data['flag'] = 'none_f_o0'             
            return response_data
        for i in range(0, size,1):
            user_id = fRecordObj[i].user.getTargetUid()
            try:
                remObj = Remarks.objects.get(target_id=long(myuser_id),remuser_id=long(user_id))
                user_name = remObj.user_remarks
            except:
                user_name = fRecordObj[i].user.user_nick
            user_type = fRecordObj[i].user.user_type
            user_portrait = fRecordObj[i].user.user_portrait
            user_public_status = fRecordObj[i].user.user_public_status
            building_num = fRecordObj[i].family_building_num
            aptnum = fRecordObj[i].family_apt_num
            family_id = None
            try:
                family_id = fRecordObj[i].family.getAddrDetailId()
            except:
                family_id = '0'
            user_profession = fRecordObj[i].user.user_profession
            user_signature = fRecordObj[i].user.user_signature
            user_level = fRecordObj[i].user.user_level
            user_phone_number = fRecordObj[i].user.user_phone_number
            if i+1 == size:
                jsonObj = genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,family_id,user_type,\
                          user_phone_number,user_profession,user_signature,user_level,user_public_status)
                json_data.append(jsonObj)
            else:
                jsonObj = genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,family_id,user_type,\
                        user_phone_number,user_profession,user_signature,user_level,user_public_status)
                json_data.append(jsonObj)
        return json_data
    else:
        response_data['flag'] = 'none_f_o1'#success
        return response_data

#注册环信
def RegistEasemob(request):
    if request.method == 'POST':
        userName = request.POST.get('user')
    else:
        userName = request.GET.get('user')
    response_data = registUser(userName,userName)
    return response_data

#登录状态
def CheckPushChannelExist(request):
    userImei = None
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
    else:
        userPhone = request.GET.get('user_phone', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone)
        userImei = userObj.user_push_user_id
    except:
        response_data['flag'] = 'none'    # userObj not exist
        response_data['channelId'] = userImei 
        return response_data
    if userObj is not None:
        response_data['flag'] = 'ok'
    else:
        response_data['flag'] = 'no'
    response_data['channelId'] = userImei
    return response_data

#获取公开状态
def GetPublicStatus(request):
    response_data = {}
    if request.method == 'POST':
        userPhone = request.POST.get('user_phone', None)
        userId    = request.POST.get('user_id', None)
    else:
        userPhone = request.GET.get('user_phone', None)
        userId    = request.GET.get('user_id', None)
    try:
        userObj = User.objects.get(user_phone_number=userPhone,user_id=userId)
    except:
        response_data['flag'] = 'none'    # userObj not exist
        response_data['status'] = 0
        return response_data
    if userObj is not None:
        userStatus = userObj.user_public_status
        response_data['flag'] = 'ok'
        response_data['status'] = userStatus
    else:
        response_data['flag'] = 'ok'
        response_data['status'] = 0
    return response_data

def genAddrDetailInfoWithCache(userObj):
    addrList = []
    familyRecordObj = FamilyRecord.objects.filter(user=userObj)
    if familyRecordObj:
        familyRecordSize = familyRecordObj.count()
        if familyRecordSize == 0:
            pass
        else:
            for i in range(0,familyRecordSize,1):
                try:
                    family_id = familyRecordObj[i].family.getAddrDetailId()
                except:
                    family_id = None
                frId = familyRecordObj[i].getFamilyRecordID()
                family_name = familyRecordObj[i].family_name
                family_address = familyRecordObj[i].family_address
                family_building_num = familyRecordObj[i].family_building_num
                family_apt_num = familyRecordObj[i].family_apt_num
                is_family_member = familyRecordObj[i].is_family_member
                family_member_count = familyRecordObj[i].family_member_count
                primary_flag = familyRecordObj[i].primary_flag
                user_avatar = familyRecordObj[i].user_avatar
                city_name = familyRecordObj[i].family_city
                city_id = familyRecordObj[i].family_city_id
                block_name = familyRecordObj[i].family_block
                block_id = familyRecordObj[i].family_block_id
                community_name = familyRecordObj[i].family_community
                community_id = familyRecordObj[i].family_community_id
                entityType = familyRecordObj[i].entity_type 
                neStatus = familyRecordObj[i].ne_status
                try:
                    cityObj = City.objects.get(city_id=long(city_id))
                    city_code = cityObj.city_code
                except:
                    city_code = '0'
                apt_num_id = familyRecordObj[i].family_apt_num_id
                building_num_id = familyRecordObj[i].family_building_num_id
                addrList.append(genFamilyRecordDict(family_id,family_name,family_address,family_building_num,\
                                                     family_apt_num,is_family_member,family_member_count,\
                                                     primary_flag,user_avatar,city_name,frId,city_id,block_name,\
                                                     block_id,community_name,community_id,entityType,neStatus,
                                                     city_code,apt_num_id,building_num_id))
        
    return addrList
    
#获取token
def CheckIMEI(request):
    userObj = None
    imei = None
    response_data = {}
    if request.method == 'POST':
        IMEI      = request.POST.get('imei', None)
        addrCache = request.POST.get('addr_cache', None)
    else:
        IMEI      = request.GET.get('imei', None)
        addrCache = request.GET.get('addr_cache', None)
    try:
        if addrCache is None:
            response_data['flag'] = 'argv_error' # 参数传递错误
            return response_data
        userTuple = User.objects.filter(user_push_user_id=str(IMEI))
        userCounts = userTuple.count()
        imei = userTuple[0].user_push_user_id
        userAddrCache = userTuple[0].addr_handle_cache
        if int(userAddrCache) == (int(addrCache)%1000):
            response_data['addr_flag'] = 'ok'
        elif int(addrCache) == -1:
            response_data['addr_flag'] = 'empty' # 需要重新登录
            userTuple = None
        else:
            response_data['addr_flag'] = 'no'
            response_data['addr_cache'] = userAddrCache
            response_data['user_nick'] = userTuple[0].user_nick
            response_data['user_portrait'] = userTuple[0].user_portrait
            response_data['user_id'] = userTuple[0].getTargetUid()
            response_data['addr_info'] = genAddrDetailInfoWithCache(userTuple[0])
    except:
        userTuple = None
    if userTuple is None:
        response_data['flag'] = 'no' # 需要重新登录
    else:
        response_data['flag'] = 'ok' # 可以直接跳转到main
    response_data['imei'] = imei
    response_data['share_info'] = u'我正在使用优邻，可以找到邻居，分享家庭闲置工具，物业通知、报修跟踪'
    return response_data

#判断用户类型
def CheckUserType(request):
    type = 0
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    try:
        adminObj = Admin.objects.get(user_id=long(userId))
        type = adminObj.admin_type
    except:
        response_data['type'] = 0
    if int(type) == 2:#管理员
        response_data['type'] = 2
    elif int(type) == 4:#物业
        response_data['type'] = 4
    response_data['flag'] = 'ok'
    return response_data

#还原移除所有黑名单失败之前的黑名单
def UndoBlackList(request):
    response_data = {}
    if request.method == 'POST':
        user_id   = request.POST.get('user_id', None)
        blackList = request.POST.get('black_list', None)
    else:
        user_id   = request.GET.get('user_id', None)
        blackList = request.GET.get('black_list', None)
    if userId is None or blackList is None:
        response_data['flag'] = 'parameter_error'
        response_data['yl_msg'] = '传递参数错误'
        return response_data
    try:
        querysetlist=[]
        blackCount = len(blackList.split(':'))
        for i in range(0,blackCount,1):
            querysetlist.append(BlackList(user_id=long(user_id),black_id=long(blackList[i])))
        BlackList.objects.bulk_create(querysetlist)
        response_data['flag'] = 'ok'
        response_data['yl_msg'] = '还原成功'
        return response_data
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['yl_msg'] = '还原失败 '+str(Exception)+' '+str(e)
        return response_data
    
#解除用户所有黑名单
def ClearBlackList(request):
    response_data = {}
    if request.method == 'POST':
        user_id = request.POST.get('user_id', None)
    else:
        user_id = request.GET.get('user_id', None)
    if user_id is None:
        response_data['flag'] = 'parameter_error'
        response_data['yl_msg'] = '传递参数错误'
        return response_data
    BlackList.objects.filter(user_id=long(user_id)).delete()
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data['flag'] = 'ok'
    response_data['yl_msg'] = '解除所有黑名单成功'
    return response_data
        
#黑名单操作
def HandleBlackList(request):
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
        blackId  = request.POST.get('black_user_id', None)
        actionId = request.POST.get('action_id', None)  #添加为1，删除为2
    else:
        userId   = request.GET.get('user_id', None)
        blackId  = request.GET.get('black_user_id', None)
        actionId = request.GET.get('action_id', None)  #添加为1，删除为2
    if userId is None or blackId is None or actionId is None:
        response_data['flag'] = 'parameter_error'
        return response_data
    if 1 == int(actionId):#添加用户
        blacklistQuerySet = BlackList.objects.get_or_create(user_id=long(userId),black_id=long(blackId))
        if blacklistQuerySet[1]:
            AsyncAddBlackList.delay(userId,blackId)
    else:
        try:
            blackObj = BlackList.objects.get(user_id=long(userId),black_id=long(blackId))
            blackObj.delete()
            
            userObj = User.objects.get(user_id = long(userId))
            try:
                from users.models import Remarks
                remObj = Remarks.objects.get(target_id=long(black_user_id),remuser_id=long(user_id))
                user_name = remObj.user_remarks
            except:
                user_name = userObj.user_nick
            user_type = userObj.user_type
            user_portrait = userObj.user_portrait
            user_public_status = userObj.user_public_status
            user_profession = userObj.user_profession
            user_signature = userObj.user_signature
            user_level = userObj.user_level
            user_phone_number = userObj.user_phone_number
            familyId = userObj.user_family_id
            try:
                from users.models import FamilyRecord
                frObj = FamilyRecord.objects.get(family_id=familyId)
                building_num = frObj.family_building_num
                aptnum = frObj.family_apt_num
            except:
                building_num = None
                aptnum = None
            userInfo = genNeighborDict(userId,user_name,user_portrait,building_num,aptnum,familyId,user_type,\
                               user_phone_number,user_profession,user_signature,user_level,user_public_status)
            response_data['user_info'] = userInfo
            AsyncDelBlackList.delay(userId,blackId)
        except Exception,e:
            response_data['error1'] = str(Exception)
            response_data['error2'] = str(e)
            response_data['flag'] = 'del_error'
            return response_data
    response_data['flag'] = 'ok'
    return response_data

def genBlackListDictByUser(blackId,userId):
    dicts = {}
    userObj = User.objects.get(user_id = long(blackId))
    try:
        remObj = Remarks.objects.get(target_id=long(userId),remuser_id=long(blackId))
        userName = remObj.user_remarks
    except:
        userName = userObj.user_nick
    userAvatar = userObj.user_portrait
    publicStatus = userObj.user_public_status
#     1.地址不公开、职业不公开2.地址公开、职业不公开3.地址不公开、职业公开4.地址公开、职业公开
    if int(publicStatus)== 1:#地址不公开、职业不公开
        userAddress = '未公开'
        userPro = '未公开'
    elif int(publicStatus)== 2:#地址公开、职业不公开
        try:
            userCommunityId = userObj.user_community_id
            userAddress = Community.objects.get(community_id=long(userCommunityId)).community_name
        except Exception,e:
            userAddress = ' '
        userPro = '未公开'
    elif int(publicStatus)== 3:#地址不公开、职业公开
        userAddress = '未公开'
        try:
            userPro = userObj.user_profession
            if userPro is not None:
                if  str(userPro)=='null' or str(userPro)=='NULL':
                    userPro = '未设置'
            else:
                userPro = '未设置'
        except:
            userPro = '未设置'
    else: #int(publicStatus)==4:#地址公开、职业公开
        try:
            userCommunityId = userObj.user_community_id
            userAddress = Community.objects.get(community_id=long(userCommunityId)).community_name
        except Exception,e:
            userAddress = ' '
        try:
            userPro = userObj.user_profession
            if userPro is not None:
                if  str(userPro)=='null' or str(userPro)=='NULL':
                    userPro = '未设置'
            else:
                userPro = '未设置'
        except:
            userPro = '未设置'
    dicts.setdefault('userId',blackId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('userName',userName)
    dicts.setdefault('userAddr',userAddress)
    dicts.setdefault('userPro',userPro)
    return dicts

#获取黑名单
def GetBlackList(request):
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    blQuerySet = BlackList.objects.filter(user_id=long(userId))
    blObjSize = blQuerySet.count()
    if int(blObjSize) == 0:#没有黑名单
        response_data['flag'] = 'none'
    else:
        blackList = []
        for i in range(0,blObjSize,1):
            blackId = blQuerySet[i].black_id
            blackList.append(genBlackListDictByUser(blackId,userId))
        response_data['flag'] = 'ok'
        response_data['black_users_id'] = blackList
    return response_data

#判断是否被加入黑名单
def VerifyBlackList(request):
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
        senderId = request.POST.get('sender_id', None)
    else:
        userId   = request.GET.get('user_id', None)
        senderId = request.GET.get('sender_id', None)
    if senderId is None or userId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    try:
        blackObj = BlackList.objects.get(user_id=long(senderId),black_id=long(userId))
        response_data['flag'] = 'ok'
    except:
        response_data['flag'] = 'no'
    return response_data

def genSingleUserDict(myUserId,userObj):
    dicts = {}
    communityId = userObj.user_community_id
    userId = userObj.getTargetUid()
    dicts.setdefault('user_id', userId)
    try:
        remObj = Remarks.objects.get(target_id=long(myUserId),remuser_id=long(userId))
        userRemarks = remObj.user_remarks
        dicts.setdefault('user_nick', userRemarks)
    except:
        dicts.setdefault('user_nick', userObj.user_nick)
    dicts.setdefault('current_nick', userObj.user_nick)
    dicts.setdefault('user_portrait', userObj.user_portrait)
    dicts.setdefault('user_gender', userObj.user_gender)
    dicts.setdefault('user_phone', userObj.user_phone_number)
    dicts.setdefault('cur_family_id', userObj.user_family_id)
    dicts.setdefault('cur_community_id', communityId)
    dicts.setdefault('cur_address', userObj.user_family_address)
    dicts.setdefault('user_birthday', userObj.user_birthday)
    dicts.setdefault('user_public_status', userObj.user_public_status)
    dicts.setdefault('user_profession', userObj.user_profession)
    dicts.setdefault('user_signature', userObj.user_signature)
    try:
        commName = Community.objects.get(community_id=long(communityId)).community_name
        dicts.setdefault('cur_community_name', commName)
    except:
        dicts.setdefault('cur_community_name', None)
    try:
        cityName = Community.objects.get(community_id=long(communityId)).city.city_name
        dicts.setdefault('cur_city_name', cityName)
    except:
        dicts.setdefault('cur_city_name', None)
    dicts.setdefault('flag', 'ok')
    return dicts

#获取详细信息
def GetUserDetailInfo(request):
    response_data = {}
    if request.method == 'POST':
        myUserId = request.POST.get('my_user_id', None)
        userId   = request.POST.get('user_id', None)
    else:
        myUserId = request.GET.get('my_user_id', None)
        userId   = request.GET.get('user_id', None)
    if userId is None or myUserId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    try:
        userObj = User.objects.get(user_id=long(userId))
        return genSingleUserDict(myUserId,userObj)
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['Exception'] = str(Exception)
        response_data['Error'] = str(e)
        return response_data

def getSignDateDict(signinObj):
    dicts = {}
    dicts.setdefault('year', signinObj.year)
    dicts.setdefault('month', signinObj.month)
    dicts.setdefault('day', signinObj.day)
    dicts.setdefault('timestamp', signinObj.timestamp)
    return dicts

#获取用户签到日期
def GetUserSignDate(request):
    signDateList = []
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    curTimestamp = time.time()
    curTime = time.localtime(curTimestamp)
    curYear = int(curTime[0])
    curMon  = int(curTime[1])
    if curMon > 2:
        curMon = curMon - 2
    else:
        curYear = curYear - 1
        if curMon == 1:
            curMon = 11
        elif curMon == 2:
            curMon = 12
    dateNode=datetime.datetime(curYear,curMon,1,0,0,0)
    tagTimestamp=long(time.mktime(dateNode.timetuple()))    
    signinQuery = Signin.objects.filter(timestamp__gt=long(tagTimestamp),user_id=long(userId)).order_by('-timestamp')
    size = signinQuery.count()
    if size == 0:
        response_data['flag'] = 'none'
        return response_data
    for i in range(0,size,1):
        signDateList.append(getSignDateDict(signinQuery[i]))
    response_data['credit'] = ConLoginDays(userId)
    signDateList.insert(0,response_data)
    return signDateList

#判断是否签到
def CheckUserSign(request):
    userCredit = None
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    curTimestamp = time.time()
    curTime = time.localtime(curTimestamp)
    curYear = int(curTime[0])
    curMon  = int(curTime[1])
    curDay  = int(curTime[2])
    try:
        userObj = User.objects.get(user_id = long(userId))
        userCredit = userObj.user_credit
    except:
        response_data['flag'] = 'error'#userId传递错误
        response_data['Exception'] = str(Exception)
        response_data['Error'] = str(e)
        return response_data
    try:
        signinObj = Signin.objects.filter(year=curYear,month=curMon,day=curDay,user_id=long(userId))
        size = signinObj.count()
        if size == 0:
            signinObj = None
    except:
        signinObj = None
    if signinObj is None:#今天还没有签到
        response_data['flag'] = 'no'  #表示未签到
        response_data['credit'] = userCredit
        return response_data
    else:
        response_data['flag'] = 'ok'  #表示已签到
        response_data['credit'] = userCredit
        return response_data

def ConAttend(days,first,second):
    if (days[first]-days[second]) == 86400:#证明是连续签到
        return True
    else:
        return False;

#连续签到多少天获得多少积分    
def ConLoginDays(userId):
    integral = 0
    dayTimeStampList = []
    dayTimeStampDict = {1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0}
    signinQuerySet = Signin.objects.filter(user_id=long(userId)).order_by('-_id')[:5]
    for signObj in signinQuerySet:
        year  = signObj.year
        month = signObj.month
        day   = signObj.day
        timeString = "{0}-{1}-{2} 00:00:00".format(year,month,day)
        timeArray = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        dayTimeStampList.append(timeStamp)
    dayCounts = len(dayTimeStampList)
    for dayIndex in range(0,dayCounts,1):
        dayTimeStampDict[dayIndex+1] = dayTimeStampList[dayIndex]
    if dayCounts==1:#证明是第一天签到
        integral = 5
    elif dayCounts==2:#判断是否连续签到2天
        if ConAttend(dayTimeStampDict,1,2):#证明是连续签到
            integral = 7
        else:
            integral = 5
    elif dayCounts==3:#判断是否连续签到3天
        if ConAttend(dayTimeStampDict,1,2):#证明是连续签到
            if ConAttend(dayTimeStampDict,2,3):
                integral = 10
            else:
                integral = 7
        else:
            integral = 5
    elif dayCounts==4:#判断是否连续签到4天
        if ConAttend(dayTimeStampDict,1,2):#证明是连续签到2
            if ConAttend(dayTimeStampDict,2,3):#证明是连续签到3
                if ConAttend(dayTimeStampDict,3,4):#证明是连续签到4
                    integral = 13
                else:
                    integral = 10
            else:
                integral = 7
        else:
            integral = 5
    elif dayCounts==5:#判断是否连续签到4天
        if ConAttend(dayTimeStampDict,1,2):#证明是连续签到2
            if ConAttend(dayTimeStampDict,2,3):#证明是连续签到3
                if ConAttend(dayTimeStampDict,3,4):#证明是连续签到4
                    if ConAttend(dayTimeStampDict,3,4):#证明是连续签到4
                        integral = 15
                    else:
                        integral = 13
                else:
                    integral = 10
            else:
                integral = 7
        else:
            integral = 5
    return integral

#用户签到
def UserSignOperation(request):
    signinObj = None
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    curTimestamp = time.time()
    curTime = time.localtime(curTimestamp)
    curYear = int(curTime[0])
    curMon  = int(curTime[1])
    curDay  = int(curTime[2])
    try:
        signinObj = Signin.objects.filter(year=curYear,month=curMon,day=curDay,user_id=long(userId))
        size = signinObj.count()
        if size == 0:
            signinObj = None
    except:
        signinObj = None
    if signinObj is None:#今天还没有签到
        try:
            userObj = User.objects.get(user_id=long(userId))
            Signin.objects.create(year=curYear,month=curMon,day=curDay,
                                  timestamp=long(curTimestamp),user_id=long(userId))
        except Exception,e:
            response_data['flag'] = 'error'#userId传递错误
            response_data['Exception'] = str(Exception)
            response_data['Error'] = str(e)
            return response_data
        curExp = userObj.user_exp
        userObj.user_exp = curExp + 3 #签到给3经验值
        curCre = userObj.user_credit
        curCre = curCre + ConLoginDays(userId)
        userObj.user_credit = curCre #签到给3积分
        userObj.save()
        response_data['flag']   = 'ok'
        response_data['year']   = curYear
        response_data['month']  = curMon
        response_data['day']    = curDay
        response_data['credit'] = curCre
    else:#不允许再签到
        response_data['flag'] = 'no'
    return response_data
        
#获取积分
def GetUserCredit(request):
    response_data = {}
    if request.method == 'POST':
        userId   = request.POST.get('user_id', None)
    else:
        userId   = request.GET.get('user_id', None)
    try:
        userObj = User.objects.get(user_id=long(userId))
        userCredit = userObj.user_credit
        response_data['flag']  = 'ok'
        response_data['credit']  = userCredit
    except:
        response_data['flag'] = 'no'
    return response_data
       
def setWelcomeTopic(family_city,family_city_id,family_community,family_community_id,user_family_address,user_family_id,user_nick,user_id):
    data = {}
    config = readIni()
    title                 = config.get('topic', "topic_title1")+ user_nick.encode('utf-8') +config.get('topic', "topic_title2")
    topic_content         = config.get('topic', "topic_content")
    topic_content_0       = config.get('topic', "topic_content_0")
    topic_content_1       = config.get('topic', "topic_content_1")
    topic_content_2       = config.get('topic', "topic_content_2")
    topic_content         = topic_content + '\n' + topic_content_0 + '\n' + topic_content_1 + '\n' + topic_content_2
    topic_time            = long(time.time()*1000)
    forum_name            = config.get('topic', "forum_name")
    sender_id             = config.get('topic', "sender_id")
    sender_name           = config.get('topic', "sender_name")
    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    sender_portrait       = userAvatar
    sender_family_id      = config.get('topic', "sender_family_id")
    sender_family_address = user_family_address
    display_name          = config.get('topic', "sender_name")+"@"+family_community.encode('utf-8')
    sender_city_id        = family_city_id
    sender_community_id   = family_community_id
    topicObj  = Topic.objects.create(topic_title=title,topic_content=topic_content,topic_category_type=2,topic_time=topic_time,\
                                       forum_id=1, forum_name=forum_name, sender_id=sender_id,sender_name=sender_name, sender_portrait=sender_portrait,\
                                       sender_family_id=sender_family_id,sender_family_address=sender_family_address, display_name=display_name,\
                                       object_data_id=0,circle_type=1,send_status=0,sender_city_id=sender_city_id,sender_community_id=sender_community_id,\
                                       cache_key=user_id)
    topicId = topicObj.getTopicId() 
        
    AsyncSetWelcomeTopic.delay(topicId,sender_id,sender_community_id)
        
#设置标注
def SetUserRemarks(request):
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        remarksId   = request.POST.get('remarks_id', None)
        remarksName = request.POST.get('remarks_name', None)
    else:
        userId      = request.GET.get('user_id', None)  
        remarksId   = request.GET.get('remarks_id', None)
        remarksName = request.GET.get('remarks_name', None)
    if userId is None or remarksId is None or remarksName is None:
        response_data['flag'] = 'argv_err'
        return response_data
    remarksTuple = Remarks.objects.get_or_create(target_id=long(userId),remuser_id=long(remarksId))
    remarksTuple[0].user_remarks = remarksName
    remarksTuple[0].tag_id = 1#默认为1
    remarksTuple[0].save()   
    response_data['flag'] = 'ok'
    response_data['remarks_name'] = remarksName
    return response_data

#获取邀请码
def GetInvCode(request):
    response_data = {}
    if request.method == 'POST':
        familyId    = request.POST.get('family_id', None)
        userId      = request.POST.get('user_id', None)
        invPhone    = request.POST.get('inv_phone', None)
        invStatus   = request.POST.get('inv_status', None)
        invType     = request.POST.get('inv_type', None)
    if userId is None or invPhone is None or invType is None or familyId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    frAddrCount = 0
    try:
        User.objects.get(user_phone_number=invPhone)
        response_data['flag'] = 'exist'
        response_data['yl_msg'] = '该手机号已注册，无法邀请。'
        return response_data
    except:
        pass
    if int(invType)==1:#证明是邀请家人
        frAddrCount = FamilyRecord.objects.filter(family_id=familyId,entity_type=1).count()
        if int(frAddrCount) > 5:
            response_data['flag'] = 'overflow'
            response_data['yl_msg'] = '很抱歉，当前地址住户已满，无法邀请家人加入。'
            return response_data
    if invStatus is not None:
        invTime = long(time.time()*1000)
        invObj = Invitation(inv_time=invTime)
        invObj.inv_phone = invPhone
        invObj.inv_status = 3
        invObj.inv_type = int(invType)
        invObj.inv_family_id = familyId
        invObj.user_id = long(userId)
        invCode = str(long(time.time()*1000))[-8:]
        invObj.inv_code = invCode
        invObj.save()
        response_data['inv_code'] = invCode
        response_data['flag'] = 'ok'
        response_data['count'] = frAddrCount
        from core.settings import SHARE_URL
        response_data['yl_msg'] = '【优邻】邀请码：'+str(invCode)+\
                                  '。加入优邻，去看看'+ SHARE_URL
        return response_data
    
#邀请新用户
def InviteNewUsers(request):
    response_data = {}
    if request.method == 'POST':
        familyId    = request.POST.get('family_id', None)
        userId      = request.POST.get('user_id', None)
        invPhone    = request.POST.get('inv_phone', None)
        invType     = request.POST.get('inv_type', None)
        invCode     = request.POST.get('inv_code', None)
    else:
        familyId    = request.GET.get('family_id', None)
        userId      = request.GET.get('user_id', None)
        invPhone    = request.GET.get('inv_phone', None)
        invType     = request.GET.get('inv_type', None)
    if userId is None or invPhone is None or invType is None or familyId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    frAddrCount = 0
    if int(invType)==1:#证明是邀请家人
        frAddrCount = FamilyRecord.objects.filter(family_id=familyId,entity_type=1).count()
        if int(frAddrCount) > 5:
            response_data['flag'] = 'overflow'
            response_data['yl_msg'] = '很抱歉，当前地址住户已满，发邀请家人加入。'
            return response_data
    try:
        User.objects.get(user_phone_number=str(invPhone))
        response_data['flag'] = 'exist'
        response_data['yl_msg'] = '很抱歉您的好友已经注册了,您可以邀请其它好友注册拿积分。'
        return response_data
    except:#证明可以进行邀请
        #开始进行邀请
        try:
            invObj = Invitation.objects.get(inv_phone=str(invPhone),inv_code=str(invCode))
            invObj.inv_type = int(invType)
            invObj.inv_status = 1
            invTime = invObj.inv_time  
            invObj.save()      
            TimingTaskWithInvStatus.apply_async((invTime, userId), countdown=60*60*3)#3h失效
            response_data['inv_code'] = invCode
        except Exception,e:
            response_data['inv_code'] = invCode
            response_data['invPhone'] = invPhone
            response_data['invType'] = invType
            response_data['errr01'] = str(Exception)
            response_data['errr02'] = str(e)
        response_data['flag'] = 'ok'
        response_data['count'] = frAddrCount
        response_data['yl_msg'] = '推送短信已发送'
        return response_data

def genInviteInfo(invObj):
    dicts = {}
    dicts.setdefault('inv_time',invObj.inv_time)
    dicts.setdefault('inv_phone',invObj.inv_phone)
    dicts.setdefault('inv_status',invObj.inv_status)
    dicts.setdefault('inv_type',invObj.inv_type)
    return dicts
    
#获取邀请信息
def GetInviteInfo(request):
    invInfoList = []
    if request.method == 'POST':
        userId = request.POST.get('user_id', None)
    else:
        userId = request.GET.get('user_id', None)
    
    invQuerySet = Invitation.objects.filter(user_id=long(userId)) 
    invCount = invQuerySet.count()
    for i in range(0,invCount,1):
        invInfoList.append(genInviteInfo(invQuerySet[i]))  
    if invInfoList:
        query = Invitation.objects.filter(user_id=long(userId),inv_status=2)
        query.group_by = ['inv_phone']
        response_data = {}
        response_data['flag'] = 'ok'
        response_data['info'] = invInfoList
        response_data['count'] = query.count()
        return response_data
    else:
        response_data = {}
        response_data['flag'] = 'no'
        response_data['info'] = 'none'
        response_data['count'] = 0
        return response_data

#生成家人地址信息字典
def genInvFamilyRecordDict(frObj):
    dicts = {}
    dicts.setdefault('fr_id',frObj.getFamilyRecordID());
    dicts.setdefault('family_name',frObj.family_name);
    dicts.setdefault('family_address',frObj.family_address);
    dicts.setdefault('family_city',frObj.family_city);
    dicts.setdefault('family_city_id',frObj.family_city_id);
    dicts.setdefault('family_block',frObj.family_block);
    dicts.setdefault('family_block_id',frObj.family_block_id);
    dicts.setdefault('family_community',frObj.family_community);
    dicts.setdefault('family_community_id',frObj.family_community_id);
    dicts.setdefault('family_building_num',frObj.family_building_num);
    dicts.setdefault('family_building_num_id',frObj.family_building_num_id);
    dicts.setdefault('family_apt_num',frObj.family_apt_num);
    dicts.setdefault('family_apt_num_id',frObj.family_apt_num_id);
    dicts.setdefault('is_family_member',frObj.is_family_member);
    dicts.setdefault('entity_type',frObj.entity_type);
    dicts.setdefault('ne_status',frObj.ne_status);
    dicts.setdefault('primary_flag',frObj.primary_flag);
    dicts.setdefault('user_avatar',frObj.user_avatar);
    dicts.setdefault('user_id',frObj.user_id);
    dicts.setdefault('family_id',frObj.family_id);
    return dicts

#获取邀请家人成功地址详情
def GetInviteFamilyInfo(request):
    response_data = {}
    if request.method == 'POST':
        userId = request.POST.get('user_id', None)
        frId   = request.POST.get('fr_id', None)
    else:
        userId = request.GET.get('user_id', None)
        frId   = request.GET.get('fr_id', None)
    if userId is None or frId is None:
        response_data['flag'] = 'argv_err'#参数传递错误
        return response_data
    try:
        fRObj = FamilyRecord.objects.get(fr_id=long(frId),user_id=long(userId))
        response_data['flag'] = 'ok'
        response_data['fr_info'] = genInvFamilyRecordDict(fRObj)
        return response_data
    except Exception,e:
        response_data['flag'] = 'no'
        response_data['error'] = str(Exception)
        response_data['yl_msg'] = str(e)
        return response_data
    
#邀请码验状态
def CheckInviteStatus(request):
    response_data = {}
    if request.method == 'POST':
        invPhone = request.POST.get('inv_phone', None)
        invCode  = request.POST.get('inv_code', None)
    else:
        invPhone = request.GET.get('inv_phone', None)
        invCode  = request.GET.get('inv_code', None)
    if invPhone is None:
        response_data['flag'] = 'argv_err'#参数传递错误
        return response_data
    if invCode is None or (len(invCode)==0):
        response_data['flag'] = 'ok'#表名没有使用邀请码
        response_data['type'] = 0
        return response_data
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)

    invCodeLen = len(invCode)
    if invCodeLen == 8:#使用的是邀请码
        try:
            invItationTuple = Invitation.objects.filter(inv_phone=str(invPhone)).order_by('-inv_time')
            invObj = invItationTuple[0]
            curInvCode = invObj.inv_code
            if str(curInvCode) != str(invCode):
                response_data['flag'] = 'error'#表名邀请码错误
                response_data['yl_msg'] = '邀请码或手机号错误，请重新确认后填写...'
                return response_data
            try:
                curInvType = invObj.inv_type
                if int(curInvType) == 1:#家人
                    frAddrCount = 0
                    curFamilyId = invObj.inv_family_id
                    frAddrCount = FamilyRecord.objects.filter(family_id=curFamilyId,entity_type=1).count()
                    if int(frAddrCount) > 5:
                        response_data['flag'] = 'overflow'
                        response_data['yl_msg'] = '很抱歉，当前地址住户已满，无法邀请家人加入。'
                        return response_data
            except:
                pass
            response_data['flag'] = 'ok'
            response_data['type'] = curInvType#邀请的类型
            return response_data
        except:
            response_data['flag'] = 'error'#表名邀请码错误
            response_data['yl_msg'] = '邀请码或手机号错误，请重新确认后填写...'
            return response_data
    elif invCodeLen == 11:#使用的是邀请者的手机号
        try:
            userObj = User.objects.get(user_phone_number=str(invCode))
        except:
            userObj = None
        if userObj is None:
            response_data['flag'] = 'error'#表名邀请码错误
            response_data['yl_msg'] = '邀请码或手机号错误，请重新确认后填写...'
            return response_data
        userId = userObj.getTargetUid()
        invItationTuple = Invitation.objects.filter(inv_phone=str(invPhone),user_id=long(userId)).order_by('-inv_time')
        if invItationTuple.count() > 0:#永远使用最新的邀请
            type = invItationTuple[0].inv_type
            response_data['flag'] = 'ok'
            response_data['type'] = type#邀请的类型
            return response_data
        else:
            response_data['flag'] = 'error'#表名此手机并没有被邀请
            response_data['type'] = -1
            response_data['yl_msg'] = '邀请码或手机号错误，请重新确认后填写...'
            return response_data
    else:
        response_data['flag'] = 'error'#表明填写的邀请码错误
        response_data['type'] = 0
        response_data['yl_msg'] = '邀请码或手机号错误，请重新确认后填写...'
        return response_data
    
#短信验证码验证        
def CodeWtihmobVerify(request): 
    response_data = {}
    if request.method == 'POST':
        phone = request.POST.get('phone', None)
        code  = request.POST.get('code', None)
        type  = request.POST.get('ios', None)
    else:
        phone = request.GET.get('phone', None)
        code  = request.GET.get('code', None)
        type  = request.GET.get('ios', None)
    if phone is None or code is None:
        response_data['flag'] = 'argv_err'#参数传递错误
        return response_data
    from users.mobsms import MobSMS
    mobSMS = MobSMS()
    if type == None:
        type = 'android'
    relValue = mobSMS.verify_sms_code(86,phone,code,type)
    response_data['flag'] = relValue
    return response_data
    
#发送邮件
def SendEmailToAdmin(dictInfo):
    response_data = {}
    from django.core.mail import send_mail
    from core.settings import EMAIL_HOST_USER,EMAIL_RECV_USER
    try:
        send_mail(dictInfo['subject'], dictInfo['message'], EMAIL_HOST_USER,[EMAIL_RECV_USER], fail_silently=False)
    except Exception,e:
        response_data['error1'] = str(Exception)
        response_data['error2'] = str(e)
        return response_data

def TestSearch(request):
    response_data = {}
    return response_data


def Test(request):
    response_data = {}
    if request.method == 'POST':
        type     = request.POST.get('type', None) #hotel  cater  life
        sortname = request.POST.get('sortname', None)#default  price  overall_rating  comment_num  distance
        query    = request.POST.get('query', None)# 银行$酒店
        pagenum  = request.POST.get('pagenum', None)# 0 1 2
        commid   = request.POST.get('commid', None)#0
    else:
        type     = request.GET.get('type', None)
        sortname = request.GET.get('sortname', None)
        query    = request.GET.get('query', None)
        pagenum  = request.GET.get('pagenum', None)
        commid   = request.GET.get('commid', None)
    import sys
    import requests 
    default_encoding = 'utf-8'
#    if sys.getdefaultencoding() != default_encoding:
#        reload(sys)
#        sys.setdefaultencoding(default_encoding)
#     query = '饭店'+'$'+'台球'     
    commObj = Community.objects.get(community_id=long(commid))
    location = (commObj.community_lat).encode('gbk') + ',' + (commObj.community_lng).encode('gbk')
    filter = 'industry_type:%s|sort_name:%s|sort_rule:%s'%(type,sortname,'1')
    payload= {'query'   : query, 
              'location': location, 
              'radius'  : 10000,
              'pagesize': 20, 
              'pagenum' : pagenum, 
              'filter'  : filter
             }
    url = "http://api.map.baidu.com/place/v2/search?query=%s&location=%s&radius=%s&output=json\
           &ak=RBhONZRWP3VjTbUx6cvqg3IK&scope=2&detail=1&page_size=%s&page_num=%s&%s"\
           %(payload['query'],payload['location'],payload['radius'],\
             payload['pagesize'],payload['pagenum'],payload['filter'])
    res = requests.get(url).content
    jsonobj = json.loads(res)
    infolist = []
    for infoindex in range(len(jsonobj['results'])):
        infolist.append(GenDetailDict(jsonobj,infoindex,commid,type))
    response_data['flag'] = 'ok'
    response_data['infolist'] = infolist
    return response_data

def GenDetailDict(jsonobj,infoindex,commid,type):
    dict = {}
    dict['uid']        = jsonobj['results'][infoindex]['uid']
    dict['name']       = jsonobj['results'][infoindex]['name']
    dict['address']    = jsonobj['results'][infoindex]['address']
    dict['location']   = json.dumps(jsonobj['results'][infoindex]['location'])
    dict['distance']   = long(jsonobj['results'][infoindex]['detail_info']['distance'])
    try:
        dict['shophours'] = jsonobj['results'][infoindex]['detail_info']['shop_hours']
    except:
        dict['shophours'] = None
    try:
        dict['overallrating'] = float(jsonobj['results'][infoindex]['detail_info']['overall_rating'])
    except:
        dict['overallrating'] = 0
    try:
        dict['favoritenum'] = float(jsonobj['results'][infoindex]['detail_info']['favorite_num'])
    except:
        dict['favoritenum'] = 0
    try:
        dict['tag'] = jsonobj['results'][infoindex]['detail_info']['tag']
    except:
        dict['tag'] = None
    try:
        dict['detail_url'] = jsonobj['results'][infoindex]['detail_info']['detail_url']
    except:
        dict['detail_url'] = None
    try:
        dict['telephone'] = jsonobj['results'][infoindex]['telephone']
    except:
        dict['telephone'] = None
    try:
        if(str(type)=='life'):
            dict['img_url'] = btsouputilone(dict['detail_url'])
        elif(str(type)=='hotel'):
            dict['img_url'] = btsouputiltwo(dict['detail_url'],dict['uid'])
        elif(str(type)=='cater'):
            dict['img_url'] = btsouputilthree(dict['detail_url'])
    except:
        dict['img_url'] = None
    from addrinfo.models import BusinessCircle
#     BusinessCircle.objects.create(bc_uid=dict['uid'],
#                                   city_id = 1,
#                                   community_id = commid,
#                                   bc_name = dict['name'],
#                                   bc_address = dict['address'],
#                                   bc_location = dict['location'],
#                                   bc_tag = dict['tag'],
#                                   bc_distance = dict['distance'],
#                                   bc_telephone = dict['telephone'],
#                                   bc_shophours = dict['shophours'],
#                                   bc_facility = dict['overallrating'],
#                                   bc_favorite = dict['favoritenum'],
#                                   bc_imgurl = dict['img_url'])
    return dict

def btsouputilone(detail_url):
    imgList = []
    import urllib2
    from bs4 import BeautifulSoup
    if detail_url is None:
        return 'no detail_url'
    else:
        page = urllib2.urlopen(detail_url)
        html_doc = page.read()
        soup = BeautifulSoup(html_doc.decode('utf-8'))
        for tag in soup.find_all(href='#picresult'):
#            imgList.append(str(tag))
            imgstr = str(tag).split('src=\"')
            imgList.append(imgstr[1].replace("\"/>\n</a>","").replace("amp;",""))
    return imgList[0]


def btsouputiltwo(detail_url,detail_uid):
    imgList = []
    import urllib,urllib2,json
    from bs4 import BeautifulSoup
#    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#    values = {'name' : 'Michael Foord',
#          'location' : 'Northampton',
#          'language' : 'Python' }
#    headers = { 'User-Agent' : user_agent }
    if detail_url is None:
        return 'no detail_url'
    else:
#        data = urllib.urlencode(values)
#        req = urllib2.Request('http://map.baidu.com/detail?qt=ninf&uid=2b26123bfbc3175a3310af65&detail=hotel', data, headers)
        page = urllib2.urlopen('http://map.baidu.com/detail?qt=img&uid='+detail_uid)
#        html_doc = page.read()
        json_str = json.load(page)
        head_img = json_str['images']
#        dict_doc = json.read(html_doc)
#        soup = BeautifulSoup(html_doc.decode('utf-8'))
#        for tag in soup.find_all('div',attrs={'class':'img-container haspic'}):
#            imgList.append(str(tag))
#    ty = type(json_str['images'])
#    dictsss = {}
#    dictsss['a'] = 1
    str2 = ''
    str3 = ''
    str5 = ''
    i = 0
    for str1 in head_img:
        str2 = head_img[str1]
    for str3 in str2:
        for str4 in str3:
            str5 = str3[str4]
        i = i+1
        if(i==1):
            break
#     head_img = str(head_img[0])
    return str5 #head_img['headImages']


def btsouputilthree(detail_url):
    imgList = []
    import urllib2
    from bs4 import BeautifulSoup
    if detail_url is None:
        return 'no detail_url'
    else:
        page = urllib2.urlopen(detail_url)
        html_doc = page.read()
        soup = BeautifulSoup(html_doc.decode('utf-8'))
        for tag in soup.find_all('img',class_='head-img'):
#            imgList.append(str(tag))
            imgstr = str(tag).split('src=\"')
            imgList.append(imgstr[1].replace("\"/>","").replace("amp;",""))
    return imgList[0]



def Btsoupnews(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}
    news_data = {}
    infolist = []
    if request.method == 'POST':
        type     = request.POST.get('keyword', None)
        pagenum  = request.POST.get('page', None)
        commid   = request.POST.get('commid', None)
    else:
        type     = request.GET.get('keyword', None)
        pagenum  = request.GET.get('page', None)
        commid   = request.GET.get('commid', None)
    commObj = Community.objects.get(community_id=long(commid))
    import sys, urllib, urllib2, json
    import time
    import datetime
    from web.models import News
    today = datetime.date.today()
    todaytime = long(time.mktime(time.strptime(str(today),'%Y-%m-%d'))*1000)
    urlbase = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news?page=1&count=20'
    urllist = []
    if type != None:
       typelist = str(type).split('$')
       for typeitem in typelist:
           url = urlbase+'&keyword=%s'%typeitem
           urllist.append(url)
#       url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news?keyword=%s&page=1&count=20'%type
    else:
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'经济'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'科技'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'娱乐'+'&page=1'+'&count=20'
        urllist.append(url)
    for urlitem in urllist:
        req = urllib2.Request(urlitem)
        req.add_header("apikey", "f2f2251558ce7cadaeee02d477baf40b")
        resp = urllib2.urlopen(req)
        try:
            json_str = json.load(resp)
        except:
            response_data['flag'] = 'error'
            return response_data
        for news_item in json_str['retData']['data']:
            news_data = {}
            news_data['title'] = news_item['title']
            news_data['abstract'] = news_item['abstract']
            news_data['url'] = news_item['url']
            news_data['datetime'] = news_item['datetime']
            news_data['index'] = len(infolist)
            try:
                news_data['sml_pic'] = news_item['img_url']
            except:
                news_data['sml_pic'] = None
            news_data['resource'] = None
            srctype = news_data['url'].replace("http://","").replace("www.","").split('.com/')[0].split('.cn/')
            news_data['type'] = srctype[0]
            try:
                detail = urllib2.urlopen(news_data['url'])
            except:
                detail = None
            news_data['content'] = None
            if detail != None:
#todaytime = long(time.mktime(time.strptime(str(today),'%Y-%m-%d'))*1000)
                if news_data['type'] == 'toutiao' and (long(time.mktime(time.strptime(news_data['datetime'],'%Y-%m-%d %H:%M'))*1000) > todaytime):
                    news_data['resource'] = '今日头条'
                    pagestr = Resource_Analysis(news_data['url'])
                    news_data['content'] = pagestr
                if news_data['content'] != None and news_data['sml_pic'] != None:
                    infolist.append(news_data)
                    News.objects.create(
                                  new_title=news_data['title'],
                                  pri_flag=1 if (news_data['index'] == 0) else 0,
                                  new_introduce=news_data['abstract'],
                                  new_source=news_data['resource'],
                                  new_content=news_data['content'],
                                  new_small_pic=news_data['sml_pic'],
                                  city_id=commObj.city_id,
                                  community_id=commid,
                                  new_add_time=long(time.time()*1000),
                                  push_flag=0)

#        infolist.append(news_data)  
    response_data['flag'] = 'ok'
    response_data['data'] = infolist
    return response_data

def GetBtsoupnews(commid):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    news_data = {}
    infolist = []
    type = None
    pagenum = None
    if int(commid) == 0:
        commObj = None
    else:
        commObj = Community.objects.get(community_id=long(commid))
        
    import sys, urllib, urllib2, json
    import time
    import datetime
    from web.models import News,NewsPush
    today = datetime.date.today()
    todaytime = long(time.mktime(time.strptime(str(today),'%Y-%m-%d'))*1000)
    urlbase = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news?page=1&count=20'
    urllist = []
    if type != None:
       typelist = str(type).split('$')
       for typeitem in typelist:
           url = urlbase+'&keyword=%s'%typeitem
           urllist.append(url)
#       url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news?keyword=%s&page=1&count=20'%type
    else:
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'经济'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'科技'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'娱乐'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'体育'+'&page=1'+'&count=20'
        urllist.append(url)
        url = 'http://apis.baidu.com/songshuxiansheng/real_time/search_news/?'+'keyword='+'民生'+'&page=1'+'&count=20'
        urllist.append(url)
    newsIdList = []
    primaryInfos = {}
    for urlitem in urllist:
        req = urllib2.Request(urlitem)
        req.add_header("apikey", "f2f2251558ce7cadaeee02d477baf40b")
        resp = urllib2.urlopen(req)
        try:
            json_str = json.load(resp)
        except:
            infolist = []
            GetBtsoupnews(commid)
            return
        try:
            jsonString = json_str['retData']['data']
        except:
            infolist = []
            jsonString = None
            GetBtsoupnews(commid)
            return
        for news_item in jsonString:
            news_data = {}
            news_data['title'] = news_item['title']
            news_data['abstract'] = news_item['abstract']
            news_data['url'] = news_item['url']
            news_data['datetime'] = news_item['datetime']
            news_data['index'] = len(infolist)
            try:
                news_data['sml_pic'] = news_item['img_url']
            except:
                news_data['sml_pic'] = None
            news_data['resource'] = None
            srctype = news_data['url'].replace("http://","").replace("www.","").split('.com/')[0].split('.cn/')
            news_data['type'] = srctype[0]
            try:
                detail = urllib2.urlopen(news_data['url'])
            except:
                detail = None
            news_data['content'] = None
            if detail != None:
#todaytime = long(time.mktime(time.strptime(str(today),'%Y-%m-%d'))*1000)
                if news_data['type'] == 'toutiao' and (long(time.mktime(time.strptime(news_data['datetime'],'%Y-%m-%d %H:%M'))*1000) > todaytime):
                    news_data['resource'] = '今日头条'
                    pagestr = Resource_Analysis(news_data['url'])
                    news_data['content'] = pagestr
                if news_data['content'] != None and news_data['sml_pic'] != None:
                    infolist.append(news_data)
                if len(infolist)>6:
                    break
    from core.settings import PUSH_STATUS
    from web.models import Subscription
    subScriptQuerySet = Subscription.objects.filter(s_type=0)
    subSize = subScriptQuerySet.count()
    if commObj is None:
        for index in range(0,subSize,1):
            commObj = subScriptQuerySet[index].community
            commid = commObj.community_id
            newsIdList = []
            for newsIndex in range(0,len(infolist),1):
                priFlag = 1 if (infolist[newsIndex]['index'] == 0) else 0
                newsObj = News(
                              new_title=infolist[newsIndex]['title'],
                              pri_flag=priFlag,
                              new_introduce=infolist[newsIndex]['abstract'],
                              new_source=infolist[newsIndex]['resource'],
                              new_content=infolist[newsIndex]['content'],
                              new_small_pic=infolist[newsIndex]['sml_pic'],
                              city_id=commObj.city_id,
                              community_id=commid,
                              new_add_time=long(time.time()*1000),
                              push_flag=1)
                newsObj.save()
                newsIdList.append(newsObj.getNewId())
                if priFlag == 1:#主新闻
                    import copy
                    primaryInfos = copy.deepcopy(infolist[newsIndex])
            #推送记录
            if len(newsIdList) < 3:
                infolist = []
                jsonString = None
                GetBtsoupnews(commid)
                return
            idstring = ''
            for newId in range(0,len(newsIdList),1):
                idstring = idstring+str(newsIdList[newId])+','
            idstring = idstring[:-1]                  
            currentPushTime = long(time.time()*1000)                    
            push_time = currentPushTime
            pushObj = NewsPush.objects.create(push_newIds=idstring,push_time=push_time,community_id=commid)
                
            config = readIni()
            tagSuffix = config.get('news', "tagSuffix")
            pushTitle = primaryInfos['title']
            customTitle = primaryInfos['title']
            userAvatar = settings.RES_URL+'res/default/avatars/default-comm-news.png'
            message1 = primaryInfos['abstract']
            from web.views_admin import getNewMsgDict
            custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,commid)
            recordId = createPushRecord(5,1,customTitle,message1,currentPushTime,2001,json.dumps(custom_content),commid,2001)   
            custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,commid,recordId)      
            apiKey = config.get("SDK", "apiKey")
            secretKey = config.get("SDK", "secretKey")
            tagName = tagSuffix+str(commid)
            pushExtra = {'pTitle': customTitle}
            pushExtra.update(custom_content)
       #     pushExtra = custom_content
            _jpush = jpush.JPush(apiKey,secretKey) 
            push = _jpush.create_push()
            push.audience = jpush.all_
            push.audience = jpush.audience(
                        jpush.tag(tagName),
                    )    
            push.notification = jpush.notification(
                                ios=jpush.ios(alert=message1, badge="+1", extras=pushExtra),
                                android=jpush.android(message1,customTitle,None,pushExtra)
                            )
            push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
            push.platform = jpush.all_
            push.send()  
    else:
        for newsIndex in range(0,len(infolist),1):
            priFlag = 1 if (infolist[newsIndex]['index'] == 0) else 0
            newsObj = News(
                          new_title=infolist[newsIndex]['title'],
                          pri_flag=priFlag,
                          new_introduce=infolist[newsIndex]['abstract'],
                          new_source=infolist[newsIndex]['resource'],
                          new_content=infolist[newsIndex]['content'],
                          new_small_pic=infolist[newsIndex]['sml_pic'],
                          city_id=commObj.city_id,
                          community_id=commid,
                          new_add_time=long(time.time()*1000),
                          push_flag=1)
            newsObj.save()
            newsIdList.append(newsObj.getNewId())
            if priFlag == 1:#主新闻
                import copy
                primaryInfos = copy.deepcopy(infolist[newsIndex])
        if len(newsIdList) < 3:
            infolist = []
            jsonString = None
            GetBtsoupnews(commid)
            return
        #推送记录
        idstring = ''
        for newId in range(0,len(newsIdList),1):
            idstring = idstring+str(newsIdList[newId])+','
        idstring = idstring[:-1]                  
        currentPushTime = long(time.time()*1000)                    
        push_time = currentPushTime
        pushObj = NewsPush.objects.create(push_newIds=idstring,push_time=push_time,community_id=commid)
            
        config = readIni()
        tagSuffix = config.get('news', "tagSuffix")
        pushTitle = primaryInfos['title']
        customTitle = primaryInfos['title']
        userAvatar = settings.RES_URL+'res/default/avatars/default-comm-news.png'
        message1 = primaryInfos['abstract']
        from web.views_admin import getNewMsgDict
        custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,commid)
        recordId = createPushRecord(5,1,customTitle,message1,currentPushTime,2001,json.dumps(custom_content),commid,2001)   
        custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,commid,recordId)      
        apiKey = config.get("SDK", "apiKey")
        secretKey = config.get("SDK", "secretKey")
        tagName = tagSuffix+str(commid)
        pushExtra = {'pTitle': customTitle}
        pushExtra.update(custom_content)
     #   pushExtra = custom_content
        _jpush = jpush.JPush(apiKey,secretKey) 
        push = _jpush.create_push()
        push.audience = jpush.all_
        push.audience = jpush.audience(
                    jpush.tag(tagName),
                )    
        push.notification = jpush.notification(
                            ios=jpush.ios(alert=message1, badge="+1", extras=pushExtra),
                            android=jpush.android(message1,customTitle,None,pushExtra)
                        )
        push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
        push.platform = jpush.all_
        push.send()
                
def Resource_Analysis(detail_url):
    detailList = []
    import urllib2
    from bs4 import BeautifulSoup
    if detail_url is None:
        return 'no detail_url'
    else:
        page = urllib2.urlopen(detail_url)
        html_doc = page.read()
        soup = BeautifulSoup(html_doc.decode('utf-8'))
        for tag in soup.find_all('div',class_='article-content'):
           strtest = str(tag).replace("<div class=\"article-content\">","")
           strtest1 = strtest[0:len(strtest)-6].split("<div class=\"mp-vote-box")[0]
           soup1 = BeautifulSoup(strtest1.decode('utf-8'))
           for tag1 in soup1.find_all('div',class_='tt-video-box'):
               return None
           strtest2 = strtest1.replace("onerror=\"javascript:errorimg.call(this);\" ","")
#replace("http","https").replace("onerror=\"javascript:errorimg.call(this);\" ","")
#           retest = re.compile("(\"https://([a-z]|[0-9]|\.|\/)*\"){1}")
#           retlist = retest.split(strtest2)
#           return retlist
#           page = ''
#           for ret in retlist:
#               if len(ret)<4:
#                   page = page
#               else:
#                   page = page+'--'+str(ret)[1:6]
#                   if(str(ret)[1:6] == 'https'):
#                       try:
#                           urllib2.urlopen(ret[1:len(ret)-1])
#                           page = page + str(ret)
#                       except:
#                           page = page + str(ret).replace("https","http")
#                   else:
#                       page = page + str(ret)
#               html_doc = page.read()
#           return page
           reobj = re.compile("img_width=\"[0-9]+\"")
           strtest3 = reobj.sub("width=\"100%\"",strtest2)
           reobj1 = re.compile("img_height=\"[0-9]+\"")
#           return retest.findall(strtest2)   
           return reobj1.sub("",strtest3)
#宝箱
def GetTreasureBox(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}
    if request.method == 'POST':
        userId          = request.POST.get('user_id', None)
        communityId     = request.POST.get('community_id', None)
    else:
        userId          = request.GET.get('user_id', None)
        communityId     = request.GET.get('community_id', None)
    if userId is None or communityId is None:
        response_data['flag'] = 'argv_error'
        return response_data
    giftTypeList = []
    tbQuerySet = Treasurebox.objects.filter(tb_comm_id=long(communityId),tb_status=1)
    tbSize = tbQuerySet.count()
    for i in range(0,tbSize,1):
        giftTypeList.append(tbQuerySet[i].tb_gift_list.g_type)
    if giftTypeList:
        curTimestamp = time.time()
        curTime = time.localtime(curTimestamp)
        curYear = int(curTime[0])
        curMon  = int(curTime[1])
        curDay  = int(curTime[2])
        index = 0
        for x in giftTypeList:
            ugrQuerySet = UserGiftsRecord.objects.filter(ug_comm_id=long(communityId),\
                                                         ug_user_id=long(userId),ug_year=curYear,\
                                                         ug_month=curMon,ug_day=curDay,ug_type=int(x))
            ugrSize = ugrQuerySet.count()
            if ugrSize > 0:
                response_data['flag'] = 'no' #表示已经领取了今天的奖品
                return response_data
            else:#还没有领取过奖品
                index = index + 1
        if index == tbSize:
            response_data['flag'] = 'ok' #表示当天一件奖品都没有获取
#             response_data['flag'] = 'no' #临时设置
            response_data['index'] = index
            return response_data
        else:
            response_data['flag'] = 'own' #表示当天一件奖品有获取
#             response_data['flag'] = 'no' #临时设置
            response_data['index'] = index
            return response_data
    else:
        response_data['flag'] = 'empty' #表示没有奖品
        response_data['yl_msg'] = u'当日没有奖品'
        return response_data

def TestJPushFunc(pushType,pushAlias):
    dicts = {}
    dicts.setdefault('title',u'推送标题')
    dicts.setdefault('key1','value1')
    dicts.setdefault('key2','value2')
    
    config = readIni()
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    _jpush = jpush.JPush(apiKey,secretKey)
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias('youlin_alias_'+pushAlias),
            )
    #ios=jpush.ios(alert="content", badge="+1", sound="a.caf", extras=dicts),
    try:
        if pushType == 'aud':
            push.notification = jpush.notification(
                        ios=jpush.ios(alert="content", badge="+1", extras=dicts),
                        android=jpush.android('content','title',None,dicts)
                    )
        elif pushType == 'msg':
            push.message = jpush.message(
                    'content',
                    u"jpush_type",
                    None,
                    u'extras'
                )
        push.options = {"time_to_live":86400, "sendno":9527, "apns_production":False}
        push.platform = jpush.all_
        push.send()
    except Exception,e:
        response_data = {}
        response_data['Exception'] = str(Exception)
        response_data['Error'] = str(e)
        return response_data


def TestJPush(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if request.method == 'POST':
        pushType  = request.POST.get('push_type', None)
        pushAlias = request.POST.get('push_alias', None)
    else:
        pushType  = request.GET.get('push_type', None)
        pushAlias = request.GET.get('push_alias', None)
    
#     AsyncJPush.apply_async((pushType,pushAlias),countdown=5)
    dicts = {}
    dicts.setdefault('title',u'推送标题')
    dicts.setdefault('key1','value1')
    dicts.setdefault('key2','value2')
    
    config = readIni()
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    _jpush = jpush.JPush(apiKey,secretKey)
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias('youlin_alias_'+pushAlias),
            )
    """
    #ios=jpush.ios(alert="content", badge="+1", sound="a.caf", extras=dicts),
    try:
        if pushType == 'aud':
            push.notification = jpush.notification(
                        ios=jpush.ios(alert="content", badge="+1", extras=dicts),
                        android=jpush.android('content','title',None,dicts)
                    )
        elif pushType == 'msg':
            push.message = jpush.message(
                    'content',
                    u"jpush_type",
                    None,
                    u'extras'
                )
        push.options = {"time_to_live":86400, "sendno":9527, "apns_production":False}
        push.platform = jpush.all_
        push.send()
    except Exception,e:
        response_data = {}
        response_data['Exception'] = str(Exception)
        response_data['Error'] = str(e)
        return response_data
    """
    response_data = {}
    response_data['flag'] = 'ok' 
    return response_data

def TestAjax(request):
    if request.method == 'POST':
        a  = request.POST.get('a', None)
        b  = request.POST.get('b', None)
    else:
        a  = request.GET.get('a', None)
        b  = request.GET.get('b', None)
    response_data = {}
    response_data['value1'] = a 
    response_data['value2'] = b  
    return response_data