# coding:utf-8
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.conf import settings
import re
import os
import json
import time
import random
import requests
import pingpp
import string

# API Key & APP ID
api_key = 'sk_test_5errXLqzDy10KCCOGKTe900O'
app_id = 'app_b9S4SOuT8CqP4Ce1'

app_subject = {'upacp'    : u'银联支付',
               'wx'       : u'微信支付',
               'alipay'   : u'支付宝支付',
               'bfb'      : u'百度支付',
               'jdpay_wap': u'京东支付'}

# 设置 API Key
pingpp.api_key = api_key
# 设置请求签名私钥路径
pingpp.private_key_path = os.path.join(
    os.path.dirname(__file__), 'rsa_private_key.pem')

def CreatePayment(request):
    response_data = {}
    
    paysalt = request.POST.get('paysalt', None)
    price   = request.POST.get('amount', None)
    type    = request.POST.get('channel', None)

    try:
        if price != None:
            price = float(price) * 100 #元转分
        else:
            price = float(100)
        orderno = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        ch = pingpp.Charge.create(
            subject = app_subject[str(type)],
            body = '您即将支付{0}元'.format(price / 100.0),
            amount = float(100) if price==None else price,
            order_no = orderno,
            currency = 'cny',
            channel = 'alipay' if type==None else type,
            client_ip = request.META['REMOTE_ADDR'],
            app = dict(id = app_id)
        )
        response_data['info'] = ch
    except Exception,e:
        response_data['info'] = 'error'
#     return HttpResponse(json.dumps(response_data['info']), content_type="application/json") 
    return response_data
   
def CreateCharge(request):
    response_data = {}
    if request.method == 'POST':
        price   = request.POST.get('amount', None)
        type    = request.POST.get('channel', None)
    else:
        price   = request.GET.get('amount', None)
        type    = request.GET.get('channel', None)
    try:
        if price != None:
            price = float(price) * 100 #元转分
        else:
            price = float(100)
        orderno = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        ch = pingpp.Charge.create(
            subject = app_subject[str(type)],
            body = '您即将支付{0}元'.format(price / 100.0),
            amount = float(100) if price==None else price,
            order_no = orderno,
            currency = 'cny',
            channel = 'alipay' if type==None else type,
            client_ip = request.META['REMOTE_ADDR'],
            app = dict(id = app_id)
        )
        response_data['info'] = ch
    except Exception,e:
        response_data['info'] = {'error':str(e),'Except':str(Exception)}
    return response_data



@api_view(['GET','POST'])    
def GenCharge(request):
    response_data = {}
    if request.method == 'POST':
        price   = request.POST.get('amount', None)
        type    = request.POST.get('channel', None)
    else:
        price   = request.GET.get('amount', None)
        type    = request.GET.get('channel', None)
    try:
        if price != None:
            price = float(price) * 100 #元转分
        else:
            price = float(100)
        orderno = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        ch = pingpp.Charge.create(
            subject = app_subject[type],
            body = '您即将支付{0}元'.format(price / 100.0),
            amount = float(100),
            order_no = orderno,
            currency = 'cny',
            channel = type,
            client_ip = request.META['REMOTE_ADDR'],
            app = dict(id = app_id)
        )
        response_data['info'] = ch    
    except Exception,e:
        response_data['info'] = {'error':str(e),'Except':str(Exception)}
    
    return HttpResponse(json.dumps(response_data['info']), content_type="application/json")
    
    
    
    
    