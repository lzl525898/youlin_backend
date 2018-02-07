#-*- coding:utf-8 -*-
import os
import urllib  
import urllib2  
from urllib import urlencode
import httplib
import json
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import (TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage, ShortVideoMessage)
#获取access_token和过期时间
# def  get_access_token_from_somewhere (name):
#     name=name
#     url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential'#grant_type为固定值
#     data={
#           'appid':'wxbce4e8e3ec75752d',
#           'secret':'e52e3895bce58d79bfa58bdf2032c1d1',
#            }
#     try:
#         data=urllib.urlencode(data)
#         html=urllib.urlopen(url,data)#>
#         html= html.read()
#         html=json.loads(html)
#         access_token =html['access_token'].encode("utf-8")
#         access_token_expires_at=int(time.time()) + html['expires_in']
#         if name==1:
#             return access_token
#         elif name==2:
#             return access_token_expires_at
#     except Exception,e:
#         reason= e
#         return HttpResponseBadRequest(reason)
#     
# access_token = get_access_token_from_somewhere (1)
# access_token_expires_at = get_access_token_from_somewhere (2)
conf = WechatConf(
   token='crteam2015',
   appid='wx573c092267bc2dff',
   appsecret='ac709f6911164d29c74a307fd8cc31e7',
   encrypt_mode='normal',
   encoding_aes_key='UdzUHjMbBq2xVLi9oALEq12YkNQK5V1vG88RBqaKuUn ',
)


@csrf_exempt
def wechat_home1(request):
   signature = request.GET.get('signature')
   timestamp = request.GET.get('timestamp')
   nonce = request.GET.get('nonce')
   BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
   path = BASE_ROOT+"/web/wx_w.txt" 
   r=open(path,"w")
   r.write("soe")
   r.close()
   wechat = WechatBasic(conf=conf)
   #wechat = WechatBasic(appid='wx4ed8e5a367d2451f', appsecret='d41a46925b7791a7fd7d2dc95823591b')
   if not wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
       return HttpResponseBadRequest('Verify Failed')
   else:
       if request.method == 'GET':
           response = request.GET.get('echostr', 'error')
       else:
           try:
#                BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#                path = BASE_ROOT+"/web/wx_w.txt" 
#                r=open(path,"w")
#                r.write("soe")
#                r.close()
#                source = wechat.message.source
#                BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#                path = BASE_ROOT+"/web/wx_w.txt" 
#                r=open(path,"w")
#                r.write("source")
#                r.close()
               wechat.parse_data(request.body) 
               response=wechat.response_text(content="reason")
           except Exception,e:
               reason=e
               response=wechat.response_text(content=reason)
               
       return HttpResponse(response, content_type="application/xml")
   
   
   
   
   
#    def POST1(request,wechat):
#      try:
#          wechat=wechat
#          if isinstance(wechat.message, EventMessage):
#              reply_text="ceshi"
#          elif isinstance(wechat.message, TextMessage):
#                 content = wechat.message.content
#                 reply_text=content
#          else:
#                 reply_text="else!\n"
# 
#             
#          response = wechat.response_text(content=reply_text)
#          return response
#      except Exception,e:
#          
#          reason= e
#          response=wechat.response_text(content=reason)
#          return response
     
