# Create your views here.
# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from models import CommunityService,WeatherPushRecord
from web.models import News,NewsPush
from django.core import serializers
from django.conf import settings
from comServices.tasks import TimingTaskWithWeather
import re
import os
import json
import time
import random
import requests


@api_view(['GET','POST'])

def loadCommunityService(request):
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
    else:
        community_id = request.GET.get('community_id')
    serviceQuerySet = CommunityService.objects.filter(community_id=community_id)
    servicesCount = serviceQuerySet.count()
    listService = []
    
    if serviceQuerySet:
        for i in range(0,servicesCount,1):
            commId = serviceQuerySet[i].getCommId()
            department = serviceQuerySet[i].service_department
            phone = serviceQuerySet[i].service_phone
            address = serviceQuerySet[i].service_address
            office_hours = serviceQuerySet[i].service_office_hours
            serviceDict = getServicesDict(department,phone,address,office_hours,commId)
            listService.append(serviceDict)
        return HttpResponse(json.dumps(listService), content_type="application/json")
    else: 
        response_data = {}
        response_data['flag'] = 'none'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def getServicesDict(department,phone,address,office_hours,commId):
    dicts = {}
    dicts.setdefault('service_id', commId)
    dicts.setdefault('service_department', department)
    dicts.setdefault('service_phone', phone)
    dicts.setdefault('service_address', address)
    dicts.setdefault('service_office_hours', office_hours)
    return dicts

@api_view(['GET','POST'])
def getNewsList(request):
 
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
        push_time = request.POST.get('push_time')
        flag = request.POST.get('flag')
        
    else:
        community_id = request.GET.get('community_id')
        push_time = request.GET.get('push_time')
        flag = request.GET.get('flag')
    response_data = {}
    try:
        if push_time is None:
            pushSet = NewsPush.objects.filter(community_id=community_id).order_by('-push_id')[:3]
        else:
            if flag == "up":
                pushSet = NewsPush.objects.filter(community_id=community_id,push_time__gt=push_time).order_by('-push_id')[3]
            else:
                pushSet = NewsPush.objects.filter(community_id=community_id,push_time__lt=push_time).order_by('-push_id')[:3]
        servicesCount = pushSet.count()
        newsList = []
        if pushSet:
            for i in range(0,servicesCount,1):
                
                newIdstr = pushSet[i].push_newIds
                newsIds = newIdstr.split(',')
                push_time = pushSet[i].push_time
                p_items = {}
                otherNews = []
                for newsId in newsIds:
                    
                    newsObj = News.objects.get(new_id=newsId)
                    servhost = request.get_host()
                    new_url = 'http://'+servhost+'/adminpush/web/getNews/?id='+newsId
                    pic_url = 'http://'+servhost+newsObj.new_small_pic
                    
                    if(newsObj.pri_flag == 1):
                        p_items['new_title'] = newsObj.new_title
                        p_items['new_id'] = newsObj.new_id
                        p_items['new_add_time'] = newsObj.new_add_time
                        p_items['new_small_pic'] = pic_url
                        p_items['new_url'] = new_url
                    else:
                        newsDict = getNewsDict(newsObj,pic_url,new_url)
                        otherNews.append(newsDict)
                serviceDict = getNewsListDict(push_time,p_items,otherNews)
                newsList.append(serviceDict)
            return HttpResponse(json.dumps(newsList), content_type="application/json")
        
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    except:
        response_data['flag'] = 'no'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def getNewsDict(newsObj,pic_url,new_url):
    dicts = {}
    dicts.setdefault('new_title', newsObj.new_title)
    dicts.setdefault('new_id', newsObj.new_id)
    dicts.setdefault('new_add_time', newsObj.new_add_time)
    dicts.setdefault('new_small_pic', pic_url)
    dicts.setdefault('new_url', new_url)
    return dicts

def getNewsListDict(push_time,p_items,otherNews,subObj):
    dicts = {}
    dicts.setdefault('push_time', push_time)
    dicts.setdefault('new_title', p_items['new_title'])
    dicts.setdefault('new_id', p_items['new_id'])
    dicts.setdefault('new_add_time', p_items['new_add_time'])
    dicts.setdefault('new_small_pic', p_items['new_small_pic'])
    dicts.setdefault('new_url', p_items['new_url'])
    dicts.setdefault('otherNew', otherNews)
    from core.settings import HOST_IP
    dicts.setdefault('subUrl', HOST_IP + subObj.s_url)
    dicts.setdefault('subName', subObj.s_name)
    return dicts


#获取小区服务信息
def LoadCommunityService(request):
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
    else:
        community_id = request.GET.get('community_id')
    serviceQuerySet = CommunityService.objects.filter(community_id=community_id)
    servicesCount = serviceQuerySet.count()
    listService = []
    
    if serviceQuerySet:
        for i in range(0,servicesCount,1):
            commId = serviceQuerySet[i].getCommId()
            department = serviceQuerySet[i].service_department
            phone = serviceQuerySet[i].service_phone
            address = serviceQuerySet[i].service_address
            office_hours = serviceQuerySet[i].service_office_hours
            serviceDict = getServicesDict(department,phone,address,office_hours,commId)
            listService.append(serviceDict)
        return listService
    else: 
        response_data = {}
        response_data['flag'] = 'null'
        return response_data
    
#获得新闻列表
def GetNewsList(request):
 
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
        push_time = request.POST.get('push_time')
        flag = request.POST.get('flag')
        
    else:
        community_id = request.GET.get('community_id')
        push_time = request.GET.get('push_time')
        flag = request.GET.get('flag')
    response_data = {}
    try:
        if push_time is None:
            pushSet = NewsPush.objects.filter(community_id=community_id).order_by('-push_id')[:3]
        else:
            if flag == "up":
                pushSet = NewsPush.objects.filter(community_id=community_id,push_time__gt=push_time).order_by('-push_id')[:3]
            else:
                pushSet = NewsPush.objects.filter(community_id=community_id,push_time__lt=push_time).order_by('-push_id')[:3]
        servicesCount = pushSet.count()
        newsList = []
        if pushSet:
            from web.models import Subscription
            subObj = Subscription.objects.get(community_id=long(community_id))
            for i in range(0,servicesCount,1):
                
                newIdstr = pushSet[i].push_newIds
                newsIds = newIdstr.split(',')
                push_time = pushSet[i].push_time
                p_items = {}
                otherNews = []
                for newsId in newsIds:
                    newsObj = News.objects.get(new_id=newsId)
                    servhost = request.get_host()
                    new_url = 'http://'+servhost+settings.SHARE_NEWS+newsId
                    tmp_pic_url = newsObj.new_small_pic
                    if tmp_pic_url[:4]=='http':
                        pic_url = tmp_pic_url
                    else:
                        pic_url = 'https://'+servhost+tmp_pic_url
                    
                    if(newsObj.pri_flag == 1):
                        p_items['new_title'] = newsObj.new_title
                        p_items['new_id'] = newsObj.new_id
                        p_items['new_add_time'] = newsObj.new_add_time
                        p_items['new_small_pic'] = pic_url
                        p_items['new_url'] = new_url
                    else:
                        newsDict = getNewsDict(newsObj,pic_url,new_url)
                        otherNews.append(newsDict)
                serviceDict = getNewsListDict(push_time,p_items,otherNews,subObj)
                newsList.append(serviceDict)
            return newsList
        
        response_data['flag'] = 'no1'
        return response_data
    except Exception,e:
        response_data['Exception'] = str(Exception)
        response_data['Error'] = str(e)
        response_data['flag'] = 'no2'
        return response_data
    
def UserRegistWithMJ(request):
    from users.easemob_server import registUserWithMahjong
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
    else:
        user_id = request.GET.get('user_id')    
    response_data = registUserWithMahjong(user_id)
    return response_data

#判断当前日期星座
def GetCurrentZodiac(zodiacList,zodiacImgList):
    from core.settings import RES_URL
    dicts = {}
    curTime = time.localtime(time.time())
    curYear = int(curTime[0])
    curMon  = int(curTime[1])
    curDay  = int(curTime[2])
    if curMon == 1 and curDay >= 20:
        dicts['name'] = zodiacList[0]
        dicts['url'] = RES_URL + zodiacImgList[0]
        return dicts
    if curMon == 2 and curDay <= 18:
        dicts['name'] = zodiacList[0]
        dicts['url'] = RES_URL + zodiacImgList[0]
        return dicts
    if curMon == 2 and curDay >= 19:
        dicts['name'] = zodiacList[1]
        dicts['url'] = RES_URL + zodiacImgList[1]
        return dicts
    if curMon == 3 and curDay <= 20:
        dicts['name'] = zodiacList[1]
        dicts['url'] = RES_URL + zodiacImgList[1]
        return dicts
    if curMon == 3 and curDay >= 21:
        dicts['name'] = zodiacList[2]
        dicts['url'] = RES_URL + zodiacImgList[2]
        return dicts
    if curMon == 4 and curDay <= 19:
        dicts['name'] = zodiacList[2]
        dicts['url'] = RES_URL + zodiacImgList[2]
        return dicts
    if curMon == 4 and curDay >= 20:
        dicts['name'] = zodiacList[3]
        dicts['url'] = RES_URL + zodiacImgList[3]
        return dicts
    if curMon == 5 and curDay <= 20:
        dicts['name'] = zodiacList[3]
        dicts['url'] = RES_URL + zodiacImgList[3]
        return dicts
    if curMon == 5 and curDay >= 21:
        dicts['name'] = zodiacList[4]
        dicts['url'] = RES_URL + zodiacImgList[4]
        return dicts
    if curMon == 6 and curDay <= 21:
        dicts['name'] = zodiacList[4]
        dicts['url'] = RES_URL + zodiacImgList[4]
        return dicts
    if curMon == 6 and curDay >= 22:
        dicts['name'] = zodiacList[5]
        dicts['url'] = RES_URL + zodiacImgList[5]
        return dicts
    if curMon == 7 and curDay <= 22:
        dicts['name'] = zodiacList[5]
        dicts['url'] = RES_URL + zodiacImgList[5]
        return dicts
    if curMon == 7 and curDay >= 23:
        dicts['name'] = zodiacList[6]
        dicts['url'] = RES_URL + zodiacImgList[6]
        return dicts
    if curMon == 8 and curDay <= 22:
        dicts['name'] = zodiacList[6]
        dicts['url'] = RES_URL + zodiacImgList[6]
        return dicts
    if curMon == 8 and curDay >= 23:
        dicts['name'] = zodiacList[7]
        dicts['url'] = RES_URL + zodiacImgList[7]
        return dicts
    if curMon == 9 and curDay <= 22:
        dicts['name'] = zodiacList[7]
        dicts['url'] = RES_URL + zodiacImgList[7]
        return dicts
    if curMon == 9 and curDay >= 23:
        dicts['name'] = zodiacList[8]
        dicts['url'] = RES_URL + zodiacImgList[8]
        return dicts
    if curMon == 10 and curDay <= 23:
        dicts['name'] = zodiacList[8]
        dicts['url'] = RES_URL + zodiacImgList[8]
        return dicts
    if curMon == 10 and curDay >= 24:
        dicts['name'] = zodiacList[9]
        dicts['url'] = RES_URL + zodiacImgList[9]
        return dicts
    if curMon == 11 and curDay <= 22:
        dicts['name'] = zodiacList[9]
        dicts['url'] = RES_URL + zodiacImgList[9]
        return dicts
    if curMon == 11 and curDay >= 23:
        dicts['name'] = zodiacList[10]
        dicts['url'] = RES_URL + zodiacImgList[10]
        return dicts
    if curMon == 12 and curDay <= 21:
        dicts['name'] = zodiacList[10]
        dicts['url'] = RES_URL + zodiacImgList[10]
        return dicts    
    if curMon == 12 and curDay >= 23:
        dicts['name'] = zodiacList[10]
        dicts['url'] = RES_URL + zodiacImgList[10]
        return dicts
    if curMon == 1 and curDay <= 19:
        dicts['name'] = zodiacList[11]
        dicts['url'] = RES_URL + zodiacImgList[11]
        return dicts 
        
#推送小区天气预报
def PushCommunityWeather():
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    from addrinfo.models import City,Community
    
    community_list = Community.objects.all() 
    
    city_list = City.objects.all()
    
    for cityIndex in range(0,city_list.count(),1):
        pass
        cityObj = city_list[cityIndex]
        commQuerySet = Community.objects.filter(city=cityObj)
        if commQuerySet.count() <= 0:
            pass
        else:
            response_data = {}
            argv_city_name = cityObj.city_name
            urlWea = "http://op.juhe.cn/onebox/weather/query?cityname="\
                     +argv_city_name+"&key=d9524c5e03f51388151c941d65166ec6"
            res = requests.get(urlWea).content
            jsonobj = json.loads(res)
            if long(jsonobj['error_code'])==207301:
                response_data['flag'] = 'error'
                response_data['yl_msg'] = u'错误的查询城市名'
                return response_data
            elif long(jsonobj['error_code'])==207302:
                response_data['flag'] = 'error'
                response_data['yl_msg'] = u'查询不到该城市的相关信息'
                return response_data
            elif long(jsonobj['error_code'])==207303:
                response_data['flag'] = 'error'
                response_data['yl_msg'] = u'网络错误，请重试'
                return response_data
            else:#正常
                zodiacDetailList = []
                zodiacList = [u'水瓶座',u'双鱼座',u'白羊座',u'金牛座',
                              u'双子座',u'巨蟹座',u'狮子座',u'处女座',
                              u'天秤座',u'天蝎座',u'射手座',u'摩羯座']
                from core.settings import RES_URL
                zodiacImgList = ['res/default/xingzuo/01.png','res/default/xingzuo/02.png','res/default/xingzuo/03.png','res/default/xingzuo/04.png',
                                 'res/default/xingzuo/05.png','res/default/xingzuo/06.png','res/default/xingzuo/07.png','res/default/xingzuo/08.png',
                                 'res/default/xingzuo/09.png','res/default/xingzuo/10.png','res/default/xingzuo/11.png','res/default/xingzuo/12.png']
                for indexZodiat in range(len(zodiacList)):
                    resultBody = requests.get("http://apis.baidu.com/bbtapi/constellation/constellation_query", 
                                           params={'consName': zodiacList[indexZodiat], 'type': 'today'}, 
                                           headers={'apikey': 'f2f2251558ce7cadaeee02d477baf40b'})
                    resultWihtZod = resultBody.content
                    jsonobjWihtZod = json.loads(resultWihtZod)
#                     zodiacDetailDict = {}
#                     zodiacDetailDict[zodiacList[indexZodiat]] = jsonobjWihtZod
                    zodiacDetailList.append(jsonobjWihtZod)
                for indexZodiaWeek in range(len(zodiacList)):
                    resultWeekBody = requests.get("http://apis.baidu.com/bbtapi/constellation/constellation_query", 
                                                   params={'consName': zodiacList[indexZodiaWeek], 'type': 'week'}, 
                                                   headers={'apikey': 'f2f2251558ce7cadaeee02d477baf40b'})
                    resultWihtWeekZod = resultWeekBody.content
                    jsonobjWihtWeekZod = json.loads(resultWihtWeekZod)
                    import copy
                    weekZodDict = copy.deepcopy(jsonobjWihtWeekZod)
                    weekZodDict['money'] = jsonobjWihtWeekZod['money'][3:]
                    weekZodDict['work'] = jsonobjWihtWeekZod['work'][3:]
                    weekZodDict['job'] = jsonobjWihtWeekZod['job'][3:]
                    if jsonobjWihtWeekZod['health'][3:][-6:]==u'作者：马子晴':
                        weekZodDict['health'] = jsonobjWihtWeekZod['health'][3:][:-6]
                    else:
                        weekZodDict['health'] = jsonobjWihtWeekZod['health'][3:]
                    weekZodDict['love'] = jsonobjWihtWeekZod['love'][3:]
                    zodiacDetailWeekDict = {}
                    zodiacDetailWeekDict['week'] = weekZodDict
                    zodiacDetailList[indexZodiaWeek].update(zodiacDetailWeekDict)
                weatherInfoDict = {}
                response_data['flag'] = 'ok'
        #             response_data['result'] = jsonobj['result']['data']
                weatherList = (jsonobj['result']['data']['weather'])[0]['info']['day']
                weatherDetail = weatherList[1] + ' ' + weatherList[2] + '°' + weatherList[4] + weatherList[3]
                weatherInfo = '【' + argv_city_name + '】 ' + weatherDetail
                import time
                wprTime = long(time.time()*1000)
                wprTimestamp = long(wprTime)/1000
                wprtime = time.localtime(wprTimestamp)
                wprMon  = int(wprtime[1])
                zodIndex = wprMon-1
#                 zodName = zodiacList[zodIndex]
                zodDicts = {}
                zodInfo = GetCurrentZodiac(zodiacList,zodiacImgList)
#                 zodDicts['zodiac_name'] = zodName
                zodDicts['zodiac_name'] = zodInfo['name']
#                 zodDicts['zodiac_imgurl'] = RES_URL + zodiacImgList[zodIndex]
                zodDicts['zodiac_imgurl'] = zodInfo['url']
                zodDicts['zodiac_summary'] = ' 【星座运势】' + (zodiacDetailList[zodIndex])['summary']
                commQuerySet[1].getCommunityId()
                commSize = commQuerySet.count()
                for commIndex in range(0,commSize,1):
                    communityId = commQuerySet[commIndex].getCommunityId()
                    if int(communityId) == 3 or int(communityId) == 4:
                        continue
                    weaObj = WeatherPushRecord(wpr_detail=json.dumps(jsonobj['result']['data']),zod_detail=json.dumps(zodiacDetailList),\
                                               wpr_time=wprTime,zod_info=json.dumps(zodDicts),community_id=long(communityId))
                    weaObj.save()
                    weaId = weaObj.getWeatherPushId()  
                    weatherInfoDict['time'] = wprTime
                    weatherInfoDict['content'] = weatherInfo
                    weatherInfoDict['community_id'] = communityId  
                    weatherInfoDict['weaorzoc_id'] = weaId
                    import jpush as jpush
                    from push.views import createPushRecord,readIni
                    config = readIni()
                    pushTitle = '天气快报'
                    pushContent = weatherInfoDict['content']
                    apiKey = config.get("SDK", "apiKey")
                    secretKey = config.get("SDK", "secretKey")
                    _jpush = jpush.JPush(apiKey,secretKey) 
                    tagSuffix = config.get('topic', "tagSuffix")
                    tagNormalName = tagSuffix + str(weatherInfoDict['community_id'])
                    tagSuffix = config.get('report', "tagSuffix")
                    tagAdminName = tagSuffix+str(weatherInfoDict['community_id'])
                    tagSuffix = config.get('property', "tagSuffix")
                    tagPropertyName = tagSuffix+str(weatherInfoDict['community_id'])
                
                    from core.settings import HOST_IP,RES_URL,PUSH_STATUS
                    currentPushTime = long(time.time()*1000)
                    evaDict = {}
                    evaDict['title'] = pushTitle
                    evaDict['content'] = pushContent
                    evaDict['pushTime'] = currentPushTime
                    evaDict['wprTime'] = weatherInfoDict['time']
                    evaDict['weaId'] = weatherInfoDict['weaorzoc_id']
                    evaDict['pushType'] = 8
                    evaDict['contentType'] = 1
                    evaDict['communityId'] = communityId
                    evaDict['userAvatar'] = RES_URL+'res/default/avatars/default-weather.png'
                    recordId = createPushRecord(8,1,pushTitle,pushContent,currentPushTime,8001,json.dumps(evaDict),communityId,8001)
                    evaDict['recordId'] = recordId
                    pushExtra = evaDict
                    push = _jpush.create_push()
                    push.audience = jpush.all_
                    push.audience = jpush.audience(
                                jpush.tag(tagNormalName,tagAdminName,tagPropertyName),
                            )
                    push.notification = jpush.notification(
                        ios=jpush.ios(alert=pushContent.encode('uft-8'), badge="+1", extras=pushExtra),
                        android=jpush.android(pushContent,pushTitle,None,pushExtra)
                    )
                    push.options = {"time_to_live":86400, "sendno":9527, "apns_production":PUSH_STATUS}
                    push.platform = jpush.all_
                    push.send()

#插入小区天气预报
def CommunityWeather(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if request.method == 'POST':
        cityId      = request.POST.get('city_id')
        communityId = request.POST.get('community_id')
    else:
        cityId      = request.GET.get('city_id')
        communityId = request.GET.get('community_id')
    if cityId is None:
        response_data['flag'] = 'argv_error'
        return response_data
    response_data = {}
    from addrinfo.models import City
#     try:
    cityObj = City.objects.get(city_id=long(cityId))
    argv_city_name = cityObj.city_name
    urlWea = "http://op.juhe.cn/onebox/weather/query?cityname="\
             +argv_city_name+"&key=d9524c5e03f51388151c941d65166ec6"
    res = requests.get(urlWea).content
    jsonobj = json.loads(res)
    if long(jsonobj['error_code'])==207301:
        response_data['flag'] = 'error'
        response_data['yl_msg'] = u'错误的查询城市名'
        return response_data
    elif long(jsonobj['error_code'])==207302:
        response_data['flag'] = 'error'
        response_data['yl_msg'] = u'查询不到该城市的相关信息'
        return response_data
    elif long(jsonobj['error_code'])==207303:
        response_data['flag'] = 'error'
        response_data['yl_msg'] = u'网络错误，请重试'
        return response_data
    else:#正常
        zodiacDetailList = []
        zodiacList = [u'水瓶座',u'双鱼座',u'白羊座',u'金牛座',
                      u'双子座',u'巨蟹座',u'狮子座',u'处女座',
                      u'天秤座',u'天蝎座',u'射手座',u'摩羯座']
        from core.settings import RES_URL
        zodiacImgList = ['res/default/xingzuo/01.png','res/default/xingzuo/02.png','res/default/xingzuo/03.png','res/default/xingzuo/04.png',
                         'res/default/xingzuo/05.png','res/default/xingzuo/06.png','res/default/xingzuo/07.png','res/default/xingzuo/08.png',
                         'res/default/xingzuo/09.png','res/default/xingzuo/10.png','res/default/xingzuo/11.png','res/default/xingzuo/12.png']
        for indexZodiat in range(len(zodiacList)):
            resultBody = requests.get("http://apis.baidu.com/bbtapi/constellation/constellation_query", 
                                   params={'consName': zodiacList[indexZodiat], 'type': 'today'}, 
                                   headers={'apikey': 'f2f2251558ce7cadaeee02d477baf40b'})
            resultWihtZod = resultBody.content
            jsonobjWihtZod = json.loads(resultWihtZod)
            zodiacDetailDict = {}
            zodiacDetailDict[zodiacList[indexZodiat]] = jsonobjWihtZod
            zodiacDetailList.append(jsonobjWihtZod)
        for indexZodiaWeek in range(len(zodiacList)):
            resultWeekBody = requests.get("http://apis.baidu.com/bbtapi/constellation/constellation_query", 
                                           params={'consName': zodiacList[indexZodiaWeek], 'type': 'week'}, 
                                           headers={'apikey': 'f2f2251558ce7cadaeee02d477baf40b'})
            resultWihtWeekZod = resultWeekBody.content
            jsonobjWihtWeekZod = json.loads(resultWihtWeekZod)
            import copy
            weekZodDict = copy.deepcopy(jsonobjWihtWeekZod)
            weekZodDict['money'] = jsonobjWihtWeekZod['money'][3:]
            weekZodDict['work'] = jsonobjWihtWeekZod['work'][3:]
            weekZodDict['job'] = jsonobjWihtWeekZod['job'][3:]
            if jsonobjWihtWeekZod['health'][3:][-6:]==u'作者：马子晴':
                weekZodDict['health'] = jsonobjWihtWeekZod['health'][3:][:-6]
            else:
                weekZodDict['health'] = jsonobjWihtWeekZod['health'][3:]
            weekZodDict['love'] = jsonobjWihtWeekZod['love'][3:]
            zodiacDetailWeekDict = {}
            zodiacDetailWeekDict['week'] = weekZodDict
            zodiacDetailList[indexZodiaWeek].update(zodiacDetailWeekDict)
        weatherInfoDict = {}
        response_data['flag'] = 'ok'
#             response_data['result'] = jsonobj['result']['data']
        weatherList = (jsonobj['result']['data']['weather'])[0]['info']['day']
        weatherDetail = weatherList[1] + ' ' + weatherList[2] + '°' + weatherList[4] + weatherList[3]
        weatherInfo = '【' + argv_city_name + '】 ' + weatherDetail
        import time
        wprTime = long(time.time()*1000)
        wprTimestamp = long(wprTime)/1000
        wprtime = time.localtime(wprTimestamp)
        wprMon  = int(wprtime[1])
        zodIndex = wprMon-1
        zodName = zodiacList[zodIndex]
        zodDicts = {}
        zodInfo = GetCurrentZodiac(zodiacList,zodiacImgList)
        zodDicts['zodiac_name'] = zodInfo['name']
        zodDicts['zodiac_imgurl'] = zodInfo['url']
        zodDicts['zodiac_summary'] = ' 【星座运势】' + (zodiacDetailList[zodIndex])['summary']
        weaObj = WeatherPushRecord(wpr_detail=json.dumps(jsonobj['result']['data']),zod_detail=json.dumps(zodiacDetailList),\
                                   wpr_time=wprTime,zod_info=json.dumps(zodDicts),community_id=long(communityId))
        weaObj.save()
        weaId = weaObj.getWeatherPushId()  
#         weatherInfoDict['time'] = wprTime
        weatherInfoDict['content'] = weatherInfo
#         weatherInfoDict['community_id'] = communityId  
#         weatherInfoDict['weaorzoc_id'] = weaId
#             TimingTaskWithWeather.delay(weatherInfoDict)
#             TimingTaskWithWeather.apply_async((communityId, weatherInfo,wprTime,weaId), countdown=10*10*10)#10s
#         response_data['systemtime'] = wprTime
#         response_data['weather_id'] = weaId
#         response_data['zodiac'] = json.loads(weaObj.wpr_detail)
        response_data['weaher'] = json.loads(weaObj.zod_detail)
#         response_data['zodinfo'] = strTemp
#         if strTemp==u'作者：马子晴':
#             response_data['flag'] = 'ok1111'
#         else:
#             response_data['flag'] = 'no1111'
        return response_data
#     except Exception,e:
#         response_data['flag'] = 'argv_error'
#         response_data['title'] = str(Exception)
#         response_data['error'] = str(e)
#         return response_data

#获取小区天气预报详情
def GetCommunityWeatherDetail(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if request.method == 'POST':
        weaorzodId  = request.POST.get('weaorzod_id') #对应的id
        communityId = request.POST.get('community_id')
    else:
        weaorzodId  = request.GET.get('weaorzod_id')
        communityId = request.GET.get('community_id')
    response_data = {}
    if weaorzodId is None or communityId is None:
        response_data['flag'] = 'argv_error'
        return response_data    
    try:
        wprObj = WeatherPushRecord.objects.get(wpr_id=long(weaorzodId),community_id=long(communityId))
        response_data['flag'] = 'ok'
        response_data['weaher_detail'] = json.loads(wprObj.wpr_detail)
        response_data['zodiac_detail'] = json.loads(wprObj.zod_detail)
        return response_data
    except Exception,e:
        response_data['flag'] = 'argv_error'
        response_data['error'] = str(e)
        return response_data

#获取小区天气预报
def GetCommunityWeather(request):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    if request.method == 'POST':
        weaorzodId  = request.POST.get('weaorzod_id') #初始化时填 0 下拉 传递传递最旧数据id 上拉 传递最新的数据id
        communityId = request.POST.get('community_id')
        actionId    = request.POST.get('action_id')#初始化时填 0 下拉 1 2上拉
    else:
        weaorzodId  = request.GET.get('weaorzod_id')
        communityId = request.GET.get('community_id')
        actionId    = request.GET.get('action_id')
    response_data = {}
    if weaorzodId is None or communityId is None or actionId is None:
        response_data['flag'] = 'argv_error'
        return response_data
    try:
        if int(actionId)==0:
            wprQuerySet = WeatherPushRecord.objects.filter(community_id=long(communityId)).order_by('-wpr_id')[:6]
        elif int(actionId)==1:
            wprQuerySet = WeatherPushRecord.objects.filter(wpr_id__lt=long(weaorzodId),community_id=long(communityId)).order_by('-wpr_id')[:6]
        else:
            wprQuerySet = WeatherPushRecord.objects.filter(wpr_id__gt=long(weaorzodId),community_id=long(communityId)).order_by('-wpr_id')
        wprList = []
        weaorzod_id = None
        wprSize = wprQuerySet.count()
        for index in range(0,wprSize,1):
            weatherDetail = {}
            weatherDetail['weaorzod_id'] = wprQuerySet[index].getWeatherPushId()
            if int(actionId)==2:
                if weaorzod_id is None:
                    weaorzod_id = weatherDetail['weaorzod_id']
            else:
                weaorzod_id = weatherDetail['weaorzod_id']
#                 weatherDetail['wpr_detail']  = ((json.loads(wprQuerySet[index].wpr_detail))['weather'])[0]['info']
            weatherDetail['wpr_time']    = GetWeatherShowTime(wprQuerySet[index].wpr_time,index)
            weatherDetail['zod_info']    = json.loads(wprQuerySet[index].zod_info)
            weatherDetail['wpr_detail']  = json.loads(wprQuerySet[index].wpr_detail)
            wprList.append(weatherDetail)
        if wprSize==0:
            response_data['flag'] = 'empty'
            return response_data
        else:
            response_data['flag'] = 'ok'
            response_data['weaorzod_id'] = weaorzod_id
            response_data['weaorzod_detail'] = wprList
            return response_data
    except Exception,e:
        response_data['flag'] = 'argv_error'
        response_data['error'] = str(e)
        return response_data

def GetWeatherShowTime(wprTime,index):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    valTime = ''
    wprTimestamp = long(wprTime)/1000
    wprtime = time.localtime(wprTimestamp)
    wprYear = int(wprtime[0])
    wprMon  = int(wprtime[1])
    wprDay  = int(wprtime[2])
    wprHour = int(wprtime[3])
    wprMin  = int(wprtime[4])
    
    curTimestamp = time.time()
    curTime = time.localtime(curTimestamp)
    curYear = int(curTime[0])
    curMon  = int(curTime[1])
    curDay  = int(curTime[2])
    
#     curTimestamp = time.time()
#     curTime = time.localtime(curTimestamp)
#     curYear = str(curTime[0])
#     curMon  = str(curTime[1])
#     curDay  = str(curTime[2])
#     curHour = '0'
#     curMin  = '0'
#     curSec  = '0'
#     a = curYear+'-'+curMon+'-'+curDay+' '+curHour+':'+curMin+':'+curSec
#     time.mktime(time.strptime(a,'%Y-%m-%d %H:%M:%S'))
    
    if wprMon<10:
        strMon = '0' + str(wprMon)
    else:
        strMon = str(wprMon)
    if wprDay<10:
        strDay = '0' + str(wprDay)
    else:
        strDay = str(wprDay)
    if curYear > wprYear:#超过一年
        strYear = str(wprYear)[2:]
        if wprHour<11:
            if wprHour<10:
                wprHour = '0'+str(wprHour)
            if wprMin<10:
                wprMin = '0'+str(wprMin)
            valTime = strYear+'/'+strMon+'/'+strDay+' '+'上午'+str(wprHour)+':'+str(wprMin)
        elif wprHour<=12 and wprHour>=11:
            if wprHour<10:
                wprHour = '0'+str(wprHour)
            if wprMin<10:
                wprMin = '0'+str(wprMin)
            valTime = strYear+'/'+strMon+'/'+strDay+' '+'中午'+str(wprHour)+':'+str(wprMin)
        elif wprHour<=24 and wprHour>18:
            if (wprHour-12)<10:
                wprHour = '0'+str(wprHour-12)
            if wprMin<10:
                wprMin = '0'+str(wprMin)
            valTime = strYear+'/'+strMon+'/'+strDay+' '+'夜间'+str(wprHour)+':'+str(wprMin)
        else:
            valTime = strYear+'/'+strMon+'/'+strDay+' '+'下午'+str(wprHour)+':'+str(wprMin)
    else:
        if index==0 and (wprDay==curDay):#表示最新的天气
            if wprHour<5 and wprHour>=0:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '凌晨'+str(wprHour)+':'+str(wprMin)
            elif wprHour<11 and wprHour>=5:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '上午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=12 and wprHour>=11:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '中午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=24 and wprHour>18:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '夜间'+str(wprHour)+':'+str(wprMin)
            else:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '下午'+str(wprHour)+':'+str(wprMin)
        elif (index==1 or index==0) and (wprDay==curDay-1):#表示昨天的天气
            if wprHour<5 and wprHour>=0:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '昨天 凌晨'+str(wprHour)+':'+str(wprMin)
            elif wprHour<11 and wprHour>=5:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '昨天 上午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=12 and wprHour>=11:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '昨天  中午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=24 and wprHour>18:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '昨天 夜间'+str(wprHour)+':'+str(wprMin)
            else:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = '昨天 下午'+str(wprHour)+':'+str(wprMin)
        else:
            if wprHour<5 and wprHour>=0:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = strMon+'-'+strDay+'凌晨'+str(wprHour)+':'+str(wprMin)
            elif wprHour<11 and wprHour>=5:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = strMon+'-'+strDay+'上午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=12 and wprHour>=11:
                if wprHour<10:
                    wprHour = '0'+str(wprHour)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = strMon+'-'+strDay+'中午'+str(wprHour)+':'+str(wprMin)
            elif wprHour<=24 and wprHour>18:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = strMon+'-'+strDay+'夜间'+str(wprHour)+':'+str(wprMin)
            else:
                if (wprHour-12)<10:
                    wprHour = '0'+str(wprHour-12)
                if wprMin<10:
                    wprMin = '0'+str(wprMin)
                valTime = strMon+'-'+strDay+'下午'+str(wprHour)+':'+str(wprMin)
    return valTime
    
    