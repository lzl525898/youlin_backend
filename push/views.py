# Create your views here.
# coding:utf-8
from django.http import HttpResponse
from models import PushRecord
from users.models import User
from rest_framework.decorators import api_view
from web.models import APK
from core.settings import HOST_IP,NEW_VERSION_URL
import json
import re
import xml.dom.minidom
from sample import pushMsgToSingleDevice,pushMsgToAll,pushMsgToTag,pushBatchUniMsg


def createPushRecord(pushType,contentType,title,description,pushTime,userId,customContent,communityId,pushContent):
    pushRecord = PushRecord.objects.create(pushType = pushType,contentType = contentType,title=title,\
                                       description=description,pushTime=pushTime,user_id=userId,\
                                       customContent=customContent,isClick=1,community_id=communityId,pushContent=pushContent)
    record_id = pushRecord.getPushRecordId()
    return record_id

@api_view(['GET','POST']) 
def getPushRecord(request): 
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        userType    = request.POST.get('type', None)
        communityId = request.POST.get('community_id', None)
    else:
        userId      = request.GET.get('user_id', None)
        userType    = request.GET.get('type', None)
        communityId = request.GET.get('community_id', None)
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1002 is new gongao info
    reportReparId = 1003 # 1003 is repair gonggao info
    reportStatuId = 1004 # 1004 is repair status gongao info
    if userType is None:
        userType = 0
    if int(userType)==2:# admin
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId))
    elif int(userType)==4:# wuye
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId))
    else:#normal
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId))
    listRecords = []
    recordsSize = pushObjs.count()
    if pushObjs:
        for i in range(0,recordsSize,1):   
            userId = pushObjs[i].user_id
            RecordDict = getRecordDict(pushObjs[i])
            listRecords.append(RecordDict)
        return HttpResponse(json.dumps(listRecords), content_type="application/json")
    else:
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
      
def getRecordDict(pushObj):
    
    dicts = {}
    dicts.setdefault('contentType',pushObj.contentType)
    tempString = pushObj.customContent.decode("unicode-escape")
    customContent = re.sub(r'[\"]','\'',tempString)
    dicts.setdefault('customContent',customContent)
    dicts.setdefault('userId',pushObj.user_id)
    dicts.setdefault('selectStatus', pushObj.isClick)
    dicts.setdefault('pushTime', pushObj.pushTime)
    dicts.setdefault('pushRecordId', pushObj.getPushRecordId())
    dicts.setdefault('pushContent', pushObj.pushContent)
    return dicts


@api_view(['GET','POST']) 
def setClickStatus(request):
    userId      = request.POST.get('user_id', None)
    recordId    = request.POST.get('record_id', None)
    communityId = request.POST.get('community_id', None)
    userType    = request.POST.get('type', None)
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1001 is gonggao info
    if userType is None:
        userType = 0
    if recordId is None:# select all
        if int(userType)==2:# admin   
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId)).update(isClick=2)
        elif int(userType)==4:# wuye  
            PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId)).update(isClick=2) 
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId)).update(isClick=2)
    else: # select singal
        if int(userType)==2:# admin 
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],record_id=recordId,community_id=long(communityId)).update(isClick=2)
        elif int(userType)==4:# wuye  
            PushRecord.objects.filter(user_id__in=[long(userId),1003],record_id=recordId,community_id=long(communityId)).update(isClick=2)
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],record_id=recordId,community_id=long(communityId)).update(isClick=2)
    response_data = {}
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@api_view(['GET','POST']) 
def deleteRecords(request):
    userId      = request.POST.get('user_id', None)
    recordId    = request.POST.get('record_id', None)
    communityId = request.POST.get('community_id', None)
    userType    = request.POST.get('type', None)
    
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1002 is new gongao info
    reportReparId = 1003 # 1003 is repair gonggao info
    reportStatuId = 1004 # 1004 is repair status gongao info
    
    if userType is None:
        userType = 0
    if recordId is None:
        if int(userType)==2:
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId)).delete()
        elif 4==int(userType):
            PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId)).delete()
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId)).delete()    
    else:
        if int(userType)==2:
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],record_id=long(recordId),community_id=long(communityId)).delete()
        elif int(userType)==4:
            PushRecord.objects.filter(user_id__in=[long(userId),1003],record_id=long(recordId),community_id=long(communityId)).delete()
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],record_id=long(recordId),community_id=long(communityId)).delete()
    response_data = {}
    response_data['flag'] = 'ok'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
     
@api_view(['GET','POST'])   
def testIni(request):
    
    channel_id = '4453924844634278088' #android
    msg = '{"title":"Message from Push","description":"hello world 88888"}'
    opts = {'msg_type':1, 'expires':300} 
    pushMsgToSingleDevice(channel_id, msg, opts)
    
    """
    msg = '{"title":"Message from Push","description":"hello world 23456789"}'
    opts = {'msg_type':1, 'expires':300} 
    pushMsgToAll(msg, opts)
    """
    """
    msg = '{"title":"Message from Push","description":"hello world tag"}'
    opts = {'msg_type':1, 'expires':300} 
    tagName="111"
    pushMsgToTag(tagName,msg,1,opts)
    """
    """
    config = readIni()
    pushTitle = config.get("users", "title")
    channel_ids = ['4453924844634278088','4203132803507075402']
    msg = '{"title":"Message from Push","description":"hello world pushBatchUniMsg"}'
    opts = {'msg_type':1, 'expires':300} 
    pushBatchUniMsg(channel_ids, msg, opts)
    """
    return 'true'
    
def readIni():
    import ConfigParser
    import os
    
    config = ConfigParser.SafeConfigParser()
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    config.read(BASE_DIR+"/push/sdk.conf")
    return config
       
    
#获取推送记录
def GetPushRecord(request): 
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        userType    = request.POST.get('type', None)
        communityId = request.POST.get('community_id', None)
    else:
        userId      = request.GET.get('user_id', None)
        userType    = request.GET.get('type', None)
        communityId = request.GET.get('community_id', None)
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1002 is new gongao info
    reportReparId = 1003 # 1003 is repair gonggao info
    reportStatuId = 1004 # 1004 is repair status gongao info
    if userType is None:
        userType = 0
    if int(userType)==2:# admin
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId))
    elif int(userType)==4:# wuye
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId))
    else:#normal
        pushObjs = PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId))
    listRecords = []
    recordsSize = pushObjs.count()
    if pushObjs:
        for i in range(0,recordsSize,1):   
            userId = pushObjs[i].user_id
            RecordDict = getRecordDict(pushObjs[i])
            listRecords.append(RecordDict)
        return listRecords
    else:
        response_data['flag'] = 'no'
        return response_data
    
#删除推送记录
def DeleteRecords(request):
    userId      = request.POST.get('user_id', None)
    recordId    = request.POST.get('record_id', None)
    communityId = request.POST.get('community_id', None)
    userType    = request.POST.get('type', None)
    
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1002 is new gongao info
    reportReparId = 1003 # 1003 is repair gonggao info
    reportStatuId = 1004 # 1004 is repair status gongao info
    
    if userType is None:
        userType = 0
    if recordId is None:
        if int(userType)==2:
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId)).delete()
        elif 4==int(userType):
            PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId)).delete()
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId)).delete()    
    else:
        if int(userType)==2:
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],record_id=long(recordId),community_id=long(communityId)).delete()
        elif int(userType)==4:
            PushRecord.objects.filter(user_id__in=[long(userId),1003],record_id=long(recordId),community_id=long(communityId)).delete()
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],record_id=long(recordId),community_id=long(communityId)).delete()
    response_data = {}
    response_data['flag'] = 'ok'
    return response_data

#推送点击状态
def SetClickStatus(request):
    userId      = request.POST.get('user_id', None)
    recordId    = request.POST.get('record_id', None)
    communityId = request.POST.get('community_id', None)
    userType    = request.POST.get('type', None)
    reportAdminId = 1001 # 1001 is report info
    reportPropyId = 1002 # 1001 is gonggao info
    if userType is None:
        userType = 0
    if recordId is None:# select all
        if int(userType)==2:# admin   
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],community_id=long(communityId)).update(isClick=2)
        elif int(userType)==4:# wuye  
            PushRecord.objects.filter(user_id__in=[long(userId),1003],community_id=long(communityId)).update(isClick=2) 
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],community_id=long(communityId)).update(isClick=2)
    else: # select singal
        if int(userType)==2:# admin 
            PushRecord.objects.filter(user_id__in=[long(userId),1001,1002,1004],record_id=recordId,community_id=long(communityId)).update(isClick=2)
        elif int(userType)==4:# wuye  
            PushRecord.objects.filter(user_id__in=[long(userId),1003],record_id=recordId,community_id=long(communityId)).update(isClick=2)
        else:
            PushRecord.objects.filter(user_id__in=[long(userId),1002,1004],record_id=recordId,community_id=long(communityId)).update(isClick=2)
    response_data = {}
    response_data['flag'] = 'ok'
    return response_data

#获取当前版本号
def GetApkVersionCode(request):
#     #打开xml文档
#     dom = xml.dom.minidom.parse('/opt/youlin_backend/media/update/version.xml')
#     #得到文档元素对象
#     root        = dom.documentElement
#     vCode       = root.getElementsByTagName('version')
#     URL         = root.getElementsByTagName('url')
#     force       = root.getElementsByTagName('force')
#     URL_SRV     = root.getElementsByTagName('url_server')
#     description = root.getElementsByTagName('description')
#     valCode        = vCode[0].firstChild.data
#     valURL         = URL[0].firstChild.data
#     valSrvUrl      = URL_SRV[0].firstChild.data
#     valForce       = force[0].firstChild.data
#     valDescription = description[0].firstChild.data
    ListApkInfo = []
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
    return response_data
