# coding: utf-8 

import requests
import json
from time import time
from requests.auth import AuthBase
import string
import random

JSON_HEADER = {'content-type': 'application/json'}

EASEMOB_HOST = "https://a1.easemob.com"

DEBUG = False

def post(url, payload, auth=None):
    r = requests.post(url, data=json.dumps(payload), headers=JSON_HEADER, auth=auth)
    return http_result(r)

def get(url, auth=None):
    r = requests.get(url, headers=JSON_HEADER, auth=auth)
    return http_result(r)

def delete(url, auth=None):
    r = requests.delete(url, headers=JSON_HEADER, auth=auth)
    return http_result(r)

def http_result(r):
    if DEBUG:
        error_log = {
                    "method": r.request.method,
                    "url": r.request.url,
                    "request_header": dict(r.request.headers),
                    "response_header": dict(r.headers),
                    "response": r.text
                }
        if r.request.body:
            error_log["payload"] = r.request.body
        print json.dumps(error_log)

    if r.status_code == requests.codes.ok:
        return True, r.json()
    else:
        return False, r.text


class Token:
    """表示一个登陆获取到的token对象"""
    def __init__(self, token, exipres_in):
        self.token = token
        self.exipres_in = exipres_in + int(time())
        
    def is_not_valid(self):
        """这个token是否还合法, 或者说, 是否已经失效了, 这里我们只需要
        检查当前的时间, 是否已经比或者这个token的时间过去了exipreis_in秒
        
        即  current_time_in_seconds < (expires_in + token_acquired_time)
        """
        return time() > self.exipres_in

class EasemobAuth(AuthBase):
    """环信登陆认证的基类"""
    
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.get_token()
        return r  
          
    def get_token(self):
        """在这里我们先检查是否已经获取过token, 并且这个token有没有过期"""
        if (self.token is None) or (self.token.is_not_valid()):
            self.token = self.acquire_token() #refresh the token
        return self.token.token
        
    def acquire_token(self):
        """真正的获取token的方法, 返回值是一个我们定义的Token对象
            这个留给子类去实现
        """
        pass
        
class AppClientAuth(EasemobAuth):
    """使用app的client_id和client_secret来获取app管理员token"""
    def __init__(self, org, app, client_id, client_secret):
        super(AppClientAuth, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = EASEMOB_HOST+("/%s/%s/token" % (org, app))
        self.token = None
        
    def acquire_token(self):
        """
        使用client_id / client_secret来获取token, 具体的REST API为
        
        POST /{org}/{app}/token {'grant_type':'client_credentials', 'client_id':'xxxx', 'client_secret':'xxxxx'}
        """
        payload = {'grant_type':'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        success, result = post(self.url, payload)
        if success:
            return Token(result['access_token'], result['expires_in'])
        else:
            # throws exception
            pass

def register_new_user(org, app, auth, username, password):
    """注册新的app用户
    POST /{org}/{app}/users {"username":"xxxxx", "password":"yyyyy"}
    """
    payload = {"username":username, "password":password}
    url = EASEMOB_HOST+("/%s/%s/users" % (org, app))
    return post(url, payload, auth)
    
def delete_user(org, app, auth, username):
    """删除app用户
    DELETE /{org}/{app}/users/{username}
    """
    url = EASEMOB_HOST+("/%s/%s/users/%s" % (org, app, username))
    return delete(url, auth)

def send_file(org, app, auth, file_path, secret=True):
    """上传文件
    上传文件
    curl --verbose --header "Authorization: Bearer YWMtz1hFWOZpEeOPpcmw1FB0RwAAAUZnAv0D7y9-i4c9_c4rcx1qJDduwylRe7Y" \
    --header "restrict-access:true" --form file=@/Users/stliu/a.jpg \
    http://a1.easemob.com/easemob-demo/chatdemoui/chatfiles
    """
    url = EASEMOB_HOST+("/%s/%s/chatfiles" % (org, app))
    # files = {'file': open(file_path, 'rb')}
    files = {'file': ('report.xls', open(file_path, 'rb'), 'image/jpeg', {'Expires': '0'})}

    r = requests.post(url, files=files,  auth=auth)
    return http_result(r)
 
def registUser(username,password):
    response_data = {}
    appkey = "nfs-hlj#youlinapp"
    org = "nfs-hlj"
    app = "youlinapp"
    client_id = "YXA66jnmoG9TEeWEjb1siTX-TA"
    client_secret = "YXA6JPd3mgIZL5R5G3-fIoWFzaHZrZ4"
    app_client_auth = AppClientAuth(org, app, client_id, client_secret)
    success, result = register_new_user(org, app, app_client_auth, username, password)
    if success:
        response_data['flag'] = 'ok'
        response_data['username'] = username
        response_data['appkey'] = appkey
    else:
        response_data['flag'] = 'no'
        response_data['username'] = username
        response_data['appkey'] = appkey
    return response_data

def registUserWithMahjong(userid):
    response_data = {}
    appkey = "nfs-hlj#mahjong"
    org = "nfs-hlj"
    app = "mahjong"
    client_id = "YXA6WdXkAOnPEeWtwseAAnOB4Q"
    client_secret = "YXA6BLYQzLfJDI3p-5M3mme60ecbs_M"
    app_client_auth = AppClientAuth(org, app, client_id, client_secret)
    success, result = register_new_user(org, app, app_client_auth, userid, userid)
    if success:
        response_data['flag'] = 'ok'
        response_data['username'] = userid
        response_data['appkey'] = appkey
    else:
        response_data['flag'] = 'no'
        response_data['username'] = userid
        response_data['appkey'] = appkey
    return response_data