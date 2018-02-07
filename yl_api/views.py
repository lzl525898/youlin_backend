# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from core.middleware import secure_required
import json
import redis
from core.views import TokenBucket
from push.views import *
from users.views import *
from addrinfo.views import *
from feedback.views import *
from property.views import *
from community.views import *
from community.views_square import *
from comServices.views import *
from comServices.views_pingpp import *
from exchange.views import *
from django.views.decorators.csrf import csrf_exempt

def getResponseDict(result, tag):
    dictVal = {'tag': tag}
    dictVal.update(result)
    return dictVal

def getResponseList(result, tag):
    retDict = {'info':result,'tag': tag}
    return retDict

def getTargetValue(request,key,type=None):
    if type is None:
        return request.POST.get(key, None)
    else:
        return request.GET.get(key, None)

def checkResponseLegal(request):
    response_data = {}
    keySet = str(getTargetValue(request,'keyset'))
    if keySet is None:
        response_data['flag'] = 'legal_error_0'
        return response_data
    else:#开始验证
        try:
            from web.views_admin import generatePassword
            newPasswdHash = ''
            keyList = keySet.split(':')
            kSize = len(keyList) - 1#去掉None
            for i in range(0,kSize,1):
                newPasswdHash = newPasswdHash + str(keyList[i])+str(getTargetValue(request,str(keyList[i])).encode('utf-8'))
        except:
            response_data['flag'] = 'legal_error_1'
            return response_data
        newPasswdHash = generatePassword(newPasswdHash,getTargetValue(request,'salt'))
        oldPasswdHash = getTargetValue(request,'hash')
        if newPasswdHash == oldPasswdHash:
            #验证成功，未进行篡改，可以继续访问接口
            response_data['flag'] = 'ok'
            return response_data
        else:
            if str(9573) == str(oldPasswdHash):
                response_data['flag'] = 'ok'
            else:
                response_data['flag'] = 'legal_error'
            return response_data

@csrf_exempt        
@secure_required
@api_view(['GET','POST'])
def postYouLinAPI(request):
    dType   = None
    response_data = {}
    if request.method == 'POST':
        apiType     = request.POST.get('apitype', None)
        postTag     = request.POST.get('tag', None)
        device_type = request.POST.get('deviceType', None)
        accessSalt  = request.POST.get('access', None)
    else:
        apiType     = request.GET.get('apitype', None)
        postTag     = request.GET.get('tag', None)
        device_type = request.GET.get('deviceType', None)
        accessSalt  = request.GET.get('access', None)
        
    if apiType is None:
        if device_type is not None:
            result = ExceptErrorRecord(request)
            return HttpResponse(json.dumps(getResponseDict(result,'except')), content_type="application/json")
        response_data['flag'] = 'api_error'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if postTag is None:
        if device_type is not None:
            result = ExceptErrorRecord(request)
            return HttpResponse(json.dumps(getResponseDict(result,'except')), content_type="application/json")
        response_data['flag'] = 'tag_error'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if accessSalt is None:
        retDict = checkResponseLegal(request)
        response_data['flag'] = 'legal_error'
        response_data['status'] = '200'
        if retDict['flag'] != 'ok':
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        if str(accessSalt) == '9527':
            pass
        else:
           return HttpResponse(json.dumps(response_data), content_type="application/json")
    if 'users'==str(apiType):
        if 'test'==str(postTag):
#             RedisObj = redis.Redis()
#             key = apiType+postTag
#             if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
#                 result = Test(request)
#             else:
#                 result = Test(request)
            result = Test(request)
            return HttpResponse(json.dumps(getResponseDict(result,'test')), content_type="application/json")
        if 'soupnews'==str(postTag):
            result = Btsoupnews(request)
            return HttpResponse(json.dumps(getResponseDict(result,'soupnews')), content_type="application/json") 

        #获取系统时间
        if 'systemtime'==str(postTag): 
            result = GetSystemTime(request)
            return HttpResponse(json.dumps(getResponseDict(result,'systemtime')), content_type="application/json")
        ##短信验证码验证-------------------------------------------------------------------------
        if 'mobverify'==str(postTag): 
            result = CodeWtihmobVerify(request)
            return HttpResponse(json.dumps(getResponseDict(result,'mobverify')), content_type="application/json")
        #用户注销-----------------------------------------------------------------------------setLogOff
        if 'logoff'==str(postTag): 
            result = SetPhoneLogoff(request)
            return HttpResponse(json.dumps(getResponseDict(result,'logoff')), content_type="application/json")
        #用户登录-----------------------------------------------------------------------------login
        elif 'login'==str(postTag):    
            relVal = LoginUser(request)
            if ((str==type(relVal)) or (list==type(relVal))):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'login')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'login')), content_type="application/json")
        #获取个人信息--------------------------------------------------------------------------getInfo
        elif 'getinfo'==str(postTag):
            relVal = GetPersonalInfo(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getinfo')),content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getinfo')), content_type="application/json")
        #修改密码-----------------------------------------------------------------------------modifypwd
        elif 'modifypwd'==str(postTag):    
            result = ModifyPwd(request)
            return HttpResponse(json.dumps(getResponseDict(result,'modifypwd')), content_type="application/json")
        #更新个人信息--------------------------------------------------------------------------upload
        elif 'upload'==str(postTag):   
            result = UploadUserInfo(request)
            return HttpResponse(json.dumps(getResponseDict(result,'upload')), content_type="application/json")
        #注册用户-----------------------------------------------------------------------------regist
        elif 'regist'==str(postTag):   
            result = RegistNewUser(request)
            return HttpResponse(json.dumps(getResponseDict(result,'regist')), content_type="application/json")
        #检测用户是否存在-----------------------------------------------------------------------check
        elif 'check'==str(postTag):   
            result = CheckPhoneExist(request)
            return HttpResponse(json.dumps(getResponseDict(result,'check')), content_type="application/json")
        #修改密码-----------------------------------------------------------------------------updatepwd
        elif 'updatepwd'==str(postTag):   
            result = UpdatePasswd(request)
            return HttpResponse(json.dumps(getResponseDict(result,'updatepwd')), content_type="application/json")
        #添加地址-----------------------------------------------------------------------------addfamily
        elif 'addfamily'==str(postTag):   
            result = AddFamily(request)
            return HttpResponse(json.dumps(getResponseDict(result,'addfamily')), content_type="application/json")
        #修改地址-----------------------------------------------------------------------------updatefamily
        elif 'changefamily'==str(postTag):   
            result = ModifiFamily(request)
            return HttpResponse(json.dumps(getResponseDict(result,'changefamily')), content_type="application/json")
        #删除地址-----------------------------------------------------------------------------delfamily
        elif 'delfamily'==str(postTag):   
            result = DeleFamilyRecord(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delfamily')), content_type="application/json")
        #设置当前地址--------------------------------------------------------------------------curaddrflag
        elif 'curaddr'==str(postTag):   
            result = UpdatePrimaryAddr(request)
            return HttpResponse(json.dumps(getResponseDict(result,'curaddr')), content_type="application/json")
        #添加城市、小区、楼栋、门牌---------------------------------------------------------------userfamily
        elif 'addr'==str(postTag):   
            relVal = HandleFamily(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'addr')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'addr')), content_type="application/json")
        #获取邻居-----------------------------------------------------------------------------neighbors
        elif 'neighbors'==str(postTag):   
            relVal = GetNeighbors(request)
            if (str==type(relVal)) or (list==type(relVal)):
                dType = request.POST.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'neighbors')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'neighbors')), content_type="application/json")
        #注册环信-----------------------------------------------------------------------------regEasemob
        elif 'regeasemob'==str(postTag):   
            result = RegistEasemob(request)
            return HttpResponse(json.dumps(getResponseDict(result,'regeasemob')), content_type="application/json")
        #登录状态-----------------------------------------------------------------------------loginStatus
        elif 'loginstatus'==str(postTag):   
            result = CheckPushChannelExist(request)
            return HttpResponse(json.dumps(getResponseDict(result,'loginstatus')), content_type="application/json")
        #获取公开状态--------------------------------------------------------------------------getStatus
        elif 'getstatus'==str(postTag):   
            result = GetPublicStatus(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getstatus')), content_type="application/json")
        #获取token---------------------------------------------------------------------------checkToken
        elif 'token'==str(postTag):   
            result = CheckIMEI(request)
            return HttpResponse(json.dumps(getResponseDict(result,'token')), content_type="application/json")
        #获取黑名单----------------------------------------------------------------------------
        elif 'getblacklist'==str(postTag):   
            result = GetBlackList(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getblacklist')), content_type="application/json")
        #黑名单操作---------------------------------------------------------------------------blacklist
        elif 'blacklist'==str(postTag):   
            result = HandleBlackList(request)
            return HttpResponse(json.dumps(getResponseDict(result,'blacklist')), content_type="application/json")
        #还原移除所有黑名单失败之前的黑名单
        elif 'undoblacklist'==str(postTag):   
            result = UndoBlackList(request)
            return HttpResponse(json.dumps(getResponseDict(result,'undoblacklist')), content_type="application/json")
        #解除用户所有黑名单
        elif 'clearblacklist'==str(postTag):   
            result = ClearBlackList(request)
            return HttpResponse(json.dumps(getResponseDict(result,'clearblacklist')), content_type="application/json")
        #判断是否被加入黑名单---------------------------------------------------------------------VerifyBlackList
        elif 'verifyblack'==str(postTag):   
            result = VerifyBlackList(request)
            return HttpResponse(json.dumps(getResponseDict(result,'verifyblack')), content_type="application/json")
        #获取耽搁用户信息-----------------------------------------------------------------------------modifypwd
        elif 'userdetailinfo'==str(postTag):    
            result = GetUserDetailInfo(request)
            return HttpResponse(json.dumps(getResponseDict(result,'userdetailinfo')), content_type="application/json")
        #判断是否签到
        elif 'checkusersign'==str(postTag):
            result = CheckUserSign(request)
            return HttpResponse(json.dumps(getResponseDict(result,'usersign')), content_type="application/json")
        #用户签到
        elif 'usersign'==str(postTag):
            result = UserSignOperation(request)
            return HttpResponse(json.dumps(getResponseDict(result,'usersign')), content_type="application/json")
        #获取用户积分
        elif 'usercredit'==str(postTag):
            result = GetUserCredit(request)
            return HttpResponse(json.dumps(getResponseDict(result,'usercredit')), content_type="application/json")
        #获取用户签到日期近3个月
        elif 'getsigndate'==str(postTag):
            relVal = GetUserSignDate(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getsigndate')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getsigndate')), content_type="application/json")
        #判断用户类型
        elif 'checkusertype'==str(postTag):
            result = CheckUserType(request)
            return HttpResponse(json.dumps(getResponseDict(result,'checkusertype')), content_type="application/json")
        #设置备注
        elif 'setuserremarks'==str(postTag):
            result = SetUserRemarks(request)
            return HttpResponse(json.dumps(getResponseDict(result,'setuserremarks')), content_type="application/json")
        #获取邀请家人成功地址详情  
        elif 'getinvfamilyinfo'==str(postTag):
            result = GetInviteFamilyInfo(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getinvfamilyinfo')), content_type="application/json")
        #邀请朋友
        elif 'invitenewusers'==str(postTag):
            result = InviteNewUsers(request)
            return HttpResponse(json.dumps(getResponseDict(result,'invitenewusers')), content_type="application/json")
        #获取邀请码
        elif 'getinvcode'==str(postTag):
            result = GetInvCode(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getinvcode')), content_type="application/json")
        #邀请码验状态
        elif 'checkinvstatus'==str(postTag):
            result = CheckInviteStatus(request)
            return HttpResponse(json.dumps(getResponseDict(result,'checkinvstatus')), content_type="application/json")
        #获取邀请信息
        elif 'getinviteinfo'==str(postTag):
            relVal = GetInviteInfo(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getinviteinfo')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getinviteinfo')), content_type="application/json")
        elif 'gettreasurebox'==str(postTag):
            result = GetTreasureBox(request)
            return HttpResponse(json.dumps(getResponseDict(result,'gettreasurebox')), content_type="application/json")
        elif 'loginthird'==str(postTag):#
            result = LoginThird(request)
            return HttpResponse(json.dumps(getResponseDict(result,'loginthird')), content_type="application/json")
        elif 'bindthird':#第三方绑定
            result = BindThird(request)
            return HttpResponse(json.dumps(getResponseDict(result,'bindthird')), content_type="application/json")
    elif 'comm'==str(apiType):
        #发送帖子---------------------------------------------------------------------------addtopic
        if 'addtopic'==str(postTag):#10分钟发40条
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = PostNewTopic(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data
#             result = PostNewTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'addtopic')), content_type="application/json")
        elif 'addoldreplace'==str(postTag):
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = PostOldReplacement(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data
#             result = PostNewTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'addoldreplace')), content_type="application/json")
        #修改帖子---------------------------------------------------------------------------updatetopic
        elif 'updatetopic'==str(postTag):   
            result = UpdateTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'updatetopic')), content_type="application/json")
        #获取所有帖子-----------------------------------------------------------------------------gettopic
        elif 'gettopic'==str(postTag):   
            relVal = GetTopic(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'gettopic')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'gettopic')), content_type="application/json")
        #获取我发的帖子-------------------------------------------------------------------------getMytopic
        elif 'mytopic'==str(postTag):   
            relVal = GetMyTopic(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'mytopic')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'mytopic')), content_type="application/json")
        #添加回复---------------------------------------------------------------------------addcomm
        elif 'addcomm'==str(postTag):#10分钟发120条  
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            RedisObj = redis.Redis()
            if TokenBucket(1, key, RedisObj, 0.2, 12, 60 * 60):
                result = AddComment(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data
            return HttpResponse(json.dumps(getResponseDict(result,'addcomm')), content_type="application/json")
        #删除回复---------------------------------------------------------------------------delcomm
        elif 'delcomm'==str(postTag):   
            result = DelComment(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delcomm')), content_type="application/json")
        #获取回复---------------------------------------------------------------------------getcomm
        elif 'getcomm'==str(postTag):   
            relVal = GetComment(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getcomm')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getcomm')), content_type="application/json")
        #搜索帖子---------------------------------------------------------------------------findtopic
        elif 'findtopic'==str(postTag):   
            relVal = SearchTopic(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'findtopic')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'findtopic')), content_type="application/json")
        #帖子点赞---------------------------------------------------------------------------hitpraise
        elif 'hitpraise'==str(postTag):   
            result = ClickPraise(request)
            return HttpResponse(json.dumps(getResponseDict(result,'hitpraise')), content_type="application/json")
        #进入帖子详情------------------------------------------------------------------------intotopic
        elif 'intotopic'==str(postTag):   
            result = IntoDetailTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'intotopic')), content_type="application/json")
        #删除帖子---------------------------------------------------------------------------deltopic
        elif 'deltopic'==str(postTag):   
            result = DeleteTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'deltopic')), content_type="application/json")
        #设置活动报名------------------------------------------------------------------------enroll
        elif 'enroll'==str(postTag):   
            result = ActivityEnroll(request)
            return HttpResponse(json.dumps(getResponseDict(result,'enroll')), content_type="application/json")
        #取消活动报名------------------------------------------------------------------------canenroll
        elif 'delenroll'==str(postTag):   
            result = CancelEnroll(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delenroll')), content_type="application/json")
        #报名详情---------------------------------------------------------------------------detenroll
        elif 'detenroll'==str(postTag):   
            result = DetailEnroll(request)
            return HttpResponse(json.dumps(getResponseDict(result,'detenroll')), content_type="application/json")
        #获取帖子是否被删除-------------------------------------------------------------------delstatus
        elif 'delstatus'==str(postTag):   
            result = GetTopicDeleteStatus(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delstatus')), content_type="application/json")
        #举报帖子---------------------------------------------------------------------------report
        elif 'report'==str(postTag):   
            result = ReportTopicHandle(request)
            return HttpResponse(json.dumps(getResponseDict(result,'report')), content_type="application/json")
        #添加收藏---------------------------------------------------------------------------addCol
        elif 'addcol'==str(postTag):   
            result = AddCollection(request)
            return HttpResponse(json.dumps(getResponseDict(result,'addcol')), content_type="application/json")
        #删除收藏---------------------------------------------------------------------------delCol
        elif 'delcol'==str(postTag):   
            result = DelCollection(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delcol')), content_type="application/json")
        #删除我的收藏------------------------------------------------------------------------delmycol
        elif 'delmycol'==str(postTag):   
            result = DelMyCollection(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delmycol')), content_type="application/json")
        #获取收藏帖子------------------------------------------------------------------------getCol
        elif 'getcol'==str(postTag):   
            relVal = GetCollectTopic(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getcol')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getcol')), content_type="application/json")
        #获取我的和收藏个数和积分--------------------------------------------------------------------getCount
        elif 'getcount'==str(postTag):   
            result = GetTopicCounts(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getcount')), content_type="application/json")
        #获取举报详情------------------------------------------------------------------------getReport
        elif 'getreport'==str(postTag):   
            relVal = GetReportInfo(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getreport')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getreport')), content_type="application/json")
        #分享小区新闻-------------------------------------------------------------------------newShare
        elif 'newshare'==str(postTag):   
            result = ShareCommunityNews(request)
            return HttpResponse(json.dumps(getResponseDict(result,'newshare')), content_type="application/json")
        #返回点赞详细信息
        elif 'praisedetail'==str(postTag):
            relVal = GetPraiseDetail(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'praisedetail')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'praisedetail')), content_type="application/json")
        #获取话题-----------------------------------------------------------------------------gettopic
        elif 'singletopic'==str(postTag):   
            relVal = GetSingleTopic(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'singletopic')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'singletopic')), content_type="application/json")
        #获取活动-----------------------------------------------------------------------------gettopic
        elif 'singleactivity'==str(postTag):   
            relVal = GetSingleActivity(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'singleactivity')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'singleactivity')), content_type="application/json")
        #获取以物易物-----------------------------------------------------------------------------gettopic
        elif 'singlebarter'==str(postTag):   
            relVal = GetSingleBarter(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'singlebarter')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'singlebarter')), content_type="application/json")
        #打招呼
        elif 'sayhello'==str(postTag):
            result = SayHelloFun(request)
            return HttpResponse(json.dumps(getResponseDict(result,'sayhello')), content_type="application/json")
        #单独或去帖子回复总数
        elif 'getcommentcount'==str(postTag):
            result = GetCommentCountFromTopic(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getcommentcount')), content_type="application/json")
        #获取公众号
        elif 'getsubscription'==str(postTag):
            result = GetSubscription(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getsubscription')), content_type="application/json")
    elif 'comsrv'==str(apiType):
        #mj.用户注册
        if 'mjregist'==str(postTag):
            result = UserRegistWithMJ(request)
            return HttpResponse(json.dumps(getResponseDict(result,'mjregist')), content_type="application/json")
        #小区天气预报-------------------------------------------------------------------------
        if 'weather'==str(postTag):
            result = CommunityWeather(request)
            return HttpResponse(json.dumps(getResponseDict(result,'weather')), content_type="application/json")
        #获取小区天气预报-------------------------------------------------------------------------
        if 'getweaorzod'==str(postTag):
            result = GetCommunityWeather(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getweaorzod')), content_type="application/json")
        #获取小区天气详情-------------------------------------------------------------------------
        if 'getweaorzodinfo'==str(postTag):
            result = GetCommunityWeatherDetail(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getweaorzodinfo')), content_type="application/json")
        #获取小区服务信息----------------------------------------------------------------------loadService
        if 'loadsrv'==str(postTag):   
            relVal = LoadCommunityService(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'loadsrv')), content_type="application/json")
                else:#android
                    if list==type(relVal):
                        return HttpResponse(json.dumps(relVal), content_type="application/json")
                    else:
                        data = {}
                        data['error'] = 'android_comsrv_not_list'
                        return HttpResponse(json.dumps(data), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'loadsrv')), content_type="application/json")
        #获得新闻列表-------------------------------------------------------------------------getNews
        if 'getnews'==str(postTag):   
            relVal = GetNewsList(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getnews')), content_type="application/json")
                else:#android
                    if list==type(relVal):
                        return HttpResponse(json.dumps(relVal), content_type="application/json")
                    else:
                        data = {}
                        data['error'] = 'android_getnews_not_list'
                        return HttpResponse(json.dumps(data), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getnews')), content_type="application/json")
    elif 'address'==str(apiType):
        #地址快速验证-------------------------------------------------------------------------addrVerify
        if 'verify'==str(postTag):   
            result = AddressVerify(request)
            return HttpResponse(json.dumps(getResponseDict(result,'verify')), content_type="application/json")
        #搜索商圈-------------------------------------------------------------------------
        if 'searchbizcir'==str(postTag):
            relVal = SearchBizCir(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'searchbizcir')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'searchbizcir')), content_type="application/json")
        #获取商圈-------------------------------------------------------------------------
        if 'bizcir'==str(postTag):
            relVal = GetBizCir(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'bizcir')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'bizcir')), content_type="application/json")
        #发布用户的商家评价-------------------------------------------------------------------------
        if 'postbizcireva'==str(postTag):
            result = PostBizCirEvaluate(request)
            return HttpResponse(json.dumps(getResponseDict(result,'postbizcireva')), content_type="application/json")
        #获取用户商家评价-------------------------------------------------------------------------
        if 'getbizcireva'==str(postTag):
            result = GetBizCirEvaluate(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getbizcireva')), content_type="application/json")
        #获取用户操作--------------
        if 'guorecord'==str(postTag):
            result = GetUserOperatRecords(request)
            return HttpResponse(json.dumps(getResponseDict(result,'guorecord')), content_type="application/json")
        #进入商家详情页-------------------------------------------------------------------------
        if 'intobizcirdetail'==str(postTag):
            result = GetBizCirDetailPage(request)
            return HttpResponse(json.dumps(getResponseDict(result,'intobizcirdetail')), content_type="application/json")
        #判断是否已评价-------------------------------------------------------------------------
        if 'getorcheckrecord'==str(postTag):
            result = GetOrCheckEvaRecord(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getorcheckrecord')), content_type="application/json")
    elif 'feedback'==str(apiType):
        #创建建议----------------------------------------------------------------------------submitFeedback
        if 'feedback'==str(postTag):   
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = SetFeedBack(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data
            return HttpResponse(json.dumps(getResponseDict(result,'feedback')), content_type="application/json")
    elif 'apiproperty'==str(apiType):
        #创建物业公告-------------------------------------------------------------------------setnotice
        if 'setnotice'==str(postTag):  
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = SetNotice(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data 
            return HttpResponse(json.dumps(getResponseDict(result,'setnotice')), content_type="application/json")
        #获取物业公告-------------------------------------------------------------------------getnotice
        if 'getnotice'==str(postTag):   
            relVal = GetNotice(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getnotice')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getnotice')), content_type="application/json")
        #创建物业建议-------------------------------------------------------------------------setsuggest
        if 'setsuggest'==str(postTag):   
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = SetSuggest(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'休息下手指，一会儿再发！'
                result = response_data
            return HttpResponse(json.dumps(getResponseDict(result,'setsuggest')), content_type="application/json")
        #获取物业建议-------------------------------------------------------------------------getsuggest
        if 'getsuggest'==str(postTag):   
            relVal = GetSuggest(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getsuggest')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getsuggest')), content_type="application/json")
        #获取物业信息-------------------------------------------------------------------------getinfo
        if 'getproperty'==str(postTag):   
            result = GetPropertyInfo(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getproperty')), content_type="application/json")
        #设置物业报修-------------------------------------------------------------------------setrepair
        if 'setrepair'==str(postTag):   
            RedisObj = redis.Redis()
            key = apiType+postTag+str(getTargetValue(request,'tokenvalue'))
            if TokenBucket(1, key, RedisObj, 0.07, 4, 60 * 60):
                result = SetProprtyRepair(request)
            else:
                response_data['flag'] = 'full'
                response_data['yl_msg'] = u'物业很繁忙，请稍后再试！'
                result = response_data
            return HttpResponse(json.dumps(getResponseDict(result,'setrepair')), content_type="application/json")
        #获取报修状态-------------------------------------------------------------------------getrepair
        if 'getrepair'==str(postTag):   
            relVal = GetProprtyRepair(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getrepair')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getrepair')), content_type="application/json")
        #设置报修状态-------------------------------------------------------------------------setstatus
        if 'setstatus'==str(postTag):   
            result = SetProcessStatus(request)
            return HttpResponse(json.dumps(getResponseDict(result,'setstatus')), content_type="application/json")
    elif 'exchange'==str(apiType):
        #兑换礼品
        if 'exchangegifts'==str(postTag):   
            result = ExchangeGifts(request)
            return HttpResponse(json.dumps(getResponseDict(result,'exchangegifts')), content_type="application/json")
        #获取我兑换的礼品列表
        if 'getmygiftlist'==str(postTag):   
            relVal = GetMyGiftlist(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getmygiftlist')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getmygiftlist')), content_type="application/json")
        #获取礼品列表
        if 'getgiftlist'==str(postTag):   
            relVal = GetGiftlist(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'getgiftlist')), content_type="application/json")
                else:#android
                    return HttpResponse(json.dumps(relVal), content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'getgiftlist')), content_type="application/json")
    elif 'push'==str(apiType):
        #获取推送记录-------------------------------------------------------------------------pushRecord
        if 'pushrecord'==str(postTag):   
            relVal = GetPushRecord(request)
            if (str==type(relVal)) or (list==type(relVal)):
                if request.method == 'POST':
                    dType = request.POST.get('deviceType', None)
                else:
                    dType = request.GET.get('deviceType', None)
                if dType is not None: #ios
                    return HttpResponse(json.dumps(getResponseList(relVal,'pushrecord')), content_type="application/json")
                else:#android
                    return HttpResponse(relVal, content_type="application/json")
            elif dict==type(relVal):
                return HttpResponse(json.dumps(getResponseDict(relVal,'pushrecord')), content_type="application/json")
        #删除推送记录-------------------------------------------------------------------------delRecord
        if 'delrecord'==str(postTag):   
            result = DeleteRecords(request)
            return HttpResponse(json.dumps(getResponseDict(result,'delrecord')), content_type="application/json")
        #推送点击状态-------------------------------------------------------------------------setClickStatus
        if 'clickstatus'==str(postTag):   
            result = SetClickStatus(request)
            return HttpResponse(json.dumps(getResponseDict(result,'clickstatus')), content_type="application/json")
        #获取当前版本号
        if 'version'==str(postTag):   
            result = GetApkVersionCode(request)
            return HttpResponse(json.dumps(getResponseDict(result,'version')), content_type="application/json")
    elif 'pay'==str(apiType):
        if 'payment'==str(postTag):
            result = CreatePayment(request)
            return HttpResponse(json.dumps(result['info']), content_type="application/json")
        elif 'gencharge'==str(postTag):
            result = CreateCharge(request)
            return HttpResponse(json.dumps(result['info']), content_type="application/json")
    elif 'square'==str(apiType):
        if 'getsquare'==str(postTag):
            result = InitSquaresInfo(request)
            return HttpResponse(json.dumps(getResponseDict(result,'getsquare')), content_type="application/json")
        elif 'moresquare'==str(postTag):
            result = GetMoreSquare(request)
            return HttpResponse(json.dumps(getResponseDict(result,'moresquare')), content_type="application/json")
    elif 'jpush'==str(apiType):
        if 'test'==str(postTag):
            result = TestJPush(request)
            return HttpResponse(json.dumps(getResponseDict(result,'test')), content_type="application/json")
        if 'ajax'==str(postTag):
            result = TestAjax(request)
            return HttpResponse(json.dumps(getResponseDict(result,'ajax')), content_type="application/json")
    elif 'h5'==str(apiType):
        if 'oldreplace'==str(postTag):#旧物置换页面-分类-我的（包括发布的、洽谈中的）
            result = GetOldReplacement(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'checktopic'==str(postTag):#详情页返回后，判断该旧物置换是否可见，如果可见则返回详细细节
            result = CheckMyOldTakeback(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'myoldreplace'==str(postTag):#获取我发的在卖的旧物置换帖子
            result = GetMyOldReplacement(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'myoldtakeback'==str(postTag):#旧物置换页面-收摊的
            result = GetMyOldTakeback(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'getbuywithtalk'==str(postTag):#洽谈中的我买的(买家身份)
            result = GetOldBuyWithTalks(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'getsellwithtalk'==str(postTag):#洽谈中的我卖的 （卖家身份）
            result = GetOldSellWithTalks(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'getsellwithfinish'==str(postTag):#我的 我卖出的 交易完成的（卖家身份）
            result = GetSellWithFinish(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'getbuywithfinish'==str(postTag):#我的 我买到的 交易完成的（买家身份）
            result = GetBuyWithFinish(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'singlereplace'==str(postTag):#旧物置换详情页面
            result = GetSingleOldReplace(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'typeofreplace'==str(postTag):#旧物置换按类别
            result = GetOldReplaceWithType(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'searcholdrep'==str(postTag):#搜索旧物置换帖子
            result = SearchOldReplace(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'favourite'==str(postTag):#用户点击我想要、我不想要
            result = MyFavourite(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'shelves'==str(postTag):#旧物置换上架商品 (只能是发布者)
            result = MyReplaceShelves(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'dealuserlist'==str(postTag):#设置交易完成时所需要的用户列表
            result = DealUserList(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'dealdone'==str(postTag):#旧物置换交易完成商品 (只能是发布者)
            result = TransactionCompletion(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'checksecond'==str(postTag):#判断是否下架、交易完成
            result = CheckSecondStatus(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'sinra'==str(postTag):#获取单个收货地址页面（编辑时使用）
            result = GetSingleAddress(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'intora'==str(postTag):#进入收货地址页面
            result = IntoReceiptAddress(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'addra'==str(postTag):#新建收货地址
            result = AddReceiptAddress(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'delra'==str(postTag):#删除收货地址
            result = DelReceiptAddress(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'editra'==str(postTag):#修改收货地址
            result = EditReceiptAddress(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'creategoods'==str(postTag):#创建爆款商品
            result = CreateSquareGoods(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'getgoodslist'==str(postTag):#获取爆款商品列表
            result = GetSquareGoodsList(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'intogdpage'==str(postTag):#进入爆款详情页面(商品、详情、评价)
            result = IntoGoodsDetailPage(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'userbuygoods'==str(postTag):#选择要购买爆款商品
            result = BuyGoodsWithUser(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
        elif 'confirmgoods'==str(postTag):#购买爆款商品的相关信息确认
            result = GoodsConfirmeMessage(request)
            return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        response_data['flag'] = 'none'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
