# coding:utf-8
from django.http import HttpResponse
from exchange.models import *
from users.models import User
import json
import time
from core.settings import HOST_IP

def genGiftListDict(glObj):
    dicts = {}
    dicts.setdefault('gl_id',glObj.getGiftId());
    picUrl = HOST_IP + glObj.gl_pic
    dicts.setdefault('gl_pic',picUrl);
    dicts.setdefault('gl_url',glObj.gl_url);
    dicts.setdefault('gl_credit',glObj.gl_credit);
    dicts.setdefault('gl_name',glObj.gl_name);
    dicts.setdefault('gl_count',glObj.gl_count);
    dicts.setdefault('gl_start_time',glObj.gl_start_time);
    dicts.setdefault('gl_end_time',glObj.gl_end_time);
    return dicts

#获取礼品列表
def GetGiftlist(request):
    curCommGiftList = []
    response_data = {}
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
    else:
        communityId = request.GET.get('community_id', None)
    if communityId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    
    glQuerySet = Giftlist.objects.filter(gl_community_id=long(communityId),gl_end_time=None).exclude(gl_status=0).order_by('gl_credit')
    glSetCount = glQuerySet.count()
    if glSetCount == 0:
        response_data['flag'] = 'empty'
        response_data['yl_msg'] = '礼品准备中，敬请期待...'
        return response_data
    for i in range(0,glSetCount,1):
        curCommGiftList.append(genGiftListDict(glQuerySet[i]))
    if curCommGiftList:
        return curCommGiftList

def genMyGiftlistDict(ueObj):
    dicts = {}
    ueGLid = ueObj.ue_glid
    ueCount = ueObj.ue_count
    ueCommId = ueObj.community_id
    dicts.setdefault('ue_id',ueObj.getUserExchangeId());
    dicts.setdefault('ue_glid',ueGLid);
    dicts.setdefault('ue_count',ueCount);
    dicts.setdefault('ue_time',ueObj.ue_time);
    dicts.setdefault('ue_status',ueObj.ue_status);
    dicts.setdefault('user_id',ueObj.user_id);
    dicts.setdefault('community_id',ueCommId);
    try:
        glObj = Giftlist.objects.get(gl_id=long(ueGLid),gl_community_id=long(ueCommId))
    except:
        glObj = None
    if glObj is not None:
        picUrl = HOST_IP + glObj.gl_pic
        glCredit = glObj.gl_credit
        dicts.setdefault('gl_name',glObj.gl_name);
        dicts.setdefault('ue_credit',glCredit*ueCount);
        dicts.setdefault('gl_pic',picUrl);
    else:
        dicts.setdefault('gl_name',None);
        dicts.setdefault('ue_credit',None);
        dicts.setdefault('gl_pic',None);
    return dicts

#兑换礼品
def ExchangeGifts(request):
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        glId        = request.POST.get('gl_id', None)   
        count       = request.POST.get('count', None)   
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        glId        = request.GET.get('gl_id', None)   
        count       = request.GET.get('count', None)
    
    if userId is None or communityId is None or glId is None or count is None:
        response_data['flag'] = 'argv_err'
        return response_data
    try:
        glObj = Giftlist.objects.get(gl_id=long(glId),gl_community_id=long(communityId))
    except Exception,e:
        glObj = None
        response_data['Error'] = str(Exception)
        response_data['error'] = str(e)
        response_data['flag'] = 'error'
        return response_data
    if glObj is not None:
        glCredit = glObj.gl_credit
        deductCredit = int(glCredit)*int(count)
        try:
            userObj = User.objects.get(user_id=long(userId),user_community_id=long(communityId))
            userCredit = userObj.user_credit
            if long(userCredit) < long(deductCredit):
                response_data['flag'] = 'overflow'
                return response_data
            userObj.user_credit = int(userCredit) - int(deductCredit)
            userObj.save()
        except Exception,e:
            userObj = None
            response_data['Error'] = str(Exception)
            response_data['error'] = str(e)
            response_data['flag'] = 'error'
            return response_data
        curTime = long(time.time()*1000)
        ueObj = UserExchange(ue_glid=long(glId),ue_count=int(count),ue_time=curTime,ue_status=1)
        ueObj.user_id = long(userId)
        ueObj.community_id = long(communityId)
        ueObj.save()
        response_data['flag'] = 'ok'
        return response_data
    else:
        response_data['flag'] = 'error'
        return response_data
     
#删除我所兑换的礼品
def DelMyGiftFromList(request):
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        actionType  = request.POST.get('action_type', None) # 动作  删除单个1 删除全部 2
        ueId        = request.POST.get('ue_id', None) # 删除全部0  删除单个的ueId
        giltType    = request.POST.get('list_type', None) # 进行中1 已交换2
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        actionType  = request.GET.get('action_type', None) # 动作  删除单个1 删除全部 2
        ueId        = request.GET.get('ue_id', None) # 删除全部0  删除单个的ueId
        giltType    = request.GET.get('list_type', None) # 进行中1 已交换2
    if communityId is None or userId is None or actionType is None or giltType is None or ueId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if int(giltType)==1:#进行中
        if int(actionType)==1:#删除单个
            pass
        else:
            pass
    else:#已交换
        if int(actionType)==1:#删除单个
            pass
        else:
            pass
        
#获取我兑换的礼品列表
def GetMyGiftlist(request):
    myGiftList = []
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user_id', None)
        communityId = request.POST.get('community_id', None)
        actionType  = request.POST.get('action_type', None) # 动作  初始化 1 上拉 2
        giltType    = request.POST.get('list_type', None) # 进行中1 已交换2
        ueId        = request.POST.get('ue_id', None) # 初始化时传0 上拉时传最后一个ueId
    else:
        userId      = request.GET.get('user_id', None)
        communityId = request.GET.get('community_id', None)
        actionType  = request.GET.get('action_type', None) # 动作  初始化 1 上拉 2
        giltType    = request.GET.get('list_type', None) # 进行中1 已交换2
        ueId        = request.GET.get('ue_id', None) # 初始化时传0 上拉时传最后一个ueId
    if communityId is None or userId is None or actionType is None or giltType is None or ueId is None:
        response_data['flag'] = 'argv_err'
        return response_data
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if int(giltType) == 1:#获取进行中
        if int(actionType) == 1:#初始化
            ueQuerySet = UserExchange.objects.filter(user_id=long(userId),community_id=long(communityId),ue_status=1).order_by('-ue_time')[:10]
        else:#上拉 
            ueQuerySet = UserExchange.objects.filter(ue_id__lt=long(ueId),user_id=long(userId),community_id=long(communityId),ue_status=1).order_by('-ue_time')[:10]
    elif int(giltType) == 2:#获取已交换2
        if int(actionType) == 1:#初始化
            ueQuerySet = UserExchange.objects.filter(user_id=long(userId),community_id=long(communityId),ue_status=2).order_by('-ue_time')[:10]
        else:#上拉 
            ueQuerySet = UserExchange.objects.filter(ue_id__lt=long(ueId),user_id=long(userId),community_id=long(communityId),ue_status=2).order_by('-ue_time')[:10]
    ueCount = ueQuerySet.count()
    if int(ueCount) == 0:
        response_data['flag'] = 'no'
        response_data['yl_msg'] = '没有更多...'
        return response_data
    for i in range(0,ueCount,1):
        myGiftList.append(genMyGiftlistDict(ueQuerySet[i]))
    if myGiftList:
        return myGiftList


    
    
    
    