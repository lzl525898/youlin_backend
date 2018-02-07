import os
from celery import Celery
# import json
import jpush as jpush
# from django.http import HttpResponse
from push.views import createPushRecord,readIni
from core.yl_celery import youlinapp
from core.settings import PUSH_STATUS

@youlinapp.task
def CeleryBeatScheduleWithNews():
    from users.views import GetBtsoupnews
#     from web.models import Subscription
#     subScriptQuerySet = Subscription.objects.filter(s_type=0)
#     subSize = subScriptQuerySet.count()
#     for index in range(0,subSize,1):
#         GetBtsoupnews(long(subScriptQuerySet[index].community.community_id))
    GetBtsoupnews(0)
    response_data = {}
    response_data['flag'] = 'ok'
    return response_data

@youlinapp.task
def AsyncForcedReturn():
    config = readIni()
    ListApkInfo = []
    from core.settings import NEW_VERSION_URL
    from web.models import APK
    QuerySet = APK.objects.filter().order_by('-v_id')[:1]
    apkObj = QuerySet[0]
    valCode  = apkObj.v_name
    valSize  = str(apkObj.v_size) + 'MB'
    valURL   = NEW_VERSION_URL
    valForce = apkObj.v_force
    function = apkObj.v_function
    bug      = apkObj.v_bug
    dicts = {}
    dicts.setdefault('fun',function)
    dicts.setdefault('bug',bug)
    ListApkInfo.append(dicts)
    response_data = {}
    response_data['flag']    = 'ok'
    response_data['vcode']   = valCode
    response_data['size']    = valSize
    response_data['url']     = valURL
    response_data['srv_url'] = 'none'
    response_data['force']   = valForce
    response_data['detail']  = ListApkInfo
    pushContent = response_data
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    tagSuffixWithTopic = config.get('topic', "tagSuffix")
    tagSuffixWithReport = config.get('report', "tagSuffix")
    tagSuffixWithProperty = config.get('property', "tagSuffix")
    _jpush = jpush.JPush(apiKey,secretKey)
    from addrinfo.models import Community
    commQuerySet = Community.objects.all()
    for i in range(0,commQuerySet.count(),1):
        commId = commQuerySet[i].getCommunityId()
        tagNormalName = tagSuffixWithTopic + str(commId)
        tagAdminName = tagSuffixWithReport+str(commId)
        tagPropertyName = tagSuffixWithProperty+str(commId)
        push = _jpush.create_push()
        push.audience = jpush.all_
        push.audience = jpush.audience(
                    jpush.tag(tagNormalName,tagAdminName,tagPropertyName),
                )
        push.message = jpush.message(
                    pushContent,
                    u"push_force_return",
                    None,
                    None
                )
        push.options = {"time_to_live":0, "sendno":9527, "apns_production":PUSH_STATUS}
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
def AsyncUpdatePasswd(userId,imei):
    config = readIni()
    pushContent = imei
    alias = config.get("SDK", "youlin")
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    currentAlias = alias + str(userId)
    _jpush = jpush.JPush(apiKey,secretKey) 

    
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
        jpush.alias(currentAlias),
    )
    push.message = jpush.message(
                pushContent,
                u"push_new_passwd",
                None,
                None
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()

@youlinapp.task
def AsyncAuditFamily(apiKey, secretKey, alias, login_account, customContent, pushContent, pushTitle):    
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
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
                jpush.alias(currentAlias),
            )
#     iosPushExtra = {}
#     iosPushExtra['title'] = message
#     iosPushExtra['extra'] = pushExtra
    push.notification = jpush.notification(
                ios=jpush.ios(alert=pushContent.encode('utf-8'), badge="+1", extras=pushExtra),
                android=jpush.android(pushContent,pushTitle,None,pushExtra)
            )
    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()

@youlinapp.task
def AsyncAddFamily(apiKey, secretKey, alias, login_account, customContent, pushContent, pushTitle):
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
def TimingTaskWithInvStatus(invTime,userId):
    from users.models import Invitation
    invObj = Invitation.objects.get(inv_time=long(invTime),user_id=long(userId))
    invStatus = invObj.inv_status
    if int(invStatus) == 1:
        invObj.inv_status = 3
        invObj.save()

@youlinapp.task
def AsyncAddBlackList(user_id,black_user_id):
    config = readIni()
    pushContent = str(user_id).encode('utf-8') + ":" \
                 +str(black_user_id).encode('utf-8')
    alias = config.get("SDK", "youlin")
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    currentAlias = alias + str(black_user_id)
    _jpush = jpush.JPush(apiKey,secretKey) 
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
        jpush.alias(currentAlias),
    )
    push.message = jpush.message(
                pushContent,
                u"push_add_black",
                None,
                None
            )
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()
    
@youlinapp.task
def AsyncDelBlackList(user_id,black_user_id):
    from users.models import User
    userObj = User.objects.get(user_id = long(user_id))
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
    from users.views import genNeighborDict
    userInfo = genNeighborDict(user_id,user_name,user_portrait,building_num,aptnum,familyId,user_type,\
                               user_phone_number,user_profession,user_signature,user_level,user_public_status)
    config = readIni()
    pushContent = userInfo
    alias = config.get("SDK", "youlin")
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    currentAlias = alias + str(black_user_id)
    _jpush = jpush.JPush(apiKey,secretKey) 
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.audience = jpush.audience(
        jpush.alias(currentAlias),
    )
    push.message = jpush.message(
                pushContent,
                u"push_del_black",
                None,
                None
            )
    push.options = {"time_to_live":3600, "sendno":9527, "apns_production":PUSH_STATUS}
    push.platform = jpush.all_
    push.send()
    
@youlinapp.task
def AsyncSendMailToSingleAdmin(dictInfo): 
    from users.views import SendEmailToAdmin
    SendEmailToAdmin(dictInfo)
    
@youlinapp.task
def AsyncJPush(pushType,pushAlias):
    from users.views import TestJPushFunc
    TestJPushFunc(pushType,pushAlias)
    
    