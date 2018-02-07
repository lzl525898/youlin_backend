# Create your views here.
# coding:utf-8
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from addrinfo.models import City,Community
from users.models import Admin,User
from users.views import genAdminContentDict,genAdminDetailDict
from push.views import createPushRecord,readIni
from push.sample import pushMsgToTag,pushMsgToSingleDevice
from django.conf import settings
import jpush as jpush
from push.views import readIni
import time
import json


class PushForms(forms.Form):
    city_id = forms.ModelChoiceField(
        queryset= City.objects.all(),
        required = True,
        label = u"城市",
        error_messages = {'required':u'必选项'}                           
    )
    community_id = forms.ModelChoiceField(
        queryset= Community.objects.all(),
        required = True,
        label = u"小区",
        error_messages = {'required':u'必选项'}                           
    )
    admin_id = forms.ModelChoiceField(
        queryset= Admin.objects.filter(admin_type = 1),
        required = True,
        label = u"申请人",
        error_messages = {'required':u'必选项'}                           
    )
    
    
    

def pushView(request):
    if request.method == 'POST':
        uf = PushForms(request.POST)
        if uf.is_valid():
            admin_id = uf.cleaned_data['admin_id'].admin_id
            city_id = uf.cleaned_data['city_id'].city_id
            community_id = uf.cleaned_data['community_id'].community_id
            #获取的表单数据与数据库进行比较
            adminObj = Admin.objects.get(admin_type=1,admin_id=admin_id,community_id = community_id,city_id =city_id)
            ListAdmin = []
            config = readIni()
            if adminObj:
                    userId = adminObj.user.user_id
                    userObj = adminObj.user
                    #baidu_channel_id = userObj.user_push_channel_id.encode('utf-8')
                    pushTitle = config.get("users", "title")
                    communityObj = adminObj.community
                    cityName = communityObj.city.city_name
                    communityName = communityObj.community_name
                    address = cityName+communityName
                    familyAddr = address.encode('utf-8')
                    pushContent = config.get("users", "content1")+ familyAddr + config.get("users", "content3")
                    ListAdmin.append(genAdminDetailDict(userId,cityName,community_id,communityName,address,2))
                    userObj.user_json = json.dumps(ListAdmin)
                    adminObj.admin_info = json.dumps(ListAdmin)
                    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
                    currentPushTime = long(time.time()*1000)
                    customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,community_id)
                    recordId = createPushRecord(1,2,pushTitle,pushContent,currentPushTime,userId,json.dumps(customContent),1)
                    customContent = genAdminContentDict(userId,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,community_id,recordId)
                    config = readIni()
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
                        pass
                    adminObj.admin_type = 2
                    adminObj.app_time = currentPushTime
                    adminObj.save()
                    userObj.user_type = 2
                    userObj.user_time = currentPushTime
                    userObj.save()
                    #比较成功，跳转index
                    return render_to_response('success.html', RequestContext(request,{'createtask_success':True,}))
                
            else:
                #小区没有管理员申请
                return render_to_response('fail.html', RequestContext(request,{'createtask_fail':True,}))
    else:
        uf = PushForms()
    return render_to_response('pushView.html',{'uf':uf},context_instance=RequestContext(request))
    
 
 
 