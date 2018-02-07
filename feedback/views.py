# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.core import serializers
from django.conf import settings
from feedback.models import OpinionRecord,ExceptionRecord
import json
import time

@api_view(['GET','POST'])
def setFeedBack(request): 
    data = {}
    if request.method == 'POST':
        opinionType    = request.POST.get('opinionType', None)
        opinionContent = request.POST.get('opinionContent', None)
        userId         = request.POST.get('user_id', None)
        communityId    = request.POST.get('community_id', None)
    else:
        opinionType    = request.GET.get('opinionType', None)
        opinionContent = request.GET.get('opinionContent', None)
        userId         = request.GET.get('user_id', None)
        communityId    = request.GET.get('community_id', None)
    
    if userId is None:
        userId = 0
    if communityId is None:
        communityId = 0
    if opinionType is not None and opinionContent is not None:
        currentTime = long(time.time()*1000)
        OpinionRecord.objects.create(opinion_type=int(opinionType),opinion_content=opinionContent,user_id=long(userId),\
                                     opinion_time=currentTime,read_status=1,handle_type=1,community_id=long(communityId))
        
        data['flag'] = "ok"
    else:
        data['flag'] = "no"
    return HttpResponse(json.dumps(data), content_type="application/json")

#设置建议
def SetFeedBack(request): 
    data = {}
    if request.method == 'POST':
        userId         = request.POST.get('userId', None)
        communityId    = request.POST.get('communityId', None)
        opinionType    = request.POST.get('opinionType', None)    # 1界面 2功能 3其他
        opinionContent = request.POST.get('opinionContent', None)
    else:
        userId         = request.GET.get('userId', None)
        communityId    = request.GET.get('communityId', None)
        opinionType    = request.GET.get('opinionType', None)
        opinionContent = request.GET.get('opinionContent', None)
    
    if opinionType is not None and opinionContent is not None:
        currentTime = long(time.time()*1000)
        OpinionRecord.objects.create(opinion_type=int(opinionType),opinion_content=opinionContent,user_id=long(userId),\
                                     opinion_time=currentTime,read_status=1,handle_type=1,community_id=long(communityId))
        
        data['flag'] = "ok"
    else:
        data['flag'] = "no"
    return data

#返回错误报告
def ExceptErrorRecord(request): 
    data = {}
    content = request.POST.get('content', None)
    device  = request.POST.get('device_type', None)
    if content is None or device is None:
        data['flag'] = 'argv_error'
        data['tag'] = 'except'
        return data
    ExceptionRecord.objects.create(er_type=int(device),er_content=str(content),er_time=long(time.time()*1000))
    data['flag'] = "ok"
    data['tag'] = 'except'
    return data