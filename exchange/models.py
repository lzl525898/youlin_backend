# coding:utf-8
from django.db import models
import json

#礼品列表
class Giftlist(models.Model):
    
    gl_id           = models.AutoField(primary_key=True)  
    gl_pic          = models.TextField(blank=True, null=True) #图片url
    gl_url          = models.TextField(blank=True, null=True) #网页url 待定
    gl_credit       = models.BigIntegerField(blank=True, null=True) #兑换所需积分
    gl_name         = models.TextField(blank=True, null=True) #兑换礼物名称
    gl_count        = models.IntegerField(blank=True, null=True) #礼品数量
    gl_start_time   = models.BigIntegerField(blank=True, null=True) #礼品上架时间
    gl_end_time     = models.BigIntegerField(blank=True, null=True) #礼品下架时间
    gl_status       = models.BigIntegerField(blank=True, null=True) #状态值 1表示可以兑换 0不可兑换
    gl_community_id = models.BigIntegerField(blank=True, null=True, db_index=True) #奖品所在小区id
    
    class Meta:
        db_table="yl_giftlist"
    
    def getGiftId(self):
        return self.gl_id

    def toJSON(self):
        return to_json(self)

#记录用户礼品兑换
class UserExchange(models.Model):
    
    ue_id        = models.AutoField(primary_key=True)
    ue_glid      = models.BigIntegerField(blank=True, null=True) #兑换礼物的id
    ue_count     = models.IntegerField(blank=True, null=True) #兑换礼品数量
    ue_time      = models.BigIntegerField(blank=True, null=True) #礼品兑换时间
    ue_status    = models.IntegerField(blank=True, null=True) #兑换礼品状态 1进行中 2已交换
    user_id      = models.BigIntegerField(blank=True, null=True, db_index=True) #奖品兑换者id
    community_id = models.BigIntegerField(blank=True, null=True, db_index=True) #用户所在小区id
    
    class Meta:
        db_table="yl_userexchange"
        
    def getUserExchangeId(self):
        return self.ue_id
    
    def toJSON(self):
        return to_json(self)
    
def to_json(obj):
    fields = []
    for field in obj._meta.fields:
        fields.append(field.name)
    d = {}
    for attr in fields:
        val = getattr(obj, attr)
        
        #如果是model类型，就要再一次执行model转json
        if isinstance(val, models.Model):
            val = json.loads(to_json(val))
        d[attr] = val
    return json.dumps(d)
    