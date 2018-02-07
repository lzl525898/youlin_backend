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
def  get_access_token_from_somewhere (name):
    name=name
    url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential'#grant_type为固定值
    data={
          'appid':'wxbce4e8e3ec75752d',
          'secret':'e52e3895bce58d79bfa58bdf2032c1d1',
           }
    try:
        data=urllib.urlencode(data)
        html=urllib.urlopen(url,data)#>
        html= html.read()
        html=json.loads(html)
        access_token =html['access_token'].encode("utf-8")
        access_token_expires_at=int(time.time()) + html['expires_in']
        if name==1:
            return access_token
        elif name==2:
            return access_token_expires_at
    except Exception,e:
        reason= e
        return HttpResponseBadRequest(reason)

access_token = get_access_token_from_somewhere (1)
access_token_expires_at = get_access_token_from_somewhere (2)
conf = WechatConf(
   token='crteam2015',
   appid='wxbce4e8e3ec75752d',
   appsecret='e52e3895bce58d79bfa58bdf2032c1d1',
   encrypt_mode='normal',
   encoding_aes_key='UdzUHjMbBq2xVLi9oALEq12YkNQK5V1vG88RBqaKuUn ',
   access_token=access_token,
   access_token_expires_at=access_token_expires_at,
)
@csrf_exempt
def wechat_home(request):
   signature = request.GET.get('signature')
   timestamp = request.GET.get('timestamp')
   nonce = request.GET.get('nonce')
   wechat = WechatBasic(conf=conf)
   #wechat = WechatBasic(appid='wx4ed8e5a367d2451f', appsecret='d41a46925b7791a7fd7d2dc95823591b')
   if not wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
       return HttpResponseBadRequest('Verify Failed')
   else:
       if request.method == 'GET':
#            menu_data={
#                         'button':[
#                                                     {
#                                                         'type': 'click',
#                                                         'name': '认识优邻1',
#                                                         'key': 'V1001_TODAY_MUSIC'
#                                                     },
#                                                     {
#                                                         'type': 'click',
#                                                         'name': '歌手简介2',
#                                                         'key': 'V1001_TODAY_SINGER'
#                                                     },
#                                                     {
#                                                         'name': '菜单2',
#                                                         'sub_button': [
#                                                             {
#                                                                 'type': 'view',
#                                                                 'name': '搜索2',
#                                                                 'url': 'http://123.57.9.62/yl/web/user_login'
#                                                             },
#                                                             {
#                                                                 'type': 'view',
#                                                                 'name': '视频4',
#                                                                 'url': 'http://v.qq.com/'
#                                                             },
#                                                             {
#                                                                 'type': 'click',
#                                                                 'name': '赞一下我们7777',
#                                                                 'key': 'V1001_GOOD'
#                                                             }
#                                                         ]
#                                                     }
#                                                 ]
#                          } 
#            wechat.create_menu(menu_data)
           response = request.GET.get('echostr', 'error')
       else:
           try:
              wechat.parse_data(request.body) 
              source = wechat.message.source
              url_down='http://www.youlinzj.cn/yl/wx/cv?auth_id=' + str(source)
              url_sign='http://www.youlinzj.cn/yl/wx/sign?auth_id=' + str(source)
              menu_data={
                          'button':[
                                    {
                                     'name': '认识优邻',
                                     'sub_button': [
                                                    {
                                                     'type': 'view',
                                                     'name': '软件下载',
                                                     'url':url_down,
#                                                      'url': "https://123.57.9.62/yl/wx/sign/",
#                                                      'url': "http://storage.pgyer.com/6/b/8/f/a/6b8fa2402b05d4baf7806e61970c739b.apk",
                                                     },
                                                    {
                                                        'type': 'click',
                                                        'name': '了解我们',
                                                        'key': 'V1002_US'
                                                    },
                                                    ]
                                     },
                                    {
                                     'name': '最新动态',
                                     'sub_button': [
                                                    {
                                                     'type': 'view',
                                                     'name': '签到有礼',
                                                     'url':url_sign,
#                                                      'url': 'https://123.57.9.62/yl/wx/sign/',
                                                     },
                                                    {
                                                        'type': 'click',
                                                        'name': '历史消息',
                                                        'key': 'V2002_HISTORY'
                                                    },
                                                    ]
                                     },
                                    {
                                     'name': '联系我们',
                                     'sub_button': [
                                                    {
                                                     'type': 'click',
                                                     'name': '常见问题',
                                                     'key': 'V3001_QUESTION'
#                                                      'url': 'http://www.soso.com/',
                                                     },
                                                    {
                                                        'type': 'click',
                                                        'name': '联系客服',
                                                        'key': 'V3002_SERVICE'
#                                                         'url': 'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000009&idx=1&sn=c42e576ab9f13aa362b6f33342cecb78#rd'
                                                    },
                                                    {
                                                        'type': 'click',
                                                        'name': '合作模式',
                                                        'key': 'V3003_WORK'
#                                                         'url': 'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000030&idx=1&sn=cd8695012624324a9dfe85253843fae1#rd'
                                                    },
                                                    ]
                                     },
                                    ]    
                           } 
              wechat.create_menu(menu_data)
              

              message = wechat.get_message()
              response=POST(request,wechat) 
           except Exception,e:
               reason= e
               response = wechat.response_text(content=reason)

       return HttpResponse(response, content_type="application/xml")

   
def POST(request,wechat):
     try:
            wechat=wechat
            reason="进入post方法\n\nid:"
            id = wechat.message.id
            reason=reason+str(id)+"\n\n"
            reason=reason+"ToUserName:\n"
            target = wechat.message.target
            reason=reason+str(target)+"\n\n"
            reason=reason+"FromUserName:\n"
            source = wechat.message.source
            request.session['FromUserName'] = str(source)
            reason=reason+str(source)+"\n\n"
            
            reason=reason+"request.session['FromUserName']\n"
            request.session['FromUserName'] = str(source)
            a=request.session.get("FromUserName","")
            
            reason=reason+str(a)+"\n\n"
            reason=reason+"CreateTime:\n"
            time = wechat.message.time
            reason=reason+str(time)+"\n\n"
            reason=reason+" MsgType:\n"
            type = wechat.message.type
            reason=reason+str(type)+"\n\n"
            reason=reason+" XML:\n"
            raw = wechat.message.raw 
            reason=reason+str(raw)+"\n\n"
#             reason=reason+"content:\n"
#             content = wechat.message.content or None
#             reason=reason+str(content)+"\n\n"
            BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
            reason=reason+"+BASE_ROOT"
            path = BASE_ROOT+"/web/wx_w.txt" 
#             r=open(path,"w")
#             r.write(reason)
#             r.close()
#事件消息
            if isinstance(wechat.message, EventMessage):
                if wechat.message.type == 'subscribe':
                    reply_text='''/:rose您关注的不仅是一个公众号\n而是一个充满正能量的世界。\n您读的不是文字，\n而是您的心情。\n
真正的友邻，\n交的是心，连的是情。\n优邻之家，只为方便您的生活~\n\n\n\n回复【帮助】，可查看使用说明。'''
                elif wechat.message.type == 'click':
                    key=wechat.message.key
                    #历史消息
                    if key=="V2002_HISTORY":
                        response = wechat.response_news([
                                                             {
                                                            'title': u'只为方便您的生活～',
                                                            'description': u'历史消息',
                                                            'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5MA8hUzJERicKibxK86r3cWZe1303j7AddNATHYBZ6gGicyG1kibzP4Qtviam0n3LXwc4tlUnV1NPOGGyQ/0?wx_fmt=jpeg',
                                                            'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000033&idx=1&sn=e140186e29cf74eca03420a16c54e80c#rd',
                                                             }, {
                                                                    'title': u'使用帮助',
                                                                    'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5NOgRyU95gibDEePib2CK9H3wJYb0KSdw8KA38G8fIr5UHBwnvZOkUTMlewVFCVnbu9UibvqjibWIL0icw/0?wx_fmt=jpeg',
                                                                    'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000020&idx=1&sn=738d485c7bae63727c58844fb4c56968#rd',
                                                                },{
                                                                    'title': u'合作创造未来',
                                                                    'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5NOgRyU95gibDEePib2CK9H3wyyF7xKEkNtspdYZp2DFkyvHwPhKr980KMVLrneEVlHNbXZYaEx4icSg/0?wx_fmt=jpeg',
                                                                    'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000033&idx=3&sn=b3c930eea6e6f811945afe8224da3314#rd',
                                                                },
                                                         ])
                        return response
                    #了解我们
                    elif key=="V1002_US":
                        response = wechat.response_news([
                                                             {
                                                            'title':  u'了解我们',
                                                            'description': u'优邻～只为方便您的生活',
                                                            'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5PN5XwPKg0DavQfmTYtS8kLysm4XQCEpCV1miaCEkJogsL25IEoibs9ZKgNIoVictRBGPev40ibL8BHUw/0?wx_fmt=jpeg',
                                                            'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000020&idx=1&sn=738d485c7bae63727c58844fb4c56968#rd',
                                                             }, 
                                                         ])
                        return response
                    #常见问题
                    elif key=="V3001_QUESTION":
                        response = wechat.response_news([
                                                             {
                                                            'title': u'常见问题',
                                                            'description': u'找找看有没有您需要的东西～',
                                                            'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5MA8hUzJERicKibxK86r3cWZexgpH8EAsjeQnj2VJIdEJUrolvEeeqGMpLh9JrYdcVeswNwcNJicZDYg/0?wx_fmt=jpeg', 
                                                            'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000001&idx=1&sn=9126ec829750ce1944c7b1149920667c#rd',
                                                             }, 
                                                         ])
                        return response
                    #联系客服
                    elif key=="V3002_SERVICE":
                        response = wechat.response_news([
                                                             {
                                                            'title': u'联系客服',
                                                            'description': u'人工服务热线：150-4600-9860',
                                                            'picurl': u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5PN5XwPKg0DavQfmTYtS8kLWIriae7AyhRpwHibfUBlHFBEicYbXcsCoMFPgtFubuCRVljCDCtmEEiazw/0?wx_fmt=jpeg',
                                                            'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000009&idx=1&sn=c42e576ab9f13aa362b6f33342cecb78#rd',
                                                             },
                                                         ])
                        return response
                    #合作模式
                    elif key=="V3003_WORK":
                        response = wechat.response_news([
                                                             {
                                                            'title': u'携手前进，共同发展',
                                                             'description':u'合作模式',
                                                            'picurl':u'https://mmbiz.qlogo.cn/mmbiz/NcXA0u90K5MA8hUzJERicKibxK86r3cWZebXXchD2hIqaHlRXW66TWnV72g5ibYDicwZFTCW1N3TB5eygKKTDHib7xw/0?wx_fmt=jpeg',
                                                            'url': u'http://mp.weixin.qq.com/s?__biz=MzI1NDIyNDQyMQ==&mid=100000033&idx=1&sn=e140186e29cf74eca03420a16c54e80c#rd',
                                                             }, 
                                                         ])
                        return response        
                    else:
                        reply_text="/:rose其他key"
                        
                                                     
                                                     
                                                     
                                                     
                                                     
                                                     
                                                     
                                                     
                    
                else:
                    reply_text="/:roseWelcome to YOULIN Home~\n～只为方便您的生活!\n"
#                     r=open(path,"w")
#                     r.write(reply_text)
#                     r.close()
            elif isinstance(wechat.message, TextMessage):
                content = wechat.message.content
                if "帮助"in content:
                    reply_text='''/:rose/:)亲，是需要帮助么？\n点击"联系我们"-"常见问题”\n看看里面是否由您正在查找的答案。\n\n您也可拨打服务热线：\n139-3605-8677；\n
                    下载APP请点击下方链接：\nhttps://123.57.9.62/yl/ \n希望可以帮助到您\n优邻之家只为方便您的生活～～'''
                elif "客服"in content:
                    reply_text="请输入【意见反馈】+您想反馈给我们的问题\n例如：\n【意见反馈】交互界面不够美观"
                else:
                    reply_text="/:8*/:8*人家还小，还不能理解您的意思～～要不您试试回复【帮助】，看看能不能找到您需要的信息？/:8*/:8*"
                    
            elif isinstance(wechat.message, ImageMessage):
                reply_text="/:8*/:8*人家还小，还不能理解图片的意思～～要不您试试回复【帮助】，看看能不能找到您需要的信息？/:8*/:8*"
#                 response = wechat.response_news([
#                                                  {
#                                                   
#                                                     'title': '自强学堂',
#                                                     'picurl': 'https://mmbiz.qlogo.cn/mmbiz/ncTh1zS4QSavcbdXjm2onnutX1Hommjn6uBGC55NE1ZVGlcMTJLKsosRpv9qC4ULECuDDWs4mBkkKL9ibOSpp3w/0?wx_fmt=jpeg',
#                                                     'description': '节目单。',
#                                                     'url': 'http://123.57.9.62/yl/privacy_clause/',
#                                                      }, {
#                                                             'title': '百度',
#                                                             'picurl': 'http://doraemonext.oss-cn-hangzhou.aliyuncs.com/test/wechat-test.jpg',
#                                                             'url': 'http://www.baidu.com',
#                                                         }
#                                                     ])
#                 reply_imaget='../../static/assets/css/images/check.ico'
#                 response = wechat.response_image(media_id='https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=12&t=media/img_list&token=960440857&lang=zh_CN')
                return response
            
            else:
                reply_text="else!\n"

            
            response = wechat.response_text(content=reply_text)
            return response
     except Exception,e:
         reason= e
         response=wechat.response_text(content=reason)
         return response
     
     
    
     