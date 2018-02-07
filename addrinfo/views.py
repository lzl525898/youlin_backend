# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from users.models import User
from users.models import FamilyRecord
from addrinfo.models import AddressDetails
from addrinfo.models import City,Community,BuildNum,AptNum,Block
from addrinfo.models import BusinessCircle,BizCirEvaluate,BizCirMediaFiles,BizCirFacility,UserEvaluatiorRecord
from push.models import PushRecord
from django.core import serializers
from django.conf import settings
import sys
import re
import os
import json
import time
import random
import jpush as jpush
from community.models import Topic
from push.views import createPushRecord,readIni
from addrinfo.tasks import *

def getFamilyRecrodDict(city_id,block_id,community_id,building_num_id,apt_num_id,ne_status,entity_type,family_id):
    dicts = {}
    dicts.setdefault('city_id',city_id)
    dicts.setdefault('block_id',block_id)
    dicts.setdefault('community_id',community_id)
    dicts.setdefault('building_num_id',building_num_id)
    dicts.setdefault('apt_num_id',apt_num_id)
    dicts.setdefault('ne_status',ne_status)
    dicts.setdefault('entity_type',entity_type)
    dicts.setdefault('family_id',family_id)
    return dicts

@api_view(['GET','POST'])
def addressVerify(request):
    recordFamilyIdList = []
    responseValue = []
    addrDetailObj = None
    familyRecord = None
    response_data = {}
    if request.method == 'POST':
        userId         = request.POST.get('user_id',None)
        familyId       = request.POST.get('family_id',None)
        familyRecordId = request.POST.get('record_id',None)
        addrDetailMask = request.POST.get('mask_code',None)
    else:
        userId         = request.GET.get('user_id',None)
        familyId       = request.GET.get('family_id',None)
        familyRecordId = request.GET.get('record_id',None)
        addrDetailMask = request.GET.get('mask_code',None)
    if familyId is None:#证明用户手动填写地址，需要联系管理员审核
        response_data['flag'] = 'failed'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    try:
        addrDetailObj = AddressDetails.objects.get(address_mark=addrDetailMask)
    except:
        response_data['flag'] = 'no_ad'  #验证码或二维码错误
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    try:
        familyRecord = FamilyRecord.objects.get(fr_id=long(familyRecordId))
        familyIdFromFR = familyRecord.family_id
        if long(familyId)!=long(familyIdFromFR):
            response_data['flag'] = 'no_fr'  #地址错误错误
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except:
        response_data['flag'] = 'no_fr'  #地址错误错误
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    #获取当前用户已经审核通过的地址
    try:            
        recordFamilys = FamilyRecord.objects.filter(user_id=userId,entity_type=1)
    except:
        response_data['flag'] = 'no_user' # 没有查到指定用户的
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    if recordFamilys is not None:
        size = recordFamilys.count()
        for i in range(0,size,1):
            recordFamilyIdList.append(recordFamilys[i].family_id)
        if str(familyId) in recordFamilyIdList:#表明已经此地址已经审核通过
            recordFamilyIdList = []
            response_data['flag'] = 'audited' #告知用户无法重复审核
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        recordFamilyIdList = []
    
    addrfmyId = addrDetailObj.getAddrDetailId()
    if str(addrfmyId) != str(familyId):
        response_data['flag'] = 'match_err' #告知用户无法重复审核
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        #证明用户没有审核通过的地址
        pass
    #修改当前验证地址
    family_id = None
    try:
        family_id = addrDetailObj.getAddrDetailId()
        familyRecord.family_id = family_id
    except:    
        response_data['flag'] = 'error'  
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    city_id      = addrDetailObj.city_id
    block_id     = addrDetailObj.block_id
    community_id = addrDetailObj.community_id
    building_id  = addrDetailObj.building_id
    apt_id       = addrDetailObj.apt_id
    familyRecord.family_city_id         = city_id
    familyRecord.family_block_id        = block_id
    familyRecord.family_community_id    = community_id
    familyRecord.family_building_num_id = building_id
    familyRecord.family_apt_num_id      = apt_id
    familyRecord.ne_status              = 0
    familyRecord.entity_type            = 1
    familyRecord.save()
    
    city_name = familyRecord.family_city
    community_name = familyRecord.family_community
    family_address = familyRecord.family_address
    user_nick = User.objects.get(user_id=long(userId)).user_nick
    setWelcomeTopic(city_name,city_id,community_name,community_id,family_address,family_id,user_nick,userId)
    
    responseValue.append(getFamilyRecrodDict(city_id,block_id,community_id,
                                             building_id,apt_id,0,1,family_id))
    response_data['flag']    = 'ok'
    response_data['addr_flag'] = 'ok'
    response_data['context'] = responseValue
    return HttpResponse(json.dumps(response_data), content_type="application/json")

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
                                       cache_key=user_id,collect_status=0)
    topicId = topicObj.getTopicId() 
    
    AsyncSetWelcome.delay(topicId, sender_id, sender_community_id)
    
def getCacheKey():
    cacheKey = int(time.time()) + int(random.randint(100,999))
    return cacheKey  

#地址快速验证
def AddressVerify(request):
    recordFamilyIdList = []
    responseValue = []
    addrDetailObj = None
    familyRecord = None
    response_data = {}
    if request.method == 'POST':
        userId         = request.POST.get('user_id',None)
        familyId       = request.POST.get('family_id',None)
        familyRecordId = request.POST.get('record_id',None)
        addrDetailMask = request.POST.get('mask_code',None)
        addrCache      = request.POST.get('addr_cache', None)# addr verfty
    else:
        userId         = request.GET.get('user_id',None)
        familyId       = request.GET.get('family_id',None)
        familyRecordId = request.GET.get('record_id',None)
        addrDetailMask = request.GET.get('mask_code',None)
    uObj = None
    try:
        uObj = User.objects.get(user_id=long(userId),addr_handle_cache=int(addrCache))
    except:
        response_data['flag']      = 'no'
        response_data['addr_flag'] = 'no'
        response_data['yl_msg']    = u'验证地址失败'
        return response_data
    response_data['addr_flag'] = 'ok'
    if familyId is None:#证明用户手动填写地址，需要联系管理员审核
        response_data['flag'] = 'failed'
        return response_data
    try:
        addrDetailObj = AddressDetails.objects.get(address_mark=addrDetailMask)
    except:
        response_data['flag'] = 'no_ad'  #验证码或二维码错误
        return response_data
    try:
        familyRecord = FamilyRecord.objects.get(fr_id=long(familyRecordId))
        familyIdFromFR = familyRecord.family_id
        if long(familyId)!=long(familyIdFromFR):
            response_data['flag'] = 'no_fr'  #地址错误错误
            return response_data
    except:
        response_data['flag'] = 'no_fr'  #地址错误错误
        return response_data
    #获取当前用户已经审核通过的地址
    try:            
        recordFamilys = FamilyRecord.objects.filter(user_id=userId,entity_type=1)
    except:
        response_data['flag'] = 'no_user' # 没有查到指定用户的
        return response_data
    if recordFamilys is not None:
        size = recordFamilys.count()
        for i in range(0,size,1):
            recordFamilyIdList.append(recordFamilys[i].family_id)
        if str(familyId) in recordFamilyIdList:#表明已经此地址已经审核通过
            recordFamilyIdList = []
            response_data['flag'] = 'audited' #告知用户无法重复审核
            return response_data
        recordFamilyIdList = []
    
    addrfmyId = addrDetailObj.getAddrDetailId()
    if str(addrfmyId) != str(familyId):
        response_data['flag'] = 'match_err' #告知用户无法重复审核
        return response_data
    else:
        #证明用户没有审核通过的地址
        pass
    #修改当前验证地址
    family_id = None
    try:
        family_id = addrDetailObj.getAddrDetailId()
        familyRecord.family_id = family_id
    except:    
        response_data['flag'] = 'error'  
        return response_data
    city_id      = addrDetailObj.city_id
    block_id     = addrDetailObj.block_id
    community_id = addrDetailObj.community_id
    building_id  = addrDetailObj.building_id
    apt_id       = addrDetailObj.apt_id
    familyRecord.family_city_id         = city_id
    familyRecord.family_block_id        = block_id
    familyRecord.family_community_id    = community_id
    familyRecord.family_building_num_id = building_id
    familyRecord.family_apt_num_id      = apt_id
    familyRecord.ne_status              = 0
    familyRecord.entity_type            = 1
    familyRecord.save()
    
    city_name = familyRecord.family_city
    community_name = familyRecord.family_community
    family_address = familyRecord.family_address
    user_nick = uObj.user_nick
    setWelcomeTopic(city_name,city_id,community_name,community_id,family_address,family_id,user_nick,userId)
    
    responseValue.append(getFamilyRecrodDict(city_id,block_id,community_id,
                                             building_id,apt_id,0,1,family_id))
    response_data['flag']    = 'ok'
    response_data['context'] = responseValue
    return response_data

#搜索商圈
def SearchBizCir(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}
    if request.method == 'POST':
        keyWord     = request.POST.get('q',None) #关键字
        page        = request.POST.get('page',None) #1 ++
        communityId = request.POST.get('commid',None)
#         sort        = request.POST.get('sort',0) #1离我最近 2好评优先 3人气最高0智能排序
#         tag         = request.POST.get('bctag',0) #0全部1酒店2美食3生活 
    else:
        keyWord     = request.GET.get('q',None) #关键字
        page        = request.GET.get('page',None) #1 ++
        communityId = request.GET.get('commid',None)
#         sort        = request.GET.get('sort',0) #1离我最近 2好评优先 3人气最高0智能排序
#         tag         = request.GET.get('bctag',0) #0全部1酒店2美食3生活 
    if page is None or communityId is None or keyWord is None:
        response_data['flag'] = 'argv_error'
        return response_data
    from haystack import indexes
    from addrinfo.models import BusinessCircle
    from haystack.views import SearchView
    from addrinfo.search_indexes import search_indexes
#    qe = queryset_comm(communityId)
#     queryset_comm.community = communityId
#    search_indexes.index_queryset = qe.my_queryset
    resultlist = []
    pagenum = long(page)
    while (len(resultlist)<10):
        search = SearchView()
#        if request.method == 'POST':
#            request.POST = request.POST.copy()
#            request.POST['page'] = str(pagenum)
#            pagenum = pagenum+1
#            request.POST['q'] = keyWord
#            request.POST['commid'] = communityId
#        else:
        request.GET = request.GET.copy()
        request.GET['page'] = str(pagenum)
        pagenum = pagenum+1
        request.GET['q'] = keyWord
        request.GET['commid'] = communityId
        try:
            result = search(request)
        except:
            result = 'final'
        if result == 'final':
#             resultlist.append(result)
            break
#        resultlist.append(str(result))
        if htmlanalysis(str(result)) != None:
            resultlist.append(htmlanalysis(str(result)))
    size = len(resultlist)
    if size==0:
        response_data['flag'] = 'none'
        response_data['yl_msg'] = u'没有更多了'
        return response_data
    else:
        response_data['flag'] = 'ok'
        response_data['page'] = pagenum
        response_data['data'] = resultlist
        return response_data
    
def htmlanalysis(htmlstr):
    resultlist = []
    from bs4 import BeautifulSoup
    if htmlstr == 'final':
        return None
    soup = BeautifulSoup(htmlstr.decode('utf-8'))
    for tag in soup.find_all('p'): #soup.select('a[class="sister"]')
        if '<p>No results found.</p>'== str(tag):
            return None
        resultitem = {}
        resultitem['name'] = str(tag).split("</a>")[0][7:]
        resultitem['address'] = str(tag).split("</a>")[1][4:]
        resultitem['community'] = str(tag).split("</a>")[2][4:]
#        resultitem['bc_location'] = str(tag).split("</a>")[3][4:]
        resultitem['bctag'] = str(tag).split("</a>")[4][4:]
        resultitem['distance'] = str(tag).split("</a>")[5][4:]
#        resultitem['bc_telephone'] = str(tag).split("</a>")[6][4:]
        imgurl = str(tag).split("</a>")[7][4:].replace("amp;","")
        resultitem['facility'] = str(tag).split("</a>")[8][4:]
        resultitem['uid'] = str(tag).split("</a>")[9][4:]
        from core import settings
        default_url = settings.RES_URL + 'res/default/avatars/'
        pattern = re.compile('酒店',re.UNICODE)
        if pattern.match(resultitem['bctag']) and imgurl is None or imgurl=='': 
            resultitem.setdefault('img_url', default_url+'bizcir-hotel.png')
        else:
            pattern = re.compile('美食',re.UNICODE)
            if pattern.match(resultitem['bctag']) and imgurl is None or imgurl=='':
                resultitem.setdefault('img_url', default_url+'bizcir-restaurant.png')
            else:
                pattern0 = re.compile('美食',re.UNICODE)
                pattern1 = re.compile('酒店',re.UNICODE)
                if pattern0.match(resultitem['bctag']) is None and pattern1.match(resultitem['bctag']) is None and imgurl is None or imgurl=='':
                    resultitem.setdefault('img_url', default_url+'bizcir-life.png')
                else:
                    resultitem.setdefault('img_url', imgurl)
#        resultlist.append(resultitem)
        if len(resultitem['name']) < 2:
            return None
        return resultitem

#from addrinfo.search_indexes import search_indexes
#class queryset_comm():
    
#     community = None
#    def __init__(self,community_id):
#        self.community = community_id
#def my_queryset(self,using=None,community_id):
#    self.my_queryset(self,using=None)
#     return self.get_model().objects.filter(community_id = 2).exclude(bc_address = None)
#获取商圈
def GetBizCir(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}
    if request.method == 'POST':
        sort        = request.POST.get('sort',None) #1离我最近 2好评优先 3人气最高0智能排序
        page        = request.POST.get('page',None) #0 ++
        communityId = request.POST.get('community_id',None)
        tag         = request.POST.get('bctag',None) #0全部1酒店2美食3生活 
    else:
        sort        = request.GET.get('sort',None) #1离我最近 2好评优先 3人气最高0智能排序
        page        = request.GET.get('page',None) #0 ++
        communityId = request.GET.get('community_id',None)
        tag         = request.GET.get('bctag',None) #0全部1酒店2美食3生活     

    if sort is None or page is None or communityId is None or tag is None:
        response_data['flag'] = 'argv_error'
        return response_data
    
    offset = int(page) * 10
    max = offset + 10
    if int(sort)==0: #智能排序
        try:
            if int(tag)==0:#全部
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).\
                             order_by('bc_distance','-bc_facility')[offset:max]
            elif int(tag)==1:#酒店
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'酒店').\
                             order_by('bc_distance','-bc_facility')[offset:max]
            elif int(tag)==2:#美食
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'美食').\
                             order_by('bc_distance','-bc_facility')[offset:max]
            elif int(tag)==3:#生活
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).exclude(bc_tag__contains=u'美食').\
                                exclude(bc_tag__contains=u'酒店').order_by('bc_distance','-bc_facility')[offset:max]
#                 bizcirQuerySet.group_by = ['bc_uid']
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    elif int(sort)==1: #离我最近
        try:
            if int(tag)==0:#全部
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).\
                             order_by('bc_distance')[offset:max]
            elif int(tag)==1:#酒店
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'酒店').\
                             order_by('bc_distance')[offset:max]
            elif int(tag)==2:#美食
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'美食').\
                             order_by('bc_distance')[offset:max]
            elif int(tag)==3:#生活
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).exclude(bc_tag__contains=u'美食').\
                                exclude(bc_tag__contains=u'酒店').order_by('bc_distance')[offset:max]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    elif int(sort)==2: #好评优先 
        try:
            if int(tag)==0:#全部
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).\
                             order_by('-bc_facility')[offset:max]
            elif int(tag)==1:#酒店
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'酒店').\
                             order_by('-bc_facility')[offset:max]
            elif int(tag)==2:#美食
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'美食').\
                             order_by('-bc_facility')[offset:max]
            elif int(tag)==3:#生活
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).exclude(bc_tag__contains=u'美食').\
                                exclude(bc_tag__contains=u'酒店').order_by('-bc_facility')[offset:max]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    elif int(sort)==3: #人气最高 
        try:
            if int(tag)==0:#全部
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).\
                             order_by('-bc_favorite')[offset:max]
            elif int(tag)==1:#酒店
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'酒店').\
                             order_by('-bc_favorite')[offset:max]
            elif int(tag)==2:#美食
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId,bc_tag__contains=u'美食').\
                             order_by('-bc_favorite')[offset:max]
            elif int(tag)==3:#生活
                bizcirQuerySet = BusinessCircle.objects.filter(community_id=communityId).exclude(bc_tag__contains=u'美食').\
                                exclude(bc_tag__contains=u'酒店').order_by('-bc_favorite')[offset:max]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    else:
        response_data['flag'] = 'none'
        response_data['yl_msg'] = u'没有更多了'
        return response_data    
    bizcirlist = []
    
    bizcirQuerySet.group_by = ['bc_uid']
        
    size = bizcirQuerySet.count()
    for i in range(0,size,1):
        myDict = {}
        imgurl = bizcirQuerySet[i].bc_imgurl
        bgTag = str(bizcirQuerySet[i].bc_tag)
        #使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        from core import settings
        default_url = settings.RES_URL + 'res/default/avatars/'
        pattern = re.compile('酒店',re.UNICODE)
        if pattern.match(bgTag) and imgurl is None or imgurl=='': 
            myDict.setdefault('img_url', default_url+'bizcir-hotel.png')
        else:
            pattern = re.compile('美食',re.UNICODE)
            if pattern.match(bgTag) and imgurl is None or imgurl=='':
                myDict.setdefault('img_url', default_url+'bizcir-restaurant.png')
            else:
                pattern0 = re.compile('美食',re.UNICODE)
                pattern1 = re.compile('酒店',re.UNICODE)
                if pattern0.match(bgTag) is None and pattern1.match(bgTag) is None and imgurl is None or imgurl=='':
                    myDict.setdefault('img_url', default_url+'bizcir-life.png')
                else:
                    myDict.setdefault('img_url', imgurl)
        myDict.setdefault('distance',bizcirQuerySet[i].bc_distance)
        myDict.setdefault('facility',bizcirQuerySet[i].bc_facility)
        myDict.setdefault('describe',bizcirQuerySet[i].bc_describe)
        myDict.setdefault('address', bizcirQuerySet[i].bc_address)
        myDict.setdefault('bctag',   bizcirQuerySet[i].bc_tag)
        myDict.setdefault('name',    bizcirQuerySet[i].bc_name)
        myDict.setdefault('uid',     bizcirQuerySet[i].bc_uid)
        bizcirlist.append(myDict)
    size = len(bizcirlist)
    if size==0:
        response_data['flag'] = 'none'
        response_data['yl_msg'] = u'没有更多了'
        return response_data
    else:
        return bizcirlist

def imgGenPath(user_id, uid):
    userDir = settings.MEDIA_ROOT+'youlin/res/eva/'+str(uid)+'/topic/' + str(user_id) + '/'
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

def getTargetFacility(facility,uid,evatag):
    #服务态度：菜品口味：环境等级
    facility_list = facility.split(":")
    attitude = float(facility_list[0])
    flavor   = float(facility_list[1])
    env      = float(facility_list[2])
    if int(evatag)==0:#0美食 1 宾馆 2 生活娱乐
        facility = round((attitude + flavor + env)/3,1)
    else:
        facility = round((attitude + env)/2,1)
    bizcirFacilityObj = BizCirFacility(bcf_uid=str(uid),bcf_tag=int(evatag),bcf_facility=float(facility),\
                                       bcf_attitude=float(attitude),bcf_flavor=float(flavor),bcf_env=float(env))
    bizcirFacilityObj.save()
    return bizcirFacilityObj
    
#发布商家评价
def PostBizCirEvaluate(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    if request.method == 'POST':
        senderId   = request.POST.get('sender_id',None) #发送者id
        uid        = request.POST.get('uid',None) #商铺标示
        type       = request.POST.get('type',None) #类型 0=》纯文字 1=》带有图片  @@@@2=》带有语音
        content    = request.POST.get('content',None)
        facility   = request.POST.get('facility',None)#服务态度：菜品口味：环境等级
        status     = request.POST.get('status',None) #是否匿名 0否 1是
        evatag     = request.POST.get('evatag',None) #0美食 1 宾馆 2 生活娱乐
    else:
        senderId   = request.GET.get('sender_id',None) #发送者id
        uid        = request.GET.get('uid',None) #商铺标示
        type       = request.GET.get('type',None) #类型 0=》纯文字 1=》带有图片  @@@@2=》带有语音
        content    = request.GET.get('content',None)
        facility   = request.GET.get('facility',None)#服务态度：菜品口味：环境等级
        status     = request.GET.get('status',None)
        evatag     = request.GET.get('evatag',None) #0美食 1 宾馆 2 生活娱乐
    curtime = long(time.time()*1000)
    userObj = User.objects.get(user_id=long(senderId))
    communityId = userObj.user_community_id

    bizcirFacilityObj = getTargetFacility(facility,uid,evatag)
    bizcirEvaObj = BizCirEvaluate(bce_uid=str(uid),bce_content=content,bce_sendtime=curtime,\
                                  bce_senderid=long(senderId),bce_status=int(status),\
                                  community_id=communityId,user_id=long(senderId),\
                                  bce_contenttype=int(type),facility=bizcirFacilityObj)
    bizcirEvaObj.save()
    bizcirEvaObjId = bizcirEvaObj.getBizCirEva()
    from community.views import makeThumbnail,imgGenName
    for ft in filesTuple:
        if ft in request.FILES:
            image = request.FILES.get(ft, None)
            newImage = imgGenName(image.name) # new image
        #    uploadImage = '00' + newImage # resImage
            bigImage = '0' + newImage # big image
            smaillImage = newImage # smaill image
            userDir = imgGenPath(senderId, uid)
            streamfile = open(userDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
        #    makeThumbnail(userDir, uploadImage, bigImage,80)
            makeThumbnail(userDir, bigImage, smaillImage,25)
            respath = 'res/eva/'+str(uid)+'/topic/'+str(senderId)+'/'+ smaillImage
            BizCirMediaFiles.objects.create(uid=str(uid),bizcirevaluate=bizcirEvaObj,bcmf_respath=respath)
    UEvaRecordQuerySet = UserEvaluatiorRecord.objects.filter(uer_uid=str(uid),user_id=long(senderId))
    for obj in UEvaRecordQuerySet:
        obj.uer_status = 1
        obj.save()
    response_data['flag'] = "ok"
    response_data['user_id'] = senderId
    response_data['bizeva_id'] = bizcirEvaObjId
    response_data['yl_msg'] = u'感谢您的评价！'
    return response_data
    
#获取商家评价
def GetBizCirEvaluate(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    all_count = 0
    img_count = 0
    response_data = {}            
    if request.method == 'POST':
        uid         = request.POST.get('uid',None)
        bceid       = request.POST.get('bceid',None) #初始化0   否则传递最后一个id
        actionId    = request.POST.get('action_id',None) #0初始化1上拉2下拉
        communityId = request.POST.get('community_id',None)
        target      = request.POST.get('target',None) #0 全部   1 晒图
    else:
        uid         = request.GET.get('uid',None)
        bceid       = request.GET.get('bceid',None) #初始化0   否则传递最后一个id
        actionId    = request.GET.get('action_id',None) #0初始化1上拉2下拉
        communityId = request.GET.get('community_id',None)
        target      = request.GET.get('target',None) #0 全部   1 晒图
    if uid is None or bceid is None or actionId is None or communityId is None:
        response_data['flag'] = 'argv_error'
        return response_data
    if int(actionId)==0:#初始化
        try:
            if int(target)==0:#全部
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid)).\
                                 order_by('-bce_id')[:10]
            else:#晒图
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid)).\
                                 exclude(bce_contenttype=0).order_by('-bce_id')[:10]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    elif int(actionId)==1:#上拉
        try:
            if int(target)==0:#全部
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid),\
                                 bce_id__lt=long(bceid)).order_by('-bce_id')[:10]
            else:#晒图
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid),\
                                 bce_id__lt=long(bceid)).exclude(bce_contenttype=0).order_by('-bce_id')[:10]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    elif int(actionId)==2:#下拉
        try:
            if int(target)==0:#全部
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid),\
                                 bce_id__gt=long(bceid)).order_by('-bce_id')[:10]
            else:
                bcEvalQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid),\
                                 bce_id__gt=long(bceid)).exclude(bce_contenttype=0).order_by('-bce_id')[:10]
        except Exception,e:
            response_data['flag'] = 'error'
            response_data['error'] = str(e)
            return response_data
    all_count = BizCirEvaluate.objects.filter(bce_uid=str(uid)).count()
    img_count = BizCirEvaluate.objects.filter(bce_uid=str(uid)).exclude(bce_contenttype=0).count()          
    bcEvalQueryList = []
    maxEvaId = None
    size = bcEvalQuerySet.count()
    from core import settings
    avatar_url = settings.RES_URL + 'res/default/avatars/0default-normal-avatar.png'
    for i in range(0,size,1):
        uid  = bcEvalQuerySet[i].bce_uid
        type = bcEvalQuerySet[i].bce_contenttype
        status = bcEvalQuerySet[i].bce_status
        dicts = {}
        maxEvaId = bcEvalQuerySet[i].getBizCirEva()
        dicts.setdefault('uid', uid)
        dicts.setdefault('type', type)
        dicts.setdefault('status', status)
        dicts.setdefault('facility', bcEvalQuerySet[i].facility.bcf_facility)
        dicts.setdefault('content', bcEvalQuerySet[i].bce_content)
        dicts.setdefault('time', bcEvalQuerySet[i].bce_sendtime)
        dicts.setdefault('userid', bcEvalQuerySet[i].user.getTargetUid())
        dicts.setdefault('nick', bcEvalQuerySet[i].user.user_nick)
        if int(status)==0:#否
            dicts.setdefault('avatar', bcEvalQuerySet[i].user.user_portrait)
        else:
            dicts.setdefault('avatar', avatar_url)
        
        if int(type)==0:#0 纯字符串  1 非纯字符串
            dicts.setdefault('media', 'none')
        else:
            bcmfQuerySet = BizCirMediaFiles.objects.filter(uid=str(uid),bcmf_contenttype=0,\
                                                           bizcirevaluate_id=long(maxEvaId)).order_by('-bcmf_id')
            bcmSize = bcmfQuerySet.count()
            bcmList = []
            for j in range(0,bcmSize,1):
                bcmList.append(settings.RES_URL+bcmfQuerySet[j].bcmf_respath)
            if len(bcmList)==0:
                dicts.setdefault('media', 'none')
            else:
                dicts.setdefault('media', bcmList)
        bcEvalQueryList.append(dicts)
    size = len(bcEvalQueryList)
    if size==0:
        response_data['flag'] = 'no'
        response_data['id'] = 0
        response_data['allcount'] = all_count
        response_data['imgcount'] = img_count
        response_data['querylist'] = None
        response_data['systime'] = long(time.time()*1000)
        return response_data
    else:
        response_data['flag'] = 'ok'
        response_data['id'] = maxEvaId
        response_data['allcount'] = all_count
        response_data['imgcount'] = img_count
        response_data['querylist'] = bcEvalQueryList
        response_data['systime'] = long(time.time()*1000)
        return response_data
    
#进入详情页
def GetBizCirDetailPage(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}            
    if request.method == 'POST':
        uid         = request.POST.get('uid',None)
        communityId = request.POST.get('community_id',None)
    else:
        uid         = request.GET.get('uid',None)
        communityId = request.GET.get('community_id',None)
    if uid is None:
        response_data['flag'] = 'argv_error'
        return response_data  
    from core import settings
    avatar_url = settings.RES_URL + 'res/default/avatars/0default-normal-avatar.png'
    bcQuerySet = BusinessCircle.objects.filter(bc_uid=str(uid),community_id=long(communityId))
    bcQuerySet.group_by = ['bc_uid']
    bcObj = bcQuerySet[0]
    bcDict = {}
    bcDict.setdefault('name', bcObj.bc_name)
    bcDict.setdefault('imgurl', bcObj.bc_imgurl)
    bcDict.setdefault('address', bcObj.bc_address)
    bcDict.setdefault('location', bcObj.bc_location)
    bcDict.setdefault('shophours', bcObj.bc_shophours)
    bcDict.setdefault('telephone', bcObj.bc_telephone)
    bcDict.setdefault('systime', long(time.time()*1000))
    bcEvaQuerySet = BizCirEvaluate.objects.filter(bce_uid=str(uid),community_id=long(communityId)).order_by('-bce_id')
    bcEvaSize = bcEvaQuerySet.count() 
    if bcEvaSize == 0:
        dicts = None
    else:
        uid  = bcEvaQuerySet[0].bce_uid
        type = bcEvaQuerySet[0].bce_contenttype
        status = bcEvaQuerySet[0].bce_status
        curId = bcEvaQuerySet[0].getBizCirEva()
        dicts = {}
        dicts.setdefault('uid', uid)
        dicts.setdefault('type', type)
        dicts.setdefault('userid', bcEvaQuerySet[0].user.getTargetUid())
        dicts.setdefault('content', bcEvaQuerySet[0].bce_content)
        dicts.setdefault('time', bcEvaQuerySet[0].bce_sendtime)
        dicts.setdefault('nick', bcEvaQuerySet[0].user.user_nick)
        dicts.setdefault('facility', bcEvaQuerySet[0].facility.bcf_facility)
        dicts.setdefault('status', status)
        if int(status)==0:#不匿名
            dicts.setdefault('avatar', bcEvaQuerySet[0].user.user_portrait)
        else:
            dicts.setdefault('avatar', avatar_url)
        if int(type)==0:#0 纯字符串  1 非纯字符串
            dicts.setdefault('media', 'none')
        else:
            bcmfQuerySet = BizCirMediaFiles.objects.filter(uid=str(uid),bcmf_contenttype=0,\
                                                           bizcirevaluate_id=long(curId)).order_by('-bcmf_id')
            bcmSize = bcmfQuerySet.count()
            bcmList = []
            for j in range(0,bcmSize,1):
                bcmList.append(settings.RES_URL+bcmfQuerySet[j].bcmf_respath)
            dicts.setdefault('media', bcmList)
    bcDict.setdefault('eva_count', bcEvaSize)
    bcDict.setdefault('eva_dict', dicts)
    response_data['flag'] = 'ok'
    response_data['detail'] = bcDict
    return response_data

#获取用户操作
def GetUserOperatRecords(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}            
    if request.method == 'POST':
        uid         = request.POST.get('uid',None)
        userId      = request.POST.get('user',None)
        communityId = request.POST.get('community',None)
    else:
        uid         = request.GET.get('uid',None)
        userId      = request.GET.get('user',None)
        communityId = request.GET.get('community',None)
    if uid is None or userId is None or communityId is None:
        response_data['flag'] = 'argv_error'
        return response_data
    try:
        #8小时候推送
        TimingTaskWithEvaluatiorRecord.apply_async((uid, userId,communityId), countdown=10)#10h失效
#         TimingTaskWithEvaluatiorRecord.apply_async((uid, userId,communityId), countdown=10*60*60)#10h失效
#         TimingTaskWithEvaluatiorRecord.delay(uid, userId,communityId)
    except Exception,e:
        response_data['flag'] = 'error'
        response_data['error'] = str(e)
    response_data['flag'] = 'ok'
    return response_data

#判断是否已评价
def GetOrCheckEvaRecord(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    response_data = {}        
    if request.method == 'POST':
        uerId = request.POST.get('uer_id',None)
    else:
        uerId = request.GET.get('uer_id',None)
    try:
        UserEvaluatiorRecord.objects.get(uer_id=long(uerId),uer_status=1)
        response_data['flag'] = 'ok'
        return response_data
    except Exception,e:#需要评论
        response_data['flag'] = 'no'
        response_data['error'] = str(e)
        return response_data
    
     
