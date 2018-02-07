#!/usr/bin/env python
# encoding: utf-8
import requests
__author__ = 'rui'

class MobSMS:
    def __init__(self):
        self.appkey = "d3f836c7d14c"
        self.android_verify_url = 'https://web.sms.mob.com/sms/verify'
        self.ios_verify_url     = 'https://webapi.sms.mob.com/sms/verify'
        
    def verify_sms_code(self, zone, phone, code, device =None,debug=False):
        if debug:
            return 200
        data = {'appkey': self.appkey, 'phone': phone, 'zone': zone, 'code': code}
        if str(device) == 'ios':
            req = requests.post(self.ios_verify_url, data=data, verify=False)
        else:
            req = requests.post(self.android_verify_url, data=data, verify=False)
        if req.status_code == 200:
            j = req.json()
            return j.get('status', 500)
        return 500